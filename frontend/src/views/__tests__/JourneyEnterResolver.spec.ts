import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import JourneyEnterResolver from '../JourneyEnterResolver.vue'
import type { CustomerJourney } from '../../api/engagement'

vi.mock('../../api/engagement', () => ({
  fetchCustomerJourneys: vi.fn(),
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

const stubs = {
  NButton: {
    props: ['disabled', 'loading'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  NSpin: { template: '<div class="n-spin" />' },
}

function journey(overrides: Partial<CustomerJourney> = {}): CustomerJourney {
  return {
    journeyId: 'journey-1',
    operatingCaseId: 'case-1',
    customerId: 'c1',
    customerName: '企业A',
    phase: 'INSIGHT_ANALYSIS',
    startedAt: '2026-09-25T06:00:00Z',
    journeyName: '企业A 经营旅程 #1',
    ...overrides,
  }
}

async function mountResolver(query = '?customerId=c1') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/engagement', name: 'JourneysHome', component: { template: '<div/>' } },
      { path: '/engagement/enter', name: 'JourneyEnterResolver', component: JourneyEnterResolver },
      { path: '/engagement/workspace/:journeyId', name: 'EngagementWorkspace', component: { template: '<div/>' } },
    ],
  })
  await router.push(`/engagement/enter${query}`)
  const wrapper = mount(JourneyEnterResolver, { global: { plugins: [router], stubs } })
  await flushPromises()
  // onMounted 内的解析可能触发 router.replace，需要再冲一次微任务
  await flushPromises()
  return { wrapper, router }
}

describe('JourneyEnterResolver（确定性直达）', () => {
  beforeEach(async () => {
    sessionStorage.clear()
    vi.clearAllMocks()
    const { fetchCustomerJourneys, startJourney } = await import('../../api/engagement')
    ;(fetchCustomerJourneys as ReturnType<typeof vi.fn>).mockResolvedValue([journey()])
    ;(startJourney as ReturnType<typeof vi.fn>).mockReset()
  })

  it('enters directly when there is exactly one active journey', async () => {
    const { fetchCustomerJourneys } = await import('../../api/engagement')
    const { router } = await mountResolver()
    expect(fetchCustomerJourneys).toHaveBeenCalledWith('c1')
    expect(router.currentRoute.value.name).toBe('EngagementWorkspace')
    expect(router.currentRoute.value.params.journeyId).toBe('journey-1')
  })

  it('ignores COMPLETED journeys when resolving', async () => {
    const { fetchCustomerJourneys } = await import('../../api/engagement')
    ;(fetchCustomerJourneys as ReturnType<typeof vi.fn>).mockResolvedValue([
      journey({ journeyId: 'done-1', phase: 'COMPLETED' }),
    ])
    const { wrapper, router } = await mountResolver()
    expect(router.currentRoute.value.name).toBe('JourneyEnterResolver')
    expect(wrapper.find('[data-testid="journey-enter-none"]').exists()).toBe(true)
  })

  it('offers to start a journey when the customer has none active', async () => {
    const { fetchCustomerJourneys, startJourney } = await import('../../api/engagement')
    ;(fetchCustomerJourneys as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(startJourney as ReturnType<typeof vi.fn>).mockResolvedValue({
      journeyId: 'journey-new',
      customerId: 'c1',
      operatingCaseId: 'case-new',
      phase: 'INSIGHT_ANALYSIS',
      startedAt: '2026-09-25T07:00:00Z',
      journeyName: '企业A 经营旅程 #1',
    })
    const { wrapper, router } = await mountResolver()
    expect(wrapper.find('[data-testid="journey-enter-none"]').exists()).toBe(true)

    await wrapper.get('[data-testid="journey-enter-start"]').trigger('click')
    await flushPromises()
    expect(startJourney).toHaveBeenCalledWith('c1')
    expect(router.currentRoute.value.params.journeyId).toBe('journey-new')
  })

  it('asks the user to choose when multiple active journeys exist', async () => {
    const { fetchCustomerJourneys } = await import('../../api/engagement')
    ;(fetchCustomerJourneys as ReturnType<typeof vi.fn>).mockResolvedValue([
      journey({ journeyId: 'j-1' }),
      journey({ journeyId: 'j-2', phase: 'PREVISIT_PREP' }),
    ])
    const { wrapper, router } = await mountResolver()
    // 歧义 ⇒ 不自动进入，交由用户选择
    expect(router.currentRoute.value.name).toBe('JourneyEnterResolver')
    expect(wrapper.find('[data-testid="journey-enter-multiple"]').exists()).toBe(true)
    const options = wrapper.findAll('[data-testid^="journey-enter-option-"]')
    expect(options).toHaveLength(2)

    await wrapper.get('[data-testid="journey-enter-option-j-2"] button').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.params.journeyId).toBe('j-2')
  })

  it('errors out without a customerId instead of guessing', async () => {
    const { fetchCustomerJourneys } = await import('../../api/engagement')
    const { wrapper } = await mountResolver('')
    expect(fetchCustomerJourneys).not.toHaveBeenCalled()
    expect(wrapper.get('[data-testid="journey-enter-error"]').text()).toContain('缺少 customerId')
  })

  it('shows a named error when the journey query fails', async () => {
    const { fetchCustomerJourneys } = await import('../../api/engagement')
    ;(fetchCustomerJourneys as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('upstream'))
    const { wrapper } = await mountResolver()
    expect(wrapper.get('[data-testid="journey-enter-error"]').text()).toContain('upstream')
  })
})
