import { mkdirSync, writeFileSync } from 'node:fs'
import { expect, test, type Page, type Response } from '@playwright/test'

/**
 * E2E QA 验收用例 · A/B/D/E/G 组（F 组回归由既有 spec 全量运行覆盖）。
 *
 * 纪律（本文件自我约束，可被 grep 验证）：
 * - **不使用 `page.route`**：本文件内没有任何请求 stub / mock / fulfill；
 * - 所有请求都是 15173 dev server → vite 代理 → 18080 后端的真实链路；
 * - 断言与产品实现冲突时不放宽，先收集全部违规再失败，保留完整证据。
 */

const EVIDENCE_DIR = process.env.QA_EVIDENCE_DIR ?? 'test-results/qa-latest'
const HAR_DIR = `${EVIDENCE_DIR}/har`
const BACKEND = process.env.QA_BACKEND_URL ?? 'http://127.0.0.1:18080'

mkdirSync(HAR_DIR, { recursive: true })

type NetEntry = {
  url: string
  method: string
  status: number
  resourceType: string
  startedDateTime: string
  time: number
  mimeType: string
  bodySize: number
  /** 仅对 /api/ 响应体留证（截断 200KB），其余为 null */
  body: string | null
}

type Recorder = {
  pageErrors: string[]
  consoleErrors: string[]
  consoleWarnings: string[]
  requestFailures: string[]
  net: NetEntry[]
}

function createRecorder(page: Page): Recorder {
  const rec: Recorder = {
    pageErrors: [],
    consoleErrors: [],
    consoleWarnings: [],
    requestFailures: [],
    net: [],
  }
  page.on('pageerror', (err) => {
    rec.pageErrors.push(err.stack ?? String(err))
  })
  page.on('console', (msg) => {
    // 带页面归属，便于定位 console.error 来自哪一页（弱证据不算证据）
    const where = `[${page.url()}]`
    if (msg.type() === 'error') rec.consoleErrors.push(`${where} ${msg.text()}`)
    if (msg.type() === 'warning') rec.consoleWarnings.push(`${where} ${msg.text()}`)
  })
  page.on('requestfailed', (req) => {
    rec.requestFailures.push(`${req.method()} ${req.url()} :: ${req.failure()?.errorText ?? 'unknown'}`)
  })
  page.on('response', async (resp: Response) => {
    const req = resp.request()
    const isApi = resp.url().includes('/api/') || resp.url().includes('/kert-api/')
    let body: string | null = null
    if (isApi) {
      try {
        body = (await resp.text()).slice(0, 200_000)
      } catch {
        body = null
      }
    }
    rec.net.push({
      url: resp.url(),
      method: req.method(),
      status: resp.status(),
      resourceType: req.resourceType(),
      startedDateTime: new Date().toISOString(),
      time: Math.max(0, Math.round(req.timing().responseEnd)),
      mimeType: (resp.headers()['content-type'] ?? '').split(';')[0],
      bodySize: body ? body.length : -1,
      body,
    })
  })
  return rec
}

/** 生成 HAR 1.2 兼容结构（字段齐全，entries 来自真实响应）。 */
function toHar(entries: NetEntry[]) {
  return {
    log: {
      version: '1.2',
      creator: { name: 'gits-cbanking-e2e-qa', version: '1.0' },
      entries: entries.map((e) => ({
        startedDateTime: e.startedDateTime,
        time: e.time,
        request: {
          method: e.method,
          url: e.url,
          httpVersion: 'HTTP/1.1',
          headers: [],
          queryString: [],
          cookies: [],
          headersSize: -1,
          bodySize: -1,
        },
        response: {
          status: e.status,
          statusText: '',
          httpVersion: 'HTTP/1.1',
          headers: [],
          cookies: [],
          content: { size: e.bodySize, mimeType: e.mimeType, text: e.body },
          redirectURL: '',
          headersSize: -1,
          bodySize: e.bodySize,
        },
        cache: {},
        timings: { send: -1, wait: -1, receive: -1 },
      })),
    },
  }
}

let current: { id: string; rec: Recorder } | null = null

