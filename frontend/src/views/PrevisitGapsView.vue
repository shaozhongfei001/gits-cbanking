<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NTooltip } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { useEngagementContext } from '../composables/useEngagementContext'
import { usePageReferenceStore } from '../stores/pageReference'
import { usePrevisitStore } from '../stores/previsit'

const PAGE_ID = 'P12'
const OBJECT_TYPE = '互动 Interaction'

const router = useRouter()
const pageRefs = usePageReferenceStore()
const previsitStore = usePrevisitStore()
const { customerId, journeyId, operatingCaseId, rmId } = useEngagementContext()

// 访前向导步骤（3.2 向导步骤条风格）
const stages: StagePathStage[] = [
  { key: 'gaps', label: '访前目标' },
  { key: 'evidence', label: '证据装配' },
  { key: 'pack', label: '访前包预览' },
  { key: 'meeting', label: '会中工作区' },
]
const completedKeys = computed<string[]>(() => [])
const currentKey = 'gaps'

const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value || previsitStore.kycLoading,
    error: error.value || previsitStore.kycError,
    hasData: previsitStore.kycGapProfile != null || requested.value,
    requested: requested.value,
  }),
)

const objectStatus = computed(() => (customerId.value || '缺对象'))

const gapItems = computed(() => {
  const profile = previsitStore.kycGapProfile
  if (!profile) return []
  return [
    ...profile.unknownItems.map((item) => ({ kind: '未知', item })),
    ...profile.partialKnownItems.map((item) => ({ kind: '部分已知', item })),
    ...profile.staleItems.map((item) => ({ kind: '过期', item })),
    ...profile.conflictingOrAmbiguousItems.map((item) => ({ kind: '冲突', item })),
    ...profile.priorityQuestions.map((item) => ({ kind: '优先问题', item })),
    ...profile.knownItems.map((item) => ({ kind: '已知', item })),
  ]
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    customerId: customerId.value || undefined,
    recordId: journeyId.value || undefined,
    viewId: 'previsit_gaps',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadProfile() {
  loading.value = true
  error.value = ''
  requested.value = true
  // 同步 store 上下文（支持深链直接进入 P12）
  previsitStore.setContext({
    journeyId: journeyId.value,
    operatingCaseId: operatingCaseId.value,
    customerId: customerId.value,
    rmId: rmId.value,
  })
  if (customerId.value) {
    await previsitStore.loadKycGap(customerId.value)
  }
  loading.value = false
}

function goEvidence() {
  persistReference()
  router.push({
    path: '/engagement/previsit/evidence',
    query: {
      ...(customerId.value ? { customerId: customerId.value } : {}),
      ...(journeyId.value ? { journeyId: journeyId.value } : {}),
      ...(operatingCaseId.value ? { operatingCaseId: operatingCaseId.value } : {}),
      ...(rmId.value ? { rmId: rmId.value } : {}),
    },
  })
}

onMounted(loadProfile)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="slice-page" data-testid="p12-previsit-gaps">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="访前目标与信息缺口"
    >
      <template #actions>
        <n-tooltip>
          <template #trigger>
            <span>
              <n-button size="small" disabled>自动填补缺口</n-button>
            </span>
          </template>
          缺口填补为写操作且无本 Loop 合同
        </n-tooltip>
        <n-button
          size="small"
          type="primary"
          data-testid="p12-go-evidence"
          :disabled="!customerId"
          @click="goEvidence"
        >
          进入证据装配 →
        </n-button>
      </template>
    </ObjectHeader>

    <StagePath :stages="stages" :current-key="currentKey" :completed-keys="completedKeys" />

    <PageState :status="status" :error="error || previsitStore.kycError" idle-description="尚未请求缺口画像" @retry="loadProfile">
      <p v-if="!customerId" class="empty">缺客户对象，暂无访前缺口</p>
      <template v-else-if="previsitStore.kycGapProfile">
        <p class="hint">数据来源：GET /api/v1/engagement/kyc/{customerId}/gap-profile（纯查询，不触发 KERT）。</p>
        <ul v-if="gapItems.length" class="item-list" data-testid="p12-gap-list">
          <li v-for="(row, idx) in gapItems" :key="idx" class="item">
            <span class="kind">{{ row.kind }}</span>
            <span>{{ row.item }}</span>
          </li>
        </ul>
        <p v-else class="empty">暂无信息缺口</p>
      </template>
    </PageState>
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
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0;
}
.item {
  display: grid;
  grid-template-columns: 7rem 1fr;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  font-size: 13px;
}
.kind {
  color: var(--text-tertiary);
}
</style>
