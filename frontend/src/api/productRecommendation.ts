import axios from 'axios'
import { getApiKey, clearApiKey } from './auth'

/**
 * 产品推荐三段式决策端点（vNext，增量候选）。
 * 契约权威源：specs/openapi/product-recommendation.openapi.json（CTR-PR-API-001）。
 * 状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。字段严格对齐 OpenAPI，禁止发明字段。
 * 端点：createRun / getRun / getStages / getVersion / retry（对应下方五个函数）。
 * 注意：OpenAPI 未定义决定写入端点（HG-D01 / D01_PRODUCT_RECOMMEND 尚待合同裁决），
 *       前端只持有结构化决定草稿，不发 POST 决定；决定对象字段对齐
 *       specs/product-recommendation/recommendation-human-decision.schema.json（CTR-PR-DEC-001）。
 */

const prApi = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

prApi.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

prApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearApiKey()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

// ===================== 类型定义（对齐 OpenAPI） =====================

export type RecommendationRunStatus =
  | 'REQUESTED'
  | 'CONTEXT_ASSEMBLING'
  | 'HARD_FILTERING'
  | 'MATCHING'
  | 'PROPOSAL_READY'
  | 'AWAITING_HUMAN'
  | 'APPROVED'
  | 'MODIFIED'
  | 'REJECTED'
  | 'HELD'
  | 'STALE_REQUIRES_RERUN'
  | 'FAILED_CLOSED'

export interface ProductRecommendationCreateRequest {
  customerId: string
  journeyId?: string
  operatingCaseId?: string
  needVersionIds?: string[]
  recommendationObjective: string
  requestedProductDomains?: string[]
  asOf: string
  customerFactSnapshotId?: string
  productKnowledgeSnapshotRef?: string
  ruleBundleRef?: string
  permissionDecisionId?: string
  activationContract?: string
}

export interface ProductRecommendationRun {
  runId: string
  customerId: string
  journeyId?: string
  operatingCaseId?: string
  needVersionIds?: string[]
  recommendationObjective?: string
  requestedProductDomains?: string[]
  asOf: string
  idempotencyKey: string
  status: RecommendationRunStatus
  currentVersionId?: string
  kertJobRef?: string
  snapshotRefs?: Record<string, string>
  createdAt: string
  updatedAt?: string
}

export interface ProductRecommendationStageResult {
  runId: string
  status: RecommendationRunStatus
  eligibilityResults?: EligibilityResult[]
  fitResults?: ProductFitResult[]
  portfolioCandidates?: ProductPortfolioCandidate[]
  needProfile?: NeedProfileItem[]
  unknowns?: string[]
  conflicts?: string[]
}

export interface ProductRecommendationProposalVersion {
  versionId: string
  runId: string
  resultRef?: string
  evidenceBundleId?: string
  contentHash: string
  supersededBy?: string
  createdAt: string
}

// ===================== 三段式结果明细（对齐 specs/product-recommendation/*.schema.json） =====================

export type EligibilityStatus = 'ELIGIBLE' | 'INELIGIBLE' | 'UNKNOWN' | 'REVIEW_REQUIRED'

export interface EligibilityRuleResult {
  ruleId: string
  ruleVersion: string
  result: 'PASS' | 'FAIL' | 'UNKNOWN' | 'REVIEW_REQUIRED'
  reasonCode: string
  inputFactRefs?: string[]
  evidenceRefs?: string[]
}

export interface EligibilityUnknownItem {
  question: string
  relatedFactRef?: string
  suggestedAction?: string
}

export interface EligibilityReviewRequirement {
  reason: string
  requiredExpertise?: string
  ruleId?: string
}

export interface EligibilityResult {
  schemaVersion?: string
  productId: string
  productVersion: string
  eligibility: EligibilityStatus
  ruleResults?: EligibilityRuleResult[]
  unknowns?: EligibilityUnknownItem[]
  reviewRequirements?: EligibilityReviewRequirement[]
}

export interface ProductFitResult {
  schemaVersion?: string
  productId: string
  productVersion: string
  rank?: number
  fitScore?: number | null
  dimensionMatches?: DimensionMatch[]
  matchedNeeds?: NeedReference[]
  matchedCapabilities?: string[]
  recommendationReasons?: RecommendationReason[]
  notRecommendReasons?: string[]
  conditions?: string[]
  materialGaps?: string[]
  riskNotes?: string[]
  salesBoundaries?: string[]
  expertCollaborationRequired?: boolean
  evidenceRefs?: string[]
}

