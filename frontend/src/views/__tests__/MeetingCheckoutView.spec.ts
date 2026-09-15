import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import MeetingCheckoutView from '../MeetingCheckoutView.vue'
import type { HumanGate } from '../../api/v11'

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchHumanGates: vi.fn(),
    decideHumanGate: vi.fn(),
  }
})

const exitGate: HumanGate = {
  gateId: 'exit-1',
  gateType: 'E01_EXIT_CONFIRM',
  journeyId: 'j1',
  status: 'PENDING',
  subject: '离场确认',
  createdAt: '2026-08-25T00:00:00Z',
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

async function mountP17() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/in-meeting/:id/checkout', name: 'MeetingCheckout', component: MeetingCheckoutView }],
  })
  await router.push('/in-meeting/j1/checkout')
  const wrapper = mount(MeetingCheckoutView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P17 MeetingCheckoutView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully with a draft checklist', async () => {
    const { fetchHumanGates } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([exitGate])
    const wrapper = await mountP17()
    expect(wrapper.get('[data-testid="p17-meeting-checkout"]').text()).toContain('离场确认')
    expect(wrapper.text()).toMatch(/双方确认/)
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when the checklist has no confirmed items', async () => {
    const { fetchHumanGates } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP17()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/草稿/)
  })

  it('shows error four-state when human-gate load fails', async () => {
    const { fetchHumanGates } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('gate down'))
    const wrapper = await mountP17()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('enables 结束会谈 only when E01_EXIT_CONFIRM is pending, otherwise disables', async () => {
    const { fetchHumanGates, decideHumanGate } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([exitGate])
    ;(decideHumanGate as ReturnType<typeof vi.fn>).mockResolvedValue({ ...exitGate, status: 'APPROVED' })
    const wrapper = await mountP17()
    const endBtn = wrapper.get('[data-testid="p17-end-meeting"]')
    expect((endBtn.element as HTMLButtonElement).disabled).toBe(false)
    await endBtn.trigger('click')
    await flushPromises()
    expect(decideHumanGate as ReturnType<typeof vi.fn>).toHaveBeenCalled()
  })

  it('disables 结束会谈 when E01_EXIT_CONFIRM is absent', async () => {
    const { fetchHumanGates } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP17()
    expect((wrapper.get('[data-testid="p17-end-meeting"]').element as HTMLButtonElement).disabled).toBe(true)
  })
})
