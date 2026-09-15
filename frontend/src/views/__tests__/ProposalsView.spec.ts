import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ProposalsView from '../ProposalsView.vue'
import { loadProposalShellList } from '../../composables/proposalDegrade'

vi.mock('../../composables/proposalDegrade', async () => {
  const actual = await vi.importActual<typeof import('../../composables/proposalDegrade')>(
    '../../composables/proposalDegrade',
  )
  return {
    ...actual,
    loadProposalShellList: vi.fn(actual.loadProposalShellList),
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

async function mountP23() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/proposals', name: 'ProposalsHome', component: ProposalsView },
      { path: '/proposals/new', name: 'ProposalWizard', component: { template: '<div />' } },
    ],
  })
  await router.push('/proposals')
  const wrapper = mount(ProposalsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P23 ProposalsView C2 degrade', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.mocked(loadProposalShellList).mockReset()
    vi.mocked(loadProposalShellList).mockResolvedValue([])
  })

  it('enters successfully and uses empty state instead of fabricating proposals', async () => {
    const { wrapper } = await mountP23()
    expect(wrapper.get('[data-testid="p23-proposals"]').text()).toContain('非正式建议书（C2 降级）')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="p23-empty"]').text()).toMatch(/暂无/)
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(wrapper.text()).not.toContain('年度综合服务方案')
  })

  it('shows error four-state when the empty-list loader fails', async () => {
    vi.mocked(loadProposalShellList).mockRejectedValueOnce(new Error('upstream'))
    const { wrapper } = await mountP23()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('keeps 导入草稿 disabled and can open the wizard degrade shell', async () => {
    const { wrapper, router } = await mountP23()
    expect(wrapper.get('[data-testid="p23-open-wizard"]').text()).toBe('新建建议书')
    expect(wrapper.text()).toContain('导入草稿')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
    await wrapper.get('[data-testid="p23-open-wizard"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/proposals/new')
  })
})
