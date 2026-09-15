<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import {
  fetchAssembledKnowledgeMap,
  fetchCustomers,
  matchProducts,
  type AssembledKnowledgeMap,
  type Customer,
  type ProductMatch,
} from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P38'
const OBJECT_TYPE = '知识要素 KE（只读）'
const KNOWLEDGE_UNLOCK = '待产品适用边界写合同批准后由独立 Loop 启用；本页 KE 保持只读'
const PREFERRED_CUSTOMER = 'CUST-CORP-0001'

const pageRefs = usePageReferenceStore()
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const customers = ref<Customer[]>([])
const customerId = ref('')
const assembled = ref<AssembledKnowledgeMap | null>(null)
const products = ref<ProductMatch[]>([])

const sections = computed(() => assembled.value?.skillSections || [])
const trace = computed(() => assembled.value?.assemblyTrace || [])
const hasSkillPayload = computed(() => sections.value.some(s => (s.content || '').trim()) || products.value.length > 0)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: customerId.value,
    viewId: 'knowledge_map_readonly',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function pickCustomer(list: Customer[]): string {
  return list.find(c => c.customerId === PREFERRED_CUSTOMER)?.customerId
    || list[0]?.customerId
    || ''
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  assembled.value = null
  products.value = []
  try {
    const list = await fetchCustomers()
    customers.value = Array.isArray(list) ? list : []
    if (!customerId.value || !customers.value.some(c => c.customerId === customerId.value)) {
      customerId.value = pickCustomer(customers.value)
    }
    if (!customerId.value) {
      assembled.value = { customerId: '', skillSections: [], assemblyTrace: [] }
      return
    }
    const [map, recs] = await Promise.all([
      fetchAssembledKnowledgeMap(customerId.value),
      matchProducts(customerId.value).catch(() => [] as ProductMatch[]),
    ])
    assembled.value = map
    products.value = Array.isArray(recs) ? recs : []
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'DKWS 未返回'
    assembled.value = null
    products.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="knowledge-map" data-testid="p38-knowledge-map">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="只读"
      title="知识卡与产品适用边界"
    />
    <div class="toolbar">
      <DisabledAction
        label="比较产品"
        :disabled="true"
        reason="产品适用边界比较写未授权，禁止比较产品写回"
        :unlock-path="KNOWLEDGE_UNLOCK"
      />
      <DisabledAction
        label="反馈知识"
        :disabled="true"
        reason="知识反馈写未授权，禁止从本页反馈知识"
        :unlock-path="KNOWLEDGE_UNLOCK"
      />
    </div>
    <p class="hint">知识地图与产品适用由 DKWS Skill 按客户装配（skill-customer-previsit-report / bank-front-product-recommendation）。本页不读取仓库内知识快照填页。</p>
    <label v-if="customers.length" class="customer-pick">
      客户
      <select v-model="customerId" data-testid="p38-customer" @change="load">
        <option v-for="c in customers" :key="c.customerId" :value="c.customerId">
          {{ c.customerName || c.customerId }}
        </option>
      </select>
    </label>
    <PageState :status="status" :error="error" idle-description="尚未加载知识地图" @retry="load">
      <div v-if="hasSkillPayload" class="payload" data-testid="p38-skill-payload">
        <p v-if="assembled?.skillReportTitle || assembled?.skillExecutiveSummary" class="summary">
          {{ assembled?.skillReportTitle }}
          <span v-if="assembled?.skillExecutiveSummary"> · {{ assembled?.skillExecutiveSummary }}</span>
        </p>
        <section v-if="sections.length" class="ki-list" data-testid="p38-sections">
          <article v-for="(section, idx) in sections" :key="`${section.heading || 's'}-${idx}`" class="element-card">
            <h2>{{ section.heading || '未命名条目' }}</h2>
            <p class="element-content">{{ section.content }}</p>
          </article>
        </section>
        <section v-if="products.length" class="product-list" data-testid="p38-products">
          <h2>产品适用</h2>
          <article v-for="p in products" :key="p.productId" class="element-card">
            <div class="element-head">
              <span class="element-id">{{ p.productId }}</span>
              <span class="element-name">{{ p.productName }}</span>
            </div>
            <p v-if="p.matchReason || p.reason || p.matchReasons?.length" class="element-content">
              {{ p.matchReason || p.reason || (p.matchReasons || []).join('、') }}
            </p>
          </article>
        </section>
        <section v-if="trace.length" class="trace" data-testid="p38-trace">
          <h2>DKWS 装配跟踪</h2>
          <p v-for="(step, idx) in trace" :key="idx">
            {{ step.phase }} · {{ step.status }} · {{ step.message }}
            <span v-if="step.kiId"> · {{ step.kiId }}</span>
          </p>
        </section>
      </div>
      <p v-else class="empty" data-testid="p38-empty">DKWS 未返回知识地图</p>
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
.hint,
.empty,
.summary,
.trace p {
  color: var(--text-tertiary);
  font-size: 13px;
}
.customer-pick {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  font-size: 13px;
  color: var(--text-secondary);
}
.customer-pick select {
  min-width: 220px;
  padding: 4px 8px;
}
.ki-list,
.product-list,
.trace {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}
.ki-list h2,
.product-list h2,
.trace h2 {
  margin: 0;
  font-size: 15px;
}
.element-card {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px 14px;
  background: var(--bg-surface);
}
.element-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}
.element-id {
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
.element-name {
  font-weight: 600;
  font-size: 14px;
}
.element-content {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
}
</style>
