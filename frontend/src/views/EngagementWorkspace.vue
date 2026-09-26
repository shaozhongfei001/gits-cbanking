<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NTag, NTooltip, useMessage } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import StagePath from '../components/shell/StagePath.vue'
import type { StagePathStage } from '../components/shell/StagePath.vue'
import HighlightsMetrics from '../components/shell/HighlightsMetrics.vue'
import {
  fetchCustomers,
  fetchJourney,
  fetchOperatingView,
  completeJourney,
  formatApiError,
  JOURNEY_PHASE_LABELS,
  type Customer,
  type CustomerOperatingViewPayload,
  type JourneyPhase,
} from '../api/engagement'
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
const loadError = ref('')
const custs = ref<Customer[]>([])
const sc = ref<Customer | null>(null)
const jid = ref('')
const jph = ref('')
const oid = ref('')
const journeyName = ref('')
const journeyCompleted = ref(false)
const operatingView = ref<CustomerOperatingViewPayload | null>(null)

const journeyIdParam = computed(() => String(route.params.journeyId || ''))

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

const jpLabel = computed(() => {
  if (!jph.value) return '已启动'
  return JOURNEY_PHASE_LABELS[jph.value as JourneyPhase] ?? jph.value
})
const jpTag = computed<'info' | 'warning' | 'success' | 'default'>(() => {
  if (journeyCompleted.value) return 'success'
  if (previsitStore.previsitDone) return 'info'
  return 'warning'
})

const activityTimeline = computed(() => {
  const items: { icon: string; title: string; time: string; done: boolean }[] = []
  items.push({ icon: '◆', title: '启动旅程', time: jid.value ? '刚刚' : '', done: !!jid.value })
  if (jid.value) {
    items.push({ icon: '◇', title: '访前准备', time: '', done: previsitStore.previsitDone })
  }
  if (previsitStore.previsitDone) {
    items.push({ icon: '◈', title: '会中互动', time: '', done: journeyCompleted.value })
  }
  if (journeyCompleted.value) {
    items.push({ icon: '◉', title: '访后复盘', time: '', done: true })
  }
  return items
})

function goList() {
  router.push({ name: 'JourneysHome' })
}

