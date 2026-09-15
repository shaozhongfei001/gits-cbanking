import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import PortfolioBoardView from '../PortfolioBoardView.vue'
import type { Customer } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
  }
})

const mockCustomers: Customer[] = [
  {
    customerId: 'c1',
    customerName: '企业A',
    customerTier: 'STRATEGIC',
    riskLevel: 'HIGH',
  },
  {
    customerId: 'c2',
    customerName: '企业B',
    customerTier: 'GROWTH',
    riskLevel: 'LOW',
  },
]

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled" v-bind="$attrs"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
}

describe('P03 PortfolioBoardView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('renders read-only columns from existing customerTier values', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/accounts/portfolio', name: 'PortfolioBoard', component: PortfolioBoardView },
        { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
      ],
    })
    const wrapper = mount(PortfolioBoardView, { global: { plugins: [router], stubs } })
    await flushPromises()
    expect(wrapper.get('[data-testid="p03-portfolio"]').text()).toContain('客户组合 Portfolio')
    expect(wrapper.find('[data-testid="tier-column-STRATEGIC"]').text()).toContain('企业A')
    expect(wrapper.find('[data-testid="tier-column-GROWTH"]').text()).toContain('企业B')
    expect(wrapper.get('[data-testid="tier-card"]').attributes('draggable')).toBe('false')
  })

  it('keeps the tier write button disabled with C2 reason', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/accounts/portfolio', component: PortfolioBoardView }],
    })
    const wrapper = mount(PortfolioBoardView, { global: { plugins: [router], stubs } })
    await flushPromises()
    const writeButton = wrapper.get('[data-testid="tier-write-action"]')
    expect((writeButton.element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toContain('C2')
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toContain('待合同批准')
  })
})
