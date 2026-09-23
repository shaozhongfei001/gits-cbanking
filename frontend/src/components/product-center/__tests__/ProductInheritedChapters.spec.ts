import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductInheritedChapters from '../ProductInheritedChapters.vue'

/**
 * PC-i1 · W1-a/W1-b/W1-d/W1-e 验收：R2 映射中「无对应区块（C6/C9）/ 仅部分承接（C2/C3/C10）/
 * 尚未接入（C8）/ 稀疏（C12）」的章节，必须在页面上**具名落位**，且呈现
 * 「原文 + 相对来源标识 + 有效状态 + **承接位置（指名引用）**」；
 * 定位不到该节 ⇒ **具名**标注（不得留空占位、不得以示意内容填充）。
 */
const SECTIONS = [
  { title: '1. 产品概览与客户价值', content: '概览原文' },
  { title: '2. 适用客户与适用场景', content: '适用场景原文' },
  { title: '3. 产品能力', content: '产品能力原文' },
  { title: '6. 前置、互斥、替代与配套产品', content: '前置产品：单位结算账户；配套产品：现金池。' },
  { title: '8. 价格边界', content: '价格边界原文' },
  { title: '9. 风险提示与人工复核', content: '需人工复核：额度审批；风险提示：不得承诺无限透支。' },
  { title: '10. 销售边界', content: '销售边界原文' }
]

const BOUNDARIES = [
  {
    boundaryId: 'SLB-1',
    boundaryKind: 'PROHIBITED_PROMISE' as const,
    text: '不得承诺"无限透支"等误导性表述。',
    riskCategory: 'PURPOSE',
    mandatoryDisplay: true
  },
  {
    boundaryId: 'SLB-2',
    boundaryKind: 'ALLOWED_EXPLANATION' as const,
    text: 'AI/模型不得直接创建透支额度（INV-09）。',
    riskCategory: 'APPROVAL',
    mandatoryDisplay: false
  }
]

const BASE_PROPS = {
  sections: SECTIONS,
  sourceFile: 'cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md',
  salesBoundaries: BOUNDARIES,
  versionStatus: 'DRAFT',
  versionLabel: '产品卡镜像（未发布）',
  effectiveFrom: null
}

describe('ProductInheritedChapters（章级承接区）', () => {
  it('C2/C3/C6/C8/C9/C10/C12 各自具名落位（含承接位置与原文）', () => {
    const wrapper = mount(ProductInheritedChapters, { props: BASE_PROPS })

    for (const key of ['c2', 'c3', 'c6', 'c8', 'c9', 'c10', 'c12']) {
      const block = wrapper.find(`[data-testid="pc-inherited-${key}"]`)
      expect(block.exists(), `${key} 必须具名落位`).toBe(true)
      expect(block.find(`[data-testid="pc-inherited-${key}-meta"]`).text()).toContain('承接位置：')
    }

    // 原文（取自产品卡，逐字呈现）
    expect(wrapper.find('[data-testid="pc-inherited-c6-content"]').text()).toContain('前置产品')
    expect(wrapper.find('[data-testid="pc-inherited-c9-content"]').text()).toContain('人工复核')
    expect(wrapper.find('[data-testid="pc-inherited-c2-content"]').text()).toContain('适用场景原文')

    // 指名引用：各章登记了明确承接位置
    expect(wrapper.find('[data-testid="pc-inherited-c6-meta"]').text()).toContain('本区独立区块')
    expect(wrapper.find('[data-testid="pc-inherited-c9-meta"]').text()).toContain('本区独立区块')
    expect(wrapper.find('[data-testid="pc-inherited-c2-meta"]').text()).toContain('适用边界')
    expect(wrapper.find('[data-testid="pc-inherited-c3-meta"]').text()).toContain('首屏能力标签')
    expect(wrapper.find('[data-testid="pc-inherited-c8-meta"]').text()).toContain('价格与协议')
    expect(wrapper.find('[data-testid="pc-inherited-c12-meta"]').text()).toContain('PROD-FIN')

    // 相对来源 + 有效状态
    const meta = wrapper.find('[data-testid="pc-inherited-c6-meta"]').text()
    expect(meta).toContain('cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md')
    expect(meta).toContain('第 6 节')
    expect(meta).toContain('DRAFT')
    expect(meta).toContain('生效日：未设定')
    expect(wrapper.text()).not.toContain('/home/')
  })

  it('C10 必须呈现**产品级**销售边界（合同字段 salesBoundaries），不只留通用声明', () => {
    const wrapper = mount(ProductInheritedChapters, { props: BASE_PROPS })

    const contract = wrapper.find('[data-testid="pc-inherited-c10-contract"]')
    expect(contract.exists()).toBe(true)
    expect(contract.findAll('[data-testid="pc-inherited-c10-boundary"]')).toHaveLength(2)
    expect(contract.text()).toContain('不得承诺"无限透支"等误导性表述。')
    expect(contract.text()).toContain('PROHIBITED_PROMISE')
    expect(contract.text()).toContain('强制展示')
  })

  it('合同字段为空时如实标注（不以示意内容填充）', () => {
    const wrapper = mount(ProductInheritedChapters, {
      props: { ...BASE_PROPS, salesBoundaries: [] }
    })

    expect(wrapper.find('[data-testid="pc-inherited-c10-contract"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="pc-inherited-c10-contract-empty"]').text()).toContain(
      'salesBoundaries` 为空'
    )
  })

  it('定位不到该节 ⇒ 具名标注（C12 在非 FIN 卡上如实缺失）', () => {
    const wrapper = mount(ProductInheritedChapters, { props: BASE_PROPS })

    expect(wrapper.find('[data-testid="pc-inherited-c12-absent"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pc-inherited-c12-content"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="pc-inherited-c12-absent"]').text()).toContain('未包含第 12 节')
  })

  it('来源不可得时如实标注，不拼接路径', () => {
    const wrapper = mount(ProductInheritedChapters, {
      props: { ...BASE_PROPS, sourceFile: null }
    })

    expect(wrapper.find('[data-testid="pc-inherited-c6-meta"]').text()).toContain('来源标识不可得')
  })
})
