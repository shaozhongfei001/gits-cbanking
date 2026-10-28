import axios from 'axios'
import { getApiKey } from './auth'

/**
 * 产品卡 API（产品中心「产品解读」菜单使用）。
 *
 * 历史上的「产品知识」二菜单（/product-knowledge/interpretation，P38 老解读页）
 * 及其独占接口（三视图解读 + LightRAG 派生检索）已下线：
 * 后端 interpretation/retrieval 端点、KERT 解读投影快照与演示数据一并移除。
 * 卡片目录与章节投影链路保留。
 */

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

/** 产品卡摘要（产品全景列表项）。 */
export interface ProductCardSummary {
  productId: string
  name: string
  family: string
  familyName: string
  summary: string
  capabilities: string[]
  scenarios: string[]
  riskNotes: string[]
  sourceFile: string
}

/** 产品卡章节。 */
export interface ProductCardSection {
  title: string
  content: string
}

/** 产品卡详情（含原始产品文档全文）。 */
export interface ProductCardDetail {
  productId: string
  name: string
  family: string
  familyName: string
  owner: string
  summary: string
  sections: ProductCardSection[]
  sourceFile: string
  rawMarkdown: string
}

/** 产品卡目录列表（产品全景）。 */
export async function fetchProductCards(): Promise<ProductCardSummary[]> {
  const { data } = await api.get<never, { data: ProductCardSummary[] }>('/cards')
  return data
}

/** 单个产品卡详情（含原始文档全文）。 */
export async function fetchProductCardDetail(productId: string): Promise<ProductCardDetail> {
  const { data } = await api.get(`/cards/${encodeURIComponent(productId)}`)
  return data
}
