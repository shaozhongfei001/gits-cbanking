<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import CustomerRecordTabs from '../components/shell/CustomerRecordTabs.vue'
import { fetchCustomer, fetchTransactions, type Customer, type TransactionRecord } from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P06'
const OBJECT_TYPE = '客户 Account'

const route = useRoute()
const pageRefs = usePageReferenceStore()

const customerId = computed(() => String(route.params.id || ''))
const customer = ref<Customer | null>(null)
const transactions = ref<TransactionRecord[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const filter = ref('')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: customer.value != null || requested.value,
    requested: requested.value,
  }),
)

const title = computed(() => customer.value?.customerName
  ? `${customer.value.customerName} · 业务资金全景`
  : '客户记录·业务资金全景')

const visible = computed(() => {
  const q = filter.value.trim()
  if (!q) {
    return transactions.value
  }
  return transactions.value.filter(item =>
    item.transactionType.includes(q) || (item.description ?? '').includes(q),
  )
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: customerId.value,
    viewId: 'funds_panorama',
    filter: filter.value,
    subtab: 'funds',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadRecord() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    const [cust, rows] = await Promise.all([
      fetchCustomer(customerId.value),
      fetchTransactions(customerId.value),
    ])
    customer.value = cust
    transactions.value = rows
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取业务资金全景'
    customer.value = null
    transactions.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  filter.value = restored.filter ?? ''
  loadRecord()
})
watch(customerId, loadRecord)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="funds-view" data-testid="p06-funds">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="资金全景"
      :title="title"
    />
    <CustomerRecordTabs :customer-id="customerId" />
    <div class="toolbar">
      <DisabledAction
        label="创建需求"
        :disabled="true"
        reason="Need 为 C3 正式对象，本 Loop 禁止伪实现"
        unlockPath="CCC 完成 CC2 后由后续 Loop 交付"
      />
      <input
        v-model="filter"
        class="filter-input"
        data-testid="p06-filter"
        placeholder="筛选交易类型或描述"
        @change="persistReference"
      />
    </div>
    <PageState :status="status" :error="error" idle-description="尚未请求交易流水" @retry="loadRecord">
      <p class="hint">数据来源：GET /api/v1/engagement/customer/:customerId/transactions（C1 只读）。</p>
      <table v-if="visible.length" class="tx-table" data-testid="p06-tx-table">
        <thead>
          <tr>
            <th>时间</th>
            <th>类型</th>
            <th>金额</th>
            <th>描述</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in visible" :key="row.transactionId">
            <td>{{ row.occurredAt }}</td>
            <td>{{ row.transactionType }}</td>
            <td>{{ row.amount.toLocaleString() }} {{ row.currency }}</td>
            <td>{{ row.description || '-' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">暂无交易流水</p>
    </PageState>
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
.filter-input {
  min-width: 220px;
  height: 32px;
  border: 1px solid var(--border-normal);
  border-radius: 6px;
  padding: 0 10px;
}
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.tx-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
  background: var(--bg-surface);
}
.tx-table th,
.tx-table td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-light);
  font-size: 13px;
}
</style>
