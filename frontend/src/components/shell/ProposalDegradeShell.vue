<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ObjectHeader from './ObjectHeader.vue'
import PageState from './PageState.vue'
import DisabledAction from './DisabledAction.vue'
import {
  loadProposalPlaceholder,
  loadProposalShellList,
  loadProposalWizardShell,
  PROPOSAL_OBJECT_TYPE,
  PROPOSAL_UNLOCK_PATH,
  type ProposalPlaceholder,
  type ProposalShellCopy,
  type ProposalWizardShell,
} from '../../composables/proposalDegrade'
import { deriveResourceStatus } from '../../composables/useResourceStatus'
import { usePageReferenceStore } from '../../stores/pageReference'

const props = defineProps<ProposalShellCopy>()

const route = useRoute()
const pageRefs = usePageReferenceStore()

const placeholderId = computed(() => String(route.params.id || ''))
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const listEmpty = ref(false)
const wizard = ref<ProposalWizardShell | null>(null)
const placeholder = ref<ProposalPlaceholder | null>(null)

const hasData = computed(() => {
  if (props.loadMode === 'list') {
    return requested.value
  }
  if (props.loadMode === 'wizard') {
    return wizard.value != null
  }
  return placeholder.value != null
})

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
    objectType: PROPOSAL_OBJECT_TYPE,
    recordId: props.loadMode === 'placeholder' ? placeholderId.value : undefined,
    viewId: `proposal_degrade_${props.pageId.toLowerCase()}`,
    subtab: props.loadMode,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  listEmpty.value = false
  wizard.value = null
  placeholder.value = null
  try {
    if (props.loadMode === 'list') {
      const rows = await loadProposalShellList()
      listEmpty.value = rows.length === 0
    } else if (props.loadMode === 'wizard') {
      wizard.value = await loadProposalWizardShell()
    } else {
      placeholder.value = await loadProposalPlaceholder(placeholderId.value)
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法装配建议书降级壳层'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(placeholderId, () => {
  if (props.loadMode === 'placeholder') {
    load()
  }
})
onBeforeUnmount(persistReference)

defineExpose({ load })
</script>

<template>
  <div class="proposal-degrade" :data-testid="testId">
    <ObjectHeader
      :page-id="pageId"
      :object-type="PROPOSAL_OBJECT_TYPE"
      :object-status="objectStatus"
      :title="title"
    />
    <div class="toolbar">
      <DisabledAction
        :label="actionLabel"
        :disabled="true"
        :reason="actionReason"
        :unlock-path="PROPOSAL_UNLOCK_PATH"
      />
      <slot name="toolbar" />
    </div>
    <p class="hint">{{ hint }}</p>
    <PageState :status="status" :error="error" :idle-description="idleDescription" @retry="load">
      <slot :placeholder="placeholder" :wizard="wizard" :list-empty="listEmpty" />
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
.hint {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
