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
      { path: '/accounts/portfolio', name: 'PortfolioBoard', component: { template: '<div/>' } },
      { path: '/commitments', name: 'CommitmentDashboard', component: { template: '<div/>' } },
      { path: '/signals', name: 'SignalsHome', component: { template: '<div/>' } },
      { path: '/engagement', name: 'EngagementWorkspace', component: { template: '<div/>' } },
      { path: '/engagement/crm-writeback', name: 'CrmWriteback', component: { template: '<div/>' } },
      { path: '/needs', name: 'NeedsHome', component: { template: '<div/>' } },
      { path: '/product-center', name: 'ProductCenter', component: { template: '<div/>' } },
      { path: '/product-center/:productId?', name: 'ProductCenterDetail', component: { template: '<div/>' } },
      { path: '/recommendation/new', name: 'RecommendationNew', component: { template: '<div/>' } },
      { path: '/proposals', name: 'ProposalsHome', component: { template: '<div/>' } },
      { path: '/approvals', name: 'ApprovalsHome', component: { template: '<div/>' } },
      { path: '/audit-trace', name: 'AuditTrace', component: { template: '<div/>' } },
      { path: '/analytics/operating-metrics', name: 'AnalyticsOperatingMetrics', component: { template: '<div/>' } },
      { path: '/analytics/segments', name: 'AnalyticsSegments', component: { template: '<div/>' } },
      { path: '/analytics/combo-query', name: 'AnalyticsComboQuery', component: { template: '<div/>' } },
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

describe('AppSidebar V8.1', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the V8.1 five navigation groups', async () => {
    const { wrapper } = await mountSidebar()
    // V8.1: 五组菜单——经营/客户/产品/方案/分析
    expect(SHELL_NAV_GROUPS.map(group => group.label)).toEqual([
      '经营',
      '客户',
      '产品',
      '方案',
      '分析',
    ])
    // 五个组名常驻
    for (const label of ['经营', '客户', '产品', '方案', '分析']) {
      expect(wrapper.text()).toContain(label)
    }
    // 当前域（经营）所在组自动展开，故其子项可见
    expect(wrapper.text()).toContain('经营总览')
    expect(wrapper.text()).toContain('承诺事项')
    expect(wrapper.text()).toContain('经营旅程')
    expect(wrapper.text()).toContain('CRM 回写')
    expect(wrapper.text()).toContain('审计追踪')
    // 其余组默认折叠（AppSidebar.vue:14-20 自动展开当前激活组），
    // 因此「菜单项完整性」在数据层断言，渲染层由下面的展开用例覆盖
    const labels = SHELL_NAV_ITEMS.map(item => item.label)
    for (const label of [
      '客户组合',
      '组合看板',
      '经营信号',
      '产品解读',
      '受控推荐',
      '建议书',
      '审批中心',
      '经营指标',
      '客户分群',
      '组合查询',
    ]) {
      expect(labels).toContain(label)
    }
    // 不包含阶段页面
    expect(wrapper.text()).not.toContain('访前路径')
    expect(wrapper.text()).not.toContain('移动端（降级）')
  })

  it('keeps core routes and does not put stage pages in L1', () => {
    const tos = SHELL_NAV_ITEMS.map(item => item.to)
    expect(tos).toContain('/workbench')
    expect(tos).toContain('/commitments')
    expect(tos).toContain('/accounts')
    expect(tos).toContain('/engagement')
    expect(tos).toContain('/product-center')
    expect(tos).toContain('/proposals')
    expect(tos).toContain('/audit-trace')
    expect(tos).toContain('/engagement/crm-writeback')
    expect(tos).toContain('/accounts/portfolio')
    // 阶段页面不在 L1
    expect(tos).not.toContain('/in-meeting')
    expect(tos).not.toContain('/m/today')
    expect(tos).not.toContain('/external-events')
  })

  it('selects correct domain for key routes', () => {
    expect(navDomainForPath('/accounts')).toBe('accounts')
    expect(navDomainForPath('/accounts/portfolio')).toBe('portfolio')
    expect(navDomainForPath('/customers/CUST-1')).toBe('panorama')
    expect(navDomainForPath('/engagement/previsit/gaps')).toBe('journeys')
    expect(navDomainForPath('/m/today')).toBe('workbench')
    expect(navDomainForPath('/audit-trace')).toBe('audit')
    expect(navDomainForPath('/engagement/crm-writeback')).toBe('crm-writeback')
  })

  /** 展开指定分组（默认只展开当前激活域所在组）。 */
  async function expand(wrapper: Awaited<ReturnType<typeof mountSidebar>>['wrapper'], groupKey: string) {
    await wrapper.get(`[data-testid="nav-group-${groupKey}"]`).trigger('click')
    await flushPromises()
  }

  it('navigates 客户组合 from the side nav', async () => {
    const { wrapper, router } = await mountSidebar()
    await expand(wrapper, 'client')
    await wrapper.get('[data-testid="nav-item-portfolio"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/accounts')
  })

  it('opens 经营信号 from the side nav', async () => {
    const { wrapper, router } = await mountSidebar()
    await expand(wrapper, 'client')
    await wrapper.get('[data-testid="nav-item-signals"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/signals')
  })

  it('opens 审计追踪 from the side nav', async () => {
    const { wrapper, router } = await mountSidebar()
    // 审计追踪在经营组
    await wrapper.get('[data-testid="nav-item-audit-trace"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/audit-trace')
  })

  it('only highlights the active analytics item, not siblings', async () => {
    const { wrapper } = await mountSidebar('/analytics/combo-query')
    await flushPromises()
    // "分析"组应已自动展开（watch activeDomain → add group key）
    // 确认展开状态
    const groupHeader = wrapper.get('[data-testid="nav-group-analytics"]')
    expect(groupHeader.attributes('aria-expanded')).toBe('true')
    // 只有"组合查询"激活
    const comboItem = wrapper.get('[data-testid="nav-item-analytics-combo"]')
    expect(comboItem.classes()).toContain('nav-item--active')
    // "经营指标"和"客户分群"不应同时激活
    const metricsItem = wrapper.get('[data-testid="nav-item-analytics-operating-metrics"]')
    const segmentsItem = wrapper.get('[data-testid="nav-item-analytics-segments"]')
    expect(metricsItem.classes()).not.toContain('nav-item--active')
    expect(segmentsItem.classes()).not.toContain('nav-item--active')
  })
})
