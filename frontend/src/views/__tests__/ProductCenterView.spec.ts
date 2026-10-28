import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ProductCenterView from '../ProductCenterView.vue'

/**
 * PC1 三栏骨架验收（REQ-PI-01 / CTR-PKC-API-001）：
 * - 环境条（DEMO 标识、基准日）、三栏结构、13 产品全目录（夹具）、产品首屏、八章导航；
 * - 诚实性：缺失字段「待核验」、无有效版本受控状态、章节未接入具名状态、助手禁用说明；
 * - 边界回归：不出现客户上下文与推荐性用语（PI-BR-002/003）。
 */
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: {} }),
  useRouter: () => ({ replace: vi.fn() })
}))

vi.mock('../../api/productCenter', () => ({
  fetchProductCenterFamilies: vi.fn(),
  fetchProductCenterProducts: vi.fn(),
  fetchProductCenterDetail: vi.fn(),
  extractErrorCode: (error: unknown) => (error as { code?: string } | null)?.code ?? null
}))

// 原始材料区与 PC-i1 章级承接区复用既有 CTR-PK-INT-001（下）与产品中心合同（上）
vi.mock('../../api/productKnowledge', () => ({
  fetchProductCardDetail: vi.fn()
}))

import {
  fetchProductCenterDetail,
  fetchProductCenterFamilies,
  fetchProductCenterProducts
} from '../../api/productCenter'
import { fetchProductCardDetail } from '../../api/productKnowledge'

/** 产品卡详情夹具（PC-i1：章级承接区与 C11 版本语义的数据源）。 */
const cardDetail = {
  productId: 'PROD-CM-003',
  name: '法人账户透支',
  family: 'CASH_MANAGEMENT',
  familyName: '现金管理',
  owner: '公司金融产品管理部',
  summary: '演示摘要',
  sections: [
    { title: '1. 产品概览与客户价值', content: '概览原文' },
    { title: '2. 适用客户与适用场景', content: '适用场景原文' },
    { title: '6. 前置、互斥、替代与配套产品', content: '前置产品：单位结算账户；配套产品：现金池。' },
    { title: '9. 风险提示与人工复核', content: '风险提示：不得承诺无限透支；需人工复核：额度审批。' },
    { title: '10. 销售边界', content: '销售边界原文' },
    { title: '11. 不可变版本语义', content: '版本一经发布不可改写；变更须发布新版本。' }
  ],
  sourceFile: 'cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md',
  rawMarkdown: '# 法人账户透支'
}

const families = [
  {
    familyId: 'CASH_MANAGEMENT',
    familyName: '现金管理',
    parentFamilyId: null,
    domainId: 'TRANSACTION_BANKING',
    domainName: '交易银行',
    displayOrder: 0,
    visibilityScope: 'ALL_RM',
    activeProductCount: 2,
    unclassifiedCount: 1
  },
  {
    familyId: 'FINANCING',
    familyName: '融资',
    parentFamilyId: null,
    domainId: 'CORPORATE_FINANCE',
    domainName: '公司金融',
    displayOrder: 1,
    visibilityScope: 'ALL_RM',
    activeProductCount: 1,
    unclassifiedCount: 0
  }
]

const products = [
  {
    productId: 'PROD-CM-003',
    productCode: 'DEMO-PROD-CM-003',
    productName: '法人账户透支',
    aliases: [],
    familyId: 'CASH_MANAGEMENT',
    familyName: '现金管理',
    lifecycleStatus: 'ACTIVE' as const,
    currentPublishedVersionId: null,
    hasPublishedVersion: false,
    environment: 'DEMO' as const,
    isDemo: true
  },
  {
    productId: 'PROD-FIN-001',
    productCode: 'DEMO-PROD-FIN-001',
    productName: '流动资金贷款',
    aliases: [],
    familyId: 'FINANCING',
    familyName: '融资',
    lifecycleStatus: 'ACTIVE' as const,
    currentPublishedVersionId: null,
    hasPublishedVersion: false,
    environment: 'DEMO' as const,
    isDemo: true
  }
]

