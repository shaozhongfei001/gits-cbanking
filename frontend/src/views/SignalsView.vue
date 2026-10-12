<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NInput, NButton, NSkeleton, NTag, NSelect } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import {
  fetchCustomers,
  fetchCustomerContext,
  SIGNAL_TYPE_LABELS,
  SIGNAL_STATUS_LABELS,
  type OpportunitySignal,
} from '../api/engagement'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P08'
const OBJECT_TYPE = '经营信号 Signal'

type SignalRow = OpportunitySignal & {
  customerId: string
  customerName: string
}

const router = useRouter()
const pageRefs = usePageReferenceStore()

const signals = ref<SignalRow[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const filter = ref('')
const typeFilter = ref<string | null>(null)
const statusFilter = ref<string | null>(null)

const typeOptions = Object.entries(SIGNAL_TYPE_LABELS).map(([value, label]) => ({ label, value }))
const statusOptions = Object.entries(SIGNAL_STATUS_LABELS).map(([value, label]) => ({ label, value }))

const visible = computed(() => {
  let result = signals.value
  const q = filter.value.trim()
  if (q) {
    result = result.filter(item =>
      item.content.includes(q) || item.customerName.includes(q) || item.signalId.includes(q),
    )
  }
  if (typeFilter.value) {
    result = result.filter(item => item.signalType === typeFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter(item => item.status === statusFilter.value)
  }
  return result
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'signal_list',
    filter: filter.value,
    subtab: 'list',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadSignals() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    const list = await fetchCustomers()
    const rows: SignalRow[] = []
    for (const customer of list) {
      const ctx = await fetchCustomerContext(customer.customerId)
      for (const signal of ctx.opportunitySignals ?? []) {
        rows.push({
          ...signal,
          customerId: customer.customerId,
          customerName: customer.customerName,
        })
      }
    }
    signals.value = rows
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取经营信号'
    signals.value = []
  } finally {
    loading.value = false
  }
}

function openSignal(id: string) {
  persistReference()
  router.push({ name: 'SignalRecord', params: { id } })
}

function openCustomer(id: string) {
  persistReference()
  router.push({ name: 'CustomerOperatingView', params: { id } })
}

function signalStatusType(status?: string): 'success' | 'warning' | 'error' | 'default' {
  if (status === 'CONFIRMED') return 'success'
  if (status === 'DISMISSED') return 'default'
  if (status === 'EXPIRED') return 'warning'
  return 'warning'
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  filter.value = restored.filter ?? ''
  loadSignals()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="signals-view" data-testid="p08-signals">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="信号台"
      title="经营信号"
    />

    <p class="page-desc">待判断的经营信号：关注客户变化与业务影响，推荐不等于自动执行。</p>

    <SignalsDomainTabs />

    <div class="toolbar">
      <n-input
        v-model:value="filter"
        data-testid="p08-filter"
        placeholder="搜索信号内容或客户"
        aria-label="搜索信号"
        style="max-width: 260px"
        clearable
        @update:value="persistReference"
      />
      <n-select
        v-model:value="typeFilter"
        :options="typeOptions"
        placeholder="信号类型"
        clearable
        style="width: 140px"
        aria-label="筛选信号类型"
      />
      <n-select
        v-model:value="statusFilter"
        :options="statusOptions"
        placeholder="状态"
        clearable
        style="width: 120px"
        aria-label="筛选信号状态"
      />
      <DisabledAction
        label="批量指派"
        :disabled="true"
        reason="本 Loop 禁止信号写回"
        unlockPath="后续 Loop 在明确授权后启用受控写 Action"
      />
      <!-- 跨页入口：侧栏无 /engagements 菜单项，删掉这里会让 P10 互动对象主页成为孤儿页（D-4） -->
      <router-link class="related-link" to="/engagements" data-testid="p08-open-engagements">
        互动对象
      </router-link>
      <router-link class="related-link" to="/engagement" data-testid="p08-open-journey">
        经营旅程
      </router-link>
    </div>

    <!-- 筛选结果计数 -->
    <div v-if="!loading && requested" class="filter-summary">
      <span v-if="filter.trim() || typeFilter || statusFilter">筛选结果：{{ visible.length }} / {{ signals.length }} 条信号</span>
      <span v-else>共 {{ signals.length }} 条信号</span>
    </div>

    <!-- Loading 骨架 -->
    <div v-if="loading" class="skeleton-list" data-testid="loading-state" aria-busy="true" aria-label="加载中">
      <div v-for="i in 4" :key="i" class="skeleton-row">
        <n-skeleton text :width="180" />
        <n-skeleton text :width="100" />
        <n-skeleton text :width="80" />
        <n-skeleton text :width="60" />
      </div>
    </div>

    <!-- Error 状态 -->
    <div v-else-if="error" class="error-block" data-testid="p08-error">
      <p class="error-text">加载失败：{{ error }}</p>
      <n-button size="small" @click="loadSignals">重试</n-button>
    </div>

    <!-- 信号列表 -->
    <template v-else>
      <ul v-if="visible.length" class="signal-list" data-testid="p08-signal-list">
        <li v-for="item in visible" :key="item.signalId" class="signal-item">
          <div class="signal-main">
            <button type="button" class="signal-customer" @click="openCustomer(item.customerId)">
              {{ item.customerName }}
            </button>
            <span class="signal-impact">{{ item.content }}</span>
          </div>
          <div class="signal-meta">
            <n-tag size="small" :bordered="false">{{ SIGNAL_TYPE_LABELS[item.signalType] || item.signalType }}</n-tag>
            <n-tag size="small" :type="signalStatusType(item.status)" :bordered="false">{{ SIGNAL_STATUS_LABELS[item.status] || item.status }}</n-tag>
            <span class="signal-time">{{ item.detectedAt ?? '近期' }}</span>
          </div>
          <button type="button" class="signal-link" @click="openSignal(item.signalId)">查看详情</button>
        </li>
      </ul>

      <!-- 空态 -->
      <div v-else class="empty-state" data-testid="p08-empty">
        <p class="empty-title">{{ (filter.trim() || typeFilter || statusFilter) ? '没有匹配的信号' : '暂无经营信号' }}</p>
        <p class="empty-desc">{{ (filter.trim() || typeFilter || statusFilter) ? '尝试调整筛选条件' : '当前没有待判断的经营信号。当客户出现业务变化时，信号将出现在此处。' }}</p>
        <n-button v-if="filter.trim() || typeFilter || statusFilter" size="small" @click="filter = ''; typeFilter = null; statusFilter = null">清除筛选</n-button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.signals-view {
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
  margin-bottom: 12px;
}

.related-link {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--v8-border, #e1e7e7);
  border-radius: 8px;
  background: #fff;
  color: var(--v8-primary, #3b58c8);
  font-size: 13px;
  text-decoration: none;
}

.related-link:hover {
  background: rgba(59, 88, 200, 0.06);
}

.filter-summary {
  font-size: 13px;
  color: var(--v8-nav-text);
  margin-bottom: 12px;
}

/* 骨架 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skeleton-row {
  display: grid;
  grid-template-columns: 180px 100px 80px 60px;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--border-light);
  border-radius: 10px;
  background: var(--bg-surface);
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

/* 信号列表 */
.signal-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0;
  margin: 0;
}
.signal-item {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 16px;
  padding: 14px 18px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  align-items: center;
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.signal-item:hover {
  border-color: var(--border-normal);
  box-shadow: 0 1px 2px rgba(17, 45, 64, 0.05);
}
.signal-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.signal-customer {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  text-align: left;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: color 0.15s ease;
}
.signal-customer:hover {
  color: var(--brand-primary-light);
}
.signal-customer:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}
.signal-impact {
  color: var(--text-primary);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.signal-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}
.signal-time {
  font-size: 12px;
  color: var(--v8-nav-text);
}
.signal-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  text-align: left;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: color 0.15s ease;
  white-space: nowrap;
}
.signal-link:hover {
  color: var(--brand-primary-light);
}
.signal-link:focus-visible {
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
  margin-bottom: 16px;
}

/* 中宽屏 */
@media (max-width: 1024px) {
  .signals-view {
    padding: 24px 24px 40px;
  }
  .signal-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}

/* 手机 */
@media (max-width: 640px) {
  .signals-view {
    padding: 16px 16px 32px;
  }
  .signal-item {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .signal-meta {
    flex-wrap: wrap;
  }
}
</style>
