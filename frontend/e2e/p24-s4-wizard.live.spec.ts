/**
 * P24 S4：新建建议书向导 —— 点击「请求 KERT 生成草稿」后，
 * 必须等到后端 SP-20 真实回包且草稿正文渲染完成才截图。
 * 三重等待：网络层 2xx + DOM 层 p24-skill-draft 可见 + 状态层按钮脱离 loading 且正文 >3000 字。
 * 回归防护（FAIL-2026-09-08-02）：各章正文必须互不相同。
 */
import { test, expect, type Page } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'

const SHOT_DIR = path.resolve(process.cwd(), '../evidence/p24-e2e/s4-service-proposal')
const CUSTOMER_ID = 'CUST-CORP-0001'

async function shot(page: Page, name: string): Promise<void> {
  fs.mkdirSync(SHOT_DIR, { recursive: true })
  await page.screenshot({ path: path.join(SHOT_DIR, `${name}.png`), fullPage: true })
}

test.use({ viewport: { width: 1600, height: 1200 } })

test('S4 建议书向导：等 KERT SP-20 真实回包后截图（各章唯一）', async ({ page }) => {
  test.setTimeout(600000)
  const errors: string[] = []
  page.on('pageerror', (e) => errors.push(e.message))

  await page.goto(`/proposals/new?customerId=${CUSTOMER_ID}`, { waitUntil: 'domcontentloaded', timeout: 45000 })
  await page.waitForResponse((r) => /engagement\/customer/.test(r.url()) && r.status() < 400, { timeout: 60000 }).catch(() => null)

  const select = page.locator('[data-testid="p24-customer"]')
  await expect(select).toHaveCount(1)
  await page.waitForFunction(() => {
    const el = document.querySelector('[data-testid="p24-customer"]') as HTMLSelectElement | null
    return !!el && el.options.length > 1 && !!el.value
  }, undefined, { timeout: 60000 })
  await select.selectOption(CUSTOMER_ID)
  await page.waitForTimeout(500)
  await shot(page, '23-proposal-wizard')
  expect(await select.inputValue()).toBe(CUSTOMER_ID)

  const genBtn = page.locator('[data-testid="p24-generate"]')
  await expect(genBtn).toBeEnabled()
  expect(await genBtn.innerText()).toMatch(/请求 (KERT|DKWS) 生成草稿/)

  const respWaiter = page.waitForResponse(
    (r) => /\/api\/v14\/proposals(\?|$)/.test(r.url()) && r.request().method() === 'POST',
    { timeout: 540000 },
  )
  const t0 = Date.now()
  await genBtn.click({ timeout: 20000 })
  const loadingSeen = await page.locator('[data-testid="p24-generate"]', { hasText: /正在请求 (KERT|DKWS) SP-20/ }).isVisible().catch(() => false)
  console.log(`[s4] loading observed=${loadingSeen}`)

  const resp = await respWaiter
  const elapsed = ((Date.now() - t0) / 1000).toFixed(1)
  expect(resp.status()).toBeLessThan(400)
  const payload = await resp.json()
  console.log(`[s4] ${resp.status()} in ${elapsed}s status=${payload.status} draftLen=${(payload.content?.proposalDraft || '').length} citations=${(payload.citations || []).length} unknowns=${(payload.unknowns || []).length}`)
  expect(['SUCCESS', 'PARTIAL']).toContain(payload.status)
  expect((payload.content?.proposalDraft || '').length).toBeGreaterThan(3000)

  await expect(page.locator('[data-testid="p24-skill-draft"]')).toBeVisible({ timeout: 120000 })
  await page.waitForFunction(() => {
    const b = document.querySelector('[data-testid="p24-generate"]') as HTMLElement | null
    const pre = document.querySelector('[data-testid="p24-skill-draft"] pre')
    return !!b && !/正在请求/.test(b.innerText) && !!pre && (pre.textContent || '').trim().length > 3000
  }, undefined, { timeout: 120000 })

  await expect(page.locator('[data-testid="p24-skill-error"]')).toHaveCount(0)
  await expect(page.locator('[data-testid="p24-skill-empty"]')).toHaveCount(0)
  await page.waitForTimeout(1500)

  const draftText = await page.locator('[data-testid="p24-skill-draft"] pre').innerText()
  const headings = draftText.split(/\n##\s+/).slice(1)
  const bodies = headings.map((h) => h.split('\n').slice(1).join('\n').trim()).filter((b) => b.length > 40)
  const uniq = new Set(bodies)
  console.log(`[s4] headings=${headings.length} bodies=${bodies.length} uniqueBodies=${uniq.size} renderedLen=${draftText.trim().length}`)
  expect(headings.length).toBeGreaterThanOrEqual(5)
  expect(uniq.size, '存在逐字相同的章节正文（各章同质回归）').toBe(bodies.length)
  expect(draftText).not.toContain('确定性样例')
  expect(draftText).not.toMatch(/正在请求 (KERT|DKWS) SP-20/)

  await shot(page, '24-proposal-generated')
  await page.locator('[data-testid="p24-skill-draft"]').scrollIntoViewIfNeeded()
  await page.waitForTimeout(800)
  await shot(page, '24b-proposal-draft-detail')

  expect(errors, `页面异常: ${errors.join('; ')}`).toHaveLength(0)
})
