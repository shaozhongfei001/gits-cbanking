import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import NeedPlanView from '../NeedPlanView.vue'
import ProposalRecordView from '../ProposalRecordView.vue'
import type { Customer, CustomerContext, OpportunitySignal } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
    fetchCustomerContext: vi.fn(),
  }
})

const mockCustomer: Customer = { customerId: 'c1', customerName: '企业A' }
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

const WORKSPACE_ROUTE = {
  path: '/recommendation/:runId',
  name: 'ProductRecommendationWorkspace',
  component: { template: '<div class="workspace-stub" />' },
}

describe('P22 发起产品推荐 entry', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    sessionStorage.clear()
  })

  it('renders and enables the entry once the customer row is loaded, then navigates', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([mockCustomer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(mockContext)

    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/needs/:id/plan', name: 'NeedPlan', component: NeedPlanView },
        WORKSPACE_ROUTE,
      ],
    })
    await router.push('/needs/sig-1/plan')
    const wrapper = mount(NeedPlanView, { global: { plugins: [router], stubs } })
    await flushPromises()

    const btn = wrapper.get('[data-testid="p22-start-recommendation"]')
    expect(btn.text()).toBe('发起产品推荐')
    expect((btn.element as HTMLButtonElement).disabled).toBe(false)

    await btn.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('ProductRecommendationWorkspace')
    expect(router.currentRoute.value.params.runId).toBe('new')
    expect(router.currentRoute.value.query.customerId).toBe('c1')
  })
})

describe('P25-G2 打开推荐工作区 entry', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    sessionStorage.clear()
  })

  it('renders the entry and opens the workspace (new mode when no linked runId)', async () => {
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/proposals/:id', name: 'ProposalRecord', component: ProposalRecordView },
        WORKSPACE_ROUTE,
      ],
    })
    await router.push('/proposals/ph-1')
    const wrapper = mount(ProposalRecordView, { global: { plugins: [router], stubs } })
    await flushPromises()

    const btn = wrapper.get('[data-testid="p25-open-recommendation"]')
    expect(btn.text()).toBe('打开推荐工作区')

    await btn.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('ProductRecommendationWorkspace')
    expect(router.currentRoute.value.params.runId).toBe('new')
  })

  it('opens the linked run when the proposal record carries query.runId', async () => {
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/proposals/:id', name: 'ProposalRecord', component: ProposalRecordView },
        WORKSPACE_ROUTE,
      ],
    })
    await router.push({ path: '/proposals/ph-1', query: { runId: 'run-9', customerId: 'c9' } })
    const wrapper = mount(ProposalRecordView, { global: { plugins: [router], stubs } })
    await flushPromises()

    await wrapper.get('[data-testid="p25-open-recommendation"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.params.runId).toBe('run-9')
    expect(router.currentRoute.value.query.customerId).toBe('c9')
  })
})