test.beforeEach(async ({ page }, testInfo) => {
  current = { id: testInfo.titlePath.slice(1).join('__').replace(/[^\w\u4e00-\u9fa5-]+/g, '_'), rec: createRecorder(page) }
})

test.afterEach(async ({}, testInfo) => {
  if (!current) return
  const { id, rec } = current
  writeFileSync(
    `${EVIDENCE_DIR}/${id}.json`,
    JSON.stringify({ testId: id, status: testInfo.status, ...rec }, null, 2),
  )
  writeFileSync(`${HAR_DIR}/${id}.har`, JSON.stringify(toHar(rec.net), null, 2))
  current = null
})

// ─────────────────────────────────────────────────────────────────────────────
// 常量：8 章清册（与 src/components/product-center/sections.ts 逐字一致）
// ─────────────────────────────────────────────────────────────────────────────

type ChapterSpec = { key: string; title: string; anchor: string; field: string; kind: 'list' | 'object' }

const CHAPTERS: ChapterSpec[] = [
  { key: 'OVERVIEW', title: '60 秒读懂', anchor: 'pc-sec-overview', field: 'summary', kind: 'object' },
  { key: 'TERMS', title: '核心条款', anchor: 'pc-sec-terms', field: 'terms', kind: 'list' },
  { key: 'FIT', title: '适用边界', anchor: 'pc-sec-fit', field: 'boundaries', kind: 'list' },
  { key: 'PROCESS', title: '办理流程', anchor: 'pc-sec-process', field: 'processSteps', kind: 'list' },
  { key: 'MATERIALS', title: '申请材料', anchor: 'pc-sec-materials', field: 'materialGroups', kind: 'list' },
  { key: 'PRICING', title: '价格与协议', anchor: 'pc-sec-pricing', field: 'pricingItems', kind: 'list' },
  { key: 'COMPARE', title: '同类产品比较', anchor: 'pc-sec-compare', field: 'comparison', kind: 'object' },
  { key: 'FAQ', title: '常见问题', anchor: 'pc-sec-faq', field: 'faqs', kind: 'list' },
]

const FORBIDDEN_PATH_TOKENS = ['/home/', '/Users/', 'Leibniz-KERT', 'gits-cbanking']

/** 同源静态资源判定：本次验收只关心 css/js/font/图片（A2）。 */
const STATIC_TYPES = new Set(['stylesheet', 'script', 'font', 'image'])

/**
 * 章节正文文本：剔除「章节号 + 标题 + 待接入 PCx 标签」后剩下的内容。
 * 用于区别「有正文」与「只有标题的空壳章节」——空壳必须被判失败。
 */
async function chapterBodyText(page: Page, ch: ChapterSpec): Promise<string> {
  const raw = await page.locator(`[data-testid="pc-chapter"][data-section-key="${ch.key}"]`).innerText()
  return raw
    .replace(ch.title, '')
    .replace(/^[\s\d]*/, '')
    .replace(/待接入\s*PC\d/g, '')
    .trim()
}

/** 章节是否在页面内呈现了具名「待接入 <批次>」。 */
async function chapterPendingTag(page: Page, ch: ChapterSpec): Promise<string | null> {
  const raw = await page.locator(`[data-testid="pc-chapter"][data-section-key="${ch.key}"]`).innerText()
  const m = raw.match(/待接入\s*PC\d/)
  return m ? m[0] : null
}

async function apiGet(page: Page, path: string) {
  return page.request.get(path)
}

// ─────────────────────────────────────────────────────────────────────────────
// A 组 · 环境与资源完整性
// ─────────────────────────────────────────────────────────────────────────────

const A_PAGES = [
  '/product-center',
  '/workbench',
  '/product-knowledge/interpretation',
  '/analytics/operating-metrics',
  '/approvals',
]

