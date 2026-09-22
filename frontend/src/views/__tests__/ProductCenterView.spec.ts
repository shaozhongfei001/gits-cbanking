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

// 原始材料区复用既有 CTR-PK-INT-001；本用例只关注骨架，材料接口给受控空态
vi.mock('../../api/productKnowledge', () => ({
  fetchProductCardDetail: vi.fn().mockRejectedValue(new Error('not-mocked'))
}))

import {
  fetchProductCenterDetail,
  fetchProductCenterFamilies,
  fetchProductCenterProducts
} from '../../api/productCenter'

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
  salesBoundaries: [],
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

    // 八章正文：OVERVIEW 渲染摘要，其余为具名未接入状态
    expect(wrapper.findAll('[data-testid="pc-chapter"]')).toHaveLength(8)
    expect(wrapper.findAll('[data-testid="pc-chapter-pending"]')).toHaveLength(7)
    // 选择器须限定到章节正文元素：导航链接同样带 data-section-key（避免选中导航项）
    expect(wrapper.find('[data-testid="pc-chapter"][data-section-key="OVERVIEW"]').text())
      .toContain('用于满足企业日常经营周转')

    // 右侧治理栏：版本 DRAFT + 无审核记录 + 助手未启用
    expect(wrapper.find('[data-testid="pc-governance"]').text()).toContain('DRAFT')
    expect(wrapper.find('[data-testid="pc-governance"]').text()).toContain('无审核记录')
    expect(wrapper.find('[data-testid="pc-assistant-disabled"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid="pc-gov-pending"]')).toHaveLength(3)
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
