import { mkdirSync, writeFileSync } from 'node:fs'
import { expect, test, type Page } from '@playwright/test'

/**
 * E2E QA · C 组 · SP-20 失败语义复验（需真实 KERT + 真实后端，故为 *.live.spec.ts）。
 *
 * 三个用例**互斥**，必须由操作者按阶段单独执行（KERT 的停/起由 QA 人工完成，脚本不代劳）：
 *
 *   QA_C_PHASE=positive   npx playwright test --config playwright.qa.config.ts \
 *                         e2e/qa-sp20-failure.live.spec.ts -g "\[C3\]"
 *   QA_C_PHASE=kert_down  ... -g "\[C1\]"        # 执行前需先停 KERT(8107)
 *   QA_C_PHASE=no_cp      ... -g "\[C2\]"        # 执行前需以「未供给控制面的工作区」重启 KERT
 *
 * 阶段不匹配 ⇒ 用例以具名 `BLOCKED:` 原因失败（**不 skip、不放行**）。
 * 本文件不含 page.route，路由不拦截；前端侧只做真实点击与观察。
 */

const EVIDENCE_DIR = process.env.QA_EVIDENCE_DIR ?? 'test-results/qa-latest'
mkdirSync(EVIDENCE_DIR, { recursive: true })

const PHASE = process.env.QA_C_PHASE ?? ''

const CUSTOMER_ID = 'CUST-CORP-0001'

type Observed = {
  phase: string
  direct: { status: number; body: unknown } | null
  ui: { errorText: string | null; draftText: string | null; citationsText: string | null }
}

let observed: Observed = { phase: PHASE, direct: null, ui: { errorText: null, draftText: null, citationsText: null } }

function dump(name: string) {
  writeFileSync(`${EVIDENCE_DIR}/${name}.json`, JSON.stringify(observed, null, 2))
}

function guardPhase(expected: string) {
  if (PHASE !== expected) {
    throw new Error(
      `BLOCKED: 阶段不匹配。本用例要求 QA_C_PHASE=${expected}，当前为「${PHASE || '(未设置)'}」。` +
        `环境前置未满足，不得以 skip/pass 处理。`,
    )
  }
}

/** 直连后端 POST /api/v14/proposals（不经 UI，便于精确定位 HTTP 语义）。 */
async function postProposal(page: Page, requestId: string) {
  const resp = await page.request.post('/api/v14/proposals', {
    data: { requestId, customerId: CUSTOMER_ID, context: {} },
    timeout: 180_000,
  })
  let body: unknown = null
  try {
    body = await resp.json()
  } catch {
    body = await resp.text()
  }
  observed.direct = { status: resp.status(), body }
  return { status: resp.status(), body: body as Record<string, any> }
}

/** 走 P24 前端向导：真实点击「请求 KERT 生成草稿」，观察前端错误/草稿呈现。 */
async function driveP24Wizard(page: Page) {
  await page.goto('/proposals/new', { waitUntil: 'networkidle', timeout: 30_000 })
  await page.waitForSelector('[data-testid="p24-empty-draft"]', { timeout: 20_000 })
  const select = page.getByTestId('p24-customer')
  await select.selectOption(CUSTOMER_ID).catch(async () => {
    // 客户选项未加载时不得静默跳过：记为具名失败
    throw new Error(`BLOCKED: P24 客户下拉未提供 ${CUSTOMER_ID}（fetchCustomers 失败？）`)
  })
  await page.getByTestId('p24-generate').click()

  const errBox = page.getByTestId('p24-skill-error')
  const draftBox = page.getByTestId('p24-skill-draft')
  await expect(errBox.or(draftBox)).toBeVisible({ timeout: 175_000 })

  if (await errBox.count()) observed.ui.errorText = (await errBox.innerText()).trim()
  if (await draftBox.count()) {
    observed.ui.draftText = (await draftBox.innerText()).trim()
    const citations = page.locator('[data-testid="p24-skill-draft"] >> text=引用')
    observed.ui.citationsText = (await citations.count()) ? (await citations.first().innerText()).trim() : null
  }
  return { errBox, draftBox }
}

