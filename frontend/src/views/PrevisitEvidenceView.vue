<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { useEngagementContext } from '../composables/useEngagementContext'
import { usePageReferenceStore } from '../stores/pageReference'
import { usePrevisitStore } from '../stores/previsit'

const PAGE_ID = 'P13'
const OBJECT_TYPE = '互动 Interaction'

const msg = useMessage()
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
const completedKeys = computed<string[]>(() => ['gaps'])
const currentKey = 'evidence'

const requested = ref(false)
const loading = ref(false)

// 本页只读消费 store 中的一键访前结果，绝不自动触发 KERT。
const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value || previsitStore.loading,
    error: previsitStore.error,
    hasData: previsitStore.previsitDone || requested.value,
    requested: requested.value,
  }),
)

const objectStatus = computed(() => (journeyId.value || '缺对象'))

const sources = computed(() => {
  const p = previsitStore.previsitResult
  if (!p) return []
  const rows: { kind: string; id: string; summary: string }[] = []
  if (p.outreachScript?.scriptId) {
    rows.push({
      kind: '外联脚本',
      id: p.outreachScript.scriptId,
      summary: p.outreachScript.objective || p.outreachScript.openingLine || '',
    })
  }
  if (p.meetingScript?.scriptId) {
    rows.push({
      kind: '会面脚本',
      id: p.meetingScript.scriptId,
      summary: p.meetingScript.meetingObjective || '',
    })
  }
  if (p.previsitReport?.reportId) {
    rows.push({
      kind: '访前报告',
      id: p.previsitReport.reportId,
      summary: p.previsitReport.visitObjective || '',
    })
  }
  if (p.battleCard?.cardId) {
    rows.push({
      kind: '速战卡',
      id: p.battleCard.cardId,
      summary: p.battleCard.visitObjective || '',
    })
  }
  return rows
})

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    customerId: customerId.value || undefined,
    recordId: journeyId.value || undefined,
    viewId: 'previsit_evidence',
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function syncContext() {
  requested.value = true
  previsitStore.setContext({
    journeyId: journeyId.value,
    operatingCaseId: operatingCaseId.value,
    customerId: customerId.value,
    rmId: rmId.value,
  })
}

function query() {
  return {
    ...(customerId.value ? { customerId: customerId.value } : {}),
    ...(journeyId.value ? { journeyId: journeyId.value } : {}),
    ...(operatingCaseId.value ? { operatingCaseId: operatingCaseId.value } : {}),
    ...(rmId.value ? { rmId: rmId.value } : {}),
  }
}

function goGaps() {
  persistReference()
  router.push({ path: '/engagement/previsit/gaps', query: query() })
}

function goPack() {
  persistReference()
  router.push({ name: 'PrevisitPack', query: query() })
}

async function generatePack() {
  if (!journeyId.value || !customerId.value || !operatingCaseId.value) {
    msg.warning('缺少旅程/客户上下文，请先从互动记录·访前路径启动旅程')
    return
  }
  loading.value = true
  const result = await previsitStore.runPrevisit('访前调研')
  loading.value = false
  if (result) {
    msg.success('访前包已从 DKWS 返回（外联 + 会面 + R1 报告 + 速战卡）')
  } else {
    msg.error(previsitStore.error || '一键访前失败')
  }
}

onMounted(syncContext)
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="slice-page" data-testid="p13-previsit-evidence">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="访前知识证据装配"
    >
      <template #actions>
        <n-button size="small" @click="goGaps">← 返回缺口</n-button>
        <n-button
          size="small"
          type="primary"
          data-testid="p13-generate-pack"
          :disabled="!journeyId || !customerId || !operatingCaseId || previsitStore.loading"
          @click="generatePack"
        >
          {{ previsitStore.loading ? '生成中…' : '生成访前包' }}
        </n-button>
        <n-button size="small" data-testid="p13-go-pack" :disabled="!customerId" @click="goPack">
          去访前包预览 →
        </n-button>
      </template>
    </ObjectHeader>

    <StagePath :stages="stages" :current-key="currentKey" :completed-keys="completedKeys" />

    <PageState :status="status" :error="previsitStore.error" idle-description="尚未装配证据" @retry="generatePack">
      <p class="hint">
        只读消费既有 preparePrevisit 返回（唯一 KERT 入口）；无来源则空态，禁止无来源结论。
      </p>

      <template v-if="previsitStore.previsitDone">
        <!-- 装配轨迹（DERIVED_READ_ONLY） -->
        <h2 class="section-title">装配轨迹</h2>
        <ul v-if="previsitStore.assemblyTrace.length" class="item-list trace-list" data-testid="p13-trace-list">
          <li v-for="(step, i) in previsitStore.assemblyTrace" :key="i" class="item trace">
            <span class="kind" :class="{ 'kind-skip': step.status === 'skipped' }">
              {{ step.status === 'skipped' ? '跳过' : step.phase }}
            </span>
            <span v-if="step.kiId" class="mono">{{ step.kiId }}</span>
            <span class="msg">{{ step.message }}</span>
          </li>
        </ul>
        <p v-else class="empty">DKWS 未返回装配轨迹</p>

        <!-- 派生来源 -->
        <h2 class="section-title">证据来源（派生视图）</h2>
        <ul v-if="sources.length" class="item-list" data-testid="p13-source-list">
          <li v-for="row in sources" :key="row.id" class="item">
            <span class="kind">来源·{{ row.kind }}</span>
            <span class="mono">{{ row.id }}</span>
            <span>{{ row.summary || '-' }}</span>
          </li>
        </ul>
      </template>
      <p v-else class="empty" data-testid="p13-empty">
        尚未执行一键访前。请先点击「生成访前包」触发 KERT（外联 + 会面 + R1 报告），装配轨迹将在此展示。
      </p>
    </PageState>
  </div>
</template>

<style scoped>
.hint,
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.section-title {
  margin: 16px 0 8px;
  font-size: 14px;
  color: var(--text-primary);
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
  grid-template-columns: 8rem 1fr 1.4fr;
  gap: 8px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  font-size: 13px;
}
.item.trace {
  grid-template-columns: 6rem 1fr 2fr;
}
.kind {
  color: var(--text-tertiary);
}
.kind-skip {
  color: var(--gits-amber-800, #7a4b00);
}
.mono {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-secondary);
}
.msg {
  color: var(--text-primary);
}
</style>
