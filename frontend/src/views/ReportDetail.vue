<template>
  <div class="report-detail">
    <div v-if="loading" class="loading-state">
      <n-spin size="large" />
    </div>
    <div v-else-if="notFoundReason" class="not-found-state" data-testid="report-not-found">
      <n-result status="info" :title="notFoundReason" description="报告只能随旅程查看：请从「旅程时间线」进入，或在地址中补充 ?journeyId=…">
        <template #footer>
          <n-button @click="goBack">返回</n-button>
        </template>
      </n-result>
    </div>
    <template v-else-if="report">
      <div class="report-header">
        <div class="report-title-row">
          <n-button text @click="goBack">&larr; 返回</n-button>
          <h2>{{ reportTypeLabel }}</h2>
          <n-tag :type="reportTypeColor" size="medium">{{ report.reportType }}</n-tag>
        </div>
        <div class="report-meta">
          <span>生成时间: {{ formatDate(report.generatedAt) }}</span>
          <span v-if="report.supersedesReportId">替代报告: {{ report.supersedesReportId.slice(0, 8) }}...</span>
        </div>
      </div>
      <div class="report-content-section">
        <n-card>
          <div class="report-content" v-html="renderedContent" />
        </n-card>
      </div>
      <div v-if="report.basedOnEvidence?.length || report.basedOnReconciliations?.length" class="evidence-section">
        <h3 class="section-title">依据信息</h3>
        <div v-if="report.basedOnEvidence?.length" class="evidence-group">
          <span class="evidence-label">证据引用:</span>
          <div class="evidence-tags">
            <n-tag v-for="e in report.basedOnEvidence" :key="e" size="small" type="info">{{ e }}</n-tag>
          </div>
        </div>
        <div v-if="report.basedOnReconciliations?.length" class="evidence-group">
          <span class="evidence-label">对账引用:</span>
          <div class="evidence-tags">
            <n-tag v-for="r in report.basedOnReconciliations" :key="r" size="small" type="warning">{{ r }}</n-tag>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NSpin, NButton, NTag, NCard, NResult } from 'naive-ui'
import { fetchReport, formatApiError } from '../api/engagement'
import type { RelationshipReport, ReportType } from '../api/engagement'
import { REPORT_TYPE_LABELS } from '../api/engagement'

const route = useRoute()
const router = useRouter()
const report = ref<RelationshipReport | null>(null)
const loading = ref(true)
/** 未取到报告时的可读原因（不得静默空白、不得占位冒充）。 */
const notFoundReason = ref('')

const reportTypeLabel = computed(() =>
  report.value ? REPORT_TYPE_LABELS[report.value.reportType as ReportType] || report.value.reportType : ''
)

const reportTypeColor = computed((): 'success' | 'warning' | 'info' | 'default' => {
  switch (report.value?.reportType) {
    case 'INTERNAL_RELATIONSHIP': return 'info'
    case 'CRM_CALL': return 'default'
    case 'UPDATED_RELATIONSHIP': return 'warning'
    case 'NEXT_PREVISIT': return 'success'
    default: return 'default'
  }
})

const renderedContent = computed(() => {
  if (!report.value?.content) return ''
  try {
    const parsed = JSON.parse(report.value.content)
    return renderStructuredContent(parsed)
  } catch {
    return report.value.content.replace(/\n/g, '<br>')
  }
})

function formatKey(key: string): string {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase()).trim()
}

function renderStructuredContent(data: any): string {
  if (!data || typeof data !== 'object') return String(data)
  let html = ''
  for (const [key, value] of Object.entries(data)) {
    const label = formatKey(key)
    if (Array.isArray(value)) {
      html += `<div class="content-block"><h4>${label}</h4><ul>`
      value.forEach((item: any) => {
        html += typeof item === 'object' && item !== null
          ? `<li>${renderStructuredContent(item)}</li>`
          : `<li>${item}</li>`
      })
      html += '</ul></div>'
    } else if (typeof value === 'object' && value !== null) {
      html += `<div class="content-block"><h4>${label}</h4>${renderStructuredContent(value)}</div>`
    } else {
      html += `<div class="content-field"><span class="field-label">${label}:</span> <span class="field-value">${value}</span></div>`
    }
  }
  return html
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  try { return new Date(dateStr).toLocaleString('zh-CN') } catch { return dateStr }
}

function goBack() { router.back() }

onMounted(async () => {
  const reportId = route.params.id as string
  const journeyId = route.query.journeyId as string | undefined
  try {
    if (!journeyId) {
      // 诚实降级：不得用占位数据冒充报告（E2E F-UAT1-06）
      notFoundReason.value = '报告详情未接入独立端点，需携带 journeyId 上下文才能定位报告'
      return
    }
    const found = await fetchReport(reportId, journeyId)
    if (!found) {
      notFoundReason.value = `未找到报告 ${reportId}（该旅程暂无报告或报告未接入）`
      return
    }
    report.value = found
  } catch (e) {
    notFoundReason.value = `报告加载失败：${formatApiError(e, '未知错误')}`
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.report-detail { max-width: 1240px; margin: 0 auto; padding: 32px 34px 48px; }
.loading-state { display: flex; justify-content: center; padding: 60px 0; }
.report-header { margin-bottom: 24px; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
.report-title-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.report-title-row h2 { font-size: 20px; color: #003366; margin: 0; }
.report-meta { display: flex; gap: 24px; font-size: 13px; color: #666; }
.section-title { font-size: 16px; color: #003366; margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 2px solid #b8860b; display: inline-block; }
.report-content { line-height: 1.8; font-size: 14px; color: #333; }
.report-content :deep(.content-block) { margin-bottom: 16px; }
.report-content :deep(.content-block h4) { font-size: 15px; color: #003366; margin: 0 0 8px; }
.report-content :deep(.content-block ul) { padding-left: 20px; margin: 0; }
.report-content :deep(.content-block li) { margin-bottom: 4px; }
.report-content :deep(.content-field) { margin-bottom: 6px; }
.report-content :deep(.field-label) { color: #8c8c8c; font-weight: 500; }
.report-content :deep(.field-value) { color: #333; }
.evidence-section { margin-top: 24px; }
.evidence-group { margin-bottom: 12px; display: flex; align-items: flex-start; gap: 8px; }
.evidence-label { font-size: 13px; color: #666; min-width: 60px; padding-top: 2px; }
.evidence-tags { display: flex; flex-wrap: wrap; gap: 4px; }
</style>
