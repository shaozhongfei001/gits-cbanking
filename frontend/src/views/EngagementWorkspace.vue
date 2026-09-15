<template>
  <div class="ew" data-testid="p11-engagement-workspace">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="互动记录·访前路径"
    >
      <template #actions>
        <n-button size="small" :disabled="!previsitStore.previsitDone" data-testid="p11-mark-ready" @click="goInMeeting">
          标记准备完成
        </n-button>
        <n-tooltip>
          <template #trigger>
            <span>
              <n-button size="small" disabled>记为正式 Claim</n-button>
            </span>
          </template>
          访前草稿为候选内容，需经人工门禁确认后才能转为正式 Claim
        </n-tooltip>
        <n-button size="small" type="primary" data-testid="p11-open-previsit" :disabled="!sc" @click="goPrevisit">
          打开访前工作区 →
        </n-button>
      </template>
    </ObjectHeader>
    <SignalsDomainTabs />

    <PageState :status="status" :error="error" idle-description="尚未加载客户列表" @retry="loadCustomers">
      <!-- 状态栏 -->
      <div class="ew-bar">
        <div class="ew-bar-left">
          <span class="ew-bar-label">当前客户</span>
          <n-tag v-if="sc" type="info">{{ sc.customerName }}</n-tag>
          <em v-else>未选择</em>
          <span class="ew-bar-sep">|</span>
          <span class="ew-bar-label">旅程</span>
          <n-tag v-if="jid" :type="jpTag">{{ jpLabel }}</n-tag>
          <em v-else>未启动</em>
        </div>
        <div class="ew-bar-right">
          <n-button size="small" data-testid="p11-select-customer" @click="showCS = true">
            {{ sc ? '切换客户' : '选择客户' }}
          </n-button>
          <button
            v-if="!jid"
            type="button"
            class="start-journey-btn"
            data-testid="p11-start-journey"
            :disabled="!sc || ld"
            @click="doStart"
          >
            {{ ld ? '启动中…' : '启动旅程' }}
          </button>
          <n-button v-if="jid" type="success" size="small" :loading="ld" @click="doComplete">
            完成旅程
          </n-button>
        </div>
      </div>
      <p v-if="startError" class="p11-start-error" data-testid="p11-start-error">{{ startError }}</p>

      <!-- 阶段 Path -->
      <StagePath :stages="stages" :current-key="currentStage" :completed-keys="completedStages" />

      <!-- 主区域 -->
      <main class="ew-body">
          <!-- 四项关键指标 -->
          <HighlightsMetrics :items="metrics" />

          <!-- 关键工作 -->
          <section class="panel" data-testid="p11-key-work">
            <div class="panel-header">
              <h3>关键工作</h3>
              <n-tag size="small" type="info">{{ keyWorkDone }} / {{ keyWork.length }}</n-tag>
            </div>
            <label v-for="kw in keyWork" :key="kw.id" class="kw-item">
              <input v-model="kw.done" type="checkbox" @change="persistReference" />
              <span :class="{ 'kw-done': kw.done }">{{ kw.label }}</span>
            </label>
          </section>

          <!-- 活动时间线（去重后的关键事件流） -->
          <section class="panel" data-testid="p11-activity">
            <div class="panel-header">
              <h3>活动时间线</h3>
              <n-tag size="small" type="info">{{ activityTimeline.length }} 项</n-tag>
            </div>
            <div v-if="!jid" class="tl-empty">
              <p>请先选择客户并启动旅程</p>
            </div>
            <div v-else class="tl-list">
              <div
                v-for="(item, idx) in activityTimeline"
                :key="idx"
                class="tl-item"
                :class="{ done: item.done }"
              >
                <div class="tl-dot">{{ item.icon }}</div>
                <div class="tl-content">
                  <div class="tl-title">{{ item.title }}</div>
                  <div v-if="item.time" class="tl-time">{{ item.time }}</div>
                </div>
              </div>
            </div>
          </section>
      </main>
    </PageState>

    <!-- 客户选择 -->
    <n-modal v-model:show="showCS" preset="dialog" title="选择客户" style="width: 500px">
      <n-input v-model:value="sq" placeholder="搜索客户名称..." clearable />
      <div class="cs-list">
        <div
          v-for="c in fc"
          :key="c.customerId"
          class="cs-item"
          :data-testid="`p11-pick-${c.customerId}`"
          @click="pickCustomer(c)"
        >
          <span>{{ c.customerName }}</span>
          <RiskBadge :level="c.riskLevel" />
        </div>
        <n-empty v-if="!fc.length" description="未找到客户" size="small" />
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NModal, NInput, NEmpty, NTag, NTooltip, useMessage } from 'naive-ui'
import RiskBadge from '../components/RiskBadge.vue'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import HighlightsMetrics from '../components/shell/HighlightsMetrics.vue'
import type { MetricItem } from '../components/shell/HighlightsMetrics.vue'
import { fetchCustomers, startJourney, completeJourney, formatApiError, type Customer } from '../api/engagement'
import { usePrevisitStore } from '../stores/previsit'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P11'
const OBJECT_TYPE = '互动 Interaction'

