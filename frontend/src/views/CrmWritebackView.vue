<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { NTag, NButton, NTooltip } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import HighlightsMetrics from '../components/shell/HighlightsMetrics.vue'
import type { MetricItem } from '../components/shell/HighlightsMetrics.vue'
import CrmWritebackApproval from '../components/CrmWritebackApproval.vue'
import {
  decideCrmWritebackCommand,
  fetchCrmWritebackCommands,
  type CrmWritebackCommand,
  type GateDecision,
  CRM_WRITEBACK_STATUS_LABELS,
} from '../api/v11'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { useEngagementContext } from '../composables/useEngagementContext'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P19'
const OBJECT_TYPE = '互动 Interaction'

const pageRefs = usePageReferenceStore()
const { customerId, journeyId } = useEngagementContext()

// 访后向导步骤（3.2 向导步骤条风格）
const stages: StagePathStage[] = [
  { key: 'reconcile', label: '访后事实对账' },
  { key: 'crm', label: 'CRM 受控回写' },
]
const completedKeys = computed<string[]>(() => ['reconcile'])
const currentKey = 'crm'

const commands = ref<CrmWritebackCommand[]>([])
const selected = ref<CrmWritebackCommand | null>(null)
const showApproval = ref(false)
const deciding = ref(false)
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

const objectStatus = computed(() => (journeyId.value || customerId.value || '待筛选'))

const metrics = computed<MetricItem[]>(() => {
  const pending = commands.value.filter((c) => c.status === 'PENDING').length
  const totalFields = commands.value.reduce((sum, c) => sum + Object.keys(c.payload || {}).length, 0)
  return [
    { label: '写回命令', value: String(commands.value.length), tone: 'blue' },
    { label: '拟写字段', value: String(totalFields), tone: 'blue' },
    { label: '待审批', value: String(pending), tone: 'amber' },
    { label: '幂等', value: '已生成', tone: 'teal' },
  ]
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    customerId: customerId.value || undefined,
    recordId: journeyId.value || undefined,
    viewId: 'crm_writeback',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function payloadEntries(command: CrmWritebackCommand): { field: string; value: string }[] {
  return Object.entries(command.payload || {}).map(([field, value]) => ({
    field,
    value: typeof value === 'object' ? JSON.stringify(value) : String(value),
  }))
}

async function loadCommands() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    commands.value = await fetchCrmWritebackCommands({
      journeyId: journeyId.value || undefined,
      customerId: customerId.value || undefined,
    })
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取 CRM 写回命令'
    commands.value = []
  } finally {
    loading.value = false
  }
}

function preview(command: CrmWritebackCommand) {
  selected.value = command
  showApproval.value = true
}

async function onDecide(
  commandId: string,
  decision: GateDecision,
  modifications: Record<string, unknown>[] | undefined,
  reason: string,
) {
  deciding.value = true
  try {
    await decideCrmWritebackCommand(commandId, {
      decision,
      modifications,
      reason,
      actorId: 'current-user',
    })
    showApproval.value = false
    await loadCommands()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '写回决策失败'
  } finally {
    deciding.value = false
  }
}

onMounted(loadCommands)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="slice-page" data-testid="p19-crm-writeback">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="CRM 受控回写"
    >
      <template #actions>
        <n-tooltip>
          <template #trigger>
            <span>
              <n-button size="small" disabled>直接写回</n-button>
            </span>
          </template>
          禁止跳过预览与人工确认的 CRM 写回
        </n-tooltip>
      </template>
    </ObjectHeader>

    <StagePath :stages="stages" :current-key="currentKey" :completed-keys="completedKeys" />

    <HighlightsMetrics :items="metrics" />

    <PageState :status="status" :error="error" idle-description="尚未加载写回命令" @retry="loadCommands">
      <p class="hint">复用 GET/decide /api/v1/crm/writeback-commands。只展示合同 payload 字段，必须预览后人工确认。</p>
      <ul v-if="commands.length" class="item-list" data-testid="p19-command-list">
        <li v-for="command in commands" :key="command.commandId" class="item">
          <div class="item-head">
            <strong>{{ command.commandId }}</strong>
            <span>{{ command.operation }} · {{ command.targetEntity }}</span>
            <n-tag size="small" :type="command.status === 'PENDING' ? 'warning' : command.status === 'SENT' ? 'success' : 'default'">
              {{ CRM_WRITEBACK_STATUS_LABELS[command.status] || command.status }}
            </n-tag>
          </div>
          <dl class="payload" data-testid="p19-diff-preview">
            <div v-for="entry in payloadEntries(command)" :key="entry.field">
              <dt>{{ entry.field }}</dt>
              <dd class="payload-old">—</dd>
              <dd class="payload-new">{{ entry.value }}</dd>
            </div>
          </dl>
          <button type="button" class="link-btn" data-testid="p19-preview-action" @click="preview(command)">
            预览并确认
          </button>
        </li>
      </ul>
      <p v-else class="empty">暂无 CRM 写回命令</p>
    </PageState>

    <CrmWritebackApproval
      v-model:show="showApproval"
      :command="selected"
      :loading="deciding"
      @decide="onDecide"
    />
  </div>
</template>

<style scoped>
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.item-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.item {
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.item-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.payload {
  display: grid;
  gap: 4px;
  margin: 0;
}
.payload div {
  display: grid;
  grid-template-columns: 8rem 4rem 1fr;
  gap: 8px;
}
dt {
  color: var(--text-tertiary);
}
dd {
  margin: 0;
}
.payload-old {
  color: var(--text-tertiary);
}
.payload-new {
  color: var(--brand-primary);
  font-weight: 500;
}
.link-btn {
  align-self: flex-start;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border-normal);
  border-radius: 6px;
  background: var(--bg-surface);
  cursor: pointer;
}
</style>
