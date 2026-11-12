<template>
  <div class="event-card" :class="`event-${severityClass}`">
    <div class="event-header">
      <span class="source-badge">{{ sourceLabel }}</span>
      <span class="severity-badge" :class="`sev-${severityClass}`">{{ confidenceLabel }}</span>
      <span v-if="event.reliability" class="reliability-badge">{{ reliabilityLabel }}</span>
    </div>
    <div class="event-title">{{ event.title }}</div>
    <div class="event-content">{{ event.content }}</div>
    <div v-if="event.possibleBusinessSignal" class="business-signal">
      信号: {{ event.possibleBusinessSignal }}
    </div>
    <div v-if="event.noGoStatement" class="no-go">
      禁止: {{ event.noGoStatement }}
    </div>
    <div class="event-meta">
      <span class="event-date">{{ formattedDate }}</span>
      <span v-if="event.bankUseAllowed" class="bank-usable">可用于银行业务</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ExternalEvent, ExternalEventType, ExternalEventConfidence } from '../api/v11'
import { EXTERNAL_EVENT_TYPE_LABELS, EXTERNAL_EVENT_CONFIDENCE_LABELS, EXTERNAL_EVENT_RELIABILITY_LABELS } from '../api/v11'

const props = defineProps<{
  event: ExternalEvent
}>()

const sourceLabel = computed(() =>
  EXTERNAL_EVENT_TYPE_LABELS[props.event.sourceType as ExternalEventType] || props.event.sourceType
)
const confidenceLabel = computed(() =>
  EXTERNAL_EVENT_CONFIDENCE_LABELS[(props.event.confidence as ExternalEventConfidence)] || props.event.confidence || '中'
)
const reliabilityLabel = computed(() =>
  EXTERNAL_EVENT_RELIABILITY_LABELS[props.event.reliability!] || props.event.reliability || ''
)
const severityClass = computed(() => {
  const sev = props.event.confidence?.toLowerCase() || 'medium'
  return sev
})
const formattedDate = computed(() => {
  try {
    return new Date(props.event.eventDate).toLocaleDateString('zh-CN')
  } catch {
    return props.event.eventDate
  }
})
</script>

<style scoped>
.event-card {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e8ecf4;
  background: #fff;
  transition: box-shadow 0.2s;
}
.event-card:hover {
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.1);
}
.event-critical { border-left: 3px solid #c0392b; }
.event-high { border-left: 3px solid #e74c3c; }
.event-medium { border-left: 3px solid #f39c12; }
.event-low { border-left: 3px solid #18a890; }
.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.source-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #eef3fe;
  color: #1a2438;
  font-weight: 600;
}
.severity-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.sev-critical { background: #fdf3f1; color: #c0392b; }
.sev-high { background: #fff2e8; color: #e74c3c; }
.sev-medium { background: #fff8ec; color: #f39c12; }
.sev-low { background: #eef9f6; color: #18a890; }
.reliability-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #eef3fe;
  color: #3368e0;
  font-weight: 500;
}
.event-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}
.event-content {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
}
.business-signal {
  font-size: 12px;
  color: #1a2438;
  background: #eef3fe;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}
.no-go {
  font-size: 12px;
  color: #c0392b;
  background: #fdf3f1;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}
.event-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}
.bank-usable {
  color: #18a890;
  font-weight: 500;
}
</style>
