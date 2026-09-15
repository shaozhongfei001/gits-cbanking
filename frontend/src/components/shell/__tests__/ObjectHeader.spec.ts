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
  })
})
