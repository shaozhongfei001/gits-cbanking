<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import CustomerFactSnapshotPanel from '../components/recommendation/CustomerFactSnapshotPanel.vue'
import EligibilityResultPanel from '../components/recommendation/EligibilityResultPanel.vue'
import ProductCandidateCompare from '../components/recommendation/ProductCandidateCompare.vue'
import ProductPortfolioPanel from '../components/recommendation/ProductPortfolioPanel.vue'
import RecommendationDecisionPanel from '../components/recommendation/RecommendationDecisionPanel.vue'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { useProductRecommendationStore } from '../stores/useProductRecommendationStore'
import type { RecommendationRunStatus, StructuredModification, RecommendationDecision } from '../api/productRecommendation'

const PAGE_ID = 'WP5-1'
const OBJECT_TYPE = '产品推荐 ProductRecommendationRun'

const route = useRoute()
const router = useRouter()
const store = useProductRecommendationStore()

const runId = computed(() => String(route.params.runId || ''))
const isCreateMode = computed(() => runId.value === 'new')

const activeTab = ref<'eligibility' | 'matching' | 'decision'>('eligibility')

const stages: StagePathStage[] = [
  { key: 'eligibility', label: '资格与缺口' },
  { key: 'matching', label: '匹配与组合' },
  { key: 'decision', label: '人工决定' },
]

const completedKeys = computed(() => {
  if (!store.run) return []
  const s = store.run.status
  if (['MATCHING', 'PROPOSAL_READY', 'AWAITING_HUMAN', 'APPROVED', 'MODIFIED', 'REJECTED', 'HELD', 'STALE_REQUIRES_RERUN', 'FAILED_CLOSED'].includes(s)) {
    return ['eligibility']
  }
  return []
})
const currentKey = computed(() => {
  if (!store.run) return 'eligibility'
  const s = store.run.status
  if (['REQUESTED', 'CONTEXT_ASSEMBLING', 'HARD_FILTERING'].includes(s)) return 'eligibility'
  if (s === 'MATCHING') return 'matching'
  return 'decision'
})

const status = computed(() =>
  deriveResourceStatus({
    loading: store.loading,
    error: store.kertUnreachable ? '' : store.error,
    hasData: store.run != null,
    requested: true,
  }),
)

const objectStatus = computed(() => (runId.value === 'new' ? '发起' : runId.value || '缺对象'))

// 创建表单
const formCustomerId = ref(String(route.query.customerId || ''))
const formJourneyId = ref(String(route.query.journeyId || ''))
const formOperatingCaseId = ref(String(route.query.operatingCaseId || ''))
const formObjective = ref(String(route.query.recommendationObjective || ''))
const formDomains = ref(String(route.query.requestedProductDomains || ''))
const formNeedVersionIds = ref(String(route.query.needVersionIds || ''))
const formAsOf = ref(new Date().toISOString())
const formError = ref('')

function reload(): void {
  if (!isCreateMode.value) {
    store.loadRun(runId.value)
  }
}

async function submitCreate(): Promise<void> {
  formError.value = ''
  if (!formCustomerId.value.trim()) {
    formError.value = '客户 ID 必填'
    return
  }
  if (!formObjective.value.trim()) {
    formError.value = '推荐目的必填（禁止空泛的“给我推荐产品”）'
    return
  }
  const journeyId = formJourneyId.value.trim()
  const operatingCaseId = formOperatingCaseId.value.trim()
  if (!journeyId && !operatingCaseId) {
    formError.value = '客户旅程 ID 或经营案例 ID 至少填一个（经营上下文必填）'
    return
  }
  const created = await store.createRun({
    customerId: formCustomerId.value.trim(),
    journeyId: journeyId || undefined,
    operatingCaseId: operatingCaseId || undefined,
    needVersionIds: formNeedVersionIds.value
      ? formNeedVersionIds.value.split(',').map((s) => s.trim()).filter(Boolean)
      : undefined,
    recommendationObjective: formObjective.value.trim(),
    requestedProductDomains: formDomains.value
      ? formDomains.value.split(',').map((s) => s.trim()).filter(Boolean)
      : undefined,
    asOf: formAsOf.value || new Date().toISOString(),
  })
  if (created) {
    router.replace({ name: 'ProductRecommendationWorkspace', params: { runId: created.runId } })
  }
}

