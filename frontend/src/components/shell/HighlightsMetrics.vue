<script lang="ts">
import { computed } from 'vue'
import type { CustomerOperatingViewPayload } from '../../api/engagement'

/** 旧接口兼容类型（CrmWritebackView 仍用 items prop） */
export interface MetricItem {
  label: string
  value: string
  tone: 'blue' | 'amber' | 'teal'
}
</script>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  view?: CustomerOperatingViewPayload | null
  isLoading?: boolean
  /** 旧接口兼容：CrmWritebackView 传入 items */
  items?: MetricItem[]
}>(), {
  view: null,
  isLoading: false,
})

interface MetricRow {
  key: string
  label: string
  value: string
  sub: string
  pct: number
}

const metrics = computed<MetricRow[]>(() => {
  if (props.items) {
    return props.items.map((m, i) => ({
      key: `metric-${i}`,
      label: m.label,
      value: m.value,
      sub: '',
      pct: 0,
    }))
  }
  if (!props.view) return []
  const e = props.view.entities?.length ?? 0
  const c = props.view.creditFacilities?.length ?? 0
  const g = props.view.groupRelationships?.length ?? 0
  const max = Math.max(e, c, g, 1)
  return [
    { key: 'entities', label: '关联实体', value: String(e), sub: '客户 / 担保人 / 集团', pct: Math.round((e / max) * 100) },
    { key: 'credit', label: '授信设施', value: String(c), sub: '在途 / 已批 / 已用', pct: Math.round((c / max) * 100) },
    { key: 'group', label: '集团关系', value: String(g), sub: '担保 / 投资 / 关联', pct: Math.round((g / max) * 100) },
  ]
})
</script>

<template>
  <div class="metrics-dash" data-testid="highlights-metrics">
    <template v-if="isLoading">
      <div v-for="i in 4" :key="i" class="metric-row">
        <div class="metric-label"><span class="loading-skeleton" style="width:56px;height:12px;display:inline-block" /></div>
        <div class="metric-bar"><span class="loading-skeleton" style="width:100%;height:6px;display:inline-block" /></div>
      </div>
    </template>
    <template v-else-if="metrics.length">
      <div v-for="m in metrics" :key="m.key" class="metric-row">
        <span class="metric-label">{{ m.label }}</span>
        <span class="metric-value">{{ m.value }}</span>
        <span v-if="m.pct > 0" class="metric-bar-track">
          <span
            class="metric-bar-fill"
            :class="{ 'metric-bar-fill--risk': m.key === 'risk' }"
            :style="{ width: m.pct + '%' }"
          />
        </span>
        <span v-if="m.sub" class="metric-sub">{{ m.sub }}</span>
      </div>
    </template>
    <div v-else class="metric-empty">暂无指标数据</div>
  </div>
</template>

<style scoped>
.metrics-dash {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 0;
}
.metric-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 28px;
}
.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 72px;
}
.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  min-width: 28px;
}
.metric-bar-track {
  flex: 1;
  height: 6px;
  background: var(--bg-hover);
  border-radius: 3px;
  overflow: hidden;
}
.metric-bar-fill {
  display: block;
  height: 100%;
  background: var(--brand-accent);
  border-radius: 3px;
  transition: width 0.4s ease;
}
.metric-bar-fill--risk {
  background: var(--color-danger);
}
.metric-sub {
  font-size: 10px;
  color: var(--text-tertiary);
  white-space: nowrap;
}
.metric-empty {
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: center;
  padding: 16px 0;
}
</style>
