import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import EngagementsView from '../EngagementsView.vue'
import type { ListedInteraction } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    listInteractions: vi.fn(),
    fetchCustomers: vi.fn(),
    fetchCustomerJourneys: vi.fn(),
  }
})

const mockItems: ListedInteraction[] = [
  {
    interactionId: 'int-1',
    customerId: 'c1',
    channel: 'PHONE',
    summary: '例行回访',
    interactionDate: '2026-08-01T00:00:00Z',
  },
]

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NInput: {
    props: ['value'],
    template: '<input data-testid="p10-filter" :value="value" @input="$emit(\'update:value\', $event.target.value)" />',
  },
}

async function mountP10() {
  const { fetchCustomers, fetchCustomerJourneys } = await import('../../api/engagement')
  ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([
    { customerId: 'c1', customerName: '企业A' },
  ])
  ;(fetchCustomerJourneys as ReturnType<typeof vi.fn>).mockResolvedValue([])
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/engagements', name: 'EngagementsHome', component: EngagementsView },
      { path: '/engagement', name: 'EngagementWorkspace', component: { template: '<div/>' } },
    ],
  })
  await router.push('/engagements')
  const wrapper = mount(EngagementsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P10 EngagementsView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully via listInteractions', async () => {
    const { listInteractions } = await import('../../api/engagement')
    ;(listInteractions as ReturnType<typeof vi.fn>).mockResolvedValue(mockItems)
    const { wrapper } = await mountP10()
    expect(wrapper.get('[data-testid="p10-engagements"]').text()).toContain('互动')
    expect(wrapper.text()).toContain('例行回访')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when the interaction list is empty', async () => {
    const { listInteractions } = await import('../../api/engagement')
    ;(listInteractions as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP10()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when listInteractions fails', async () => {
    const { listInteractions } = await import('../../api/engagement')
    ;(listInteractions as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('upstream'))
    const { wrapper } = await mountP10()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables 同步日历', async () => {
    const { listInteractions } = await import('../../api/engagement')
    ;(listInteractions as ReturnType<typeof vi.fn>).mockResolvedValue(mockItems)
    const { wrapper } = await mountP10()
    expect(wrapper.text()).toContain('同步日历')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })

  it('links to the P11 journey workspace without starting a write', async () => {
    const { listInteractions } = await import('../../api/engagement')
    ;(listInteractions as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { wrapper } = await mountP10()
    expect(wrapper.get('[data-testid="p10-open-journey"]').attributes('href')).toBe('/engagement')
  })

  it('opens the journey workspace with customerId when a row is clicked', async () => {
    const { listInteractions } = await import('../../api/engagement')
    ;(listInteractions as ReturnType<typeof vi.fn>).mockResolvedValue(mockItems)
    const { wrapper } = await mountP10()
    expect(wrapper.get('[data-testid="p10-interaction-row"]').attributes('href')).toBe('/engagement?customerId=c1')
  })
})
