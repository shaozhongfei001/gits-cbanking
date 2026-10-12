<script setup lang="ts">
import { computed } from 'vue'

/** 轻量 SVG 折线趋势图（12 个月走势，原型「走势图」口径；零外部依赖）。 */
const props = defineProps<{
  title: string
  points: Array<{ label: string; value: number | null }>
  percent?: boolean
  /** 取数失败原因（非空即显示错误态，不得与"数据不足"混淆） */
  error?: string
}>()

const W = 560
const H = 200
const PAD = 28

const valid = computed(() => props.points.filter((p) => p.value !== null) as Array<{ label: string; value: number }>)
const ready = computed(() => valid.value.length >= 2)

const min = computed(() => (ready.value ? Math.min(...valid.value.map((p) => p.value)) : 0))
const max = computed(() => (ready.value ? Math.max(...valid.value.map((p) => p.value)) : 0))
const span = computed(() => (max.value - min.value) || 1)

function x(i: number): number {
  const n = props.points.length
  if (n <= 1) return PAD
  return PAD + (i * (W - 2 * PAD)) / (n - 1)
}

function y(v: number): number {
  return H - PAD - ((v - min.value) / span.value) * (H - 2 * PAD)
}

const path = computed(() =>
  props.points
    .map((p, i) => (p.value === null ? null : `${x(i)},${y(p.value as number)}`))
    .filter((s): s is string => s !== null)
    .join(' '),
)

const fmt = (v: number) => (props.percent ? `${(v * 100).toFixed(1)}%` : v.toLocaleString('zh-CN', { maximumFractionDigits: 0 }))
</script>

<template>
  <div class="trend-chart" data-testid="analytics-trend-chart">
    <div class="cap">{{ title }}</div>
    <div v-if="error" class="fail" role="alert" data-testid="analytics-trend-error">
      趋势取数失败：{{ error }}
    </div>
    <div v-else-if="!ready" class="empty">趋势数据不足（至少 2 期）</div>
    <svg v-else :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="title">
      <line :x1="PAD" :y1="H - PAD" :x2="W - PAD" :y2="H - PAD" class="axis" />
      <line :x1="PAD" :y1="PAD" :x2="PAD" :y2="H - PAD" class="axis" />
      <polyline :points="path" class="line" />
      <circle
        v-for="(p, i) in points"
        v-show="p.value !== null"
        :key="i"
        :cx="x(i)"
        :cy="p.value === null ? 0 : y(p.value as number)"
        r="3"
        class="dot"
      />
      <text v-for="(p, i) in points" v-show="i % Math.ceil(points.length / 6) === 0" :key="`t${i}`" :x="x(i)" :y="H - 8" class="tick">
        {{ p.label }}
      </text>
      <text :x="PAD + 2" :y="PAD - 8" class="tick val">{{ fmt(max) }}</text>
      <text :x="PAD + 2" :y="H - PAD - 4" class="tick val">{{ fmt(min) }}</text>
    </svg>
  </div>
</template>

<style scoped>
.trend-chart {
  flex: 1;
  min-width: 420px;
  background: #fff;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 10px 12px;
}
.cap {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-primary);
  margin-bottom: 4px;
}
.empty {
  color: var(--v8-nav-text);
  font-size: 13px;
  padding: 40px 0;
  text-align: center;
}
.fail {
  color: #c53030;
  font-size: 13px;
  padding: 40px 0;
  text-align: center;
}
.axis { stroke: #cbd5e1; stroke-width: 1 }
.line { fill: none; stroke: var(--brand-primary); stroke-width: 2 }
.dot { fill: var(--brand-primary) }
.tick { font-size: 9px; fill: var(--v8-nav-text); text-anchor: middle }
.tick.val { text-anchor: start }
</style>
