import axios from 'axios'
import { getApiKey, clearApiKey } from './auth'

const api = axios.create({
  baseURL: '/api/v14',
  timeout: 180000, // SP-20 async 轮询需更长超时
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器: 注入API Key
api.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

// 响应拦截器: 401时清除认证并提示
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

// ===================== 类型定义 (契约 v1.4) =====================

export interface ServiceProposalContent {
  proposalDraft: string
  internalVersion: ServiceProposalVersion | null
  customerVersion: ServiceProposalVersion | null
  customerVersionNote: string
}

export interface ServiceProposalVersion {
  content: string
  factLabels: Record<string, string>
  filteringNotes: string[]
  includes: string[]
  excludes: string[]
  releaseBlockedUntil: string[]
}

export interface Citation {
  id: string
  claim: string
  source: string
  date: string
  factLabel: string
  chapterRef: string
}

export interface Unknown {
  id: string
  description: string
  suggestedAction: string
  relatedChapter: string
}

export interface GateCheck {
  gate: string
  state: string
  name: string
  checklist: Record<string, string[]>
}

export interface GateRecommendations {
  currentGate: string
  passedGates: string[]
  overallReadiness: string
  checklist: GateCheck[]
  nextGatePrerequisites: string[]
}

export interface RuleViolation {
  code: string
  severity: string
  message: string
  ruleRef?: string
}

export interface ServiceProposal {
  schemaVersion: string
  skillId: string
  runId: string
  status: string
  timestamp: string
  content: ServiceProposalContent
  citations: Citation[]
  unknowns: Unknown[]
  limitations: string[]
  gateRecommendations: GateRecommendations | null
  ruleViolations: RuleViolation[]
}

export interface CandidateMemory {
  memoryId: string
  category: string
  confidence: number
  suggestedDecayRule: string
  evidenceQuote: string
  content: string
}

export interface MemoryUpdate {
  memoryId: string
  action: string
  confidenceDelta: number
  reason: string
}

export interface MemorySupersession {
  supersededMemoryId: string
  newMemoryId: string
  reason: string
}

export interface InteractionMemoryExtraction {
  schemaVersion: string
  interactionId: string
  status: string
  candidateMemories: CandidateMemory[]
  memoryUpdates: MemoryUpdate[]
  memorySupersessions: MemorySupersession[]
  ruleViolations: RuleViolation[]
}

export interface GateDefinition {
  gateId: string
  name: string
  description: string
  criteria: string[]
}

export interface GateAssets {
  schemaVersion: string
  customerId: string
  flowName: string
  gates: GateDefinition[]
}

export interface GateSnapshot {
  customerId: string
  currentGate: string
  passedGates: string[]
  releaseReady: boolean
  checklist: Array<{ gate: string; state: string; evidence: string[] }>
}

// ===================== API 方法 =====================

/** SP-20: 生成服务建议书 (async 202+轮询由后端处理) */
export async function generateServiceProposal(requestId: string, customerId: string, context: Record<string, unknown>): Promise<ServiceProposal> {
  const { data } = await api.post<ServiceProposal>('/proposals', { requestId, customerId, context })
  return data
}

/** SP-21: 交互记忆抽取 */
export async function extractInteractionMemories(
  interactionId: string,
  customerId: string,
  interactionContent: string,
  existingMemories: unknown[] = []
): Promise<InteractionMemoryExtraction> {
  const { data } = await api.post<InteractionMemoryExtraction>('/memories/extract', {
    interactionId,
    customerId,
    interactionContent,
    existingMemories
  })
  return data
}

/** 闸门: 拉取 GATE-BIZ 清单资产 */
export async function fetchGateAssets(customerId: string): Promise<GateAssets> {
  const { data } = await api.get<GateAssets>(`/gates/assets/${customerId}`)
  return data
}

/** 闸门: GITS 权威状态快照 */
export async function fetchGateState(customerId: string): Promise<GateSnapshot> {
  const { data } = await api.get<GateSnapshot>(`/gates/state/${customerId}`)
  return data
}

/** 闸门: 镜像决策到 DKWS audit (失败不影响权威状态) */
export async function mirrorGateAudit(customerId: string, auditEntry: Record<string, unknown>): Promise<{ recorded: boolean }> {
  const { data } = await api.post<{ recorded: boolean }>('/gates/audit', { ...auditEntry, customerId })
  return data
}

export default api
