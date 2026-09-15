import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import SignalsView from '../SignalsView.vue'
import type { Customer, CustomerContext, OpportunitySignal } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
    fetchCustomerContext: vi.fn(),
  }
})

const mockCustomer: Customer = {
  customerId: 'c1',
  customerName: '企业A',
}

const mockSignal: OpportunitySignal = {
  signalId: 'sig-1',
  signalType: 'FINANCING_NEED',
  content: '流动资金周转压力',
  sourceType: 'ANALYSIS',
  status: 'DETECTED',
  detectedAt: '2026-08-01T00:00:00Z',
}

const mockContext: CustomerContext = {
  customer: mockCustomer,
  opportunitySignals: [mockSignal],
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
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NInput: {
    props: ['value'],
    template: '<input data-testid="p08-filter" :value="value" @input="$emit(\'update:value\', $event.target.value)" />',
  },
}

async function mountP08() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/signals', name: 'SignalsHome', component: SignalsView },
      { path: '/signals/:id', name: 'SignalRecord', component: { template: '<div/>' } },
      { path: '/engagements', name: 'EngagementsHome', component: { template: '<div/>' } },
      { path: '/engagement', name: 'EngagementWorkspace', component: { template: '<div/>' } },
    ],
  })
  await router.push('/signals')
  const wrapper = mount(SignalsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P08 SignalsView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully from fetchCustomers and opportunitySignals', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP08()
    expect(wrapper.get('[data-testid="p08-signals"]').text()).toContain('经营信号')
    expect(wrapper.text()).toContain('流动资金周转压力')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when no signals are present', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...mockContext,
      opportunitySignals: [],
    })
    const wrapper = await mountP08()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchCustomers fails', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('forbidden'))
    const wrapper = await mountP08()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('keeps batch write actions disabled', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP08()
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })

  it('links 互动对象 to P10 and 经营旅程 to P11', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP08()
    expect(wrapper.get('[data-testid="p08-open-engagements"]').attributes('href')).toBe('/engagements')
    expect(wrapper.get('[data-testid="p08-open-journey"]').attributes('href')).toBe('/engagement')
    expect(wrapper.get('[data-testid="signals-tab-p11"]').attributes('href')).toBe('/engagement')
    expect(wrapper.get('[data-testid="signals-tab-p08"]').attributes('href')).toBe('/signals')
    expect(wrapper.get('[data-testid="signals-tab-p10"]').attributes('href')).toBe('/engagements')
  })
})
