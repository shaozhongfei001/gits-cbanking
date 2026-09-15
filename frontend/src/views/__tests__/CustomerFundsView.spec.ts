import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CustomerFundsView from '../CustomerFundsView.vue'
import type { Customer, TransactionRecord } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomer: vi.fn(),
    fetchTransactions: vi.fn(),
  }
})

const mockCustomer: Customer = {
  customerId: 'c1',
  customerName: '企业A',
}

const mockTx: TransactionRecord[] = [
  {
    transactionId: 't1',
    customerId: 'c1',
    amount: 10000,
    currency: 'CNY',
    transactionType: 'DEPOSIT',
    occurredAt: '2026-01-01T00:00:00Z',
    description: '结算入账',
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
}

async function mountP06() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
      { path: '/customers/:id/group', name: 'CustomerGroupView', component: { template: '<div/>' } },
      { path: '/customers/:id/funds', name: 'CustomerFundsView', component: CustomerFundsView },
      { path: '/customers/:id/parties', name: 'CustomerPartiesView', component: { template: '<div/>' } },
    ],
  })
  await router.push('/customers/c1/funds')
  const wrapper = mount(CustomerFundsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P06 CustomerFundsView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully with fetchTransactions', async () => {
    const { fetchCustomer, fetchTransactions } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    ;(fetchTransactions as ReturnType<typeof vi.fn>).mockResolvedValue(mockTx)
    const wrapper = await mountP06()
    expect(wrapper.get('[data-testid="p06-funds"]').text()).toContain('客户 Account')
    expect(wrapper.text()).toContain('结算入账')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when there are no transactions', async () => {
    const { fetchCustomer, fetchTransactions } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    ;(fetchTransactions as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP06()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchTransactions fails', async () => {
    const { fetchCustomer, fetchTransactions } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    ;(fetchTransactions as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('upstream'))
    const wrapper = await mountP06()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables 创建需求 because Need is C3', async () => {
    const { fetchCustomer, fetchTransactions } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    ;(fetchTransactions as ReturnType<typeof vi.fn>).mockResolvedValue(mockTx)
    const wrapper = await mountP06()
    expect(wrapper.text()).toContain('创建需求')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/C3|Need|CCC/)
  })
})
