<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import ObjectHeader from './ObjectHeader.vue'
import PageState from './PageState.vue'
import DisabledAction from './DisabledAction.vue'
import {
  loadGovDegradeShell,
  probeDegradeServices,
  type GovDegradePageCopy,
  type ServiceProbe,
} from '../../composables/govDegrade'
import { deriveResourceStatus } from '../../composables/useResourceStatus'
import { usePageReferenceStore } from '../../stores/pageReference'

const props = defineProps<GovDegradePageCopy>()

const pageRefs = usePageReferenceStore()
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const probes = ref<ServiceProbe[]>([])

const hasData = computed(() => requested.value)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: hasData.value,
    requested: requested.value,
  }),
)

function persistReference() {
  pageRefs.capture(props.pageId, {
    objectType: props.objectType,
    viewId: `gov_degrade_${props.pageId.toLowerCase()}`,
    subtab: props.loadMode,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  probes.value = []
  try {
    if (props.loadMode === 'probe') {
      probes.value = await probeDegradeServices()
    } else {
      await loadGovDegradeShell()
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法装配治理降级壳层'
  } finally {
    loading.value = false
  }
}

onMounted(load)
onBeforeUnmount(persistReference)

defineExpose({ load })
</script>

<template>
  <div class="gov-degrade" :data-testid="testId">
    <ObjectHeader
      :page-id="pageId"
      :object-type="objectType"
      :object-status="objectStatus"
      :title="title"
    />
    <div class="toolbar">
      <DisabledAction
        v-for="action in actions"
        :key="action.label"
        :label="action.label"
        :disabled="true"
        :reason="action.reason"
        :unlock-path="action.unlockPath"
      />
    </div>
    <p class="hint">{{ hint }}</p>
    <PageState :status="status" :error="error" :idle-description="idleDescription" @retry="load">
      <ul v-if="probes.length" class="probe-list" data-testid="p40-probes">
        <li v-for="probe in probes" :key="probe.serviceId">
          {{ probe.label }}：{{ probe.available ? '可用' : '不可用' }}（{{ probe.detail }}）
        </li>
      </ul>
      <p class="empty" :data-testid="`${testId}-empty`">{{ emptyText }}</p>
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
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.probe-list {
  margin: 0 0 12px;
  padding-left: 18px;
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