async function handleRerun(): Promise<void> {
  const next = await store.retryRun(runId.value)
  if (next) {
    await store.loadRun(next.runId)
  }
}

function handleDecide(payload: { decision: RecommendationDecision; modifications?: StructuredModification[]; reason?: string }): void {
  store.recordDecision(payload)
}

onMounted(reload)
watch(runId, () => {
  if (!isCreateMode.value) {
    reload()
  }
})
</script>

<template>
  <div class="pr-workspace" data-testid="pr-workspace">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="产品推荐三段式工作区"
    >
      <template #actions>
        <button v-if="!isCreateMode && store.run" type="button" class="ghost" data-testid="pr-rerun-top" @click="handleRerun">
          重跑
        </button>
      </template>
    </ObjectHeader>

    <StagePath :stages="stages" :current-key="currentKey" :completed-keys="completedKeys" />

    <!-- 发起模式（P22 入口） -->
    <form v-if="isCreateMode" class="create-form" data-testid="pr-create-form" @submit.prevent="submitCreate">
      <h2>发起产品推荐</h2>
      <p class="hint">
        依据唯一权威 Need 版本发起受控推荐运行（idempotency 由前端生成幂等键）。KERT 不可达时失败关闭（INV-07），禁止本地回退。
      </p>
      <label>
        <span>客户 ID（必填）</span>
        <input v-model="formCustomerId" type="text" data-testid="pr-create-customer" />
      </label>
      <label>
        <span>客户旅程 ID（与经营案例 ID 至少填一个）</span>
        <input v-model="formJourneyId" type="text" data-testid="pr-create-journey" />
      </label>
      <label>
        <span>经营案例 ID（可选，与客户旅程 ID 二选一必填）</span>
        <input v-model="formOperatingCaseId" type="text" data-testid="pr-create-opcase" />
      </label>
      <label>
        <span>推荐目的（必填）</span>
        <textarea v-model="formObjective" rows="2" data-testid="pr-create-objective" />
      </label>
      <label>
        <span>Need 版本引用（逗号分隔，可选）</span>
        <input v-model="formNeedVersionIds" type="text" data-testid="pr-create-needs" />
      </label>
      <label>
        <span>请求产品域（逗号分隔，可选）</span>
        <input v-model="formDomains" type="text" data-testid="pr-create-domains" />
      </label>
      <label>
        <span>业务时点 asOf</span>
        <input v-model="formAsOf" type="text" data-testid="pr-create-asof" />
      </label>
      <div class="create-actions">
        <button type="submit" class="primary" data-testid="pr-create-submit" :disabled="store.creating">
          {{ store.creating ? '发起中…' : '发起产品推荐' }}
        </button>
        <span v-if="store.error" class="error" data-testid="pr-create-error">{{ store.error }}</span>
        <span v-if="formError" class="error" data-testid="pr-create-form-error">{{ formError }}</span>
      </div>
    </form>

    <!-- 工作区模式（P25-G2 入口 / 发起成功后） -->
    <template v-else>
      <div v-if="store.kertUnreachable" class="kert-unreachable" data-testid="kert-unreachable">
        <p class="kert-title">KERT（DKWS）不可达</p>
        <p class="kert-desc">
          受控失败空态（INV-07 fail-closed）：禁止在本地生产推荐回退。请稍后重试，或联系知识 Owner 排查 KERT 执行契约。
        </p>
        <button type="button" class="primary" data-testid="kert-retry" @click="reload">重试</button>
      </div>

      <PageState v-else :status="status" :error="store.error" idle-description="尚未加载产品推荐运行" @retry="reload">
        <template v-if="store.run">
          <nav class="tabs" data-testid="pr-tabs" aria-label="三段式工作区页签">
            <button
              type="button"
              class="tab"
              :class="{ active: activeTab === 'eligibility' }"
              data-testid="pr-tab-eligibility"
              @click="activeTab = 'eligibility'"
            >
              资格与缺口
            </button>
            <button
              type="button"
              class="tab"
              :class="{ active: activeTab === 'matching' }"
              data-testid="pr-tab-matching"
              @click="activeTab = 'matching'"
            >
              匹配与组合
            </button>
            <button
              type="button"
              class="tab"
              :class="{ active: activeTab === 'decision' }"
              data-testid="pr-tab-decision"
              @click="activeTab = 'decision'"
            >
              人工决定
            </button>
          </nav>

          <div v-show="activeTab === 'eligibility'" class="tab-panel" data-testid="pr-tab-eligibility-panel">
            <CustomerFactSnapshotPanel :run="store.run" />
            <EligibilityResultPanel :stages="store.stages" />
          </div>
          <div v-show="activeTab === 'matching'" class="tab-panel" data-testid="pr-tab-matching-panel">
            <ProductCandidateCompare :stages="store.stages" />
            <ProductPortfolioPanel :stages="store.stages" />
          </div>
          <div v-show="activeTab === 'decision'" class="tab-panel" data-testid="pr-tab-decision-panel">
            <RecommendationDecisionPanel
              :run="store.run"
              :version="store.version"
              :stale="store.isStale"
              @decide="handleDecide"
              @rerun="handleRerun"
            />
          </div>

          <div v-if="store.decision" class="decision-receipt" data-testid="pr-decision-receipt">
            <p>已记录决定草稿：{{ store.decision.decision }}（版本 {{ store.decision.proposalVersionId }}）</p>
          </div>
        </template>
      </PageState>
    </template>
  </div>
