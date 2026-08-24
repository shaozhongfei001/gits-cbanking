<template>
  <div class="customer-view">
    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
    </div>

    <template v-else-if="context">
      <!-- 客户基本信息 -->
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

      <!-- KYC 页面知识属于访前 KI-FRONT-005，不展示 H2 种子缺口卡片 -->
      <div class="section kyc-section">
        <h3 class="section-title">KYC缺口摘要</h3>
        <p class="dkws-empty-hint">DKWS 未返回该条目，请在访前报告 KI-FRONT-005 查看</p>
      </div>

      <!-- 产品匹配属于访前 KI-FRONT-006，只展示 DKWS Skill 返回项 -->
      <div class="section product-section">
        <h3 class="section-title">产品匹配</h3>
        <div v-if="productMatches.length" class="product-list">
          <div v-for="item in productMatches" :key="item.productId" class="product-item">
            <span class="product-name">{{ item.productName }}</span>
            <span v-if="item.reason" class="product-reason">{{ item.reason }}</span>
          </div>
        </div>
        <p v-else class="dkws-empty-hint">DKWS 未返回该条目，请在访前报告 KI-FRONT-006 查看</p>
      </div>

      <!-- 机会信号 -->
      <div class="section">
        <h3 class="section-title">机会信号</h3>
        <div v-if="context.opportunitySignals?.length" class="signal-list">
          <SignalCard v-for="signal in context.opportunitySignals" :key="signal.signalId" :signal="signal" />
        </div>
        <n-empty v-else description="暂无机会信号" size="small" />
      </div>

      <!-- 交易流水属于访前 KI-FRONT-003，不展示 H2 种子明细 -->
      <div class="section tx-section">
        <h3 class="section-title">近期交易流水</h3>
        <p class="dkws-empty-hint">请在访前报告 KI-FRONT-003 查看</p>
      </div>

      <!-- 旅程列表 -->
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
        <n-empty v-else description="暂无经营旅程" size="small" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NSpin, NGrid, NGi, NCard, NTag, NEmpty
} from 'naive-ui'
import RiskBadge from '../components/RiskBadge.vue'
import SignalCard from '../components/SignalCard.vue'
import { fetchCustomerContext, matchProducts } from '../api/engagement'
import type { CustomerContext, Industry, EnterpriseScale, CustomerTier, RiskLevel, JourneyPhase, ProductMatch } from '../api/engagement'
import {
  INDUSTRY_LABELS, ENTERPRISE_SCALE_LABELS, CUSTOMER_TIER_LABELS,
  RISK_LEVEL_LABELS, JOURNEY_PHASE_LABELS
} from '../api/engagement'

const route = useRoute()
const router = useRouter()
const context = ref<CustomerContext | null>(null)
const productMatches = ref<ProductMatch[]>([])
const loading = ref(true)

const industryLabel = computed(() =>
  context.value?.customer.industry ? INDUSTRY_LABELS[context.value.customer.industry as Industry] : '-'
)
const scaleLabel = computed(() =>
  context.value?.customer.enterpriseScale ? ENTERPRISE_SCALE_LABELS[context.value.customer.enterpriseScale as EnterpriseScale] : '-'
)
const tierLabel = computed(() =>
  context.value?.customer.customerTier ? CUSTOMER_TIER_LABELS[context.value.customer.customerTier as CustomerTier] : '-'
)
const riskLabel = computed(() =>
  context.value?.customer.riskLevel ? RISK_LEVEL_LABELS[context.value.customer.riskLevel as RiskLevel] : '-'
)

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
  router.push({ name: 'JourneyTimeline', params: { id: journeyId } })
}

onMounted(async () => {
  const customerId = route.params.id as string
  try {
    context.value = await fetchCustomerContext(customerId)
  } catch (e) {
    console.error('Failed to load customer context:', e)
  }
  try {
    const matches = await matchProducts(customerId)
    productMatches.value = Array.isArray(matches) ? matches : []
  } catch (e) {
    console.error('Failed to load product matches:', e)
    productMatches.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.customer-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-6);
}
.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
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
.dkws-empty-hint {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}
.product-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.product-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.product-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: 500;
}
.product-reason {
  font-size: var(--text-xs);
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
