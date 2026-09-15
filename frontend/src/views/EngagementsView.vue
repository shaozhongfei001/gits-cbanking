<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  NInput, NGrid, NGi, NTag, NIcon, NEmpty, NButton, NSpin
} from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import {
  listInteractions,
  fetchCustomers,
  fetchCustomerJourneys,
  INTERACTION_CHANNEL_LABELS,
  type InteractionChannel,
  type ListedInteraction,
  type Customer,
  type CustomerJourney,
} from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P10'
const OBJECT_TYPE = '互动 Interaction'

const pageRefs = usePageReferenceStore()

const interactions = ref<ListedInteraction[]>([])
const customers = ref<Customer[]>([])
const customerJourneys = ref<Map<string, CustomerJourney>>(new Map())
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const filter = ref('')
const subtab = ref('list')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: interactions.value.length > 0 || requested.value,
    requested: requested.value,
  }),
)

// 客户名称映射
const customerNameMap = computed(() => {
  const map = new Map<string, string>()
  for (const c of customers.value) {
    map.set(c.customerId, c.customerName)
  }
  return map
})

function getCustomerName(customerId: string): string {
  return customerNameMap.value.get(customerId) || customerId
}

// 关键指标
const metrics = computed(() => {
  const total = interactions.value.length
  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  const thisWeek = interactions.value.filter(i => {
    const d = new Date(i.interactionDate || i.createdAt || '')
    return d >= weekAgo
  }).length
  const recentMonth = interactions.value.filter(i => {
    const d = new Date(i.interactionDate || i.createdAt || '')
    const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    return d >= monthAgo
  }).length
  // 按客户分组统计
  const customerSet = new Set(interactions.value.map(i => i.customerId))
  return {
    total,
    thisWeek,
    recentMonth,
    customerCount: customerSet.size,
  }
})

// 按客户分组的互动记录
const groupedByCustomer = computed(() => {
  const q = filter.value.trim().toLowerCase()
  const filtered = q
    ? interactions.value.filter(item =>
        item.interactionId.toLowerCase().includes(q)
        || item.customerId.toLowerCase().includes(q)
        || (item.summary ?? '').toLowerCase().includes(q)
        || (getCustomerName(item.customerId)).toLowerCase().includes(q)
        || String(item.channel).toLowerCase().includes(q)
        || (item.participants ?? []).some(p => p.toLowerCase().includes(q)),
      )
    : interactions.value

  const groups = new Map<string, ListedInteraction[]>()
  for (const item of filtered) {
    const key = item.customerId
    const list = groups.get(key) || []
    list.push(item)
    groups.set(key, list)
  }
  // 每组按时间倒序
  for (const [, list] of groups) {
    list.sort((a, b) => {
      const da = new Date(a.interactionDate || a.createdAt || 0).getTime()
      const db = new Date(b.interactionDate || b.createdAt || 0).getTime()
      return db - da
    })
  }
  return groups
})

const sortedCustomerIds = computed(() => {
  // 按最新互动时间排序客户
  const entries = Array.from(groupedByCustomer.value.entries())
  entries.sort((a, b) => {
    const latestA = new Date(a[1][0]?.interactionDate || a[1][0]?.createdAt || 0).getTime()
    const latestB = new Date(b[1][0]?.interactionDate || b[1][0]?.createdAt || 0).getTime()
    return latestB - latestA
  })
  return entries.map(([id]) => id)
})

function channelLabel(channel: string): string {
  return INTERACTION_CHANNEL_LABELS[channel as InteractionChannel] || channel
}

