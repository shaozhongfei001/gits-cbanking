<template>
  <span class="risk-badge" :class="levelClass">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RiskLevel } from '../api/engagement'
import { RISK_LEVEL_LABELS } from '../api/engagement'

const props = defineProps<{
  level?: RiskLevel | string
}>()

const label = computed(() =>
  props.level ? RISK_LEVEL_LABELS[props.level as RiskLevel] || props.level : '未评估'
)

const levelClass = computed(() => {
  switch (props.level) {
    case 'HIGH': return 'risk-high'
    case 'MEDIUM': return 'risk-medium'
    case 'LOW': return 'risk-low'
    default: return 'risk-unknown'
  }
})
</script>

<style scoped>
.risk-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}
.risk-high {
  background: #fdf3f1;
  color: #c0392b;
  border: 1px solid #ffa39e;
}
.risk-medium {
  background: #fff8ec;
  color: #d46b08;
  border: 1px solid #ffd591;
}
.risk-low {
  background: #eef9f6;
  color: #18a890;
  border: 1px solid #b7eb8f;
}
.risk-unknown {
  background: #f7f9fd;
  color: #7a8899;
  border: 1px solid #d0d6e0;
}
</style>