test.describe('QA-C SP-20 失败语义', () => {
  test('[C3] 正例：KERT 正常 ⇒ 200 且草稿非空（citations>=1、proposalDraft 非空）', async ({ page }) => {
    test.setTimeout(200_000)
    guardPhase('positive')

    const { status, body } = await postProposal(page, `QA-C3-${Date.now()}`)
    expect(status, `C3 期望 HTTP 200，实际 ${status}；body=${JSON.stringify(body).slice(0, 400)}`).toBe(200)
    expect(body.status, 'C3 status 必须为 SUCCESS').toBe('SUCCESS')
    const citations = body.citations ?? []
    const draft: string = body.content?.proposalDraft ?? ''
    expect(citations.length, 'C3 citations 必须 >= 1').toBeGreaterThanOrEqual(1)
    expect(draft.trim().length, 'C3 content.proposalDraft 必须非空').toBeGreaterThan(0)

    const { errBox, draftBox } = await driveP24Wizard(page)
    expect(await errBox.count(), 'C3 前端不得出现错误态').toBe(0)
    expect(await draftBox.count(), 'C3 前端必须呈现草稿区').toBe(1)
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-c3-positive.png`, fullPage: true })
    dump('c3-positive')
  })

  test('[C1] 反例：停 KERT 后 ⇒ HTTP 503 + 具名码 KERT_UNAVAILABLE，前端显示具名错误', async ({ page }) => {
    test.setTimeout(200_000)
    guardPhase('kert_down')

    const { status, body } = await postProposal(page, `QA-C1-${Date.now()}`)
    const problems: string[] = []
    if (status !== 503) problems.push(`期望 HTTP 503，实际 ${status}`)
    if (body.status === 'SUCCESS') problems.push('出现旧缺陷：HTTP 响应体 status=SUCCESS（空壳成功）')
    if (body.errorCode !== 'KERT_UNAVAILABLE') problems.push(`期望 errorCode=KERT_UNAVAILABLE，实际 ${body.errorCode}`)
    if (!body.message || String(body.message).trim().length === 0) problems.push('错误响应缺少 message（不可诊断）')

    const { errBox, draftBox } = await driveP24Wizard(page)
    if (await draftBox.count()) problems.push('KERT 不可用时前端仍渲染了草稿区（静默降级）')
    if (!(await errBox.count())) {
      problems.push('KERT 不可用时前端未显示任何错误提示（静默无草稿）')
    } else {
      const errText = (await errBox.innerText()).trim()
      // 规格原文要求「前端须显示具名错误」，对立面是「静默无草稿」；
      // 因此判据 = 有错误提示 + 非通用兜底文案 + 非空。
      if (errText.length === 0) problems.push('前端错误提示为空文本')
      if (errText.includes('KERT 未返回建议书草稿')) problems.push(`前端仅为通用兜底文案，未透出后端诊断：${errText}`)
    }

    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-c1-kert-down.png`, fullPage: true })
    dump('c1-kert-down')
    expect(problems, `C1 失败项：\n${problems.join('\n')}`).toEqual([])
  })

  test('[C2] 反例：KERT 可连但未供给控制面 ⇒ 503 且 message 含 KERT 错误码', async ({ page }) => {
    test.setTimeout(200_000)
    guardPhase('no_cp')

    const { status, body } = await postProposal(page, `QA-C2-${Date.now()}`)
    const message = String(body.message ?? '')
    const problems: string[] = []
    if (status !== 503) problems.push(`期望 HTTP 503，实际 ${status}`)
    if (body.status === 'SUCCESS') problems.push('出现旧缺陷：HTTP 响应体 status=SUCCESS（空壳成功）')
    if (body.errorCode !== 'KERT_UNAVAILABLE') problems.push(`期望 errorCode=KERT_UNAVAILABLE，实际 ${body.errorCode}`)
    if (!/KERT_PERMISSION_DENIED|ROUTE_POLICY_ABSENT|ROUTE_UNRESOLVED|KERT_CONTEXT_INSUFFICIENT|KERT_[A-Z_]+/.test(message)) {
      problems.push(`message 未包含任何 KERT 具名错误码：${message}`)
    }

    const { errBox, draftBox } = await driveP24Wizard(page)
    if (await draftBox.count()) problems.push('未供给控制面时前端仍渲染了草稿区（不得渲染成成功）')
    if (!(await errBox.count())) {
      problems.push('未供给控制面时前端未显示错误提示（被渲染成成功）')
    } else {
      const errText = (await errBox.innerText()).trim()
      if (errText.length === 0) problems.push('前端错误提示为空文本')
      if (errText.includes('KERT 未返回建议书草稿')) problems.push(`前端仅为通用兜底文案，未透出后端诊断：${errText}`)
    }

    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-c2-no-control-plane.png`, fullPage: true })
    dump('c2-no-control-plane')
    expect(problems, `C2 失败项：\n${problems.join('\n')}`).toEqual([])
  })
})
