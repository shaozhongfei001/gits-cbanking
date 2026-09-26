import { expect, test, type Page } from '@playwright/test'

/**
 * 访前链端到端（P11 → P12 → P13 → P14），**含写路径与跨服务 KERT 触发**。
 *
 * 为什么存在：2026-09-23 之前**没有任何可信的"业务场景端到端"用例** ——
 * `five-scenarios.live.spec.ts` 端口写死 `8082`/`8106`（现行 `18080`/`8107`）、
 * 被 `playwright.config.ts` 的 `testIgnore` 默认排除，且多处为**条件断言**
 * （`if (await nav.isVisible())` ⇒ 会自跳过）⇒ 不能作为"链路已验证"的依据。
 *
 * 本用例的口径（**严格，不得放宽**）：
 *   · **零条件跳过**：所有前置不满足即失败（不得 `if (visible)` 式放行）；
 *   · **写路径必须留证**：断言 `201 POST /journey/start` 与 `200 POST …/prepare-previsit` 真实发生；
 *   · **跨服务必须留证**：断言分块出现**装配轨迹**（`skillId` / `KM-CORP-RM-PREVISIT`）；
 *   · **全链无 4xx/5xx**（无白名单、无豁免）；
 *   · 页面文案为「尚未执行一键访前」等**如实空态**时，`点击生成访前包` 后该文案**必须消失**。
 *
 * 前置：后端 `18080` 已启动、KERT `8107` 可服务、前端 dev server（由本配置 webServer 起，
 * `VITE_API_PROXY_TARGET=http://127.0.0.1:18080` 注入）。
 * 运行：
 *   VITE_API_PROXY_TARGET=http://127.0.0.1:18080 \
 *   npx playwright test --config=playwright.live.config.ts e2e/previsit-chain.live.spec.ts
 */

const CUSTOMER_ID = process.env.LIVE_CUSTOMER_ID ?? 'CUST-CORP-0001'

/** 主区正文（剔除导航/侧栏，避免把导航文本当业务内容）。 */
async function mainText(page: Page): Promise<string> {
  return page.evaluate(() => {
    const clone = document.body.cloneNode(true) as HTMLElement
    clone
      .querySelectorAll('aside,nav,header,script,style,[class*=sidebar]')
      .forEach((el) => el.remove())
    return (clone.innerText || '').replace(/\s+/g, ' ').trim()
  })
}

