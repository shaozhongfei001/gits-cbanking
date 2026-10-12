import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  fetchOpportunities, fetchActiveOpportunities, createOpportunity, updateOpportunityStage,
  type Opportunity, type OpportunityStage, type OpportunityType
} from '../api/v11'

/** 后端 estimatedAmount 为字符串（可能含单位或为空），此处仅提取数值用于汇总。 */
function parseAmount(raw?: string): number {
  if (!raw) return 0
  const matched = raw.replace(/,/g, '').match(/-?\d+(\.\d+)?/)
  return matched ? Number(matched[0]) : 0
}

export const useOpportunityStore = defineStore('opportunity', () => {
  const opportunities = ref<Opportunity[]>([])
  const loading = ref(false)
  const error = ref('')

  const CLOSED_STATUSES: string[] = ['WON', 'LOST', 'STALE']

  const activeOpportunities = computed(() =>
    opportunities.value.filter(o => !CLOSED_STATUSES.includes(o.status))
  )

  const wonOpportunities = computed(() =>
    opportunities.value.filter(o => o.status === 'WON')
  )

  const totalEstimatedAmount = computed(() =>
    activeOpportunities.value.reduce((sum, o) => sum + parseAmount(o.estimatedAmount), 0)
  )

  async function loadOpportunities(params?: {
    customerId?: string
    status?: OpportunityStage
    opportunityType?: OpportunityType
    assignedTo?: string
  }) {
    loading.value = true
    error.value = ''
    try {
      opportunities.value = await fetchOpportunities(params ?? {})
    } catch (e: any) {
      error.value = e.message || '加载机会列表失败'
    } finally {
      loading.value = false
    }
  }

  async function loadActiveOpportunities(customerId: string) {
    loading.value = true
    error.value = ''
    try {
      opportunities.value = await fetchActiveOpportunities(customerId)
    } catch (e: any) {
      error.value = e.message || '加载活跃机会失败'
    } finally {
      loading.value = false
    }
  }

  async function addOpportunity(opportunity: Partial<Opportunity>) {
    try {
      const created = await createOpportunity(opportunity)
      opportunities.value.push(created)
      return created
    } catch (e: any) {
      error.value = e.message || '创建机会失败'
      throw e
    }
  }

  async function changeStage(opportunityId: string, stage: OpportunityStage) {
    try {
      await updateOpportunityStage(opportunityId, stage)
      const idx = opportunities.value.findIndex(o => o.opportunityId === opportunityId)
      if (idx >= 0) {
        opportunities.value[idx] = { ...opportunities.value[idx], status: stage }
      }
    } catch (e: any) {
      error.value = e.message || '更新机会阶段失败'
      throw e
    }
  }

  return {
    opportunities, loading, error,
    activeOpportunities, wonOpportunities, totalEstimatedAmount,
    loadOpportunities, loadActiveOpportunities, addOpportunity, changeStage
  }
})
