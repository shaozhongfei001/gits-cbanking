import type { GlobalThemeOverrides } from 'naive-ui'

/**
 * naive-ui 主题覆盖 —— V9.0 浦发风格工作台设计系统
 *
 * 铁律：本文件**不得定义任何 theme.css 之外的颜色**。
 * 所有取值必须等于 assets/styles/theme.css 中对应 token 解析后的值；
 * 该约束由 __tests__/naiveTheme.spec.ts 守卫（直接解析 theme.css 比对），
 * 违反即测试失败，因此不需要人工比对，也不会静默漂移。
 *
 * 之所以在 TS 里复制一份取值、而不是运行时读 CSS 变量：
 * naive-ui 会对 primaryColor 等做颜色运算，传入 `var(--x)` 会得到非法色值。
 * 因此这里放解析后的字面量，由测试保证与 CSS 同源。
 *
 * 注意：取值大小写必须与 theme.css 完全一致（token 解析不做归一）。
 */

/** 与 theme.css `--font-sans` 严格一致（空白已被归一，比较时忽略换行/缩进）。 */
export const GITS_FONT_SANS =
  "Inter, 'PingFang SC', 'Microsoft YaHei', 'Noto Sans CJK SC', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

/** 与 theme.css `--radius-md` 严格一致 — V9 8px 卡片圆角。 */
export const GITS_BORDER_RADIUS = '8px'

/** 亮 / 暗两模式共用的不变量。字号按模板 13px 基准收紧。 */
const SHARED_COMMON = {
  borderRadius: GITS_BORDER_RADIUS,
  fontFamily: GITS_FONT_SANS,
  fontSize: '13px',
  fontSizeMini: '11px',
  fontSizeTiny: '11.5px',
  fontSizeSmall: '12.5px',
  fontSizeMedium: '13px',
  fontSizeLarge: '14px',
  fontSizeHuge: '16px',
  lineHeight: '1.5',
}

/**
 * 品牌与语义色。键为 naive-ui 变量名，值为 theme.css token 名（供测试反查）。
 * 这里只记录 token 名，真实取值仍以 theme.css 为准。
 */
export const NAIVE_TOKEN_MAP = {
  primaryColor: '--brand-primary',
  primaryColorHover: '--brand-primary-light',
  primaryColorPressed: '--brand-primary-dark',
  primaryColorSuppl: '--brand-primary',
  successColor: '--color-success',
  warningColor: '--color-warning',
  errorColor: '--color-danger',
  infoColor: '--color-info',
} as const

export type NaiveColorVar = keyof typeof NAIVE_TOKEN_MAP

/** 亮色模式解析结果（值 = theme.css :root 下对应 token 的解析值）。 */
const LIGHT_COMMON: Record<NaiveColorVar, string> = {
  primaryColor: '#0048D8',
  primaryColorHover: '#3368E0',
  primaryColorPressed: '#003BB3',
  primaryColorSuppl: '#0048D8',
  successColor: '#18A890',
  warningColor: '#C87F0A',
  errorColor: '#C0392B',
  infoColor: '#0048D8',
}

/** 暗色模式解析结果（值 = theme.css [data-theme="dark"] 下对应 token 的解析值）。 */
const DARK_COMMON: Record<NaiveColorVar, string> = {
  primaryColor: '#3368E0',
  primaryColorHover: '#5A86E8',
  primaryColorPressed: '#0048D8',
  primaryColorSuppl: '#3368E0',
  successColor: '#2FBBA3',
  warningColor: '#F39C12',
  errorColor: '#E74C3C',
  infoColor: '#5A86E8',
}

export const GITS_THEME_LIGHT: GlobalThemeOverrides = {
  common: { ...SHARED_COMMON, ...LIGHT_COMMON },
}

export const GITS_THEME_DARK: GlobalThemeOverrides = {
  common: { ...SHARED_COMMON, ...DARK_COMMON },
}

/**
 * 按明暗模式返回主题覆盖。
 *
 * V9.0：浦发风格工作台。
 * 单一品牌锚 —— 浦发深蓝(#0048D8)同时承担品牌识别与交互承载，
 * 取消 V8 的「品牌深蓝 + 靛蓝」双蓝层级，改用白壳层与浅蓝灰背板拉分层。
 */
export function gitsThemeFor(isDark: boolean): GlobalThemeOverrides {
  return isDark ? GITS_THEME_DARK : GITS_THEME_LIGHT
}
