import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import EngagementWorkspace from '../EngagementWorkspace.vue'
import type { Customer, CustomerJourney } from '../../api/engagement'

vi.mock('../../api/engagement', () => ({
  fetchCustomers: vi.fn(),
  fetchJourney: vi.fn(),
  fetchKycGapProfile: vi.fn(),
  generateOutreachScript: vi.fn(),
  generateMeetingScript: vi.fn(),
  executePrevisit: vi.fn(),
  preparePrevisit: vi.fn(),
  executePostvisit: vi.fn(),
  completeJourney: vi.fn(),
  handleNewEvidence: vi.fn(),
  executeSupplyChainGraph: vi.fn(),
  JOURNEY_PHASE_LABELS: {
    KYC_COLLECT: 'KYC信息采集',
    INSIGHT_ANALYSIS: '洞察分析',
    PRODUCT_MATCHING: '产品匹配',
    PREVISIT_PREP: '访前准备',
    POSTVISIT_REVIEW: '访后复盘',
    COMPLETED: '已完成',
  },
  formatApiError: (e: unknown, fallback: string) => (e instanceof Error ? e.message : fallback),
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

const mockCustomers: Customer[] = [
  { customerId: 'c1', customerName: '企业A', riskLevel: 'HIGH', rmId: 'RM-1' },
]

const emptyGap = {
  profileId: 'p1',
  customerId: 'c1',
  asOf: '2026-08-25T00:00:00Z',
  knownItems: [],
  partialKnownItems: [],
  staleItems: [],
  conflictingOrAmbiguousItems: [],
  unknownItems: [],
  priorityQuestions: [],
}

function journeyFixture(overrides: Partial<CustomerJourney> = {}): CustomerJourney {
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

const stubs = {
  NButton: {
    props: ['disabled', 'loading'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
}

async function mountWorkspace(path = '/engagement/workspace/journey-1') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/engagement', name: 'JourneysHome', component: { template: '<div data-testid="list-home" />' } },
      { path: '/engagement/workspace/:journeyId?', name: 'EngagementWorkspace', component: EngagementWorkspace },
      { path: '/engagement/previsit/gaps', name: 'PrevisitGaps', component: { template: '<div/>' } },
      { path: '/in-meeting/:id?', name: 'InMeetingAssistant', component: { template: '<div/>' } },
    ],
  })
  await router.push(path)
  const wrapper = mount(EngagementWorkspace, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P11 EngagementWorkspace（journeyId 驱动的确定性工作区）', () => {
  beforeEach(async () => {
    sessionStorage.clear()
    vi.clearAllMocks()
    const { fetchCustomers, fetchJourney, fetchKycGapProfile } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
    ;(fetchJourney as ReturnType<typeof vi.fn>).mockResolvedValue(journeyFixture())
    ;(fetchKycGapProfile as ReturnType<typeof vi.fn>).mockResolvedValue(emptyGap)
  })

  it('renders the journey from the URL param, not from session state', async () => {
    const { fetchJourney } = await import('../../api/engagement')
    const { wrapper } = await mountWorkspace('/engagement/workspace/journey-1')

    expect(fetchJourney).toHaveBeenCalledWith('journey-1')
    const bar = wrapper.get('[data-testid="p11-journey-bar"]')
    expect(bar.text()).toContain('企业A')
    expect(bar.text()).toContain('洞察分析')
    expect(bar.text()).toContain('企业A 经营旅程 #1')
    expect(bar.text()).not.toContain('未启动')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('keeps stage path and metrics, and never exposes start/switch customer actions', async () => {
    const { wrapper } = await mountWorkspace()
    // 当前 ObjectHeader 渲染 objectType/objectStatus（router meta: 互动 Interaction / 经营旅程）
    expect(wrapper.text()).toContain('互动 Interaction')
    expect(wrapper.text()).toContain('经营旅程')
    expect(wrapper.find('[data-testid="stage-path"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="highlights-metrics"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('访前准备')
    expect(wrapper.text()).toContain('会中协作')
    // 回归：工作区不再提供「启动旅程 / 选择客户 / 切换客户」
    expect(wrapper.find('[data-testid="p11-start-journey"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="p11-select-customer"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('切换客户')
    expect(wrapper.text()).not.toContain('请先选择客户')
  })

  it('opens previsit workspace and keeps 记为正式 Claim gated', async () => {
    const { wrapper } = await mountWorkspace()
    expect((wrapper.get('[data-testid="p11-open-previsit"]').element as HTMLButtonElement).disabled).toBe(false)
    expect((wrapper.get('[data-testid="p11-mark-ready"]').element as HTMLButtonElement).disabled).toBe(true)
    const claimBtn = wrapper.findAll('button').find((b) => b.text().includes('记为正式 Claim'))
    expect(claimBtn).toBeTruthy()
    expect((claimBtn!.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('redirects to the journey list when journeyId is missing (铁律：无 id 不渲染工作区)', async () => {
    const { router } = await mountWorkspace('/engagement/workspace')
    expect(router.currentRoute.value.name).toBe('JourneysHome')
  })

  it('shows error four-state when the journey cannot be loaded', async () => {
    const { fetchJourney } = await import('../../api/engagement')
    ;(fetchJourney as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('旅程不存在'))
    const { wrapper } = await mountWorkspace()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('hides 完成旅程 for a COMPLETED journey', async () => {
    const { fetchJourney } = await import('../../api/engagement')
    ;(fetchJourney as ReturnType<typeof vi.fn>).mockResolvedValue(
      journeyFixture({ phase: 'COMPLETED' }),
    )
    const { wrapper } = await mountWorkspace()
    expect(wrapper.get('[data-testid="p11-journey-bar"]').text()).toContain('已完成')
    expect(wrapper.find('[data-testid="p11-complete-journey"]').exists()).toBe(false)
  })

  it('navigates back to the journey list from 返回列表', async () => {
    const { wrapper, router } = await mountWorkspace()
    await wrapper.get('[data-testid="p11-back-list"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('JourneysHome')
  })

  it('keeps the workspace usable when the KYC gap profile fails (journey context intact)', async () => {
    const { fetchKycGapProfile } = await import('../../api/engagement')
    ;(fetchKycGapProfile as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('KYC 不可用'))
    const { wrapper } = await mountWorkspace()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="p11-journey-bar"]').text()).toContain('企业A')
    expect(wrapper.get('[data-testid="p11-start-error"]').text()).toContain('KYC')
  })

  it('falls back to journey-carried customer fields when the customer list fails', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('客户列表不可用'))
    const { wrapper } = await mountWorkspace()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="p11-journey-bar"]').text()).toContain('企业A')
  })
})
