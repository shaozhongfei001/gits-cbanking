import axios from 'axios'
import { getApiKey, clearApiKey } from './auth'

const knowledgeApi = axios.create({
  baseURL: '/api/v1/knowledge',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器: 注入API Key
knowledgeApi.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

// 响应拦截器: 401时清除认证并提示
knowledgeApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearApiKey()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

// ===================== 类型定义（对齐后端 KnowledgeElement 合同）=====================

/** 知识要素类型（生产方式维度，权威规范定义） */
export type ElementKind =
  | 'K-Type-F'
  | 'K-Type-R'
  | 'K-Type-P'
  | 'K-Type-E'
  | 'K-Type-M'
  | 'K-Type-F/R'

/** 权威来源标注 */
export type Authority = 'AUTHORITATIVE' | 'REFERENCE' | 'DERIVED' | 'SYNTHETIC'

/** 知识要素（对齐 CTR-KELEM-001） */
export interface KnowledgeElement {
  schemaVersion: string
  elementId: string
  name: string
  kind: ElementKind
  knowledgeItemId: string
  content: string
  source: {
    sourceRef: string
    authority: Authority
  }
  relatedRules?: string[]
  status: 'DRAFT' | 'VALIDATION' | 'ACTIVE' | 'RETIRED'
}

/** 知识条目摘要（/items 端点） */
export interface KnowledgeItem {
  knowledgeItemId: string
  elementCount: number
  firstElementName: string
}

/** 拉取全部知识要素 */
export function fetchAllElements(): Promise<KnowledgeElement[]> {
  return knowledgeApi.get('/elements').then((r) => r.data)
}

/** 拉取指定 KI 下要素 */
export function fetchElementsByItem(kiId: string): Promise<KnowledgeElement[]> {
  return knowledgeApi.get(`/items/${kiId}`).then((r) => r.data)
}

/** 拉取知识条目清单 */
export function fetchKnowledgeItems(): Promise<KnowledgeItem[]> {
  return knowledgeApi.get('/items').then((r) => r.data)
}

/** 拉取知识地图（按 KI 分组的要素映射）。P38 客户经营页不得调用本接口。 */
export function fetchKnowledgeMap(): Promise<Record<string, KnowledgeElement[]>> {
  return knowledgeApi.get('/map').then((r) => r.data)
}
