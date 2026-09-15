import axios from 'axios'
import { getApiKey, clearApiKey } from './auth'
import type { RecommendationDecision, StructuredModification } from './productRecommendation'

// V1.1 新增实体的API客户端
const v11Api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

v11Api.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

v11Api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearApiKey()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

// ===================== 类型定义 =====================

export type CommitmentType = 'RM_COMMITMENT' | 'CUSTOMER_COMMITMENT' | 'REGULATORY_COMMITMENT'
export type CommitmentStatus = 'OPEN' | 'FULFILLED' | 'BREACHED' | 'WAIVED'

export type TaskType = 'FOLLOW_UP' | 'DOCUMENT_COLLECTION' | 'APPROVAL' | 'REVIEW' | 'COMPLIANCE_CHECK'
export type TaskStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'

export type OpportunityType = 'FINANCING' | 'DEPOSIT' | 'SETTLEMENT' | 'INVESTMENT' | 'INSURANCE' | 'ADVISORY'
export type OpportunityStage = 'IDENTIFIED' | 'QUALIFIED' | 'PROPOSAL' | 'NEGOTIATION' | 'CLOSED_WON' | 'CLOSED_LOST'

export type ExternalEventType = 'OFFICIAL_ANNOUNCEMENT' | 'INDUSTRY' | 'NEWS' | 'REGULATORY' | 'SOCIAL_MEDIA'
export type ExternalEventConfidence = 'HIGH' | 'MEDIUM' | 'LOW'
export type ExternalEventReliability = 'VERIFIED' | 'UNVERIFIED' | 'DISPUTED'

export type RecordingConsentStatus = 'GRANTED' | 'DENIED' | 'PENDING' | 'REVOKED'

export interface Commitment {
  commitmentId: string
  operatingCaseId?: string
  journeyId?: string
  commitmentType: CommitmentType
  content: string
  owner?: string
  dueDate?: string
  status: CommitmentStatus
  evidenceRef?: string
  createdAt?: string
  fulfilledAt?: string
}

export interface Task {
  taskId: string
  interactionId?: string
  operatingCaseId?: string
  customerId?: string
  taskType: TaskType
  title: string
  description?: string
  assignedTo?: string
  dueDate?: string
  status: TaskStatus
  parentTaskId?: string
  createdAt?: string
  completedAt?: string
}

export interface Opportunity {
  opportunityId: string
  customerId: string
  opportunityType: OpportunityType
  stage: OpportunityStage
  estimatedAmount?: number
  currency?: string
  description: string
  assignedTo?: string
  sourceSignalId?: string
  probability?: number
  expectedCloseDate?: string
  createdAt?: string
  updatedAt?: string
}

export interface ExternalEvent {
  eventId: string
  eventDate: string
  sourceType: ExternalEventType
  sourceName?: string
  entity?: string
  title: string
  content: string
  confidence?: ExternalEventConfidence
  reliability?: ExternalEventReliability
  bankUseAllowed?: boolean
  linkedThemes?: string[]
  possibleBusinessSignal?: string
  noGoStatement?: string
  evidenceRef?: string
}

export interface ProductKnowledgeVersion {
  versionId: string
  productId: string
  version: string
  category?: string
  content: string
  changeSummary?: string
  effectiveFrom: string
  effectiveTo?: string
  createdAt?: string
}

export interface RecordingConsent {
  consentId: string
  interactionId: string
  customerId?: string
  consentStatus: RecordingConsentStatus
  consentMethod?: string
  recordingPurpose?: string
  grantedAt?: string
  revokedAt?: string
}

// ===================== Commitment API =====================

export async function fetchCommitment(commitmentId: string): Promise<Commitment> {
  const { data } = await v11Api.get(`/commitments/${commitmentId}`)
  return data
}

export async function fetchCommitments(params: {
  interactionId?: string
  customerId?: string
  status?: CommitmentStatus
}): Promise<Commitment[]> {
  const { data } = await v11Api.get('/commitments', { params })
  return data
}