</template>

<style scoped>
.pr-workspace {
  padding: 0 0 24px;
}
.ghost {
  border: 1px solid var(--border-light);
  background: var(--bg-surface);
  border-radius: 6px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 12px;
}
.create-form {
  display: grid;
  gap: 12px;
  max-width: 560px;
}
.create-form h2 {
  margin: 0;
  font-size: 16px;
}
.hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
}
.create-form label {
  display: grid;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}
.create-form input,
.create-form textarea {
  font-size: 13px;
  padding: 6px 8px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background: var(--bg-surface);
}
.create-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.primary {
  border: 1px solid var(--gits-blue-600, #1976d2);
  background: var(--gits-blue-600, #1976d2);
  color: #fff;
  border-radius: 6px;
  padding: 6px 16px;
  cursor: pointer;
  font-size: 13px;
}
.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.error {
  color: #b91c1c;
  font-size: 12px;
}
.kert-unreachable {
  margin-top: 8px;
  padding: 24px;
  border: 1px dashed rgba(220, 38, 38, 0.4);
  border-radius: 8px;
  text-align: center;
}
.kert-title {
  font-size: 15px;
  font-weight: 600;
  color: #b91c1c;
  margin: 0 0 8px;
}
.kert-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 16px;
}
.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 16px;
}
.tab {
  border: none;
  background: transparent;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
}
.tab.active {
  color: var(--gits-blue-600, #1976d2);
  border-bottom-color: var(--gits-blue-600, #1976d2);
  font-weight: 600;
}
.tab-panel {
  display: grid;
  gap: 20px;
}
.decision-receipt {
  margin-top: 16px;
  padding: 10px 12px;
  border: 1px solid rgba(18, 167, 160, 0.4);
  border-radius: 8px;
  background: rgba(18, 167, 160, 0.06);
  font-size: 13px;
}
.decision-receipt p {
  margin: 0;
}
</style>
