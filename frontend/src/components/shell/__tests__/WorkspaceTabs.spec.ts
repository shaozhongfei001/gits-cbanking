import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import WorkspaceTabs from '../WorkspaceTabs.vue'
import { useWorkspaceTabsStore } from '../../../stores/workspaceTabs'

const stubs = {
  NButton: { template: '<button class="n-button" v-bind="$attrs" @click="$emit(\'click\')"><slot /></button>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
}

describe('WorkspaceTabs', () => {
  it('renders opened tabs and can close them', async () => {
    setActivePinia(createPinia())
    const store = useWorkspaceTabsStore()
    store.openTab({
      id: 'p01',
      title: '我的客户经营',
      path: '/workbench',
      routeName: 'Workbench',
      objectType: '客户经营应用',
    })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/workbench', component: { template: '<div/>' } }],
    })
    await router.push('/workbench')
    const wrapper = mount(WorkspaceTabs, { global: { plugins: [router], stubs } })
    expect(wrapper.text()).toContain('我的客户经营')
    await wrapper.get('[data-testid="workspace-tab-close-p01"]').trigger('click')
    expect(store.tabs).toHaveLength(0)
  })
})
