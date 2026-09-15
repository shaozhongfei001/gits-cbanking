<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NInput } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import {
  fetchCustomers,
  fetchCustomerContext,
  SIGNAL_TYPE_LABELS,
  SIGNAL_STATUS_LABELS,
  type OpportunitySignal,
} from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P08'
const OBJECT_TYPE = '经营信号 Signal'

/** C1 候选：由客户列表与 opportunitySignals 装配，非正式合同字段。 */
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
const subtab = ref('list')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: signals.value.length > 0 || requested.value,
    requested: requested.value,
  }),
)

const visible = computed(() => {
  const q = filter.value.trim()
  if (!q) {
    return signals.value
  }
  return signals.value.filter(item =>
    item.content.includes(q) || item.customerName.includes(q) || item.signalId.includes(q),
  )
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'signal_list',
    filter: filter.value,
    subtab: subtab.value,
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

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  filter.value = restored.filter ?? ''
  subtab.value = restored.subtab ?? 'list'
  loadSignals()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="signals-view" data-testid="p08-signals">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="列表"
      title="经营信号对象主页"
    />
    <SignalsDomainTabs />
    <div class="toolbar">
      <DisabledAction
        label="批量指派"
        :disabled="true"
        reason="本 Loop 禁止信号写回；即使存在 confirm/dismiss 合同也不作为页面主动作"
        unlockPath="后续 Loop 在明确授权后启用受控写 Action"
      />
      <n-input
        v-model:value="filter"
        data-testid="p08-filter"
        placeholder="筛选信号内容或客户"
        style="max-width: 240px"
        @update:value="persistReference"
      />
      <router-link class="related-link" to="/engagements" data-testid="p08-open-engagements">
        互动对象
      </router-link>
      <router-link class="related-link" to="/engagement" data-testid="p08-open-journey">
        经营旅程
      </router-link>
    </div>
    <p class="hint">C1 候选列表：由 fetchCustomers + fetchCustomerContext.opportunitySignals 装配，不等于自动执行。互动对象打开 P10 列表；经营旅程打开 P11 访前路径工作台（在那里启动旅程）。</p>
    <PageState :status="status" :error="error" idle-description="尚未请求经营信号" @retry="loadSignals">
      <ul v-if="visible.length" class="signal-list" data-testid="p08-signal-list">
        <li v-for="item in visible" :key="item.signalId" class="signal-item">
          <button type="button" class="signal-link" @click="openSignal(item.signalId)">
            {{ item.content }}
          </button>
          <span>{{ item.customerName }}</span>
          <span>{{ SIGNAL_TYPE_LABELS[item.signalType] || item.signalType }}</span>
          <span>{{ SIGNAL_STATUS_LABELS[item.status] || item.status }}</span>
        </li>
      </ul>
      <p v-else class="empty">暂无经营信号</p>
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
.signal-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0;
}
.signal-item {
  display: grid;
  grid-template-columns: 1.6fr 1fr 0.8fr 0.6fr;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  align-items: center;
}
.signal-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  text-align: left;
  cursor: pointer;
  font-weight: 600;
}
</style>
