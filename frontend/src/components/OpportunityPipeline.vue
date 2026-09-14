<template>
  <div class="pipeline">
    <div class="pipeline-header">
      <h3>机会管线</h3>
      <div class="pipeline-stats">
        <span>活跃: {{ activeCount }}</span>
        <span>总金额: {{ formattedTotal }}</span>
      </div>
    </div>
    <div class="pipeline-columns">
      <div v-for="stage in stages" :key="stage.key" class="pipeline-column">
        <div class="column-header" :class="`stage-${stage.class}`">
          <span class="stage-name">{{ stage.label }}</span>
          <span class="stage-count">{{ getStageItems(stage.key).length }}</span>
        </div>
        <div class="column-body">
          <div
            v-for="opp in getStageItems(stage.key)"
            :key="opp.opportunityId"
            class="pipeline-item"
            @click="$emit('select', opp)"
          >
            <div class="item-type">{{ getTypeLabel(opp.opportunityType) }}</div>
            <div class="item-desc">{{ opp.description }}</div>
            <div v-if="opp.estimatedAmount" class="item-amount">
              {{ formatAmount(opp.estimatedAmount) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Opportunity, OpportunityType, OpportunityStage } from '../api/v11'
import { OPPORTUNITY_TYPE_LABELS, OPPORTUNITY_STAGE_LABELS } from '../api/v11'

const props = defineProps<{
  opportunities: Opportunity[]
}>()

defineEmits<{
  select: [opportunity: Opportunity]
}>()

const stages = [
  { key: 'IDENTIFIED', label: '已识别', class: 'identified' },
  { key: 'QUALIFIED', label: '已确认', class: 'qualified' },
  { key: 'PROPOSAL', label: '方案提议', class: 'proposal' },
  { key: 'NEGOTIATION', label: '谈判中', class: 'negotiation' },
  { key: 'WON', label: '已赢单', class: 'won' },
]

const CLOSED_STATUSES: string[] = ['WON', 'LOST', 'STALE']

/** 后端 estimatedAmount 为字符串，此处仅提取数值用于汇总。 */
function parseAmount(raw?: string): number {
  if (!raw) return 0
  const matched = raw.replace(/,/g, '').match(/-?\d+(\.\d+)?/)
  return matched ? Number(matched[0]) : 0
}

const activeCount = computed(() =>
  props.opportunities.filter(o => !CLOSED_STATUSES.includes(o.status)).length
)

const formattedTotal = computed(() => {
  const total = props.opportunities
    .filter(o => !CLOSED_STATUSES.includes(o.status))
    .reduce((sum, o) => sum + parseAmount(o.estimatedAmount), 0)
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY', maximumFractionDigits: 0 }).format(total)
})

function getStageItems(stage: string) {
  return props.opportunities.filter(o => o.status === stage)
}

function getTypeLabel(type: string) {
  return OPPORTUNITY_TYPE_LABELS[type as OpportunityType] || type
}

function formatAmount(amount?: string) {
  const value = parseAmount(amount)
  if (!value) return ''
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency', currency: 'CNY', maximumFractionDigits: 0
  }).format(value)
}
</script>

<style scoped>
.pipeline { }
.pipeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.pipeline-header h3 {
  font-size: 16px;
  color: #003366;
  margin: 0;
}
.pipeline-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #666;
}
.pipeline-columns {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.pipeline-column {
  min-width: 200px;
  flex: 1;
  background: #fafafa;
  border-radius: 8px;
  padding: 8px;
}
.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
}
.stage-identified { background: #e6f7ff; color: #003366; }
.stage-qualified { background: #e6f7ff; color: #1890ff; }
.stage-proposal { background: #fff7e6; color: #b8860b; }
.stage-negotiation { background: #fff7e6; color: #fa8c16; }
.stage-won { background: #f6ffed; color: #389e0d; }
.stage-count {
  background: rgba(0,0,0,0.1);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
}
.column-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.pipeline-item {
  background: #fff;
  padding: 8px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid #e8e8e8;
  transition: box-shadow 0.2s;
}
.pipeline-item:hover {
  box-shadow: 0 1px 4px rgba(0, 51, 102, 0.15);
}
.item-type {
  font-size: 11px;
  color: #003366;
  font-weight: 600;
}
.item-desc {
  font-size: 13px;
  color: #333;
  margin: 4px 0;
  line-height: 1.4;
}
.item-amount {
  font-size: 14px;
  font-weight: 700;
  color: #003366;
}
</style>
