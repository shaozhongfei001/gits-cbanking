/**
 * PC-i1 · 独立 QA 复验探针 B（V-B2 独立交叉验证；**不复用**上一轮 probe-faultcard 的判定逻辑）
 *
 * 与上一轮探针的差异（刻意）：
 *  1) **含正向对照**：先在同一产品、同一浏览器、**不注入失败**的条件下确证 c12/c11 原文**确实会渲染**
 *     ⇒ 随后「原文消失」才可归因于中断，而非页面本来就没渲染（排除空转/假绿）；
 *  2) 抽样全部 13 张卡（不止 PROD-FIN-003），核验「来源不可得」口径的普遍性；
 *  3) 判据实现见 `rules-fault.mjs`（与 pre-fix 回放共用同一代码路径 ⇒ 可证非空转）。
 *
 * 用法：node probe-reverify-faultcard.mjs <outDir>
 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'
import { judgeFault } from './rules-fault.mjs'

const OUT = process.argv[2] || '.'
mkdirSync(OUT, { recursive: true })
const BASE = 'http://127.0.0.1:15173'
const norm = (s) => (s ?? '').replace(/\s+/g, ' ').trim()

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 } })

const productsResp = await ctx.request.get(`${BASE}/api/v1/product-center/products`)
const products = await productsResp.json()

const pick = async (page) =>
  page.evaluate(() => {
    const t = (sel) => document.querySelector(sel)?.textContent ?? null
    return {
      c6head: t('[data-testid="pc-inherited-c6"] .pc-inherited-block-title'),
      c12head: t('[data-testid="pc-inherited-c12"] .pc-inherited-block-title'),
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

const violations = []
const perProduct = []

for (const p of products) {
  const pid = p.productId
  const cardResp = await ctx.request.get(`${BASE}/api/v1/product-knowledge/cards/${pid}`)
  const sections = cardResp.ok() ? ((await cardResp.json()).sections ?? []) : []
  const hasEvidence = sections.some((s) => String(s.title).includes('EvidenceRef'))
  const hasImmutable = sections.some((s) => String(s.title).includes('不可变版本语义'))

  // —— 阶段 1：正向对照（无失败注入）⇒ 原文应确实渲染 ——
  const control = await ctx.newPage()
  await control.goto(`${BASE}/product-center/${pid}`, { waitUntil: 'domcontentloaded' })
  await control.locator('[data-testid="pc-inherited-chapters"]').waitFor({ timeout: 20000 }).catch(() => {})
  const ctrlDom = await pick(control)
  await control.close()

  // —— 阶段 2：失败注入（仅中断卡接口，不注入假数据）——
  const page = await ctx.newPage()
  let aborted = 0
  let cardsHttpOk = 0
  page.on('response', (r) => {
    if (r.url().includes('/api/v1/product-knowledge/cards/') && r.ok()) cardsHttpOk += 1
  })
  await page.route('**/api/v1/product-knowledge/cards/**', (route) => {
    aborted += 1
    return route.abort('failed')
  })
  await page.goto(`${BASE}/product-center/${pid}`, { waitUntil: 'domcontentloaded' })
  await page.locator('[data-testid="pc-inherited-chapters"]').waitFor({ timeout: 20000 }).catch(() => {})
  const faultDom = await pick(page)
  await page.close()

  const v = judgeFault(faultDom, { aborted })
  // 正向对照（非空转证明）：接口表明该卡**确有该节** ⇒ 无注入时必须渲染原文
  if (hasEvidence && !ctrlDom.c12content) v.push('CONTROL_NO_CONTENT:c12（无注入时也未渲染 ⇒ 故障观察不可归因）')
  if (hasImmutable && !ctrlDom.immContent) v.push('CONTROL_NO_CONTENT:c11（无注入时也未渲染 ⇒ 故障观察不可归因）')
  if (hasEvidence && !/（第\s*\d+\s*节）/.test(norm(ctrlDom.c12meta)))
    v.push('CONTROL_NO_SECTION_NO:c12（无注入时 meta 无节号 ⇒ 对照无效）')
  const rec = {
    productId: pid,
    apiSays: { hasEvidenceRef: hasEvidence, hasImmutableVersion: hasImmutable },
    abortedRequests: aborted,
    cardsHttpOkDuringFault: cardsHttpOk,
    control: {
      c12content: ctrlDom.c12content ? norm(ctrlDom.c12content).slice(0, 40) : null,
      immContent: ctrlDom.immContent ? norm(ctrlDom.immContent).slice(0, 40) : null,
      c12meta: norm(ctrlDom.c12meta).slice(0, 80)
    },
    fault: {
      c6head: norm(faultDom.c6head),
      c12head: norm(faultDom.c12head),
      c6meta: norm(faultDom.c6meta),
      c6absent: norm(faultDom.c6absent),
      c12meta: norm(faultDom.c12meta),
      c12absent: norm(faultDom.c12absent),
      immAbsent: norm(faultDom.immAbsent),
      c12content: faultDom.c12content,
      immContent: faultDom.immContent,
      c10contractPresent: Boolean(faultDom.c10contract)
    },
    violations: v
  }
  perProduct.push(rec)
  for (const x of v) violations.push({ productId: pid, code: x })
}

const out = {
  probe: 'probe-reverify-faultcard（独立 QA 交叉验证：正向对照 + 失败注入 + 13 卡抽样）',
  generatedAt: new Date().toISOString(),
  base: BASE,
  products: products.length,
  violationCount: violations.length,
  violations,
  perProduct
}
writeFileSync(`${OUT}/probe-reverify-faultcard.json`, JSON.stringify(out, null, 2))
console.log(JSON.stringify({ products: out.products, violationCount: out.violationCount, violations }, null, 2))
await browser.close()
process.exit(violations.length === 0 ? 0 : 1)
