<script setup lang="ts">
/**
 * P45 经营旅程对象主页（列表）—— 二级菜单「经营旅程」的第一入口。
 *
 * 职责（Owner 决议 2026-09-25，方案 B）：
 * - 列：经营旅程名称（关联 journeyId）、客户名称、旅程状态、开始时间、「继续旅程」；
 * - 工具栏「启动旅程」：先选客户（保持既有交互），启动成功即**默认进入该旅程工作区**；
 * - 已存在且**状态未结束**（phase ≠ COMPLETED）的行显示「持续经营」，进入该旅程工作区；
 * - 工作区身份一律由 URL 路径参数承载 ⇒ 本页只产出确定的 journeyId 再跳转，不做隐式猜测。
 *
 * 数据来源：`GET /api/v1/engagement/journey`（OpenAPI `listEngagementJourneys`，无 customerId ⇒ 全量）。
 */
import { computed, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NDataTable, NEmpty, NInput, NModal, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import SignalsDomainTabs from '../components/shell/SignalsDomainTabs.vue'
import RiskBadge from '../components/RiskBadge.vue'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { formatDateTime } from '../utils/datetime'
import {
  fetchAllJourneys,
  fetchCustomers,
  formatApiError,
  startJourney,
  JOURNEY_PHASE_LABELS,
  type Customer,
  type CustomerJourney,
  type JourneyPhase,
} from '../api/engagement'

const PAGE_ID = 'P45'
const OBJECT_TYPE = '经营旅程 Journey'

const router = useRouter()
const message = useMessage()

const journeys = ref<CustomerJourney[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)

// ── 启动旅程（选客户弹窗） ──
const showCustomerPicker = ref(false)
const customers = ref<Customer[]>([])
const customersLoading = ref(false)
const customersError = ref('')
const keyword = ref('')
const starting = ref(false)
const startError = ref('')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: requested.value,
    requested: requested.value,
  }),
)

const objectStatus = computed(() =>
  loading.value ? '加载中' : `共 ${journeys.value.length} 条`,
)

const filteredCustomers = computed(() => {
  if (!keyword.value) return customers.value.slice(0, 50)
  const key = keyword.value.trim().toLowerCase()
  return customers.value
    .filter(c => c.customerName.toLowerCase().includes(key) || c.customerId.toLowerCase().includes(key))
    .slice(0, 50)
})

/** 状态未结束（可继续经营）。 */
function isActive(journey: CustomerJourney): boolean {
  return journey.phase !== 'COMPLETED'
}

function phaseLabel(phase: JourneyPhase | string): string {
  return JOURNEY_PHASE_LABELS[phase as JourneyPhase] ?? String(phase)
}

function phaseTagType(phase: JourneyPhase | string): 'info' | 'success' | 'default' {
  if (phase === 'COMPLETED') return 'success'
  if (phase) return 'info'
  return 'default'
}

const columns = computed<DataTableColumns<CustomerJourney>>(() => [
  {
    title: '经营旅程名称',
    key: 'journeyName',
    minWidth: 300,
    ellipsis: { tooltip: true },
    render(row) {
      return h(
        'a',
        {
          class: 'journey-link',
          href: workspaceHref(row.journeyId),
          'data-testid': `p45-journey-link-${row.journeyId}`,
          title: `经营旅程 ID：${row.journeyId}`,
          onClick: (event: MouseEvent) => {
            event.preventDefault()
            openWorkspace(row.journeyId)
          },
        },
        row.journeyName || row.journeyId,
      )
    },
  },
  {
    title: '经营旅程 ID',
    key: 'journeyId',
    width: 150,
    ellipsis: { tooltip: true },
    render: row => h('span', { class: 'mono', title: row.journeyId }, row.journeyId.slice(0, 8)),
  },
  {
    title: '客户名称',
    key: 'customerName',
    width: 220,
    ellipsis: { tooltip: true },
    render: row => row.customerName || row.customerId,
  },
  {
    title: '旅程状态',
    key: 'phase',
    width: 130,
    render: row => h(
      NTag,
      { size: 'small', type: phaseTagType(row.phase), bordered: true },
      () => phaseLabel(row.phase),
    ),
  },
  {
    title: '开始时间',
    key: 'startedAt',
    width: 170,
    render: row => formatDateTime(row.startedAt),
  },
  {
    title: '继续旅程',
    key: 'actions',
    width: 130,
    render(row) {
      if (!isActive(row)) {
        return h('span', { class: 'ended', 'data-testid': `p45-ended-${row.journeyId}` }, '已结束')
      }
      return h(
        NButton,
        {
          size: 'tiny',
          type: 'primary',
          secondary: true,
          'data-testid': `p45-continue-${row.journeyId}`,
          onClick: (event: MouseEvent) => {
            event.stopPropagation()
            openWorkspace(row.journeyId)
          },
        },
        () => '持续经营',
      )
    },
  },
])

/** 工作区 href（真实链接语义，支持新开标签）。 */
function workspaceHref(journeyId: string): string {
  return router.resolve({ name: 'EngagementWorkspace', params: { journeyId } }).href
}

function openWorkspace(journeyId: string) {
  router.push({ name: 'EngagementWorkspace', params: { journeyId } })
}

