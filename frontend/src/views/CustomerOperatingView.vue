<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NGrid, NGi, NCard, NTag, NDataTable
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import DisabledAction from '../components/shell/DisabledAction.vue'
import CustomerRecordTabs from '../components/shell/CustomerRecordTabs.vue'
import RiskBadge from '../components/RiskBadge.vue'
import SignalCard from '../components/SignalCard.vue'
import {
  fetchCustomer,
  fetchCustomerContext,
  INDUSTRY_LABELS,
  ENTERPRISE_SCALE_LABELS,
  CUSTOMER_TIER_LABELS,
  RISK_LEVEL_LABELS,
  JOURNEY_PHASE_LABELS,
} from '../api/engagement'
import type {
  Customer,
  CustomerContext,
  Industry,
  EnterpriseScale,
  CustomerTier,
  RiskLevel,
  JourneyPhase,
  TransactionRecord,
} from '../api/engagement'
import { deriveResourceStatus } from '../composables/useResourceStatus'
import { usePageReferenceStore } from '../stores/pageReference'

const PAGE_ID = 'P04'
const OBJECT_TYPE = '客户 Account'

const route = useRoute()
const router = useRouter()
const pageRefs = usePageReferenceStore()

const customerId = computed(() => String(route.params.id || ''))
const customer = ref<Customer | null>(null)
const context = ref<CustomerContext | null>(null)
const loading = ref(true)
const error = ref('')
const requested = ref(false)
const subtab = ref('overview')

const status = computed(() =>
  deriveResourceStatus({
    loading: loading.value,
    error: error.value,
    hasData: customer.value != null,
    requested: requested.value,
  }),
)

const headerTitle = computed(() => customer.value?.customerName || '客户记录·经营总览')

const industryLabel = computed(() =>
  context.value?.customer.industry ? INDUSTRY_LABELS[context.value.customer.industry as Industry] : '-',
)
const scaleLabel = computed(() =>
  context.value?.customer.enterpriseScale
    ? ENTERPRISE_SCALE_LABELS[context.value.customer.enterpriseScale as EnterpriseScale]
    : '-',
)
const tierLabel = computed(() =>
  context.value?.customer.customerTier
    ? CUSTOMER_TIER_LABELS[context.value.customer.customerTier as CustomerTier]
    : '-',
)
const riskLabel = computed(() =>
  context.value?.customer.riskLevel
    ? RISK_LEVEL_LABELS[context.value.customer.riskLevel as RiskLevel]
    : '-',
)

const txColumns: DataTableColumns<TransactionRecord> = [
  { title: '时间', key: 'occurredAt', width: 120, render: (row) => formatDate(row.occurredAt) },
  { title: '类型', key: 'transactionType', width: 100 },
  { title: '金额', key: 'amount', width: 120, render: (row) => `${row.amount.toLocaleString()} ${row.currency}` },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
]

function persistReference() {
  pageRefs.capture(PAGE_ID, {
    objectType: OBJECT_TYPE,
    recordId: customerId.value,
    viewId: 'operating_overview',
    subtab: subtab.value,
    scrollAnchor: typeof window !== 'undefined' ? window.scrollY : 0,
  })
}

function formatCapital(value?: number): string {
  if (!value) return '-'
  if (value >= 1e8) return `${(value / 1e8).toFixed(2)}亿元`
  if (value >= 1e4) return `${(value / 1e4).toFixed(2)}万元`
  return `${value.toLocaleString()}元`
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN')
  } catch {
    return dateStr
  }
}

function journeyPhaseLabel(phase: JourneyPhase): string {
  return JOURNEY_PHASE_LABELS[phase] || phase
}

function journeyPhaseColor(phase: JourneyPhase): 'success' | 'warning' | 'info' | 'default' | 'error' {
  switch (phase) {
    case 'COMPLETED': return 'success'
    case 'POSTVISIT_REVIEW': return 'warning'
    case 'KYC_COLLECT': return 'info'
    default: return 'default'
  }
}

function goToJourney(journeyId: string) {
  persistReference()
  router.push({ name: 'JourneyTimeline', params: { id: journeyId } })
}

