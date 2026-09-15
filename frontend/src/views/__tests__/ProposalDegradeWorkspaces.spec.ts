import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter, type RouteRecordRaw } from 'vue-router'
import type { Component } from 'vue'
import ProposalEditorView from '../ProposalEditorView.vue'
import ProposalMapView from '../ProposalMapView.vue'
import ProposalEvidenceView from '../ProposalEvidenceView.vue'
import ProposalProjectView from '../ProposalProjectView.vue'
import ProposalVersionsView from '../ProposalVersionsView.vue'
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

type WorkspaceCase = {
  pageId: string
  path: string
  name: string
  component: Component
  testId: string
  action: string
  degradeNeedle: string
}

const CASES: WorkspaceCase[] = [
  {
    pageId: 'P26',
    path: '/proposals/ph-1/editor',
    name: 'ProposalEditor',
    component: ProposalEditorView,
    testId: 'p26-proposal-editor',
    action: '提交评审',
    degradeNeedle: '非正式 / C2 降级',
  },
  {
    pageId: 'P27',
    path: '/proposals/ph-1/map',
    name: 'ProposalMap',
    component: ProposalMapView,
    testId: 'p27-proposal-map',
    action: '运行完整性检查',
    degradeNeedle: '非正式 / C2 降级',
  },
  {
    pageId: 'P28',
    path: '/proposals/ph-1/evidence',
    name: 'ProposalEvidence',
    component: ProposalEvidenceView,
    testId: 'p28-proposal-evidence',
    action: '标记问题',
    degradeNeedle: '当前不可反查',
  },
  {
    pageId: 'P29',
    path: '/proposals/ph-1/project',
    name: 'ProposalProject',
    component: ProposalProjectView,
    testId: 'p29-proposal-project',
    action: '查看隐藏规则',
    degradeNeedle: '非正式 / C2 降级',
  },
  {
    pageId: 'P30',
    path: '/proposals/ph-1/versions',
    name: 'ProposalVersions',
    component: ProposalVersionsView,
    testId: 'p30-proposal-versions',
    action: '创建新版本',
    degradeNeedle: '非正式 / C2 降级',
  },
]

async function mountPage(page: WorkspaceCase) {
  setActivePinia(createPinia())
  const routes: RouteRecordRaw[] = [
    { path: page.path.replace('ph-1', ':id'), name: page.name, component: page.component },
  ]
  const router = createRouter({ history: createMemoryHistory(), routes })
  await router.push(page.path)
  const wrapper = mount(page.component, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P26-P30 proposal workspace C2 degrade shells', () => {
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

  for (const page of CASES) {
    describe(page.pageId, () => {
      it('enters successfully with a placeholder object id', async () => {
        const wrapper = await mountPage(page)
        expect(wrapper.get(`[data-testid="${page.testId}"]`).text()).toContain('非正式建议书（C2 降级）')
        expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
        expect(wrapper.text()).toContain('ph-1')
        expect(wrapper.text()).toContain(page.degradeNeedle)
        expect(wrapper.text()).not.toContain('NEED-826')
      })

      it('shows error four-state when the placeholder loader fails', async () => {
        vi.mocked(loadProposalPlaceholder).mockRejectedValueOnce(new Error('upstream'))
        const wrapper = await mountPage(page)
        expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
      })

      it(`keeps ${page.action} disabled`, async () => {
        const wrapper = await mountPage(page)
        expect(wrapper.text()).toContain(page.action)
        expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
        expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
      })
    })
  }
})
