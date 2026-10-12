<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NAlert, NButton, NCheckbox, NDataTable, NEmpty, NInput, NInputNumber,
  NSelect, NSpin, NPagination,
} from 'naive-ui'
import type { DataTableColumn, SelectOption } from 'naive-ui'
import {
  COMBO_COLUMNS,
  postComboQuery,
  type AnalyticsRow,
  type ComboQueryFilters,
} from '../api/analytics'
import { fetchDimensions, fetchOrgs, fetchPeriods, type AnalyticsOrg } from '../api/analytics'

/**
 * 组合条件查询分析（CCRM 经营分析 · 二级菜单「组合查询工具」直挂页）。
 * 客户级多条件圈选：属性 / 数值区间（白名单运算符）/ 标识，产出营销或尽调名单。
 */
const orgs = ref<AnalyticsOrg[]>([])
const periods = ref<string[]>([])
const industryOptions = ref<SelectOption[]>([])
const ratingOptions = ref<SelectOption[]>([])
const scaleOptions = ref<SelectOption[]>([])
const metaLoading = ref(true)
const metaError = ref('')

const orgId = ref('350000')
const period = ref('201012')
const custName = ref('')
const creditRating = ref<string[]>([])
const entScale = ref<string[]>([])
const industryCodes = ref<string[]>([])
const ruleMetric = ref('depBal')
const ruleOp = ref<'=' | '>' | '>=' | '<' | '<='>('>=')
const ruleValue = ref<number | null>(5000)
const isKeyCustHq = ref(false)
const isStrategyCust = ref(false)
const isSme = ref(false)

const rows = ref<AnalyticsRow[]>([])
const total = ref(0)
const pageNumber = ref(0)
const pageSize = 20
const loading = ref(false)
const error = ref('')
const searched = ref(false)

const RULE_METRICS: SelectOption[] = [
  { label: '存款时点金额', value: 'depBal' },
  { label: '存款月日均金额', value: 'depAvgDay' },
  { label: '贷款时点金额', value: 'loanBal' },
  { label: '贷款月日均金额', value: 'loanAvgDay' },
  { label: '年结算累计金额', value: 'settAmtYear' },
  { label: '年结算累计笔数', value: 'settCntYear' },
  { label: '年中间业务收入', value: 'feeYear' },
  { label: '年利润贡献', value: 'profitTotalYear' },
  { label: '存贷比', value: 'ldr' },
]
const OPS: SelectOption[] = [
  { label: '=', value: '=' }, { label: '>', value: '>' }, { label: '≥', value: '>=' },
  { label: '<', value: '<' }, { label: '≤', value: '<=' },
]

const orgOptions = computed(() => orgs.value.map((o) => ({ label: o.orgName, value: o.orgId })))
const periodOptions = computed(() =>
  periods.value.map((p) => ({ label: `${p.slice(0, 4)}-${p.slice(4)}`, value: p })).reverse())

onMounted(async () => {
  try {
    const [os, ps, dims] = await Promise.all([fetchOrgs(), fetchPeriods(), fetchDimensions()])
    orgs.value = os
    periods.value = ps
    industryOptions.value =
      (dims.find((d) => d.dimType === 'INDUSTRY')?.members ?? []).map((m) => ({ label: m, value: m }))
    ratingOptions.value =
      (dims.find((d) => d.dimType === 'CREDIT_RATING')?.members ?? []).map((m) => ({ label: m, value: m }))
    scaleOptions.value =
      (dims.find((d) => d.dimType === 'ENT_SCALE')?.members ?? []).map((m) => ({ label: m, value: m }))
  } catch (e: unknown) {
    metaError.value = e instanceof Error ? e.message : '分析元数据加载失败'
  } finally {
    metaLoading.value = false
  }
})

function buildFilters(): ComboQueryFilters {
  return {
    orgId: orgId.value,
    period: period.value,
    ...(custName.value ? { custName: custName.value } : {}),
    ...(creditRating.value.length ? { creditRating: creditRating.value } : {}),
    ...(entScale.value.length ? { entScale: entScale.value } : {}),
    ...(industryCodes.value.length ? { industryCodes: industryCodes.value } : {}),
    ...(ruleValue.value !== null ? {
      amountRules: [{ metric: ruleMetric.value, op: ruleOp.value, value: ruleValue.value }],
    } : {}),
    ...(isKeyCustHq.value ? { isKeyCustHq: true } : {}),
    ...(isStrategyCust.value ? { isStrategyCust: true } : {}),
    ...(isSme.value ? { isSme: true } : {}),
  }
}

