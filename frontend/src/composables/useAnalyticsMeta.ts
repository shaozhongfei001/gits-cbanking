import { onMounted, ref } from 'vue'
import {
  fetchDimensions,
  fetchOrgs,
  fetchPeriods,
  type AnalyticsDimension,
  type AnalyticsOrg,
} from '../api/analytics'

/** 经营分析页共用元数据（维度/机构/期间），一次挂载拉取。 */
export function useAnalyticsMeta() {
  const dimensions = ref<AnalyticsDimension[]>([])
  const orgs = ref<AnalyticsOrg[]>([])
  const periods = ref<string[]>([])
  const metaLoading = ref(true)
  const metaError = ref('')

  onMounted(async () => {
    try {
      const [dims, os, ps] = await Promise.all([
        fetchDimensions(), fetchOrgs(), fetchPeriods(),
      ])
      dimensions.value = dims
      orgs.value = os
      periods.value = ps
    } catch (e: unknown) {
      metaError.value = e instanceof Error ? e.message : '分析元数据加载失败'
    } finally {
      metaLoading.value = false
    }
  })

  return { dimensions, orgs, periods, metaLoading, metaError }
}
