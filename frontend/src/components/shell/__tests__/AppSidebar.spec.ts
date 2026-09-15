import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import AppSidebar from '../AppSidebar.vue'
import { SHELL_NAV_GROUPS, SHELL_NAV_ITEMS, navDomainForPath } from '../../../layouts/navConfig'

vi.mock('../../../api/v11', () => ({
  fetchCommitments: vi.fn().mockResolvedValue([]),
}))

vi.mock('../../../api/engagement', () => ({
  fetchCustomers: vi.fn().mockResolvedValue([]),
  fetchOperatingView: vi.fn().mockResolvedValue({
    customer: { customerId: 'x', customerName: 'x' },
    entities: [],
    groupRelationships: [],
    creditFacilities: [],
  }),
}))

async function mountSidebar(path = '/workbench') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/workbench', name: 'Workbench', component: { template: '<div/>' } },
      { path: '/accounts', name: 'AccountsHome', component: { template: '<div/>' } },
      { path: '/commitments', name: 'CommitmentDashboard', component: { template: '<div/>' } },
      { path: '/signals', name: 'SignalsHome', component: { template: '<div/>' } },
      { path: '/engagement', name: 'EngagementWorkspace', component: { template: '<div/>' } },
      { path: '/needs', name: 'NeedsHome', component: { template: '<div/>' } },
      { path: '/proposals', name: 'ProposalsHome', component: { template: '<div/>' } },
      { path: '/collab', name: 'CollabHome', component: { template: '<div/>' } },
      { path: '/account-plans', name: 'AccountPlansHome', component: { template: '<div/>' } },
      { path: '/claims', name: 'ClaimsHome', component: { template: '<div/>' } },
      { path: '/approvals', name: 'ApprovalsHome', component: { template: '<div/>' } },
      { path: '/customers/:id/group', name: 'CustomerGroupView', component: { template: '<div/>' } },
      { path: '/customers/:id', name: 'CustomerOperatingView', component: { template: '<div/>' } },
    ],
  })
  await router.push(path)
  await router.isReady()
  const wrapper = mount(AppSidebar, { global: { plugins: [router] } })
  await flushPromises()
  return { wrapper, router }
}

describe('AppSidebar V3.2 L1', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the four V3.2 groups and eleven stable domains', async () => {
    const { wrapper } = await mountSidebar()
    expect(SHELL_NAV_GROUPS.map(group => group.label)).toEqual([
      '日常作业',
      '客户经营',
      '方案与交付',
      '知识与治理',
    ])
    expect(SHELL_NAV_ITEMS).toHaveLength(12)
    expect(wrapper.text()).toContain('客户经营作战台')
    expect(wrapper.text()).toContain('我的任务与承诺')
    expect(wrapper.text()).toContain('客户组合')
    expect(wrapper.text()).toContain('客户全景')
    expect(wrapper.text()).toContain('信号与互动')
    expect(wrapper.text()).toContain('需求与机会')
    expect(wrapper.text()).toContain('服务建议书')
    expect(wrapper.text()).toContain('产品推荐')
    expect(wrapper.text()).toContain('专家协同')
    expect(wrapper.text()).toContain('账户计划与价值')
    expect(wrapper.text()).toContain('产品解读与知识')
    expect(wrapper.text()).toContain('审批与审计')
    expect(wrapper.text()).not.toContain('访前路径')
    expect(wrapper.text()).not.toContain('移动端（降级）')
    expect(wrapper.get('[data-testid="shell-brand"]').text()).toContain('GITS Bank')
    expect(wrapper.get('[data-testid="shell-brand"]').text()).toContain('对公客户经营工作台')
  })

  it('keeps /commitments in 日常作业 and does not put stage pages in L1', () => {
    const tos = SHELL_NAV_ITEMS.map(item => item.to)
    expect(tos).toContain('/workbench')
    expect(tos).toContain('/commitments')
    expect(tos).toContain('/accounts')
    expect(tos).toContain('/engagement')
    expect(tos).toContain('/needs')
    expect(tos).toContain('/proposals')
    expect(tos).not.toContain('/in-meeting')
    expect(tos).not.toContain('/m/today')
    expect(tos).not.toContain('/external-events')
    expect(tos).not.toContain('/accounts/portfolio')
  })

  it('selects 客户组合 on portfolio and 客户全景 on customer record', () => {
    expect(navDomainForPath('/accounts')).toBe('accounts')
    expect(navDomainForPath('/accounts/portfolio')).toBe('accounts')
    expect(navDomainForPath('/customers/CUST-1')).toBe('panorama')
    expect(navDomainForPath('/engagement/previsit/gaps')).toBe('signals')
    expect(navDomainForPath('/m/today')).toBe('workbench')
  })

  it('navigates 客户组合 from the side nav', async () => {
    const { wrapper, router } = await mountSidebar()
    await wrapper.get('[data-testid="nav-item-portfolio"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/accounts')
  })

  it('opens the first customer from 客户全景 when no workspace tab exists', async () => {
    const { fetchCustomers, fetchOperatingView } = await import('../../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([{ customerId: 'CUST-1', customerName: '测试企业A' }])
    ;(fetchOperatingView as ReturnType<typeof vi.fn>).mockResolvedValue({
      customer: { customerId: 'CUST-1', customerName: '测试企业A' },
      entities: [{ entityId: 'ENT-1', name: '测试企业A', role: '集团本部/母公司' }],
      groupRelationships: [],
      creditFacilities: [],
    })
    const { wrapper, router } = await mountSidebar()
    await wrapper.get('[data-testid="nav-item-panorama"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/customers/CUST-1/group')
  })

  it('opens 客户经营旅程 from L1 信号与互动', async () => {
    const { wrapper, router } = await mountSidebar()
    await wrapper.get('[data-testid="nav-item-signals"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/engagement')
  })
})