test.describe('访前链端到端（P11→P14 · 含写路径与 KERT 触发）', () => {
  test('启动旅程 → 信息缺口 → 生成访前包 → 访前包预览', async ({ page }) => {
    const writes: string[] = []
    const failures: string[] = []
    page.on('response', (res) => {
      const url = res.url()
      if (!url.includes('/api/')) {
        return
      }
      const method = res.request().method()
      if (method !== 'GET') {
        writes.push(`${res.status()} ${method} ${url}`)
      }
      if (res.status() >= 400) {
        failures.push(`${res.status()} ${method} ${url}`)
      }
    })

    // 〇 前置判据：KYC 画像必须可用（本链的期望值来源；不成立即失败，不得跳过）
    const gapResp = await page.request.get(`/api/v1/engagement/kyc/${CUSTOMER_ID}/gap-profile`)
    expect(
      gapResp.ok(),
      `前置失败：GET /api/v1/engagement/kyc/${CUSTOMER_ID}/gap-profile 应 200，实际 ${gapResp.status()}`
    ).toBe(true)

    // ① P45 列表：启动旅程（写路径）——启动后默认进入该旅程工作区（journeyId 进 URL）
    await page.goto('/engagement')
    await expect(page.getByTestId('p45-journey-list')).toBeVisible()

    const startBtn = page.getByTestId('p45-start-journey')
    await expect(startBtn, '启动旅程入口必须可见可用（若被禁用，应改由合同授权，不得跳过本用例）').toBeEnabled()
    await startBtn.click()

    // 启动旅程需先选客户（保持既有交互）
    const firstCustomer = page.locator('[data-testid^="p45-pick-"]').first()
    await expect(firstCustomer).toBeVisible({ timeout: 30000 })
    await firstCustomer.click()

    // 断言 UI 真的流转到工作区（而非仅接口 201）
    await expect(page).toHaveURL(/\/engagement\/workspace\/[0-9a-f-]{8,}/, { timeout: 30000 })
    await expect(page.locator('.ew-bar')).toBeVisible()
    await expect(page.locator('.ew-bar')).not.toContainText('未启动', { timeout: 30000 })
    await expect(page.locator('.ew-bar')).toContainText('完成旅程')
    expect(
      writes.some((w) => w.startsWith('201') && w.includes('/engagement/journey/start')),
      `应发生 201 POST /journey/start；实际写请求：${writes.join(' | ') || '(无)'}`
    ).toBe(true)

    // ② P12：访前目标与信息缺口（读路径，必须带 journeyId 上下文）
    await page.getByTestId('p11-open-previsit').click()
    await expect(page).toHaveURL(/\/engagement\/previsit\/gaps\?.*journeyId=/)
    await expect(page.getByTestId('p12-previsit-gaps')).toBeVisible()
    const gaps = await mainText(page)
    expect(gaps.length, '访前差距页正文不得为空（空态即失败）').toBeGreaterThan(120)
    expect(
      /已知|未知|优先问题/.test(gaps),
      `访前差距页应呈现缺口事实（已知/未知/优先问题）；实际正文：${gaps.slice(0, 160)}`
    ).toBe(true)

    // ③ P13：访前知识证据装配 —— 先确认「如实空态」，再触发一键访前
    await page.getByTestId('p12-go-evidence').click()
    await expect(page.getByTestId('p13-previsit-evidence')).toBeVisible()
    await expect(page.getByTestId('p13-previsit-evidence')).toContainText('尚未执行一键访前')

    const genBtn = page.getByRole('button', { name: /生成访前包|一键访前/ })
    await expect(genBtn, '「生成访前包」入口必须存在且可用').toBeEnabled()
    await genBtn.click()

    // 跨服务触发：**正向等待**装配轨迹出现
    // （反例：曾以「空态文案消失」为信号 → 会在**加载中态**就继续，读到 119 字的骨架 ⇒ 竞态假失败）
    const p13 = page.getByTestId('p13-previsit-evidence')
    await expect(p13).toContainText(/skillId|KM-CORP-RM-PREVISIT|装配轨迹/, { timeout: 90000 })
    await expect(p13).not.toContainText('尚未执行一键访前')
    const trace = await mainText(page)
    expect(trace.length, '装配轨迹正文过短，疑未真正触发 KERT').toBeGreaterThan(300)
    expect(
      /skillId|KM-CORP-RM-PREVISIT|装配轨迹/.test(trace),
      `应出现装配轨迹（skillId / 知识地图）；实际正文：${trace.slice(0, 200)}`
    ).toBe(true)
    expect(
      writes.some((w) => w.startsWith('200') && w.includes('prepare-previsit')),
      `应发生 200 POST …/prepare-previsit；实际写请求：${writes.join(' | ')}`
    ).toBe(true)

    // ④ P14：访前包预览（必须有实质交付物文本）
    await page.getByTestId('p13-go-pack').click()
    const p14 = page.getByTestId('p14-previsit-pack')
    await expect(p14).toBeVisible()
    await expect(p14).toContainText(/外联脚本|会面脚本/, { timeout: 30000 })
    const pack = await mainText(page)
    expect(pack.length, '访前包正文过短，疑未生成').toBeGreaterThan(300)
    expect(
      /外联脚本|会面脚本/.test(pack),
      `访前包应含外联/会面脚本；实际正文：${pack.slice(0, 200)}`
    ).toBe(true)
    await expect(page.getByTestId('p14-previsit-pack')).not.toContainText('尚未生成访前包')

    // ⑤ 全链无 4xx/5xx（无白名单、无豁免）
    expect(failures, `本链出现 4xx/5xx：\n${failures.join('\n')}`).toEqual([])
  })
})
