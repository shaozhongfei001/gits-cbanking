import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ObjectHeader from '../ObjectHeader.vue'

const stubs = {
  NButton: { template: '<button class="n-button" v-bind="$attrs" @click="$emit(\'click\')"><slot /></button>' },
}

describe('ObjectHeader', () => {
  it('shows object type, title, status and a restore-back control', async () => {
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div/>' } }],
    })
    const wrapper = mount(ObjectHeader, {
      props: {
        objectType: '客户经营应用',
        objectStatus: '今日',
        title: '首页·我的客户经营',
        pageId: 'P01',
      },
      global: { plugins: [router], stubs },
    })
    expect(wrapper.get('[data-testid="object-header"]').text()).toContain('客户经营应用')
    expect(wrapper.text()).toContain('首页·我的客户经营')
    expect(wrapper.get('[data-testid="object-status"]').text()).toContain('今日')
    expect(wrapper.find('[data-testid="page-reference-back"]').exists()).toBe(true)

    // 视觉压缩契约：可见行只有「对象类型 + 当前状态」，大号标题不再渲染；
    // 标题降级为 sr-only 的 h1，保留无障碍语义与既有文本断言。
    expect(wrapper.get('.object-copy').find('h1').exists()).toBe(false)
    expect(wrapper.findAll('.object-copy > p')).toHaveLength(2)
    expect(wrapper.get('h1.object-title-sr').text()).toBe('首页·我的客户经营')
  })
})
