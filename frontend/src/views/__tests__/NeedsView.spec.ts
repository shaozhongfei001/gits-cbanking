import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import NeedsView from '../NeedsView.vue'
import type { Claim, Customer, CustomerContext, OpportunitySignal } from '../../api/engagement'

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

const mockClaim: Claim = {
  claimId: 'clm-1',
  customerId: 'c1',
  claimType: 'CUSTOMER_STATEMENT',
  content: '客户口头提及扩产意向',
  status: 'CANDIDATE',
}

const mockContext: CustomerContext = {
  customer: mockCustomer,
  opportunitySignals: [mockSignal],
  claims: [mockClaim],
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

async function mountP20() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/needs', name: 'NeedsHome', component: NeedsView },
      { path: '/needs/:id', name: 'NeedRecord', component: { template: '<div/>' } },
    ],
  })
  await router.push('/needs')
  const wrapper = mount(NeedsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P20 NeedsView C2 degrade', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully from opportunitySignals and claims without inventing needId', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const { wrapper } = await mountP20()
    expect(wrapper.get('[data-testid="p20-needs"]').text()).toContain('非正式 Need（C2 降级）')
    expect(wrapper.text()).toContain('流动资金周转压力')
    expect(wrapper.text()).toContain('客户口头提及扩产意向')
    expect(wrapper.text()).toContain('sig-1')
    expect(wrapper.text()).toContain('clm-1')
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when there are no signals or claims', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...mockContext,
      opportunitySignals: [],
      claims: [],
    })
    const { wrapper } = await mountP20()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchCustomers fails', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('forbidden'))
    const { wrapper } = await mountP20()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('keeps 新建机会 disabled and does not treat PNG codes as writable Need ids', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const { wrapper, router } = await mountP20()
    expect(wrapper.text()).toContain('新建机会')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
    await wrapper.get('[data-testid="p20-open-sig-1"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/needs/sig-1')
  })
})