test.describe('QA-A 环境与资源完整性', () => {
  test('A1 页面 200 且 HTML 非空（产品中心 + 4 个其他页）', async ({ page }) => {
    const problems: string[] = []
    for (const path of A_PAGES) {
      const resp = await page.goto(path, { waitUntil: 'domcontentloaded', timeout: 20000 })
      const status = resp?.status() ?? 0
      const html = (await resp?.text().catch(() => '')) ?? ''
      if (status !== 200) problems.push(`${path} HTTP ${status}`)
      if (html.trim().length === 0) problems.push(`${path} HTML 为空`)
      await page.waitForTimeout(1500)
      const appHtml = await page.locator('#app').innerHTML().catch(() => '')
      if (appHtml.trim().length === 0) problems.push(`${path} #app 渲染为空（白屏）`)
      await page.screenshot({ path: `${EVIDENCE_DIR}/shot-a1-${path.replace(/\//g, '_')}.png` })
    }
    expect(problems, `A1 失败项：\n${problems.join('\n')}`).toEqual([])
  })

  test('A2 同源 css/js/font/image 无 4xx/5xx', async ({ page }) => {
    const bad: string[] = []
    for (const path of A_PAGES) {
      await page.goto(path, { waitUntil: 'networkidle', timeout: 25000 })
    }
    const origin = new URL(page.url()).origin
    const rec = current!.rec
    for (const e of rec.net) {
      if (!e.url.startsWith(origin)) continue
      const isStatic = STATIC_TYPES.has(e.resourceType) || /\.(css|js|mjs|woff2?|ttf|svg|png|jpg|webp)(\?|$)/.test(e.url)
      if (!isStatic) continue
      if (e.status >= 400) bad.push(`${e.status} ${e.resourceType} ${e.url}`)
    }
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-a2.png`, fullPage: false })
    expect(bad, `A2 失败的同源静态资源：\n${bad.slice(0, 40).join('\n')}`).toEqual([])
  })

  test('A3 全程无 pageerror / console.error（无白名单）', async ({ page }) => {
    for (const path of A_PAGES) {
      await page.goto(path, { waitUntil: 'networkidle', timeout: 25000 })
      await page.waitForTimeout(800)
    }
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await page.waitForTimeout(1200)
    const { pageErrors, consoleErrors } = current!.rec
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-a3.png` })
    expect(
      { pageErrors, consoleErrors },
      `A3 pageerror=${pageErrors.length} consoleError=${consoleErrors.length}`,
    ).toEqual({ pageErrors: [], consoleErrors: [] })
  })

  test('A4 关键 API 真实发起且 200（浏览器响应体与直连后端逐字节一致，证明非 stub）', async ({ page }) => {
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await page.waitForTimeout(1500)

    const required = [
      '/api/v1/product-center/families',
      '/api/v1/product-center/products',
      '/api/v1/product-center/products/PROD-CM-003',
    ]
    const problems: string[] = []
    const seen = current!.rec.net.filter((e) => e.url.includes('/api/'))
    for (const path of required) {
      const hits = seen.filter((e) => e.url.includes(path) && e.method === 'GET')
      if (hits.length === 0) {
        problems.push(`${path} 未在浏览器内真实发起`)
        continue
      }
      if (hits[0].status !== 200) problems.push(`${path} HTTP ${hits[0].status}`)
    }

    // 反 stub 证明：把浏览器拿到的那一份响应体，与直连 18080 的响应体做逐字节比对
    const browserFamilies = seen.find((e) => e.url.includes('/api/v1/product-center/families') && e.body)
    const directFamilies = await page.request.get(`${BACKEND}/api/v1/product-center/families`)
    const directBody = await directFamilies.text()
    if (!browserFamilies?.body) {
      problems.push('未能取到浏览器侧 families 响应体（无法证明非 stub）')
    } else if (browserFamilies.body !== directBody) {
      problems.push('浏览器侧 families 响应体与直连后端不一致（疑似被 stub 或中间层改写）')
    }

    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-a4.png` })
    expect(problems, `A4 失败项：\n${problems.join('\n')}`).toEqual([])
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// B 组 · 产品中心 8 章
// ─────────────────────────────────────────────────────────────────────────────

test.describe('QA-B 产品中心 8 章', () => {
  test('B1/B2 目录 6 族 13 卡；点选产品 URL 与首屏标识一致', async ({ page }) => {
    await page.setViewportSize({ width: 1680, height: 1000 })
    await page.goto('/product-center', { waitUntil: 'networkidle', timeout: 25000 })

    await expect(page.getByTestId('pc-catalog-family')).toHaveCount(6)
    await expect(page.getByTestId('pc-catalog-product')).toHaveCount(13)

    await page.getByTestId('pc-catalog-product').filter({ hasText: '法人账户透支' }).getByRole('button').click()
    await expect(page).toHaveURL(/\/product-center\/PROD-CM-003/, { timeout: 15000 })
    await expect(page.getByTestId('pc-hero-product-id')).toHaveText('PROD-CM-003')
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-b1-b2.png`, fullPage: false })
  })

  test('B3 导航 8 项、标题逐字匹配清册、锚点可跳', async ({ page }) => {
    await page.setViewportSize({ width: 1680, height: 1000 })
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await expect(page.getByTestId('pc-chapter')).toHaveCount(8, { timeout: 15000 })

    const nav = page.getByTestId('pc-section-link')
    await expect(nav).toHaveCount(8)
    const titles: string[] = []
    for (let i = 0; i < 8; i += 1) titles.push((await nav.nth(i).innerText()).trim())
    expect(titles, 'B3 导航标题须与清册逐字一致').toEqual(CHAPTERS.map((c) => c.title))

    const problems: string[] = []
    for (const ch of CHAPTERS) {
      await page.getByTestId('pc-section-link').filter({ hasText: ch.title }).first().click()
      await page.waitForTimeout(500)
      if (!page.url().includes(`#${ch.anchor}`)) problems.push(`点击「${ch.title}」后 URL 无 #${ch.anchor}（实际 ${page.url()}）`)
      const attached = await page.locator(`#${ch.anchor}`).count()
      if (attached !== 1) problems.push(`锚点元素 #${ch.anchor} 数量=${attached}`)
    }
    // 末章「常见问题」点击后应真正滚入视口（锚点可跳的用户可见行为）
    await page.getByTestId('pc-section-link').filter({ hasText: '常见问题' }).first().click()
    await expect(page.locator('#pc-sec-faq')).toBeInViewport({ timeout: 8000 })
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-b3.png` })
    expect(problems, `B3 失败项：\n${problems.join('\n')}`).toEqual([])
  })

  test('B4 逐章二选一：有数据⇒正文非空且与接口一致；无数据⇒具名「待接入 <批次>」', async ({ page }) => {
    await page.setViewportSize({ width: 1680, height: 1200 })
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await expect(page.getByTestId('pc-chapter')).toHaveCount(8, { timeout: 15000 })

    const apiResp = await apiGet(page, '/api/v1/product-center/products/PROD-CM-003')
    expect(apiResp.status()).toBe(200)
    const detail = (await apiResp.json()) as Record<string, unknown>

    const violations: string[] = []
    const perChapter: Record<string, string> = {}

    for (const ch of CHAPTERS) {
      const raw = detail[ch.field]
      const hasPayload =
        ch.kind === 'list' ? Array.isArray(raw) && raw.length > 0 : raw !== null && raw !== undefined
      const pendingCount = await page
        .locator(`[data-testid="pc-chapter"][data-section-key="${ch.key}"] [data-testid="pc-chapter-pending"]`)
        .count()
      const bodyText = await chapterBodyText(page, ch)
      const pendingTag = await chapterPendingTag(page, ch)

      if (hasPayload) {
        perChapter[ch.key] = `hasPayload=true, pendingTag=${pendingTag ?? '无'}, bodyLen=${bodyText.length}`
        if (pendingTag) violations.push(`${ch.title}（${ch.key}）接口有数据却显示「${pendingTag}」`)
        if (bodyText.length === 0) {
          violations.push(`${ch.title}（${ch.key}）接口有数据但章节正文为空 ⇒ 空白章节（P0）`)
        }
      } else {
        perChapter[ch.key] = `hasPayload=false, pendingCount=${pendingCount}, pendingTag=${pendingTag ?? '无'}`
        if (pendingTag === null) {
          violations.push(`${ch.title}（${ch.key}）无数据却未显示具名「待接入 <批次>」（P0）`)
        }
        if (pendingCount !== 1) {
          violations.push(`${ch.title}（${ch.key}）无数据但未接入说明段落数量=${pendingCount}（期望 1）`)
        }
      }
    }

    // 抽查 ≥1 处正文与接口一致：TERMS 第 1 条的 businessDefinition 必须出现在正文里
    const firstTerm = (detail['terms'] as Array<Record<string, string>>)[0]
    if (firstTerm?.businessDefinition) {
      const termsChapter = page.locator('[data-testid="pc-chapter"][data-section-key="TERMS"]')
      const termsText = await termsChapter.innerText()
      if (!termsText.includes(firstTerm.businessDefinition)) {
        violations.push(`核心条款正文未包含接口 terms[0].businessDefinition（「${firstTerm.businessDefinition.slice(0, 30)}…」）`)
      }
    }

    writeFileSync(`${EVIDENCE_DIR}/b4-per-chapter.json`, JSON.stringify({ perChapter, violations }, null, 2))
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-b4.png`, fullPage: true })
    expect(violations, `B4 违规清单：\n${violations.join('\n')}`).toEqual([])
  })

  test('B5 元信息缺失位显示「待维护/未设定」，不得伪造日期', async ({ page }) => {
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await expect(page.getByTestId('pc-governance')).toBeVisible({ timeout: 15000 })

    const apiResp = await apiGet(page, '/api/v1/product-center/products/PROD-CM-003')
    const detail = (await apiResp.json()) as Record<string, any>
    const version = detail.version

    const problems: string[] = []
    const banner = await page.getByTestId('pc-knowledge-as-of').innerText()
    if (version.knowledgeAsOf === null) {
      if (!banner.includes('基准日待维护')) problems.push(`knowledgeAsOf=null 但环境条未显示「基准日待维护」：${banner}`)
    } else if (!banner.includes(version.knowledgeAsOf)) {
      problems.push(`环境条基准日与接口不一致：页面「${banner}」接口「${version.knowledgeAsOf}」`)
    }

    const gov = await page.getByTestId('pc-governance').innerText()
    if (version.effectiveFrom === null && !gov.includes('未设定')) problems.push('生效日为空却未显示「未设定」')
    if (version.reviewedBy.length === 0 && !gov.includes('无审核记录')) problems.push('无审核记录却未声明')
    if (version.reviewedBy.length === 0 && !gov.includes('不得视为已审核')) problems.push('无审核记录缺少「不得视为已审核」限定')
    expect(problems, `B5 失败项：\n${problems.join('\n')}`).toEqual([])
  })

  test('B6 页面文本不含服务器绝对路径', async ({ page }) => {
    for (const path of ['/product-center/PROD-CM-003', '/product-knowledge/interpretation']) {
      await page.goto(path, { waitUntil: 'networkidle', timeout: 25000 })
      await page.waitForTimeout(1200)
      const body = await page.locator('body').innerText()
      for (const token of FORBIDDEN_PATH_TOKENS) {
        expect(body, `${path} 页面文本不得包含 ${token}`).not.toContain(token)
      }
    }
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-b6.png` })
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// D 组 · 跨页一致性与证据链
// ─────────────────────────────────────────────────────────────────────────────

test.describe('QA-D 跨页一致性与证据链', () => {
  test('D1 同一产品在产品中心 / 解读页同字段一致', async ({ page }) => {
    const problems: string[] = []

    const pc = (await (await apiGet(page, '/api/v1/product-center/products')).json()) as Array<Record<string, any>>
    const cards = (await (await apiGet(page, '/api/v1/product-knowledge/cards')).json()) as Array<Record<string, any>>

    const pcById = new Map(pc.map((p) => [p.productId, p]))
    const cardById = new Map(cards.map((c) => [c.productId, c]))
    expect(pcById.size).toBeGreaterThan(0)
    expect(cardById.size).toBeGreaterThan(0)

    const rows: Array<Record<string, string>> = []
    for (const [id, p] of pcById) {
      const c = cardById.get(id)
      if (!c) {
        problems.push(`${id} 存在于产品中心目录但不在解读页目录中`)
        continue
      }
      rows.push({ productId: id, pcName: p.productName, cardName: c.name, pcFamily: p.familyName, cardFamily: c.familyName })
      if (p.productName !== c.name) problems.push(`${id} 产品名不一致：产品中心「${p.productName}」 vs 解读页「${c.name}」`)
      if (p.familyName !== c.familyName) problems.push(`${id} 产品族名不一致：产品中心「${p.familyName}」 vs 解读页「${c.familyName}」`)
    }
    for (const id of cardById.keys()) {
      if (!pcById.has(id)) problems.push(`${id} 存在于解读页目录但不在产品中心目录中（一页有一页空）`)
    }

    // 页面级复验：产品中心首屏 vs 解读页摘要卡（同一产品 PROD-CM-003）
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    const hero = await page.getByTestId('pc-hero').innerText()
    await page.goto('/product-knowledge/interpretation', { waitUntil: 'networkidle', timeout: 25000 })
    await page.getByText('法人账户透支', { exact: false }).first().click()
    await page.waitForTimeout(1200)
    const body = await page.locator('body').innerText()
    if (hero.includes('法人账户透支') && !body.includes('法人账户透支')) {
      problems.push('产品中心首屏有该产品，解读页选中后页面无该产品名（一页有一页空）')
    }

    writeFileSync(`${EVIDENCE_DIR}/d1-cross-page.json`, JSON.stringify({ rows, problems }, null, 2))
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-d1.png`, fullPage: false })
    expect(problems, `D1 失败项：\n${problems.join('\n')}`).toEqual([])
  })

  test('D2 证据/出处与限制声明可见（不得静默隐藏）', async ({ page }) => {
    const problems: string[] = []

    // ① 产品中心侧：受控限制必须常驻可见
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    const gov = page.getByTestId('pc-governance')
    await expect(gov).toBeVisible({ timeout: 15000 })
    const govText = await gov.innerText()
    for (const token of ['DRAFT', '无审核记录', '制度与证据', '待接入 PC4']) {
      if (!govText.includes(token)) problems.push(`产品中心治理栏缺少限制声明「${token}」`)
    }
    if (!(await page.getByTestId('pc-publish-status').innerText()).includes('未发布受控版本')) {
      problems.push('产品中心未声明「未发布受控版本」')
    }

    // ② 解读页侧：出处与「未复核（不补值）」限制必须可见
    await page.goto('/product-knowledge/interpretation', { waitUntil: 'networkidle', timeout: 25000 })
    await page.waitForSelector('[data-testid="p38-product-interpretation"]', { timeout: 20000 })
    await page.waitForTimeout(1500)
    const srcPath = page.locator('.src-path').first()
    if ((await srcPath.count()) === 0) problems.push('解读页未呈现产品原始文件（出处缺失）')

    const cardList = (await (await apiGet(page, '/api/v1/product-knowledge/cards')).json()) as Array<Record<string, any>>
    const target = cardList[0]
    const interpResp = await apiGet(
      page,
      `/api/v1/product-knowledge/${encodeURIComponent(target.productId)}/interpretation?view=ELIGIBILITY&purpose=INTERPRETATION`,
    )
    if (interpResp.status() === 200) {
      const interp = (await interpResp.json()) as Record<string, any>
      const pageText = await page.locator('body').innerText()
      if (interp.releaseId && !pageText.includes(interp.releaseId)) problems.push(`解读页未呈现 Release 标识 ${interp.releaseId}`)
      const unknownFields = (interp.fields as Array<Record<string, any>>).filter((f) => f.knowledgeState === 'UNKNOWN')
      if (unknownFields.length > 0 && !pageText.includes('未复核（不补值）')) {
        problems.push(`接口有 ${unknownFields.length} 个 UNKNOWN 字段，但页面未显示「未复核（不补值）」限制`)
      }
      const withEvidence = (interp.fields as Array<Record<string, any>>).filter((f) => f.evidenceSummaries.length > 0)
      if (withEvidence.length > 0) {
        const quote = withEvidence[0].evidenceSummaries[0].quoteExcerpt
        const summaryTitle = `依据原文（${withEvidence[0].evidenceSummaries.length} 条）`
        const toggle = page.getByText(summaryTitle, { exact: false }).first()
        if ((await toggle.count()) === 0) {
          problems.push('有证据字段未呈现「依据原文」入口（证据被静默隐藏）')
        } else {
          await toggle.click()
          await page.waitForTimeout(600)
          const expanded = await page.locator('body').innerText()
          if (quote && !expanded.includes(quote.slice(0, 20))) problems.push('展开「依据原文」后未见 evidenceSummaries.quoteExcerpt 原文')
        }
      }
    } else {
      problems.push(`解读接口非 200（${interpResp.status()}），无法核对证据链`)
    }

    writeFileSync(`${EVIDENCE_DIR}/d2-evidence.json`, JSON.stringify({ problems }, null, 2))
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-d2.png`, fullPage: false })
    expect(problems, `D2 失败项：\n${problems.join('\n')}`).toEqual([])
  })

  test('D3 降级页 / 审计追溯页 / 审批页可开、无 console 错误、无空白', async ({ page }) => {
    const problems: string[] = []
    for (const path of ['/degrade', '/audit-trace', '/approvals']) {
      const before = current!.rec.consoleErrors.length
      const resp = await page.goto(path, { waitUntil: 'networkidle', timeout: 25000 })
      await page.waitForTimeout(1000)
      if ((resp?.status() ?? 0) !== 200) problems.push(`${path} HTTP ${resp?.status()}`)
      const text = (await page.locator('body').innerText()).trim()
      if (text.length < 20) problems.push(`${path} 页面近乎空白（innerText 长度 ${text.length}）`)
      const newErrors = current!.rec.consoleErrors.slice(before)
      if (newErrors.length > 0) problems.push(`${path} console.error ${newErrors.length} 条：${newErrors[0]}`)
      await page.screenshot({ path: `${EVIDENCE_DIR}/shot-d3-${path.replace(/\//g, '_')}.png`, fullPage: true })
    }
    expect(problems, `D3 失败项：\n${problems.join('\n')}`).toEqual([])
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// E 组 · 诚实性红线
// ─────────────────────────────────────────────────────────────────────────────

test.describe('QA-E 诚实性红线', () => {
  test('E1 未接入能力显式标注', async ({ page }) => {
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await expect(page.getByTestId('pc-identity')).toContainText('身份服务未接入', { timeout: 15000 })
    await expect(page.getByTestId('pc-publish-status')).toContainText('未发布受控版本')
    const gov = await page.getByTestId('pc-governance').innerText()
    const pendingCount = await page.getByTestId('pc-gov-pending').count()
    expect(pendingCount, '治理栏未接入项数量').toBeGreaterThanOrEqual(3)
    expect(gov).toContain('待接入 PC4')

    const chapters = await page.getByTestId('pc-chapter').count()
    const pending = await page.getByTestId('pc-chapter-pending').count()
    const noPendingAndEmpty: string[] = []
    const detail: Record<string, string> = {}
    for (const ch of CHAPTERS) {
      const bodyText = await chapterBodyText(page, ch)
      const pendingTag = await chapterPendingTag(page, ch)
      detail[ch.key] = `pendingTag=${pendingTag ?? '无'} bodyLen=${bodyText.length}`
      // 既没有「待接入 <批次>」具名标注，又没有正文 ⇒ 空壳章节（P0）
      if (pendingTag === null && bodyText.length === 0) noPendingAndEmpty.push(ch.key)
    }
    writeFileSync(
      `${EVIDENCE_DIR}/e1-pending.json`,
      JSON.stringify({ chapters, pending, detail, noPendingAndEmpty }, null, 2),
    )
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-e1.png` })
    expect(noPendingAndEmpty, '存在既无正文又无「待接入 <批次>」标注的空壳章节（P0）').toEqual([])
  })

  test('E2 演示数据必须显式标注，不得当作真实数据呈现（P0 红线）', async ({ page }) => {
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await expect(page.getByTestId('pc-env-banner')).toBeVisible({ timeout: 15000 })

    const apiResp = await apiGet(page, '/api/v1/product-center/products/PROD-CM-003')
    const detail = (await apiResp.json()) as Record<string, any>

    const problems: string[] = []
    const isDemo = detail.version?.isDemo === true && detail.version?.environment === 'DEMO'
    const envTag = await page.getByTestId('pc-env-tag').innerText()
    const dataEnv = await page.getByTestId('pc-data-environment').innerText()
    const provenance = await page.getByTestId('pc-data-provenance').innerText()

    if (isDemo) {
      if (!envTag.includes('DEMO')) problems.push('接口 isDemo=true 但顶部环境条未标注 DEMO')
      if (!envTag.includes('演示数据')) problems.push('接口 isDemo=true 但顶部环境条未标注「演示数据」')
      if (!dataEnv.includes('演示数据')) problems.push('治理栏「数据环境」未标注演示数据')
      if (!provenance.includes('不代表真实银行制度')) problems.push('缺少「不代表真实银行制度」声明')
      if (!provenance.includes('禁止对客引用')) problems.push('缺少「禁止对客引用」声明')
    }
    const body = await page.locator('body').innerText()
    if (isDemo && !body.includes('演示数据') && !body.includes('（DEMO）')) {
      problems.push('全页未见任何演示数据标注 ⇒ 演示数据被当作真实数据呈现（P0）')
    }

    writeFileSync(`${EVIDENCE_DIR}/e2-demo.json`, JSON.stringify({ isDemo, envTag, dataEnv, provenance, problems }, null, 2))
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-e2.png` })
    expect(problems, `E2 失败项：\n${problems.join('\n')}`).toEqual([])
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// G 组 · 窄屏 / 移动降级（390×844）
// ─────────────────────────────────────────────────────────────────────────────

test.describe('QA-G 窄屏降级 390x844', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('G1 窄屏下 A2/A3/B3 通过（无失败静态资源、无 console 错误、8 章导航完整）', async ({ page }) => {
    const problems: string[] = []
    await page.goto('/product-center/PROD-CM-003', { waitUntil: 'networkidle', timeout: 25000 })
    await expect(page.getByTestId('pc-env-banner')).toBeVisible({ timeout: 15000 })

    const nav = page.getByTestId('pc-section-link')
    const navCount = await nav.count()
    if (navCount !== 8) problems.push(`窄屏下章节导航项数=${navCount}（期望 8）`)
    const chapterCount = await page.getByTestId('pc-chapter').count()
    if (chapterCount !== 8) problems.push(`窄屏下章节数=${chapterCount}（期望 8）`)

    // 窄屏下核心字段不得消失（<1180px 变全宽侧板）
    for (const id of ['pc-catalog', 'pc-identity', 'pc-knowledge-as-of', 'pc-governance']) {
      const visible = await page.getByTestId(id).first().isVisible().catch(() => false)
      if (!visible) problems.push(`窄屏下 ${id} 不可见（字段消失）`)
    }
    await page.screenshot({ path: `${EVIDENCE_DIR}/shot-g1-mobile.png`, fullPage: true })

    const rec = current!.rec
    const origin = new URL(page.url()).origin
    const badStatic = rec.net.filter(
      (e) => e.url.startsWith(origin) && e.status >= 400 && (STATIC_TYPES.has(e.resourceType) || /\.(css|js|mjs)(\?|$)/.test(e.url)),
    )
    if (badStatic.length > 0) problems.push(`窄屏静态资源失败 ${badStatic.length} 条：${badStatic[0].status} ${badStatic[0].url}`)
    if (rec.pageErrors.length > 0) problems.push(`窄屏 pageerror：${rec.pageErrors[0]}`)
    if (rec.consoleErrors.length > 0) problems.push(`窄屏 console.error：${rec.consoleErrors[0]}`)

    expect(problems, `G1 失败项：\n${problems.join('\n')}`).toEqual([])
  })
})
