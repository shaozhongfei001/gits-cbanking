/**
 * AN0 独立 QA 目视复核脚本（Q9 左侧页面内导航 / Q10 同域单项高亮 / Q11 认证旁路）。
 * QA 自研；真实链路 5173 → /kert-api → KERT 8107。截图落 /tmp/qa_an0/shots。
 */
const { chromium } = require('playwright')
const fs = require('fs')

const OUT = '/tmp/qa_an0/shots'
const BASE = 'http://127.0.0.1:5173'
const results = []
const cases = [
  ['/analytics/operating-metrics', 'operating-metrics', 'analytics-panel-operating-customer'],
  ['/analytics/segments', 'segments', 'analytics-panel-segment-distribution'],
  ['/analytics/monitors', 'monitors', 'analytics-panel-monitor-balance'],
  ['/analytics/combo-query', 'combo-query', null],
]

function rec(label, ok, detail) {
  results.push({ label, ok, detail })
  console.log(`[${ok ? 'PASS' : 'FAIL'}] ${label}: ${detail}`)
}

;(async () => {
  fs.mkdirSync(OUT, { recursive: true })
  const browser = await chromium.launch()

  for (const [path, name, panelTestId] of cases) {
    // Q11：全新 context（无 storage）直开深链 ⇒ 不跳登录页
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
    const page = await ctx.newPage()
    const bad = []
    const apiKeyHeaders = []
    page.on('response', r => { if (r.status() >= 400) bad.push(`${r.status()} ${r.url()}`) })
    page.on('request', r => { if (r.headers()['x-api-key']) apiKeyHeaders.push(r.url()) })
    await page.goto(BASE + path, { waitUntil: 'networkidle' })
    await page.waitForTimeout(800)

    rec(`Q11 ${name} 免登录直达`, page.url().endsWith(path),
        `url=${page.url()}`)
    const storage = await page.evaluate(() => Object.keys(localStorage))
    rec(`Q11 ${name} 无 API Key 注入`, apiKeyHeaders.length === 0 && !storage.includes('gits_api_key'),
        `x-api-key 请求=${apiKeyHeaders.length} localStorage=${JSON.stringify(storage)}`)

    if (panelTestId) {
      const nav = page.getByTestId('analytics-page-nav')
      const panel = page.getByTestId(panelTestId)
      rec(`Q9 ${name} 面板默认可见`, await panel.isVisible(), `panel=${panelTestId}`)
      const navBox = await nav.boundingBox()
      const panelBox = await panel.boundingBox()
      rec(`Q9 ${name} 页面内导航位于左侧`,
          !!navBox && !!panelBox && navBox.x + navBox.width <= panelBox.x + 2,
          `nav.x=${navBox && Math.round(navBox.x)} nav.right=${navBox && Math.round(navBox.x + navBox.width)} panel.x=${panelBox && Math.round(panelBox.x)}`)
      const n = await nav.getByTestId('analytics-nav-item').count()
      const activeNav = await nav.locator('.nav-item.active').count()
      rec(`Q9 ${name} 左导航项数=${n} 且仅 1 项激活`, n >= 2 && activeNav === 1,
          `items=${n} active=${activeNav}`)
    } else {
      const navCount = await page.getByTestId('analytics-page-nav').count()
      rec('Q9 combo-query 为直挂页（无页面内导航）', navCount === 0, `page-nav count=${navCount}`)
    }

    // Q10：侧边栏 4 项逐一进入，组内仅 1 项高亮
    const group = page.getByTestId('nav-group-analytics')
    rec(`${name} 菜单组 4 项`, (await group.getByRole('button').count()) === 4,
        `count=${await group.getByRole('button').count()}`)
    rec(`${name} 组内仅 1 项高亮`, (await group.locator('.nav-item.active').count()) === 1,
        `active=${await group.locator('.nav-item.active').count()}`)

    const sidebarText = await page.getByTestId('shell-sidebar').innerText()
    rec(`${name} 无「产品分析器」`, !sidebarText.includes('产品分析器'), 'sidebar text checked')

    await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true })
    if (bad.length) console.log(`     ${name} 4xx/5xx:`, bad.slice(0, 5))
    else console.log(`     ${name} 无 4xx/5xx 响应`)
    await ctx.close()
  }

  // Q10 交叉：依次点击 4 个菜单，每次组内激活数必须为 1
  for (const key of ['analytics-operating-metrics', 'analytics-segments', 'analytics-combo', 'analytics-monitors']) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
    const page = await ctx.newPage()
    await page.goto(BASE + '/workbench', { waitUntil: 'networkidle' })
    await page.getByTestId(`nav-item-${key}`).click()
    await page.waitForTimeout(900)
    const n = await page.getByTestId('nav-group-analytics').locator('.nav-item.active').count()
    const txt = n === 1 ? (await page.getByTestId('nav-group-analytics').locator('.nav-item.active').innerText()).trim() : ''
    rec(`Q10 点击 ${key} 后组内高亮数`, n === 1, `active=${n} label=${txt}`)
    await ctx.close()
  }

  await browser.close()
  const failed = results.filter(r => !r.ok)
  console.log(`\n合计 ${results.length} 项，FAIL ${failed.length} 项`)
  fs.writeFileSync('/tmp/qa_an0/qa_visual_result.json', JSON.stringify(results, null, 2))
  process.exit(failed.length ? 1 : 0)
})()