async function loadRecord() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    const [cust, ctx] = await Promise.all([
      fetchCustomer(customerId.value),
      fetchCustomerContext(customerId.value),
    ])
    customer.value = cust
    context.value = ctx
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '无法获取客户经营总览'
    customer.value = null
    context.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const restored = pageRefs.restore(PAGE_ID, OBJECT_TYPE)
  subtab.value = restored.subtab ?? 'overview'
  loadRecord()
})

watch(customerId, () => {
  loadRecord()
})

onBeforeUnmount(persistReference)
</script>

<template>
  <div class="customer-view" data-testid="p04-customer-record">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="经营总览"
      :title="headerTitle"
    />

    <CustomerRecordTabs :customer-id="customerId" />

    <div class="toolbar">
      <DisabledAction
        label="编辑经营结论"
        :disabled="true"
        reason="P04 仅授权 C0 只读消费；经营结论写回无本 Loop 合同"
        unlockPath="后续 Loop 在合同批准后启用写 Action"
      />
    </div>

    <PageState :status="status" :error="error" idle-description="尚未请求客户经营总览" @retry="loadRecord">
      <template v-if="context">
        <div class="section customer-info-section">
          <div class="section-header">
            <h2>{{ context.customer.customerName }}</h2>
            <RiskBadge :level="context.customer.riskLevel" />
          </div>
          <n-grid :cols="4" :x-gap="16" :y-gap="12">
            <n-gi>
              <div class="info-item">
                <span class="info-label">行业</span>
                <span class="info-value">{{ industryLabel }}</span>
              </div>
            </n-gi>
            <n-gi>
              <div class="info-item">
                <span class="info-label">规模</span>
                <span class="info-value">{{ scaleLabel }}</span>
              </div>
            </n-gi>
            <n-gi>
              <div class="info-item">
                <span class="info-label">客户层级</span>
                <span class="info-value tier">{{ tierLabel }}</span>
              </div>
            </n-gi>
            <n-gi>
              <div class="info-item">
                <span class="info-label">风险等级</span>
                <span class="info-value">{{ riskLabel }}</span>
              </div>
            </n-gi>
            <n-gi>
              <div class="info-item">
                <span class="info-label">统一社会信用代码</span>
                <span class="info-value">{{ context.customer.unifiedSocialCreditCode || '-' }}</span>
              </div>
            </n-gi>
            <n-gi>
              <div class="info-item">
                <span class="info-label">注册资本</span>
                <span class="info-value">{{ formatCapital(context.customer.registeredCapitalCny) }}</span>
              </div>
            </n-gi>
            <n-gi>
              <div class="info-item">
                <span class="info-label">客户经理</span>
                <span class="info-value">{{ context.customer.rmName || '-' }}</span>
              </div>
            </n-gi>
            <n-gi>
              <div class="info-item">
                <span class="info-label">管辖区</span>
                <span class="info-value">{{ context.customer.region || '-' }}</span>
              </div>
            </n-gi>
          </n-grid>
          <div v-if="context.customer.relationshipSummary" class="summary-row">
            <span class="info-label">关系概要</span>
            <span class="summary-text">{{ context.customer.relationshipSummary }}</span>
          </div>
        </div>

        <div v-if="context.kycGapProfile" class="section">
          <h3 class="section-title">KYC缺口摘要</h3>
          <n-grid :cols="3" :x-gap="16" :y-gap="12">
            <n-gi>
              <n-card size="small" class="gap-card gap-unknown">
                <div class="gap-count">{{ context.kycGapProfile.unknownItems?.length || 0 }}</div>
                <div class="gap-label">未知项</div>
                <div v-if="context.kycGapProfile.unknownItems?.length" class="gap-items">
                  <n-tag v-for="item in context.kycGapProfile.unknownItems.slice(0, 5)" :key="item" size="small" type="error">{{ item }}</n-tag>
                </div>
              </n-card>
            </n-gi>
            <n-gi>
              <n-card size="small" class="gap-card gap-partial">
                <div class="gap-count">{{ context.kycGapProfile.partialKnownItems?.length || 0 }}</div>
                <div class="gap-label">部分已知</div>
                <div v-if="context.kycGapProfile.partialKnownItems?.length" class="gap-items">
                  <n-tag v-for="item in context.kycGapProfile.partialKnownItems.slice(0, 5)" :key="item" size="small" type="warning">{{ item }}</n-tag>
                </div>
              </n-card>
            </n-gi>
            <n-gi>
              <n-card size="small" class="gap-card gap-stale">
                <div class="gap-count">{{ context.kycGapProfile.staleItems?.length || 0 }}</div>
                <div class="gap-label">过期项</div>
                <div v-if="context.kycGapProfile.staleItems?.length" class="gap-items">
                  <n-tag v-for="item in context.kycGapProfile.staleItems.slice(0, 5)" :key="item" size="small" type="info">{{ item }}</n-tag>
                </div>
              </n-card>
            </n-gi>
          </n-grid>
          <div v-if="context.kycGapProfile.priorityQuestions?.length" class="priority-questions">
            <span class="info-label">优先问题：</span>
            <ul>
              <li v-for="q in context.kycGapProfile.priorityQuestions" :key="q">{{ q }}</li>
            </ul>
          </div>
        </div>

        <div class="section">
          <h3 class="section-title">机会信号</h3>
          <div v-if="context.opportunitySignals?.length" class="signal-list">
            <SignalCard v-for="signal in context.opportunitySignals" :key="signal.signalId" :signal="signal" />
          </div>
          <p v-else class="empty">暂无机会信号</p>
        </div>

        <div v-if="context.recentTransactions?.length" class="section">
          <h3 class="section-title">近期交易流水</h3>
          <n-data-table :columns="txColumns" :data="context.recentTransactions" :bordered="false" size="small" />
        </div>

        <div class="section">
          <h3 class="section-title">经营旅程</h3>
          <div v-if="context.activeJourneys?.length" class="journey-list">
            <n-card
              v-for="journey in context.activeJourneys"
              :key="journey.journeyId"
              class="journey-card"
              hoverable
              @click="goToJourney(journey.journeyId)"
            >
              <div class="journey-header">
                <span class="journey-id">{{ journey.journeyId.slice(0, 8) }}</span>
                <n-tag :type="journeyPhaseColor(journey.phase)" size="small">
                  {{ journeyPhaseLabel(journey.phase) }}
                </n-tag>
              </div>
              <div class="journey-meta">
                <span>开始时间: {{ formatDate(journey.startedAt) }}</span>
              </div>
            </n-card>
          </div>
          <p v-else class="empty">暂无经营旅程</p>
        </div>
      </template>
    </PageState>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.section {
  margin-bottom: var(--space-6);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}
