<script setup lang="ts">
/**
 * 建议书降级壳层 — 可折叠提示。
 *
 * 优化：降级提示（hint + DisabledAction reason）默认折叠为单行提示条，
 * 点击展开可查看完整说明；建议书生成后自动折叠释放空间。
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NCollapse, NCollapseItem } from 'naive-ui'
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

/** 提示折叠状态：默认展开，slot 内容有数据时自动折叠 */
const hintCollapsed = ref(false)

const hasData = computed(() => {
  if (props.loadMode === 'list') {
    return requested.value
  }
  if (props.loadMode === 'wizard') {
    return wizard.value != null
  }
  return placeholder.value != null
})

/** 建议书生成后自动折叠提示，释放空间 */
watch(hasData, (val) => {
  if (val) {
    hintCollapsed.value = true
  }
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
        :hide-reason="true"
      />
      <slot name="toolbar" />
    </div>

    <!-- 可折叠提示区 -->
    <div class="hint-area" :class="{ 'is-collapsed': hintCollapsed }">
      <div class="hint-summary" @click="hintCollapsed = !hintCollapsed">
        <span class="hint-icon">{{ hintCollapsed ? '▸' : '▾' }}</span>
        <span class="hint-text">{{ hint }}</span>
      </div>
      <!--
        折叠时用 v-show 而非 v-if：原因文本常驻 DOM（可检索 / 可断言），
        同时保持「默认单行、需要时展开」的紧凑版面。
      -->
      <div v-show="!hintCollapsed" class="hint-detail">
        <p class="hint-reason" data-testid="disabled-reason">
          <b>禁用原因：</b>{{ actionReason }}
        </p>
        <p class="hint-unlock">
          <b>解除路径：</b>{{ PROPOSAL_UNLOCK_PATH }}
        </p>
      </div>
    </div>

    <PageState :status="status" :error="error" :idle-description="idleDescription" @retry="load">
      <slot :placeholder="placeholder" :wizard="wizard" :list-empty="listEmpty" />
    </PageState>
  </div>
</template>

<style scoped>
.proposal-degrade {
  max-width: 1240px;
  padding: 32px 34px 48px;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
}

/* ── 可折叠提示区 ── */
.hint-area {
  margin-bottom: 12px;
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.03);
  overflow: hidden;
  transition: all 0.2s ease;
}

.hint-area.is-collapsed {
  background: transparent;
  border-color: transparent;
}

.hint-summary {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
}

.hint-summary:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 4px;
}

.hint-area.is-collapsed .hint-summary {
  padding: 4px 0;
}

.hint-icon {
  flex-shrink: 0;
  font-size: 11px;
  color: var(--v8-nav-text);
  margin-top: 2px;
}

.hint-text {
  font-size: 12px;
  line-height: 1.5;
  color: var(--v8-nav-text);
}

.hint-detail {
  padding: 0 12px 10px 28px;
}

.hint-reason,
.hint-unlock {
  margin: 0 0 4px;
  font-size: 11px;
  line-height: 1.5;
  color: var(--v8-nav-text);
}

.hint-reason b,
.hint-unlock b {
  color: var(--v8-nav-text);
}
@media (max-width: 1024px) {
  .proposal-degrade {
    padding: 24px 24px 40px;
  }
}
@media (max-width: 640px) {
  .proposal-degrade {
    padding: 16px 16px 32px;
  }
}
</style>
