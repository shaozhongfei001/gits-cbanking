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

  /** 打开推荐工作区：加载 run → stages →（如有当前版本）version。 */
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