export async function fetchOverdueCommitments(): Promise<Commitment[]> {
  const { data } = await v11Api.get('/commitments/overdue')
  return data
}

export async function createCommitment(commitment: Partial<Commitment>): Promise<Commitment> {
  const { data } = await v11Api.post('/commitments', commitment)
  return data
}

export async function updateCommitmentStatus(commitmentId: string, status: CommitmentStatus): Promise<void> {
  await v11Api.put(`/commitments/${commitmentId}/status`, { status })
}

// ===================== Task API =====================

export async function fetchTask(taskId: string): Promise<Task> {
  const { data } = await v11Api.get(`/tasks/${taskId}`)
  return data
}

export async function fetchTasks(params: {
  interactionId?: string
  customerId?: string
  operatingCaseId?: string
  assignedTo?: string
}): Promise<Task[]> {
  const { data } = await v11Api.get('/tasks', { params })
  return data
}

export async function fetchOverdueTasks(): Promise<Task[]> {
  const { data } = await v11Api.get('/tasks/overdue')
  return data
}

export async function createTask(task: Partial<Task>): Promise<Task> {
  const { data } = await v11Api.post('/tasks', task)
  return data
}

export async function updateTaskStatus(taskId: string, status: TaskStatus): Promise<void> {
  await v11Api.put(`/tasks/${taskId}/status`, { status })
}

// ===================== Opportunity API =====================

export async function fetchOpportunity(opportunityId: string): Promise<Opportunity> {
  const { data } = await v11Api.get(`/opportunities/${opportunityId}`)
  return data
}

export async function fetchOpportunities(params: {
  customerId?: string
  status?: OpportunityStage
  opportunityType?: OpportunityType
  assignedTo?: string
}): Promise<Opportunity[]> {
  const { data } = await v11Api.get('/opportunities', { params })
  return data
}

export async function fetchActiveOpportunities(customerId: string): Promise<Opportunity[]> {
  const { data } = await v11Api.get(`/opportunities/${customerId}/active`)
  return data
}

export async function createOpportunity(opportunity: Partial<Opportunity>): Promise<Opportunity> {
  const { data } = await v11Api.post('/opportunities', opportunity)
  return data
}

export async function updateOpportunityStage(opportunityId: string, stage: OpportunityStage): Promise<void> {
  await v11Api.put(`/opportunities/${opportunityId}/status`, { stage })
}

// ===================== ExternalEvent API =====================

export async function fetchExternalEvent(eventId: string): Promise<ExternalEvent> {
  const { data } = await v11Api.get(`/external-events/${eventId}`)
  return data
}

export async function fetchExternalEvents(params: {
  eventType?: ExternalEventType
  customerId?: string
  industry?: string
  confidence?: ExternalEventConfidence
}): Promise<ExternalEvent[]> {
  const { data } = await v11Api.get('/external-events', { params })
  return data
}

export async function fetchRecentExternalEvents(limit: number = 20): Promise<ExternalEvent[]> {
  const { data } = await v11Api.get('/external-events/recent', { params: { limit } })
  return data
}

export async function createExternalEvent(event: Partial<ExternalEvent>): Promise<ExternalEvent> {
  const { data } = await v11Api.post('/external-events', event)
  return data
}

// ===================== ProductKnowledgeVersion API =====================

export async function fetchProductKnowledgeVersion(versionId: string): Promise<ProductKnowledgeVersion> {
  const { data } = await v11Api.get(`/product-knowledge/versions/${versionId}`)
  return data
}

export async function fetchProductKnowledgeVersions(params: {
  productId?: string
  category?: string
}): Promise<ProductKnowledgeVersion[]> {
  const { data } = await v11Api.get('/product-knowledge', { params })
  return data
}

export async function fetchLatestProductKnowledge(productId: string): Promise<ProductKnowledgeVersion> {
  const { data } = await v11Api.get(`/product-knowledge/latest/${productId}`)
  return data
}

