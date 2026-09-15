import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ProposalRecordView from '../ProposalRecordView.vue'
import { loadProposalPlaceholder } from '../../composables/proposalDegrade'

vi.mock('../../composables/proposalDegrade', async () => {
  const actual = await vi.importActual<typeof import('../../composables/proposalDegrade')>(
    '../../composables/proposalDegrade',
  )
  return {
    ...actual,
    loadProposalPlaceholder: vi.fn(actual.loadProposalPlaceholder),
  }
})

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

async function mountP25(id = 'ph-1') {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/proposals/new', name: 'ProposalWizard', component: { template: '<div />' } },
      { path: '/proposals/:id', name: 'ProposalRecord', component: ProposalRecordView },
    ],
  })
  await router.push(`/proposals/${id}`)
  const wrapper = mount(ProposalRecordView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P25 ProposalRecordView C3 stage-machine degrade', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.mocked(loadProposalPlaceholder).mockReset()
    vi.mocked(loadProposalPlaceholder).mockImplementation(async (id: string) => ({
      placeholderId: id,
      informal: true,
      degradeLabel: '非正式 / C2 降级',
      contractNote: '本分支无建议书工厂合同。占位 ID 仅来自路由参数，非正式事实。',
    }))
  })

  it('enters successfully with a route-param placeholder, not a formal proposal body', async () => {
    const wrapper = await mountP25('ph-1')
    expect(wrapper.get('[data-testid="p25-proposal-record"]').text()).toContain('非正式建议书（C2 降级）')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('ph-1')
    expect(wrapper.text()).toContain('非正式 / C2 降级')
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(wrapper.get('[data-testid="p25-stage-notice"]').text()).toContain('阶段机 C3 未授权')
  })

  it('shows error four-state when the placeholder loader fails', async () => {
    vi.mocked(loadProposalPlaceholder).mockRejectedValueOnce(new Error('upstream'))
    const wrapper = await mountP25()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables 预览客户版 and does not render clickable G0-G5 promotion', async () => {
    const wrapper = await mountP25()
    expect(wrapper.text()).toContain('预览客户版')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
    const clickableStages = wrapper.findAll('button').filter(button => /^G[0-5]$/.test(button.text()))
    expect(clickableStages).toHaveLength(0)
  })
})
