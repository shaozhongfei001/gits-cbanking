import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductCenterView from '../ProductCenterView.vue'

/**
 * PC0 骨架验收：
 * - 路由/菜单占位页可渲染；
 * - 八个固定章节占位齐备（PI-FR-026 的静态前身）；
 * - 骨架不得读取客户上下文、不得出现推荐性用语（PI-BR-002/003）。
 */
describe('ProductCenterView PC0 骨架', () => {
  it('renders shell, hero and eight static section placeholders without business calls', () => {
    const wrapper = mount(ProductCenterView)

    expect(wrapper.find('[data-testid="product-center-shell"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="product-center-hero"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="product-center-skeleton-note"]').exists()).toBe(true)

    const items = wrapper.findAll('.pc-section-item')
    expect(items).toHaveLength(8)
    expect(items[0].text()).toContain('60 秒读懂')
    expect(items[7].text()).toContain('常见问题')

    expect(wrapper.text()).toContain('企业金融产品中心')
  })

  it('keeps product-first boundary: no customer context, no recommendation wording', () => {
    const wrapper = mount(ProductCenterView)

    // PI-BR-002：不读取客户画像 / 账户 / 交易 / 授信 / 商机
    expect(wrapper.text()).not.toContain('客户画像')
    // PI-BR-003：不输出适配分 / 推荐 / 授信结论
    expect(wrapper.text()).not.toContain('适配分')
    expect(wrapper.text()).not.toContain('立即推荐')
    expect(wrapper.text()).not.toContain('下一最佳行动')
  })
})
