import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ProposalRecordView from '../ProposalRecordView.vue'
import { loadProposalPlaceholder } from '../../composables/proposalDegrade'
import { useProposalDraftStore, type ProposalDraftRecord } from '../../stores/proposalDraft'
import type { ServiceProposal } from '../../api/v14'

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
  NTag: { template: '<span class="n-tag"><slot /></span>' },
}

const RECORD_ID = 'RUN-PROPOSAL-DETAIL-1'

function proposalFixture(): ServiceProposal {
  return {
    schemaVersion: '1.0.0',
    skillId: 'SP-20',
    runId: RECORD_ID,
    status: 'SUCCESS',
    timestamp: '2026-09-25T06:11:25Z',
    content: {
      proposalDraft: [
        '# 华东精工装备集团综合金融服务建议书',
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
      ].join('\n'),
      internalVersion: null,
      customerVersion: null,
      customerVersionNote: '',
    },
    citations: [
      { id: 'CIT-0001', claim: '成立于 2005 年', source: 'basicInfo', date: '2024-01-01', factLabel: 'F', chapterRef: 'CH01' },
    ],
    unknowns: [
      { id: 'UNK-0001', description: '缺少股东名册', suggestedAction: '调取工商档案', relatedChapter: 'CH01' },
    ],
    limitations: ['ContextPackage 50KB 上限。'],
    gateRecommendations: null,
    ruleViolations: [],
  }
}

function recordFixture(): ProposalDraftRecord {
  return {
    id: RECORD_ID,
    customerId: 'CUST-CORP-0001',
    customerName: '华东精工装备集团',
    proposalName: '华东精工装备集团 — 非正式建议书草稿',
    generatedAt: '2026-09-25T06:11:25Z',
    status: 'INFORMAL',
    skillId: 'SP-20',
    chapterCount: 2,
    citationCount: 1,
    unknownCount: 1,
    limitationCount: 1,
    proposal: proposalFixture(),
  }
}

async function mountP25(id = RECORD_ID, seed?: (pinia: ReturnType<typeof createPinia>) => void) {
  const pinia = createPinia()
  setActivePinia(pinia)
  if (seed) seed(pinia)
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/proposals/new', name: 'ProposalWizard', component: { template: '<div />' } },
      { path: '/proposals', name: 'ProposalsHome', component: { template: '<div />' } },
      { path: '/proposals/:id', name: 'ProposalRecord', component: ProposalRecordView },
    ],
  })
  await router.push(`/proposals/${id}`)
  const wrapper = mount(ProposalRecordView, { global: { plugins: [router, pinia], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P25 ProposalRecordView 详情页（命中会话暂存）', () => {
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

  it('展示对象元数据（客户 / 名称 / 生成时间 / 状态 / 运行标识）', async () => {
    const { wrapper } = await mountP25(RECORD_ID, (pinia) => {
      useProposalDraftStore(pinia).add(recordFixture())
    })
    const detail = wrapper.get('[data-testid="p25-skill-draft"]')
    const text = detail.text()
    expect(text).toContain('华东精工装备集团（CUST-CORP-0001）')
    expect(text).toContain('华东精工装备集团 — 非正式建议书草稿')
    expect(text).toContain('非正式草稿（未落库）')
    expect(text).toContain(RECORD_ID)
    // 生成时间按本地时区格式化，不再裸露 ISO
    expect(text).toMatch(/2026-09-2\d \d{2}:\d{2}:\d{2}/)
  })

  it('展示章节卡片与章节目录（详情可跳转）', async () => {
    const { wrapper } = await mountP25(RECORD_ID, (pinia) => {
      useProposalDraftStore(pinia).add(recordFixture())
    })
    const detail = wrapper.get('[data-testid="p25-skill-draft"]')
    expect(detail.findAll('[data-testid="proposal-chapter"]')).toHaveLength(2)
    expect(detail.findAll('[data-testid="proposal-toc-item"]')).toHaveLength(2)
    expect(detail.text()).toContain('华东精工装备集团是一家制造企业。')
    expect(detail.text()).toContain('客户有资金周转需求。')
  })

  it('阶段机说明（C3）始终可见且可折叠', async () => {
    const { wrapper } = await mountP25(RECORD_ID, (pinia) => {
      useProposalDraftStore(pinia).add(recordFixture())
    })
    expect(wrapper.get('[data-testid="p25-stage-notice"]').text()).toContain('阶段机 C3 未授权')
    expect(wrapper.text()).not.toContain('NEED-826')
  })
})

describe('P25 ProposalRecordView 详情页（未命中会话暂存）', () => {
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
    const { wrapper } = await mountP25('ph-1')
    expect(wrapper.get('[data-testid="p25-proposal-record"]').text()).toContain('非正式建议书（C2 降级）')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('ph-1')
    expect(wrapper.text()).toContain('非正式 / C2 降级')
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(wrapper.get('[data-testid="p25-stage-notice"]').text()).toContain('阶段机 C3 未授权')
  })

  it('shows error four-state when the placeholder loader fails', async () => {
    vi.mocked(loadProposalPlaceholder).mockRejectedValueOnce(new Error('upstream'))
    const { wrapper } = await mountP25()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('不编造正文：说明未命中暂存并给出返回列表 / 重新生成出口', async () => {
    const { wrapper } = await mountP25('ph-1')
    expect(wrapper.find('[data-testid="p25-skill-draft"]').exists()).toBe(false)
    expect(wrapper.findAll('[data-testid="proposal-chapter"]')).toHaveLength(0)
    expect(wrapper.get('[data-testid="p25-not-cached"]').text()).toContain('不在本次浏览器会话的暂存中')
    expect(wrapper.find('[data-testid="p25-miss-back-list"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p25-miss-regenerate"]').exists()).toBe(true)
  })

  it('disables 预览客户版 and does not render clickable G0-G5 promotion', async () => {
    const { wrapper } = await mountP25()
    expect(wrapper.text()).toContain('预览客户版')
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
    const clickableStages = wrapper.findAll('button').filter(button => /^G[0-5]$/.test(button.text()))
    expect(clickableStages).toHaveLength(0)
  })
})
