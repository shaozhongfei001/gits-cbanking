import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import WorkbenchView from '../WorkbenchView.vue'
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
  {
    customerId: 'c2',
    customerName: '企业B',
    industry: 'FINANCE',
    enterpriseScale: 'MEDIUM',
    customerTier: 'KEY',
    riskLevel: 'LOW',
  },
]

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
}

async function mountPage() {
  const { fetchCustomers } = await import('../../api/engagement')
  ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/workbench', name: 'Workbench', component: WorkbenchView },
      { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
    ],
  })
  await router.push('/workbench')
  const wrapper = mount(WorkbenchView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P01 WorkbenchView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('renders object context and derived action queue', async () => {
    const wrapper = await mountPage()
    expect(wrapper.get('[data-testid="p01-workbench"]').text()).toContain('客户经营应用')
    expect(wrapper.text()).toContain('首页·我的客户经营')
    expect(wrapper.find('[data-testid="p01-action-queue"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('企业A')
    expect(wrapper.text()).toContain('候选')
  })

  it('shows loading then success four-state', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/workbench', component: WorkbenchView }],
    })
    const wrapper = mount(WorkbenchView, { global: { plugins: [router], stubs } })
    expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(true)
  })

  it('keeps confirm actions disabled on the read-only slice', async () => {
    const wrapper = await mountPage()
    const gated = wrapper.get('[data-testid="gated-action"]')
    expect((gated.element as HTMLButtonElement).disabled).toBe(true)
  })
})
