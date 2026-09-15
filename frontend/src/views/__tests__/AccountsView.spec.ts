import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import AccountsView from '../AccountsView.vue'
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
    industry: 'MANUFACTURING',
    enterpriseScale: 'LARGE',
    customerTier: 'STRATEGIC',
    riskLevel: 'HIGH',
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
  NInput: {
    props: ['value'],
    template: '<input data-testid="p02-filter" :value="value" @input="$emit(\'update:value\', $event.target.value)" />',
  },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NCard: { template: '<div class="n-card" @click="$emit(\'click\')"><slot /></div>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
}

describe('P02 AccountsView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('loads customers via fetchCustomers and shows object context', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/accounts', name: 'AccountsHome', component: AccountsView },
        { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
      ],
    })
    const wrapper = mount(AccountsView, { global: { plugins: [router], stubs } })
    await flushPromises()
    expect(fetchCustomers).toHaveBeenCalled()
    expect(wrapper.get('[data-testid="p02-accounts"]').text()).toContain('客户 Account')
    expect(wrapper.text()).toContain('企业A')
  })

  it('disables import write action', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/accounts', component: AccountsView }],
    })
    const wrapper = mount(AccountsView, { global: { plugins: [router], stubs } })
    await flushPromises()
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.text()).toContain('导入名单')
  })

  it('shows error state when listCustomers fails', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('forbidden'))
    setActivePinia(createPinia())
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/accounts', component: AccountsView }],
    })
    const wrapper = mount(AccountsView, { global: { plugins: [router], stubs } })
    await flushPromises()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })
})