function channelColor(channel: string): string {
  switch (channel) {
    case 'IN_PERSON': return '#2080f0'
    case 'PHONE': return '#18a058'
    case 'VIDEO': return '#f0a020'
    case 'EMAIL': return '#909399'
    case 'WECHAT': return '#07c160'
    default: return '#909399'
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hours = d.getHours().toString().padStart(2, '0')
  const minutes = d.getMinutes().toString().padStart(2, '0')
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${month}月${day}日 ${weekDays[d.getDay()]} ${hours}:${minutes}`
}

function formatDuration(seconds?: number): string {
  if (!seconds || seconds <= 0) return ''
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}分钟`
  const hours = Math.floor(minutes / 60)
  const remainMinutes = minutes % 60
  return remainMinutes > 0 ? `${hours}小时${remainMinutes}分` : `${hours}小时`
}

function getSummaryTitle(item: ListedInteraction): string {
  // 从 summary 中提取第一句作为标题
  const s = item.summary || ''
  const dotIdx = s.indexOf('。')
  const firstSentence = dotIdx > 0 ? s.substring(0, dotIdx) : s
  // 截取前30字
  return firstSentence.length > 30 ? firstSentence.substring(0, 30) + '...' : firstSentence
}

/** 获取客户的经营旅程路由：有旅程→JourneyTimeline，无旅程→新建访前路径 */
function getJourneyRoute(customerId: string): string {
  const journey = customerJourneys.value.get(customerId)
  if (journey?.journeyId) {
    return `/journeys/${journey.journeyId}`
  }
  return `/engagement?customerId=${customerId}`
}

/** 获取旅程链接文字 */
function getJourneyLinkText(customerId: string): string {
  const journey = customerJourneys.value.get(customerId)
  return journey?.journeyId ? '查看经营旅程 →' : '新建经营旅程 →'
}

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    viewId: 'interaction_list',
    filter: filter.value,
    subtab: subtab.value,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

async function loadData() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    const [interactionsData, customersData] = await Promise.all([
      listInteractions(),
      fetchCustomers('ALL'),
    ])
    interactions.value = interactionsData
    customers.value = customersData

    // 获取每个客户的旅程
    const journeyMap = new Map<string, CustomerJourney>()
    const customerIds = [...new Set(interactionsData.map(i => i.customerId))]
    await Promise.all(
      customerIds.map(async (cid) => {
        try {
          const journeys = await fetchCustomerJourneys(cid)
          if (journeys.length > 0) {
            journeyMap.set(cid, journeys[0]) // 取最新旅程
          }
        } catch {
          // 单个客户旅程查询失败不影响整体
        }
      }),
    )
    customerJourneys.value = journeyMap
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取互动列表'
    interactions.value = []
    customers.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  filter.value = restored.filter ?? ''
  subtab.value = restored.subtab ?? 'list'
  loadData()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="engagements-view" data-testid="p10-engagements">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="进行中"
      title="互动对象主页"
    />
    <SignalsDomainTabs />

    <!-- 关键指标 -->
    <div class="metrics-bar">
      <div class="metric-card">
        <span class="metric-value">{{ metrics.total }}</span>
        <span class="metric-label">互动记录</span>
      </div>
      <div class="metric-card">
        <span class="metric-value">{{ metrics.thisWeek }}</span>
        <span class="metric-label">本周互动</span>
      </div>
      <div class="metric-card">
        <span class="metric-value">{{ metrics.recentMonth }}</span>
        <span class="metric-label">近30天</span>
      </div>
      <div class="metric-card">
        <span class="metric-value">{{ metrics.customerCount }}</span>
        <span class="metric-label">关联客户</span>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <DisabledAction
        label="同步日历"
        :disabled="true"
        reason="日历同步为写操作且无本 Loop 合同"
        unlockPath="待合同批准后由后续 Loop 启用"
      />
      <n-input
        v-model:value="filter"
        data-testid="p10-filter"
        placeholder="搜索客户、摘要、渠道..."
        style="max-width: 280px"
        clearable
        @update:value="persistReference"
      />
      <router-link class="related-link" to="/engagement" data-testid="p10-open-journey">
        进入经营旅程（访前路径） →
      </router-link>
    </div>

    <!-- 主内容区 -->
    <PageState :status="status" :error="error" idle-description="尚未请求互动列表" @retry="loadData">
      <div v-if="sortedCustomerIds.length" class="interaction-groups" data-testid="p10-interaction-list">
        <div
          v-for="customerId in sortedCustomerIds"
          :key="customerId"
          class="customer-group"
        >
          <!-- 客户分组头 -->
          <div class="group-header">
            <div class="group-header-left">
              <span class="customer-name">{{ getCustomerName(customerId) }}</span>
              <n-tag size="small" :bordered="false" type="info">
                {{ customerId }}
              </n-tag>
              <span class="interaction-count">{{ groupedByCustomer.get(customerId)?.length || 0 }} 条互动</span>
            </div>
            <router-link
              class="group-link"
              :to="getJourneyRoute(customerId)"
              @click="persistReference"
            >
              {{ getJourneyLinkText(customerId) }}
            </router-link>
          </div>

          <!-- 互动记录列表 -->
          <div class="interaction-list">
            <router-link
              v-for="item in groupedByCustomer.get(customerId)"
              :key="item.interactionId"
              class="interaction-card"
              data-testid="p10-interaction-row"
              :to="getJourneyRoute(item.customerId)"
              @click="persistReference"
            >
              <div class="card-left">
                <div class="card-channel" :style="{ backgroundColor: channelColor(String(item.channel)) + '15', color: channelColor(String(item.channel)) }">
                  {{ channelLabel(String(item.channel)) }}
                </div>
              </div>
              <div class="card-body">
                <div class="card-title">{{ getSummaryTitle(item) }}</div>
                <div class="card-summary">{{ item.summary || '-' }}</div>
                <div class="card-meta">
                  <span class="meta-participants">{{ (item.participants || []).join('、') }}</span>
                  <span v-if="item.durationSeconds" class="meta-duration">{{ formatDuration(item.durationSeconds) }}</span>
                </div>
              </div>
              <div class="card-right">
                <div class="card-date">{{ formatDate(item.interactionDate || item.createdAt) }}</div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
      <n-empty v-else description="暂无互动记录。启动旅程请进入访前路径工作台。" />
    </PageState>
  </div>
</template>

<style scoped>
.metrics-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}
.metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 24px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  min-width: 100px;
}
.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--brand-primary);
  line-height: 1.2;
}
.metric-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.toolbar {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 20px;
}
.related-link {
  color: var(--brand-primary);
  align-self: center;
  font-size: 13px;
  text-decoration: none;
  margin-left: auto;
}
.related-link:hover {
  text-decoration: underline;
}

.interaction-groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.customer-group {
  border: 1px solid var(--border-light);
  border-radius: 10px;
  overflow: hidden;
}
.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-elevated, #f8f9fa);
  border-bottom: 1px solid var(--border-light);
}
.group-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.customer-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.interaction-count {
  font-size: 12px;
  color: var(--text-tertiary);
}
.group-link {
  font-size: 13px;
  color: var(--brand-primary);
  text-decoration: none;
}
.group-link:hover {
  text-decoration: underline;
}

.interaction-list {
  display: flex;
  flex-direction: column;
}
.interaction-card {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-light);
  color: inherit;
  text-decoration: none;
  transition: background-color 0.15s;
}
.interaction-card:last-child {
  border-bottom: none;
}
.interaction-card:hover {
  background: var(--bg-hover, rgba(0, 0, 0, 0.02));
}

.card-left {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}
.card-channel {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.card-body {
  flex: 1;
  min-width: 0;
}
.card-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
  line-height: 1.4;
}
.card-summary {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 6px;
}
.card-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-tertiary);
}
.meta-participants {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta-duration {
  white-space: nowrap;
}

.card-right {
  flex-shrink: 0;
  text-align: right;
  min-width: 120px;
}
.card-date {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}
</style>
