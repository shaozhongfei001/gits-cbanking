<template>
  <div class="signal-card" :class="`signal-${signal.status.toLowerCase()}`">
    <div class="signal-header">
      <span class="signal-type-badge">{{ signalTypeLabel }}</span>
      <span class="signal-status-badge" :class="`status-${signal.status.toLowerCase()}`">
        {{ statusLabel }}
      </span>
    </div>
    <div class="signal-content">{{ signal.content }}</div>
    <div class="signal-meta">
      <span v-if="signal.confidence != null" class="confidence">
        置信度: {{ (signal.confidence * 100).toFixed(0) }}%
      </span>
      <span class="detected-at">{{ formattedTime }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OpportunitySignal, SignalType, SignalStatus } from '../api/engagement'
import { SIGNAL_TYPE_LABELS, SIGNAL_STATUS_LABELS } from '../api/engagement'

const props = defineProps<{
  signal: OpportunitySignal
}>()

const signalTypeLabel = computed(() =>
  SIGNAL_TYPE_LABELS[props.signal.signalType as SignalType] || props.signal.signalType
)
const statusLabel = computed(() =>
  SIGNAL_STATUS_LABELS[props.signal.status as SignalStatus] || props.signal.status
)
const formattedTime = computed(() => {
  try {
    return new Date(props.signal.detectedAt).toLocaleDateString('zh-CN')
  } catch {
    return props.signal.detectedAt
  }
})
</script>

<style scoped>
.signal-card {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e8ecf4;
  background: #fff;
  transition: box-shadow 0.2s;
}
.signal-card:hover {
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.1);
}
.signal-confirmed {
  border-left: 3px solid #c87f0a;
}
.signal-detected {
  border-left: 3px solid #1a2438;
}
.signal-dismissed {
  border-left: 3px solid #d0d6e0;
  opacity: 0.6;
}
.signal-converted {
  border-left: 3px solid #18a890;
}
.signal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.signal-type-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #eef3fe;
  color: #1a2438;
  font-weight: 600;
}
.signal-status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.status-detected {
  background: #eef3fe;
  color: #1a2438;
}
.status-confirmed {
  background: #fff8ec;
  color: #c87f0a;
}
.status-dismissed {
  background: #f7f9fd;
  color: #999;
}
.status-converted {
  background: #eef9f6;
  color: #18a890;
}
.signal-content {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 8px;
}
.signal-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}
.confidence {
  color: #c87f0a;
  font-weight: 500;
}
</style>
