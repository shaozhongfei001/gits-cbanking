<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { SIGNAL_STATUS_LABELS, SIGNAL_TYPE_LABELS } from '../api/engagement'
import { loadNeedApproxById, NEED_OBJECT_TYPE, type NeedApproxRow } from '../composables/needApprox'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P21'

const route = useRoute()
const router = useRouter()
const pageRefs = usePageReferenceStore()

const sourceId = computed(() => String(route.params.id || ''))
const row = ref<NeedApproxRow | null>(null)
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: row.value != null,
    requested: requested.value,
  }),
)

const title = computed(() =>
  row.value ? `需求记录 · ${row.value.sourceId}` : '需求记录',
)

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: NEED_OBJECT_TYPE,
    recordId: sourceId.value,
    customerId: row.value?.customerId,
    viewId: 'need_approx_record',
    subtab: 'detail',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadRecord() {
  loading.value = true
  error.value = ''
  requested.value = true
  row.value = null
  try {
    const found = await loadNeedApproxById(sourceId.value)
    if (!found) {
      error.value = '未找到该非正式 Need 近似对象（仅匹配既有 signalId / claimId）'
      return
    }
    row.value = found
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取需求记录近似对象'
  } finally {
    loading.value = false
  }
}

function openPlan() {
  persistReference()
  router.push({ name: 'NeedPlan', params: { id: sourceId.value } })
}

onMounted(loadRecord)
watch(sourceId, loadRecord)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="need-record" data-testid="p21-need-record">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="NEED_OBJECT_TYPE"
      object-status="记录"
      :title="title"
    />
    <div class="toolbar">
      <DisabledAction
        label="请求专家"
        :disabled="true"
        reason="专家协同无本 Loop 合同；禁止把非正式 Need 当作可回写对象"
        unlockPath="待 Need 合同批准后由后续 Loop 启用受控写 Action"
      />
      <button type="button" class="link-btn" data-testid="p21-open-plan" @click="openPlan">
        查看只读服务计划派生
      </button>
    </div>
    <PageState :status="status" :error="error" idle-description="尚未定位非正式 Need 近似对象" @retry="loadRecord">
      <dl v-if="row" class="facts">
        <div>
          <dt>主键（既有 ID，非 needId）</dt>
          <dd>{{ row.sourceId }}</dd>
        </div>
        <div>
          <dt>近似来源</dt>
          <dd>{{ row.kindLabel }}</dd>
        </div>
        <div>
          <dt>客户</dt>
          <dd>{{ row.customerName }}</dd>
        </div>
        <div>
          <dt>摘要</dt>
          <dd>{{ row.summary }}</dd>
        </div>
        <div v-if="row.signal">
          <dt>信号类型（合同字段，非正式 Need 枚举）</dt>
          <dd>{{ SIGNAL_TYPE_LABELS[row.signal.signalType] || row.signal.signalType }}</dd>
        </div>
        <div v-if="row.signal">
          <dt>信号状态</dt>
          <dd>{{ SIGNAL_STATUS_LABELS[row.signal.status] || row.signal.status }}</dd>
        </div>
        <div v-if="row.claim">
          <dt>Claim 类型（合同字段，非正式 Need 枚举）</dt>
          <dd>{{ row.claim.claimType }}</dd>
        </div>
        <div v-if="row.claim">
          <dt>Claim 状态</dt>
          <dd>{{ row.claim.status }}</dd>
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
  align-items: flex-start;
  margin-bottom: 16px;
}
.link-btn {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border-normal);
  border-radius: 6px;
  background: var(--bg-surface);
  cursor: pointer;
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
