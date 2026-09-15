import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchKycGapProfile,
  preparePrevisit,
  executeSupplyChainGraph,
  type KycGapProfile,
  type PreparedPrevisitResponse,
  type SupplyChainGraphReport,
} from '../api/engagement'

/**
 * 访前共享状态。
 * 一键访前（唯一 KERT 入口）的产物在 P11→P12→P13→P14 间共享，
 * 避免 P13/P14 各自重复调用后端（消除 KERT 重复调用缺陷）。
 * 仅内存态；整页刷新后的持久化需后端结果缓存查询（方案 C，本轮不做后端变更）。
 */
export const usePrevisitStore = defineStore('previsit', () => {
  // 旅程上下文（P11 启动后 setContext；P12–P14 读取）
  const journeyId = ref('')
  const operatingCaseId = ref('')
  const customerId = ref('')
  const rmId = ref('')

  // KYC 缺口画像（纯查询，P11/P12 共享）
  const kycGapProfile = ref<KycGapProfile | null>(null)
  const kycLoading = ref(false)
  const kycError = ref('')

  // 一键访前结果（唯一 KERT 入口产物，P13/P14 只读消费）
  const previsitResult = ref<PreparedPrevisitResponse | null>(null)
  const supplyChainReport = ref<SupplyChainGraphReport | null>(null)
  const loading = ref(false)
  const error = ref('')
  const running = ref(false)

  const previsitDone = computed(() => running.value && previsitResult.value != null)
  const assemblyTrace = computed(() => previsitResult.value?.assemblyTrace || [])

  function setContext(ctx: {
    journeyId?: string
    operatingCaseId?: string
    customerId?: string
    rmId?: string
  }): void {
    if (ctx.journeyId !== undefined) journeyId.value = ctx.journeyId
    if (ctx.operatingCaseId !== undefined) operatingCaseId.value = ctx.operatingCaseId
    if (ctx.customerId !== undefined) customerId.value = ctx.customerId
    if (ctx.rmId !== undefined) rmId.value = ctx.rmId
  }

  async function loadKycGap(cid: string): Promise<KycGapProfile | null> {
    if (!cid) {
      kycGapProfile.value = null
      return null
    }
    kycLoading.value = true
    kycError.value = ''
    try {
      kycGapProfile.value = await fetchKycGapProfile(cid)
      return kycGapProfile.value
    } catch (e: unknown) {
      kycError.value = e instanceof Error ? e.message : '无法获取 KYC 缺口画像'
      kycGapProfile.value = null
      return null
    } finally {
      kycLoading.value = false
    }
  }

  /** 一键访前：唯一 KERT 入口。3 Skill 并行（外联/会面/R1），另并行供应链图谱。 */
  async function runPrevisit(visitObjective = '访前调研'): Promise<PreparedPrevisitResponse | null> {
    if (!journeyId.value || !customerId.value || !operatingCaseId.value) {
      error.value = '缺少旅程/客户/经营案例上下文，无法执行一键访前'
      return null
    }
    loading.value = true
    error.value = ''
    running.value = true
    supplyChainReport.value = null
    const graphJob = executeSupplyChainGraph(customerId.value)
      .then((g) => { supplyChainReport.value = g })
      .catch(() => { /* 图谱失败不阻断主流程，仅缺失图谱视图 */ })
    try {
      previsitResult.value = await preparePrevisit(
        journeyId.value,
        customerId.value,
        operatingCaseId.value,
        visitObjective,
        rmId.value,
      )
      await graphJob
      return previsitResult.value
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '一键访前失败'
      return null
    } finally {
      loading.value = false
    }
  }

  function reset(): void {
    kycGapProfile.value = null
    previsitResult.value = null
    supplyChainReport.value = null
    running.value = false
    error.value = ''
    kycError.value = ''
  }

  return {
    journeyId, operatingCaseId, customerId, rmId,
    kycGapProfile, kycLoading, kycError,
    previsitResult, supplyChainReport, loading, error, running,
    previsitDone, assemblyTrace,
    setContext, loadKycGap, runPrevisit, reset,
  }
})
