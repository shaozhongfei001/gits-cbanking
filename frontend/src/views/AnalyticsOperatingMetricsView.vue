<script setup lang="ts">
import { computed, ref } from 'vue'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import AnalyticsResultsPanel from '../components/analytics/AnalyticsResultsPanel.vue'
import AnalyticsFilterBar from '../components/analytics/AnalyticsFilterBar.vue'
import AnalyticsPageNav from '../components/analytics/AnalyticsPageNav.vue'
import { useAnalyticsMeta } from '../composables/useAnalyticsMeta'
import { OPERATING_SCREENS } from '../api/analytics'

/**
 * 经营指标分析（CCRM 经营分析 · 二级菜单）。
 * 页面内导航菜单（左侧）：客户指标分析 / 业务概况分析 / 利润贡献分析 / 风险指标分析。
 * 行=机构（原文口径）；分布维度作为客户范围过滤条件。
 */
const PAGE_ID = 'P18'
const OBJECT_TYPE = '经营指标 Metric'

const { orgs, periods, metaLoading, metaError } = useAnalyticsMeta()

const active = ref(OPERATING_SCREENS[0].id)
const navItems = computed(() => OPERATING_SCREENS.map((s) => ({ id: s.id, label: s.label })))
const activeDef = computed(
  () => OPERATING_SCREENS.find((s) => s.id === active.value) ?? OPERATING_SCREENS[0])

const dim = ref('INDUSTRY')
const orgId = ref('350000')
const period = ref('201012')
</script>

<template>
  <div class="page" data-testid="p18-operating-metrics">
    <ObjectHeader
      :page-id="PAGE_ID"
      :object-type="OBJECT_TYPE"
      object-status="分析"
      title="经营指标"
    />

    <p class="page-desc">按机构评价对公经营表现（客户规模 / 业务规模 / 盈利贡献 / 资产质量）；行=机构，分布维度为客户范围过滤条件。</p>

    <AnalyticsFilterBar
      v-model:dim="dim"
      v-model:org-id="orgId"
      v-model:period="period"
      :dims="activeDef.dims"
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
  </div>
</template>

<style scoped>
.page {
  max-width: 1240px;
  padding: 32px 34px 48px;
}
.page-desc {
  color: var(--v8-nav-text);
  font-size: 14px;
  margin: -4px 0 16px;
}
.layout {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}
.content {
  flex: 1;
  min-width: 0;
}

@media (max-width: 1024px) {
  .page {
    padding: 24px 24px 40px;
  }
  .layout {
    flex-direction: column;
  }
}

@media (max-width: 640px) {
  .page {
    padding: 16px 16px 32px;
  }
}
</style>
