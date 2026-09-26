<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { NButton, NCard, NEmpty, NTag } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import HumanGateDialog from '../components/HumanGateDialog.vue'
import {
  decideHumanGate,
  fetchHumanGates,
  GATE_TYPE_LABELS,
  HUMAN_GATE_STATUS_LABELS,
  type GateDecision,
  type HumanGate,
} from '../api/v11'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P32'
const OBJECT_TYPE = '人工门禁 HumanGate'

const pageRefs = usePageReferenceStore()
const gates = ref<HumanGate[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const showDialog = ref(false)
const selectedGate = ref<HumanGate | null>(null)
const deciding = ref(false)

const pendingGates = computed(() => gates.value.filter(gate => gate.status === 'PENDING'))
const firstPending = computed(() => pendingGates.value[0] ?? null)

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
    viewId: 'approvals_work_center',
    recordId: selectedGate.value?.gateId,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    gates.value = await fetchHumanGates({})
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法加载审批门禁'
    gates.value = []
  } finally {
    loading.value = false
  }
}

function openReturnedGate(gate: HumanGate) {
  if (!gates.value.some(item => item.gateId === gate.gateId)) {
    return
  }
  selectedGate.value = gate
  showDialog.value = true
}

function openFirstPending() {
  if (!firstPending.value) {
    return
  }
  openReturnedGate(firstPending.value)
}

async function handleDecide(
  gateId: string,
  decision: GateDecision,
  modification: Record<string, unknown> | undefined,
  reason: string,
) {
  if (!gates.value.some(item => item.gateId === gateId)) {
    return
  }
  deciding.value = true
  try {
    const updated = await decideHumanGate(gateId, {
      decision,
      modification,
      reason,
      actorId: 'current-user',
    })
    const idx = gates.value.findIndex(item => item.gateId === gateId)
    if (idx >= 0) {
      gates.value[idx] = updated
    }
    showDialog.value = false
  } finally {
    deciding.value = false
  }
}

onMounted(load)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="approvals" data-testid="p32-approvals">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="工作中心"
      title="审批工作中心"
    />
    <div class="toolbar">
      <n-button
        type="primary"
        size="small"
        :disabled="!firstPending"
        data-testid="p32-open-first"
        @click="openFirstPending"
      >
        打开首项
      </n-button>
    </div>
    <p class="hint">
      仅对 API 已返回的门禁调用既有 decide。不对授信/定价作业流建模，也不提供新建门禁表单。
    </p>
    <PageState :status="status" :error="error" idle-description="尚未加载审批门禁" @retry="load">
      <n-empty v-if="!gates.length" description="暂无审批门禁" data-testid="p32-empty" />
      <div v-else class="gate-list" data-testid="p32-gate-list">
        <n-card
          v-for="gate in gates"
          :key="gate.gateId"
          size="small"
          hoverable
          class="gate-card"
          :data-testid="`p32-gate-${gate.gateId}`"
          @click="openReturnedGate(gate)"
        >
          <div class="gate-row">
            <n-tag size="small" :type="gate.status === 'PENDING' ? 'warning' : 'default'">
              {{ GATE_TYPE_LABELS[gate.gateType] || gate.gateType }}
            </n-tag>
            <n-tag size="small">{{ HUMAN_GATE_STATUS_LABELS[gate.status] || gate.status }}</n-tag>
            <span class="gate-id">{{ gate.gateId }}</span>
          </div>
          <p class="subject">{{ gate.subject }}</p>
        </n-card>
      </div>
    </PageState>
    <HumanGateDialog
      :show="showDialog"
      :gate="selectedGate"
      :loading="deciding"
      @update:show="showDialog = $event"
      @decide="handleDecide"
    />
  </div>
</template>

<style scoped>
.approvals {
  max-width: 1240px;
  padding: 32px 34px 48px;
}
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.hint {
  color: var(--v8-nav-text);
  font-size: 13px;
}
.gate-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.gate-card {
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.gate-card:focus-within,
.gate-card:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}
.gate-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.gate-id {
  font-family: ui-monospace, monospace;
  font-size: 12px;
  color: var(--v8-nav-text);
}
.subject {
  margin: 8px 0 0;
  font-size: 14px;
}
@media (max-width: 1024px) {
  .approvals {
    padding: 24px 24px 40px;
  }
}
@media (max-width: 640px) {
  .approvals {
    padding: 16px 16px 32px;
  }
}
</style>
