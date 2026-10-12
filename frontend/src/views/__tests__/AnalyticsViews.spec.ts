import { describe, expect, it, vi, beforeEach } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import AnalyticsOperatingMetricsView from '../AnalyticsOperatingMetricsView.vue'
import AnalyticsSegmentView from '../AnalyticsSegmentView.vue'
import AnalyticsMonitorView from '../AnalyticsMonitorView.vue'
import type { AnalyticsMetrics } from '../../api/analytics'

vi.mock('../../api/analytics', async () => {
  const actual = await vi.importActual<typeof import('../../api/analytics')>('../../api/analytics')
  return {
    ...actual,
    fetchDimensions: vi.fn().mockResolvedValue([
      { dimType: 'INDUSTRY', label: '行业', members: ['制造业', '批发和零售业'] },
    ]),
    fetchOrgs: vi.fn().mockResolvedValue([
      { orgId: '350000', orgName: '福建省分行', orgLevel: 2, orgPath: '/总行/福建省分行' },
    ]),
    fetchPeriods: vi.fn().mockResolvedValue(['201001', '201012']),
    fetchMetrics: vi.fn().mockResolvedValue({
      screen: 'operating-customer', screenLabel: '客户指标分析',
      bizType: null, dim: 'INDUSTRY', orgId: '350000', period: '201012',
      rowAxis: 'ORG',
      rows: [
        { dimValue: '厦门分行', custCnt: 61, custCntMom: 0.02, custCntYtd: 0.05, custCntNew: 3 },
        { dimValue: '泉州分行', custCnt: 55, custCntMom: -0.03, custCntYtd: 0.01, custCntNew: 1 },
      ],
    } satisfies AnalyticsMetrics),
    fetchTrend: vi.fn().mockResolvedValue({
      dimValue: '厦门分行', metric: 'custCnt',
      points: [{ period: '201001', value: 60 }, { period: '201002', value: 61 }],
    }),
  }
})

const stubs: Record<string, { template: string; props?: string[] }> = {
  NSpin: { template: '<div class="n-spin" />' }, Spin: { template: '<div class="n-spin" />' },
  NAlert: { template: '<div class="n-alert"><slot /></div>' }, Alert: { template: '<div class="n-alert"><slot /></div>' },
  NButton: { props: ['loading'], template: '<button class="n-button"><slot /></button>' }, Button: { props: ['loading'], template: '<button class="n-button"><slot /></button>' },
  NEmpty: { template: '<div class="n-empty" />' }, Empty: { template: '<div class="n-empty" />' },
  NSelect: { props: ['value', 'options'], template: '<div class="n-select" />' }, Select: { props: ['value', 'options'], template: '<div class="n-select" />' },
  NDataTable: { props: ['columns', 'data'], template: '<div class="n-table" />' }, DataTable: { props: ['columns', 'data'], template: '<div class="n-table" />' },
}

async function mountView(view: typeof AnalyticsOperatingMetricsView, path: string) {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path, name: 'TestView', component: view }],
  })
  await router.push(path)
  const wrapper = mount(view, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

function navLabels(wrapper: Awaited<ReturnType<typeof mountView>>): string[] {
  return wrapper.findAll('[data-testid="analytics-nav-item"]').map((n) => n.text().replace('◧', '').trim())
}

describe('经营分析页面内导航（Owner 口径：左侧导航面板切换分析图表）', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('经营指标分析：左侧 4 项导航，点击切换分析图表', async () => {
    const wrapper = await mountView(AnalyticsOperatingMetricsView, '/analytics/operating-metrics')
    expect(navLabels(wrapper)).toEqual(['客户指标分析', '业务概况分析', '利润贡献分析', '风险指标分析'])
    // 默认展示第一项的图表面板
    expect(wrapper.find('[data-testid="analytics-panel-operating-customer"]').exists()).toBe(true)
    // 点击「风险指标分析」切换面板
    await wrapper.findAll('[data-testid="analytics-nav-item"]')[3].trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="analytics-panel-operating-risk"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="analytics-panel-operating-customer"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('行=机构的屏：趋势按 ORG 轴取数（QA-F1/F3 回归）', async () => {
    const api = await import('../../api/analytics')
    const trendMock = api.fetchTrend as unknown as ReturnType<typeof vi.fn>
    const wrapper = await mountView(AnalyticsOperatingMetricsView, '/analytics/operating-metrics')
    // 此前把「分布维度」当 dim 传（dim=INDUSTRY）+ dimValue=机构名 ⇒ 后端 500 被前端静默吞
    expect(trendMock).toHaveBeenCalledWith(expect.objectContaining({ dim: 'ORG' }))
    wrapper.unmount()
  })

  it('趋势取数失败必须显示错误态，不得静默显示“数据不足”（QA-F3 回归）', async () => {
    const api = await import('../../api/analytics')
    const trendMock = api.fetchTrend as unknown as ReturnType<typeof vi.fn>
    trendMock.mockRejectedValueOnce(new Error('Request failed with status code 500'))
    const wrapper = await mountView(AnalyticsOperatingMetricsView, '/analytics/operating-metrics')
    const err = wrapper.find('[data-testid="analytics-trend-error"]')
    expect(err.exists()).toBe(true)
    expect(err.text()).toContain('趋势取数失败')
    expect(wrapper.text()).not.toContain('趋势数据不足')
    wrapper.unmount()
  })

  it('指标监视器：左侧 3 项导航', async () => {
    const wrapper = await mountView(AnalyticsMonitorView, '/analytics/monitors')
    expect(navLabels(wrapper)).toEqual(['业务增减变化监控', '存贷比变化监控', '不良贷款分布变化监控'])
    expect(wrapper.find('[data-testid="analytics-panel-monitor-balance"]').exists()).toBe(true)
    await wrapper.findAll('[data-testid="analytics-nav-item"]')[1].trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="analytics-panel-monitor-ldr"]').exists()).toBe(true)
    wrapper.unmount()
  })

  it('细分客群分析：2 项导航 + 细分客户业务 4 个子项，子项切换 bizType', async () => {
    const wrapper = await mountView(AnalyticsSegmentView, '/analytics/segments')
    expect(navLabels(wrapper)).toEqual(['客户分布特征分析', '细分客户业务分析'])
    const subs = wrapper.findAll('[data-testid="analytics-nav-subitem"]').map((n) => n.text().trim())
    expect(subs).toEqual(['存款业务', '贷款业务', '中间业务', '结算量业务'])
    expect(wrapper.find('[data-testid="analytics-panel-segment-distribution"]').exists()).toBe(true)
    // 点击子项「结算量业务」→ segment-business 面板
    await wrapper.findAll('[data-testid="analytics-nav-subitem"]')[3].trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="analytics-panel-segment-business"]').exists()).toBe(true)
    const { fetchMetrics } = await import('../../api/analytics')
    expect(fetchMetrics).toHaveBeenCalledWith(expect.objectContaining({ bizType: 'SETTLEMENT' }))
    wrapper.unmount()
  })
})
