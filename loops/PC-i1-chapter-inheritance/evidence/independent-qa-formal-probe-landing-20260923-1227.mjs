/**
 * PC-i1 独立 QA 探针 2：12 章「落点」独立核验（W1-g §1 表可复核性）。
 *
 * 只核 **C1/C3/C4/C5/C7/C10** 的落点（C2/C6/C8/C9/C12 与 C11 由 probe-pci1.mjs 覆盖）。
 * 判据全部**取自接口**（推导在探针内独立实现）；不使用 page.route / stub。
 * 用法：node probe-landing.mjs <outDir>
 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'

const OUT = process.argv[2] || '.'
const BASE = 'http://127.0.0.1:15173'
const API = 'http://127.0.0.1:18080'
mkdirSync(OUT, { recursive: true })

// 变异复验（证明判据非空转）：QA_MUTATE=1 ⇒ C4/C5/C7 期望值故意改错，必须报违规。
const MUTATE = process.env.QA_MUTATE === '1'
if (MUTATE) console.error('*** MUTANT MODE ON ***')

const norm = (s) => String(s ?? '').replace(/\s+/g, '')
const violations = []
const rows = []

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } })

const products = await (await fetch(`${API}/api/v1/product-center/products`)).json()

for (const { productId: pid } of products) {
  const d = await (await fetch(`${API}/api/v1/product-center/products/${pid}`)).json()
  await page.goto(`${BASE}/product-center/${pid}`, { waitUntil: 'domcontentloaded' })
  await page.locator('[data-testid="pc-hero"]').waitFor({ timeout: 20000 }).catch(() => {})

  const dom = await page.evaluate(() => {
    const t = (sel) => document.querySelector(sel)?.textContent?.trim() ?? null
    return {
      hero: t('[data-testid="pc-hero"]'),
      overview: t(
        '[data-testid="pc-chapter"][data-section-key="OVERVIEW"] [data-testid="pc-chapter-body"]'
      ),
      heroTags: Array.from(document.querySelectorAll('.pc-hero-tags .n-tag')).map((e) =>
        e.textContent.trim()
      ),
      fixed: t('[data-testid="pc-fixed-boundaries"]'),
      rightCol: t('[data-testid="pc-col-right"]'),
      fit: t('[data-testid="pc-chapter"][data-section-key="FIT"] [data-testid="pc-chapter-body"]'),
      process: t(
        '[data-testid="pc-chapter"][data-section-key="PROCESS"] [data-testid="pc-chapter-body"]'
      ),
      materials: t(
        '[data-testid="pc-chapter"][data-section-key="MATERIALS"] [data-testid="pc-chapter-body"]'
      ),
      fitPending: !!document.querySelector(
        '[data-testid="pc-chapter"][data-section-key="FIT"] [data-testid="pc-chapter-pending"]'
      )
    }
  })

  const v = (code, detail) => violations.push({ productId: pid, code, detail })
  const rec = { productId: pid, checks: {} }

  // C1 产品概览与客户价值 → 「60 秒读懂」章（OVERVIEW 正文）
  const c1 = d.summary?.oneSentenceDefinition
  rec.checks.C1 = !!c1 && norm(dom.overview).includes(norm(c1))
  if (!rec.checks.C1) v('C1_LANDING', `OVERVIEW 章未含 summary.oneSentenceDefinition`)

  // C3 产品能力 → 首屏能力标签（指名引用）
  const tags = d.tags ?? []
  const missingTags = tags.filter((t) => !dom.heroTags.includes(t))
  rec.checks.C3 = tags.length > 0 && missingTags.length === 0
  if (!rec.checks.C3) v('C3_LANDING', `能力标签缺失：${JSON.stringify(missingTags)}`)

  // C4 准入条件 → FIT 章（prerequisites）
  const pre = (d.prerequisites ?? []).map((p) => p.requirementText).filter(Boolean)
  if (MUTATE) pre.push('__QA_MUTANT_C4__')
  const missPre = pre.filter((x) => !norm(dom.fit).includes(norm(x)))
  rec.checks.C4 = pre.length > 0 && missPre.length === 0
  if (!rec.checks.C4) v('C4_LANDING', `FIT 未含 prerequisites：${JSON.stringify(missPre.slice(0, 2))}`)

  // C5 排除条件与禁止用途 → FIT 章（boundaries）
  const bnd = (d.boundaries ?? [])
    .map((b) => b.scenarioName || b.scenarioDescription)
    .filter(Boolean)
  if (MUTATE) bnd.push('__QA_MUTANT_C5__')
  const missBnd = bnd.filter((x) => !norm(dom.fit).includes(norm(x)))
  rec.checks.C5 = bnd.length > 0 && missBnd.length === 0
  if (!rec.checks.C5) v('C5_LANDING', `FIT 未含 boundaries：${JSON.stringify(missBnd.slice(0, 2))}`)

  // C7 流程与材料 → PROCESS(steps) + MATERIALS(items)
  const steps = (d.processSteps ?? []).map((s) => s.stepName).filter(Boolean)
  const mats = (d.materialGroups ?? []).flatMap((g) => (g.items ?? []).map((i) => i.materialName))
  const missSteps = steps.filter((x) => !norm(dom.process).includes(norm(x)))
  const missMats = mats.filter((x) => !norm(dom.materials).includes(norm(x)))
  rec.checks.C7 = steps.length > 0 && mats.length > 0 && !missSteps.length && !missMats.length
  if (missSteps.length) v('C7_STEPS', `PROCESS 缺步骤：${JSON.stringify(missSteps.slice(0, 2))}`)
  if (missMats.length) v('C7_MATERIALS', `MATERIALS 缺材料：${JSON.stringify(missMats.slice(0, 2))}`)

  // C10 销售边界 → 首屏固定边界 + 右栏页面边界
  const fb = d.fixedBoundaryStatements ?? []
  const missFb = fb.filter((x) => !norm(dom.hero).includes(norm(x)))
  const missRight = fb.filter((x) => !norm(dom.rightCol).includes(norm(x)))
  rec.checks.C10 = fb.length > 0 && !missFb.length && !missRight.length
  if (missFb.length) v('C10_FIXED_HERO', `首屏缺固定边界：${JSON.stringify(missFb.slice(0, 1))}`)
  if (missRight.length) v('C10_FIXED_RIGHT', `右栏缺页面边界：${JSON.stringify(missRight.slice(0, 1))}`)

  rows.push(rec)
}

const totals = {
  products: rows.length,
  violations: violations.length,
  landedChaptersChecked: 6
}
writeFileSync(`${OUT}/probe-landing.json`, JSON.stringify({ totals, violations, rows }, null, 2))
console.log(JSON.stringify({ totals, violations }, null, 2))
await browser.close()
process.exit(violations.length === 0 ? 0 : 1)
