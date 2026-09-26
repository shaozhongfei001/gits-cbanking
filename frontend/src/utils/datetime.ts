/**
 * 时间展示工具。
 *
 * 约定：后端回包时间为 ISO 8601（UTC），界面按**本地时区**展示为 `YYYY-MM-DD HH:mm:ss`；
 * 非法/缺失值不伪装成合法时间——缺失返回占位符，非法原样返回。
 */

const EMPTY_PLACEHOLDER = '—'

export function formatDateTime(source: string | null | undefined, placeholder = EMPTY_PLACEHOLDER): string {
  if (!source) return placeholder
  const parsed = new Date(source)
  if (Number.isNaN(parsed.getTime())) return source
  const pad = (value: number) => String(value).padStart(2, '0')
  return `${parsed.getFullYear()}-${pad(parsed.getMonth() + 1)}-${pad(parsed.getDate())} `
    + `${pad(parsed.getHours())}:${pad(parsed.getMinutes())}:${pad(parsed.getSeconds())}`
}
