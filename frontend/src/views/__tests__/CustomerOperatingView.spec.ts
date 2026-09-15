import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CustomerOperatingView from '../CustomerOperatingView.vue'
import type { Customer, CustomerContext } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomer: vi.fn(),
    fetchCustomerContext: vi.fn(),
  }
})

const mockCustomer: Customer = {
  customerId: 'c1',
  customerName: '企业A',
  industry: 'MANUFACTURING',
  enterpriseScale: 'LARGE',
  customerTier: 'STRATEGIC',
  riskLevel: 'HIGH',
  groupFlag: true,
  relationshipSummary: '集团核心成员',
}

const mockContext: CustomerContext = {
  customer: mockCustomer,
  opportunitySignals: [],
  recentInteractions: [],
  activeJourneys: [],
  recentTransactions: [],
}

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty"><slot /></div>' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NGrid: { template: '<div class="n-grid"><slot /></div>' },
  NGi: { template: '<div class="n-gi"><slot /></div>' },
  NCard: { template: '<div class="n-card"><slot /></div>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  NDataTable: { template: '<div class="n-data-table" />' },
}

async function mountP04(path = '/customers/c1') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/customers/:id', name: 'CustomerOperatingView', component: CustomerOperatingView, meta: { pageId: 'P04', objectType: '客户 Account', title: '客户记录·经营总览' } },
      { path: '/customers/:id/group', name: 'CustomerGroupView', component: { template: '<div/>' } },
      { path: '/customers/:id/funds', name: 'CustomerFundsView', component: { template: '<div/>' } },
      { path: '/customers/:id/parties', name: 'CustomerPartiesView', component: { template: '<div/>' } },
      { path: '/journeys/:id', name: 'JourneyTimeline', component: { template: '<div/>' } },
    ],
  })
  await router.push(path)
  const wrapper = mount(CustomerOperatingView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P04 CustomerOperatingView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully with operating overview from fetchCustomer and fetchCustomerContext', async () => {
    const { fetchCustomer, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP04()
    expect(wrapper.get('[data-testid="p04-customer-record"]').text()).toContain('客户 Account')
    expect(wrapper.text()).toContain('企业A')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="tab-p05"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="tab-p06"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="tab-p07"]').exists()).toBe(true)
  })

  it('shows empty success when KYC and signals are absent', async () => {
    const { fetchCustomer, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP04()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('暂无机会信号')
  })

  it('shows error four-state when fetchCustomer fails', async () => {
    const { fetchCustomer, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('not found'))
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('not found'))
    const wrapper = await mountP04()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('shows loading four-state before the customer record resolves', async () => {
    const { fetchCustomer, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/customers/:id', name: 'CustomerOperatingView', component: CustomerOperatingView },
        { path: '/customers/:id/group', name: 'CustomerGroupView', component: { template: '<div/>' } },
        { path: '/customers/:id/funds', name: 'CustomerFundsView', component: { template: '<div/>' } },
        { path: '/customers/:id/parties', name: 'CustomerPartiesView', component: { template: '<div/>' } },
      ],
    })
    await router.push('/customers/c1')
    const wrapper = mount(CustomerOperatingView, { global: { plugins: [router], stubs } })
    expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(true)
  })

  it('keeps the write action disabled with a reason and unlock path', async () => {
    const { fetchCustomer, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP04()
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })
})
