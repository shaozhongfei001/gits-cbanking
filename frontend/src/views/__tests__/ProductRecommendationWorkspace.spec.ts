import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ProductRecommendationWorkspace from '../ProductRecommendationWorkspace.vue'
import type {
  ProductRecommendationRun,
  ProductRecommendationStageResult,
  ProductRecommendationProposalVersion,
} from '../../api/productRecommendation'

vi.mock('../../api/productRecommendation', async () => {
  const actual = await vi.importActual<typeof import('../../api/productRecommendation')>('../../api/productRecommendation')
  return {
    ...actual,
    createProductRecommendationRun: vi.fn(),
    getProductRecommendationRun: vi.fn(),
    getProductRecommendationStages: vi.fn(),
    getProductRecommendationVersion: vi.fn(),
    retryProductRecommendationRun: vi.fn(),
  }
})

const mockRun: ProductRecommendationRun = {
  runId: 'run-1',
  customerId: 'c1',
  status: 'AWAITING_HUMAN',
  asOf: '2026-08-31T10:00:00Z',
  idempotencyKey: 'idem-1',
  createdAt: '2026-08-31T09:00:00Z',
  recommendationObjective: '扩产融资',
  needVersionIds: ['NV-1'],
  requestedProductDomains: ['CREDIT'],
  currentVersionId: 'v1',
  snapshotRefs: { customerFactSnapshotId: 'CFS-1', ruleBundleRef: 'RB-1' },
}

const mockStages: ProductRecommendationStageResult = {
  runId: 'run-1',
  status: 'AWAITING_HUMAN',
  eligibilityResults: [
    {
      productId: 'PROD-1',
      productVersion: '2.0',
      eligibility: 'ELIGIBLE',
      ruleResults: [
        { ruleId: 'PR-ELIG-001', ruleVersion: '1.3', result: 'PASS', reasonCode: 'PRODUCT_VERSION_ACTIVE' },
      ],
    },
  ],
  fitResults: [
    {
      productId: 'PROD-1',
      productVersion: '2.0',
      rank: 1,
      fitScore: 0.9,
      dimensionMatches: [{ dimension: 'CORE_NEED_FIT', result: 'STRONG', rationale: '能力吻合' }],
    },
  ],
  portfolioCandidates: [
    {
      portfolioId: 'PF-1',
      primaryProduct: { productId: 'PROD-1', productVersion: '2.0', role: 'PRIMARY' },
      recommendationCategory: 'IMMEDIATE_COMMUNICATE',
    },
  ],
  unknowns: ['注册资本未核验'],
  conflicts: [],
}

const mockVersion: ProductRecommendationProposalVersion = {
  versionId: 'v1',
  runId: 'run-1',
  contentHash: 'sha256:abc',
  createdAt: '2026-08-31T10:30:00Z',
}

const stubs = {
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NEmpty: { template: '<div class="n-empty" />' },
}

