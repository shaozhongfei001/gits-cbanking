import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  createProductRecommendationRun,
  getProductRecommendationRun,
  getProductRecommendationStages,
  getProductRecommendationVersion,
  retryProductRecommendationRun,
  isKertUnreachable,
  type ProductRecommendationRun,
  type ProductRecommendationStageResult,
  type ProductRecommendationProposalVersion,
  type ProductRecommendationCreateRequest,
  type RecommendationDecision,
  type RecommendationHumanDecision,
  type StructuredModification,
} from '../api/productRecommendation'
import { fetchRecentProductKnowledge } from '../api/v11'

/**
 * 产品推荐三段式共享状态。
 * run = 运行生命周期；stage = 三段式技术结果；version = 不可变方案版本；decision = 人工决定草稿。
 * 仅内存态。决定写入端点不在 vNext OpenAPI（HG-D01 待合同裁决），前端只持有结构化草稿，不发写。
 */
export const useProductRecommendationStore = defineStore('productRecommendation', () => {
  const run = ref<ProductRecommendationRun | null>(null)
  const stages = ref<ProductRecommendationStageResult | null>(null)
  const version = ref<ProductRecommendationProposalVersion | null>(null)
  const decision = ref<RecommendationHumanDecision | null>(null)

  /**
   * productId → productName 映射。
   *
   * 优先从产品知识版本 API 获取（UUID 格式 productId）；
   * 同时内置 KERT 返回的业务编码（PROD-FIN-001 等）→ 中文名称映射，
   * 因为 KERT 使用自己的产品编码体系，与 GITS 产品知识的 UUID 不一致。
   */
  const productNameMap = ref<Record<string, string>>({
    // KERT 产品编码 → 中文名称（对齐 KERT 知识库中的产品定义）
    'PROD-FIN-001': '流动资金贷款',
    'PROD-FIN-002': '应收账款质押融资',
    'PROD-FIN-003': '订单融资',
    'PROD-SET-001': '对公结算账户',
    'PROD-SET-002': '企业网上银行',
    'PROD-CM-001': '集团现金池',
    'PROD-CM-002': '智能存款与通知存款',
    'PROD-CM-003': '智能存款与通知存款',
    'PROD-TF-001': '国内信用证',
    'PROD-TF-002': '银行承兑汇票',
    'PROD-CB-001': '跨境汇款与结售汇',
    'PROD-CB-002': '外汇避险（远期结售汇）',
    'PROD-IB-001': '债务融资工具承销',
  })

  const loading = ref(false)
  const creating = ref(false)
  const error = ref('')
  const kertUnreachable = ref(false)

  const isStale = computed(() => run.value?.status === 'STALE_REQUIRES_RERUN')
  const canDecide = computed(() => Boolean(run.value && version.value && !isStale.value))

  function newIdempotencyKey(): string {
    const cryptoObj = (globalThis as { crypto?: { randomUUID?: () => string } }).crypto
    if (cryptoObj?.randomUUID) {
      return cryptoObj.randomUUID()
    }
    return `idem-${Date.now()}-${Math.random().toString(36).slice(2)}`
  }

  /** 发起产品推荐：创建运行（带幂等键），成功后切到该 run。 */
  async function createRun(request: ProductRecommendationCreateRequest): Promise<ProductRecommendationRun | null> {
    creating.value = true
    error.value = ''
    kertUnreachable.value = false
    try {
      run.value = await createProductRecommendationRun(request, newIdempotencyKey())
      return run.value
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '发起产品推荐失败'
      kertUnreachable.value = isKertUnreachable(e)
      return null
    } finally {
      creating.value = false
    }
  }

  /** 打开推荐工作区：加载 run → stages →（如有当前版本）version，同时加载产品名称映射。 */
  async function loadRun(runId: string): Promise<void> {
    loading.value = true
    error.value = ''
    kertUnreachable.value = false
    run.value = null
    stages.value = null
    version.value = null
    decision.value = null
    try {
      const r = await getProductRecommendationRun(runId)
      run.value = r
      try {
        stages.value = await getProductRecommendationStages(runId)
      } catch {
        stages.value = null
      }
      const vid = r.currentVersionId
      if (vid) {
        try {
          version.value = await getProductRecommendationVersion(runId, vid)
        } catch {
          version.value = null
        }
      }
      // 顺便加载产品名称映射（合并到内置映射，不覆盖）
      try {
        const pkList = await fetchRecentProductKnowledge(100)
        const map: Record<string, string> = { ...productNameMap.value }
        for (const pk of pkList) {
          if (!map[pk.productId]) {
            map[pk.productId] = pk.productName
          }
        }
        productNameMap.value = map
      } catch { /* 非关键，忽略 */ }
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '无法加载产品推荐运行'
      kertUnreachable.value = isKertUnreachable(e)
    } finally {
      loading.value = false
    }
  }

  /** 重跑（STALE_REQUIRES_RERUN / 可重试失败）。 */
  async function retryRun(runId: string): Promise<ProductRecommendationRun | null> {
    loading.value = true
    error.value = ''
    kertUnreachable.value = false
    try {
      run.value = await retryProductRecommendationRun(runId)
      return run.value
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '重跑产品推荐失败'
      kertUnreachable.value = isKertUnreachable(e)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 记录人工决定草稿。前端不发写（无决定端点）；补齐 runId/proposalVersionId/gateId/actorId/decidedAt。
   */
  function recordDecision(input: {
    decision: RecommendationDecision
    modifications?: StructuredModification[]
    reason?: string
  }): void {
    if (!run.value || !version.value) {
      return
    }
    decision.value = {
      gateId: 'HG-D01',
      runId: run.value.runId,
      proposalVersionId: version.value.versionId,
      expectedVersion: version.value.versionId,
      decision: input.decision,
      modifications: input.decision === 'MODIFY' ? input.modifications ?? [] : undefined,
      reason: input.reason,
      actorId: 'current-user',
      actorRole: 'RELATIONSHIP_MANAGER',
      decidedAt: new Date().toISOString(),
    }
  }

  function reset(): void {
    run.value = null
    stages.value = null
    version.value = null
    decision.value = null
    loading.value = false
    creating.value = false
    error.value = ''
    kertUnreachable.value = false
  }

  return {
    run,
    stages,
    version,
    decision,
    productNameMap,
    loading,
    creating,
    error,
    kertUnreachable,
    isStale,
    canDecide,
    createRun,
    loadRun,
    retryRun,
    recordDecision,
    reset,
  }
})
