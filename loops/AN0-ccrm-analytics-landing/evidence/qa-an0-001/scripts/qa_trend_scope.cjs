/**
 * 追加探针：经营指标分析 4 个 tab 与细分客群/监视器的 trend 请求实际状态码。
 * 用于确定 500 缺陷的影响面（哪些页面/图表受影响）。
 */
const { chromium } = require('playwright')
const BASE = 'http://127.0.0.1:5173'

const TABS = ['客户指标分析', '业务概况分析', '利润贡献分析', '风险指标分析']
const SUB = ['存款业务', '贷款业务', '中间业务', '结算量业务']

;(async () => {
  const browser = await chromium.launch()
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const page = await ctx.newPage()
  const seen = []
  page.on('response', r => {
    if (r.url().includes('/v1/analytics/trend')) seen.push(`${r.status()} ${decodeURIComponent(r.url().split('/v1/analytics/')[1])}`)
  })

  async function report(label) {
    await page.waitForTimeout(1200)
    const before = seen.length
    console.log(`\n### ${label}`)
    const trend = await page.locator('.trend-wrap').first().innerText().catch(() => '(无)')
    console.log(`   趋势图容器文本: ${trend.replace(/\n/g, ' | ').slice(0, 120)}`)
    console.log(`   期间新增 trend 请求: ${seen.length - before}`)
    await page.waitForTimeout(600)
    for (const s of seen.slice(-2)) console.log(`   ${s}`)
  }

  // 经营指标分析 4 个 tab
  await page.goto(BASE + '/analytics/operating-metrics', { waitUntil: 'networkidle' })
  for (const t of TABS) {
    seen.length = 0
    await page.locator('[data-testid="analytics-nav-item"]', { hasText: t }).click()
    await report(`经营指标分析 / ${t}`)
  }

  // 细分客群：客户分布特征 + 4 个子项
  await page.goto(BASE + '/analytics/segments', { waitUntil: 'networkidle' })
  seen.length = 0
  await report('细分客群分析 / 客户分布特征分析')
  for (const s of SUB) {
    seen.length = 0
    await page.locator('[data-testid="analytics-nav-subitem"]', { hasText: s }).click()
    await report(`细分客群分析 / 细分客户业务 / ${s}`)
  }

  // 指标监视器 3 屏
  await page.goto(BASE + '/analytics/monitors', { waitUntil: 'networkidle' })
  for (const t of ['业务增减变化监控', '存贷比变化监控', '不良贷款分布变化监控']) {
    seen.length = 0
    await page.locator('[data-testid="analytics-nav-item"]', { hasText: t }).click()
    await report(`指标监视器 / ${t}`)
  }
  await browser.close()
})()
