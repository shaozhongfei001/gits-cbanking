/**
 * PC-i1 独立 QA 探针 3：**故障注入**（卡片接口不可达时，缺失归因是否如实）。
 *
 * 只做一件事：把 `/api/v1/product-knowledge/cards/**` 拦断（不伪造任何数据），
 * 观察「章级承接区」与「版本语义区」的**缺失文案**是否如实区分"来源不可得"与"该卡未含该节"。
 * 用法：node probe-faultcard.mjs <outDir> <productId>
 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'

const OUT = process.argv[2] || '.'
const PID = process.argv[3] || 'PROD-FIN-003'
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } })

let aborted = 0
await page.route('**/api/v1/product-knowledge/cards/**', (route) => {
  aborted += 1
  route.abort('failed')
})

await page.goto(`http://127.0.0.1:15173/product-center/${PID}`, { waitUntil: 'domcontentloaded' })
await page
  .locator('[data-testid="pc-inherited-chapters"]')
  .waitFor({ timeout: 20000 })
  .catch(() => {})

const dom = await page.evaluate(() => {
  const t = (sel) => document.querySelector(sel)?.textContent?.trim() ?? null
  return {
    c6meta: t('[data-testid="pc-inherited-c6-meta"]'),
    c6absent: t('[data-testid="pc-inherited-c6-absent"]'),
    c12meta: t('[data-testid="pc-inherited-c12-meta"]'),
    c12content: t('[data-testid="pc-inherited-c12-content"]'),
    c12absent: t('[data-testid="pc-inherited-c12-absent"]'),
    immSource: t('[data-testid="pc-immutable-source"]'),
    immContent: t('[data-testid="pc-immutable-content"]'),
    immAbsent: t('[data-testid="pc-immutable-absent"]'),
    c10contract: t('[data-testid="pc-inherited-c10-contract"]')
  }
})

const findings = []
// 卡片接口不可达 ⇒ meta 应如实显示"来源标识不可得"
if (!/来源标识不可得/.test(dom.c6meta ?? '')) findings.push('META_NOT_HONEST:c6')
// 但 absent 文案断言"该产品卡未包含第 N 节" —— 归因不当（实为来源不可得）
if (/未包含第/.test(dom.c6absent ?? ''))
  findings.push('ABSENT_ATTRIBUTION_UNSOUND:c6（把"来源不可得"表述为"该卡未含该节"）')
// C12 在 FIN 卡本应 §11 有原文；来源不可得时页面不得声称"未包含第 12 节"
if (/未包含第/.test(dom.c12absent ?? '')) findings.push('ABSENT_ATTRIBUTION_UNSOUND:c12')
if (dom.c12content) findings.push('CONTENT_DESPITE_ABORT:c12（接口失败仍渲染原文）')
// C11：同样问题
if (/未包含第\s*11\s*节/.test(dom.immAbsent ?? ''))
  findings.push('ABSENT_ATTRIBUTION_UNSOUND:c11（并写死 §11）')
if (dom.immContent) findings.push('CONTENT_DESPITE_ABORT:c11')
// C10 走的是 product-center 接口（未拦断）⇒ 合同字段仍应渲染
if (!dom.c10contract) findings.push('C10_CONTRACT_LOST（被无关接口失败连带影响）')

const out = { productId: PID, abortedRequests: aborted, dom, findings }
writeFileSync(`${OUT}/probe-faultcard-${PID}.json`, JSON.stringify(out, null, 2))
console.log(JSON.stringify(out, null, 2))
await browser.close()
process.exit(0)
