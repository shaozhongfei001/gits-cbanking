import { mkdirSync } from 'node:fs'
import { expect, test } from '@playwright/test'

/**
 * PC1 浏览器验收（REQ-PI-01 / Loop PC1）：
 * DEMO 环境条 + 13 产品全目录 + 产品首屏 + 八章导航 + 三档宽度截图。
 *
 * 依赖真实链路：前端 5173 → vite 代理 → 后端 8088（CTR-PKC-API-001）。
 * 后端未启动时本用例应失败（不得以 mock 数据代替验收，需求 §十三）。
 */
const SHOT_DIR = 'test-results/pc1'
const WIDTHS = [1680, 1440, 1280] as const

test.describe('PC1 产品中心三栏骨架', () => {
  test.beforeAll(() => {
    mkdirSync(SHOT_DIR, { recursive: true })
  })

  test('DEMO 标识 + 13 产品全目录 + 首屏 + 八章导航（真实后端）', async ({ page }) => {
    await page.setViewportSize({ width: 1680, height: 1000 })
    await page.goto('/product-center')

    // ① 顶部环境条：DEMO 标识常驻 + 基准日待维护 + 搜索 + 身份缺口说明
    await expect(page.getByTestId('pc-env-banner')).toBeVisible()
    await expect(page.getByTestId('pc-env-tag')).toContainText('DEMO')
    await expect(page.getByTestId('pc-env-tag')).toContainText('演示数据')
    await expect(page.getByTestId('pc-knowledge-as-of')).toHaveText('知识基准日：基准日待维护')
    await expect(page.getByTestId('pc-search-input')).toBeVisible()
    await expect(page.getByTestId('pc-identity')).toContainText('身份服务未接入')

    // ② 左侧目录：受控分类法 6 族 / 13 产品（真实 taxonomy，非演示子集）
    await expect(page.getByTestId('pc-catalog-family')).toHaveCount(6)
    await expect(page.getByTestId('pc-catalog-product')).toHaveCount(13)
    await expect(page.getByTestId('pc-catalog')).toContainText('现金管理')
    await expect(page.getByTestId('pc-catalog')).toContainText('跨境金融')
    await expect(page.getByTestId('pc-catalog')).toContainText('无有效版本')

    // ③ 选择参考产品（法人账户透支）→ 首屏
    await page.getByTestId('pc-catalog-product').filter({ hasText: '法人账户透支' }).getByRole('button').click()
    await expect(page.getByTestId('pc-hero')).toContainText('法人账户透支')
    await expect(page.getByTestId('pc-hero-product-id')).toHaveText('PROD-CM-003')
    await expect(page.getByTestId('pc-publish-status')).toContainText('未发布受控版本')
    await expect(page.getByTestId('pc-hero')).toContainText('待核验')
    await expect(page.getByTestId('pc-fixed-boundaries')).toContainText('不等于具体客户的适配或推荐结论')
    await expect(page).toHaveURL(/\/product-center\/PROD-CM-003/)

    // ④ 八章导航（顺序受控）+ 章节正文：**逐章二选一**（判据取自接口事实，禁止用常量计数）
    //    有契约数据 ⇒ 该章必须渲染正文且不得显示「待接入」；无数据 ⇒ 必须具名「待接入 <批次>」。
    //    理由（QA D-3）：常量计数会把「有数据却渲染空白」的空壳章节锁成"通过"。
    const nav = page.getByTestId('pc-section-link')
    await expect(nav).toHaveCount(8)
    await expect(nav.nth(0)).toHaveText('60 秒读懂')
    await expect(nav.nth(7)).toHaveText('常见问题')
    await expect(page.getByTestId('pc-chapter')).toHaveCount(8)

    const detailResp = await page.request.get('/api/v1/product-center/products/PROD-CM-003')
    expect(detailResp.ok(), `产品详情接口应可用（本组判据来源）：HTTP ${detailResp.status()}`).toBe(true)
    const detail = (await detailResp.json()) as Record<string, unknown>
    const chapterPayload: Record<string, string[]> = {
      OVERVIEW: ['summary'],
      TERMS: ['terms'],
      FIT: ['boundaries', 'prerequisites'],
      PROCESS: ['processSteps'],
      MATERIALS: ['materialGroups'],
      PRICING: ['pricingItems'],
      COMPARE: ['comparison'],
      FAQ: ['faqs']
    }
    for (const [key, fields] of Object.entries(chapterPayload)) {
      const hasPayload = fields.some((field) => {
        const raw = detail[field]
        return Array.isArray(raw) ? raw.length > 0 : raw !== null && raw !== undefined
      })
      const chapter = page.locator(`[data-testid="pc-chapter"][data-section-key="${key}"]`)
      if (hasPayload) {
        await expect(chapter.getByTestId('pc-chapter-body'), `${key}：有契约数据必须渲染正文`).toBeVisible()
        await expect(chapter.getByTestId('pc-chapter-pending'), `${key}：有数据时不得显示「待接入」`).toHaveCount(0)
      } else {
        await expect(chapter.getByTestId('pc-chapter-pending'), `${key}：无数据时必须具名标注未接入`).toHaveCount(1)
        await expect(chapter.getByTestId('pc-chapter-body'), `${key}：无数据时不得渲染正文`).toHaveCount(0)
      }
    }

    // 内容抽查：渲染的是**契约数据**（terms[0].businessDefinition），不是示意文案。
    // 先断言判据前提（接口确有该值），再断言页面含该值 —— 前提不成立即失败，不得静默跳过。
    const terms = (detail.terms ?? []) as Array<{ businessDefinition?: string | null }>
    expect(terms.length, 'PROD-CM-003 应有 terms（本判据前提）').toBeGreaterThan(0)
    expect(terms[0]?.businessDefinition, 'terms[0].businessDefinition 应非空（本判据前提）').toBeTruthy()
    await expect(page.locator('[data-testid="pc-chapter"][data-section-key="TERMS"]'))
      .toContainText(String(terms[0].businessDefinition))

    // ④b PC-i1 章级承接（R2 映射：C6/C9 记为「无任何对应区块」⇒ 必须有**独立可见区块**）
    //     判据：呈现该章**原文** + **相对来源标识** + **有效状态**；不得留空占位。
    for (const [id, no, keyword] of [['c6', 6, '前置产品'], ['c9', 9, '人工复核']] as const) {
      const block = page.getByTestId(`pc-inherited-${id}`)
      await expect(block, `${id} 必须有独立可见区块`).toBeVisible()
      await expect(block.getByTestId(`pc-inherited-${id}-content`)).toContainText(keyword)
      const meta = block.getByTestId(`pc-inherited-${id}-meta`)
      await expect(meta).toContainText(`第 ${no} 节`)
      await expect(meta).toContainText('来源：')
      await expect(meta).toContainText('有效状态：')
      // 相对来源：不得以绝对路径充当来源标识
      expect(await meta.innerText()).not.toMatch(/来源：\s*\//)
    }

    // ④c C11：版本区须承载「不可变版本语义」（不得仅以版本徽章敷衍）
    const immutable = page.getByTestId('pc-immutable-version')
    await expect(immutable).toBeVisible()
    await expect(immutable.getByTestId('pc-immutable-statement')).toContainText('不可变')
    await expect(immutable.getByTestId('pc-immutable-facts')).toContainText('生效日')
    await expect(immutable.getByTestId('pc-immutable-content')).toContainText('不可变')
    // 来源标识用**实际**节标题（各卡节号不一致，不得写死节号）
    await expect(immutable.getByTestId('pc-immutable-source')).toContainText('不可变版本语义')

    // ④d W1-d/W1-e：C2/C3/C8/C10/C12 具名落位 + 承接位置（指名引用）
    for (const key of ['c2', 'c3', 'c8', 'c10', 'c12']) {
      const block = page.getByTestId(`pc-inherited-${key}`)
      await expect(block, `${key} 必须具名落位`).toBeVisible()
      await expect(block.getByTestId(`pc-inherited-${key}-meta`)).toContainText('承接位置：')
    }
    // C10：必须呈现**产品级**销售边界（合同字段），不得只留通用声明
    await expect(page.getByTestId('pc-inherited-c10-contract')).toBeVisible()
    await expect(page.getByTestId('pc-inherited-c10-contract')).toContainText('salesBoundaries')

    // ④e QA-B1 / QA-N1 反向断言：C12 在本卡确实缺该节 ⇒ 缺失文案不得用 R2 登记章号冒充节号
    const cmCardResp = await page.request.get('/api/v1/product-knowledge/cards/PROD-CM-003')
    expect(cmCardResp.ok(), `卡详情接口应可用（本判据前提）：HTTP ${cmCardResp.status()}`).toBe(true)
    const cmSections =
      ((await cmCardResp.json()) as { sections?: Array<{ title: string }> }).sections ?? []
    expect(
      cmSections.some((s) => s.title.includes('EvidenceRef')),
      'PROD-CM-003 应不含 EvidenceRef 节（本判据前提）'
    ).toBe(false)
    const c12AbsentText = await page.getByTestId('pc-inherited-c12-absent').innerText()
    expect(c12AbsentText).toContain('R2 章号 C12')
    expect(c12AbsentText).not.toMatch(/未包含第\s*\d+\s*节/)
    await expect(page.getByTestId('pc-inherited-c12-meta')).toContainText('本卡未含该节')

    // ⑤ 右侧知识治理栏：版本 DRAFT + 无审核记录 + 助手未启用
    await expect(page.getByTestId('pc-governance')).toContainText('DRAFT')
    await expect(page.getByTestId('pc-governance')).toContainText('无审核记录')
    await expect(page.getByTestId('pc-assistant-disabled')).toBeVisible()

    // ⑥ 原始材料区（PC1.5）：真实材料 + 常驻未受控警示 + 不泄露本机绝对路径
    await expect(page.getByTestId('pc-source-material')).toBeVisible()
    await expect(page.getByTestId('pc-source-warning')).toContainText('尚未形成受控知识版本')
    await expect(page.getByTestId('pc-source-warning')).toContainText('不得对客引用')
    const sourceFile = await page.getByTestId('pc-source-file').innerText()
    expect(sourceFile).toContain('product-cards/PROD-CM-003.md')
    expect(sourceFile.startsWith('/')).toBe(false)

    // ⑥b 演示数据必须显式声明（DP-04）：不得让读者误以为是真实银行规则
    await expect(page.getByTestId('pc-source-warning')).toContainText('模拟（DEMO）数据，非真实银行规则')
    await expect(page.getByTestId('pc-data-environment')).toContainText('DEMO（演示数据）')
    await expect(page.getByTestId('pc-data-provenance')).toContainText('不代表真实银行制度')
    await expect(page.getByTestId('pc-data-provenance')).toContainText('禁止对客引用')

    // ⑦ 边界回归：不得出现推荐性用语，且不得泄露本机路径
    const text = await page.locator('body').innerText()
    for (const forbidden of ['适配分', '立即推荐', '加入客户方案', '测算适配度', '下一最佳行动', '胜率']) {
      expect(text).not.toContain(forbidden)
    }
    expect(text).not.toContain('/home/szf')

    // ⑧ 三档宽度截图（1680 / 1440 / 1280）
    for (const width of WIDTHS) {
      await page.setViewportSize({ width, height: 1000 })
      await page.waitForTimeout(250)
      await page.screenshot({ path: `${SHOT_DIR}/product-center-${width}.png`, fullPage: true })
    }
  })

  test('章级承接：FIN 卡节号错位不得错配（不可变版本语义 ↔ §12，EvidenceRef ↔ §11）', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto('/product-center/PROD-FIN-003')

    const resp = await page.request.get('/api/v1/product-knowledge/cards/PROD-FIN-003')
    expect(resp.ok(), `卡详情接口应可用（本判据前提）：HTTP ${resp.status()}`).toBe(true)
    const card = (await resp.json()) as { sections?: Array<{ title: string; content: string }> }
    const sections = card.sections ?? []
    const immutable = sections.find((s) => s.title.includes('不可变版本语义'))
    const evidenceRef = sections.find((s) => s.title.includes('EvidenceRef'))
    expect(immutable, 'PROD-FIN-003 应含「不可变版本语义」节（判据前提）').toBeTruthy()
    expect(evidenceRef, 'PROD-FIN-003 应含「EvidenceRef」节（判据前提）').toBeTruthy()
    expect(immutable!.title.startsWith('12.'), '本卡该节应为 §12（编号错位的事实前提）').toBe(true)
    expect(evidenceRef!.title.startsWith('11.'), '本卡 EvidenceRef 应为 §11').toBe(true)

    const strip = (text: string) => text.replace(/\s+/g, '')
    const head = (text: string) => strip(text).slice(0, 16)

    // C11：版本区必须绑到「不可变版本语义」（不得被 §11 EvidenceRef 抢走）
    await expect(page.getByTestId('pc-immutable-source')).toContainText('12.')
    expect(strip(await page.getByTestId('pc-immutable-content').innerText())).toContain(head(immutable!.content))

    // C12：承接区必须绑到 §11 EvidenceRef，并展示**实际**节号
    expect(strip(await page.getByTestId('pc-inherited-c12-content').innerText())).toContain(head(evidenceRef!.content))
    await expect(page.getByTestId('pc-inherited-c12-meta')).toContainText('第 11 节')

    // QA-B1 / QA-N1：标题只以「章节标题 + 卡内实际节号」呈现，不得写「12.」与 meta 冲突
    const c12Head = page.getByTestId('pc-inherited-c12').locator('.pc-inherited-block-title')
    await expect(c12Head).toContainText('EvidenceRef')
    await expect(c12Head).toContainText('卡内第 11 节')
    expect(await c12Head.innerText()).not.toMatch(/(^|\s)12\./)
  })

  test('故障路径：产品卡接口不可达 ⇒ 缺失归因如实（不判定该卡是否含该节，QA-B2）', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    // 只做**失败注入**（中断请求），不注入任何假数据
    let aborted = 0
    await page.route('**/api/v1/product-knowledge/cards/**', (route) => {
      aborted += 1
      return route.abort('failed')
    })
    await page.goto('/product-center/PROD-FIN-003')
    await expect(page.getByTestId('pc-inherited-chapters')).toBeVisible()
    expect(aborted, '应确实中断了卡接口请求（本判据前提）').toBeGreaterThan(0)

    // 承接区：区块仍在，但 meta 如实「来源标识不可得」且**不判定**节号
    const c12Meta = page.getByTestId('pc-inherited-c12-meta')
    await expect(c12Meta).toContainText('来源标识不可得')
    await expect(c12Meta).toContainText('节号不可判')
    const c12Absent = page.getByTestId('pc-inherited-c12-absent')
    await expect(c12Absent).toContainText('无法判定')
    expect(await c12Absent.innerText()).not.toMatch(/未包含第\s*\d+\s*节/)

    // 版本区同口径（修复前写死「第 11 节」）
    const immAbsent = page.getByTestId('pc-immutable-absent')
    await expect(immAbsent).toContainText('无法判定')
    expect(await immAbsent.innerText()).not.toMatch(/未包含第\s*\d+\s*节/)

    // 未读到卡 ⇒ 不得渲染任何原文（不得伪造内容）；无关接口不受连带影响
    await expect(page.getByTestId('pc-inherited-c12-content')).toHaveCount(0)
    await expect(page.getByTestId('pc-immutable-content')).toHaveCount(0)
    await expect(page.getByTestId('pc-inherited-c10-contract')).toBeVisible()
  })

  test('异常状态：无有效版本产品显示受控状态（不展示草稿）', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    // 目录中所有产品当前均无已发布受控版本 ⇒ 直接断言目录标记与详情受控状态一致性
    await page.goto('/product-center')
    await expect(page.getByTestId('pc-catalog')).toContainText('无有效版本')
    const heroText = await page.getByTestId('pc-hero').innerText()
    expect(heroText).toContain('未发布受控版本')
  })
})
