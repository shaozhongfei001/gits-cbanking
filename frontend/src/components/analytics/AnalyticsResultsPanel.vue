<script setup lang="ts">
import { computed, h, ref, watch } from 'vue'
import { NAlert, NButton, NDataTable, NEmpty, NSpin } from 'naive-ui'
import type { DataTableColumn, DataTableRowKey } from 'naive-ui'
import { fetchMetrics, fetchTrend, type AnalyticsRow, type ScreenDef } from '../../api/analytics'
import BarList from './BarList.vue'
import TrendChart from './TrendChart.vue'

/**
 * 分析结果面板（10 屏共用）：分组表格 + 成员对比条形图 + 选中成员 12 个月趋势。
 * 四态齐备：Loading（NSpin）/ Error（NAlert+重试）/ Empty（NEmpty）/ Success。
 */
const props = defineProps<{
  def: ScreenDef
  dim: string
  orgId: string
  period: string
  bizType?: string
}>()

const loading = ref(false)
const error = ref('')
const rows = ref<AnalyticsRow[]>([])
const focus = ref('')
const trendPoints = ref<Array<{ label: string; value: number | null }>>([])
const trendLoading = ref(false)
// QA FAIL-2026-09-22-AN0-QA-03：趋势请求失败不得静默吞掉（此前整屏显示"趋势数据不足"）
const trendError = ref('')

const PCT_KEYS = ['ldr', 'nplRatio', 'roa', 'roe']

const isMonitor = computed(() => props.def.id.startsWith('monitor-'))
const primaryIsPercent = computed(() => PCT_KEYS.includes(props.def.primary))

/** 透出 KERT 具名错误（ErrorResponse.error.message），无则退回 axios/异常文案。 */
function requestMessage(e: unknown): string {
  const resp = (e as { response?: { data?: { error?: { message?: string } } } })?.response
  return resp?.data?.error?.message
    || (e instanceof Error ? e.message : '分析服务请求失败')
}

async function load(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchMetrics({
      screen: props.def.id, dim: props.dim, orgId: props.orgId,
      period: props.period, ...(props.bizType ? { bizType: props.bizType } : {}),
    })
    rows.value = data.rows
    if (!focus.value && data.rows.length) {
      focus.value = String(data.rows[0].dimValue ?? '')
    }
    void loadTrend()
  } catch (e: unknown) {
    error.value = requestMessage(e)
    rows.value = []
  } finally {
    loading.value = false
  }
}

async function loadTrend(): Promise<void> {
  if (!focus.value) return
  trendLoading.value = true
  trendError.value = ''
  try {
    const t = await fetchTrend({
      screen: props.def.id,
      // 行=机构的屏（经营指标 4 屏）趋势按 ORG 轴取数（dimValue 是机构名）；
      // 其余屏按当前分布维度取数（QA FAIL-2026-09-22-AN0-QA-03 根因之一）。
      dim: props.def.rowAxis === 'ORG' ? 'ORG' : props.dim,
      dimValue: focus.value,
      orgId: props.orgId, metric: props.def.primary, months: 12,
    })
    trendPoints.value = t.points.map((p) => ({ label: `${p.period.slice(4)}月`, value: p.value }))
  } catch (e: unknown) {
    trendPoints.value = []
    trendError.value = requestMessage(e)
  } finally {
    trendLoading.value = false
  }
}

watch(
  () => [props.def.id, props.bizType, props.dim, props.orgId, props.period],
  () => { focus.value = ''; void load() },
  { immediate: true },
)

// ---------------- 列渲染 ----------------

function fmtValue(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—'
  const n = Number(v)
  return Number.isFinite(n) ? n.toLocaleString('zh-CN', { maximumFractionDigits: 2 }) : String(v)
}

function fmtArrow(v: unknown): ReturnType<typeof h> {
  if (v === null || v === undefined || v === '') return h('span', { class: 'na' }, '—')
  const n = Number(v)
  const pct = `${(n * 100).toFixed(1)}%`
  const cls = n >= 0 ? 'up' : 'down'
  const arrow = n >= 0 ? '↑' : '↓'
  return h('span', { class: cls }, `${pct} ${arrow}`)
}

function fmtPct(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—'
  const n = Number(v)
  return Number.isFinite(n) ? `${(n * 100).toFixed(2)}%` : String(v)
}

