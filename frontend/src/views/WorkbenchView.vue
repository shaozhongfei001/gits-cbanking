<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NSpin, NSkeleton, NTag } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { fetchCustomers, type Customer, CUSTOMER_TIER_LABELS, RISK_LEVEL_LABELS } from '../api/engagement'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P01'
const OBJECT_TYPE = '客户经营应用'

const router = useRouter()
const pageRefs = usePageReferenceStore()

const customers = ref<Customer[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const filter = ref('')
const subtab = ref('queue')
const draftNote = ref('')
const snapshot = ref<Customer[] | null>(null)

const status = computed(() => {
  if (loading.value) {
    return 'loading' as const
  }
  if (error.value && !snapshot.value) {
    return 'error' as const
  }
  if (customers.value.length > 0 || snapshot.value !== null) {
    return 'success' as const
  }
  if (error.value) {
    return 'error' as const
  }
  return requested.value ? 'success' as const : 'idle' as const
})

/** C1 View Model：行动队列由既有客户列表派生，推荐不等于自动执行。 */
const actionQueue = computed(() => {
  const source = customers.value.length ? customers.value : (snapshot.value ?? [])
  return [...source]
    .map(customer => ({
      customerId: customer.customerId,
      customerName: customer.customerName,
      riskLevel: customer.riskLevel,
      customerTier: customer.customerTier,
      candidateReason: deriveCandidateReason(customer),
    }))
    .filter(item => !filter.value || item.customerName.includes(filter.value) || item.candidateReason.includes(filter.value))
    .sort((a, b) => rank(b) - rank(a))
})

/** V8.1: 最近经营脉络——从客户列表派生最近活跃客户（简化演示，真实场景由旅程 API 提供） */
const recentThreads = computed(() => {
  const source = customers.value.length ? customers.value : (snapshot.value ?? [])
  return source.slice(0, 5).map(c => ({
    customerId: c.customerId,
    customerName: c.customerName,
    lastAction: '经营检视',
    time: '近期',
  }))
})

/** V8.1: 待完成承诺——从客户列表中高风险客户派生（简化演示，真实场景由承诺 API 提供） */
const pendingCommitments = computed(() => {
  const source = customers.value.length ? customers.value : (snapshot.value ?? [])
  return source
    .filter(c => c.riskLevel === 'HIGH' || c.customerTier === 'STRATEGIC')
    .slice(0, 4)
    .map(c => ({
      customerId: c.customerId,
      customerName: c.customerName,
      commitment: c.riskLevel === 'HIGH' ? '风险跟进' : '战略客户检视',
      dueLabel: '待处理',
    }))
})

/** V8.1: 当前重点任务——队列中最高优先级的 1 项 */
const focusTask = computed(() => actionQueue.value[0] ?? null)

function rank(item: { riskLevel?: string; customerTier?: string }): number {
  const risk = item.riskLevel === 'HIGH' ? 30 : item.riskLevel === 'MEDIUM' ? 20 : 10
  const tier = item.customerTier === 'STRATEGIC' ? 4 : item.customerTier === 'KEY' ? 3 : item.customerTier === 'GROWTH' ? 2 : 1
  return risk + tier
}

function deriveCandidateReason(customer: Customer): string {
  if (customer.riskLevel === 'HIGH') {
    return '高风险客户需跟进（候选，非自动执行）'
  }
  if (customer.customerTier === 'STRATEGIC') {
    return '战略客户经营检视（候选）'
  }
  return '常规经营检视（候选）'
}

function riskTagType(level?: string): 'error' | 'warning' | 'default' {
  if (level === 'HIGH') return 'error'
  if (level === 'MEDIUM') return 'warning'
  return 'default'
}

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'daily_workbench',
    filter: filter.value,
    subtab: subtab.value,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
    draftId: draftNote.value || undefined,
  })
}

async function loadCustomers() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    customers.value = await fetchCustomers()
    snapshot.value = customers.value
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取客户列表'
    if (snapshot.value) {
      customers.value = snapshot.value
    }
  } finally {
    loading.value = false
  }
}