const detail = {
  productId: 'PROD-CM-003',
  productCode: 'DEMO-PROD-CM-003',
  productName: '法人账户透支',
  aliases: [],
  familyId: 'CASH_MANAGEMENT',
  familyName: '现金管理',
  tags: ['资金集中'],
  publishStatus: 'DRAFT',
  version: {
    versionId: 'MIRROR-PROD-CM-003',
    versionLabel: '产品卡镜像（未发布）',
    versionStatus: 'DRAFT',
    knowledgeAsOf: null,
    effectiveFrom: null,
    effectiveTo: null,
    publishedAt: null,
    publishedBy: null,
    reviewedBy: [],
    reviewRecordId: null,
    nextReviewAt: null,
    changeSummary: '产品卡原始材料镜像；尚未形成受控知识版本',
    changeReason: null,
    evidenceSnapshotId: null,
    environment: 'DEMO' as const,
    isDemo: true
  },
  summary: {
    oneSentenceDefinition: '用于满足企业日常经营周转的短期资金需求。',
    boundaryStatement: '额度、期限、利率以批复和协议为准。',
    productPurpose: null,
    usageMode: null,
    interestSummary: null,
    eligibleEntitySummary: null,
    solves: null,
    isNot: null,
    nearestDifference: null
  },
  terms: [],
  boundaries: [],
  prerequisites: [],
  processSteps: [],
  materialGroups: [],
  pricingItems: [],
  agreementClauses: [],
  salesBoundaries: [
    {
      boundaryId: 'SLB-1',
      boundaryKind: 'PROHIBITED_PROMISE',
      text: '不得承诺"无限透支"等误导性表述。',
      riskCategory: 'PURPOSE',
      mandatoryDisplay: true
    }
  ],
  faqs: [],
  comparison: null,
  evidenceRefs: [],
  fixedBoundaryStatements: [
    '产品适用边界不等于具体客户的适配或推荐结论。',
    '额度、期限、利率、费用、担保方式与办理时效以最终批复和协议约定为准，本页不作任何承诺。'
  ],
  assistant: { enabled: false, quickQuestions: [] }
}

const mockedFamilies = vi.mocked(fetchProductCenterFamilies)
const mockedProducts = vi.mocked(fetchProductCenterProducts)
const mockedDetail = vi.mocked(fetchProductCenterDetail)
const mockedCardDetail = vi.mocked(fetchProductCardDetail)

async function mountView() {
  const wrapper = mount(ProductCenterView)
  await flushPromises()
  return wrapper
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedFamilies.mockResolvedValue(families as never)
  mockedProducts.mockResolvedValue(products as never)
  mockedDetail.mockResolvedValue(detail as never)
  mockedCardDetail.mockResolvedValue(cardDetail as never)
})

