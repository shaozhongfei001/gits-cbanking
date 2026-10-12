/**
 * 业务场景「人工可验证性」实测探针（**只读**：不改仓内文件、不注入假数据）。
 *
 * 回答：在当前环境（前端 15173 → 后端 18080 → KERT 8107）下，
 * 一个**人类**能否对业务场景做主链路验证？逐场景测量：
 *   · 页面可达性与正文字数（"有没有内容可看"）
 *   · 关键 API 4xx/5xx（"数据是否真的到页"）· console 错误
 *   · **诚实性标注**是否在场（待接入/未接入/待核验/DEMO/演示数据/来源标识不可得/只读）
 * 用法：node bs-feasibility-probe.mjs <outDir>
 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'

const BASE = process.env.BS_BASE || 'http://127.0.0.1:15173'
const OUT = process.argv[2] || '/tmp/bs-feasibility'
mkdirSync(OUT, { recursive: true })

const ROUTES = [
  ['P01 我的客户经营', '/workbench'],
  ['P02 客户对象主页', '/accounts'],
  ['P04 客户记录·经营总览', '/customers/CUST-CORP-0003'],
  ['P08 经营信号对象主页', '/signals'],
  ['P10 互动对象主页', '/engagements'],
  ['P11 互动记录·访前路径', '/engagement'],
  ['P12 访前目标与信息缺口', '/engagement/previsit/gaps'],
  ['P13 访前知识证据装配', '/engagement/previsit/evidence'],
  ['P14 访前包预览', '/engagement/previsit/pack'],
  ['P15 会中工作区', '/in-meeting/CUST-CORP-0003'],
  ['P23 建议书对象主页', '/proposals'],
  ['P32 审批工作中心', '/approvals'],
  ['P38 知识卡与产品适用边界', '/knowledge-map'],
  ['P39 审计与权限', '/audit-trace'],
  ['PI 产品中心·产品解读（PC-i1 交付面）', '/product-center/PROD-CM-003'],
  ['P40 服务降级与异常恢复', '/degrade'],
  ['P41 移动端·今日客户行动', '/m/today']
]

const LABELS = ['待接入', '未接入', '待核验', 'DEMO', '演示数据', '来源标识不可得', '无有效版本', '只读', '未发布受控版本']

const browser = await chromium.launch()
const rows = []
for (const [name, path] of ROUTES) {
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } })
  const api4xx = [], api5xx = [], consoleErr = []
  page.on('response', (r) => {
    const u = r.url()
    if (!u.includes('/api/')) return
    if (r.status() >= 500) api5xx.push(`${r.status()} ${u}`)
    else if (r.status() >= 400) api4xx.push(`${r.status()} ${u.replace(BASE, '')}`)
  })
  page.on('console', (m) => {
    if (m.type() === 'error') consoleErr.push(m.text().slice(0, 120))
  })
  let status = 0, text = '', err = null
  try {
    const resp = await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 25000 })
    status = resp ? resp.status() : 0
    await page.waitForTimeout(2500)
    text = (await page.locator('body').innerText()).replace(/\s+/g, ' ').trim()
  } catch (e) {
    err = String(e).slice(0, 160)
  }
  const labels = LABELS.filter((k) => text.includes(k))
  rows.push({
    name, path, status, textLen: text.length,
    api4xx: api4xx.length, api5xx: api5xx.length,
    api4xxSamples: api4xx.slice(0, 2), api5xxSamples: api5xx.slice(0, 2),
    consoleErrors: consoleErr.length, consoleErrSamples: consoleErr.slice(0, 2),
    honestyLabels: labels, error: err,
    snippet: text.slice(0, 160)
  })
  await page.close()
}
await browser.close()
writeFileSync(`${OUT}/bs-feasibility.json`, JSON.stringify({ base: BASE, rows }, null, 2))
console.log('场景 | HTTP | 正文字数 | api4xx | api5xx | consoleErr | 诚实标注')
for (const r of rows) {
  console.log(`${r.name} | ${r.status} | ${r.textLen} | ${r.api4xx} | ${r.api5xx} | ${r.consoleErrors} | ${r.honestyLabels.join('/')}${r.error ? ' | ERR:' + r.error : ''}`)
}