export async function fetchRecentProductKnowledge(limit: number = 20): Promise<ProductKnowledgeVersion[]> {
  const { data } = await v11Api.get('/product-knowledge/recent', { params: { limit } })
  return data
}

export async function createProductKnowledgeVersion(version: Partial<ProductKnowledgeVersion>): Promise<ProductKnowledgeVersion> {
  const { data } = await v11Api.post('/product-knowledge', version)
  return data
}

// ===================== RecordingConsent API =====================

export async function fetchRecordingConsent(consentId: string): Promise<RecordingConsent> {
  const { data } = await v11Api.get(`/recording-consents/${consentId}`)
  return data
}

export async function fetchRecordingConsents(params: {
  interactionId?: string
  customerId?: string
  status?: RecordingConsentStatus
}): Promise<RecordingConsent[]> {
  const { data } = await v11Api.get('/recording-consents', { params })
  return data
}

export async function fetchLatestRecordingConsent(interactionId: string): Promise<RecordingConsent> {
  const { data } = await v11Api.get(`/recording-consents/latest/${interactionId}`)
  return data
}

export async function createRecordingConsent(consent: Partial<RecordingConsent>): Promise<RecordingConsent> {
  const { data } = await v11Api.post('/recording-consents', consent)
  return data
}

export async function updateRecordingConsentStatus(consentId: string, status: RecordingConsentStatus): Promise<void> {
  await v11Api.put(`/recording-consents/${consentId}/status`, { status })
}

// ===================== 枚举映射 =====================

export const COMMITMENT_TYPE_LABELS: Record<CommitmentType, string> = {
  RM_COMMITMENT: '客户经理承诺',
  CUSTOMER_COMMITMENT: '客户承诺',
  REGULATORY_COMMITMENT: '合规承诺'
}

export const COMMITMENT_STATUS_LABELS: Record<CommitmentStatus, string> = {
  OPEN: '待履行',
  FULFILLED: '已履行',
  BREACHED: '已违约',
  WAIVED: '已豁免'
}

export const TASK_TYPE_LABELS: Record<TaskType, string> = {
  FOLLOW_UP: '跟进',
  DOCUMENT_COLLECTION: '文档收集',
  APPROVAL: '审批',
  REVIEW: '审核',
  COMPLIANCE_CHECK: '合规检查'
}

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  PENDING: '待处理',
  IN_PROGRESS: '进行中',
  COMPLETED: '已完成',
  CANCELLED: '已取消'
}

export const OPPORTUNITY_TYPE_LABELS: Record<OpportunityType, string> = {
  FINANCING: '融资',
  DEPOSIT: '存款',
  SETTLEMENT: '结算',
  INVESTMENT: '投资',
  INSURANCE: '保险',
  ADVISORY: '咨询'
}

export const OPPORTUNITY_STAGE_LABELS: Record<OpportunityStage, string> = {
  IDENTIFIED: '已识别',
  QUALIFIED: '已确认',
  PROPOSAL: '方案提议',
  NEGOTIATION: '谈判中',
  CLOSED_WON: '已赢单',
  CLOSED_LOST: '已输单'
}

export const EXTERNAL_EVENT_TYPE_LABELS: Record<ExternalEventType, string> = {
  OFFICIAL_ANNOUNCEMENT: '官方公告',
  INDUSTRY: '行业动态',
  NEWS: '新闻',
  REGULATORY: '监管法规',
  SOCIAL_MEDIA: '社交媒体'
}

export const EXTERNAL_EVENT_CONFIDENCE_LABELS: Record<ExternalEventConfidence, string> = {
  HIGH: '高',
  MEDIUM: '中',
  LOW: '低'
}

export const EXTERNAL_EVENT_RELIABILITY_LABELS: Record<ExternalEventReliability, string> = {
  VERIFIED: '已验证',
  UNVERIFIED: '未验证',
  DISPUTED: '有争议'
}

