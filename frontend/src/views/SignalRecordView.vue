<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import {
  fetchCustomers,
  fetchCustomerContext,
  SIGNAL_TYPE_LABELS,
  SIGNAL_STATUS_LABELS,
  type Customer,
  type OpportunitySignal,
} from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P09'
const OBJECT_TYPE = '经营信号 Signal'

const route = useRoute()
const pageRefs = usePageReferenceStore()

const signalId = computed(() => String(route.params.id || ''))
const signal = ref<OpportunitySignal | null>(null)
const customer = ref<Customer | null>(null)
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: signal.value != null,
    requested: requested.value,
  }),
)

const title = computed(() => signal.value?.content
  ? `经营信号记录 · ${signal.value.signalId}`
  : '经营信号记录')

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: signalId.value,
    customerId: customer.value?.customerId,
    viewId: 'signal_record',
    subtab: 'detail',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadRecord() {
  loading.value = true
  error.value = ''
  requested.value = true
  signal.value = null
  customer.value = null
  try {
    const list = await fetchCustomers()
    for (const item of list) {
      const ctx = await fetchCustomerContext(item.customerId)
      const found = (ctx.opportunitySignals ?? []).find(row => row.signalId === signalId.value)
      if (found) {
        signal.value = found
        customer.value = item
        return
      }
    }
    error.value = '未找到该经营信号'
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取经营信号记录'
  } finally {
    loading.value = false
  }
}

onMounted(loadRecord)
watch(signalId, loadRecord)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="signal-record" data-testid="p09-signal-record">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="记录"
      :title="title"
    />
    <SignalsDomainTabs />
    <div class="toolbar">
      <DisabledAction
        label="忽略"
        :disabled="true"
        reason="本 Loop 禁止 dismissSignal 写回，即使 SDK 已有该方法"
        unlockPath="后续 Loop 在明确授权后启用受控写 Action"
      />
      <DisabledAction
        label="确认"
        :disabled="true"
        reason="本 Loop 禁止 confirmSignal 写回，即使 SDK 已有该方法"
        unlockPath="后续 Loop 在明确授权后启用受控写 Action"
      />
      <DisabledAction
        label="批量指派"
        :disabled="true"
        reason="批量指派无本 Loop 合同，禁止作为页面主动作"
        unlockPath="待合同批准后由后续 Loop 交付"
      />
    </div>
    <PageState :status="status" :error="error" idle-description="尚未定位经营信号" @retry="loadRecord">
      <dl v-if="signal" class="facts">
        <div>
          <dt>信号编号</dt>
          <dd>{{ signal.signalId }}</dd>
        </div>
        <div>
          <dt>客户</dt>
          <dd>{{ customer?.customerName || '-' }}</dd>
        </div>
        <div>
          <dt>类型</dt>
          <dd>{{ SIGNAL_TYPE_LABELS[signal.signalType] || signal.signalType }}</dd>
        </div>
        <div>
          <dt>状态</dt>
          <dd>{{ SIGNAL_STATUS_LABELS[signal.status] || signal.status }}</dd>
        </div>
        <div>
          <dt>内容</dt>
          <dd>{{ signal.content }}</dd>
        </div>
        <div>
          <dt>来源</dt>
          <dd>{{ signal.sourceType }}</dd>
        </div>
        <div>
          <dt>检测时间</dt>
          <dd>{{ signal.detectedAt }}</dd>
        </div>
        <div v-if="signal.confidence != null">
          <dt>置信度（合同字段，非自动执行）</dt>
          <dd>{{ signal.confidence }}</dd>
        </div>
      </dl>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.facts {
  display: grid;
  gap: 12px;
  margin: 0;
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
