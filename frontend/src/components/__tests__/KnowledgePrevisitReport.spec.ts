import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import KnowledgePrevisitReport from '../KnowledgePrevisitReport.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

const stubs = {
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  SupplyChainForceGraph: { template: '<div class="sc-graph-stub" />' },
}

describe('KnowledgePrevisitReport R2', () => {
  it('shows DKWS empty hint when battle card lists are empty', () => {
    const wrapper = mount(KnowledgePrevisitReport, {
      props: {
        report: { reportId: 'R1-1', visitObjective: '了解二期' },
        battleCard: {
          customerName: '华东精工',
          visitObjective: '了解二期',
          customerTier: 'STRATEGIC',
          riskLevel: 'MEDIUM',
          keyPoints: [],
          productHints: [],
          dontForget: [],
          bottomLine: '',
        },
        skillSections: [],
      },
      global: { stubs },
    })

    expect(wrapper.find('.battle-card').exists()).toBe(true)
    expect(wrapper.text()).toContain('DKWS 未返回速战卡')
    expect(wrapper.text()).not.toContain('要点（KI-009/002）')
  })

  it('renders Skill lists when battle card is filled', () => {
    const wrapper = mount(KnowledgePrevisitReport, {
      props: {
        report: { reportId: 'R1-1', visitObjective: '了解二期' },
        battleCard: {
          customerName: '华东精工',
          visitObjective: '了解二期',
          keyPoints: ['行业：精密制造'],
          productHints: ['供应链票据贴现方案'],
          dontForget: ['补齐实控人'],
          bottomLine: '',
        },
        skillSections: [],
      },
      global: { stubs },
    })

    expect(wrapper.text()).toContain('行业：精密制造')
    expect(wrapper.text()).toContain('供应链票据贴现方案')
    expect(wrapper.text()).not.toContain('DKWS 未返回速战卡')
  })

  it('renders V3.2 metric separators on the supply-chain block', () => {
    const wrapper = mount(KnowledgePrevisitReport, {
      props: {
        report: { reportId: 'R1-1', visitObjective: '了解二期' },
        skillSections: [],
        supplyChainReport: {
          requestId: 'SCG-1',
          customerId: 'c1',
          result: {
            nodes: [
              { id: 'e', name: '华东精工', layer: 'enterprise' },
              { id: 's', name: '钢厂', layer: 'supplier' },
              { id: 'c', name: '主机厂', layer: 'customer' },
            ],
            edges: [{ source: 's', target: 'e' }],
            interpretation: { overallAssessment: '位置稳固', followUpQuestions: ['核对应收'] },
          },
        },
      },
      global: { stubs },
    })
    expect(wrapper.text()).toContain('图谱节点')
    expect(wrapper.text()).toContain('上游')
    expect(wrapper.find('.sc-metric-teal').exists()).toBe(true)
    expect(wrapper.find('.sc-viz').exists()).toBe(true)
  })
})