export const RECORDING_CONSENT_STATUS_LABELS: Record<RecordingConsentStatus, string> = {
  GRANTED: '已授权',
  DENIED: '已拒绝',
  PENDING: '待确认',
  REVOKED: '已撤销'
}

// ===================== V1.1 Human Gate 类型 =====================

export type GateType =
  | 'A01_OUTREACH' | 'A02_SIGNAL_CONFIRM' | 'A03_OPPORTUNITY_VALIDATE'
  | 'B01_CONTEXT_ENRICH' | 'B02_FACT_VALIDATE'
  | 'C01_PREVISIT_APPROVE' | 'C02_REPORT_APPROVE'
  | 'D01_PRODUCT_RECOMMEND' | 'E01_EXIT_CONFIRM'
  | 'F01_CRM_WRITEBACK' | 'F02_CREDIT_CHECK' | 'F03_PRICE_APPROVE'
  | 'F04_RISK_REVIEW' | 'F05_RECORDING_APPROVE' | 'F06_CONTROLLED_ACTION'

export type HumanGateStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'MODIFIED'
export type GateDecision = 'APPROVE' | 'REJECT' | 'MODIFY' | 'HOLD' | 'DECLINE'

export interface HumanGate {
  gateId: string
  gateType: GateType
  journeyId?: string
  customerId?: string
  operatingCaseId?: string
  status: HumanGateStatus
  subject: string
  proposal?: Record<string, unknown>
  evidenceRefs?: string[]
  decision?: GateDecision
  modification?: Record<string, unknown>
  decisionReason?: string
  actorId?: string
  createdAt: string
  decidedAt?: string
}

export interface HumanGateDecisionRequest {
  decision: GateDecision
  modification?: Record<string, unknown>
  reason?: string
  actorId: string
}

// ===================== HG-D01 结构化人工决定（对齐 recommendation-human-decision.schema.json） =====================

export interface RecommendationHumanDecisionRequest {
  schemaVersion?: string
  runId: string
  proposalVersionId: string
  expectedVersion?: string
  decision: RecommendationDecision
  modifications?: StructuredModification[]
  reason?: string
  actorId: string
  actorRole?: string
}

export interface RecommendationHumanDecisionResult {
  decisionId: string
  gateId: string
  runId: string
  proposalVersionId: string
  decision: RecommendationDecision
  modifications?: StructuredModification[]
  reason?: string
  actorId: string
  actorRole?: string
  decidedAt: string
}

// ===================== V1.1 CRM Writeback 类型 =====================

export type CrmWritebackStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'SENT' | 'FAILED'

export interface CrmWritebackCommand {
  commandId: string
  journeyId?: string
  customerId?: string
  operatingCaseId?: string
  operation: string
  targetEntity: string
  payload: Record<string, unknown>
  status: CrmWritebackStatus
  humanConfirmationRequired: boolean
  decision?: string
  modifications?: Record<string, unknown>[]
  decisionReason?: string
  actorId?: string
  createdAt: string
  decidedAt?: string
  sentAt?: string
}

export interface CrmWritebackDecisionRequest {
  decision: GateDecision
  modifications?: Record<string, unknown>[]
  reason?: string
  actorId: string
}

// ===================== V1.1 Evidence Version 类型 =====================

export interface EvidenceVersion {
  versionId: string
  evidenceId: string
  version: number
  changeDescription?: string
  previousVersionId?: string
  createdBy?: string
  createdAt: string
}

// ===================== V1.1 Audit Trace 类型 =====================

export interface AuditTraceEntry {
  traceId: string
  entityType: string
  entityId: string
  operation: string
  beforeSnapshot?: Record<string, unknown>
  afterSnapshot?: Record<string, unknown>
  actorId?: string
  actorRole?: string
  occurredAt: string
  correlationId?: string
}

// ===================== Human Gate API =====================

export async function fetchHumanGates(params: {
  status?: HumanGateStatus
  gateType?: GateType
  journeyId?: string
  customerId?: string
}): Promise<HumanGate[]> {
  const { data } = await v11Api.get('/human-gates', { params })
  return data
}

