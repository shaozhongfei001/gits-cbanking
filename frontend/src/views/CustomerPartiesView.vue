<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import CustomerRecordTabs from '../components/shell/CustomerRecordTabs.vue'
import { fetchCustomer, type Customer } from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P07'
const OBJECT_TYPE = '客户 Account'

const route = useRoute()
const pageRefs = usePageReferenceStore()

const customerId = computed(() => String(route.params.id || ''))
const customer = ref<Customer | null>(null)
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: customer.value != null,
    requested: requested.value,
  }),
)

const title = computed(() => customer.value?.customerName
  ? `${customer.value.customerName} · 关系人情报`
  : '客户记录·关系人情报')

const hasSummary = computed(() =>
  Boolean(customer.value?.relationshipSummary || customer.value?.rmName || customer.value?.coreTags?.length),
)

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: customerId.value,
    viewId: 'parties_readonly',
    subtab: 'parties',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadRecord() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    customer.value = await fetchCustomer(customerId.value)
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取关系人情报'
    customer.value = null
  } finally {
    loading.value = false
  }
}

onMounted(loadRecord)
watch(customerId, loadRecord)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="parties-view" data-testid="p07-parties">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="关系人"
      :title="title"
    />
    <CustomerRecordTabs :customer-id="customerId" />
    <div class="toolbar">
      <DisabledAction
        label="请求引荐"
        :disabled="true"
        reason="C2：引荐写操作无合同；禁止发明关系人图 API"
        unlockPath="待关系人对象合同批准后由后续 Loop 启用"
      />
    </div>
    <PageState :status="status" :error="error" idle-description="尚未请求关系摘要" @retry="loadRecord">
      <p class="hint">中性关系摘要仅使用既有 Customer 字段（relationshipSummary、rmName、managingBranch、coreTags）。</p>
      <dl v-if="hasSummary" class="facts">
        <div>
          <dt>客户经理</dt>
          <dd>{{ customer?.rmName || '-' }}</dd>
        </div>
        <div>
          <dt>管辖机构</dt>
          <dd>{{ customer?.managingBranch || '-' }}</dd>
        </div>
        <div>
          <dt>关系摘要</dt>
          <dd>{{ customer?.relationshipSummary || '-' }}</dd>
        </div>
        <div>
          <dt>标签</dt>
          <dd>{{ customer?.coreTags?.join('、') || '-' }}</dd>
        </div>
      </dl>
      <p v-else class="empty">暂无关系人摘要</p>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.facts {
  display: grid;
  gap: 12px;
  margin: 16px 0 0;
}
.facts div {
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}
dt {
  font-size: 12px;
  color: var(--text-tertiary);
}
dd {
  margin: 4px 0 0;
  font-size: 14px;
}
</style>