export interface DimensionMatch {
  dimension: 'CORE_NEED_FIT' | 'SCENARIO_FIT' | 'EXECUTABILITY' | 'RELATIONSHIP_INCREMENT' | 'PORTFOLIO_SYNERGY' | 'EVIDENCE_SUFFICIENCY'
  result: 'STRONG' | 'MODERATE' | 'WEAK' | 'UNKNOWN'
  rationale?: string
  evidenceRefs?: string[]
}

export interface NeedReference {
  needId: string
  needVersionId?: string
  needStatus: 'VERIFIED_FACT' | 'HUMAN_CONFIRMED' | 'INFERRED_NEED' | 'UNKNOWN' | 'CONFLICT'
  evidenceRefs?: string[]
}

export interface RecommendationReason {
  text: string
  evidenceRefs: string[]
  sourceType?: 'FACT' | 'KNOWLEDGE' | 'RULE' | 'INTERACTION'
}

export interface PortfolioMember {
  productId: string
  productVersion: string
  role: 'PRIMARY' | 'SUPPORTING'
  servedNeedId?: string
  evidenceRefs?: string[]
}

export interface PortfolioDependency {
  from: string
  to: string
  type: 'PREREQUISITE' | 'SEQUENCE' | 'COMPLEMENTARY'
  note?: string
}

export interface PortfolioConflict {
  productA: string
  productB: string
  kind: 'MUTUAL_EXCLUSION' | 'DUPLICATE' | 'SALES_BOUNDARY'
  reasonCode?: string
  evidenceRefs?: string[]
}

export interface ProductPortfolioCandidate {
  schemaVersion?: string
  portfolioId: string
  primaryProduct: PortfolioMember
  supportingProducts?: PortfolioMember[]
  dependencies?: PortfolioDependency[]
  conflicts?: PortfolioConflict[]
  recommendationCategory?: 'IMMEDIATE_COMMUNICATE' | 'SUPPLEMENT_FACTS_THEN_EVALUATE' | 'EXPERT_REVIEW_REQUIRED'
  rationale?: string
  evidenceRefs?: string[]
}

export interface NeedProfileItem {
  needId: string
  needType?: string
  needStatus: 'VERIFIED_FACT' | 'HUMAN_CONFIRMED' | 'INFERRED_NEED' | 'UNKNOWN' | 'CONFLICT'
  evidenceRefs?: string[]
  priority?: number
}

// ===================== 人工决定（对齐 recommendation-human-decision.schema.json） =====================

export type RecommendationDecision = 'APPROVE' | 'MODIFY' | 'REJECT' | 'HOLD'

export type StructuredModificationKind =
  | 'REMOVE_CANDIDATE'
  | 'REORDER_CANDIDATE'
  | 'MOVE_TO_REVIEW'
  | 'ADD_SUPPORTING_PRODUCT'
  | 'REMOVE_SUPPORTING_PRODUCT'
  | 'CHANGE_NEXT_ACTION'
  | 'ADD_CONFIRMED_FACT'

export interface StructuredModification {
  kind: StructuredModificationKind
  targetProductId?: string
  targetPortfolioId?: string
  fromPosition?: number
  toPosition?: number
  value?: string
  note?: string
}

export interface RecommendationHumanDecision {
  schemaVersion?: string
  gateId?: string
  runId: string
  proposalVersionId: string
  expectedVersion?: string
  decision: RecommendationDecision
  modifications?: StructuredModification[]
  reason?: string
  actorId: string
  actorRole?: string
  decidedAt: string
}

// ===================== API 调用 =====================

/** 创建产品推荐运行。要求 Idempotency-Key；同一幂等键返回同一 run。 */
export async function createProductRecommendationRun(
  request: ProductRecommendationCreateRequest,
  idempotencyKey: string,
): Promise<ProductRecommendationRun> {
  const { data } = await prApi.post<ProductRecommendationRun>('/product-recommendation-runs', request, {
    headers: { 'Idempotency-Key': idempotencyKey },
  })
  return data
}

