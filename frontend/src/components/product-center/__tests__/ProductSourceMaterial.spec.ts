import { describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import ProductSourceMaterial from '../ProductSourceMaterial.vue'

/**
 * 原始材料区（PC1.5）验收：
 * 1) 必须常驻「未受控知识版本 / 不得对客引用」警示；
 * 2) 只呈现相对源文件标识，**不得**出现本机绝对路径（P38 现状缺陷 F-P38-01 回归防线）；
 * 3) 无材料时给受控空态，不报错、不静默。
 */
vi.mock('../../../api/productKnowledge', () => ({
  fetchProductCardDetail: vi.fn()
}))

import { fetchProductCardDetail } from '../../../api/productKnowledge'

const mockedDetail = vi.mocked(fetchProductCardDetail)

const cardDetail = {
  productId: 'PROD-CM-003',
  name: '法人账户透支',
  family: 'CASH_MANAGEMENT',
  familyName: '现金管理',
  owner: '交易银行部',
  summary: '用于满足企业日常经营周转的短期资金需求。',
  sections: [
    { title: '产品概览与客户价值', content: '法人账户透支是银行与对公客户签订协议…' },
    { title: '适用客户与适用场景', content: '适用于符合准入条件的企业法人。' }
  ],
  sourceFile: 'cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md',
  rawMarkdown: '# 法人账户透支'
}

describe('ProductSourceMaterial', () => {
  it('常驻未受控警示 + 相对源文件 + 章节正文', async () => {
    mockedDetail.mockResolvedValueOnce(cardDetail as never)
    const wrapper = mount(ProductSourceMaterial, { props: { productId: 'PROD-CM-003' } })
    await flushPromises()

    const warning = wrapper.find('[data-testid="pc-source-warning"]')
    expect(warning.exists()).toBe(true)
    expect(warning.text()).toContain('尚未形成受控知识版本')
    expect(warning.text()).toContain('不得对客引用')
    // 演示数据必须显式声明（DP-04）：不得让读者误以为是真实银行规则
    expect(warning.text()).toContain('模拟（DEMO）数据，非真实银行规则')
    expect(warning.text()).toContain('不得进入生产正式版本')

    expect(wrapper.find('[data-testid="pc-source-file"]').text())
      .toBe('cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md')
    expect(wrapper.findAll('[data-testid="pc-source-section"]')).toHaveLength(2)
    // 首节默认展开，正文可直接阅读（避免"打开页面还要再点一次"）
    expect(wrapper.text()).toContain('法人账户透支是银行与对公客户签订协议')
    expect(wrapper.text()).toContain('适用客户与适用场景')
  })

  it('不得泄露本机绝对路径（回归防线）', async () => {
    mockedDetail.mockResolvedValueOnce(cardDetail as never)
    const wrapper = mount(ProductSourceMaterial, { props: { productId: 'PROD-CM-003' } })
    await flushPromises()

    const text = wrapper.text()
    expect(text).not.toContain('/home/')
    expect(text).not.toContain('/Users/')
    expect(text).not.toContain('Leibniz-KERT')
  })

  it('无材料时给出受控空态（不静默、不报错）', async () => {
    mockedDetail.mockRejectedValueOnce(new Error('404'))
    const wrapper = mount(ProductSourceMaterial, { props: { productId: 'PROD-CM-003' } })
    await flushPromises()

    expect(wrapper.find('[data-testid="pc-source-error"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid="pc-source-section"]')).toHaveLength(0)
  })
})
