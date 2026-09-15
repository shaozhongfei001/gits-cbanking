import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import SignalRecordView from '../SignalRecordView.vue'
import type { Customer, CustomerContext, OpportunitySignal } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
    fetchCustomerContext: vi.fn(),
    confirmSignal: vi.fn(),
    dismissSignal: vi.fn(),
  }
})

const mockCustomer: Customer = {
  customerId: 'c1',
  customerName: '企业A',
}

const mockSignal: OpportunitySignal = {
  signalId: 'sig-1',
  signalType: 'PRODUCT_OPPORTUNITY',
  content: '结算产品适配候选',
  sourceType: 'ANALYSIS',
  status: 'DETECTED',
  confidence: 0.72,
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
}

async function mountP09(id = 'sig-1') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/signals', name: 'SignalsHome', component: { template: '<div/>' } },
      { path: '/signals/:id', name: 'SignalRecord', component: SignalRecordView },
      { path: '/engagements', name: 'EngagementsHome', component: { template: '<div/>' } },
      { path: '/engagement', name: 'EngagementWorkspace', component: { template: '<div/>' } },
    ],
  })
  await router.push(`/signals/${id}`)
  const wrapper = mount(SignalRecordView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P09 SignalRecordView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully from an already loaded signal DTO', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP09()
    expect(wrapper.get('[data-testid="p09-signal-record"]').text()).toContain('经营信号')
    expect(wrapper.text()).toContain('结算产品适配候选')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows error four-state when the signal cannot be resolved', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...mockContext,
      opportunitySignals: [],
    })
    const wrapper = await mountP09('missing')
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('shows empty/error when customer list load fails', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('upstream'))
    const wrapper = await mountP09()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables 忽略 / 确认 / 批量指派 and does not call write APIs', async () => {
    const { fetchCustomers, fetchCustomerContext, confirmSignal, dismissSignal } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP09()
    expect(wrapper.text()).toContain('忽略')
    expect(wrapper.text()).toContain('确认')
    expect(wrapper.text()).toContain('批量指派')
    const gated = wrapper.findAll('[data-testid="gated-action"]')
    expect(gated.length).toBeGreaterThanOrEqual(3)
    for (const button of gated) {
      expect((button.element as HTMLButtonElement).disabled).toBe(true)
    }
    expect(confirmSignal).not.toHaveBeenCalled()
    expect(dismissSignal).not.toHaveBeenCalled()
  })
})
