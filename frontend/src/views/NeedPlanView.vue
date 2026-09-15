<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import { loadNeedApproxById, NEED_OBJECT_TYPE, type NeedApproxRow } from '../composables/needApprox'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P22'

const route = useRoute()
const router = useRouter()
const pageRefs = usePageReferenceStore()

const sourceId = computed(() => String(route.params.id || ''))
const row = ref<NeedApproxRow | null>(null)
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: row.value != null,
    requested: requested.value,
  }),
)

const kycItems = computed(() => {
  const kyc = row.value?.kyc
  if (!kyc) {
    return []
  }
  return [
    ...kyc.unknownItems.map(item => ({ kind: '未知', item })),
    ...kyc.priorityQuestions.map(item => ({ kind: '优先问题', item })),
    ...kyc.partialKnownItems.map(item => ({ kind: '部分已知', item })),
    ...kyc.knownItems.map(item => ({ kind: '已知', item })),
  ]
})

/** 发起产品推荐：进入 WP5-1 三段式工作区（发起模式）。 */
function startRecommendation() {
  persistReference()
  router.push({
    name: 'ProductRecommendationWorkspace',
    params: { runId: 'new' },
    query: {
      ...(row.value?.customerId ? { customerId: row.value.customerId } : {}),
    },
  })
}

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: NEED_OBJECT_TYPE,
    recordId: sourceId.value,
    customerId: row.value?.customerId,
    viewId: 'need_approx_plan',
    subtab: 'plan',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadPlan() {
  loading.value = true
  error.value = ''
  requested.value = true
  row.value = null
  try {
    const found = await loadNeedApproxById(sourceId.value)
    if (!found) {
      error.value = '未找到可派生的非正式 Need 近似对象'
      return
    }
    row.value = found
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取服务计划派生视图'
  } finally {
    loading.value = false
  }
}

onMounted(loadPlan)
watch(sourceId, loadPlan)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="need-plan" data-testid="p22-need-plan">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="NEED_OBJECT_TYPE"
      object-status="只读派生"
      title="机会与服务计划记录"
    />
    <div class="toolbar">
      <DisabledAction
        label="创建建议书"
        :disabled="true"
        reason="建议书工厂属 P34；本 Loop 禁止创建建议书，亦无 ServicePlan 合同对象"
        unlockPath="P34-gits-bank-proposal-degrade 在合同批准后交付"
      />
      <button
        type="button"
        class="start-rec"
        data-testid="p22-start-recommendation"
        :disabled="!row?.customerId"
        @click="startRecommendation"
      >
        发起产品推荐
      </button>
    </div>
    <p class="hint">
      C2 只读派生：KYC 缺口与信号/Claim 摘要。这不是正式 ServicePlan，禁止把建议书阶段写成可回写枚举。
    </p>
    <PageState :status="status" :error="error" idle-description="尚未装配只读服务计划派生" @retry="loadPlan">
      <section v-if="row" class="plan-body">
        <dl class="facts">
          <div>
            <dt>主键（既有 signalId / claimId）</dt>
            <dd>{{ row.sourceId }}</dd>
          </div>
          <div>
            <dt>近似来源</dt>
            <dd>{{ row.kindLabel }}</dd>
          </div>
          <div>
            <dt>信号/Claim 摘要</dt>
            <dd>{{ row.summary }}</dd>
          </div>
        </dl>
        <h2>KYC 摘要</h2>
        <ul v-if="kycItems.length" class="item-list" data-testid="p22-kyc-list">
          <li v-for="(item, idx) in kycItems" :key="idx" class="item">
            <span class="kind">{{ item.kind }}</span>
            <span>{{ item.item }}</span>
          </li>
        </ul>
        <p v-else class="empty">暂无 KYC 缺口摘要</p>
      </section>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}
.start-rec {
  border: 1px solid var(--gits-blue-600, #1976d2);
  background: var(--gits-blue-600, #1976d2);
  color: #fff;
  border-radius: 6px;
  padding: 5px 14px;
  cursor: pointer;
  font-size: 13px;
}
.start-rec:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.plan-body h2 {
  font-size: 16px;
  margin: 16px 0 8px;
}
.facts {
  display: grid;
  gap: 12px;
  margin: 0;
}
.facts div,
.item {
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}
dt {
  font-size: 12px;
  color: var(--text-tertiary);
}
dd {
  margin: 4px 0 0;
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
  grid-template-columns: 0.6fr 1.4fr;
  gap: 8px;
}
.kind {
  color: var(--text-tertiary);
  font-size: 12px;
}
</style>