export async function fetchHumanGate(gateId: string): Promise<HumanGate> {
  const { data } = await v11Api.get(`/human-gates/${gateId}`)
  return data
}

export async function decideHumanGate(gateId: string, request: HumanGateDecisionRequest): Promise<HumanGate> {
  const { data } = await v11Api.post(`/human-gates/${gateId}/decide`, request)
  return data
}

/** D01（产品推荐）结构化人工决定：POST /human-gates/{gateId}/decide，携带结构化 payload（含 proposalVersionId）。 */
export async function decideRecommendationHumanGate(
  gateId: string,
  request: RecommendationHumanDecisionRequest,
): Promise<RecommendationHumanDecisionResult> {
  const { data } = await v11Api.post(`/human-gates/${gateId}/decide`, request)
  return data
}

// ===================== CRM Writeback API =====================

export async function fetchCrmWritebackCommands(params: {
  status?: string
  journeyId?: string
  customerId?: string
}): Promise<CrmWritebackCommand[]> {
  const { data } = await v11Api.get('/crm/writeback-commands', { params })
  return data
}

export async function fetchCrmWritebackCommand(commandId: string): Promise<CrmWritebackCommand> {
  const { data } = await v11Api.get(`/crm/writeback-commands/${commandId}`)
  return data
}

export async function decideCrmWritebackCommand(commandId: string, request: CrmWritebackDecisionRequest): Promise<CrmWritebackCommand> {
  const { data } = await v11Api.post(`/crm/writeback-commands/${commandId}/decide`, request)
  return data
}

// ===================== Evidence Version API =====================

export async function fetchEvidenceVersions(evidenceId: string): Promise<EvidenceVersion[]> {
  const { data } = await v11Api.get(`/evidences/${evidenceId}/versions`)
  return data
}

// ===================== Audit Trace API =====================

export async function fetchAuditTrace(params: {
  entityType?: string
  entityId?: string
  actorId?: string
  from?: string
  to?: string
}): Promise<AuditTraceEntry[]> {
  const { data } = await v11Api.get('/audit-trace', { params })
  return data
}

// ===================== V1.1 枚举标签 =====================

export const GATE_TYPE_LABELS: Record<GateType, string> = {
  A01_OUTREACH: '外联触达',
  A02_SIGNAL_CONFIRM: '信号确认',
  A03_OPPORTUNITY_VALIDATE: '商机验证',
  B01_CONTEXT_ENRICH: '上下文补充',
  B02_FACT_VALIDATE: '事实校验',
  C01_PREVISIT_APPROVE: '访前审批',
  C02_REPORT_APPROVE: '报告审批',
  D01_PRODUCT_RECOMMEND: '产品推荐',
  E01_EXIT_CONFIRM: '离场确认',
  F01_CRM_WRITEBACK: 'CRM写回',
  F02_CREDIT_CHECK: '授信审查',
  F03_PRICE_APPROVE: '定价审批',
  F04_RISK_REVIEW: '风险复核',
  F05_RECORDING_APPROVE: '录音授权',
  F06_CONTROLLED_ACTION: '受控行动'
}

export const HUMAN_GATE_STATUS_LABELS: Record<HumanGateStatus, string> = {
  PENDING: '待审批',
  APPROVED: '已批准',
  REJECTED: '已驳回',
  MODIFIED: '已修改'
}

export const GATE_DECISION_LABELS: Record<GateDecision, string> = {
  APPROVE: '批准',
  REJECT: '驳回',
  MODIFY: '修改后批准',
  HOLD: '暂缓',
  DECLINE: '拒绝'
}

export const CRM_WRITEBACK_STATUS_LABELS: Record<CrmWritebackStatus, string> = {
  PENDING: '待审批',
  APPROVED: '已批准',
  REJECTED: '已驳回',
  SENT: '已发送',
  FAILED: '发送失败'
}