const msg = useMessage()
const router = useRouter()
const route = useRoute()
const pageRefs = usePageReferenceStore()
const previsitStore = usePrevisitStore()

const loading = ref(true)
const error = ref('')
const requested = ref(false)
const ld = ref(false)
const startError = ref('')
const custs = ref<Customer[]>([])
const sc = ref<Customer | null>(null)
const sq = ref('')
const showCS = ref(false)
const jid = ref('')
const jph = ref('')
const oid = ref('')
const journeyCompleted = ref(false)

const keyWork = ref([
  { id: 'goal', label: '确认拜访目标与成功标准', done: false },
  { id: 'evidence', label: '补齐行业/客户证据', done: false },
  { id: 'expert', label: '确定专家与会中分工', done: false },
])

const stages: StagePathStage[] = [
  { key: 'previsit', label: '访前准备' },
  { key: 'meeting', label: '会中协作' },
  { key: 'postvisit', label: '访后核验与受控回写' },
]

const completedStages = computed<string[]>(() => {
  const done: string[] = []
  if (previsitStore.previsitDone) done.push('previsit')
  if (journeyCompleted.value) {
    done.push('meeting')
    done.push('postvisit')
  }
  return done
})

const currentStage = computed(() => {
  if (!jid.value) return ''
  if (journeyCompleted.value) return 'postvisit'
  if (previsitStore.previsitDone) return 'meeting'
  return 'previsit'
})

const keyWorkDone = computed(() => keyWork.value.filter((k) => k.done).length)

const metrics = computed<MetricItem[]>(() => {
  const gap = previsitStore.kycGapProfile
  const openQuestions = gap
    ? (gap.unknownItems?.length || 0)
      + (gap.partialKnownItems?.length || 0)
      + (gap.conflictingOrAmbiguousItems?.length || 0)
    : 0
  return [
    {
      label: '准备完整度',
      value: previsitStore.previsitDone ? '100%' : jid.value ? '待准备' : '—',
      tone: 'blue',
    },
    { label: '待核实问题', value: gap ? String(openQuestions) : '—', tone: 'amber' },
    { label: '客户参会人', value: '—', tone: 'blue' },
    { label: '关联需求', value: '—', tone: 'teal' },
  ]
})

const activityTimeline = computed(() => {
  const items: { icon: string; title: string; time: string; done: boolean }[] = []
  items.push({ icon: '🚀', title: '启动旅程', time: jid.value ? '刚刚' : '', done: !!jid.value })
  if (jid.value) {
    items.push({ icon: '📋', title: '访前准备', time: '', done: previsitStore.previsitDone })
  }
  if (previsitStore.previsitDone) {
    items.push({ icon: '🤝', title: '会中互动', time: '', done: journeyCompleted.value })
  }
  if (journeyCompleted.value) {
    items.push({ icon: '📊', title: '访后复盘', time: '', done: true })
  }
  return items
})

const jpLabel = computed(() => jph.value || '已启动')
const jpTag = computed<'info' | 'warning' | 'success' | 'default'>(() => {
  if (journeyCompleted.value) return 'success'
  if (previsitStore.previsitDone) return 'info'
  return 'warning'
})

const fc = computed(() => {
  if (!sq.value) return custs.value.slice(0, 20)
  const q = sq.value.toLowerCase()
  return custs.value.filter((c) => c.customerName.toLowerCase().includes(q)).slice(0, 20)
})

function pickCustomer(c: Customer) {
  sc.value = c
  showCS.value = false
  resetJourney()
  previsitStore.setContext({ customerId: c.customerId, rmId: c.rmId })
  msg.info(`已选择客户：${c.customerName}，请点击"启动旅程"开始经营流程`)
}

function resetJourney() {
  jid.value = ''
  jph.value = ''
  oid.value = ''
  journeyCompleted.value = false
  startError.value = ''
  previsitStore.reset()
}

