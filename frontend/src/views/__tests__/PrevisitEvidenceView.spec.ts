import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import PrevisitEvidenceView from '../PrevisitEvidenceView.vue'
import { usePrevisitStore } from '../../stores/previsit'
import type { PreparedPrevisitResponse } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    preparePrevisit: vi.fn(),
  }
})

vi.mock('naive-ui', async () => {
  const actual = await vi.importActual<typeof import('naive-ui')>('naive-ui')
  return {
    ...actual,
    useMessage: () => ({ success: vi.fn(), error: vi.fn(), warning: vi.fn() }),
  }
})

const mockTrace = [
  { stepId: 's1', phase: '读图', kiId: 'KI-FRONT-001', status: 'done', message: '读取企业基本信息' },
  { stepId: 's2', phase: '装配', kiId: 'KI-FRONT-002', status: 'done', message: '装配行业风险' },
  { stepId: 's3', phase: '生成', kiId: '', status: 'skipped', message: '跳过：无供应链数据' },
]

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
  assemblyTrace: mockTrace,
  skillSections: [],
}

const stubs = {
  ObjectHeader: { template: '<div class="object-header-stub"><slot /><slot name="actions" /></div>' },
  PageState: {
    props: ['status', 'error', 'idleDescription'],
    template: '<div class="page-state-stub" :data-status="status"><slot /><slot name="default" /></div>',
  },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
}

async function mountP13(
  query: Record<string, string> = { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' },
  seed?: (store: ReturnType<typeof usePrevisitStore>) => void,
) {
  setActivePinia(createPinia())
  if (seed) {
    seed(usePrevisitStore())
  }
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/engagement/previsit/evidence', name: 'PrevisitEvidence', component: PrevisitEvidenceView },
      { path: '/engagement/previsit/pack', name: 'PrevisitPack', component: { template: '<div />' } },
    ],
  })
  await router.push({ path: '/engagement/previsit/evidence', query })
  const wrapper = mount(PrevisitEvidenceView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P13 PrevisitEvidenceView', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.clearAllMocks()
  })

  it('renders page shell with correct data-testid', async () => {
    const { wrapper } = await mountP13()
    expect(wrapper.find('[data-testid="p13-previsit-evidence"]').exists()).toBe(true)
  })

  it('does NOT auto-call preparePrevisit on mount', async () => {
    const { preparePrevisit } = await import('../../api/engagement')
    await mountP13()
    expect(preparePrevisit as ReturnType<typeof vi.fn>).not.toHaveBeenCalled()
  })

  it('shows empty state when previsit not yet generated', async () => {
    const { wrapper } = await mountP13()
    expect(wrapper.find('[data-testid="p13-empty"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/尚未执行一键访前/)
  })

  it('shows assembly trace when previsit is done', async () => {
    const { wrapper } = await mountP13(
      { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' },
      (store) => {
        store.setContext({ journeyId: 'j1', operatingCaseId: 'oc1', customerId: 'c1', rmId: 'rm1' })
        store.previsitResult = mockPack
        store.running = true
      },
    )
    expect(wrapper.find('[data-testid="p13-trace-list"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('读图')
    expect(wrapper.text()).toContain('KI-FRONT-001')
    expect(wrapper.text()).toContain('跳过')
  })

  it('shows derived sources when previsit is done', async () => {
    const { wrapper } = await mountP13(
      { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' },
      (store) => {
        store.setContext({ journeyId: 'j1', operatingCaseId: 'oc1', customerId: 'c1', rmId: 'rm1' })
        store.previsitResult = mockPack
        store.running = true
      },
    )
    expect(wrapper.find('[data-testid="p13-source-list"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('外联脚本')
    expect(wrapper.text()).toContain('会面脚本')
  })

  it('has navigation button to P14 with correct data-testid', async () => {
    const { wrapper } = await mountP13(
      { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' },
      (store) => {
        store.setContext({ journeyId: 'j1', operatingCaseId: 'oc1', customerId: 'c1', rmId: 'rm1' })
        store.previsitResult = mockPack
        store.running = true
      },
    )
    const btn = wrapper.find('[data-testid="p13-go-pack"]')
    expect(btn.exists()).toBe(true)
    expect(btn.text()).toMatch(/去访前包预览/)
  })

  it('disables generate button when context is missing', async () => {
    const { wrapper } = await mountP13({})
    const btn = wrapper.find('[data-testid="p13-generate-pack"]')
    expect((btn.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('generate button calls store.runPrevisit when clicked', async () => {
    const { wrapper } = await mountP13(
      { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' },
      (store) => {
        store.setContext({ journeyId: 'j1', operatingCaseId: 'oc1', customerId: 'c1', rmId: 'rm1' })
        vi.spyOn(store, 'runPrevisit').mockResolvedValue(mockPack)
      },
    )
    const btn = wrapper.find('[data-testid="p13-generate-pack"]')
    expect((btn.element as HTMLButtonElement).disabled).toBe(false)
    await btn.trigger('click')
    await flushPromises()
    const store = usePrevisitStore()
    expect(store.runPrevisit).toHaveBeenCalledWith('访前调研')
  })
})
