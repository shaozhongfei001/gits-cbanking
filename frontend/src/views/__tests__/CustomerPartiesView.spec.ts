import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CustomerPartiesView from '../CustomerPartiesView.vue'
import type { Customer } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomer: vi.fn(),
  }
})

const mockCustomer: Customer = {
  customerId: 'c1',
  customerName: '企业A',
  rmName: '张经理',
  managingBranch: '杭州分行',
  relationshipSummary: '长期合作，关键联系人由客户经理维护',
  coreTags: ['战略'],
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

async function mountP07() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
      { path: '/customers/:id/group', name: 'CustomerGroupView', component: { template: '<div/>' } },
      { path: '/customers/:id/funds', name: 'CustomerFundsView', component: { template: '<div/>' } },
      { path: '/customers/:id/parties', name: 'CustomerPartiesView', component: CustomerPartiesView },
    ],
  })
  await router.push('/customers/c1/parties')
  const wrapper = mount(CustomerPartiesView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P07 CustomerPartiesView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully using existing Customer relationship fields', async () => {
    const { fetchCustomer } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    const wrapper = await mountP07()
    expect(wrapper.get('[data-testid="p07-parties"]').text()).toContain('客户 Account')
    expect(wrapper.text()).toContain('张经理')
    expect(wrapper.text()).toContain('长期合作')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when relationship summary is absent', async () => {
    const { fetchCustomer } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue({
      customerId: 'c1',
      customerName: '企业A',
    })
    const wrapper = await mountP07()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchCustomer fails', async () => {
    const { fetchCustomer } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('not found'))
    const wrapper = await mountP07()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables 请求引荐', async () => {
    const { fetchCustomer } = await import('../../api/engagement')
    ;(fetchCustomer as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomer)
    const wrapper = await mountP07()
    expect(wrapper.text()).toContain('请求引荐')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })
})
