<template>
  <div class="opportunity-list">
    <div class="list-header">
      <h3>{{ title }}</h3>
      <div class="filter-bar">
        <select v-model="stageFilter" class="filter-select">
          <option value="">全部阶段</option>
          <option v-for="(label, key) in OPPORTUNITY_STAGE_LABELS" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
      </div>
    </div>
    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="filteredOpportunities.length === 0" class="empty-state">暂无机会数据</div>
    <div v-else class="opportunity-items">
      <OpportunityCard
        v-for="o in filteredOpportunities"
        :key="o.opportunityId"
        :opportunity="o"
        @click="$emit('select', o)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Opportunity, OpportunityStage } from '../api/v11'
import { OPPORTUNITY_STAGE_LABELS } from '../api/v11'
import OpportunityCard from './OpportunityCard.vue'

const props = defineProps<{
  opportunities: Opportunity[]
  title?: string
  loading?: boolean
}>()

defineEmits<{
  select: [opportunity: Opportunity]
}>()

const stageFilter = ref('')

const filteredOpportunities = computed(() => {
  if (!stageFilter.value) return props.opportunities
  return props.opportunities.filter(o => o.status === stageFilter.value)
})
</script>

<style scoped>
.opportunity-list { }
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.list-header h3 {
  font-size: 16px;
  color: #003366;
  margin: 0;
}
.filter-bar { display: flex; gap: 8px; }
.filter-select {
  padding: 4px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 13px;
}
.loading-state, .empty-state {
  text-align: center;
  padding: 24px;
  color: #8c8c8c;
}
.opportunity-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
