import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ProposalWizardView from '../ProposalWizardView.vue'
import { loadProposalWizardShell } from '../../composables/proposalDegrade'
import { useProposalDraftStore } from '../../stores/proposalDraft'
import type { ServiceProposal } from '../../api/v14'

vi.mock('../../composables/proposalDegrade', async () => {
  const actual = await vi.importActual<typeof import('../../composables/proposalDegrade')>(
    '../../composables/proposalDegrade',
  )
  return {
    ...actual,
    loadProposalWizardShell: vi.fn(actual.loadProposalWizardShell),
  }
})

vi.mock('../../api/engagement', () => ({
  fetchCustomers: vi.fn(),
  formatApiError: (e: unknown, fallback: string) => (e instanceof Error ? e.message : fallback),
}))

vi.mock('../../api/v14', () => ({
  generateServiceProposal: vi.fn(),
}))

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled', 'loading'],
    template: '<button class="n-button" :disabled="disabled" :loading="loading"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  NCollapse: { template: '<div class="n-collapse"><slot /></div>' },
  NCollapseItem: {
    template: '<div class="n-collapse-item"><slot name="header" /><slot name="header-extra" /><slot /></div>',
  },
}

const DRAFT = [
  '# 华东精工装备集团综合金融服务建议书',
  '',
  '> 类型：INITIAL ｜ 阶段：FIRST_CONTACT',
  '',
  '# 第一章 企业概况',
  '',
  '## 1.1 基本信息',
  '',
  '华东精工装备集团是一家制造企业。',
  '',
  '# 第二章 需求分析',
  '',
  '## 2.1 资金需求',
  '',
  '客户有资金周转需求。',
].join('\n')

function proposalFixture(overrides: Partial<ServiceProposal> = {}): ServiceProposal {
  return {
    schemaVersion: '1.0.0',
    skillId: 'SP-20',
    runId: 'RUN-PROPOSAL-1',
    status: 'SUCCESS',
    timestamp: '2026-09-25T10:00:00Z',
    content: {
      proposalDraft: DRAFT,
      internalVersion: null,
      customerVersion: null,
      customerVersionNote: '',
    },
    citations: [
      { id: 'CIT-0001', claim: '公司成立于 2005 年', source: 'basicInfo', date: '2024-01-01', factLabel: 'F', chapterRef: 'CH01' },
      { id: 'CIT-0002', claim: '月均交易量 2.8 亿', source: 'transactionSummary', date: '2024-01-01', factLabel: 'F', chapterRef: 'CH02' },
    ],
    unknowns: [
      { id: 'UNK-0001', description: '缺少股东名册', suggestedAction: '调取工商档案', relatedChapter: 'CH01' },
    ],
    limitations: ['ContextPackage 50KB 上限。'],
    gateRecommendations: null,
    ruleViolations: [],
    ...overrides,
  }
}

async function mountP24(seed?: (pinia: Pinia) => void) {
  const pinia = createPinia()
  setActivePinia(pinia)
  if (seed) seed(pinia)
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/proposals/new', name: 'ProposalWizard', component: ProposalWizardView },
      { path: '/proposals/:id', name: 'ProposalRecord', component: { template: '<div />' } },
      { path: '/proposals', name: 'ProposalsHome', component: { template: '<div />' } },
    ],
  })
  await router.push('/proposals/new')
  const wrapper = mount(ProposalWizardView, { global: { plugins: [router, pinia], stubs } })
  await flushPromises()
  return { wrapper, router, pinia }
}

