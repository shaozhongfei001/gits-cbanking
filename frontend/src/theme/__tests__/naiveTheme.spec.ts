import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  GITS_BORDER_RADIUS,
  GITS_FONT_SANS,
  GITS_THEME_DARK,
  GITS_THEME_LIGHT,
  NAIVE_TOKEN_MAP,
  gitsThemeFor,
} from '../naiveTheme'
import type { NaiveColorVar } from '../naiveTheme'

/**
 * 令牌漂移守卫。
 *
 * 本测试直接解析 assets/styles/theme.css，把 token 解析到字面值，
 * 再与 naiveTheme.ts 的取值逐项比对。目的是让「TS 主题覆盖」与「CSS token」
 * 无法静默分叉 —— 任何一侧改了颜色而另一侧没跟上，这里立即红。
 */

const THEME_CSS_PATH = resolve(process.cwd(), 'src/assets/styles/theme.css')
const NAIVE_THEME_PATH = resolve(process.cwd(), 'src/theme/naiveTheme.ts')

/** 去掉注释后再解析，避免注释中的示例文本被误认为声明。 */
const cssSource = readFileSync(THEME_CSS_PATH, 'utf-8').replace(/\/\*[\s\S]*?\*\//g, '')

function extractBlock(selector: string): string {
  const start = cssSource.indexOf(selector)
  if (start === -1) {
    throw new Error(`theme.css 缺少选择器块：${selector}`)
  }
  const open = cssSource.indexOf('{', start)
  const close = cssSource.indexOf('}', open)
  if (open === -1 || close === -1) {
    throw new Error(`theme.css 选择器块不完整：${selector}`)
  }
  return cssSource.slice(open + 1, close)
}

function parseCustomProperties(block: string): Record<string, string> {
  const props: Record<string, string> = {}
  for (const match of block.matchAll(/(--[a-z0-9-]+)\s*:\s*([^;]+);/gi)) {
    props[match[1]] = match[2].trim()
  }
  return props
}

const rootProps = parseCustomProperties(extractBlock(':root'))
const darkProps = parseCustomProperties(extractBlock('[data-theme="dark"]'))

/** 把 `var(--a)` 链解析为最终字面值；暗色缺失的 token 回退到 :root。 */
function resolveToken(name: string, mode: 'light' | 'dark'): string {
  const scopes = mode === 'dark' ? [darkProps, rootProps] : [rootProps]
  const seen = new Set<string>()
  let current = name

  for (let depth = 0; depth < 10; depth += 1) {
    if (seen.has(current)) {
      throw new Error(`theme.css token 出现循环引用：${name}`)
    }
    seen.add(current)

    const raw = scopes.map(scope => scope[current]).find(value => value !== undefined)
    if (raw === undefined) {
      throw new Error(`theme.css ${mode} 模式缺少 token：${current}`)
    }

    const varMatch = raw.match(/^var\(\s*(--[a-z0-9-]+)\s*\)$/i)
    if (!varMatch) {
      return raw
    }
    current = varMatch[1]
  }

  throw new Error(`theme.css token 解析层级过深：${name}`)
}

const normalize = (value: string) => value.replace(/\s+/g, ' ').trim()

const NAIVE_VARS = Object.keys(NAIVE_TOKEN_MAP) as NaiveColorVar[]
const lightCommon = GITS_THEME_LIGHT.common as unknown as Record<string, string>
const darkCommon = GITS_THEME_DARK.common as unknown as Record<string, string>

describe('naiveTheme 与 theme.css 保持同源', () => {
  it('theme.css 已定义亮暗两套 token 块', () => {
    expect(Object.keys(rootProps).length).toBeGreaterThan(20)
    expect(Object.keys(darkProps).length).toBeGreaterThan(10)
  })

  it('覆盖了全部品牌与语义色变量', () => {
    expect(NAIVE_VARS).toHaveLength(8)
  })

  it('亮色模式每个色变量都等于 theme.css 解析值', () => {
    for (const naiveVar of NAIVE_VARS) {
      const cssToken = NAIVE_TOKEN_MAP[naiveVar]
      expect(lightCommon[naiveVar], `亮色 ${naiveVar} 应等于 ${cssToken}`).toBe(
        resolveToken(cssToken, 'light'),
      )
    }
  })

  it('暗色模式每个色变量都等于 theme.css 解析值', () => {
    for (const naiveVar of NAIVE_VARS) {
      const cssToken = NAIVE_TOKEN_MAP[naiveVar]
      expect(darkCommon[naiveVar], `暗色 ${naiveVar} 应等于 ${cssToken}`).toBe(
        resolveToken(cssToken, 'dark'),
      )
    }
  })

  it('亮暗两套主题确实不同（防止复制后未改）', () => {
    expect(GITS_THEME_LIGHT.common?.primaryColor).not.toBe(GITS_THEME_DARK.common?.primaryColor)
    expect(GITS_THEME_LIGHT.common?.errorColor).not.toBe(GITS_THEME_DARK.common?.errorColor)
  })

  it('borderRadius 等于 --radius-md（V8 9px 分层圆角）', () => {
    expect(GITS_BORDER_RADIUS).toBe(resolveToken('--radius-md', 'light'))
    expect(GITS_THEME_LIGHT.common?.borderRadius).toBe(resolveToken('--radius-md', 'light'))
    expect(GITS_THEME_DARK.common?.borderRadius).toBe(resolveToken('--radius-md', 'dark'))
  })

  it('fontFamily 归一并解析后等于 --font-sans', () => {
    const cssFont = normalize(resolveToken('--font-sans', 'light'))
    expect(normalize(GITS_FONT_SANS)).toBe(cssFont)
    expect(normalize(String(GITS_THEME_LIGHT.common?.fontFamily))).toBe(cssFont)
    expect(normalize(String(GITS_THEME_DARK.common?.fontFamily))).toBe(cssFont)
  })

  it('--font-sans 含 V8 字体族(Inter)和中文字体', () => {
    const cssFont = resolveToken('--font-sans', 'light')
    expect(cssFont).toMatch(/Inter/)
    expect(cssFont).toMatch(/PingFang SC/)
    expect(cssFont).toMatch(/Microsoft YaHei/)
  })

  it('gitsThemeFor 按模式分发同一对象引用', () => {
    expect(gitsThemeFor(true)).toBe(GITS_THEME_DARK)
    expect(gitsThemeFor(false)).toBe(GITS_THEME_LIGHT)
  })

  it('naiveTheme.ts 不含 theme.css 未定义的色值', () => {
    const source = readFileSync(NAIVE_THEME_PATH, 'utf-8')
    const hexes = [...source.matchAll(/#[0-9a-fA-F]{3,8}\b/g)].map(match => match[0].toLowerCase())
    const cssLower = cssSource.toLowerCase()
    const unknown = [...new Set(hexes)].filter(hex => !cssLower.includes(hex))
    expect(unknown, '这些色值在 theme.css 中不存在，必须改为引用既有 token').toEqual([])
  })
})
