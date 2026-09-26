<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AnalyticsResultsPanel from '../components/analytics/AnalyticsResultsPanel.vue'
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar.vue'
import AnalyticsPageNav from '../components/analytics/AnalyticsPageNav.vue'
import { useAnalyticsMeta } from '../composables/useAnalyticsMeta'
import { ALL_DIMS, SEGMENT_BIZ_TABS, SEGMENT_SCREENS } from '../api/analytics'

/**
 * 细分客群分析（CCRM 经营分析 · 二级菜单）。
 * 页面内导航菜单（左侧）：客户分布特征分析 / 细分客户业务分析
 * （子项：存款业务 / 贷款业务 / 中间业务 / 结算量业务）。
 * 行=维度成员（行业/信用等级/企业规模…）。
 */
const { orgs, periods, metaLoading, metaError } = useAnalyticsMeta()

const active = ref('distribution')

const navItems = computed(() => [
  { id: 'distribution', label: '客户分布特征分析' },
  {
    id: 'business',
    label: '细分客户业务分析',
    children: SEGMENT_BIZ_TABS.map((t) => ({ id: `biz-${t.bizType}`, label: t.label })),
  },
])

const activeBiz = computed(() =>
  SEGMENT_BIZ_TABS.find((t) => `biz-${t.bizType}` === active.value))
const activeDef = computed(() =>
  activeBiz.value ? activeBiz.value.def : SEGMENT_SCREENS[0])

/** 细分客户业务屏的维度受限（原文口径：行业/信用等级/企业规模）。 */
const allowedDims = computed(() =>
  activeBiz.value ? activeBiz.value.def.dims : [...ALL_DIMS])

const dim = ref('INDUSTRY')
const orgId = ref('350000')
const period = ref('201012')

watch(active, () => {
  if (!allowedDims.value.includes(dim.value)) dim.value = 'INDUSTRY'
})
</script>

<template>
  <section class="page">
    <h1 class="title">细分客群分析</h1>
    <p class="desc">客群结构画像（数量 / 户均价值 / 基础账户）与分条线业务透视；行=维度成员，分段维度阈值由参数配置驱动。</p>

    <AnalyticsFilterBar
      v-model:dim="dim"
      v-model:org-id="orgId"
      v-model:period="period"
      :dims="allowedDims"
      :orgs="orgs"
      :periods="periods"
      :loading="metaLoading"
      :error="metaError"
    />

    <div class="layout">
      <AnalyticsPageNav v-model="active" :items="navItems" />
      <div class="content">
        <AnalyticsResultsPanel
          :key="active"
          :def="activeDef"
          :biz-type="activeBiz ? activeBiz.bizType : undefined"
          :dim="dim"
          :org-id="orgId"
          :period="period"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.page { max-width: 1240px; padding: 32px 34px 48px }
.title { font-size: 18px; color: var(--text-primary); margin-bottom: 4px }
.desc { font-size: 13px; color: var(--v8-nav-text); margin-bottom: 14px }
.layout { display: flex; gap: 14px; align-items: flex-start }
.content { flex: 1; min-width: 0 }
@media (max-width: 1024px) { .page { padding: 24px 24px 40px } }
@media (max-width: 640px) { .page { padding: 16px 16px 32px } }
</style>
