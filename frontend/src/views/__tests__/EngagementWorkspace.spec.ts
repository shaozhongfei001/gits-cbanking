import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import EngagementWorkspace from '../EngagementWorkspace.vue'
import type { Customer } from '../../api/engagement'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('../../api/engagement', () => ({
  fetchCustomers: vi.fn(),
  reloadCrmCustomerMaster: vi.fn(),
  upsertCrmCustomer: vi.fn(),
  generateOutreachScript: vi.fn(),
  generateMeetingScript: vi.fn(),
  executePrevisit: vi.fn(),
  executePostvisit: vi.fn(),
  startJourney: vi.fn(),
  handleNewEvidence: vi.fn(),
  completeJourney: vi.fn(),
  executeSupplyChainGraph: vi.fn(),
  preparePrevisit: vi.fn(),
}))

vi.mock('naive-ui', async () => {
  const actual = await vi.importActual('naive-ui')
  return {
    ...actual,
    useMessage: () => ({
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    }),
  }
})

const mockCustomers: Customer[] = [
  { customerId: 'c1', customerName: '企业A', riskLevel: 'HIGH' },
  { customerId: 'c2', customerName: '企业B', riskLevel: 'LOW' },
]

const stubs = {
  NGrid: { template: '<div class="n-grid"><slot /></div>' },
  NGi: { template: '<div class="n-gi"><slot /></div>' },
  NCard: { template: '<div class="n-card"><slot /></div>' },
  NButton: { template: '<button class="n-button"><slot /></button>' },
  NModal: true,
  NInput: { template: '<input class="n-input" />' },
  NEmpty: { template: '<div class="n-empty" />' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  NDescriptions: { template: '<div class="n-descriptions"><slot /></div>' },
  NDescriptionsItem: { template: '<div class="n-descriptions-item"><slot /></div>' },
  NTable: { template: '<div class="n-table"><slot /></div>' },
  RiskBadge: { template: '<span class="risk-badge">{{ $attrs.level }}</span>' },
}

async function mountWorkspace() {
  const { fetchCustomers, reloadCrmCustomerMaster } = await import('../../api/engagement')
  ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue(mockCustomers)
  ;(reloadCrmCustomerMaster as ReturnType<typeof vi.fn>).mockResolvedValue({
    upsertedCount: 2,
    customerIds: ['c1', 'c2'],
  })

  const wrapper = mount(EngagementWorkspace, {
    global: { stubs },
  })
  await flushPromises()
  return wrapper
}

describe('EngagementWorkspace', () => {
  it('renders page title', async () => {
    const wrapper = await mountWorkspace()
    expect(wrapper.find('h1').text()).toBe('持续经营工作台')
  })

  it('renders spiral flow with start node', async () => {
    const wrapper = await mountWorkspace()
    const nodes = wrapper.findAll('.sp-node')
    // Start, PREVISIT, INTERACTION, POSTVISIT, ITERATE (decision), COMPLETE = 6 nodes
    expect(nodes.length).toBeGreaterThanOrEqual(5)
  })

  it('renders spiral node labels', async () => {
    const wrapper = await mountWorkspace()
    const labels = wrapper.findAll('.sp-label').map(el => el.text())
    expect(labels).toContain('启动旅程')
    expect(labels).toContain('访前准备')
    expect(labels).toContain('互动执行')
    expect(labels).toContain('访后复盘')
    expect(labels).toContain('迭代决策')
    expect(labels).toContain('完成旅程')
  })

  it('start node subtitle is enter-operating, not KYC insight', async () => {
    const wrapper = await mountWorkspace()
    const startSub = wrapper.findAll('.sp-sub')[0]
    expect(startSub.text()).toBe('选择客户，进入经营')
    expect(wrapper.text()).not.toContain('KYC洞察')
  })

  it('renders action panel with 4 actions', async () => {
    const wrapper = await mountWorkspace()
    const actions = wrapper.findAll('.ew-act')
    expect(actions).toHaveLength(4)
  })

  it('renders action titles', async () => {
    const wrapper = await mountWorkspace()
    const titles = wrapper.findAll('.ew-act-title').map(el => el.text())
    expect(titles).toContain('执行访前准备（一键）')
    expect(titles).toContain('执行访后复盘')
    expect(titles).toContain('迭代决策')
    expect(titles).toContain('完成旅程')
  })

  it('marks start node as active when no journey', async () => {
    const wrapper = await mountWorkspace()
    const nodes = wrapper.findAll('.sp-node')
    // First node (START) should be active
    expect(nodes[0].classes()).toContain('active')
  })

  it('action cards are disabled when no journey started', async () => {
    const wrapper = await mountWorkspace()
    const actions = wrapper.findAll('.ew-act')
    // All actions should be disabled (no journey started)
    const disabledActions = actions.filter(a => a.classes().includes('disabled'))
    expect(disabledActions.length).toBe(actions.length)
  })

  it('shows customer select button', async () => {
    const wrapper = await mountWorkspace()
    const buttons = wrapper.findAll('.n-button')
    const selectBtn = buttons.find(b => b.text().includes('选择客户'))
    expect(selectBtn).toBeDefined()
  })

  it('shows refresh customer directory button', async () => {
    const wrapper = await mountWorkspace()
    const buttons = wrapper.findAll('.n-button')
    const refreshBtn = buttons.find(b => b.text().includes('刷新客户目录'))
    expect(refreshBtn).toBeDefined()
  })

  it('refresh directory reloads fixture then re-GETs customers', async () => {
    const wrapper = await mountWorkspace()
    const { fetchCustomers, reloadCrmCustomerMaster } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockClear()
    ;(reloadCrmCustomerMaster as ReturnType<typeof vi.fn>).mockClear()
    const refreshBtn = wrapper.findAll('.n-button').find(b => b.text().includes('刷新客户目录'))
    expect(refreshBtn).toBeDefined()
    await refreshBtn!.trigger('click')
    await flushPromises()
    expect(reloadCrmCustomerMaster).toHaveBeenCalledTimes(1)
    expect(fetchCustomers).toHaveBeenCalledTimes(1)
  })

  it('refresh directory still fetches customers when reload returns 404', async () => {
    const wrapper = await mountWorkspace()
    const { fetchCustomers, reloadCrmCustomerMaster } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockClear()
    ;(reloadCrmCustomerMaster as ReturnType<typeof vi.fn>).mockRejectedValue({ response: { status: 404 } })
    const refreshBtn = wrapper.findAll('.n-button').find(b => b.text().includes('刷新客户目录'))
    await refreshBtn!.trigger('click')
    await flushPromises()
    expect(reloadCrmCustomerMaster).toHaveBeenCalled()
    expect(fetchCustomers).toHaveBeenCalledTimes(1)
  })

  it('renders iteration loop badge', async () => {
    const wrapper = await mountWorkspace()
    const badge = wrapper.find('.sp-loop-badge')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toContain('迭代环')
  })
})
