import axios from 'axios'
import { getApiKey, clearApiKey } from './auth'

const api = axios.create({
  baseURL: '/api/v1/engagement',
  timeout: 15000,
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

// ===================== 类型定义 =====================

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW'
export type Industry = 'MANUFACTURING' | 'FINANCE' | 'TECHNOLOGY' | 'REAL_ESTATE' | 'ENERGY' | 'HEALTHCARE' | 'AGRICULTURE' | 'LOGISTICS' | 'RETAIL' | 'OTHER'
export type EnterpriseScale = 'LARGE' | 'MEDIUM' | 'SMALL' | 'MICRO'
export type CustomerTier = 'STRATEGIC' | 'KEY' | 'GROWTH' | 'GENERAL'
export type ListedStatus = 'LISTED' | 'UNLISTED' | 'DELISTED'

export type JourneyPhase = 'KYC_COLLECT' | 'INSIGHT_ANALYSIS' | 'PRODUCT_MATCHING' | 'PREVISIT_PREP' | 'POSTVISIT_REVIEW' | 'COMPLETED'

export type SignalType = 'FINANCING_NEED' | 'PRODUCT_OPPORTUNITY' | 'RELATIONSHIP_CHANGE'
export type SignalSourceType = 'INTERACTION' | 'EXTERNAL_EVENT' | 'ANALYSIS'
export type SignalStatus = 'DETECTED' | 'CONFIRMED' | 'DISMISSED' | 'CONVERTED'

export type ReportType = 'INTERNAL_RELATIONSHIP' | 'CRM_CALL' | 'UPDATED_RELATIONSHIP' | 'NEXT_PREVISIT'

export type InteractionType = 'SIGNAL_TRIGGER' | 'AI_INSIGHT_PUSH' | 'PHONE_CALL' | 'FACE_TO_FACE_VISIT' | 'VIDEO_CONFERENCE' | 'INSTANT_MESSAGE' | 'EMAIL' | 'PRODUCT_PRESENTATION' | 'CUSTOMER_COMPLAINT' | 'FOLLOW_UP'
export type Direction = 'OUTBOUND' | 'INBOUND'
export type InteractionOutcome = 'COMPLETED' | 'CUSTOMER_AGREED' | 'CUSTOMER_DECLINED' | 'CUSTOMER_DEFERRED' | 'FOLLOW_UP_REQUIRED' | 'INTERRUPTED' | 'INFORMATION_GATHERED'

export interface Customer {
  customerId: string
  customerName: string
  customerShortName?: string
  unifiedSocialCreditCode?: string
  establishedDate?: string
  registeredCapitalCny?: number
  industry?: Industry
  region?: string
  enterpriseScale?: EnterpriseScale
  customerTier?: CustomerTier
  relationshipSince?: string
  rmId?: string
  rmName?: string
  managingBranch?: string
  groupFlag?: boolean
  listedStatus?: ListedStatus
  riskLevel?: RiskLevel
  mainProducts?: string[]
  coreTags?: string[]
  relationshipSummary?: string
  createdAt?: string
  updatedAt?: string
}

export interface CustomerJourney {
  journeyId: string
  operatingCaseId: string
  customerId: string
  customerName: string
  phase: JourneyPhase
  startedAt: string
  updatedAt?: string
}

export interface OperatingCase {
  caseId: string
  customerId: string
  caseType: string
  status: string
  createdAt?: string
  updatedAt?: string
}

export interface KycGapProfile {
  profileId: string
  customerId: string
  asOf: string
  knownItems: string[]
  partialKnownItems: string[]
  staleItems: string[]
  conflictingOrAmbiguousItems: string[]
  unknownItems: string[]
  priorityQuestions: string[]
}

export interface OpportunitySignal {
  signalId: string
  operatingCaseId?: string
  journeyId?: string
  signalType: SignalType
  content: string
  sourceType: SignalSourceType
  sourceRef?: string
  confidence?: number
  status: SignalStatus
  evidenceRef?: string
  detectedAt: string
  confirmedAt?: string
}

export interface RelationshipReport {
  reportId: string
  operatingCaseId?: string
  journeyId?: string
  reportType: ReportType
  content: string
  basedOnEvidence?: string[]
  basedOnReconciliations?: string[]
  generatedAt: string
  supersedesReportId?: string
}

export interface Interaction {
  interactionId: string
  caseId: string
  journeyId?: string
  type: InteractionType
  direction: Direction
  channel: string
  initiator: Participant
  participants?: Participant[]
  contentSummary?: string
  producedClaimIds?: string[]
  outcome: InteractionOutcome
  occurredAt: string
  endedAt?: string
}

export interface Participant {
  participantId: string
  role: string
  displayName: string
}

export interface Claim {
  claimId: string
  operatingCaseId?: string
  journeyId?: string
  claimType: string
  content: string
  status: string
  evidenceRefs?: string[]
  createdAt?: string
}

export interface TransactionRecord {
  transactionId: string
  customerId: string
  amount: number
  currency: string
  transactionType: string
  occurredAt: string
  description?: string
}

export interface CustomerContext {
  customer: Customer
  kycGapProfile?: KycGapProfile
  opportunitySignals: OpportunitySignal[]
  recentInteractions: Interaction[]
  activeJourneys: CustomerJourney[]
  recentTransactions: TransactionRecord[]
}

export interface PrevisitReport {
  reportId: string
  customerOverview: Customer
  kycGaps: KycGapProfile
  productRecommendations: string[]
  opportunitySignals: OpportunitySignal[]
  previousVisitSummary?: string
}

export interface PostvisitReport {
  reportId: string
  keyFindings: string[]
  opportunitySignals: OpportunitySignal[]
  commitments: string[]
  factReconciliation: { item: string; status: string }[]
  nextSteps: string[]
}


// ===================== API 调用 =====================
// 注意：后端API路径前缀为 /api/v1/engagement（axios baseURL）
//       以及 /api/journey、/api/case、/api/claim、/api/interaction、/api/evaluation
//       非 /api/v1/engagement 前缀的端点使用独立的 axios 实例

const rootApi = axios.create({
  baseURL: '',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

rootApi.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

rootApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearApiKey()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

/** 获取客户列表（按RM查询，rmId可选，不传则返回全部） */
export async function fetchCustomers(rmId?: string): Promise<Customer[]> {
  const params = rmId ? { rmId } : { rmId: 'ALL' }
  const { data } = await api.get('/customer', { params })
  return data
}

/** 获取客户详情（通过经营视图接口获取） */
export async function fetchCustomer(customerId: string): Promise<Customer> {
  const { data } = await api.get(`/customer/${customerId}/operating-view`)
  return data.customer
}

/** 获取客户上下文（含KYC、信号、交互、旅程、交易） */
export async function fetchCustomerContext(customerId: string): Promise<CustomerContext> {
  // 后端无单一上下文端点，组合多个调用
  const [operatingView, kycProfile, signals, transactions] = await Promise.allSettled([
    api.get(`/customer/${customerId}/operating-view`),
    api.get(`/kyc/${customerId}/gap-profile`),
    api.get(`/signal/${customerId}`),
    api.get(`/customer/${customerId}/transactions`)
  ])

  const viewData = operatingView.status === 'fulfilled' ? operatingView.value.data : null
  const kycData = kycProfile.status === 'fulfilled' ? kycProfile.value.data : undefined
  const signalsData = signals.status === 'fulfilled' ? signals.value.data : []
  const txData = transactions.status === 'fulfilled' ? transactions.value.data : []

  return {
    customer: viewData?.customer ?? { customerId, customerName: customerId },
    kycGapProfile: kycData,
    opportunitySignals: signalsData,
    recentInteractions: [],
    activeJourneys: [],
    recentTransactions: txData
  }
}

/** 获取客户旅程列表 */
export async function fetchCustomerJourneys(customerId: string): Promise<CustomerJourney[]> {
  try {
    // 后端: POST /api/v1/engagement/journey/open (启动旅程) 或 GET /api/journey/{journeyId}
    // 列表查询暂无专用端点，返回空数组
    return []
  } catch {
    return []
  }
}

/** 获取旅程详情 */
export async function fetchJourney(journeyId: string): Promise<CustomerJourney> {
  const { data } = await rootApi.get(`/api/journey/${journeyId}`)
  return data
}

/** 获取旅程交互记录 */
export async function fetchJourneyInteractions(journeyId: string): Promise<Interaction[]> {
  // 后端交互记录按 caseId 查询，需要 journey 中的 operatingCaseId
  const journey = await fetchJourney(journeyId)
  if (!journey.operatingCaseId) return []
  const { data } = await rootApi.get('/api/interaction', { params: { caseId: journey.operatingCaseId } })
  return data
}

/** 获取旅程主张列表 */
export async function fetchJourneyClaims(journeyId: string): Promise<Claim[]> {
  try {
    const journey = await fetchJourney(journeyId)
    if (!journey.operatingCaseId) return []
    const { data } = await rootApi.get(`/api/claim/case/${journey.operatingCaseId}`)
    return data
  } catch {
    return []
  }
}

/** 获取旅程机会信号 */
export async function fetchJourneySignals(journeyId: string): Promise<OpportunitySignal[]> {
  // 后端信号按 operatingCaseId 查询
  const journey = await fetchJourney(journeyId)
  if (!journey.operatingCaseId) return []
  const { data } = await api.get(`/signal/${journey.operatingCaseId}`)
  return data
}

/** 获取报告详情 — TODO: 后端需提供 /api/report/{reportId} 端点，当前返回占位数据 */
export async function fetchReport(reportId: string): Promise<RelationshipReport> {
  // 后端无独立报告端点，返回占位数据
  return {
    reportId,
    reportType: 'INTERNAL_RELATIONSHIP',
    content: '报告内容加载中...',
    generatedAt: new Date().toISOString()
  }
}

/** 获取经营案例列表 */
export async function fetchOperatingCases(customerId: string): Promise<OperatingCase[]> {
  try {
    // 后端: GET /api/v1/engagement/customer/{customerId}/operating-view
    const { data } = await rootApi.get(`/api/v1/engagement/customer/${customerId}/operating-view`)
    return data
  } catch {
    return []
  }
}

/** 执行访前报告生成 */
export async function executePrevisit(journeyId: string, customerId: string = '', operatingCaseId: string = '', visitObjective: string = ''): Promise<PrevisitExecutionResponse> {
  const { data } = await api.post(`/journey/${journeyId}/previsit`, {
    customerId,
    operatingCaseId,
    visitObjective
  })
  return data
}

/** 执行访后分析 */
export async function executePostvisit(journeyId: string, customerId: string = '', operatingCaseId: string = '', rawTranscript: string = ''): Promise<PostvisitExecutionResponse> {
  const { data } = await api.post(`/journey/${journeyId}/postvisit`, {
    customerId,
    operatingCaseId,
    rawTranscript
  })
  return data
}

/** 生成外联脚本 */
export async function generateOutreachScript(customerId: string, rmId: string = '', operatingCaseId: string = '', journeyId: string = '', channel: string = 'PHONE'): Promise<OutreachScriptResponse> {
  const { data } = await api.post('/journey/outreach-script', {
    customerId,
    rmId,
    operatingCaseId,
    journeyId,
    channel
  })
  return data
}

/** 生成会面脚本 */
export async function generateMeetingScript(customerId: string, rmId: string = '', operatingCaseId: string = '', journeyId: string = ''): Promise<MeetingScriptResponse> {
  const { data } = await api.post('/journey/meeting-script', {
    customerId,
    rmId,
    operatingCaseId,
    journeyId
  })
  return data
}

/** 一键访前自动准备响应（P23/G6，知识地图任务映射驱动） */
export interface PreparedPrevisitResponse {
  outreachScript: OutreachScriptResponse
  meetingScript: MeetingScriptResponse
  previsitReport: PrevisitExecutionResponse['previsitReport']
  battleCard: PrevisitExecutionResponse['battleCard']
  supplyChainMarkdown?: string
}

/** 一键访前自动准备：合并外联 + 会面 + R1 + R2 为一次调用（知识地图驱动） */
export async function preparePrevisit(
  journeyId: string,
  customerId: string,
  operatingCaseId: string,
  visitObjective: string = '',
  rmId: string = '',
  channel: string = 'EMAIL'
): Promise<PreparedPrevisitResponse> {
  const { data } = await api.post(`/journey/${journeyId}/prepare-previsit`, {
    customerId,
    rmId,
    operatingCaseId,
    journeyId,
    channel,
    visitObjective
  })
  return data
  return data
}

/** 获取KYC缺口画像 */
export async function fetchKycGapProfile(customerId: string): Promise<KycGapProfile> {
  const { data } = await api.get(`/kyc/${customerId}/gap-profile`)
  return data
}

/** 获取机会信号列表 */
export async function fetchOpportunitySignals(operatingCaseId: string): Promise<OpportunitySignal[]> {
  const { data } = await api.get(`/signal/${operatingCaseId}`)
  return data
}

/** 获取交易流水 */
export async function fetchTransactions(customerId: string): Promise<TransactionRecord[]> {
  const { data } = await api.get(`/customer/${customerId}/transactions`)
  return data
}

/** 确认信号 */
export async function confirmSignal(signalId: string): Promise<void> {
  await api.post(`/signal/${signalId}/confirm`)
}

/** 驳回信号 */
export async function dismissSignal(signalId: string): Promise<void> {
  await api.post(`/signal/${signalId}/dismiss`)
}

/** 启动旅程 */
export async function startJourney(customerId: string): Promise<JourneyStartResponse> {
  const { data } = await api.post('/journey/start', { customerId })
  return data
}

/** 完成旅程 */
export async function completeJourney(journeyId: string): Promise<void> {
  await api.post(`/journey/${journeyId}/complete`)
}

/** 处理新证据 */
export async function handleNewEvidence(journeyId: string, customerId: string, operatingCaseId: string, evidenceDescription: string, previousReportId?: string): Promise<NewEvidenceResponse> {
  const { data } = await api.post(`/journey/${journeyId}/new-evidence`, {
    customerId,
    operatingCaseId,
    evidenceDescription,
    previousReportId
  })
  return data
}

/** 产品匹配 */
export async function matchProducts(customerId: string): Promise<ProductMatch[]> {
  const { data } = await api.post(`/customer/${customerId}/product-matching`)
  return data
}

/** 评估运营案例 */
export async function evaluateCase(caseId: string): Promise<EvaluationResponse> {
  const { data } = await rootApi.get(`/api/evaluation/${caseId}`)
  return data
}

// ---- 后端响应类型（与后端DTO对齐） ----

export interface CustomerOverview {
  industry: string
  enterpriseScale: string
  customerTier: string
  registeredCapitalCny: number
  riskLevel: string
  relationshipSummary: string
}

export interface KycGapSummary {
  knownItems: string[]
  partialKnownItems: string[]
  unknownItems: string[]
  priorityQuestions: string[]
}

export interface ProductScheme {
  productId: string
  productName: string
  matchReason: string
  suggestedAmount: string
  suggestedTerm: string
  keyConditions: string[]
  requiredMaterials: string[]
  riskPoints: string[]
}

export interface PrevisitReportContent {
  reportId: string
  customerId: string
  customerName: string
  rmName: string
  visitObjective: string
  customerOverview: CustomerOverview
  kycGapSummary: KycGapSummary
  productSchemes: ProductScheme[]
  keyQuestions: string[]
  riskReminders: string[]
  visitStrategy: string
}

export interface QuickBattleCard {
  cardId: string
  customerName: string
  visitObjective: string
  customerTier: string
  riskLevel: string
  keyPoints: string[]
  productHints: string[]
  dontForget: string[]
  bottomLine: string
}

export interface PrevisitExecutionResponse {
  previsitReport: PrevisitReportContent
  battleCard: QuickBattleCard
  supplyChainMarkdown?: string
}

export interface PostvisitExecutionResponse {
  transcriptId: string
  analysisId: string
  internalReportId: string
  crmReportId: string
  crmCommandCount: number
  allCommandsRequireHumanConfirm: boolean
}

export interface JourneyStartResponse {
  journeyId: string
  customerId: string
  operatingCaseId: string
  phase: JourneyPhase
  startedAt: string
  kycGapSummary?: string
}

export interface NewEvidenceResponse {
  updatedReportId: string
  nextPrevisitReportId: string
}

export interface ProductMatch {
  productId: string
  productName: string
  matchScore: number
  matchReason: string
}

export interface EvaluationResponse {
  caseId: string
  compositeScore: number
  dimensions: Record<string, number>
  contextSummary: {
    evidenceCount: number
    evidenceCompleteCount: number
    lastDataUpdateAt: string
    ruleHitCount: number
    totalRuleCount: number
  }
  evaluatedAt: string
}

export interface TalkingPoint {
  topic: string
  detail: string
  suggestedQuestion: string
  priority: number
}

export interface OutreachScriptResponse {
  scriptId: string
  customerId: string
  rmId: string
  operatingCaseId: string
  journeyId: string
  channel: string
  objective: string
  openingLine: string
  talkingPoints: TalkingPoint[]
  riskReminders: string[]
  closingLine: string
  followUpAction: string
  createdAt: string
}

export interface AgendaItem {
  topic: string
  durationMinutes: number
  keyPoints: string
  expectedOutcome: string
}

export interface KycQuestionItem {
  gapArea: string
  question: string
  purpose: string
  expectedAnswerType: string
}

export interface ProductDiscussionItem {
  productId: string
  productName: string
  discussionAngle: string
  keySellingPoints: string[]
}

export interface MeetingScriptResponse {
  scriptId: string
  customerId: string
  rmId: string
  operatingCaseId: string
  journeyId: string
  meetingObjective: string
  previsitSummary: string
  agendaItems: AgendaItem[]
  kycQuestions: KycQuestionItem[]
  productDiscussions: ProductDiscussionItem[]
  riskPoints: string[]
  closingSummary: string
  createdAt: string
}

export interface PostvisitAnalysisContent {
  analysisId: string
  journeyId: string
  visitSummary: string
  keyFindings: { extractionType: string; content: string; confidence: number }[]
  opportunitySignals: { signalType: string; description: string; confidence: number }[]
  commitments: { content: string; deadline: string; owner: string }[]
  reconciliationItems: { factDescription: string; previousClaim: string; newEvidence: string; reconciliationResult: string }[]
  followUpActions: string[]
  nextStepRecommendation: string
}

// ===================== 枚举映射 =====================

export const INDUSTRY_LABELS: Record<Industry, string> = {
  MANUFACTURING: '制造业',
  FINANCE: '金融业',
  TECHNOLOGY: '科技业',
  REAL_ESTATE: '房地产',
  ENERGY: '能源业',
  HEALTHCARE: '医疗健康',
  AGRICULTURE: '农业',
  LOGISTICS: '物流业',
  RETAIL: '零售业',
  OTHER: '其他'
}

export const ENTERPRISE_SCALE_LABELS: Record<EnterpriseScale, string> = {
  LARGE: '大型',
  MEDIUM: '中型',
  SMALL: '小型',
  MICRO: '微型'
}

export const CUSTOMER_TIER_LABELS: Record<CustomerTier, string> = {
  STRATEGIC: '战略客户',
  KEY: '重点客户',
  GROWTH: '成长客户',
  GENERAL: '一般客户'
}

export const RISK_LEVEL_LABELS: Record<RiskLevel, string> = {
  HIGH: '高风险',
  MEDIUM: '中风险',
  LOW: '低风险'
}

export const JOURNEY_PHASE_LABELS: Record<JourneyPhase, string> = {
  KYC_COLLECT: 'KYC信息采集',
  INSIGHT_ANALYSIS: '洞察分析',
  PRODUCT_MATCHING: '产品匹配',
  PREVISIT_PREP: '访前准备',
  POSTVISIT_REVIEW: '访后复盘',
  COMPLETED: '已完成'
}

export const SIGNAL_TYPE_LABELS: Record<SignalType, string> = {
  FINANCING_NEED: '融资需求',
  PRODUCT_OPPORTUNITY: '产品机会',
  RELATIONSHIP_CHANGE: '关系变化'
}

export const SIGNAL_STATUS_LABELS: Record<SignalStatus, string> = {
  DETECTED: '已检测',
  CONFIRMED: '已确认',
  DISMISSED: '已排除',
  CONVERTED: '已转化'
}

export const REPORT_TYPE_LABELS: Record<ReportType, string> = {
  INTERNAL_RELATIONSHIP: 'R5A 内部关系报告',
  CRM_CALL: 'R5B CRM通话报告',
  UPDATED_RELATIONSHIP: 'R7 更新关系报告',
  NEXT_PREVISIT: 'R8 下一轮访前报告'
}

export const INTERACTION_TYPE_LABELS: Record<InteractionType, string> = {
  SIGNAL_TRIGGER: '信号触发',
  AI_INSIGHT_PUSH: 'AI洞察推送',
  PHONE_CALL: '电话沟通',
  FACE_TO_FACE_VISIT: '面对面拜访',
  VIDEO_CONFERENCE: '视频会议',
  INSTANT_MESSAGE: '即时消息',
  EMAIL: '邮件往来',
  PRODUCT_PRESENTATION: '产品推介',
  CUSTOMER_COMPLAINT: '客户投诉',
  FOLLOW_UP: '回访跟进'
}

export const OUTCOME_LABELS: Record<InteractionOutcome, string> = {
  COMPLETED: '已完成',
  CUSTOMER_AGREED: '客户同意',
  CUSTOMER_DECLINED: '客户拒绝',
  CUSTOMER_DEFERRED: '客户延后',
  FOLLOW_UP_REQUIRED: '需跟进',
  INTERRUPTED: '中断',
  INFORMATION_GATHERED: '信息收集'
}