const columns = computed<DataTableColumn[]>(() =>
  props.def.columns.map((c) => {
    if (c.kind === 'dim') {
      return { title: c.label, key: c.key, minWidth: 130, fixed: 'left' as const }
    }
    const render = (v: unknown) => {
      if (c.kind === 'mom' || c.kind === 'ytd') return fmtArrow(v)
      if (c.kind === 'pct' || c.kind === 'sharePct') return fmtPct(v)
      return fmtValue(v)
    }
    return {
      title: c.label,
      key: c.key,
      align: 'right' as const,
      width: c.kind === 'value' ? 130 : 96,
      render: (row: Record<string, unknown>) => render(row[c.key]),
    }
  }),
)

function rowAlerted(row: AnalyticsRow): boolean {
  if (!isMonitor.value) return false
  const mom = row[`${props.def.primary}Mom`]
  return typeof mom === 'number' && Math.abs(mom) > 0.15
}

const rowProps = (row: AnalyticsRow) => ({
  style: 'cursor: pointer',
  class: { 'row-alert': rowAlerted(row), 'row-focus': String(row.dimValue) === focus.value },
  onClick: () => {
    focus.value = String(row.dimValue ?? '')
    void loadTrend()
  },
})

const barItems = computed(() =>
  rows.value.slice(0, 8).map((r) => ({
    label: String(r.dimValue ?? ''),
    value: Number(r[props.def.primary] ?? 0) || 0,
  })))

const chartTitleSuffix = computed(() =>
  primaryIsPercent.value ? '（%）' : '（万元）')
</script>

<template>
  <section class="panel" :data-testid="`analytics-panel-${def.id}`">
    <header class="panel-cap">
      <span>{{ def.label }}</span>
      <span class="unit">单位：万元 / 户 / %　环比=比上月　较年初=对当年首月</span>
    </header>

    <div v-if="loading" class="state"><NSpin size="medium" /><span>加载中…</span></div>

    <div v-else-if="error" class="state">
      <NAlert type="error" :show-icon="false" title="分析服务不可用">
        <div class="err-body">
          {{ error }}（KERT 分析服务 /kert-api，请确认 KERT_ANALYTICS_DUCKDB 已配置）
          <NButton size="small" @click="load()">重试</NButton>
        </div>
      </NAlert>
    </div>

    <NEmpty v-else-if="!rows.length" description="该条件下无数据" class="state" />

    <template v-else>
      <NDataTable
        :columns="columns"
        :data="rows"
        :row-key="(row: AnalyticsRow) => String(row.dimValue)"
        :row-props="rowProps"
        :pagination="false"
        size="small"
        :scroll-x="def.columns.length * 110"
        class="table"
      />
      <div class="charts">
        <BarList :title="`${def.label} · 各成员对比（点击表格行切换重点）${chartTitleSuffix}`" :items="barItems" :focus="focus" :percent="primaryIsPercent" />
        <div class="trend-wrap">
          <NSpin v-if="trendLoading" size="small" class="trend-spin" />
          <TrendChart
            :title="`${focus} · 12个月趋势（${def.primary}）${chartTitleSuffix}`"
            :points="trendPoints"
            :percent="primaryIsPercent"
            :error="trendError"
          />
        </div>
      </div>
      <p v-if="isMonitor" class="alert-legend">红色行 = 主指标环比变动超 ±15%（告警阈值，KERT 侧计算）</p>
    </template>
  </section>
</template>

<style scoped>
.panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px 14px;
}
.panel-cap {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
  font-weight: 600;
  color: var(--brand-primary);
}
.unit { font-size: 12px; font-weight: 400; color: var(--v8-nav-text) }
.state { padding: 32px 0; display: flex; flex-direction: column; align-items: center; gap: 8px }
.charts { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 14px }
.trend-wrap { flex: 1; min-width: 420px; position: relative }
.trend-spin { position: absolute; top: 8px; right: 12px; z-index: 1 }
.alert-legend { margin-top: 8px; font-size: 12px; color: #c53030 }
.table :deep(.row-alert) td { background: #fff5f5 !important }
.table :deep(.row-focus) td { background: #e8f1fd !important }
.table :deep(.up) { color: #e53e3e }
.table :deep(.down) { color: #38a169 }
.table :deep(.na) { color: var(--v8-nav-text) }
</style>
