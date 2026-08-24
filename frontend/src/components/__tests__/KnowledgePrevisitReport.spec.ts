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
})
