import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ReviewRequiredPanel from '../ReviewRequiredPanel.vue'
import { createTask } from '../../../api/v11'
import type { ReviewRequiredItem } from '../types'
import type { Task } from '../../../api/v11'

vi.mock('../../../api/v11', () => ({
  createTask: vi.fn(),
}))

const mockedCreateTask = vi.mocked(createTask)

// naive-ui 组件 `name` 选项不带 N 前缀（如 NButton → Button），stubs 需按 name 匹配。
const stubs = {
  Button: {
    props: ['disabled'],
    template: '<button class="n-button-stub" :disabled="disabled"><slot /></button>',
  },
  Tag: { template: '<span class="n-tag-stub"><slot /></span>' },
  Empty: { template: '<div class="n-empty-stub"><slot /></div>' },
  Alert: { props: ['title'], template: '<div class="n-alert-stub"><slot />{{ title }}</div>' },
  Space: { template: '<div class="n-space-stub"><slot /></div>' },
}

function createTaskStub(overrides: Partial<Task> = {}): Task {
  return {
    taskId: 'TASK-1',
    taskType: 'REVIEW',
    title: '专家协同：PROD-1@2.2',
    status: 'PENDING',
    ...overrides,
  }
}

function mountPanel(props: Record<string, unknown> = {}) {
  return mount(ReviewRequiredPanel, {
    props: {
      items: [],
      runId: 'REC-1',
      customerId: 'CUST-1',
      operatingCaseId: 'OC-1',
      ...props,
    },
    global: { stubs },
  })
}

const reviewItem: ReviewRequiredItem = {
  productId: 'PROD-1',
  productVersion: '2.2',
  eligibility: 'REVIEW_REQUIRED',
  reason: '产品需风险专家复核准入边界',
  reasonCode: 'REVIEW_ADMISSION_BOUNDARY',
  ruleId: 'PR-ADM-004',
  requiredExpertise: '风险专家',
  suggestedAction: '复核客户行业准入边界',
}

const unknownItem: ReviewRequiredItem = {
  productId: 'PROD-2',
  eligibility: 'UNKNOWN',
  reason: '缺少客户行业分类事实',
  suggestedAction: '补齐行业分类后重新评估',
}

describe('ReviewRequiredPanel', () => {
  beforeEach(() => {
    mockedCreateTask.mockReset()
    mockedCreateTask.mockResolvedValue(createTaskStub())
  })

  it('renders REVIEW_REQUIRED item with reason and expert-collaboration entry', () => {
    const wrapper = mountPanel({ items: [reviewItem] })
    expect(wrapper.find('[data-testid="review-eligibility"]').text()).toContain('需复核')
    expect(wrapper.find('[data-testid="review-product"]').text()).toBe('PROD-1@2.2')
    expect(wrapper.find('[data-testid="review-reason"]').text()).toBe(reviewItem.reason)
    expect(wrapper.find('[data-testid="review-rule"]').text()).toContain('PR-ADM-004')
    expect(wrapper.find('[data-testid="create-task-button"]').text()).toBe('创建专家协同任务')
  })

  it('renders UNKNOWN item with follow-up entry', () => {
    const wrapper = mountPanel({ items: [unknownItem] })
    expect(wrapper.find('[data-testid="review-eligibility"]').text()).toContain('未知')
    expect(wrapper.find('[data-testid="create-task-button"]').text()).toBe('创建待核实任务')
  })

  it('creates a REVIEW task associated with runId on REVIEW_REQUIRED item', async () => {
    const wrapper = mountPanel({ items: [reviewItem] })
    await wrapper.find('[data-testid="create-task-button"]').trigger('click')
    await flushPromises()

    expect(mockedCreateTask).toHaveBeenCalledTimes(1)
    const payload = mockedCreateTask.mock.calls[0][0] as Record<string, unknown>
    expect(payload.taskType).toBe('REVIEW')
    expect(payload.runId).toBe('REC-1')
    expect(payload.customerId).toBe('CUST-1')
    expect(payload.operatingCaseId).toBe('OC-1')
    expect(String(payload.description)).toContain('REC-1')
    expect(String(payload.title)).toContain('PROD-1@2.2')
    expect(wrapper.emitted('created')).toBeTruthy()
  })

  it('creates a FOLLOW_UP task for UNKNOWN item', async () => {
    const wrapper = mountPanel({ items: [unknownItem] })
    await wrapper.find('[data-testid="create-task-button"]').trigger('click')
    await flushPromises()

    const payload = mockedCreateTask.mock.calls[0][0] as Record<string, unknown>
    expect(payload.taskType).toBe('FOLLOW_UP')
    expect(payload.runId).toBe('REC-1')
  })

  it('marks item as created and disables its button after success', async () => {
    const wrapper = mountPanel({ items: [reviewItem] })
    await wrapper.find('[data-testid="create-task-button"]').trigger('click')
    await flushPromises()

    expect(wrapper.find('[data-testid="create-task-button"]').text()).toBe('已创建任务')
    expect(wrapper.find('[data-testid="create-task-button"]').attributes('disabled')).toBeDefined()
  })

  it('shows error message and emits error when createTask rejects', async () => {
    mockedCreateTask.mockRejectedValue(new Error('创建任务失败'))
    const wrapper = mountPanel({ items: [reviewItem] })
    await wrapper.find('[data-testid="create-task-button"]').trigger('click')
    await flushPromises()

    expect(wrapper.find('.n-alert-stub').exists()).toBe(true)
    expect(wrapper.text()).toContain('创建任务失败')
    expect(wrapper.emitted('error')).toBeTruthy()
  })

  it('renders empty state when there are no review items', () => {
    const wrapper = mountPanel({ items: [] })
    expect(wrapper.find('[data-testid="review-empty"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="review-item"]').exists()).toBe(false)
  })
})