/** 查询总体状态和当前版本。无副作用，不得触发 KERT 生成。 */
export async function getProductRecommendationRun(runId: string): Promise<ProductRecommendationRun> {
  const { data } = await prApi.get<ProductRecommendationRun>(`/product-recommendation-runs/${runId}`)
  return data
}

/** 查询三段式阶段结果（只读组合视图，不触发生成）。 */
export async function getProductRecommendationStages(runId: string): Promise<ProductRecommendationStageResult> {
  const { data } = await prApi.get<ProductRecommendationStageResult>(`/product-recommendation-runs/${runId}/stages`)
  return data
}

/** 查询不可变方案版本。 */
export async function getProductRecommendationVersion(
  runId: string,
  versionId: string,
): Promise<ProductRecommendationProposalVersion> {
  const { data } = await prApi.get<ProductRecommendationProposalVersion>(
    `/product-recommendation-runs/${runId}/versions/${versionId}`,
  )
  return data
}

/** 对可重试失败发起新 attempt。 */
export async function retryProductRecommendationRun(runId: string): Promise<ProductRecommendationRun> {
  const { data } = await prApi.post<ProductRecommendationRun>(`/product-recommendation-runs/${runId}/retry`)
  return data
}

/** 派工口径的短别名（createRun/getRun/getStages/getVersion/retry）。 */
export const createRun = createProductRecommendationRun
export const getRun = getProductRecommendationRun
export const getStages = getProductRecommendationStages
export const getVersion = getProductRecommendationVersion
export const retry = retryProductRecommendationRun

// ===================== 工具 =====================

/**
 * 判断错误是否为「KERT 不可达」（受控失败空态，INV-07 fail-closed）。
 * 网络级失败（无 response）或上游网关 502/503/504 视为 KERT 不可达；
 * 其余业务/客户端错误不算 KERT 不可达。
 */
export function isKertUnreachable(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return true
    }
    return [502, 503, 504].includes(error.response.status)
  }
  return false
}

// ===================== 枚举标签 =====================

export const RECOMMENDATION_RUN_STATUS_LABELS: Record<RecommendationRunStatus, string> = {
  REQUESTED: '已请求',
  CONTEXT_ASSEMBLING: '上下文装配中',
  HARD_FILTERING: '硬约束过滤中',
  MATCHING: '需求匹配中',
  PROPOSAL_READY: '方案已就绪',
  AWAITING_HUMAN: '待人工决定',
  APPROVED: '已采纳',
  MODIFIED: '已修改采纳',
  REJECTED: '已驳回',
  HELD: '已暂缓',
  STALE_REQUIRES_RERUN: '已过期需重跑',
  FAILED_CLOSED: '失败关闭',
}

export const RECOMMENDATION_DECISION_LABELS: Record<RecommendationDecision, string> = {
  APPROVE: '采纳',
  MODIFY: '修改后采纳',
  REJECT: '驳回',
  HOLD: '暂缓',
}

export const ELIGIBILITY_STATUS_LABELS: Record<EligibilityStatus, string> = {
  ELIGIBLE: '合格',
  INELIGIBLE: '不合格',
  UNKNOWN: '未知（事实缺失）',
  REVIEW_REQUIRED: '需复核',
}

export const STRUCTURED_MODIFICATION_KIND_LABELS: Record<StructuredModificationKind, string> = {
  REMOVE_CANDIDATE: '移除候选产品',
  REORDER_CANDIDATE: '调整候选顺序',
  MOVE_TO_REVIEW: '转入复核',
  ADD_SUPPORTING_PRODUCT: '新增配套产品',
  REMOVE_SUPPORTING_PRODUCT: '移除配套产品',
  CHANGE_NEXT_ACTION: '更改后续行动',
  ADD_CONFIRMED_FACT: '补充已确认事实',
}

export const PORTFOLIO_CATEGORY_LABELS: Record<
  NonNullable<ProductPortfolioCandidate['recommendationCategory']>,
  string
> = {
  IMMEDIATE_COMMUNICATE: '可立即沟通',
  SUPPLEMENT_FACTS_THEN_EVALUATE: '补充事实后评估',
  EXPERT_REVIEW_REQUIRED: '需专家复核',
}
