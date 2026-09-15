<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
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
      title="首页·我的客户经营"
    />

    <div class="toolbar">
      <n-button type="primary" data-testid="view-queue-action" @click="subtab = 'queue'">查看工作队列</n-button>
      <DisabledAction
        label="确认型操作"
        :disabled="true"
        reason="P30 只读切片禁止确认型写操作；队列失败时仅展示快照"
        unlockPath="后续 Loop 在合同批准后启用确认型 Action"
      />
      <input
        v-model="filter"
        class="filter-input"
        data-testid="p01-filter"
        placeholder="筛选客户或候选原因"
        @change="persistReference"
      />
    </div>

    <p class="candidate-note">行动队列为 C1 视图模型，由 GET /api/v1/engagement/customer 列表派生；推荐不等于自动执行。</p>

    <PageState :status="status" :error="error" idle-description="尚未请求客户列表" @retry="loadCustomers">
      <div v-if="error && snapshot" class="degraded" data-testid="p01-degraded">
        队列服务不可用，展示最近成功快照；确认型操作已禁用。
      </div>
      <ul class="queue" data-testid="p01-action-queue">
        <li v-for="item in actionQueue" :key="item.customerId" class="queue-item">
          <button type="button" class="queue-link" @click="openCustomer(item.customerId)">
            {{ item.customerName }}
          </button>
          <span>{{ item.riskLevel ? RISK_LEVEL_LABELS[item.riskLevel] : '-' }}</span>
          <span>{{ item.customerTier ? CUSTOMER_TIER_LABELS[item.customerTier] : '-' }}</span>
          <span class="reason">{{ item.candidateReason }}</span>
        </li>
      </ul>
      <p v-if="!actionQueue.length" class="empty">暂无派生行动项</p>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}
.filter-input {
  min-width: 220px;
  height: 32px;
  border: 1px solid var(--border-normal);
  border-radius: 6px;
  padding: 0 10px;
}
.candidate-note,
.empty,
.degraded,
.reason {
  color: var(--text-tertiary);
  font-size: 13px;
}
.degraded {
  margin-bottom: 12px;
  color: var(--color-warning);
}
.queue {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.queue-item {
  display: grid;
  grid-template-columns: 1.4fr 0.6fr 0.8fr 1.6fr;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  align-items: center;
}
.queue-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  text-align: left;
  cursor: pointer;
  font-weight: 600;
}
</style>
