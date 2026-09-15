<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import MobileDegradeFrame from '../components/shell/MobileDegradeFrame.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { decideHumanGate, fetchHumanGates, type HumanGate } from '../api/v11'
import { MOBILE_DEGRADE_PAGES } from '../composables/mobileDegrade'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const page = MOBILE_DEGRADE_PAGES.P44
const pageRefs = usePageReferenceStore()
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const ending = ref(false)
const gates = ref<HumanGate[]>([])

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

const exitGate = computed(
  () => gates.value.find(gate => gate.gateType === 'E01_EXIT_CONFIRM' && gate.status === 'PENDING') ?? null,
)

function persistReference() {
  pageRefs.capture(page.pageId, {
    objectType: page.objectType,
    viewId: 'mobile_checkout',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadGates() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    gates.value = await fetchHumanGates({
      gateType: 'E01_EXIT_CONFIRM',
    })
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法加载离场确认门禁'
    gates.value = []
  } finally {
    loading.value = false
  }
}

async function completeMeeting() {
  if (!exitGate.value) {
    return
  }
  ending.value = true
  try {
    await decideHumanGate(exitGate.value.gateId, {
      decision: 'APPROVE',
      actorId: 'current-user',
      reason: '离场确认',
    })
    await loadGates()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '完成会谈提交失败'
  } finally {
    ending.value = false
  }
}

onMounted(loadGates)
onBeforeUnmount(persistReference)
</script>

<template>
  <MobileDegradeFrame
    :page-id="page.pageId"
    :title="page.title"
    :object-type="page.objectType"
    :object-status="page.objectStatus"
    :test-id="page.testId"
    :hint="page.hint"
  >
    <template #toolbar>
      <button
        v-if="exitGate"
        type="button"
        class="link-btn"
        data-testid="p44-complete-meeting"
        :disabled="ending"
        @click="completeMeeting"
      >
        完成会谈
      </button>
      <DisabledAction
        v-else
        label="完成会谈"
        :disabled="true"
        reason="无待处理 E01_EXIT_CONFIRM HumanGate，禁止提交完成会谈"
        unlockPath="仅当既有 HumanGate 类型 E01_EXIT_CONFIRM 处于 PENDING 时才可提交；与桌面 P17 同一合同"
        button-test-id="p44-complete-meeting"
      />
      <DisabledAction
        v-for="action in page.disabledActions"
        :key="action.label"
        :label="action.label"
        :disabled="true"
        :reason="action.reason"
        :unlock-path="action.unlockPath"
      />
    </template>
    <PageState :status="status" :error="error" :idle-description="page.idleDescription" @retry="loadGates">
      <p class="empty" data-testid="p44-mobile-checkout-empty">
        {{ exitGate ? '存在待处理 E01_EXIT_CONFIRM，完成会谈走既有 decideHumanGate。禁止离线完成。' : page.emptyText }}
      </p>
    </PageState>
  </MobileDegradeFrame>
</template>

<style scoped>
.link-btn {
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border-normal);
  border-radius: 6px;
  background: var(--bg-surface);
  cursor: pointer;
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
