/** 金额（元）格式化为万/亿；无数据不编造。 */
export function formatAmountYuan(value?: number | null): string {
  if (value == null || Number.isNaN(Number(value))) {
    return '—'
  }
  const n = Number(value)
  if (n >= 1e8) {
    return `${(n / 1e8).toFixed(2)} 亿`
  }
  if (n >= 1e4) {
    return `${(n / 1e4).toFixed(1)} 万`
  }
  return String(n)
}

/** 占比 0-1 → 百分比。 */
export function formatShare(value?: number | null): string {
  if (value == null || Number.isNaN(Number(value))) {
    return '—'
  }
  return `${(Number(value) * 100).toFixed(1)}%`
}

export const LAYER_LABEL: Record<string, string> = {
  supplier: '上游供应商',
  enterprise: '本企业',
  customer: '下游客户',
}

export const TREND_LABEL: Record<string, string> = {
  up: '↑ 上升',
  down: '↓ 下降',
  flat: '→ 持平',
  unknown: '—',
}

export const RELATION_LABEL: Record<string, string> = {
  purchase: '采购',
  sale: '销售',
}

/** V3.2 描边色：本企业蓝、上游青绿、下游浅蓝。 */
export const LAYER_COLOR: Record<string, string> = {
  supplier: '#12a7a0',
  enterprise: '#1976d2',
  customer: '#48a7e8',
}

/** V3.2 节点填充：白底圆 + 分层浅底，对应 05 集团关系图。 */
export const LAYER_FILL: Record<string, string> = {
  supplier: '#e8f8f6',
  enterprise: '#ffffff',
  customer: '#eaf4fe',
}

export type GraphInsightInput = {
  supplyChainPosition?: string
  concentrationRisk?: string[]
  keyChanges?: string
  overallAssessment?: string
  followUpQuestions?: string[]
}

export type GraphInsightStrip = {
  tone: 'blue' | 'amber' | 'teal'
  label: string
  text: string
}

/** 图谱底部三色分隔条：只展示 Skill 已返回字段，不编造文案。 */
export function graphInsightStrips(interp?: GraphInsightInput | null): GraphInsightStrip[] {
  if (!interp) {
    return []
  }
  const strips: GraphInsightStrip[] = []
  const judgment = nonBlank(interp.overallAssessment) || nonBlank(interp.supplyChainPosition)
  if (judgment) {
    strips.push({ tone: 'blue', label: '关键判断', text: judgment })
  }
  const gap = (interp.concentrationRisk || []).map(nonBlank).filter(Boolean).join('；')
    || nonBlank(interp.keyChanges)
  if (gap) {
    strips.push({ tone: 'amber', label: '信息缺口', text: gap })
  }
  const action = nonBlank(interp.followUpQuestions?.[0])
  if (action) {
    strips.push({ tone: 'teal', label: '建议动作', text: action })
  }
  return strips
}

function nonBlank(value?: string | null): string {
  return value && value.trim() ? value.trim() : ''
}

export function formatConfidence(value: unknown): string {
  if (value == null) {
    return '—'
  }
  if (typeof value === 'string' || typeof value === 'number') {
    return String(value)
  }
  if (typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>)
      .map(([k, v]) => `${k}=${v}`)
      .join('；')
  }
  return String(value)
}

export function isPartialBuild(status?: string): boolean {
  return status === 'partial'
}
