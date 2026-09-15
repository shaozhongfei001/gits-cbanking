import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import Dashboard from '../Dashboard.vue'
import type { Customer } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
  }
})

const mockCustomers: Customer[] = [
  {
    customerId: 'c1',
    customerName: '企业A',
    industry: 'MANUFACTURING',
    enterpriseScale: 'LARGE',
    customerTier: 'STRATEGIC',
    riskLevel: 'HIGH',
  },
]

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result" />' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
}

describe('Dashboard compatibility', () => {
  it('still renders the P01 workbench so legacy / Dashboard entry remains open', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'Dashboard', component: Dashboard },
        { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
      ],
    })
    const wrapper = mount(Dashboard, { global: { plugins: [router], stubs } })
    await flushPromises()
    expect(wrapper.find('[data-testid="p01-workbench"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('首页·我的客户经营')
  })
})
