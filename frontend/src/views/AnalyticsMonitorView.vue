<script setup lang="ts">
import { computed, ref } from 'vue'
import AnalyticsResultsPanel from '../components/analytics/AnalyticsResultsPanel.vue'
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar.vue'
import AnalyticsPageNav from '../components/analytics/AnalyticsPageNav.vue'
import { useAnalyticsMeta } from '../composables/useAnalyticsMeta'
import { MONITOR_SCREENS } from '../api/analytics'

/**
 * 指标监视器（CCRM 经营分析 · 二级菜单）。
 * 页面内导航菜单（左侧）：业务增减变化监控 / 存贷比变化监控 / 不良贷款分布变化监控。
 * 维度限定原文口径（行业 / 客户类型 / 客户类别）；超 ±15% 变动行红色告警。
 */
const { orgs, periods, metaLoading, metaError } = useAnalyticsMeta()

const active = ref(MONITOR_SCREENS[0].id)
const navItems = computed(() => MONITOR_SCREENS.map((s) => ({ id: s.id, label: s.label })))
const activeDef = computed(
  () => MONITOR_SCREENS.find((s) => s.id === active.value) ?? MONITOR_SCREENS[0])

const dim = ref('INDUSTRY')
const orgId = ref('350000')
const period = ref('201012')
</script>

<template>
  <section class="page">
    <h1 class="title">指标监视器</h1>
    <p class="desc">核心业务量当期变动、存贷比水平与不良分布监控；主指标环比超 ±15% 的行红色告警（阈值可配置）。</p>

    <AnalyticsFilterBar
      v-model:dim="dim"
      v-model:org-id="orgId"
      v-model:period="period"
      :dims="MONITOR_SCREENS[0].dims"
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