async function mountWorkspace(runId: string, query: Record<string, string> = {}) {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/recommendation/:runId', name: 'ProductRecommendationWorkspace', component: ProductRecommendationWorkspace },
    ],
  })
  await router.push({ name: 'ProductRecommendationWorkspace', params: { runId }, query })
  const wrapper = mount(ProductRecommendationWorkspace, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

async function mockLoaded(overrides?: Partial<ProductRecommendationRun>) {
  const api = await import('../../api/productRecommendation')
  ;(api.getProductRecommendationRun as ReturnType<typeof vi.fn>).mockResolvedValue({ ...mockRun, ...overrides })
  ;(api.getProductRecommendationStages as ReturnType<typeof vi.fn>).mockResolvedValue(mockStages)
  ;(api.getProductRecommendationVersion as ReturnType<typeof vi.fn>).mockResolvedValue(mockVersion)
}

describe('WP5-1 ProductRecommendationWorkspace', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    sessionStorage.clear()
  })

  it('renders three-stage workspace with tabs and all five panels', async () => {
    await mockLoaded()
    const { wrapper } = await mountWorkspace('run-1')
    expect(wrapper.get('[data-testid="pr-workspace"]').text()).toContain('产品推荐三段式工作区')
    expect(wrapper.find('[data-testid="pr-tab-eligibility"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pr-tab-matching"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="pr-tab-decision"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="customer-fact-snapshot"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="eligibility-result-panel"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="product-candidate-compare"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="product-portfolio-panel"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="recommendation-decision-panel"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('客户事实快照')
    expect(wrapper.text()).toContain('CFS-1')
  })

  it('renders stage path with three stages', async () => {
    await mockLoaded()
    const { wrapper } = await mountWorkspace('run-1')
    expect(wrapper.find('[data-testid="stage-path"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('资格与缺口')
    expect(wrapper.text()).toContain('匹配与组合')
    expect(wrapper.text()).toContain('人工决定')
  })

  it('decision area offers structured APPROVE/MODIFY/REJECT/HOLD and MODIFY uses structured items', async () => {
    await mockLoaded()
    const { wrapper } = await mountWorkspace('run-1')
    expect(wrapper.find('[data-testid="decision-approve"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="decision-modify"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="decision-reject"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="decision-hold"]').exists()).toBe(true)

    await wrapper.get('[data-testid="decision-modify"]').trigger('click')
    expect(wrapper.find('[data-testid="modify-builder"]').exists()).toBe(true)
    // 结构化修改项（非原始 JSON 编辑）：通过字段选择 + 输入组装
    await wrapper.get('[data-testid="modify-product-id"]').setValue('PROD-2')
    await wrapper.get('[data-testid="modify-add"]').trigger('click')
    expect(wrapper.find('[data-testid="modify-list"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="modify-list"]').text()).toContain('移除候选产品')
    expect(wrapper.get('[data-testid="modify-list"]').text()).toContain('PROD-2')
    expect(wrapper.find('textarea').exists()).toBe(false)
  })

  it('STALE_REQUIRES_RERUN blocks approval and prompts rerun', async () => {
    await mockLoaded({ status: 'STALE_REQUIRES_RERUN' })
    const { wrapper } = await mountWorkspace('run-1')
    expect(wrapper.find('[data-testid="decision-stale-banner"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="decision-rerun"]').exists()).toBe(true)
    expect((wrapper.get('[data-testid="decision-approve"]').element as HTMLButtonElement).disabled).toBe(true)
    expect((wrapper.get('[data-testid="decision-modify"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.text()).toContain('STALE_REQUIRES_RERUN')
  })

  it('shows controlled failure empty state when KERT is unreachable', async () => {
    const api = await import('../../api/productRecommendation')
    const networkErr = new Error('Network Error') as Error & { isAxiosError: boolean; response?: unknown; code?: string }
    networkErr.isAxiosError = true
    networkErr.response = undefined
    networkErr.code = 'ECONNREFUSED'
    ;(api.getProductRecommendationRun as ReturnType<typeof vi.fn>).mockRejectedValue(networkErr)
    const { wrapper } = await mountWorkspace('run-1')
    expect(wrapper.find('[data-testid="kert-unreachable"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('KERT（DKWS）不可达')
    expect(wrapper.text()).toContain('INV-07')
  })

  it('renders create form in "new" mode and validates objective before calling createRun', async () => {
    const api = await import('../../api/productRecommendation')
    const { wrapper } = await mountWorkspace('new', { customerId: 'c9' })
    expect(wrapper.find('[data-testid="pr-create-form"]').exists()).toBe(true)
    expect((wrapper.get('[data-testid="pr-create-customer"]').element as HTMLInputElement).value).toBe('c9')
    await wrapper.get('[data-testid="pr-create-form"]').trigger('submit')
    expect(wrapper.find('[data-testid="pr-create-form-error"]').exists()).toBe(true)
    expect(api.createProductRecommendationRun).not.toHaveBeenCalled()
  })

  it('calls createRun with aligned request when form is valid', async () => {
    const api = await import('../../api/productRecommendation')
    ;(api.createProductRecommendationRun as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...mockRun,
      runId: 'run-2',
    })
    const { wrapper } = await mountWorkspace('new', { customerId: 'c9' })
    await wrapper.get('[data-testid="pr-create-objective"]').setValue('扩产融资')
    await wrapper.get('[data-testid="pr-create-journey"]').setValue('JOURNEY-1')
    await wrapper.get('[data-testid="pr-create-form"]').trigger('submit')
    await flushPromises()
    expect(api.createProductRecommendationRun).toHaveBeenCalledTimes(1)
    const call = (api.createProductRecommendationRun as ReturnType<typeof vi.fn>).mock.calls[0]
    expect(call[0]).toMatchObject({ customerId: 'c9', recommendationObjective: '扩产融资', journeyId: 'JOURNEY-1' })
    expect(typeof call[1]).toBe('string')
  })
})
