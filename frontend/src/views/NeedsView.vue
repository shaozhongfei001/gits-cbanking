<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { loadNeedApproxRows, NEED_OBJECT_TYPE, type NeedApproxRow } from '../composables/needApprox'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P20'

const router = useRouter()
const pageRefs = usePageReferenceStore()

const rows = ref<NeedApproxRow[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: rows.value.length > 0 || requested.value,
    requested: requested.value,
  }),
)

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: NEED_OBJECT_TYPE,
    viewId: 'need_approx_list',
    subtab: 'list',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadRows() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    rows.value = await loadNeedApproxRows()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取需求/机会近似列表'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function openRecord(id: string) {
  persistReference()
  router.push({ name: 'NeedRecord', params: { id } })
}

onMounted(loadRows)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="needs-view" data-testid="p20-needs">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="NEED_OBJECT_TYPE"
      object-status="列表"
      title="需求与机会对象主页"
    />
    <div class="toolbar">
      <DisabledAction
        label="新建机会"
        :disabled="true"
        reason="Need 正式写无本 Loop 合同；禁止发明正式 needId 或 Need 枚举并回写"
        unlockPath="待 CCC-GITS-BANK-20260825-003 完成 CC2 后由独立合同 Loop 启用"
      />
    </div>
    <p class="hint">
      C2 降级：列表由 fetchCustomerContext.opportunitySignals 与 claims 只读近似装配。主键为既有
      signalId / claimId，非正式 Need。
    </p>
    <PageState :status="status" :error="error" idle-description="尚未请求需求/机会近似对象" @retry="loadRows">
      <ul v-if="rows.length" class="need-list" data-testid="p20-need-list">
        <li v-for="item in rows" :key="`${item.sourceKind}:${item.sourceId}`" class="need-item">
          <button
            type="button"
            class="need-link"
            :data-testid="`p20-open-${item.sourceId}`"
            @click="openRecord(item.sourceId)"
          >
            {{ item.summary }}
          </button>
          <span>{{ item.customerName }}</span>
          <span>{{ item.kindLabel }}</span>
          <span data-testid="p20-source-id">{{ item.sourceId }}</span>
        </li>
      </ul>
      <p v-else class="empty">暂无机会信号或 Claim 可作非正式 Need 近似</p>
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
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.need-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0;
}
.need-item {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 0.8fr;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  align-items: center;
}
.need-link {
  border: 0;
  background: transparent;
  color: var(--brand-primary);
  text-align: left;
  cursor: pointer;
  font-weight: 600;
}
</style>