async function search(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const data = await postComboQuery(buildFilters(), pageNumber.value, pageSize)
    rows.value = data.rows
    total.value = data.total
    searched.value = true
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '组合查询失败'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function turnPage(p: number): void {
  pageNumber.value = p - 1
  void search()
}

const columns = computed<DataTableColumn[]>(() =>
  COMBO_COLUMNS.map((c) => ({
    title: c.label,
    key: c.key,
    minWidth: c.kind === 'dim' ? 120 : 130,
    align: c.kind === 'dim' ? ('left' as const) : ('right' as const),
    render: (row: Record<string, unknown>) => {
      const v = row[c.key]
      if (c.kind === 'dim') return String(v ?? '—')
      if (v === null || v === undefined || v === '') return '—'
      const n = Number(v)
      return Number.isFinite(n) ? n.toLocaleString('zh-CN', { maximumFractionDigits: 2 }) : String(v)
    },
  })))
</script>

<template>
  <section class="page">
    <h1 class="title">组合条件查询分析</h1>
    <p class="desc">客户级多条件圈选（营销 / 尽调名单）；数值条件由 KERT 白名单校验（fail-closed）。</p>

    <NAlert v-if="metaError" type="error" :show-icon="false" title="无法连接 KERT 分析服务" class="mb">
      {{ metaError }}（/kert-api 代理 → 8107）
    </NAlert>
    <div v-else-if="metaLoading" class="loading"><NSpin size="small" /><span>加载分析选项…</span></div>

    <div v-else class="form">
      <div class="row">
        <label class="ctl"><span>机构</span>
          <NSelect v-model:value="orgId" :options="orgOptions" size="small" style="width: 160px" /></label>
        <label class="ctl"><span>时间</span>
          <NSelect v-model:value="period" :options="periodOptions" size="small" style="width: 120px" /></label>
        <label class="ctl"><span>客户名称</span>
          <NInput v-model:value="custName" size="small" placeholder="模糊匹配" style="width: 160px" clearable /></label>
        <label class="ctl"><span>信用等级</span>
          <NSelect v-model:value="creditRating" :options="ratingOptions" multiple size="small" style="width: 180px" placeholder="不限" clearable /></label>
        <label class="ctl"><span>企业规模</span>
          <NSelect v-model:value="entScale" :options="scaleOptions" multiple size="small" style="width: 150px" placeholder="不限" clearable /></label>
        <label class="ctl"><span>所属行业</span>
          <NSelect v-model:value="industryCodes" :options="industryOptions" multiple size="small" style="width: 200px" placeholder="不限" clearable /></label>
      </div>
      <div class="row">
        <label class="ctl"><span>数值条件</span>
          <NSelect v-model:value="ruleMetric" :options="RULE_METRICS" size="small" style="width: 150px" />
          <NSelect v-model:value="ruleOp" :options="OPS" size="small" style="width: 70px" />
          <NInputNumber v-model:value="ruleValue" size="small" placeholder="金额（万元）" style="width: 150px" clearable /></label>
        <label class="ctl"><NCheckbox v-model:checked="isKeyCustHq" size="small">总行级重点客户</NCheckbox></label>
        <label class="ctl"><NCheckbox v-model:checked="isStrategyCust" size="small">战略客户</NCheckbox></label>
        <label class="ctl"><NCheckbox v-model:checked="isSme" size="small">小企业</NCheckbox></label>
        <NButton type="primary" size="small" :loading="loading" @click="pageNumber = 0; search()">查 询</NButton>
      </div>
    </div>

    <NAlert v-if="error" type="error" :show-icon="false" title="查询失败" class="mb">{{ error }}</NAlert>

    <template v-if="searched && !error">
      <NEmpty v-if="!rows.length && !loading" description="无符合条件的客户" class="empty" />
      <NSpin v-else-if="loading" size="medium" class="empty" />
      <template v-else>
        <NDataTable
          :columns="columns"
          :data="rows"
          :pagination="false"
          size="small"
          :scroll-x="1250"
          data-testid="combo-result-table"
        />
        <footer class="pager">
          <span>共 {{ total }} 户</span>
          <NPagination
            :page="pageNumber + 1"
            :page-size="pageSize"
            :item-count="total"
            size="small"
            @update:page="turnPage"
          />
        </footer>
      </template>
    </template>
  </section>
</template>

<style scoped>
.page { max-width: 1240px; padding: 32px 34px 48px }
.title { font-size: 18px; color: var(--text-primary); margin-bottom: 4px }
.desc { font-size: 13px; color: var(--v8-nav-text); margin-bottom: 14px }
.mb { margin-bottom: 12px }
.loading { display: inline-flex; gap: 8px; align-items: center; font-size: 13px; color: var(--v8-nav-text) }
.form {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 14px;
}
.row { display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin-bottom: 10px }
.row:last-child { margin-bottom: 0 }
.ctl { display: inline-flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-secondary) }
.empty { padding: 40px 0 }
.pager { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 13px; color: var(--text-secondary) }
@media (max-width: 1024px) { .page { padding: 24px 24px 40px } }
@media (max-width: 640px) { .page { padding: 16px 16px 32px } }
</style>
