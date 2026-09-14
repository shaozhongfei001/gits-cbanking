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
import { useRecommendationFormOptions, PRODUCT_DOMAIN_LABELS } from '../composables/useRecommendationFormOptions'
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
const formAsOf = ref(new Date().toISOString())
const formError = ref('')

// 表单选项数据源（客户 / 经营案例 / 需求候选 / 产品域，均取自后端真实端点）
const options = useRecommendationFormOptions()

/** Need 版本引用：多选，值为需求候选 ID。 */
const formNeedVersionIds = ref<string[]>(splitCsvQuery(route.query.needVersionIds))
/** 请求产品域：多选，值为 product_knowledge_version.category。 */
const formDomains = ref<string[]>(splitCsvQuery(route.query.requestedProductDomains))

/** 经营上下文选择方式：经营案例（默认）或客户旅程。 */
const contextMode = ref<'operatingCase' | 'journey'>(
  route.query.journeyId && !route.query.operatingCaseId ? 'journey' : 'operatingCase',
)

/** 当前客户下的经营案例选项（客户切换时联动）。 */
const scopedOperatingCases = computed(() =>
  formCustomerId.value ? options.operatingCasesOf(formCustomerId.value) : options.operatingCaseOptions.value,
)
/** 当前客户下的需求候选（客户切换时联动）。 */
const scopedNeedCandidates = computed(() =>
  formCustomerId.value ? options.needCandidatesOf(formCustomerId.value) : options.needCandidates.value,
)

