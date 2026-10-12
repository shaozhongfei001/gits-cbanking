<script setup lang="ts">
import { NAlert, NButton, NSelect, NSpin } from 'naive-ui'
import type { SelectOption } from 'naive-ui'
import { computed } from 'vue'
import { DIM_LABELS, type AnalyticsOrg } from '../../api/analytics'

/** 分析选项条（原型「分析选项」：分布维度 / 机构 / 时间 / 分析按钮）。 */
const props = defineProps<{
  dims: string[]
  dim: string
  orgs: AnalyticsOrg[]
  orgId: string
  periods: string[]
  period: string
  loading?: boolean
  error?: string
}>()

const emit = defineEmits<{
  (e: 'update:dim', v: string): void
  (e: 'update:orgId', v: string): void
  (e: 'update:period', v: string): void
  (e: 'analyze'): void
}>()

const dimOptions = computed<SelectOption[]>(() =>
  props.dims.map((d) => ({ label: DIM_LABELS[d] ?? d, value: d })))

const orgOptions = computed<SelectOption[]>(() =>
  props.orgs.map((o) => ({ label: o.orgName, value: o.orgId })))

const periodOptions = computed<SelectOption[]>(() =>
  props.periods.map((p) => ({
    label: `${p.slice(0, 4)}-${p.slice(4)}`,
    value: p,
  })).reverse())
</script>

<template>
  <div class="filter-bar" data-testid="analytics-filter-bar">
    <div v-if="error" class="error">
      <NAlert type="error" :show-icon="false" :title="error">
        无法连接 KERT 分析服务（/kert-api 代理 → 8107）。请先启动：
        KERT_ANALYTICS_DUCKDB=… python3 scripts/serve_analytics_api.py
      </NAlert>
    </div>
    <div v-else-if="loading" class="loading"><NSpin size="small" /><span>分析选项加载中…</span></div>
    <div v-else class="controls">
      <label class="ctl">
        <span>分布维度</span>
        <NSelect :value="dim" :options="dimOptions" size="small" style="width: 170px"
                 @update:value="(v: string) => emit('update:dim', v)" />
      </label>
      <label class="ctl">
        <span>机构</span>
        <NSelect :value="orgId" :options="orgOptions" size="small" style="width: 170px"
                 @update:value="(v: string) => emit('update:orgId', v)" />
      </label>
      <label class="ctl">
        <span>时间</span>
        <NSelect :value="period" :options="periodOptions" size="small" style="width: 120px"
                 @update:value="(v: string) => emit('update:period', v)" />
      </label>
      <NButton type="primary" size="small" @click="emit('analyze')">分 析</NButton>
    </div>
  </div>
</template>

<style scoped>
.filter-bar { margin-bottom: 12px }
.controls { display: flex; flex-wrap: wrap; gap: 16px; align-items: center }
.ctl { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: #4a5568 }
.loading { display: inline-flex; gap: 8px; align-items: center; font-size: 13px; color: var(--v8-nav-text) }
</style>
