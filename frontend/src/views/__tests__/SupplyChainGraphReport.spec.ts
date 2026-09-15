import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { defineComponent } from 'vue'
import SupplyChainGraphReport from '../SupplyChainGraphReport.vue'
import type { SupplyChainGraphReport as Report } from '../../api/engagement'

const fetchMock = vi.fn()
vi.mock('../../api/engagement', () => ({
  fetchSupplyChainGraphReport: (...args: unknown[]) => fetchMock(...args),
}))
vi.mock('../../components/SupplyChainForceGraph.vue', () => ({
  default: defineComponent({ name: 'SupplyChainForceGraph', template: '<div class="graph-stub" />' }),
}))
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { requestId: 'SCG-1' } }),
  useRouter: () => ({ push: vi.fn() }),
}))

const partialReport: Report = {
  requestId: 'SCG-1',
  customerId: 'CUST-001',
  customerName: '杭州智造',
  generatedAt: '2026-08-22T02:00:00Z',
  status: 'ok',
  reportUrl: '/supply-chain-report/SCG-1',
  result: {
    schemaVersion: '1.0',
    buildStatus: 'partial',
    nodes: [{ id: 'N-E', name: '杭州智造', layer: 'enterprise', annualAmount: 50000000, share: 1 }],
    edges: [],
    interpretation: { overallAssessment: '输入不足' },
  },
}

describe('SupplyChainGraphReport', () => {
  beforeEach(() => {
    fetchMock.mockReset()
  })

  it('renders partial badge without throwing', async () => {
    fetchMock.mockResolvedValue(partialReport)
    const wrapper = mount(SupplyChainGraphReport)
    await flushPromises()
    expect(wrapper.text()).toContain('部分降级，仅供参考')
    expect(wrapper.text()).toContain('输入不足')
    expect(wrapper.text()).toContain('5000.0 万')
  })

  it('shows expired message on 404', async () => {
    const err = Object.assign(new Error('not found'), {
      isAxiosError: true,
      response: { status: 404, data: { message: '报告已过期，请重新执行' } },
    })
    fetchMock.mockRejectedValue(err)
    const wrapper = mount(SupplyChainGraphReport)
    await flushPromises()
    expect(wrapper.text()).toContain('报告已过期，请重新执行')
  })
})
