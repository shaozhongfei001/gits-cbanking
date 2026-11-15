import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, enableAutoUnmount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import InMeetingAssistant from '../InMeetingAssistant.vue'
import type { HumanGate } from '../../api/v11'

enableAutoUnmount(afterEach)

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchHumanGates: vi.fn(),
    fetchCrmWritebackCommands: vi.fn(),
    decideHumanGate: vi.fn(),
    decideCrmWritebackCommand: vi.fn(),
  }
})

const mockGate: HumanGate = {
  gateId: 'g1',
  gateType: 'C01_PREVISIT_APPROVE',
  status: 'PENDING',
  subject: '访前包待确认',
  createdAt: '2026-08-25T00:00:00Z',
}

const stubs = {
  NSpin: { template: '<div class="n-spin"><slot /></div>' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { props: ['description'], template: '<div class="n-empty">{{ description }}</div>' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NLayout: { template: '<div class="n-layout"><slot /></div>' },
  NLayoutSider: { template: '<div class="n-sider"><slot /></div>' },
  NLayoutContent: { template: '<div class="n-content"><slot /></div>' },
  NCard: { template: '<div class="n-card"><slot name="header" /><slot /><slot name="header-extra" /></div>' },
  NTabs: { template: '<div class="n-tabs"><slot /></div>' },
  NTabPane: { template: '<div class="n-tab-pane"><slot /></div>' },
  NSpace: { template: '<div class="n-space"><slot /></div>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  NInput: { template: '<textarea class="n-input" />' },
  NAlert: { template: '<div class="n-alert" />' },
  NBadge: { template: '<span class="n-badge"><slot /></span>' },
  NDivider: { template: '<hr />' },
  HumanGateDialog: { template: '<div />' },
  CrmWritebackApproval: { template: '<div />' },
}

async function mountP15(path = '/in-meeting/j1') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/in-meeting/:id?', name: 'InMeetingAssistant', component: InMeetingAssistant },
      { path: '/in-meeting/:id/capture', name: 'MeetingCapture', component: { template: '<div/>' } },
      { path: '/in-meeting/:id/checkout', name: 'MeetingCheckout', component: { template: '<div/>' } },
    ],
  })
  await router.push(path)
  const wrapper = mount(InMeetingAssistant, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P15 InMeetingAssistant', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully with object context', async () => {
    const { fetchHumanGates, fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([mockGate])
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP15()
    expect(wrapper.get('[data-testid="p15-in-meeting"]').text()).toContain('会中工作区')
    expect(wrapper.text()).toContain('互动 Interaction')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when no pending gates exist', async () => {
    const { fetchHumanGates, fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP15()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when human-gate load fails', async () => {
    const { fetchHumanGates, fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('gate down'))
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP15()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables recording a formal Claim from the meeting workspace', async () => {
    const { fetchHumanGates, fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP15()
    const claimBtn = wrapper.findAll('button').find((b) => b.text().includes('记为正式 Claim'))
    expect(claimBtn).toBeTruthy()
    expect((claimBtn!.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('uses interpretation wording instead of recording wording', async () => {
    const { fetchHumanGates, fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP15()
    expect(wrapper.text()).toContain('未解读')
    expect(wrapper.text()).toContain('开始解读')
    expect(wrapper.text()).not.toContain('录音')

    const toggle = wrapper.findAll('button').find((b) => b.text().includes('开始解读'))
    expect(toggle).toBeTruthy()
    await toggle!.trigger('click')
    expect(wrapper.text()).toContain('解读中')
    expect(wrapper.text()).toContain('停止解读')
  })

  it('renders pre-generated RM and customer dialogue in the meeting-notes tab', async () => {
    const { fetchHumanGates, fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP15()
    expect(wrapper.find('[data-testid="p15-meeting-dialogue"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid^="p15-turn-"]')).toHaveLength(10)
    expect(wrapper.text()).toContain('演示样例 · 预生成对话')
    expect(wrapper.text()).toContain('客户经理')
    expect(wrapper.findAll('.dialogue-turn.is-customer').length).toBeGreaterThan(0)
    expect(wrapper.findAll('.dialogue-turn.is-rm').length).toBeGreaterThan(0)
  })

  it('keeps the four-state page stable during the 5s silent refresh', async () => {
    // 只 fake interval：flushPromises 依赖的真实 setTimeout 不受影响。
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    try {
      const { fetchHumanGates, fetchCrmWritebackCommands } = await import('../../api/v11')
      ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
      ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
      const { wrapper } = await mountP15()
      await flushPromises()
      expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)

      const callsBefore = (fetchHumanGates as ReturnType<typeof vi.fn>).mock.calls.length
      await vi.advanceTimersByTimeAsync(5000)
      await flushPromises()

      // 后台仍刷新，但整页不得回到 loading/spinner（刷屏根因的回归护栏）。
      expect((fetchHumanGates as ReturnType<typeof vi.fn>).mock.calls.length).toBeGreaterThan(callsBefore)
      expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="loading-state"]').exists()).toBe(false)
      expect(wrapper.find('[data-testid="p15-refresh-failed"]').exists()).toBe(false)
    } finally {
      vi.useRealTimers()
    }
  })
})