function openCustomer(id: string) {
  persistReference()
  router.push({ name: 'CustomerOperatingView', params: { id } })
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  filter.value = restored.filter ?? ''
  subtab.value = restored.subtab ?? 'queue'
  draftNote.value = restored.draftId ?? ''
  loadCustomers()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="workbench" data-testid="p01-workbench">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="今日"
      title="经营总览"
    />

    <p class="work-summary">今天的经营重点：关注高风险客户跟进与战略客户检视，行动队列由客户列表派生，推荐不等于自动执行。</p>

    <!-- V8.1: 当前重点任务深蓝提示块 -->
    <div v-if="focusTask && !loading" class="focus-block" data-testid="p01-focus-task">
      <div class="focus-block__label">当前重点</div>
      <div class="focus-block__customer">{{ focusTask.customerName }}</div>
      <div class="focus-block__reason">{{ focusTask.candidateReason }}</div>
      <n-button size="small" type="info" ghost @click="openCustomer(focusTask.customerId)">进入客户</n-button>
    </div>

    <div class="workbench-body">
      <!-- 主列 2/3：行动队列 -->
      <section class="main-col">
        <div class="toolbar">
          <input
            v-model="filter"
            class="filter-input"
            data-testid="p01-filter"
            placeholder="筛选客户或候选原因"
            aria-label="筛选客户或候选原因"
            @change="persistReference"
          />
          <DisabledAction
            label="确认型操作"
            :disabled="true"
            reason="P30 只读切片禁止确认型写操作；队列失败时仅展示快照"
            unlockPath="后续 Loop 在合同批准后启用确认型 Action"
          />
        </div>

        <!-- Loading 骨架 -->
        <div v-if="loading" class="skeleton-list" data-testid="loading-state" aria-busy="true" aria-label="加载中">
          <div v-for="i in 4" :key="i" class="skeleton-row">
            <n-skeleton text :width="140" />
            <n-skeleton text :width="60" />
            <n-skeleton text :width="80" />
            <n-skeleton text :width="200" />
          </div>
        </div>

        <!-- Error 状态 -->
        <div v-else-if="error && !snapshot" class="error-block" data-testid="error-state">
          <p class="error-text">加载失败：{{ error }}</p>
          <n-button size="small" data-testid="retry-action" @click="loadCustomers">重试</n-button>
        </div>

        <!-- 降级状态 -->
        <div v-else-if="error && snapshot" class="degraded" data-testid="p01-degraded">
          队列服务不可用，展示最近成功快照；确认型操作已禁用。
        </div>

        <!-- 成功有数据 -->
        <template v-else-if="actionQueue.length > 0">
          <div data-testid="success-state">
          <ul class="queue" data-testid="p01-action-queue">
            <li v-for="item in actionQueue" :key="item.customerId" class="queue-item">
              <button type="button" class="queue-link" @click="openCustomer(item.customerId)">
                {{ item.customerName }}
              </button>
              <n-tag :type="riskTagType(item.riskLevel)" size="small" round>
                {{ item.riskLevel ? RISK_LEVEL_LABELS[item.riskLevel] : '-' }}
              </n-tag>
              <span class="tier-label">{{ item.customerTier ? CUSTOMER_TIER_LABELS[item.customerTier] : '-' }}</span>
              <span class="reason">{{ item.candidateReason }}</span>
              <n-button size="tiny" quaternary type="primary" @click="openCustomer(item.customerId)">进入客户</n-button>
            </li>
          </ul>
          </div>
        </template>

        <!-- 真空数据空态 -->
        <div v-else class="empty-state" data-testid="p01-empty">
          <p class="empty-title">目前没有待处理行动</p>
          <p class="empty-desc">行动队列由客户列表派生。当有高风险或战略客户需要跟进时，行动项将出现在此处。</p>
          <n-button size="small" @click="router.push('/accounts')">前往客户组合</n-button>
        </div>
      </section>

      <!-- 右列 1/3：经营脉络与待完成承诺 -->
      <aside class="side-col">
        <!-- 最近经营脉络 -->
        <div class="side-section">
          <h3 class="side-section__title">最近经营脉络</h3>
          <div v-if="loading" class="side-skeleton" aria-busy="true">
            <n-skeleton v-for="i in 3" :key="i" text :width="180" style="margin-bottom: 8px" />
          </div>
          <ul v-else-if="recentThreads.length" class="thread-list">
            <li v-for="t in recentThreads" :key="t.customerId" class="thread-item">
              <button type="button" class="thread-link" @click="openCustomer(t.customerId)">{{ t.customerName }}</button>
              <span class="thread-meta">{{ t.lastAction }} · {{ t.time }}</span>
            </li>
          </ul>
          <p v-else class="side-empty">暂无最近经营记录</p>
        </div>

        <!-- 待完成承诺 -->
        <div class="side-section">
          <h3 class="side-section__title">待完成承诺</h3>
          <div v-if="loading" class="side-skeleton" aria-busy="true">
            <n-skeleton v-for="i in 2" :key="i" text :width="160" style="margin-bottom: 8px" />
          </div>
          <ul v-else-if="pendingCommitments.length" class="commitment-list">
            <li v-for="c in pendingCommitments" :key="c.customerId" class="commitment-item">
              <button type="button" class="commitment-link" @click="openCustomer(c.customerId)">{{ c.customerName }}</button>
              <span class="commitment-label">{{ c.commitment }}</span>
              <n-tag size="small" :bordered="false" type="warning">{{ c.dueLabel }}</n-tag>
            </li>
          </ul>
          <p v-else class="side-empty">暂无待完成承诺</p>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.workbench {
  max-width: 1240px;
  padding: 32px 34px 48px;
}

.work-summary {
  color: var(--v8-nav-text);
  font-size: 14px;
  margin: -4px 0 20px;
  line-height: 1.5;
}

/* V8.1: 深蓝重点任务提示块——全页唯一深色大块 */
.focus-block {
  background: var(--v8-dark);
  color: #FFFFFF;
  border-radius: 12px;
  padding: 18px 22px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.focus-block__label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.7;
  font-weight: 600;
}
.focus-block__customer {
  font-size: 16px;
  font-weight: 600;
}
.focus-block__reason {
  font-size: 13px;
  opacity: 0.85;
  flex: 1;
  min-width: 120px;
}

/* 双栏布局 */
.workbench-body {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(260px, 0.85fr);
  gap: 28px;
  align-items: start;
}

/* 主列 */
.main-col {
  min-width: 0;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.filter-input {
  min-width: 240px;
  height: 36px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 0 14px;
  font-size: 13px;
  background: var(--bg-surface);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.filter-input:focus {
  outline: none;
  border-color: var(--v8-focus-on-light);
  box-shadow: 0 0 0 3px rgba(44, 70, 174, 0.15);
}
.filter-input:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

/* 骨架 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skeleton-row {
  display: grid;
  grid-template-columns: 140px 60px 80px 1fr;
  gap: 12px;
  padding: 14px 18px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
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

.degraded {
  margin-bottom: 12px;
  color: var(--color-warning, #836239);
  font-size: 13px;
  padding: 10px 14px;
  background: rgba(131, 98, 57, 0.06);
  border-radius: 8px;
}

/* 行动队列 */
.queue {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.queue-item {
  display: grid;
  grid-template-columns: 1.4fr auto auto 1.4fr auto;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  align-items: center;
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.queue-item:hover {
  border-color: var(--border-normal);
  box-shadow: 0 1px 2px rgba(17, 45, 64, 0.05);
}
.queue-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  text-align: left;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: color 0.15s ease;
}
.queue-link:hover {
  color: var(--brand-primary-light);
}
.queue-link:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}
.tier-label {
  font-size: 12px;
  color: var(--v8-nav-text);
}
.reason {
  color: var(--v8-nav-text);
  font-size: 13px;
}

/* 真空数据空态 */
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
  margin-bottom: 16px;
}

/* 右列 */
.side-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.side-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 16px 18px;
}
.side-section__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px;
}
.side-empty {
  font-size: 13px;
  color: var(--v8-nav-text);
}
.side-skeleton {
  display: flex;
  flex-direction: column;
}

/* 经营脉络 */
.thread-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.thread-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.thread-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  text-align: left;
  transition: color 0.15s ease;
}
.thread-link:hover {
  color: var(--brand-primary-light);
}
.thread-link:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}
.thread-meta {
  font-size: 11px;
  color: var(--v8-nav-text);
  white-space: nowrap;
}

/* 待完成承诺 */
.commitment-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.commitment-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.commitment-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  text-align: left;
  transition: color 0.15s ease;
}
.commitment-link:hover {
  color: var(--brand-primary-light);
}
.commitment-link:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}
.commitment-label {
  font-size: 12px;
  color: var(--v8-nav-text);
  flex: 1;
}

/* 中宽屏：右列下移 */
@media (max-width: 1024px) {
  .workbench-body {
    grid-template-columns: 1fr;
  }
  .workbench {
    padding: 24px 24px 40px;
  }
}

/* 手机 */
@media (max-width: 640px) {
  .workbench {
    padding: 16px 16px 32px;
  }
  .focus-block {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .queue-item {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
