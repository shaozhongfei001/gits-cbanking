<template>
  <div class="journey-timeline">
    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
    </div>

    <template v-else>
      <!-- 旅程头部 -->
      <div class="journey-header-section">
        <div class="journey-title-row">
          <n-button text @click="goBack">
            &larr; 返回
          </n-button>
          <h2>经营旅程</h2>
          <n-tag :type="phaseColor" size="medium">
            {{ phaseLabel }}
          </n-tag>
        </div>
        <div class="journey-meta-row">
          <span>客户: {{ journey?.customerName }}</span>
          <span>开始时间: {{ formatDate(journey?.startedAt) }}</span>
        </div>
        <PhaseIndicator v-if="journey" :current="journey.phase" />
      </div>

      <!-- 报告区域 -->
      <div v-if="reports.length" class="reports-section">
        <h3 class="section-title">经营报告</h3>
        <div class="reports-list">
          <n-card v-for="report in reports" :key="report.reportId" size="small" class="report-card">
            <template #header>
              <div class="report-header">
                <n-tag size="small" :type="reportTypeColor(report.reportType)">
                  {{ reportTypeLabel(report.reportType) }}
                </n-tag>
                <span class="report-date">{{ formatDate(report.generatedAt) }}</span>
              </div>
            </template>
            <div class="report-content" v-html="renderMarkdown(report.content)" />
          </n-card>
        </div>
      </div>

      <!-- 供应链图谱 -->
      <div v-if="journey?.customerId" class="graph-section">
        <h3 class="section-title">集团关系图谱</h3>
        <div class="graph-container">
          <SupplyChainGraph :customer-id="journey.customerId" />
        </div>
      </div>

      <!-- 时间线内容 -->
      <div class="timeline-section">
        <h3 class="section-title">交互时间线</h3>
        <div v-if="interactions.length" class="timeline">
          <TimelineItem
            v-for="interaction in interactions"
            :key="interaction.interactionId"
            :title="channelLabel(interaction.channel)"
            :subtitle="interaction.summary"
            :time="interaction.interactionDate"
            :color="interactionColor(interaction)"
          >
            <div class="interaction-detail">
              <div class="detail-row">
                <span class="detail-label">渠道:</span>
                <span>{{ channelLabel(interaction.channel) }}</span>
              </div>
              <div v-if="interaction.durationSeconds" class="detail-row">
                <span class="detail-label">时长:</span>
                <span>{{ formatDuration(interaction.durationSeconds) }}</span>
              </div>
              <div v-if="interaction.participants?.length" class="detail-row">
                <span class="detail-label">参与人:</span>
                <span>{{ interaction.participants.join('、') }}</span>
              </div>
            </div>
          </TimelineItem>
        </div>
        <n-empty v-else description="暂无交互记录" />
      </div>

      <!-- 主张列表 -->
      <div class="claims-section">
        <h3 class="section-title">主张与洞察</h3>
        <div v-if="claims.length" class="claims-list">
          <n-card v-for="claim in claims" :key="claim.claimId" size="small" class="claim-card">
            <div class="claim-header">
              <n-tag size="small" :type="claimStatusColor(claim.status)">{{ claim.status }}</n-tag>
              <n-tag size="small" type="info">{{ claim.claimType }}</n-tag>
            </div>
            <div class="claim-content">{{ claim.statement }}</div>
          </n-card>
        </div>
        <n-empty v-else description="暂无主张记录" />
      </div>

      <!-- 机会信号 -->
      <div class="signals-section">
        <h3 class="section-title">机会信号</h3>
        <div v-if="signals.length" class="signal-list">
          <SignalCard v-for="signal in signals" :key="signal.signalId" :signal="signal" />
        </div>
        <n-empty v-else description="暂无机会信号" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NSpin, NButton, NTag, NCard, NEmpty } from 'naive-ui'
import PhaseIndicator from '../components/PhaseIndicator.vue'
import TimelineItem from '../components/TimelineItem.vue'
import SignalCard from '../components/SignalCard.vue'
import SupplyChainGraph from '../components/SupplyChainGraph.vue'
import { fetchJourney, fetchJourneyInteractions, fetchJourneyClaims, fetchJourneySignals, fetchJourneyReports } from '../api/engagement'
import type { CustomerJourney, ListedInteraction, Claim, OpportunitySignal, RelationshipReport, JourneyPhase, InteractionChannel } from '../api/engagement'
import { JOURNEY_PHASE_LABELS, REPORT_TYPE_LABELS } from '../api/engagement'

const route = useRoute()
const router = useRouter()

const journey = ref<CustomerJourney | null>(null)
const interactions = ref<ListedInteraction[]>([])
const claims = ref<Claim[]>([])
const signals = ref<OpportunitySignal[]>([])
const reports = ref<RelationshipReport[]>([])
const loading = ref(true)

const phaseLabel = computed(() =>
  journey.value ? JOURNEY_PHASE_LABELS[journey.value.phase as JourneyPhase] : ''
)

