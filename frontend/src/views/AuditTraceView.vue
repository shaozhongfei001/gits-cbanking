<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { NDataTable, NInput, NSpace } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { fetchAuditTrace, type AuditTraceEntry } from '../api/v11'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P39'
const OBJECT_TYPE = '审计追踪 AuditTrace'
const AUDIT_UNLOCK = '待导出审计包 / 验权 API 纳入合同后由独立 Loop 启用'

const pageRefs = usePageReferenceStore()
const entityType = ref('')
const entityId = ref('')
const actorId = ref('')
const entries = ref<AuditTraceEntry[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

const columns = [
  { title: '时间', key: 'occurredAt', width: 180 },
  { title: '实体类型', key: 'entityType', width: 120 },
  { title: '实体ID', key: 'entityId', width: 120 },
  { title: '操作', key: 'operation', width: 100 },
  { title: '操作人', key: 'actorId', width: 120 },
  { title: '角色', key: 'actorRole', width: 100 },
  { title: '关联ID', key: 'correlationId', width: 120 },
]

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'audit_trace',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    entries.value = await fetchAuditTrace({
      entityType: entityType.value || undefined,
      entityId: entityId.value || undefined,
      actorId: actorId.value || undefined,
    })
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '加载审计追踪失败'
    entries.value = []
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="audit-trace-view" data-testid="p39-audit-trace">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="查询"
      title="审计与权限"
    />
    <div class="toolbar">
      <DisabledAction
        label="导出审计包"
        :disabled="true"
        reason="无导出审计包 API，禁止导出"
        :unlock-path="AUDIT_UNLOCK"
      />
      <DisabledAction
        label="验证权限"
        :disabled="true"
        reason="无验证权限 API，禁止从前端验权写回"
        :unlock-path="AUDIT_UNLOCK"
      />
    </div>
    <p class="hint">只读消费 fetchAuditTrace。导出审计包与验证权限未授权。</p>
    <n-space class="filters">
      <n-input v-model:value="entityType" placeholder="实体类型" clearable style="width: 150px" />
      <n-input v-model:value="entityId" placeholder="实体ID" clearable style="width: 150px" />
      <n-input v-model:value="actorId" placeholder="操作人" clearable style="width: 150px" />
    </n-space>
    <PageState :status="status" :error="error" idle-description="尚未加载审计追踪" @retry="load">
      <p v-if="!entries.length" class="empty" data-testid="p39-empty">暂无审计记录。</p>
      <n-data-table
        v-else
        :columns="columns"
        :data="entries"
        :bordered="true"
        size="small"
        :pagination="{ pageSize: 20 }"
        :scroll-x="900"
        data-testid="p39-table"
      />
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
.filters {
  margin-bottom: 12px;
}
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
