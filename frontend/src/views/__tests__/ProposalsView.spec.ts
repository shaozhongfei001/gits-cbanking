import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import { NDataTable } from 'naive-ui'
import { createMemoryHistory, createRouter } from 'vue-router'
import ProposalsView from '../ProposalsView.vue'
import { loadProposalShellList } from '../../composables/proposalDegrade'
import { useProposalDraftStore, type ProposalDraftRecord } from '../../stores/proposalDraft'
import type { ServiceProposal } from '../../api/v14'

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
    props: ['disabled', 'loading'],
    template: '<button class="n-button" :disabled="disabled" :loading="loading"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" data-testid="n-empty"><slot /></div>' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
}

async function mountP23(seed?: (pinia: Pinia) => void) {
  const pinia = createPinia()
  setActivePinia(pinia)
  if (seed) seed(pinia)
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/proposals', name: 'ProposalsHome', component: ProposalsView },
      { path: '/proposals/new', name: 'ProposalWizard', component: { template: '<div />' } },
      { path: '/proposals/:id', name: 'ProposalRecord', component: { template: '<div />' } },
    ],
  })
  await router.push('/proposals')
  const wrapper = mount(ProposalsView, { global: { plugins: [router, pinia], stubs } })
  await flushPromises()
  return { wrapper, router }
}

function proposalFixture(): ServiceProposal {
  return {
    schemaVersion: '1.0.0',
    skillId: 'SP-20',
    runId: 'RUN-PROPOSAL-1',
    status: 'SUCCESS',
    timestamp: '2026-09-25T10:00:00Z',
    content: {
      proposalDraft: '# 客户建议书\n\n# 第一章 概况\n\n## 1.1 基本信息\n\n正文。',
      internalVersion: null,
      customerVersion: null,
      customerVersionNote: '',
    },
    citations: [],
    unknowns: [],
    limitations: [],
    gateRecommendations: null,
    ruleViolations: [],
  }
}

/** 会话暂存中的一条非正式草稿记录 */
function seedRecord(): ProposalDraftRecord {
  return {
    id: 'RUN-PROPOSAL-1',
    customerId: 'CUST-CORP-0001',
    customerName: '华东精工装备集团',
    proposalName: '华东精工装备集团 — 非正式建议书草稿',
    generatedAt: '2026-09-25T10:00:00Z',
    status: 'INFORMAL',
    skillId: 'SP-20',
    chapterCount: 1,
    citationCount: 3,
    unknownCount: 2,
    limitationCount: 1,
    proposal: proposalFixture(),
  }
}

describe('P23 ProposalsView C2 degrade', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.mocked(loadProposalShellList).mockReset()
    vi.mocked(loadProposalShellList).mockResolvedValue([])
  })

  it('enters successfully and shows empty state', async () => {
    const { wrapper } = await mountP23()
    expect(wrapper.get('[data-testid="p23-proposals"]').text()).toContain('非正式建议书（C2 降级）')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.find('.n-empty').exists() || wrapper.find('[data-testid="n-empty"]').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(wrapper.text()).not.toContain('年度综合服务方案')
  })

  it('shows error four-state when the empty-list loader fails', async () => {
    vi.mocked(loadProposalShellList).mockRejectedValueOnce(new Error('upstream'))
    const { wrapper } = await mountP23()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('has 新建建议书 enabled and exactly one disabled 导入草稿 (from the degrade shell)', async () => {
    const { wrapper } = await mountP23()
    expect(wrapper.get('[data-testid="p23-new-proposal"]').text()).toContain('新建建议书')
    expect((wrapper.get('[data-testid="p23-new-proposal"]').element as HTMLButtonElement).disabled).toBe(false)
    // 「导入草稿」由降级壳的 DisabledAction 唯一提供，不得重复渲染
    const importButtons = wrapper
      .findAll('button')
      .filter(button => button.text().includes('导入草稿'))
    expect(importButtons).toHaveLength(1)
    expect((importButtons[0].element as HTMLButtonElement).disabled).toBe(true)
  })

  it('navigates to the P24 wizard page when clicking 新建建议书 (no modal)', async () => {
    const { wrapper, router } = await mountP23()
    await wrapper.get('[data-testid="p23-new-proposal"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('ProposalWizard')
    expect(wrapper.find('[data-testid="p23-wizard-overlay"]').exists()).toBe(false)
  })

  it('opens the detail page when clicking the row, the name link or 查看详情', async () => {
    const { wrapper, router } = await mountP23((pinia) => {
      useProposalDraftStore(pinia).add({ ...seedRecord(), id: 'RUN-ROW-1' })
    })

    // 行可点（整行即详情入口）
    const row = wrapper.get('[data-testid="p23-row-RUN-ROW-1"]')
    expect(row.attributes('tabindex')).toBe('0')
    await row.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('ProposalRecord')
    expect(router.currentRoute.value.params.id).toBe('RUN-ROW-1')

    // 名称是真实链接（可新开标签），href 指向详情页
    const link = wrapper.get('[data-testid="p23-proposal-link-RUN-ROW-1"]')
    expect(link.attributes('href')).toBe('/proposals/RUN-ROW-1')

    // 操作列提供显式「查看详情」
    expect(wrapper.get('[data-testid="p23-view-detail-RUN-ROW-1"]').text()).toContain('查看详情')
  })

  it('renders stored drafts from the memory store with 建议书要素列', async () => {
    const { wrapper } = await mountP23((pinia) => {
      useProposalDraftStore(pinia).add(seedRecord())
    })
    const table = wrapper.findComponent(NDataTable)
    expect(table.exists()).toBe(true)
    expect(table.props('data')).toHaveLength(1)
    expect(wrapper.find('[data-testid="n-empty"]').exists()).toBe(false)
    const headers = (table.props('columns') as { title: string }[]).map(column => column.title)
    expect(headers).toEqual(
      expect.arrayContaining(['客户', '建议书名称', '生成时间', '状态', '章数', '引用', '待确认', '边界']),
    )
  })
})
