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
  terms: unknown[]
  boundaries: unknown[]
  prerequisites: unknown[]
  processSteps: unknown[]
  materialGroups: unknown[]
  pricingItems: unknown[]
  agreementClauses: unknown[]
  salesBoundaries: unknown[]
  faqs: unknown[]
  comparison: unknown | null
  evidenceRefs: unknown[]
  fixedBoundaryStatements: string[]
  assistant: { enabled: boolean; quickQuestions: string[] }
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