/** 行级交互：整行点开该旅程工作区（未结束才可点；已结束行仅作信息展示）。 */
function rowProps(row: CustomerJourney) {
  if (!isActive(row)) {
    return { class: 'journey-row journey-row--ended' }
  }
  return {
    class: 'journey-row',
    style: 'cursor: pointer;',
    tabindex: 0,
    title: '点击进入该经营旅程工作区',
    'data-testid': `p45-row-${row.journeyId}`,
    onClick: () => openWorkspace(row.journeyId),
    onKeydown: (event: KeyboardEvent) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        openWorkspace(row.journeyId)
      }
    },
  }
}

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    journeys.value = await fetchAllJourneys()
  } catch (e: unknown) {
    error.value = formatApiError(e, '无法获取经营旅程列表')
    journeys.value = []
  } finally {
    loading.value = false
  }
}

async function openCustomerPicker() {
  showCustomerPicker.value = true
  startError.value = ''
  if (customers.value.length > 0 || customersLoading.value) return
  customersLoading.value = true
  customersError.value = ''
  try {
    customers.value = await fetchCustomers()
  } catch (e: unknown) {
    customersError.value = formatApiError(e, '无法获取客户列表')
    customers.value = []
  } finally {
    customersLoading.value = false
  }
}

/** 启动旅程：选客户 → 创建 → **默认进入该旅程工作区**（等价于「点击启动旅程 + 进入工作区」）。 */
async function pickCustomer(customer: Customer) {
  if (starting.value) return
  starting.value = true
  startError.value = ''
  try {
    const result = await startJourney(customer.customerId)
    showCustomerPicker.value = false
    customersError.value = ''
    const kycHint = result.kycGapSummary ? `｜KYC: ${result.kycGapSummary}` : ''
    message.success(`旅程已启动：${result.journeyName || result.journeyId}${kycHint}`)
    router.replace({ name: 'EngagementWorkspace', params: { journeyId: result.journeyId } })
  } catch (e: unknown) {
    startError.value = formatApiError(e, '启动旅程失败')
    message.error(startError.value)
  } finally {
    starting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="journey-list" data-testid="p45-journey-list">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      :object-status="objectStatus"
      title="经营旅程对象主页"
    >
      <template #actions>
        <NButton size="small" type="primary" data-testid="p45-start-journey" @click="openCustomerPicker">
          启动旅程
        </NButton>
      </template>
    </ObjectHeader>
    <SignalsDomainTabs />

    <PageState :status="status" :error="error" idle-description="尚未加载经营旅程列表" @retry="load">
      <NDataTable
        v-if="journeys.length > 0"
        :columns="columns"
        :data="journeys"
        :bordered="false"
        :single-line="false"
        size="small"
        :row-key="(row: CustomerJourney) => row.journeyId"
        :row-props="rowProps"
        :max-height="640"
        :scroll-x="1220"
      />
      <NEmpty
        v-else
        data-testid="p45-empty"
        description="暂无经营旅程。点击「启动旅程」选择客户后开始持续经营。"
      />
    </PageState>

    <!-- 启动旅程：选择客户（保持既有交互） -->
    <NModal v-model:show="showCustomerPicker" preset="dialog" title="启动旅程 — 选择客户" style="width: 520px">
      <NInput v-model:value="keyword" placeholder="搜索客户名称或客户号..." clearable />
      <p class="picker-note">启动后将直接进入该客户经营旅程工作区。</p>
      <p v-if="starting" class="picker-state" data-testid="p45-starting">正在启动旅程…</p>
      <p v-else-if="customersLoading" class="picker-state">正在加载客户列表…</p>
      <p v-else-if="customersError" class="picker-error" data-testid="p45-customers-error">
        {{ customersError }}
      </p>
      <p v-else-if="startError" class="picker-error" data-testid="p45-start-error">{{ startError }}</p>
      <p v-else-if="!filteredCustomers.length" class="picker-state">未找到客户</p>
      <div v-else class="picker-list">
        <div
          v-for="c in filteredCustomers"
          :key="c.customerId"
          class="picker-item"
          :data-testid="`p45-pick-${c.customerId}`"
          @click="pickCustomer(c)"
        >
          <span class="picker-name">{{ c.customerName }}</span>
          <RiskBadge :level="c.riskLevel" />
        </div>
      </div>
    </NModal>
  </div>
</template>

<style scoped>
.journey-list {
  max-width: 1240px;
  margin: 0 auto;
  padding: 32px 34px 48px;
}

.journey-list :deep(.journey-row:hover) {
  background: var(--brand-primary-lighter, #eaf4fe);
}

.journey-list :deep(.journey-row:focus-visible) {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: -2px;
}

.journey-list :deep(.journey-row--ended) {
  color: var(--v8-nav-text);
}

.journey-list :deep(.journey-link) {
  color: var(--brand-primary, #1976d2);
  font-weight: 600;
  text-decoration: none;
}

.journey-list :deep(.journey-link:hover) {
  text-decoration: underline;
}

.journey-list :deep(.mono) {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 12px;
  color: var(--v8-nav-text, #596779);
}

.journey-list :deep(.ended) {
  font-size: 12px;
  color: var(--v8-nav-text);
}

.picker-note {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--v8-nav-text);
}

.picker-state {
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--v8-nav-text);
}

.picker-error {
  margin: 12px 0 0;
  font-size: 13px;
  color: var(--color-danger);
}

.picker-list {
  max-height: 320px;
  margin-top: 12px;
  overflow-y: auto;
}

.picker-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.picker-item:hover {
  background: var(--bg-hover);
}

.picker-name {
  font-size: 13px;
  color: var(--text-primary);
}
</style>
