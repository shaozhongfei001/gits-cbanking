import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CommitmentDashboard from '../CommitmentDashboard.vue'
import type { Commitment, Task } from '../../api/v11'

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchCommitments: vi.fn(),
    fetchTasks: vi.fn(),
    fetchOverdueCommitments: vi.fn(),
    fetchOverdueTasks: vi.fn(),
    createCommitment: vi.fn(),
    createTask: vi.fn(),
    fetchOpportunities: vi.fn(),
  }
})

const mockCommitment: Commitment = {
  commitmentId: 'cm-1',
  commitmentType: 'RM_COMMITMENT',
  content: '本周回访资金缺口',
  status: 'OPEN',
}

const mockTask: Task = {
  taskId: 'tk-1',
  taskType: 'FOLLOW_UP',
  title: '准备结算材料',
  status: 'PENDING',
}

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  CommitmentList: {
    props: ['commitments'],
    template: '<div data-testid="p36-commitment-list">{{ commitments.map(c => c.content).join(",") }}</div>',
  },
  TaskList: {
    props: ['tasks'],
    template: '<div data-testid="p36-task-list">{{ tasks.map(t => t.title).join(",") }}</div>',
  },
  OpportunityPipeline: { template: '<div data-testid="p36-opportunity-pipeline" />' },
  CommitmentForm: { template: '<form data-testid="p36-commitment-form" />' },
  TaskForm: { template: '<form data-testid="p36-task-form" />' },
}

async function mountP36() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/commitments', name: 'CommitmentDashboard', component: CommitmentDashboard }],
  })
  await router.push('/commitments')
  const wrapper = mount(CommitmentDashboard, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P36 CommitmentDashboard C0', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully from fetchCommitments and fetchTasks', async () => {
    const { fetchCommitments, fetchTasks, fetchOverdueCommitments, fetchOverdueTasks, fetchOpportunities } = await import('../../api/v11')
    ;(fetchCommitments as ReturnType<typeof vi.fn>).mockResolvedValue([mockCommitment])
    ;(fetchTasks as ReturnType<typeof vi.fn>).mockResolvedValue([mockTask])
    ;(fetchOverdueCommitments as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchOverdueTasks as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchOpportunities as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP36()
    expect(wrapper.get('[data-testid="p36-commitments"]').text()).toContain('任务与承诺')
    expect(wrapper.get('[data-testid="p36-commitments"]').attributes('data-page-id')).toBe('P36')
    expect(wrapper.find('[data-testid="object-header"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('本周回访资金缺口')
    expect(wrapper.text()).toContain('准备结算材料')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when commitments and tasks are empty', async () => {
    const { fetchCommitments, fetchTasks, fetchOverdueCommitments, fetchOverdueTasks, fetchOpportunities } = await import('../../api/v11')
    ;(fetchCommitments as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchTasks as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchOverdueCommitments as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchOverdueTasks as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchOpportunities as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP36()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchCommitments fails', async () => {
    const { fetchCommitments, fetchTasks } = await import('../../api/v11')
    ;(fetchCommitments as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('forbidden'))
    ;(fetchTasks as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP36()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('keeps Need-derived task generation disabled while C0 createCommitment remains available', async () => {
    const { fetchCommitments, fetchTasks, fetchOverdueCommitments, fetchOverdueTasks, fetchOpportunities } = await import('../../api/v11')
    ;(fetchCommitments as ReturnType<typeof vi.fn>).mockResolvedValue([mockCommitment])
    ;(fetchTasks as ReturnType<typeof vi.fn>).mockResolvedValue([mockTask])
    ;(fetchOverdueCommitments as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchOverdueTasks as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchOpportunities as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP36()
    expect((wrapper.get('[data-testid="gated-action"]').element as HTMLButtonElement).disabled).toBe(true)
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
    expect((wrapper.get('[data-testid="p36-create-commitment"]').element as HTMLButtonElement).disabled).toBe(false)
  })
})
