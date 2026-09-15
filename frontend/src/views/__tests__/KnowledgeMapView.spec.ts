import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import KnowledgeMapView from '../KnowledgeMapView.vue'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
    fetchAssembledKnowledgeMap: vi.fn(),
    matchProducts: vi.fn(),
  }
})

vi.mock('../../api/knowledge', () => ({
  fetchKnowledgeMap: vi.fn(),
}))

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

async function mountP38() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/knowledge-map', name: 'KnowledgeMapView', component: KnowledgeMapView }],
  })
  await router.push('/knowledge-map')
  const wrapper = mount(KnowledgeMapView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P38 KnowledgeMapView DKWS', () => {
  beforeEach(async () => {
    sessionStorage.clear()
    const { fetchCustomers, fetchAssembledKnowledgeMap, matchProducts } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([
      { customerId: 'CUST-CORP-0001', customerName: '华东精工装备集团' },
    ])
    ;(fetchAssembledKnowledgeMap as ReturnType<typeof vi.fn>).mockResolvedValue({
      customerId: 'CUST-CORP-0001',
      skillSections: [],
      assemblyTrace: [],
    })
    ;(matchProducts as ReturnType<typeof vi.fn>).mockResolvedValue([])
  })

  it('does not fill the page from the GITS knowledge snapshot', async () => {
    const { fetchKnowledgeMap } = await import('../../api/knowledge')
    const wrapper = await mountP38()
    expect(wrapper.get('[data-testid="p38-knowledge-map"]').text()).toContain('知识卡与产品适用边界')
    expect(wrapper.text()).toContain('知识要素 KE（只读）')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="p38-empty"]').text()).toContain('DKWS 未返回知识地图')
    expect(wrapper.text()).not.toContain('KE-1')
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(fetchKnowledgeMap).not.toHaveBeenCalled()
  })

  it('renders DKWS skill sections when the Skill returns them', async () => {
    const { fetchAssembledKnowledgeMap } = await import('../../api/engagement')
    ;(fetchAssembledKnowledgeMap as ReturnType<typeof vi.fn>).mockResolvedValue({
      customerId: 'CUST-CORP-0001',
      skillReportTitle: '访前知识地图',
      skillSections: [{ heading: 'KI-009 企业客户基本信息', content: '行业：装备制造' }],
      assemblyTrace: [{ phase: 'retrieve', status: 'ok', message: '平台库取到', kiId: 'KI-009' }],
    })
    const wrapper = await mountP38()
    expect(wrapper.find('[data-testid="p38-empty"]').exists()).toBe(false)
    expect(wrapper.get('[data-testid="p38-sections"]').text()).toContain('行业：装备制造')
    expect(wrapper.get('[data-testid="p38-trace"]').text()).toContain('平台库取到')
  })

  it('keeps 比较产品 and 反馈知识 disabled', async () => {
    const wrapper = await mountP38()
    expect(wrapper.text()).toContain('比较产品')
    expect(wrapper.text()).toContain('反馈知识')
    const buttons = wrapper.findAll('[data-testid="gated-action"]')
    expect(buttons.length).toBe(2)
    for (const button of buttons) {
      expect((button.element as HTMLButtonElement).disabled).toBe(true)
    }
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })
})
