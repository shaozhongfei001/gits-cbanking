import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import NeedPlanView from '../NeedPlanView.vue'
import type { Customer, CustomerContext, KycGapProfile, OpportunitySignal } from '../../api/engagement'

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

const mockKyc: KycGapProfile = {
  profileId: 'gap-1',
  customerId: 'c1',
  asOf: '2026-08-25T00:00:00Z',
  knownItems: ['统一社会信用代码'],
  partialKnownItems: [],
  staleItems: [],
  conflictingOrAmbiguousItems: [],
  unknownItems: ['近12个月结算结构'],
  priorityQuestions: ['本轮资金缺口确认？'],
}

const mockContext: CustomerContext = {
  customer: mockCustomer,
  kycGapProfile: mockKyc,
  opportunitySignals: [mockSignal],
  claims: [],
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

async function mountP22(id = 'sig-1') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/needs/:id/plan', name: 'NeedPlan', component: NeedPlanView },
      { path: '/needs/:id', name: 'NeedRecord', component: { template: '<div/>' } },
    ],
  })
  await router.push(`/needs/${id}/plan`)
  const wrapper = mount(NeedPlanView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P22 NeedPlanView C2 degrade', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully as a read-only KYC/signal derived view', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP22()
    expect(wrapper.get('[data-testid="p22-need-plan"]').text()).toContain('非正式 Need（C2 降级）')
    expect(wrapper.text()).toContain('流动资金周转压力')
    expect(wrapper.text()).toContain('近12个月结算结构')
    expect(wrapper.text()).toContain('sig-1')
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(wrapper.text()).not.toMatch(/\bG0\b/)
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty derived KYC when the profile has no items', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...mockContext,
      kycGapProfile: {
        ...mockKyc,
        knownItems: [],
        unknownItems: [],
        priorityQuestions: [],
      },
    })
    const wrapper = await mountP22()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetch fails', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('upstream'))
    const wrapper = await mountP22()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables 创建建议书 because proposals are out of this loop', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)
    const wrapper = await mountP22()
    expect(wrapper.text()).toContain('创建建议书')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })
})