const phaseColor = computed((): 'success' | 'warning' | 'info' | 'default' => {
  switch (journey.value?.phase) {
    case 'COMPLETED': return 'success'
    case 'POSTVISIT_REVIEW': return 'warning'
    case 'KYC_COLLECT': return 'info'
    default: return 'default'
  }
})

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

function channelLabel(channel: InteractionChannel | string): string {
  const labels: Record<string, string> = {
    'PHONE': '电话',
    'IN_PERSON': '现场拜访',
    'EMAIL': '邮件',
    'WECHAT': '微信',
    'VIDEO': '视频会议',
    'OTHER': '其他'
  }
  return labels[channel] || channel
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  const hours = Math.floor(seconds / 3600)
  const mins = Math.round((seconds % 3600) / 60)
  return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`
}

function interactionColor(interaction: ListedInteraction): string {
  if (interaction.channel === 'IN_PERSON') return '#12A7A0'
  if (interaction.channel === 'VIDEO') return '#1976D2'
  if (interaction.channel === 'WECHAT') return '#F2B84B'
  return '#596779'
}

function reportTypeLabel(type: string): string {
  return REPORT_TYPE_LABELS[type as keyof typeof REPORT_TYPE_LABELS] || type
}

function reportTypeColor(type: string): 'success' | 'warning' | 'info' | 'default' {
  switch (type) {
    case 'INTERNAL_RELATIONSHIP': return 'info'
    case 'CRM_CALL': return 'success'
    case 'UPDATED_RELATIONSHIP': return 'warning'
    case 'NEXT_PREVISIT': return 'default'
    default: return 'info'
  }
}

function claimStatusColor(status: string): 'success' | 'warning' | 'error' | 'info' | 'default' {
  switch (status) {
    case 'VERIFIED_FACT': return 'success'
    case 'HUMAN_CONFIRMED': return 'success'
    case 'CANDIDATE': return 'warning'
    case 'CONFLICT': return 'error'
    case 'REJECTED': return 'default'
    default: return 'info'
  }
}

function renderMarkdown(content: string): string {
  return content
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- \[ \] (.+)$/gm, '<div class="todo-item">☐ $1</div>')
    .replace(/^- \[x\] (.+)$/gm, '<div class="todo-item done">☑ $1</div>')
    .replace(/^- (.+)$/gm, '<div class="list-item">• $1</div>')
    .replace(/\n\n/g, '<br/>')
    .replace(/\n/g, '<br/>')
}

function goBack() {
  router.back()
}

onMounted(async () => {
  const journeyId = route.params.id as string
  try {
    const [journeyData, interactionsData, claimsData, signalsData, reportsData] = await Promise.all([
      fetchJourney(journeyId),
      fetchJourneyInteractions(journeyId),
      fetchJourneyClaims(journeyId),
      fetchJourneySignals(journeyId),
      fetchJourneyReports(journeyId)
    ])
    journey.value = journeyData
    interactions.value = interactionsData
    claims.value = claimsData
    signals.value = signalsData
    reports.value = reportsData
  } catch (e) {
    console.error('Failed to load journey:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.journey-timeline {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--space-6);
}
.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-12) 0;
}
.journey-header-section {
  margin-bottom: var(--space-6);
  padding: var(--space-5);
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xs);
}
.journey-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}
.journey-title-row h2 {
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin: 0;
  font-weight: 600;
}
.journey-meta-row {
  display: flex;
  gap: var(--space-6);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-4);
}
.section-title {
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 2px solid #1976D2;
  display: inline-block;
  font-weight: 600;
}
.reports-section,
.graph-section,
.timeline-section,
.claims-section,
.signals-section {
  margin-bottom: var(--space-6);
}
.reports-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.report-card {
  border-left: 3px solid #12A7A0;
}
.report-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}
.report-date {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}
.report-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}
.report-content :deep(h3) {
  font-size: var(--text-base);
  color: var(--text-primary);
  margin: var(--space-3) 0 var(--space-2);
}
.report-content :deep(h4) {
  font-size: var(--text-sm);
  color: var(--text-primary);
  margin: var(--space-2) 0 var(--space-1);
}
.report-content :deep(.list-item) {
  padding-left: var(--space-2);
  margin: var(--space-1) 0;
}
.report-content :deep(.todo-item) {
  padding-left: var(--space-2);
  margin: var(--space-1) 0;
  color: var(--text-secondary);
}
.report-content :deep(.todo-item.done) {
  color: var(--text-tertiary);
  text-decoration: line-through;
}
.graph-container {
  min-height: 300px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  overflow: hidden;
}
.timeline {
  padding-left: var(--space-2);
}
.interaction-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.detail-row {
  display: flex;
  gap: var(--space-2);
  font-size: var(--text-sm);
}
.detail-label {
  color: var(--text-tertiary);
  min-width: 60px;
}
.claims-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.claim-card {
  border-left: 3px solid #1976D2;
}
.claim-header {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}
.claim-content {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
}
.signal-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
</style>
