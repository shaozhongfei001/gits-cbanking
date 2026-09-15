/**
 * WP5-3 推荐证据抽屉与专家协同 —— 类型定义（只读镜像）。
 *
 * 状态块：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO
 *
 * 权威依据（本文件只读镜像 schema 字段，不新增后端契约）：
 * - specs/product-recommendation/eligibility-result.schema.json（CTR-PR-ELIG-001）
 * - specs/product-recommendation/product-fit-result.schema.json（CTR-PR-FIT-001）
 * - specs/product-recommendation/recommendation-result.schema.json（CTR-PR-RES-001）
 */

export type EligibilityStatus = 'ELIGIBLE' | 'INELIGIBLE' | 'UNKNOWN' | 'REVIEW_REQUIRED'
export type RuleResultStatus = 'PASS' | 'FAIL' | 'UNKNOWN' | 'REVIEW_REQUIRED'

/** 每条硬规则的结论：ruleId + ruleVersion + result + reasonCode（CTR-PR-ELIG-001 RuleResult）。 */
export interface RuleResult {
  ruleId: string
  ruleVersion: string
  result: RuleResultStatus
  /** 对客户经理展示的业务化原因码；敏感内部规则按权限脱敏（schema 描述）。 */
  reasonCode: string
  inputFactRefs?: string[]
  evidenceRefs?: string[]
}

export interface UnknownItem {
  question: string
  relatedFactRef?: string
  suggestedAction?: string
}

export interface ReviewRequirement {
  reason: string
  requiredExpertise?: string
  ruleId?: string
}

/** 第一段硬约束过滤结果（CTR-PR-ELIG-001 EligibilityResult）。 */
export interface EligibilityResult {
  schemaVersion?: string
  productId: string
  productVersion: string
  eligibility: EligibilityStatus
  ruleResults?: RuleResult[]
  unknowns?: UnknownItem[]
  reviewRequirements?: ReviewRequirement[]
}

/**
 * EvidenceBundle（CTR-PR-RES-001 顶层字段）：KERT(SP-15) 输出信封中的
 * skillId / skillVersion / contentHash / traceId，用于重放与过期判断。
 */
export interface EvidenceBundle {
  skillId: string
  skillVersion: string
  contentHash: string
  traceId: string
  evidenceBundleId?: string
  productKnowledgeSnapshotRef?: string
  ruleExecutionRef?: string
}

/**
 * 客户事实来源。canViewSource=false 表示当前行为人无权查看原文；
 * 此时 UI 只展示“证据存在 + 权限说明”，严禁渲染 content 原文。
 */
export interface CustomerFactSource {
  ref: string
  canViewSource: boolean
  content?: string
}

/** 排除原因（INELIGIBLE / FAIL 规则或 notRecommendReasons 的业务化表达）。 */
export interface ExclusionReason {
  reasonCode?: string
  text: string
  ruleId?: string
}

/** REVIEW_REQUIRED / UNKNOWN 待处理项（ReviewRequiredPanel 输入）。 */
export interface ReviewRequiredItem {
  productId?: string
  productVersion?: string
  eligibility: 'REVIEW_REQUIRED' | 'UNKNOWN'
  /** 业务化原因说明（可为 reasonCode 或 UnknownItem.question）。 */
  reason: string
  reasonCode?: string
  ruleId?: string
  requiredExpertise?: string
  suggestedAction?: string
}

export const ELIGIBILITY_LABELS: Record<EligibilityStatus, string> = {
  ELIGIBLE: '合格',
  INELIGIBLE: '不合格',
  UNKNOWN: '未知',
  REVIEW_REQUIRED: '需复核',
}

export const RULE_RESULT_LABELS: Record<RuleResultStatus, string> = {
  PASS: '通过',
  FAIL: '不通过',
  UNKNOWN: '未知',
  REVIEW_REQUIRED: '需复核',
}
