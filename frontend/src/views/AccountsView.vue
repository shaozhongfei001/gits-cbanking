<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NInput } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import CustomerCard from '../components/CustomerCard.vue'
import { fetchCustomers, type Customer } from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P02'
const OBJECT_TYPE = '客户 Account'

const route = useRoute()
const router = useRouter()
const pageRefs = usePageReferenceStore()

const customers = ref<Customer[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const filter = ref('')
const subtab = ref('table')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: customers.value.length > 0,
    requested: requested.value,
  }),
)

const visibleCustomers = computed(() => {
  const q = filter.value.trim()
  if (!q) {
    return customers.value
  }
  return customers.value.filter(item => item.customerName.includes(q) || item.customerId.includes(q))
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'object_list',
    filter: filter.value,
    subtab: subtab.value,
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
    error.value = e instanceof Error ? e.message : '无法获取客户列表'
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
  filter.value = String(route.query.q || restored.filter || '')
  subtab.value = restored.subtab ?? 'table'
  loadCustomers()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="accounts" data-testid="p02-accounts">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="列表"
      title="客户对象主页"
    />

    <div class="toolbar">
      <DisabledAction
        label="导入名单"
        :disabled="true"
        reason="导入名单为写操作，P30 仅授权只读切片"
        unlockPath="待合同批准与后续 Loop 授权既有写 Action"
      />
      <n-input
        v-model:value="filter"
        data-testid="p02-filter"
        placeholder="筛选客户名称"
        style="max-width: 240px"
        @update:value="persistReference"
      />
      <router-link class="related-link" to="/accounts/portfolio" data-testid="p02-open-portfolio">
        客户分层看板
      </router-link>
    </div>

    <PageState :status="status" :error="error" idle-description="尚未请求客户 Account 列表" @retry="loadCustomers">
      <p class="hint">数据来源：GET /api/v1/engagement/customer?rmId=（C0 listCustomers）。</p>
      <div class="customer-grid" data-testid="p02-customer-grid">
        <CustomerCard
          v-for="customer in visibleCustomers"
          :key="customer.customerId"
          :customer="customer"
          @click="openCustomer(customer.customerId)"
        />
      </div>
      <p v-if="!visibleCustomers.length" class="empty">暂无客户数据</p>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}
.hint,
.empty,
.related-link {
  color: var(--text-tertiary);
  font-size: 13px;
}
.related-link {
  color: var(--brand-primary);
  align-self: center;
}
.customer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 12px;
}
</style>
