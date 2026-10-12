import axios from 'axios'
import { getApiKey, clearApiKey } from './auth'

/**
 * 企业金融产品中心 API 客户端（CTR-PKC-API-001 · Loop PC1）。
 *
 * 纪律：类型逐项对齐合同，**禁止发明后端未定义字段**；
 * PC1 只消费三个只读端点（families / products / products/{productId}）。
 */
const api = axios.create({
  baseURL: '/api/v1/product-center',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearApiKey()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

/** 合同 PkcProductFamily。 */
export interface ProductCenterFamily {
  familyId: string
  familyName: string
  parentFamilyId: string | null
  domainId: string
  domainName: string
  displayOrder: number
  visibilityScope: string
  activeProductCount: number
  unclassifiedCount: number
}

/** 合同 PkcProductCatalogEntry。 */
export interface ProductCenterProductEntry {
  productId: string
  productCode: string
  productName: string
  aliases: string[]
  familyId: string
  familyName: string
  lifecycleStatus: 'ACTIVE' | 'SUSPENDED' | 'RETIRED'
  currentPublishedVersionId: string | null
  hasPublishedVersion: boolean
  environment: 'DEMO' | 'UAT' | 'PROD'
  isDemo: boolean
}

/** 合同 PkcVersionSummary。 */
export interface ProductCenterVersionSummary {
  versionId: string
  versionLabel: string
  versionStatus: string
  knowledgeAsOf: string | null
  effectiveFrom: string | null
  effectiveTo: string | null
  publishedAt: string | null
  publishedBy: string | null
  reviewedBy: string[]
  reviewRecordId: string | null
  nextReviewAt: string | null
  changeSummary: string
  changeReason: string | null
  evidenceSnapshotId: string | null
  environment: 'DEMO' | 'UAT' | 'PROD'
  isDemo: boolean
}

/** 合同 PkcProductSummary；null = 待核验（不得用文案冒充）。 */
export interface ProductCenterSummary {
  oneSentenceDefinition: string | null
  boundaryStatement: string | null
  productPurpose: string | null
  usageMode: string | null
  interestSummary: string | null
  eligibleEntitySummary: string | null
  solves: string | null
  isNot: string | null
  nearestDifference: string | null
}

/** 合同 PkcDisclosureLevel（披露级别；取值由合同枚举定义，此处不作本地收窄）。 */
export type PkcDisclosureLevel = string

/** 合同 PkcEvidenceRef（依据引用）。 */
export interface PkcEvidenceRef {
  evidenceId: string
  evidenceType: string
  evidenceClass: string
  title: string
  documentNumber: string | null
  documentVersion: string
  effectiveFrom: string | null
  effectiveTo: string | null
  ownerOrg: string
  sourceRef: string
  anchor: string | null
  accessLevel: PkcDisclosureLevel
  verificationState: string
  contentHash: string | null
  isDemo: boolean
}

/** 合同 PkcCertaintyType（确定性类型枚举，逐字对齐合同）。 */
export type PkcCertaintyType =
  | 'VERIFIED'
  | 'PENDING_VERIFICATION'
  | 'APPROVAL_VARIABLE'
  | 'PRICING_VARIABLE'
  | 'CONFLICTING'
  | 'EXPIRED'
  | 'NOT_APPLICABLE'

/** 合同 PkcTerm（八章 · 02 核心条款）。 */
export interface PkcTerm {
  termId: string
  termKey: string
  businessDefinition: string | null
  explanationForRm: string | null
  certaintyType: PkcCertaintyType
  displayOrder: number
  evidenceRefs: PkcEvidenceRef[]
  conflictId: string | null
}

/** 合同 PkcBoundary（八章 · 03 适用边界）。 */
export interface PkcBoundary {
  boundaryId: string
  boundaryType: string
  scenarioName: string
  scenarioDescription: string
  alternativeDirection: string | null
  evidenceRefs: PkcEvidenceRef[]
}

/** 合同 PkcPrerequisite（八章 · 03 适用边界 的前置条件）。 */
export interface PkcPrerequisite {
  prerequisiteId: string
  prerequisiteType: string
  requirementText: string
  conditional: boolean
  evidenceRefs: PkcEvidenceRef[]
}

/** 合同 PkcProcessStep（八章 · 04 办理流程）。 */
export interface PkcProcessStep {
  stepId: string
  sequence: number
  stepName: string
  summary: string
  actors: string[]
  inputs: string[]
  outputs: string[]
  exceptions: Record<string, unknown>[]
  humanDecisionRequired: boolean
  slaReference: string | null
  evidenceRefs: PkcEvidenceRef[]
}

/** 合同 PkcMaterialItem（八章 · 05 申请材料）。 */
export interface PkcMaterialItem {
  materialId: string
  materialName: string
  requirementLevel: string
  conditionExpression: string | null
  purpose: string
  validityRule: string | null
  templateFileRef: string | null
  sampleFileRef: string | null
  scope: Record<string, unknown>
  evidenceRefs: PkcEvidenceRef[]
}

/** 合同 PkcMaterialGroup（八章 · 05 申请材料）。 */
export interface PkcMaterialGroup {
  groupType: string
  items: PkcMaterialItem[]
}

/** 八章 · 07 同类产品比较：维度。 */
export interface PkcComparisonDimension {
  dimensionId: string
  dimensionName: string
}

/** 八章 · 07 同类产品比较：比较行。 */
export interface PkcComparisonRow {
  productId: string
  versionId?: string
  values: Record<string, string | number | null>
}

/**
 * 合同 PkcComparisonSet（八章 · 07 同类产品比较）。
 *
 * 口径说明：合同对 `dimensions` / `rows` 声明为 `array<object>`（未定义字段级结构），
 * 上列 `PkcComparisonDimension` / `PkcComparisonRow` 按 `GET /api/v1/product-center/products/{id}`
 * **实测响应形状**收窄（2026-09-22 实测：`dimensionId`/`dimensionName`、`productId`/`values`/`versionId`）；
 * 若合同后续给出显式 schema，以合同为准（本条为实测注释，不构成字段发明）。
 */
export interface PkcComparisonSet {
  comparisonSetId: string
  comparisonAsOf: string
  dimensions: PkcComparisonDimension[]
  rows: PkcComparisonRow[]
  reviewState: string
}

/**
 * 合同 `PkcSalesBoundary`（八章 · 10 销售边界的**产品级**内容；R2 映射 `C10` 记为"仅通用 2 条 ⇒ 产品级缺失"）。
 */
export interface PkcSalesBoundary {
  boundaryId: string
  boundaryKind: 'ALLOWED_EXPLANATION' | 'PROHIBITED_PROMISE'
  text: string
  riskCategory: string
  mandatoryDisplay: boolean
}

/** 合同 PkcProductDetail（PC1 子集；章节集合在 PC2–PC4 接入）。 */
export interface ProductCenterDetail {
  productId: string
  productCode: string
  productName: string
  aliases: string[]
  familyId: string
  familyName: string
  tags: string[]
  publishStatus: string
  version: ProductCenterVersionSummary
  summary: ProductCenterSummary
  terms: PkcTerm[]
  boundaries: PkcBoundary[]
  prerequisites: PkcPrerequisite[]
  processSteps: PkcProcessStep[]
  materialGroups: PkcMaterialGroup[]
  pricingItems: unknown[]
  agreementClauses: unknown[]
  salesBoundaries: PkcSalesBoundary[]
  faqs: unknown[]
  comparison: PkcComparisonSet | null
  evidenceRefs: unknown[]
  fixedBoundaryStatements: string[]
  assistant: { enabled: boolean; quickQuestions: string[] }
  retrievalTrace: RetrievalTrace | null
}

/** 请求链路步骤。 */
export interface TraceStep {
  name: string
  description: string
  durationMs: number
  status: string
}

/** LightRAG 检索详情。 */
export interface LightRagTrace {
  query: string
  mode: string
  entityCount: number
  relationCount: number
  citationCount: number
  evidenceClass: string | null
  provenanceState: string | null
  simulationOnly: boolean | null
  retrievalMs: number
  entityNames: string[]
}

/** LightRAG 检索跟踪信息。 */
export interface RetrievalTrace {
  steps: TraceStep[]
  lightrag: LightRagTrace | null
  totalMs: number
}

/** 合同 PkcError。 */
export interface ProductCenterErrorBody {
  status: number
  error: string
  code: string
  message: string
  path: string
  timestamp: string
}

/** 产品族目录（PI-FR-009/010/014）。 */
export async function fetchProductCenterFamilies(): Promise<ProductCenterFamily[]> {
  const { data } = await api.get<ProductCenterFamily[]>('/families')
  return data
}

/** 产品目录（按族/关键词过滤）。 */
export async function fetchProductCenterProducts(params: {
  familyId?: string
  keyword?: string
} = {}): Promise<ProductCenterProductEntry[]> {
  const { data } = await api.get<ProductCenterProductEntry[]>('/products', { params })
  return data
}

/** 产品详情（PC1 子集）。 */
export async function fetchProductCenterDetail(productId: string): Promise<ProductCenterDetail> {
  const { data } = await api.get<ProductCenterDetail>(`/products/${encodeURIComponent(productId)}`)
  return data
}

/** 从 axios 错误中提取合同错误码（受控失败矩阵；无 code 时返回 null）。 */
export function extractErrorCode(error: unknown): string | null {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ProductCenterErrorBody | undefined
    return body?.code ?? null
  }
  return null
}
