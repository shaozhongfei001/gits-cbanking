import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductInheritedChapters from '../ProductInheritedChapters.vue'

/**
 * PC-i1 · W1-a/W1-b 验收：R2 映射记为「无任何对应区块」的 C6/C9，
 * 必须有**独立可见区块**，且呈现「原文 + 相对来源标识 + 有效状态」；
 * 定位不到该节 ⇒ **具名**标注（不得留空占位、不得以示意内容填充）。
 */
const SECTIONS = [
  { title: '1. 产品概览与客户价值', content: '概览原文' },
  { title: '6. 前置、互斥、替代与配套产品', content: '前置产品：单位结算账户；配套产品：现金池。' },
  { title: '9. 风险提示与人工复核', content: '需人工复核：额度审批；风险提示：不得承诺无限透支。' }
]

const BASE_PROPS = {
  sections: SECTIONS,
  sourceFile: 'cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md',
  versionStatus: 'DRAFT',
  versionLabel: '产品卡镜像（未发布）',
  effectiveFrom: null
}

describe('ProductInheritedChapters（C6/C9 独立承接区）', () => {
  it('C6/C9 各自独立呈现原文 + 相对来源 + 有效状态', () => {
    const wrapper = mount(ProductInheritedChapters, { props: BASE_PROPS })

    for (const id of ['c6', 'c9']) {
      expect(wrapper.find(`[data-testid="pc-inherited-${id}"]`).exists()).toBe(true)
      expect(wrapper.find(`[data-testid="pc-inherited-${id}-content"]`).text()).not.toBe('')
    }
    expect(wrapper.find('[data-testid="pc-inherited-c6-content"]').text()).toContain('前置产品')
    expect(wrapper.find('[data-testid="pc-inherited-c9-content"]').text()).toContain('人工复核')

    const meta = wrapper.find('[data-testid="pc-inherited-c6-meta"]').text()
    expect(meta).toContain('cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md')
    expect(meta).toContain('第 6 节')
    expect(meta).toContain('DRAFT')
    expect(meta).toContain('生效日：未设定')

    // 相对来源：不得出现绝对路径
    expect(wrapper.text()).not.toContain('/home/')
  })

  it('定位不到该节 ⇒ 具名标注，不以示意内容填充', () => {
    const wrapper = mount(ProductInheritedChapters, {
      props: { ...BASE_PROPS, sections: [SECTIONS[0]] }
    })

    expect(wrapper.find('[data-testid="pc-inherited-c6-absent"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pc-inherited-c6-content"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="pc-inherited-c6-absent"]').text()).toContain('未包含第 6 节')
  })

  it('来源不可得时如实标注，不拼接路径', () => {
    const wrapper = mount(ProductInheritedChapters, {
      props: { ...BASE_PROPS, sourceFile: null }
    })

    expect(wrapper.find('[data-testid="pc-inherited-c6-meta"]').text()).toContain('来源标识不可得')
  })
})