.section-header h2 {
  font-size: var(--text-2xl);
  color: var(--text-primary);
  margin: 0;
  font-weight: 600;
}
.section-title {
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 2px solid var(--brand-primary);
  display: inline-block;
  font-weight: 600;
}
.customer-info-section {
  padding: var(--space-5);
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
}
.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.info-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
.info-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: 500;
}
.info-value.tier {
  color: var(--brand-accent);
}
.summary-row {
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
}
.summary-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}
.gap-card {
  text-align: center;
}
.gap-count {
  font-size: var(--text-3xl);
  font-weight: 700;
}
.gap-unknown .gap-count { color: var(--color-danger); }
.gap-partial .gap-count { color: var(--color-warning); }
.gap-stale .gap-count { color: var(--brand-primary); }
.gap-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: var(--space-1) 0 var(--space-2);
}
.gap-items {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  justify-content: center;
}
.priority-questions {
  margin-top: var(--space-3);
  padding: var(--space-3);
  background: var(--color-warning-bg);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-warning);
}
.priority-questions ul {
  margin: var(--space-1) 0 0;
  padding-left: var(--space-5);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
.signal-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.journey-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-3);
}
.journey-card {
  cursor: pointer;
  transition: transform var(--transition-fast);
}
.journey-card:hover {
  transform: translateY(-1px);
}
.journey-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.journey-id {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
.journey-meta {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
</style>
