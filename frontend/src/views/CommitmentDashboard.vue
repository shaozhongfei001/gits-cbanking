<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { NButton, NSkeleton, NTag } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import CommitmentList from '../components/CommitmentList.vue'
import TaskList from '../components/TaskList.vue'
import OpportunityPipeline from '../components/OpportunityPipeline.vue'
import CommitmentForm from '../components/CommitmentForm.vue'
import TaskForm from '../components/TaskForm.vue'
import {
  createCommitment,
  createTask,
  fetchCommitments,
  fetchOpportunities,
  fetchOverdueCommitments,
  fetchOverdueTasks,
  fetchTasks,
  type Commitment,
  type Opportunity,
  type Task,
} from '../api/v11'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P36'
const OBJECT_TYPE = '承诺事项 Commitment/Task'

const pageRefs = usePageReferenceStore()

const commitments = ref<Commitment[]>([])
const tasks = ref<Task[]>([])
const overdueCommitments = ref<Commitment[]>([])
const overdueTasks = ref<Task[]>([])
const opportunities = ref<Opportunity[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const showCommitmentForm = ref(false)
const showTaskForm = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: commitments.value.length > 0 || tasks.value.length > 0 || requested.value,
    requested: requested.value,
  }),
)

const openCount = computed(() => commitments.value.filter(item => item.status === 'OPEN').length)
const pendingCount = computed(() => tasks.value.filter(item => item.status === 'PENDING').length)

/** V8.1: 近期到期——7天内到期的承诺 */
const dueSoonCommitments = computed(() => {
  const now = new Date()
  const week = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  return commitments.value.filter(c => {
    if (c.status !== 'OPEN' || !c.dueDate) return false
    const d = new Date(c.dueDate)
    return d <= week
  })
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'commitment_task_center',
    subtab: 'lists',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadCenter() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    const [commitmentRows, taskRows] = await Promise.all([
      fetchCommitments({}),
      fetchTasks({}),
    ])
    commitments.value = commitmentRows
    tasks.value = taskRows
    const [overdueC, overdueT, opps] = await Promise.allSettled([
      fetchOverdueCommitments(),
      fetchOverdueTasks(),
      fetchOpportunities({}),
    ])
    overdueCommitments.value = overdueC.status === 'fulfilled' ? overdueC.value : []
    overdueTasks.value = overdueT.status === 'fulfilled' ? overdueT.value : []
    opportunities.value = opps.status === 'fulfilled' ? opps.value : []
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取承诺或任务'
    commitments.value = []
    tasks.value = []
  } finally {
    loading.value = false
  }
}

function onCommitmentSelect(item: Commitment) {
  persistReference()
  void item.commitmentId
}

function onTaskSelect(item: Task) {
  persistReference()
  void item.taskId
}

function onOpportunitySelect(item: Opportunity) {
  persistReference()
  void item.opportunityId
}

async function onCreateCommitment(data: Parameters<typeof createCommitment>[0]) {
  try {
    await createCommitment(data)
    showCommitmentForm.value = false
    await loadCenter()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '创建承诺失败'
  }
}

async function onCreateTask(data: Parameters<typeof createTask>[0]) {
  try {
    await createTask(data)
    showTaskForm.value = false
    await loadCenter()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '创建任务失败'
  }
}