describe('ProductCenterView PC1 三栏骨架', () => {
  it('渲染环境条（DEMO 标识 + 基准日待维护）与三栏结构', async () => {
    const wrapper = await mountView()

    expect(wrapper.find('[data-testid="product-center-shell"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pc-col-left"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pc-col-main"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pc-col-right"]').exists()).toBe(true)

    const banner = wrapper.find('[data-testid="pc-env-banner"]')
    expect(banner.exists()).toBe(true)
    expect(banner.text()).toContain('企业金融产品中心')
    expect(wrapper.find('[data-testid="pc-env-tag"]').text()).toContain('DEMO')
    expect(wrapper.find('[data-testid="pc-env-tag"]').text()).toContain('演示数据')
    // 基准日缺失必须显示「待维护」，不得用系统日期冒充
    expect(wrapper.find('[data-testid="pc-knowledge-as-of"]').text()).toBe('知识基准日：基准日待维护')
    // 身份服务未接入必须显式说明（不以假身份填充）
    expect(wrapper.find('[data-testid="pc-identity"]').text()).toContain('身份服务未接入')
  })

  it('左侧目录按族渲染产品，并标记无有效版本与待维护计数', async () => {
    const wrapper = await mountView()

    expect(wrapper.findAll('[data-testid="pc-catalog-family"]')).toHaveLength(2)
    expect(wrapper.findAll('[data-testid="pc-catalog-product"]')).toHaveLength(2)
    expect(wrapper.find('[data-testid="pc-catalog-total"]').text()).toContain('2 个产品')
    expect(wrapper.find('[data-testid="pc-catalog"]').text()).toContain('现金管理')
    expect(wrapper.find('[data-testid="pc-catalog"]').text()).toContain('法人账户透支')
    expect(wrapper.find('[data-testid="pc-catalog"]').text()).toContain('无有效版本')
    expect(wrapper.find('[data-testid="pc-catalog"]').text()).toContain('1 个产品待维护内容')
  })

  it('默认选中目录首项并渲染首屏、八章导航与知识治理栏', async () => {
    const wrapper = await mountView()

    // 首屏（含「待核验」缺口，不用空白冒充）
    const hero = wrapper.find('[data-testid="pc-hero"]')
    expect(hero.exists()).toBe(true)
    expect(hero.text()).toContain('法人账户透支')
    expect(wrapper.find('[data-testid="pc-hero-product-id"]').text()).toBe('PROD-CM-003')
    expect(hero.text()).toContain('待核验')
    expect(wrapper.find('[data-testid="pc-fixed-boundaries"]').text())
      .toContain('不等于具体客户的适配或推荐结论')

    // 八章导航（顺序受控）
    const navLinks = wrapper.findAll('[data-testid="pc-section-link"]')
    expect(navLinks).toHaveLength(8)
    expect(navLinks[0].text()).toBe('60 秒读懂')
    expect(navLinks[7].text()).toBe('常见问题')

    // 八章正文：**逐章二选一**（有契约数据 ⇒ 正文非空；无数据 ⇒ 具名未接入）
    // 不使用常量计数代替判据：常量会把「有数据却渲染空白」的空壳章节锁成"通过"（QA D-3）。
    // 本夹具的契约事实：仅 summary 有值；terms/boundaries/prerequisites/processSteps/
    // materialGroups/pricingItems/comparison/faqs 均为空 ⇒ 除 OVERVIEW 外 7 章应为具名未接入。
    expect(wrapper.findAll('[data-testid="pc-chapter"]')).toHaveLength(8)
    const fixtureHasPayload: Record<string, boolean> = {
      // 由**夹具事实**推导（独立 QA-5：原为手写常量表，夹具变更时会误报）
      OVERVIEW: detail.summary !== null,
      TERMS: detail.terms.length > 0,
      FIT: detail.boundaries.length > 0 || detail.prerequisites.length > 0,
      PROCESS: detail.processSteps.length > 0,
      MATERIALS: detail.materialGroups.length > 0,
      PRICING: detail.pricingItems.length > 0,
      COMPARE: detail.comparison !== null,
      FAQ: detail.faqs.length > 0
    }
    for (const [key, hasPayload] of Object.entries(fixtureHasPayload)) {
      const chapter = wrapper.find(`[data-testid="pc-chapter"][data-section-key="${key}"]`)
      expect(chapter.exists(), `章节 ${key} 应存在`).toBe(true)
      const body = chapter.find('[data-testid="pc-chapter-body"]')
      const pending = chapter.find('[data-testid="pc-chapter-pending"]')
      if (hasPayload) {
        expect(body.exists(), `${key}：有契约数据必须渲染正文`).toBe(true)
        expect(pending.exists(), `${key}：有数据时不得显示「待接入」`).toBe(false)
        expect(body.text().replace(/\s/g, '').length, `${key}：正文不得为空`).toBeGreaterThan(0)
      } else {
        expect(pending.exists(), `${key}：无契约数据必须具名标注未接入`).toBe(true)
        expect(body.exists(), `${key}：无数据时不得渲染正文`).toBe(false)
      }
    }
    // 选择器须限定到章节正文元素：导航链接同样带 data-section-key（避免选中导航项）
    expect(wrapper.find('[data-testid="pc-chapter"][data-section-key="OVERVIEW"]').text())
      .toContain('用于满足企业日常经营周转')

    // 右侧治理栏：版本 DRAFT + 无审核记录 + 助手未启用 + 演示数据来源声明（DP-04）
    expect(wrapper.find('[data-testid="pc-governance"]').text()).toContain('DRAFT')
    expect(wrapper.find('[data-testid="pc-governance"]').text()).toContain('无审核记录')
    expect(wrapper.find('[data-testid="pc-data-environment"]').text()).toBe('DEMO（演示数据）')
    expect(wrapper.find('[data-testid="pc-data-provenance"]').text()).toContain('不代表真实银行制度')
    expect(wrapper.find('[data-testid="pc-data-provenance"]').text()).toContain('禁止对客引用')
    expect(wrapper.find('[data-testid="pc-assistant-disabled"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid="pc-gov-pending"]')).toHaveLength(3)
  })

  it('有契约数据的章节必须渲染正文（W-1 回归：不得留空占位）', async () => {
    // 与本文件既有夹具相反：此处 5 章**有契约数据** ⇒ 必须渲染正文。
    // 这正是 QA D-1（5 章空壳）的机械反面；修 W-1 时它就是防回归的锁。
    const populated = {
      ...detail,
      terms: [
        {
          termId: 'TERM-1',
          termKey: 'TERM-DEMO',
          businessDefinition: '演示术语业务定义',
          explanationForRm: '演示 RM 解释',
          certaintyType: 'VERIFIED',
          displayOrder: 1,
          evidenceRefs: [],
          conflictId: null
        }
      ],
      boundaries: [
        {
          boundaryId: 'BND-1',
          boundaryType: 'TYPICAL_USE',
          scenarioName: '典型场景A',
          scenarioDescription: '演示场景描述',
          alternativeDirection: null,
          evidenceRefs: []
        }
      ],
      prerequisites: [
        {
          prerequisiteId: 'PRE-1',
          prerequisiteType: 'ENTITY',
          requirementText: '演示前置条件',
          conditional: false,
          evidenceRefs: []
        }
      ],
      processSteps: [
        {
          stepId: 'STEP-1',
          sequence: 1,
          stepName: '受理',
          summary: '演示步骤摘要',
          actors: ['客户经理'],
          inputs: ['申请书'],
          outputs: ['受理回执'],
          exceptions: [],
          humanDecisionRequired: true,
          slaReference: 'T+1',
          evidenceRefs: []
        }
      ],
      materialGroups: [
        {
          groupType: 'BASIC_REQUIRED',
          items: [
            {
              materialId: 'MAT-1',
              materialName: '营业执照',
              requirementLevel: 'MUST',
              conditionExpression: null,
              purpose: '主体资格核验',
              validityRule: null,
              templateFileRef: null,
              sampleFileRef: null,
              scope: {},
              evidenceRefs: []
            }
          ]
        }
      ],
      comparison: {
        comparisonSetId: 'CMP-1',
        comparisonAsOf: '2026-09-01',
        dimensions: [{ dimensionId: 'RELATION', dimensionName: '与本产品关系' }],
        rows: [{ productId: 'PROD-SET-001', versionId: '', values: { RELATION: '前置产品' } }],
        reviewState: 'DRAFT'
      }
    }
    mockedDetail.mockResolvedValue(populated as never)

    const wrapper = await mountView()

    for (const key of ['TERMS', 'FIT', 'PROCESS', 'MATERIALS', 'COMPARE']) {
      const chapter = wrapper.find(`[data-testid="pc-chapter"][data-section-key="${key}"]`)
      expect(chapter.find('[data-testid="pc-chapter-body"]').exists(), `${key} 必须渲染正文`).toBe(true)
      expect(chapter.find('[data-testid="pc-chapter-pending"]').exists(), `${key} 有数据不得显示「待接入」`).toBe(false)
    }

    // 内容抽查：渲染的是契约数据，不是示意文案
    const chapterText = (key: string) =>
      wrapper.find(`[data-testid="pc-chapter"][data-section-key="${key}"]`).text()
    expect(chapterText('TERMS')).toContain('演示术语业务定义')
    expect(chapterText('TERMS')).toContain('VERIFIED')
    expect(chapterText('FIT')).toContain('演示场景描述')
    expect(chapterText('FIT')).toContain('演示前置条件')
    expect(chapterText('PROCESS')).toContain('需人工决策')
    expect(chapterText('PROCESS')).toContain('客户经理')
    expect(chapterText('MATERIALS')).toContain('营业执照')
    expect(chapterText('COMPARE')).toContain('前置产品')
    expect(chapterText('COMPARE')).toContain('DRAFT')

    // 修 W-1 不得把「真未接入」的章节改成空白：PRICING / FAQ 仍须具名未接入
    for (const key of ['PRICING', 'FAQ']) {
      const chapter = wrapper.find(`[data-testid="pc-chapter"][data-section-key="${key}"]`)
      expect(chapter.find('[data-testid="pc-chapter-pending"]').exists(), `${key} 应保持具名未接入`).toBe(true)
      expect(chapter.find('[data-testid="pc-chapter-body"]').exists()).toBe(false)
    }
  })

  it('PC-i1 章级承接：C6/C9 独立区块 + C11 版本区承载（原文 + 相对来源 + 有效状态）', async () => {
    const wrapper = await mountView()

    for (const [id, keyword] of [['c6', '前置产品'], ['c9', '人工复核']] as const) {
      const block = wrapper.find(`[data-testid="pc-inherited-${id}"]`)
      expect(block.exists(), `${id} 必须有独立可见区块`).toBe(true)
      expect(block.find(`[data-testid="pc-inherited-${id}-content"]`).text()).toContain(keyword)
      const meta = block.find(`[data-testid="pc-inherited-${id}-meta"]`).text()
      expect(meta).toContain(cardDetail.sourceFile)
      expect(meta).toContain('有效状态')
      expect(meta).toContain('DRAFT')
    }
    // 相对来源：页面不得出现本机绝对路径
    expect(wrapper.text()).not.toContain('/home/')

    // C11：版本区须承载该节语义（不得仅以版本徽章敷衍）
    const immutable = wrapper.find('[data-testid="pc-immutable-version"]')
    expect(immutable.exists()).toBe(true)
    expect(immutable.find('[data-testid="pc-immutable-statement"]').text()).toContain('不可变')
    expect(immutable.find('[data-testid="pc-immutable-content"]').text()).toContain('不可改写')
    expect(immutable.find('[data-testid="pc-immutable-source"]').text()).toContain(cardDetail.sourceFile)
    expect(immutable.find('[data-testid="pc-immutable-facts"]').text()).toContain('DRAFT')

    // W1-d/W1-e：C2/C3/C8/C10/C12 具名落位（含承接位置），C10 呈现**产品级**销售边界
    for (const key of ['c2', 'c3', 'c8', 'c10', 'c12']) {
      const block = wrapper.find(`[data-testid="pc-inherited-${key}"]`)
      expect(block.exists(), `${key} 必须具名落位`).toBe(true)
      expect(block.find(`[data-testid="pc-inherited-${key}-meta"]`).text()).toContain('承接位置：')
    }
    const c10Contract = wrapper.find('[data-testid="pc-inherited-c10-contract"]')
    expect(c10Contract.exists()).toBe(true)
    expect(c10Contract.text()).toContain('不得承诺"无限透支"等误导性表述。')
    // C12 在本卡（11 节，无 EvidenceRef）如实缺失
    expect(wrapper.find('[data-testid="pc-inherited-c12-absent"]').exists()).toBe(true)
  })

  it('PC-i1 章级承接：来源不可得时具名标注（不伪造、不留空占位）', async () => {
    mockedCardDetail.mockRejectedValueOnce(new Error('card-detail-unavailable'))
    const wrapper = await mountView()

    expect(wrapper.find('[data-testid="pc-inherited-c6-absent"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pc-inherited-c6-meta"]').text()).toContain('来源标识不可得')
    expect(wrapper.find('[data-testid="pc-immutable-absent"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pc-immutable-content"]').exists()).toBe(false)
  })

  it('受控失败：源不可读显示目录错误态；无有效版本显示中栏受控状态', async () => {
    mockedFamilies.mockRejectedValueOnce({ code: 'SOURCES_UNAVAILABLE' })
    mockedProducts.mockRejectedValueOnce({ code: 'SOURCES_UNAVAILABLE' })
    const wrapper = await mountView()

    const catalogError = wrapper.find('[data-testid="pc-catalog-error"]')
    expect(catalogError.exists()).toBe(true)
    expect(catalogError.text()).toContain('fail-closed')
    expect(catalogError.text()).toContain('SOURCES_UNAVAILABLE')

    // 目录失败时不得静默展示空目录
    expect(wrapper.findAll('[data-testid="pc-catalog-product"]')).toHaveLength(0)

    mockedDetail.mockRejectedValueOnce({ code: 'NO_PUBLISHED_VERSION' })
    const second = await mountView()
    expect(second.find('[data-testid="pc-no-published-version"]').exists()).toBe(true)
  })

  it('边界回归：不出现客户上下文与推荐性用语', async () => {
    const wrapper = await mountView()
    const text = wrapper.text()

    // PI-BR-002：不读取客户画像 / 账户 / 交易 / 授信 / 商机
    expect(text).not.toContain('客户画像')
    expect(text).not.toContain('商机')
    // PI-BR-003：不输出适配分 / 推荐 / 排名 / 赢单概率 / 下一最佳行动
    expect(text).not.toContain('适配分')
    expect(text).not.toContain('立即推荐')
    expect(text).not.toContain('加入客户方案')
    expect(text).not.toContain('测算适配度')
    expect(text).not.toContain('下一最佳行动')
    expect(text).not.toContain('胜率')
    // PI-FR-033：不承诺额度 / 价格 / 时效
    expect(text).toContain('不作任何承诺')
  })
})
