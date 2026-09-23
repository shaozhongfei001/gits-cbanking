/**
 * PC-i1 · 独立 QA 复验探针 A（V-B1 独立 oracle；**不复用**上一轮探针的硬编码期望）
 *
 * 期望值由 `GET /api/v1/product-knowledge/cards/{id}` 的 `sections[].title` **独立推导**
 * （章标题关键字为唯一语义锚），再与真实页面 DOM 做一致性比对；判据实现见 `rules-heading.mjs`
 * （与 pre-fix 回放脚本 `probe-reverify-replay-prefix.mjs` **共用同一规则代码路径** ⇒ 可证非空转）。
 *
 * 用法：node probe-reverify-heading.mjs <outDir>
 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'
import { judgeChapter, judgeImm, norm } from './rules-heading.mjs'

const OUT = process.argv[2] || '.'
mkdirSync(OUT, { recursive: true })
const BASE = 'http://127.0.0.1:15173'

/** R2 登记章号（C1–C12）与其章节标题（语义锚来自 R2 映射，非取自实现代码）。 */
const CHAPTERS = [
  { key: 'c2', id: 'C2', title: '适用客户与适用场景' },
  { key: 'c3', id: 'C3', title: '产品能力' },
  { key: 'c6', id: 'C6', title: '前置、互斥、替代与配套产品' },
  { key: 'c8', id: 'C8', title: '价格边界' },
  { key: 'c9', id: 'C9', title: '风险提示与人工复核' },
  { key: 'c10', id: 'C10', title: '销售边界' },
  { key: 'c12', id: 'C12', title: 'EvidenceRef' }
]
const C11_TITLE = '不可变版本语义'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } })

const productsResp = await page.request.get(`${BASE}/api/v1/product-center/products`)
const products = await productsResp.json()
const violations = []
const perProduct = []

for (const p of products) {
  const pid = p.productId
  const cardResp = await page.request.get(`${BASE}/api/v1/product-knowledge/cards/${pid}`)
  const cardOk = cardResp.ok()
  const sections = cardOk ? ((await cardResp.json()).sections ?? []) : []

  await page.goto(`${BASE}/product-center/${pid}`, { waitUntil: 'domcontentloaded' })
  await page
    .locator('[data-testid="pc-inherited-chapters"]')
    .waitFor({ timeout: 20000 })
    .catch(() => {})

  const dom = await page.evaluate((keys) => {
    const t = (sel) => document.querySelector(sel)?.textContent ?? null
    const out = {}
    for (const k of keys) {
      out[k] = {
        head: t(`[data-testid="pc-inherited-${k}"] .pc-inherited-block-title`),
        meta: t(`[data-testid="pc-inherited-${k}-meta"]`),
        content: t(`[data-testid="pc-inherited-${k}-content"]`),
        absent: t(`[data-testid="pc-inherited-${k}-absent"]`)
      }
    }
    out.imm = {
      source: t('[data-testid="pc-immutable-source"]'),
      content: t('[data-testid="pc-immutable-content"]'),
      absent: t('[data-testid="pc-immutable-absent"]')
    }
    return out
  }, CHAPTERS.map((c) => c.key))

  const rec = {
    productId: pid,
    cardHttpOk: cardOk,
    sections: sections.map((s) => s.title),
    chapters: {},
    imm: {}
  }

  for (const ch of CHAPTERS) {
    const section = sections.find((s) => String(s.title).includes(ch.title)) ?? null
    const v = judgeChapter({ ch, section, dom: dom[ch.key] })
    rec.chapters[ch.id] = {
      expectedNo: section ? (/^(\d+)\./.exec(String(section.title)) ?? [])[1] : null,
      head: norm(dom[ch.key]?.head),
      meta: norm(dom[ch.key]?.meta),
      violations: v
    }
    for (const x of v) violations.push({ productId: pid, code: x })
  }

  const immSection = sections.find((s) => String(s.title).includes(C11_TITLE)) ?? null
  const iv = judgeImm({ immSection, dom: dom.imm })
  rec.imm = { expectedTitle: immSection?.title ?? null, source: norm(dom.imm.source), violations: iv }
  for (const x of iv) violations.push({ productId: pid, code: `C11:${x}` })

  perProduct.push(rec)
}

const out = {
  probe: 'probe-reverify-heading（独立 QA 复验；期望值由接口独立推导）',
  generatedAt: new Date().toISOString(),
  base: BASE,
  products: products.length,
  chapterChecks: products.length * CHAPTERS.length,
  violationCount: violations.length,
  violations,
  perProduct
}
writeFileSync(`${OUT}/probe-reverify-heading.json`, JSON.stringify(out, null, 2))
console.log(
  JSON.stringify(
    { products: out.products, chapterChecks: out.chapterChecks, violationCount: out.violationCount, violations: violations.slice(0, 20) },
    null,
    2
  )
)
await browser.close()
process.exit(violations.length === 0 ? 0 : 1)
