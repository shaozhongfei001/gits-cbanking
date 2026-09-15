import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CustomerGroupView from '../CustomerGroupView.vue'
import type { CustomerOperatingViewPayload, SupplyChainGraphReport } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchOperatingView: vi.fn(),
    executeSupplyChainGraph: vi.fn(),
  }
})

vi.mock('../../components/SupplyChainForceGraph.vue', () => ({
  default: {
    name: 'SupplyChainForceGraph',
    props: ['nodes', 'edges', 'compact'],
    template: '<div class="mock-sc-graph">{{ nodes?.length || 0 }} nodes</div>',
  },
}))

const mockView: CustomerOperatingViewPayload = {
  customer: {
    customerId: 'c1',
    customerName: '企业A',
    groupFlag: true,
    relationshipSummary: '集团核心成员',
    listedStatus: 'LISTED',
  },
  entities: [],
  groupRelationships: [],
  creditFacilities: [{ facilityId: 'FAC-1', borrowerEntity: '企业A' }],
}

const dkwsGraph: SupplyChainGraphReport = {
  requestId: 'SCG-1',
  customerId: 'c1',
  customerName: '企业A',
  result: {
    nodes: [
      { id: 'n1', name: '华东精工', layer: 'enterprise' },
      { id: 'n2', name: '上游钢厂', layer: 'supplier' },
    ],
    edges: [{ source: 'n2', target: 'n1', relation: 'purchase' }],
  },
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

async function mountP05() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
      { path: '/customers/:id/group', name: 'CustomerGroupView', component: CustomerGroupView },
      { path: '/customers/:id/funds', name: 'CustomerFundsView', component: { template: '<div/>' } },
      { path: '/customers/:id/parties', name: 'CustomerPartiesView', component: { template: '<div/>' } },
    ],
  })
  await router.push('/customers/c1/group')
  const wrapper = mount(CustomerGroupView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P05 CustomerGroupView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('renders the DKWS knowledge graph when Skill returns nodes', async () => {
    const { fetchOperatingView, executeSupplyChainGraph } = await import('../../api/engagement')
    ;(fetchOperatingView as ReturnType<typeof vi.fn>).mockResolvedValue(mockView)
    ;(executeSupplyChainGraph as ReturnType<typeof vi.fn>).mockResolvedValue(dkwsGraph)
    const wrapper = await mountP05()
    expect(wrapper.get('[data-testid="p05-group"]').text()).toContain('客户 Account')
    expect(wrapper.find('[data-testid="p05-group-graph"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="p05-member-table"]').text()).toContain('上游钢厂')
    expect(wrapper.get('[data-testid="p05-metrics"]').text()).toContain('图谱节点')
    expect(wrapper.text()).not.toContain('董事长')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows DKWS empty state instead of H2 seed edges', async () => {
    const { fetchOperatingView, executeSupplyChainGraph } = await import('../../api/engagement')
    ;(fetchOperatingView as ReturnType<typeof vi.fn>).mockResolvedValue(mockView)
    ;(executeSupplyChainGraph as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('DKWS down'))
    const wrapper = await mountP05()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="p05-empty-graph"]').text()).toMatch(/DKWS/)
    expect(wrapper.text()).not.toContain('智能制造子公司')
  })

  it('shows error four-state when fetchOperatingView fails', async () => {
    const { fetchOperatingView } = await import('../../api/engagement')
    ;(fetchOperatingView as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('forbidden'))
    const wrapper = await mountP05()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables 发起核验 with C2 reason', async () => {
    const { fetchOperatingView, executeSupplyChainGraph } = await import('../../api/engagement')
    ;(fetchOperatingView as ReturnType<typeof vi.fn>).mockResolvedValue(mockView)
    ;(executeSupplyChainGraph as ReturnType<typeof vi.fn>).mockResolvedValue(dkwsGraph)
    const wrapper = await mountP05()
    expect(wrapper.text()).toContain('发起核验')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/C2|合同|解除路径/)
  })
})