describe('P24 ProposalWizardView C2 degrade', () => {
  beforeEach(async () => {
    sessionStorage.clear()
    vi.mocked(loadProposalWizardShell).mockReset()
    vi.mocked(loadProposalWizardShell).mockResolvedValue({
      informal: true,
      emptyDraft: true,
      degradeLabel: '非正式 / C2 降级',
    })
    const { fetchCustomers } = await import('../../api/engagement')
    const { generateServiceProposal } = await import('../../api/v14')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([
      { customerId: 'CUST-CORP-0001', customerName: '华东精工装备集团' },
    ])
    ;(generateServiceProposal as ReturnType<typeof vi.fn>).mockReset()
  })

  it('enters successfully as an empty informal wizard', async () => {
    const { wrapper } = await mountP24()
    expect(wrapper.get('[data-testid="p24-proposal-wizard"]').text()).toContain('非正式建议书（C2 降级）')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('选择客户')
    expect(wrapper.text()).toContain('非正式 / C2 降级')
    expect(wrapper.text()).not.toContain('NEED-826')
  })

  it('shows error four-state when the wizard shell loader fails', async () => {
    vi.mocked(loadProposalWizardShell).mockRejectedValueOnce(new Error('upstream'))
    const { wrapper } = await mountP24()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('keeps 保存并继续 disabled when no draft', async () => {
    const { wrapper } = await mountP24()
    expect(wrapper.text()).toContain('保存并继续')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
  })

  it('enables 保存并继续 after draft is generated', async () => {
    const { generateServiceProposal } = await import('../../api/v14')
    ;(generateServiceProposal as ReturnType<typeof vi.fn>).mockResolvedValue(proposalFixture())
    const { wrapper } = await mountP24()

    await wrapper.get('[data-testid="p24-generate"]').trigger('click')
    await flushPromises()

    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(false)
  })

  it('navigates to record page on 保存并继续 click', async () => {
    const { generateServiceProposal } = await import('../../api/v14')
    ;(generateServiceProposal as ReturnType<typeof vi.fn>).mockResolvedValue(proposalFixture())
    const { wrapper, router } = await mountP24()

    await wrapper.get('[data-testid="p24-generate"]').trigger('click')
    await flushPromises()

    await wrapper.get('[data-testid="gated-action"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('ProposalRecord')
    expect(router.currentRoute.value.params.id).toBe('RUN-PROPOSAL-1')
  })

  it('renders the KERT draft as chapter cards (not a raw pre)', async () => {
    const { generateServiceProposal } = await import('../../api/v14')
    ;(generateServiceProposal as ReturnType<typeof vi.fn>).mockResolvedValue(proposalFixture())
    const { wrapper } = await mountP24()

    await wrapper.get('[data-testid="p24-generate"]').trigger('click')
    await flushPromises()

    expect(generateServiceProposal).toHaveBeenCalledWith(
      expect.stringMatching(/^REQ-SP20-/),
      'CUST-CORP-0001',
      {},
    )
    const draftBox = wrapper.get('[data-testid="p24-skill-draft"]')
    expect(draftBox.text()).toContain('华东精工装备集团综合金融服务建议书')
    expect(draftBox.text()).toContain('企业概况')

    // 每章一张卡片，且章内按节展示
    const chapters = draftBox.findAll('[data-testid="proposal-chapter"]')
    expect(chapters).toHaveLength(2)
    expect(chapters[0].attributes('data-chapter-code')).toBe('CH01')
    expect(chapters[0].text()).toContain('1.1 基本信息')
    expect(chapters[0].text()).toContain('华东精工装备集团是一家制造企业。')
    expect(chapters[0].text()).toContain('1 项待确认')
    expect(chapters[0].text()).toContain('1 条引用')
    expect(chapters[1].text()).toContain('客户有资金周转需求。')

    // 原始 Markdown 只作为默认收起的逐字核对入口保留，不占据版面
    const rawPanel = draftBox.get('[data-testid="proposal-draft-raw-panel"]')
    expect(rawPanel.element.hasAttribute('open')).toBe(false)
    expect(rawPanel.get('summary').text()).toContain('原始 Markdown')
    expect(draftBox.get('[data-testid="proposal-draft-raw"]').text()).toContain('# 第一章 企业概况')
  })

  it('stores the generated draft for P23/P25 (same runId, no write API)', async () => {
    const { generateServiceProposal } = await import('../../api/v14')
    ;(generateServiceProposal as ReturnType<typeof vi.fn>).mockResolvedValue(proposalFixture())
    const { wrapper, pinia } = await mountP24()
    await wrapper.get('[data-testid="p24-generate"]').trigger('click')
    await flushPromises()

    const store = useProposalDraftStore(pinia)
    expect(store.drafts).toHaveLength(1)
    expect(store.drafts[0]).toMatchObject({
      id: 'RUN-PROPOSAL-1',
      customerName: '华东精工装备集团',
      status: 'INFORMAL',
      skillId: 'SP-20',
      chapterCount: 2,
      citationCount: 2,
      unknownCount: 1,
      limitationCount: 1,
    })
    // 已生成后出现「返回列表 / 查看记录页」，但不得出现任何保存类动作
    expect(wrapper.find('[data-testid="p24-back-list"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p24-open-record"]').exists()).toBe(true)
  })

  it('shows the named error when KERT fails (no silent empty draft)', async () => {
    const { generateServiceProposal } = await import('../../api/v14')
    ;(generateServiceProposal as ReturnType<typeof vi.fn>).mockRejectedValue(
      new Error('KERT 服务不可用（KERT_UNAVAILABLE）'),
    )
    const { wrapper } = await mountP24()
    await wrapper.get('[data-testid="p24-generate"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-testid="p24-skill-error"]').text()).toContain('KERT_UNAVAILABLE')
    expect(wrapper.find('[data-testid="p24-skill-draft"]').exists()).toBe(false)
  })

  it('shows 空草稿 when KERT returns SUCCESS without draft text', async () => {
    const { generateServiceProposal } = await import('../../api/v14')
    ;(generateServiceProposal as ReturnType<typeof vi.fn>).mockResolvedValue(
      proposalFixture({ content: { proposalDraft: '   ', internalVersion: null, customerVersion: null, customerVersionNote: '' } }),
    )
    const { wrapper } = await mountP24()
    await wrapper.get('[data-testid="p24-generate"]').trigger('click')
    await flushPromises()

    expect(wrapper.find('[data-testid="p24-skill-empty"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p24-skill-draft"]').exists()).toBe(false)
  })
})
