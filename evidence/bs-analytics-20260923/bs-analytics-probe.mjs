/** 经营分析模块四页实测：逐页取主区正文 + analytics 接口状态 + 错误文案。只读。 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'

const BASE = process.env.BS_BASE || 'http://127.0.0.1:15173'
const OUT = process.argv[2] || '/tmp/bs-analytics'
mkdirSync(OUT, { recursive: true })
const mainText = (page) => page.evaluate(() => {
  const c = document.body.cloneNode(true)
  c.querySelectorAll('aside,nav,header,[class*=sidebar]').forEach((e) => e.remove())
  return (c.innerText || '').replace(/\s+/g, ' ').trim()
})

const PAGES = [
  ['经营指标分析', '/analytics/operating-metrics'],
  ['指标监视器', '/analytics/monitors'],
  ['细分客群分析', '/analytics/segments'],
  ['组合查询工具', '/analytics/combo-query']
]

const b = await chromium.launch()
const out = []
for (const [name, path] of PAGES) {
  const p = await b.newPage({ viewport: { width: 1600, height: 1000 } })
  const api = []
  p.on('response', (r) => {
    if (r.url().includes('/api/') || r.url().includes('/v1/analytics')) api.push(`${r.status()} ${r.request().method()} ${r.url().replace(BASE, '')}`)
  })
  let http = 0
  try {
    const r = await p.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 25000 })
    http = r ? r.status() : 0
    await p.waitForTimeout(3000)
  } catch (e) { /* ignore */ }
  const txt = await mainText(p)
  out.push({ name, path, http, mainLen: txt.length, main: txt.slice(0, 300), api: api.slice(0, 8) })
  console.log(`\n=== ${name}（${path}）HTTP ${http} | 主区 ${txt.length} 字`)
  console.log(`  正文: ${txt.slice(0, 200) || '(空)'}`)
  console.log(`  接口: ${api.join(' ; ') || '(无)'}`)
  await p.close()
}
await b.close()
writeFileSync(`${OUT}/analytics-pages.json`, JSON.stringify(out, null, 2))
