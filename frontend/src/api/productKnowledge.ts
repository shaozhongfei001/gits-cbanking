import axios from 'axios'
import { getApiKey } from './auth'

/** 类型严格对齐 CTR-PK-INT-001，禁止发明后端未定义字段。 */

export type InterpretationView = 'OVERVIEW' | 'ELIGIBILITY' | 'PRICING'
export type InterpretationPurpose = 'INTERPRETATION' | 'RECOMMENDATION'
export type KnowledgeState =
  | 'SUPPORTED'
  | 'UNKNOWN'
  | 'CONFLICT'
  | 'NOT_APPLICABLE'
  | 'STALE'

export interface EvidenceSummary {
  evidenceId: string
  sourceId: string
  sourceVersionId: string
  authorityLevel: 'INTERNAL_POLICY' | 'REGULATORY' | 'PUBLIC_PRICE_DISCLOSURE' | 'PUBLIC_MARKETING'
  locatorHint: string
  quoteExcerpt: string
}

export interface InterpretedField {
  fieldPath: string
  displayValue: string | null
  knowledgeState: KnowledgeState
  evidenceSummaries: EvidenceSummary[]
  conflictId: string | null
}

export interface InterpretationResponse {
  productId: string
  releaseId: string
  bundleHash: string
  view: InterpretationView
  purpose: InterpretationPurpose
  isStale: boolean
  fields: InterpretedField[]
  generatedAt: string
}

export interface ProductKnowledgeErrorResponse {
  status: number
  error: string
  code:
    | 'PRODUCT_KNOWLEDGE_NOT_PUBLISHED'
    | 'PURPOSE_NOT_ALLOWED'
    | 'RELEASE_STALE'
    | 'KNOWLEDGE_GATE_FAILED'
    | 'FAILED_CLOSED'
    | 'BAD_REQUEST'
  message: string
  path: string
  timestamp: string
}

/** 统一错误载体：把后端错误结构原样带给 UI，避免各页面自行拼装。 */
export class ProductKnowledgeError extends Error {
  readonly status: number
  readonly code: string
  readonly path: string
  readonly timestamp: string

  constructor(payload: ProductKnowledgeErrorResponse) {
    super(payload.message)
    this.name = 'ProductKnowledgeError'
    this.status = payload.status
    this.code = payload.code
    this.path = payload.path
    this.timestamp = payload.timestamp
  }
}

const api = axios.create({
  baseURL: '/api/v1/product-knowledge',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

export interface InterpretationQuery {
  productId: string
  view: InterpretationView
  purpose: InterpretationPurpose
}

export async function fetchInterpretation(
  query: InterpretationQuery
): Promise<InterpretationResponse> {
  try {
    const response = await api.get<InterpretationResponse>(
      `/${encodeURIComponent(query.productId)}/interpretation`,
      { params: { view: query.view, purpose: query.purpose } }
    )
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data) {
      const payload = error.response.data as ProductKnowledgeErrorResponse
      if (payload && typeof payload.code === 'string') {
        throw new ProductKnowledgeError(payload)
      }
    }
    throw error
  }
}
