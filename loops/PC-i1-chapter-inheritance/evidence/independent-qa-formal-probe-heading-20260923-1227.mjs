/**
 * PC-i1 独立 QA 探针 4：C12 区块**标题节号**与 meta 实际节号是否自洽（正常路径）。
 * 用法：node probe-heading.mjs <outDir>
 */
import { chromium } from 'playwright'
import { writeFileSync, mkdirSync } from 'node:fs'

const OUT = process.argv[2] || '.'
mkdirSync(OUT, { recursive: true })
const targets = ['PROD-FIN-003', 'PROD-CM-003', 'PROD-FIN-001', 'PROD-IB-001']

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } })
const out = []

for (const pid of targets) {
  await page.goto(`http://127.0.0.1:15173/product-center/${pid}`, { waitUntil: 'domcontentloaded' })
  await page
    .locator('[data-testid="pc-inherited-chapters"]')
    .waitFor({ timeout: 20000 })
    .catch(() => {})
  const r = await page.evaluate(() => {
    const pick = (k) => {
      const el = document.querySelector(`[data-testid="pc-inherited-${k}"]`)
      if (!el) return null
      const head = el.querySelector('.pc-inherited-block-head')?.textContent?.replace(/\s+/g, ' ').trim()
      const meta = el.querySelector(`[data-testid="pc-inherited-${k}-meta"]`)?.textContent?.replace(/\s+/g, ' ').trim()
      return { head, meta }
    }
    return { c12: pick('c12'), c6: pick('c6') }
  })
  out.push({ productId: pid, ...r })
}

writeFileSync(`${OUT}/probe-heading.json`, JSON.stringify(out, null, 2))
console.log(JSON.stringify(out, null, 2))
await browser.close()
