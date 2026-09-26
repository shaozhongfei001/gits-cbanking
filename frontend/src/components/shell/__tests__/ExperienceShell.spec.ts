import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ExperienceShell from '../../../layouts/ExperienceShell.vue'

const stubs = {
  NLayout: { template: '<div class="n-layout"><slot /></div>' },
  NLayoutSider: { template: '<aside class="n-layout-sider"><slot /></aside>' },
  NLayoutHeader: { template: '<header class="n-layout-header"><slot /></header>' },
  NLayoutContent: { template: '<main class="n-layout-content"><slot /></main>' },
  NTag: { template: '<span />' },
  NButton: { template: '<button><slot /></button>' },
  NIcon: { template: '<i><slot /></i>' },
  NTooltip: { template: '<div><slot /></div>' },
  NAvatar: { template: '<span><slot /></span>' },
  NSpace: { template: '<div><slot /></div>' },
  AppSidebar: {
    template:
      '<nav data-testid="shell-sidebar"><button data-testid="shell-brand">GITS 对公客户经营工作台</button>日常作业</nav>',
  },
}

describe('ExperienceShell', () => {
  it('renders the shell with sidebar and header', async () => {
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/workbench', name: 'Workbench', meta: { title: '我的客户经营', objectType: '客户经营应用' }, component: { template: '<div/>' } }],
    })
    await router.push('/workbench')
    const wrapper = mount(ExperienceShell, {
      global: { plugins: [router], stubs },
    })
    expect(wrapper.find('[data-testid="shell-sidebar"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="shell-brand"]').text()).toContain('GITS')
    expect(wrapper.text()).toContain('日常作业')
  })
})
