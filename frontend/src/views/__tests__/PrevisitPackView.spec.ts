import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import PrevisitPackView from '../PrevisitPackView.vue'
import { usePrevisitStore } from '../../stores/previsit'
import type { PreparedPrevisitResponse } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    executePrevisit: vi.fn(),
  }
})

vi.mock('../../components/KnowledgePrevisitReport.vue', () => ({
  default: { template: '<div class="knowledge-previsit-stub" />' },
}))

const mockPack: PreparedPrevisitResponse = {
  outreachScript: {
    scriptId: 'out-1',
    customerId: 'c1',
    rmId: 'rm1',
    operatingCaseId: 'oc1',
    journeyId: 'j1',
    channel: 'EMAIL',
    objective: '确认扩产节奏',
    openingLine: '开场',
    talkingPoints: [],
    riskReminders: [],
    closingLine: '结束',
    followUpAction: '预约会面',
    createdAt: '2026-08-25T00:00:00Z',
  },
  meetingScript: {
    scriptId: 'meet-1',
    customerId: 'c1',
    rmId: 'rm1',
    operatingCaseId: 'oc1',
    journeyId: 'j1',
    meetingObjective: '扩产融资专题',
    previsitSummary: '摘要',
    agendaItems: [],
    kycQuestions: [],
    productDiscussions: [],
    riskPoints: [],
    closingSummary: '收口',
    createdAt: '2026-08-25T00:00:00Z',
  },
  previsitReport: {
    reportId: 'r1',
    customerId: 'c1',
    customerName: '企业A',
    rmName: '张经理',
    visitObjective: '扩产融资专题拜访',
    customerOverview: {
      industry: '制造业',
      enterpriseScale: '大型',
      customerTier: '战略客户',
      registeredCapitalCny: 1,
      riskLevel: '中',
      relationshipSummary: '长期合作',
    },
    kycGapSummary: { knownItems: [], partialKnownItems: [], unknownItems: [], priorityQuestions: [] },
    productSchemes: [],
    keyQuestions: [],
    riskReminders: [],
    visitStrategy: '先对账',
  },
  battleCard: {
    cardId: 'bc1',
    customerName: '企业A',
    visitObjective: '扩产融资专题拜访',
    customerTier: '战略客户',
    riskLevel: '中',
    keyPoints: [],
    productHints: [],
    dontForget: [],
    bottomLine: '不承诺定价',
  },
  assemblyTrace: [],
  skillSections: [],
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

async function mountP14(
  query: Record<string, string> = { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' },
  seed?: (store: ReturnType<typeof usePrevisitStore>) => void,
) {
  setActivePinia(createPinia())
  if (seed) {
    seed(usePrevisitStore())
  }
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/engagement/previsit/pack', name: 'PrevisitPack', component: PrevisitPackView }],
  })
  await router.push({ path: '/engagement/previsit/pack', query })
  const wrapper = mount(PrevisitPackView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P14 PrevisitPackView', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.clearAllMocks()
  })

  it('shows full pack read-only from store without calling executePrevisit', async () => {
    const { executePrevisit } = await import('../../api/engagement')
    const wrapper = await mountP14(
      { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' },
      (store) => {
        store.setContext({ journeyId: 'j1', operatingCaseId: 'oc1', customerId: 'c1', rmId: 'rm1' })
        store.previsitResult = mockPack
        store.running = true
      },
    )
    expect(wrapper.get('[data-testid="p14-previsit-pack"]').text()).toContain('访前包')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p14-pack-result"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('外联脚本')
    expect(executePrevisit as ReturnType<typeof vi.fn>).not.toHaveBeenCalled()
  })

  it('shows empty success when previsit not yet generated', async () => {
    const wrapper = await mountP14()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p14-empty"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/尚未生成访前包/)
  })

  it('disables complete when journey object is missing', async () => {
    const wrapper = await mountP14({})
    expect((wrapper.get('[data-testid="p14-complete"]').element as HTMLButtonElement).disabled).toBe(true)
    expect((wrapper.get('[data-testid="p14-send-mobile"]').element as HTMLButtonElement).disabled).toBe(true)
  })

  it('renders 3.2 wizard step path', async () => {
    const wrapper = await mountP14()
    expect(wrapper.find('[data-testid="stage-path"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('访前目标')
    expect(wrapper.text()).toContain('证据装配')
    expect(wrapper.text()).toContain('访前包预览')
    expect(wrapper.text()).toContain('会中工作区')
  })
})