async function doComplete() {
  if (!jid.value) {
    msg.warning('缺少旅程上下文，无法完成')
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

async function resolveCustomer(customerId: string, customerName: string): Promise<Customer> {
  try {
    custs.value = await fetchCustomers()
    const found = custs.value.find(c => c.customerId === customerId)
    if (found) return found
  } catch {
    custs.value = []
  }
  return { customerId, customerName }
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

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  loadError.value = ''

  const journeyId = journeyIdParam.value
  if (!journeyId) {
    await router.replace({ name: 'JourneysHome' })
    loading.value = false
    return
  }

  try {
    const journey = await fetchJourney(journeyId)
    const customer = await resolveCustomer(journey.customerId, journey.customerName)
    sc.value = customer
    jid.value = journey.journeyId
    jph.value = journey.phase
    oid.value = journey.operatingCaseId
    journeyName.value = journey.journeyName || ''
    journeyCompleted.value = journey.phase === 'COMPLETED'
    previsitStore.setContext({
      journeyId: journey.journeyId,
      operatingCaseId: journey.operatingCaseId,
      customerId: journey.customerId,
      rmId: customer.rmId,
    })
    await previsitStore.loadKycGap(journey.customerId)
    if (previsitStore.kycError) {
      loadError.value = `KYC 缺口画像加载失败：${previsitStore.kycError}（旅程上下文已就绪，首屏指标可能不完整）`
    }
    try {
      operatingView.value = await fetchOperatingView(journey.customerId)
    } catch {
      operatingView.value = null
    }
  } catch (e: unknown) {
    error.value = formatApiError(e, '无法加载该经营旅程')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  const ids = new Set((restored.draftId || '').split(',').filter(Boolean))
  keyWork.value = keyWork.value.map((k) => ({ ...k, done: ids.has(k.id) }))
  load()
})
onBeforeUnmount(persistReference)
</script>

<template>
  <div class="ew" data-testid="p11-engagement-workspace">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="经营旅程"
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

    <PageState :status="status" :error="error" idle-description="尚未加载经营旅程" @retry="load">
      <!-- Hero: 客户姓名 + 旅程阶段 -->
      <div class="ew-hero" data-testid="p11-hero">
        <h1 class="ew-hero-name">{{ sc?.customerName || '未选择客户' }}</h1>
        <div class="ew-hero-meta">
          <span v-if="jpLabel" class="ew-hero-phase badge badge--info">{{ jpLabel }}</span>
          <span v-if="journeyName" class="ew-hero-journey">{{ journeyName }}</span>
        </div>
      </div>

      <!-- 阶段 Path -->
      <StagePath :stages="stages" :current-key="currentStage" :completed-keys="completedStages" />

      <!-- 状态栏 -->
      <div class="ew-bar" data-testid="p11-journey-bar">
        <div class="ew-bar-left">
          <span class="ew-bar-label">当前客户</span>
          <n-tag v-if="sc" type="info">{{ sc.customerName }}</n-tag>
          <em v-else>未选择</em>
          <span class="ew-bar-sep">|</span>
          <span class="ew-bar-label">旅程</span>
          <n-tag v-if="jid" :type="jpTag">{{ jpLabel }}</n-tag>
          <em v-else>未启动</em>
          <template v-if="journeyName">
            <span class="ew-bar-sep">|</span>
            <span class="ew-bar-name" data-testid="p11-journey-name">{{ journeyName }}</span>
          </template>
        </div>
        <div class="ew-bar-right">
          <n-button size="small" data-testid="p11-back-list" @click="goList">返回列表</n-button>
          <n-button
            v-if="jid && !journeyCompleted"
            type="success"
            size="small"
            :loading="ld"
            data-testid="p11-complete-journey"
            @click="doComplete"
          >
            完成旅程
          </n-button>
        </div>
      </div>
      <p v-if="loadError" class="p11-start-error" data-testid="p11-start-error">{{ loadError }}</p>

      <!-- 主区域 -->
      <main class="ew-body">
          <!-- 指标仪表盘 -->
          <HighlightsMetrics :view="operatingView" :is-loading="loading" />

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

          <!-- 活动时间线 -->
          <section class="panel" data-testid="p11-activity">
            <div class="panel-header">
              <h3>活动时间线</h3>
              <n-tag size="small" type="info">{{ activityTimeline.length }} 项</n-tag>
            </div>
            <div v-if="!jid" class="tl-empty">
              <p>启动旅程后，活动将在此呈现</p>
              <n-button size="small" type="primary" class="tl-empty-action" @click="goList">选择客户启动旅程</n-button>
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

  </div>
</template>

<style scoped>
.ew {
  max-width: 1240px;
  margin: 0 auto;
  padding: 32px 34px 48px;
}
.p11-start-error {
  color: var(--color-danger);
  font-size: 13px;
  margin: 0 0 12px;
}

/* Hero */
.ew-hero {
  margin-bottom: var(--space-4);
}
.ew-hero-name {
  font-family: var(--font-display);
  font-size: 30px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.25;
  margin: 0 0 var(--space-2);
}
.ew-hero-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.ew-hero-phase {
  font-size: var(--text-xs);
}
.ew-hero-journey {
  font-size: var(--text-sm);
  color: var(--text-secondary);
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
  color: var(--v8-nav-text);
  font-size: 12px;
}
.ew-bar-sep {
  color: var(--border-light);
}
.ew-bar em {
  color: var(--v8-nav-text);
  font-style: italic;
}
.ew-bar-name {
  max-width: 420px;
  overflow: hidden;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Main Layout */
.ew-body {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Panel — 深海蓝左边竖线 */
.panel {
  background: var(--bg-surface-soft);
  border: 1px solid var(--border-light);
  border-left: 3px solid var(--brand-primary);
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
  color: var(--v8-nav-text);
  text-decoration: line-through;
}

/* Activity timeline */
.tl-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-8) var(--space-4);
  text-align: center;
  color: var(--v8-nav-text);
  font-size: 13px;
}
.tl-empty p {
  margin: 0 0 var(--space-3);
}
.tl-empty-action {
  margin-top: var(--space-2);
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
  font-size: 11px;
  color: var(--brand-primary);
  background: var(--brand-primary-lighter);
  flex-shrink: 0;
}
.tl-item.done .tl-dot {
  color: var(--color-success);
  background: var(--color-success-bg);
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
  color: var(--v8-nav-text);
}

@media (max-width: 900px) {
  .ew-bar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
