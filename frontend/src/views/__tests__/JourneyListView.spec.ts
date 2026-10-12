import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { NDataTable } from 'naive-ui'
import { createMemoryHistory, createRouter } from 'vue-router'
import JourneyListView from '../JourneyListView.vue'
import type { Customer, CustomerJourney } from '../../api/engagement'

vi.mock('../../api/engagement', () => ({
  fetchAllJourneys: vi.fn(),
  fetchCustomers: vi.fn(),
  startJourney: vi.fn(),
  formatApiError: (e: unknown, fallback: string) => (e instanceof Error ? e.message : fallback),
  JOURNEY_PHASE_LABELS: {
    KYC_COLLECT: 'KYC信息采集',
    INSIGHT_ANALYSIS: '洞察分析',
    PRODUCT_MATCHING: '产品匹配',
    PREVISIT_PREP: '访前准备',
    POSTVISIT_REVIEW: '访后复盘',
    COMPLETED: '已完成',
  },
}))

vi.mock('naive-ui', async () => {
  const actual = await vi.importActual('naive-ui')
  return {
    ...actual,
    useMessage: () => ({
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    }),
  }
})

/**
 * naive-ui 组件内部 name 不含 `N` 前缀（NModal → `Modal`），
 * 故按真实 name 打桩；其余组件用真实实现以满足行/按钮语义断言。
 */
const stubs = {
  Modal: { template: '<div class="n-modal"><slot /></div>' },
  Spin: { template: '<div class="n-spin" />' },
  Result: { template: '<div class="n-result"><slot name="footer" /></div>' },
  RiskBadge: { template: '<span class="risk-badge" />' },
}

function journey(overrides: Partial<CustomerJourney> = {}): CustomerJourney {
  return {
    journeyId: 'journey-1',
    operatingCaseId: 'case-1',
    customerId: 'c1',
    customerName: '企业A',
    phase: 'INSIGHT_ANALYSIS',
    startedAt: '2026-09-25T06:00:00Z',
    updatedAt: '2026-09-25T06:00:00Z',
    journeyName: '企业A 经营旅程 #1',
    ...overrides,
  }
}

const mockCustomers: Customer[] = [
  { customerId: 'c1', customerName: '企业A', riskLevel: 'HIGH' },
  { customerId: 'c2', customerName: '企业B', riskLevel: 'LOW' },
]

async function mountList() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/engagement', name: 'JourneysHome', component: JourneyListView },
      { path: '/engagement/workspace/:journeyId', name: 'EngagementWorkspace', component: { template: '<div/>' } },
      { path: '/engagement/enter', name: 'JourneyEnterResolver', component: { template: '<div/>' } },
    ],
  })
  await router.push('/engagement')
  const wrapper = mount(JourneyListView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P45 JourneyListView（经营旅程列表）', () => {
  beforeEach(async () => {
    sessionStorage.clear()
    vi.clearAllMocks()
    const { fetchAllJourneys, fetchCustomers, startJourney } = await import('../../api/engagement')
    ;(fetchAllJourneys as ReturnType<typeof vi.fn>).mockResolvedValue([
      journey(),
      journey({
        journeyId: 'journey-2',
        customerId: 'c2',
        customerName: '企业B',
        phase: 'COMPLETED',
        journeyName: '企业B 经营旅程 #1',
      }),
    ])
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
    ;(startJourney as ReturnType<typeof vi.fn>).mockReset()
  })

  it('lists journeys with the required columns', async () => {
    const { wrapper } = await mountList()
    const table = wrapper.findComponent(NDataTable)
    expect(table.props('data')).toHaveLength(2)
    const titles = (table.props('columns') as { title: string }[]).map(column => column.title)
    expect(titles).toEqual(
      expect.arrayContaining([
        '经营旅程名称',
        '经营旅程 ID',
        '客户名称',
        '旅程状态',
        '开始时间',
        '继续旅程',
      ]),
    )
  })

  it('shows 持续经营 only for journeys that are not COMPLETED', async () => {
    const { wrapper } = await mountList()
    expect(wrapper.find('[data-testid="p45-continue-journey-1"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p45-continue-journey-2"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="p45-ended-journey-2"]').exists()).toBe(true)
  })

  it('enters the workspace of the clicked journey (确定的 journeyId)', async () => {
    const { wrapper, router } = await mountList()
    await wrapper.get('[data-testid="p45-continue-journey-1"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('EngagementWorkspace')
    expect(router.currentRoute.value.params.journeyId).toBe('journey-1')
  })

  it('opens the journey workspace by clicking the row of an active journey', async () => {
    const { wrapper, router } = await mountList()
    await wrapper.get('[data-testid="p45-row-journey-1"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.params.journeyId).toBe('journey-1')
  })

  it('shows empty state without inventing rows', async () => {
    const { fetchAllJourneys } = await import('../../api/engagement')
    ;(fetchAllJourneys as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountList()
    expect(wrapper.find('[data-testid="p45-empty"]').exists()).toBe(true)
    expect(wrapper.findComponent(NDataTable).exists()).toBe(false)
  })

  it('shows error four-state when the list request fails', async () => {
    const { fetchAllJourneys } = await import('../../api/engagement')
    ;(fetchAllJourneys as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('upstream'))
    const { wrapper } = await mountList()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('starts a journey for the picked customer and enters its workspace', async () => {
    const { startJourney } = await import('../../api/engagement')
    ;(startJourney as ReturnType<typeof vi.fn>).mockResolvedValue({
      journeyId: 'journey-new',
      customerId: 'c1',
      operatingCaseId: 'case-new',
      phase: 'INSIGHT_ANALYSIS',
      startedAt: '2026-09-25T07:00:00Z',
      journeyName: '企业A 经营旅程 #2',
    })
    const { wrapper, router } = await mountList()

    await wrapper.get('[data-testid="p45-start-journey"]').trigger('click')
    await flushPromises()
    await wrapper.get('[data-testid="p45-pick-c1"]').trigger('click')
    await flushPromises()

    expect(startJourney).toHaveBeenCalledWith('c1')
    // 启动后默认进入旅程（等价于「点击启动旅程 + 进入工作区」）
    expect(router.currentRoute.value.name).toBe('EngagementWorkspace')
    expect(router.currentRoute.value.params.journeyId).toBe('journey-new')
  })

  it('surfaces a named start error and stays on the list when starting fails', async () => {
    const { startJourney } = await import('../../api/engagement')
    ;(startJourney as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('KERT_UNAVAILABLE'))
    const { wrapper, router } = await mountList()

    await wrapper.get('[data-testid="p45-start-journey"]').trigger('click')
    await flushPromises()
    await wrapper.get('[data-testid="p45-pick-c1"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-testid="p45-start-error"]').text()).toContain('KERT_UNAVAILABLE')
    expect(router.currentRoute.value.name).toBe('JourneysHome')
  })

  it('surfaces a customer-list error inside the picker instead of silently showing none', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('客户列表不可用'))
    const { wrapper } = await mountList()
    await wrapper.get('[data-testid="p45-start-journey"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="p45-customers-error"]').text()).toContain('客户列表不可用')
  })
})
