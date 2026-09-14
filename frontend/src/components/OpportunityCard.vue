<template>
  <div class="opportunity-card" :class="`opp-${stageClass}`">
    <div class="opp-header">
      <span class="type-badge">{{ typeLabel }}</span>
      <span class="stage-badge" :class="`stage-${stageClass}`">{{ stageLabel }}</span>
    </div>
    <div v-if="opportunity.productName" class="opp-product">{{ opportunity.productName }}</div>
    <div class="opp-description">{{ opportunity.description }}</div>
    <div class="opp-amount" v-if="opportunity.estimatedAmount">
      {{ opportunity.estimatedAmount }}
    </div>
    <div class="opp-meta">
      <span v-if="opportunity.assignedTo" class="assignee">{{ opportunity.assignedTo }}</span>
      <span v-if="opportunity.probability" class="probability">
        赢率: {{ opportunity.probability }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Opportunity, OpportunityType, OpportunityStage } from '../api/v11'
import { OPPORTUNITY_TYPE_LABELS, OPPORTUNITY_STAGE_LABELS } from '../api/v11'

const props = defineProps<{
  opportunity: Opportunity
}>()

const typeLabel = computed(() =>
  OPPORTUNITY_TYPE_LABELS[props.opportunity.opportunityType as OpportunityType] || props.opportunity.opportunityType
)
const stageLabel = computed(() =>
  OPPORTUNITY_STAGE_LABELS[props.opportunity.status as OpportunityStage] || props.opportunity.status
)
const stageClass = computed(() => props.opportunity.status.toLowerCase().replace(/_/g, '-'))
</script>

<style scoped>
.opportunity-card {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  background: #fff;
  transition: box-shadow 0.2s;
}
.opportunity-card:hover {
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.1);
}
.opp-identified { border-left: 3px solid #003366; }
.opp-qualified { border-left: 3px solid #1890ff; }
.opp-proposal { border-left: 3px solid #b8860b; }
.opp-negotiation { border-left: 3px solid #fa8c16; }
.opp-won { border-left: 3px solid #389e0d; }
.opp-lost { border-left: 3px solid #d9d9d9; }
.opp-stale { border-left: 3px solid #bfbfbf; }
.opp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.type-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #e6f7ff;
  color: #003366;
  font-weight: 600;
}
.stage-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.stage-identified { background: #e6f7ff; color: #003366; }
.stage-qualified { background: #e6f7ff; color: #1890ff; }
.stage-proposal { background: #fff7e6; color: #b8860b; }
.stage-negotiation { background: #fff7e6; color: #fa8c16; }
.stage-won { background: #f6ffed; color: #389e0d; }
.stage-lost { background: #f5f5f5; color: #999; }
.stage-stale { background: #fafafa; color: #8c8c8c; }
.opp-product {
  font-size: 13px;
  color: #003366;
  font-weight: 600;
  margin-bottom: 4px;
}
.opp-description {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 8px;
}
.opp-amount {
  font-size: 18px;
  font-weight: 700;
  color: #003366;
  margin-bottom: 8px;
}
.opp-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}
.assignee { color: #003366; font-weight: 500; }
.probability { color: #b8860b; }
</style>