function splitCsvQuery(raw: unknown): string[] {
  if (!raw) return []
  return String(raw)
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

/**
 * 应用默认值：默认客户取第一个可选客户，经营案例/需求取该客户下第一项，产品域取第一个可选域。
 * 仅在对应字段为空时填充，不覆盖 URL query 传入的显式值。
 */
function applyDefaults(): void {
  if (!formCustomerId.value && options.customerOptions.value.length > 0) {
    formCustomerId.value = options.customerOptions.value[0].value
  }
  if (!formOperatingCaseId.value && !formJourneyId.value && scopedOperatingCases.value.length > 0) {
    formOperatingCaseId.value = scopedOperatingCases.value[0].value
    contextMode.value = 'operatingCase'
  }
  if (formNeedVersionIds.value.length === 0 && scopedNeedCandidates.value.length > 0) {
    formNeedVersionIds.value = [scopedNeedCandidates.value[0].value]
  }
  if (formDomains.value.length === 0 && options.productDomainOptions.value.length > 0) {
    formDomains.value = [options.productDomainOptions.value[0].value]
  }
  if (!formObjective.value) {
    formObjective.value = buildDefaultObjective()
  }
}

/** 默认推荐目的：基于已选产品域生成具体表述，避免空泛的「给我推荐产品」。 */
function buildDefaultObjective(): string {
  const domainLabels = formDomains.value
    .map((d) => PRODUCT_DOMAIN_LABELS[d] ?? d)
    .filter(Boolean)
  if (domainLabels.length === 0) return ''
  return `围绕${domainLabels.join('、')}需求，评估可落地的对公产品组合与准入缺口`
}

/** 客户变更时，重置依赖客户的经营上下文与需求选择，并重新填默认值。 */
function onCustomerChange(): void {
  formOperatingCaseId.value = ''
  formJourneyId.value = ''
  formNeedVersionIds.value = []
  applyDefaults()
}

/** 经营上下文方式切换时，清空另一路取值，保证二选一语义。 */
function onContextModeChange(): void {
  if (contextMode.value === 'operatingCase') {
    formJourneyId.value = ''
    if (!formOperatingCaseId.value && scopedOperatingCases.value.length > 0) {
      formOperatingCaseId.value = scopedOperatingCases.value[0].value
    }
  } else {
    formOperatingCaseId.value = ''
  }
}

function reload(): void {
  if (!isCreateMode.value) {
    store.loadRun(runId.value)
  }
}

async function submitCreate(): Promise<void> {
  formError.value = ''
  if (!formCustomerId.value.trim()) {
    formError.value = '请选择客户'
    return
  }
  if (!formObjective.value.trim()) {
    formError.value = '推荐目的必填（禁止空泛的“给我推荐产品”）'
    return
  }
  const journeyId = formJourneyId.value.trim()
  const operatingCaseId = formOperatingCaseId.value.trim()
  if (!journeyId && !operatingCaseId) {
    formError.value = '请选择客户旅程或经营案例（经营上下文必填）'
    return
  }
  const created = await store.createRun({
    customerId: formCustomerId.value.trim(),
    journeyId: journeyId || undefined,
    operatingCaseId: operatingCaseId || undefined,
    needVersionIds: formNeedVersionIds.value.length > 0 ? [...formNeedVersionIds.value] : undefined,
    recommendationObjective: formObjective.value.trim(),
    requestedProductDomains: formDomains.value.length > 0 ? [...formDomains.value] : undefined,
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

onMounted(async () => {
  reload()
  if (isCreateMode.value) {
    await options.load()
    applyDefaults()
  }
})
watch(runId, async () => {
  if (isCreateMode.value) {
    if (!options.loaded.value) {
      await options.load()
    }
    applyDefaults()
  } else {
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

      <p v-if="options.loading.value" class="options-state" data-testid="pr-options-loading">
        正在加载客户、经营案例与产品域选项…
      </p>
      <p v-else-if="options.error.value" class="options-state error" data-testid="pr-options-error">
        选项加载失败：{{ options.error.value }}
        <button type="button" class="ghost" data-testid="pr-options-retry" @click="options.load()">重试</button>
      </p>

      <label>
        <span>客户（必填）</span>
        <select
          v-model="formCustomerId"
          data-testid="pr-create-customer"
          :disabled="options.loading.value"
          @change="onCustomerChange"
        >
          <option value="">请选择客户</option>
          <option v-for="opt in options.customerOptions.value" :key="opt.value" :value="opt.value">
            {{ opt.label }}{{ opt.description ? ` — ${opt.description}` : '' }}
          </option>
        </select>
      </label>

      <fieldset class="context-mode">
        <legend>经营上下文（经营案例与客户旅程二选一，必填）</legend>
        <label class="inline">
          <input v-model="contextMode" type="radio" value="operatingCase" data-testid="pr-context-mode-opcase" @change="onContextModeChange" />
          <span>选择经营案例</span>
        </label>
        <label class="inline">
          <input v-model="contextMode" type="radio" value="journey" data-testid="pr-context-mode-journey" @change="onContextModeChange" />
          <span>填写客户旅程 ID</span>
        </label>
      </fieldset>

      <label v-if="contextMode === 'operatingCase'">
        <span>经营案例</span>
        <select v-model="formOperatingCaseId" data-testid="pr-create-opcase" :disabled="options.loading.value">
          <option value="">请选择经营案例</option>
          <option v-for="opt in scopedOperatingCases" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        <small v-if="!options.loading.value && scopedOperatingCases.length === 0" class="field-hint">
          当前客户暂无经营案例，可切换为填写客户旅程 ID。
        </small>
      </label>

      <label v-else>
        <span>客户旅程 ID</span>
        <input v-model="formJourneyId" type="text" data-testid="pr-create-journey" placeholder="例如 JOURNEY-001" />
      </label>

      <label>
        <span>需求（可选，多选）</span>
        <select v-model="formNeedVersionIds" multiple size="4" data-testid="pr-create-needs" :disabled="options.loading.value">
          <option v-for="opt in scopedNeedCandidates" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        <small class="field-hint">
          候选项派生自该客户的商机（后端暂无 NeedVersion 列表端点）；按住 Ctrl/Cmd 可多选。
        </small>
      </label>

      <label>
        <span>请求产品域（可选，多选）</span>
        <select v-model="formDomains" multiple size="4" data-testid="pr-create-domains" :disabled="options.loading.value">
          <option v-for="opt in options.productDomainOptions.value" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        <small class="field-hint">取自产品知识版本的产品域；按住 Ctrl/Cmd 可多选。</small>
      </label>

      <label>
        <span>推荐目的（必填）</span>
        <textarea v-model="formObjective" rows="2" data-testid="pr-create-objective" />
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
        <p class="kert-title">KERT（KERT）不可达</p>
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
.create-form select,
.create-form textarea {
  font-size: 13px;
  padding: 6px 8px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background: var(--bg-surface);
}
.create-form select[multiple] {
  padding: 4px;
}
.create-form .field-hint {
  font-size: 11px;
  color: var(--text-tertiary);
}
.options-state {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
}
.options-state.error {
  color: #b91c1c;
}
.context-mode {
  display: flex;
  gap: 16px;
  align-items: center;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  padding: 8px 12px;
  margin: 0;
}
.context-mode legend {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 0 4px;
}
.context-mode label.inline {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
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