onMounted(loadCenter)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="commitment-dashboard" data-testid="p36-commitments" data-page-id="P36">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="中心"
      title="承诺事项"
    />

    <p class="page-desc">跟踪承诺履行与任务进展，逾期项需优先处理。</p>

    <div class="toolbar">
      <button
        type="button"
        class="btn-add"
        data-testid="p36-create-commitment"
        @click="showCommitmentForm = true"
      >
        + 新增承诺
      </button>
      <button type="button" class="btn-add" data-testid="p36-create-task" @click="showTaskForm = true">
        + 新增任务
      </button>
      <DisabledAction
        label="从需求生成任务"
        :disabled="true"
        reason="Need 无正式合同对象，禁止从非正式 Need 生成任务"
        unlockPath="待 Need 合同批准后由后续 Loop 启用派生写"
      />
    </div>

    <!-- Loading 骨架 -->
    <div v-if="loading" class="skeleton-area" data-testid="loading-state" aria-busy="true" aria-label="加载中">
      <div class="skeleton-summary">
        <n-skeleton text :width="200" />
        <n-skeleton text :width="160" />
      </div>
      <div class="skeleton-grid">
        <n-skeleton v-for="i in 4" :key="i" text :width="320" style="margin-bottom: 10px" />
      </div>
    </div>

    <!-- Error 状态 -->
    <div v-else-if="error" class="error-block" data-testid="p36-error">
      <p class="error-text">加载失败：{{ error }}</p>
      <n-button size="small" @click="loadCenter">重试</n-button>
    </div>

    <template v-else>
      <!-- V8.1: 两个可行动摘要——近期到期 + 逾期需处理 -->
      <div class="action-summary">
        <div class="summary-card summary-card--due">
          <span class="summary-card__count">{{ dueSoonCommitments.length }}</span>
          <span class="summary-card__label">近期到期（7天内）</span>
        </div>
        <div class="summary-card summary-card--overdue">
          <span class="summary-card__count">{{ overdueCommitments.length + overdueTasks.length }}</span>
          <span class="summary-card__label">逾期需处理</span>
        </div>
      </div>

      <!-- 逾期提醒 -->
      <div v-if="overdueCommitments.length > 0 || overdueTasks.length > 0" class="overdue-alert">
        <span class="overdue-alert__icon">⚠</span>
        <span>有 {{ overdueCommitments.length }} 项承诺和 {{ overdueTasks.length }} 项任务已逾期，请优先处理。</span>
      </div>

      <!-- 空态 -->
      <div v-if="!commitments.length && !tasks.length" class="empty-state" data-testid="p36-empty">
        <p class="empty-title">暂无承诺或任务</p>
        <p class="empty-desc">当有客户承诺或待办任务时，它们将出现在此处。</p>
      </div>

      <!-- 承诺与任务双栏 -->
      <div v-else class="dashboard-grid">
        <section class="section">
          <div class="section-header">
            <h2>承诺列表</h2>
            <n-tag size="small" :bordered="false">{{ openCount }} 项待履行</n-tag>
          </div>
          <CommitmentList :commitments="commitments" :loading="false" @select="onCommitmentSelect" />
        </section>
        <section class="section">
          <div class="section-header">
            <h2>任务列表</h2>
            <n-tag size="small" :bordered="false">{{ pendingCount }} 项待处理</n-tag>
          </div>
          <TaskList :tasks="tasks" :loading="false" @select="onTaskSelect" />
        </section>
      </div>

      <!-- 商机管线（可折叠） -->
      <details class="opportunity-section">
        <summary class="opportunity-toggle">商机阶段摘要（{{ opportunities.length }} 项）</summary>
        <OpportunityPipeline :opportunities="opportunities" @select="onOpportunitySelect" />
      </details>
    </template>

    <!-- 创建承诺弹窗 -->
    <div v-if="showCommitmentForm" class="modal-overlay" @click.self="showCommitmentForm = false">
      <div class="modal-content" role="dialog" aria-label="创建承诺">
        <h3>创建承诺</h3>
        <CommitmentForm @submit="onCreateCommitment" @cancel="showCommitmentForm = false" />
      </div>
    </div>

    <!-- 创建任务弹窗 -->
    <div v-if="showTaskForm" class="modal-overlay" @click.self="showTaskForm = false">
      <div class="modal-content" role="dialog" aria-label="创建任务">
        <h3>创建任务</h3>
        <TaskForm @submit="onCreateTask" @cancel="showTaskForm = false" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.commitment-dashboard {
  max-width: 1240px;
  padding: 32px 34px 48px;
}

.page-desc {
  color: var(--v8-nav-text);
  font-size: 14px;
  margin: -4px 0 16px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.btn-add {
  padding: 6px 14px;
  background: var(--brand-primary);
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s ease;
}
.btn-add:hover {
  background: var(--brand-primary-light);
}
.btn-add:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

/* 骨架 */
.skeleton-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.skeleton-summary {
  display: flex;
  gap: 20px;
}
.skeleton-grid {
  display: flex;
  flex-direction: column;
}

/* 错误 */
.error-block {
  padding: 24px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  text-align: center;
}
.error-text {
  color: var(--color-error, #C0392B);
  margin-bottom: 12px;
  font-size: 14px;
}

/* V8.1: 两个可行动摘要卡片 */
.action-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}
.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 10px;
  border: 1px solid var(--border-light);
  background: var(--bg-surface);
  flex: 1;
}
.summary-card--due {
  border-left: 3px solid var(--color-warning, #836239);
}
.summary-card--overdue {
  border-left: 3px solid var(--color-error, #C0392B);
}
.summary-card__count {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.summary-card__label {
  font-size: 14px;
  color: var(--v8-nav-text);
}

/* 逾期提醒 */
.overdue-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(192, 57, 43, 0.06);
  border: 1px solid rgba(192, 57, 43, 0.15);
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-error, #C0392B);
  margin-bottom: 20px;
}
.overdue-alert__icon {
  font-size: 16px;
}

/* 双栏布局 */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.section h2 {
  font-size: 18px;
  color: var(--text-primary);
  margin: 0;
  font-weight: 600;
}

/* 商机折叠区 */
.opportunity-section {
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 12px 18px;
  background: var(--bg-surface);
}
.opportunity-toggle {
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: var(--brand-primary);
  padding: 4px 0;
}
.opportunity-toggle:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}

/* 空态 */
.empty-state {
  padding: 40px 24px;
  text-align: center;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
}
.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.empty-desc {
  font-size: 13px;
  color: var(--v8-nav-text);
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #FFFFFF;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  box-shadow: 0 8px 24px rgba(17, 45, 64, 0.12);
  min-width: 400px;
  max-width: 600px;
}
.modal-content h3 {
  font-size: 18px;
  color: var(--text-primary);
  margin: 0 0 16px;
  font-weight: 600;
}

/* 中宽屏 */
@media (max-width: 1024px) {
  .commitment-dashboard {
    padding: 24px 24px 40px;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

/* 手机 */
@media (max-width: 640px) {
  .commitment-dashboard {
    padding: 16px 16px 32px;
  }
  .action-summary {
    flex-direction: column;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .modal-content {
    min-width: 0;
    margin: 16px;
  }
}
</style>
