<script setup lang="ts">
import { computed } from 'vue'

/** 轻量横向条形图（维度成员对比/占比，原型「分组柱状图/饼图」的信息等价呈现）。 */
const props = defineProps<{
  title: string
  items: Array<{ label: string; value: number }>
  percent?: boolean
  focus?: string
}>()

const max = computed(() => Math.max(...props.items.map((i) => Math.abs(i.value)), 1e-9))

const fmt = (v: number) =>
  props.percent ? `${(v * 100).toFixed(1)}%` : v.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
</script>

<template>
  <div class="bar-list" data-testid="analytics-bar-list">
    <div class="cap">{{ title }}</div>
    <div v-if="!items.length" class="empty">暂无数据</div>
    <div v-for="item in items" :key="item.label" class="row" :class="{ focus: item.label === focus }">
      <span class="label" :title="item.label">{{ item.label }}</span>
      <span class="track">
        <span class="bar" :style="{ width: `${Math.max((Math.abs(item.value) / max) * 100, 1)}%` }" />
      </span>
      <span class="value">{{ fmt(item.value) }}</span>
    </div>
  </div>
</template>

<style scoped>
.bar-list {
  flex: 1;
  min-width: 380px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 10px 12px;
}
.cap {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-primary);
  margin-bottom: 8px;
}
.empty { color: var(--v8-nav-text); font-size: 13px; padding: 24px 0; text-align: center }
.row { display: flex; align-items: center; gap: 8px; margin-bottom: 7px }
.row.focus .label { font-weight: 700; color: var(--brand-primary) }
.row.focus .bar { background: var(--brand-primary) }
.label { width: 148px; font-size: 12px; color: #2d3748; overflow: hidden; text-overflow: ellipsis; white-space: nowrap }
.track { flex: 1; height: 14px; background: #edf2f7; border-radius: 3px; overflow: hidden }
.bar { display: block; height: 100%; background: #7fa8d4; border-radius: 3px }
.value { width: 88px; text-align: right; font-size: 12px; color: #2d3748; font-variant-numeric: tabular-nums }
</style>