async function doStart() {
  if (!sc.value) {
    msg.warning('请先选择客户')
    showCS.value = true
    return
  }
  ld.value = true
  startError.value = ''
  try {
    const r = await startJourney(sc.value.customerId)
    jid.value = r.journeyId
    jph.value = r.phase
    oid.value = r.operatingCaseId
    previsitStore.setContext({
      journeyId: r.journeyId,
      operatingCaseId: r.operatingCaseId,
      customerId: sc.value.customerId,
      rmId: sc.value.rmId,
    })
    // 纯查询 KYC 缺口，供首屏指标使用（不触发 KERT）
    await previsitStore.loadKycGap(sc.value.customerId)
    const kycHint = r.kycGapSummary ? ` | KYC: ${r.kycGapSummary}` : ''
    msg.success(`旅程已启动 (ID: ${r.journeyId.substring(0, 8)}...)${kycHint}`)
  } catch (e: unknown) {
    startError.value = formatApiError(e, '启动旅程失败')
    msg.error(startError.value)
  } finally {
    ld.value = false
  }
}

async function doComplete() {
  if (!jid.value) {
    msg.warning('请先启动旅程')
    return
  }
  ld.value = true
  try {
    await completeJourney(jid.value)
    journeyCompleted.value = true
    msg.success('旅程已完成，CRM 回写已确认')
  } catch (e: unknown) {
    msg.error(formatApiError(e, '完成旅程失败'))
  } finally {
    ld.value = false
  }
}

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

const objectStatus = computed(() => sc.value?.customerName || '缺对象')

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    customerId: sc.value?.customerId,
    recordId: jid.value || undefined,
    viewId: 'previsit_path',
    draftId: keyWork.value.filter((k) => k.done).map((k) => k.id).join(','),
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function sliceQuery() {
  const query: Record<string, string> = {}
  if (sc.value?.customerId) query.customerId = sc.value.customerId
  if (jid.value) query.journeyId = jid.value
  if (oid.value) query.operatingCaseId = oid.value
  if (sc.value?.rmId) query.rmId = sc.value.rmId
  return query
}

function goPrevisit() {
  persistReference()
  router.push({ path: '/engagement/previsit/gaps', query: sliceQuery() })
}

function goInMeeting() {
  persistReference()
  if (jid.value) {
    router.push({ name: 'InMeetingAssistant', params: { id: jid.value }, query: sliceQuery() })
    return
  }
  router.push({ path: '/in-meeting', query: sliceQuery() })
}

async function loadCustomers() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    custs.value = await fetchCustomers()
    const qid = String(route.query.customerId || '')
    const preferred =
      (qid && custs.value.find((c) => c.customerId === qid))
      || custs.value.find((c) => c.customerId === 'CUST-CORP-0001')
      || custs.value[0]
    if (preferred) {
      sc.value = preferred
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取客户列表'
    custs.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  const ids = new Set((restored.draftId || '').split(',').filter(Boolean))
  keyWork.value = keyWork.value.map((k) => ({ ...k, done: ids.has(k.id) }))
  loadCustomers()
})
onBeforeUnmount(persistReference)
</script>

<style scoped>
.ew {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--space-6);
}
.p11-start-error {
  color: var(--color-danger);
  font-size: 13px;
  margin: 0 0 12px;
}

/* Context Bar */
.ew-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
}
.ew-bar-left,
.ew-bar-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.ew-bar-label {
  color: var(--text-tertiary);
  font-size: 12px;
}
.ew-bar-sep {
  color: var(--border-light);
}
.ew-bar em {
  color: var(--text-tertiary);
  font-style: italic;
}
.start-journey-btn {
  height: 28px;
  padding: 0 12px;
  border: 0;
  border-radius: 4px;
  background: var(--gits-amber-400, #f0a020);
  color: #1a1308;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}
.start-journey-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* Main Layout */
.ew-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: var(--space-5);
  align-items: start;
}
.ew-body {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Panel */
.panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}
.panel-header h3 {
  margin: 0;
  font-size: var(--text-base);
  color: var(--text-primary);
}

/* Key Work */
.kw-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
}
.kw-done {
  color: var(--text-tertiary);
  text-decoration: line-through;
}

/* Activity timeline */
.tl-empty {
  color: var(--text-tertiary);
  font-size: 13px;
  padding: var(--space-3) 0;
}
.tl-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.tl-item {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-left: 3px solid transparent;
  padding-left: var(--space-3);
}
.tl-item.done .tl-title {
  color: var(--color-success);
}
.tl-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  background: var(--bg-hover);
  flex-shrink: 0;
}
.tl-content {
  min-width: 0;
}
.tl-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}
.tl-time {
  font-size: 11px;
  color: var(--text-tertiary);
}

/* Customer modal */
.cs-list {
  max-height: 300px;
  overflow-y: auto;
  margin-top: var(--space-3);
}
.cs-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.cs-item:hover {
  background: var(--bg-hover);
}

@media (max-width: 900px) {
  .ew-main {
    grid-template-columns: 1fr;
  }
  .ew-bar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
