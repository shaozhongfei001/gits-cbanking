<script setup lang="ts">
/**
 * 进入经营旅程 — 确定性解析页（Owner 决议 2026-09-25，替代"裸入口猜旅程"）。
 *
 * 输入：`?customerId=X`（其它页面「进入经营旅程」链接携带）。
 * 解析规则（**不做隐式猜测**）：
 * - 该客户**恰好 1 条未结束**旅程 ⇒ 直接 `replace` 到 `/engagement/workspace/{id}`；
 * - **0 条**未结束 ⇒ 显示空态与「启动旅程」；启动成功即进入新旅程工作区；
 * - **多条**未结束 ⇒ 列出让用户选择（每条给出确定的 journeyId）。
 *
 * 红线：本页绝不回退到"最近一次会话状态"或硬编码客户；无 customerId 时直接给出错误态与出口。
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NSpin, NTag, useMessage } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import { formatDateTime } from '../utils/datetime'
import {
  fetchCustomerJourneys,
  formatApiError,
  startJourney,
  JOURNEY_PHASE_LABELS,
  type CustomerJourney,
  type JourneyPhase,
} from '../api/engagement'

const PAGE_ID = 'P45'
const OBJECT_TYPE = '经营旅程 Journey'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const customerId = computed(() => String(route.query.customerId || '').trim())
const journeys = ref<CustomerJourney[]>([])
const loading = ref(true)
const error = ref('')
const starting = ref(false)
const startError = ref('')

const activeJourneys = computed(() => journeys.value.filter(j => j.phase !== 'COMPLETED'))

const objectStatus = computed(() => (loading.value ? '解析中' : `候选 ${activeJourneys.value.length} 条`))

function phaseLabel(phase: JourneyPhase | string): string {
  return JOURNEY_PHASE_LABELS[phase as JourneyPhase] ?? String(phase)
}

function openWorkspace(journeyId: string) {
  router.replace({ name: 'EngagementWorkspace', params: { journeyId } })
}

async function resolve() {
  loading.value = true
  error.value = ''
  if (!customerId.value) {
    loading.value = false
    error.value = '缺少 customerId，无法确定性解析经营旅程。请从「经营旅程」列表进入。'
    return
  }
  try {
    journeys.value = await fetchCustomerJourneys(customerId.value)
    if (activeJourneys.value.length === 1) {
      // 唯一候选 ⇒ 直接进入（确定性，无歧义）
      openWorkspace(activeJourneys.value[0].journeyId)
      return
    }
  } catch (e: unknown) {
    error.value = formatApiError(e, '无法获取该客户的经营旅程')
    journeys.value = []
  } finally {
    loading.value = false
  }
}

async function startNewJourney() {
  if (starting.value || !customerId.value) return
  starting.value = true
  startError.value = ''
  try {
    const result = await startJourney(customerId.value)
    message.success(`旅程已启动：${result.journeyName || result.journeyId}`)
    openWorkspace(result.journeyId)
  } catch (e: unknown) {
    startError.value = formatApiError(e, '启动旅程失败')
  } finally {
    starting.value = false
  }
}

onMounted(resolve)
</script>

<template>
  <div class="journey-enter" data-testid="journey-enter">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="进入经营旅程"
    />
    <SignalsDomainTabs />

    <div v-if="loading" class="enter-state" data-testid="journey-enter-loading">
      <NSpin size="medium" />
      <span>正在解析该客户的经营旅程…</span>
    </div>

    <div v-else-if="error" class="enter-state enter-error" data-testid="journey-enter-error">
      <p>{{ error }}</p>
      <NButton size="small" @click="router.push({ name: 'JourneysHome' })">返回经营旅程列表</NButton>
    </div>

    <!-- 0 条未结束 ⇒ 引导启动 -->
    <div v-else-if="activeJourneys.length === 0" class="enter-state" data-testid="journey-enter-none">
      <p>客户 {{ customerId }} 暂无进行中的经营旅程。</p>
      <div class="enter-actions">
        <NButton size="small" type="primary" :loading="starting" data-testid="journey-enter-start" @click="startNewJourney">
          启动旅程并进入
        </NButton>
        <NButton size="small" @click="router.push({ name: 'JourneysHome' })">返回经营旅程列表</NButton>
      </div>
      <p v-if="startError" class="enter-error-text" data-testid="journey-enter-start-error">{{ startError }}</p>
    </div>

    <!-- 多条未结束 ⇒ 让用户选（每条给出确定 journeyId） -->
    <div v-else class="enter-state" data-testid="journey-enter-multiple">
      <p>客户 {{ customerId }} 有 {{ activeJourneys.length }} 条进行中的经营旅程，请选择要继续的一条：</p>
      <div class="enter-list">
        <div
          v-for="journey in activeJourneys"
          :key="journey.journeyId"
          class="enter-item"
          :data-testid="`journey-enter-option-${journey.journeyId}`"
        >
          <div class="enter-copy">
            <span class="enter-name">{{ journey.journeyName || journey.journeyId }}</span>
            <span class="enter-meta">
              {{ journey.customerName }} · {{ formatDateTime(journey.startedAt) }} ·
              <span class="mono">{{ journey.journeyId.slice(0, 8) }}</span>
            </span>
          </div>
          <NTag size="small" type="info" :bordered="true">{{ phaseLabel(journey.phase) }}</NTag>
          <NButton size="tiny" type="primary" secondary @click="openWorkspace(journey.journeyId)">继续</NButton>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.journey-enter {
  max-width: 1240px;
  margin: 0 auto;
  padding: 32px 34px 48px;
}

.enter-state {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  padding: 24px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.enter-state p {
  margin: 0;
}

.enter-error {
  color: var(--color-danger);
}

.enter-error-text {
  color: var(--color-danger);
  font-size: 13px;
}

.enter-actions {
  display: flex;
  gap: 8px;
}

.enter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.enter-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}

.enter-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.enter-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.enter-meta {
  font-size: 12px;
  color: var(--v8-nav-text);
}

.mono {
  font-family: var(--font-mono, ui-monospace, monospace);
}
</style>
