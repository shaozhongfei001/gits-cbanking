<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import {
  fetchCustomers,
  CUSTOMER_TIER_LABELS,
  type Customer,
  type CustomerTier,
} from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P03'
const OBJECT_TYPE = '客户组合 Portfolio'

const TIERS: CustomerTier[] = ['STRATEGIC', 'KEY', 'GROWTH', 'GENERAL']

const router = useRouter()
const pageRefs = usePageReferenceStore()

const customers = ref<Customer[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const filter = ref('')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: customers.value.length > 0,
    requested: requested.value,
  }),
)

const columns = computed(() =>
  TIERS.map(tier => ({
    tier,
    label: CUSTOMER_TIER_LABELS[tier],
    items: customers.value.filter(item => {
      const matchTier = (item.customerTier ?? 'GENERAL') === tier
      const matchFilter = !filter.value || item.customerName.includes(filter.value)
      return matchTier && matchFilter
    }),
  })),
)

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'portfolio_board',
    filter: filter.value,
    subtab: 'board',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadCustomers() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    customers.value = await fetchCustomers()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取客户组合'
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
  loadCustomers()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="portfolio" data-testid="p03-portfolio">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="分层"
      title="客户分层与组合看板"
    />

    <div class="toolbar">
      <DisabledAction
        label="批量调整分层"
        :disabled="true"
        button-test-id="tier-write-action"
        reason="分层拖动写回为 C2，待合同批准，禁止发明正式分层写 Action"
        unlockPath="CCC 完成 CC2 签署后由后续 Loop 调用既有写 Action"
      />
      <input
        v-model="filter"
        class="filter-input"
        data-testid="p03-filter"
        placeholder="筛选客户"
        @change="persistReference"
      />
    </div>

    <p class="hint" data-testid="tier-write-disabled-reason">
      看板按既有 customerTier 只读展示。拖动写回已禁用。
    </p>

    <PageState :status="status" :error="error" idle-description="尚未请求客户组合" @retry="loadCustomers">
      <div class="board" data-testid="p03-board">
        <section v-for="column in columns" :key="column.tier" class="column" :data-testid="`tier-column-${column.tier}`">
          <h2>{{ column.label }}</h2>
          <button
            v-for="item in column.items"
            :key="item.customerId"
            type="button"
            class="card"
            draggable="false"
            data-testid="tier-card"
            @click="openCustomer(item.customerId)"
          >
            {{ item.customerName }}
          </button>
          <p v-if="!column.items.length" class="empty">无客户</p>
        </section>
      </div>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}
.filter-input {
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
.board {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}
.column {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px;
  min-height: 240px;
}
.column h2 {
  font-size: 14px;
  margin-bottom: 8px;
}
.card {
  display: block;
  width: 100%;
  margin-bottom: 8px;
  padding: 10px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background: var(--bg-surface-soft);
  text-align: left;
  cursor: pointer;
}
</style>
