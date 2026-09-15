import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter, type RouteRecordRaw } from 'vue-router'
import type { Component } from 'vue'
import MobileTodayView from '../MobileTodayView.vue'
import MobilePrevisitView from '../MobilePrevisitView.vue'
import MobileNotesView from '../MobileNotesView.vue'
import MobileCheckoutView from '../MobileCheckoutView.vue'
import { loadMobileDegradeShell, loadTodayActions } from '../../composables/mobileDegrade'
import type { HumanGate } from '../../api/v11'

vi.mock('../../composables/mobileDegrade', async () => {
  const actual = await vi.importActual<typeof import('../../composables/mobileDegrade')>(
    '../../composables/mobileDegrade',
  )
  return {
    ...actual,
    loadMobileDegradeShell: vi.fn(actual.loadMobileDegradeShell),
    loadTodayActions: vi.fn(actual.loadTodayActions),
  }
})

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchHumanGates: vi.fn(),
    decideHumanGate: vi.fn(),
  }
})

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

const exitGate: HumanGate = {
  gateId: 'exit-1',
  gateType: 'E01_EXIT_CONFIRM',
  journeyId: 'j1',
  status: 'PENDING',
  subject: '离场确认',
  createdAt: '2026-08-25T00:00:00Z',
}

const routes: RouteRecordRaw[] = [
  { path: '/m/today', name: 'MobileToday', component: MobileTodayView },
  { path: '/m/previsit', name: 'MobilePrevisit', component: MobilePrevisitView },
  { path: '/m/notes', name: 'MobileNotes', component: MobileNotesView },
  { path: '/m/checkout', name: 'MobileCheckout', component: MobileCheckoutView },
  { path: '/workbench', name: 'Workbench', component: { template: '<div />' } },
  { path: '/commitments', name: 'CommitmentDashboard', component: { template: '<div />' } },
  { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div />' } },
  { path: '/engagement/previsit/pack', name: 'PrevisitPack', component: { template: '<div />' } },
  { path: '/in-meeting/:id?', name: 'InMeetingAssistant', component: { template: '<div />' } },
]

async function mountPage(path: string, component: Component) {
  setActivePinia(createPinia())
  const router = createRouter({ history: createMemoryHistory(), routes })
  await router.push(path)
  const wrapper = mount(component, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P41-P44 mobile C2 degrade shells', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.mocked(loadMobileDegradeShell).mockReset()
    vi.mocked(loadMobileDegradeShell).mockResolvedValue({ empty: true, informal: true })
    vi.mocked(loadTodayActions).mockReset()
    vi.mocked(loadTodayActions).mockResolvedValue([
      { customerId: 'c1', customerName: '企业A', onlinePath: '/customers/c1' },
    ])
  })

  describe('P41', () => {
    it('enters successfully with object header and does not treat the queue as formal tasks', async () => {
      const { wrapper } = await mountPage('/m/today', MobileTodayView)
      expect(wrapper.get('[data-testid="p41-mobile-today"]').text()).toContain('非正式今日行动（C2 降级）')
      expect(wrapper.get('[data-testid="object-header"]').text()).toContain('移动端·今日客户行动')
      expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('企业A')
      expect(wrapper.text()).not.toMatch(/原生 App|Service Worker/)
    })

    it('shows error four-state when today actions fail to load', async () => {
      vi.mocked(loadTodayActions).mockRejectedValueOnce(new Error('upstream'))
      const { wrapper } = await mountPage('/m/today', MobileTodayView)
      expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="retry-action"]').exists()).toBe(true)
    })

    it('shows empty success when there is no online first item', async () => {
      vi.mocked(loadTodayActions).mockResolvedValueOnce([])
      const { wrapper } = await mountPage('/m/today', MobileTodayView)
      expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
      expect(wrapper.get('[data-testid="p41-mobile-today-empty"]').text()).toMatch(/暂无/)
    })

    it('keeps 加入离线队列 disabled with reason and unlock path', async () => {
      const { wrapper } = await mountPage('/m/today', MobileTodayView)
      expect(wrapper.text()).toContain('加入离线队列')
      const button = wrapper.get('[data-testid="gated-action"]')
      expect((button.element as HTMLButtonElement).disabled).toBe(true)
      expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
    })

    it('opens the first item only via an existing online deep link', async () => {
      const { wrapper, router } = await mountPage('/m/today', MobileTodayView)
      const link = wrapper.get('[data-testid="p41-open-first"]')
      expect(link.attributes('href')).toBe('/customers/c1')
      await link.trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.path).toBe('/customers/c1')
    })

    it('falls back to /workbench when there is no first online item', async () => {
      vi.mocked(loadTodayActions).mockResolvedValueOnce([])
      const { wrapper } = await mountPage('/m/today', MobileTodayView)
      expect(wrapper.get('[data-testid="p41-open-first"]').attributes('href')).toBe('/workbench')
    })
  })

  describe('P42', () => {
    it('enters successfully and explains the desktop previsit pack', async () => {
      const { wrapper } = await mountPage('/m/previsit', MobilePrevisitView)
      expect(wrapper.get('[data-testid="p42-mobile-previsit"]').text()).toContain('非正式访前包（C2 降级')
      expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
      expect(wrapper.get('[data-testid="p42-desktop-pack"]').attributes('href')).toBe('/engagement/previsit/pack')
    })

    it('shows error four-state when the shell loader fails', async () => {
      vi.mocked(loadMobileDegradeShell).mockRejectedValueOnce(new Error('upstream'))
      const { wrapper } = await mountPage('/m/previsit', MobilePrevisitView)
      expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="retry-action"]').exists()).toBe(true)
    })

    it('keeps 开始拜访 disabled with reason and unlock path', async () => {
      const { wrapper } = await mountPage('/m/previsit', MobilePrevisitView)
      expect(wrapper.text()).toContain('开始拜访')
      expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
      expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/离线包|缓存/)
    })
  })

  describe('P43', () => {
    it('enters successfully and does not treat drafts as Claims', async () => {
      const { wrapper } = await mountPage('/m/notes', MobileNotesView)
      expect(wrapper.get('[data-testid="p43-mobile-notes"]').text()).toContain('非正式会中速记（C2 降级')
      expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
      expect(wrapper.text()).toMatch(/非正式 Claim|不得当成正式 Claim/)
    })

    it('shows error four-state when the shell loader fails', async () => {
      vi.mocked(loadMobileDegradeShell).mockRejectedValueOnce(new Error('upstream'))
      const { wrapper } = await mountPage('/m/notes', MobileNotesView)
      expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
    })

    it('keeps 新增速记 disabled with reason and unlock path', async () => {
      const { wrapper } = await mountPage('/m/notes', MobileNotesView)
      expect(wrapper.text()).toContain('新增速记')
      expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
      expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
    })
  })

  describe('P44', () => {
    it('enters successfully and disables 完成会谈 when E01_EXIT_CONFIRM is absent', async () => {
      const { fetchHumanGates } = await import('../../api/v11')
      vi.mocked(fetchHumanGates).mockResolvedValue([])
      const { wrapper } = await mountPage('/m/checkout', MobileCheckoutView)
      expect(wrapper.get('[data-testid="p44-mobile-checkout"]').text()).toContain('离场确认')
      expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
      expect((wrapper.get('[data-testid="p44-complete-meeting"]').element as HTMLButtonElement).disabled).toBe(true)
      expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/E01_EXIT_CONFIRM/)
    })

    it('shows error four-state when human-gate load fails', async () => {
      const { fetchHumanGates } = await import('../../api/v11')
      vi.mocked(fetchHumanGates).mockRejectedValue(new Error('gate down'))
      const { wrapper } = await mountPage('/m/checkout', MobileCheckoutView)
      expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
    })

    it('keeps 离线完成会谈 disabled even when an online gate exists', async () => {
      const { fetchHumanGates } = await import('../../api/v11')
      vi.mocked(fetchHumanGates).mockResolvedValue([exitGate])
      const { wrapper } = await mountPage('/m/checkout', MobileCheckoutView)
      expect(wrapper.text()).toContain('离线完成会谈')
      const offline = wrapper.findAll('[data-testid="gated-action"]').find(button => button.text().includes('离线完成会谈'))
      expect(offline).toBeTruthy()
      expect((offline!.element as HTMLButtonElement).disabled).toBe(true)
    })

    it('allows 完成会谈 only via decideHumanGate when E01_EXIT_CONFIRM is pending', async () => {
      const { fetchHumanGates, decideHumanGate } = await import('../../api/v11')
      vi.mocked(fetchHumanGates).mockResolvedValue([exitGate])
      vi.mocked(decideHumanGate).mockResolvedValue({ ...exitGate, status: 'APPROVED' })
      const { wrapper } = await mountPage('/m/checkout', MobileCheckoutView)
      const complete = wrapper.get('[data-testid="p44-complete-meeting"]')
      expect((complete.element as HTMLButtonElement).disabled).toBe(false)
      await complete.trigger('click')
      await flushPromises()
      expect(decideHumanGate).toHaveBeenCalledWith('exit-1', {
        decision: 'APPROVE',
        actorId: 'current-user',
        reason: '离场确认',
      })
    })
  })
})
