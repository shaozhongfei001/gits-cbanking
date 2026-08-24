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

export const LAYER_COLOR: Record<string, string> = {
  supplier: '#4d9fff',
  enterprise: '#ef476f',
  customer: '#2dd4a7',
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
