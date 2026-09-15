<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
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
const OBJECT_TYPE = '任务与承诺 Commitment/Task'

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
      title="任务与承诺中心"
    />
    <div class="toolbar">
      <DisabledAction
        label="从需求生成任务"
        :disabled="true"
        reason="Need 无正式合同对象，禁止从非正式 Need 生成任务或发明新字段"
        unlockPath="待 Need 合同批准后由后续 Loop 启用派生写"
      />
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
    </div>
    <p class="hint">C0：消费既有 fetchCommitments / fetchTasks。可保留 createCommitment / createTask，不发明新字段。</p>
    <PageState :status="status" :error="error" idle-description="尚未请求承诺与任务" @retry="loadCenter">
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-value">{{ openCount }}</span>
          <span class="stat-label">待履行承诺</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ overdueCommitments.length }}</span>
          <span class="stat-label">逾期承诺</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ pendingCount }}</span>
          <span class="stat-label">待处理任务</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ overdueTasks.length }}</span>
          <span class="stat-label">逾期任务</span>
        </div>
      </div>
      <p v-if="!commitments.length && !tasks.length" class="empty">暂无承诺或任务</p>
      <div class="dashboard-grid">
        <section class="section">
          <div class="section-header">
            <h2>承诺列表</h2>
          </div>
          <CommitmentList :commitments="commitments" :loading="false" @select="onCommitmentSelect" />
        </section>
        <section class="section">
          <div class="section-header">
            <h2>任务列表</h2>
          </div>
          <TaskList :tasks="tasks" :loading="false" @select="onTaskSelect" />
        </section>
      </div>
      <section class="section full-width">
        <OpportunityPipeline :opportunities="opportunities" @select="onOpportunitySelect" />
      </section>
    </PageState>

    <div v-if="showCommitmentForm" class="modal-overlay" @click.self="showCommitmentForm = false">
      <div class="modal-content">
        <h3>创建承诺</h3>
        <CommitmentForm @submit="onCreateCommitment" @cancel="showCommitmentForm = false" />
      </div>
    </div>
    <div v-if="showTaskForm" class="modal-overlay" @click.self="showTaskForm = false">
      <div class="modal-content">
        <h3>创建任务</h3>
        <TaskForm @submit="onCreateTask" @cancel="showTaskForm = false" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.stats-bar {
  display: flex;
  gap: var(--space-6);
  margin-bottom: var(--space-6);
  padding: var(--space-5) var(--space-6);
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-primary-light));
  border-radius: var(--radius-lg);
  color: var(--text-inverse);
  box-shadow: var(--shadow-md);
}
.stat-item { display: flex; flex-direction: column; align-items: center; min-width: 80px; }
.stat-value { font-size: var(--text-3xl); font-weight: 700; }
.stat-label { font-size: var(--text-xs); opacity: 0.85; margin-top: 2px; }
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}
.section h2 { font-size: var(--text-lg); color: var(--text-primary); margin: 0 0 var(--space-3); font-weight: 600; }
.btn-add {
  padding: var(--space-2) var(--space-3);
  background: var(--brand-primary);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-sm);
}
.full-width { grid-column: 1 / -1; }
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: var(--bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
}
.modal-content {
  background: var(--bg-surface);
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xl);
  min-width: 400px;
  max-width: 600px;
}
.modal-content h3 { font-size: var(--text-lg); color: var(--text-primary); margin: 0 0 var(--space-4); font-weight: 600; }
</style>
