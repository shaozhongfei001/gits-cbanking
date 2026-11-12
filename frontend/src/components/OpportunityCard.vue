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
  border: 1px solid #e8ecf4;
  background: #fff;
  transition: box-shadow 0.2s;
}
.opportunity-card:hover {
  box-shadow: 0 2px 8px rgba(0, 51, 102, 0.1);
}
.opp-identified { border-left: 3px solid #1a2438; }
.opp-qualified { border-left: 3px solid #0048d8; }
.opp-proposal { border-left: 3px solid #c87f0a; }
.opp-negotiation { border-left: 3px solid #f39c12; }
.opp-won { border-left: 3px solid #18a890; }
.opp-lost { border-left: 3px solid #d0d6e0; }
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
  background: #eef3fe;
  color: #1a2438;
  font-weight: 600;
}
.stage-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.stage-identified { background: #eef3fe; color: #1a2438; }
.stage-qualified { background: #eef3fe; color: #0048d8; }
.stage-proposal { background: #fff8ec; color: #c87f0a; }
.stage-negotiation { background: #fff8ec; color: #f39c12; }
.stage-won { background: #eef9f6; color: #18a890; }
.stage-lost { background: #f7f9fd; color: #999; }
.stage-stale { background: #f7f9fd; color: #7a8899; }
.opp-product {
  font-size: 13px;
  color: #1a2438;
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
  color: #1a2438;
  margin-bottom: 8px;
}
.opp-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}
.assignee { color: #1a2438; font-weight: 500; }
.probability { color: #c87f0a; }
</style>
