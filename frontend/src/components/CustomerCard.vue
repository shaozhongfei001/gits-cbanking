<template>
  <n-card class="customer-card" hoverable tabindex="0" role="link" :aria-label="`查看 ${customer.customerName} 详情`" @click="$emit('click')" @keydown.enter="$emit('click')">
    <div class="card-header">
      <span class="customer-name">{{ customer.customerName }}</span>
      <RiskBadge :level="customer.riskLevel" />
    </div>
    <div class="card-body">
      <div class="next-action">
        <span class="next-action__label">下一步</span>
        <span class="next-action__text">{{ nextActionText }}</span>
      </div>
      <div class="info-row">
        <span class="label">层级</span>
        <span class="value tier">{{ tierLabel }}</span>
      </div>
      <div class="info-row">
        <span class="label">行业</span>
        <span class="value">{{ industryLabel }}</span>
      </div>
      <div v-if="customer.coreTags?.length" class="tags-row">
        <n-tag v-for="tag in customer.coreTags?.slice(0, 3)" :key="tag" size="small" :bordered="false">
          {{ tag }}
        </n-tag>
      </div>
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NCard, NTag } from 'naive-ui'
import RiskBadge from './RiskBadge.vue'
import type { Customer, Industry, EnterpriseScale, CustomerTier } from '../api/engagement'
import { INDUSTRY_LABELS, ENTERPRISE_SCALE_LABELS, CUSTOMER_TIER_LABELS } from '../api/engagement'

const props = defineProps<{
  customer: Customer
}>()

defineEmits<{ click: [] }>()

const industryLabel = computed(() =>
  props.customer.industry ? INDUSTRY_LABELS[props.customer.industry as Industry] : '-'
)
const scaleLabel = computed(() =>
  props.customer.enterpriseScale ? ENTERPRISE_SCALE_LABELS[props.customer.enterpriseScale as EnterpriseScale] : '-'
)
const tierLabel = computed(() =>
  props.customer.customerTier ? CUSTOMER_TIER_LABELS[props.customer.customerTier as CustomerTier] : '-'
)

/** V8.1: 下一步行动——由风险和层级派生（真实场景由旅程/承诺 API 提供） */
const nextActionText = computed(() => {
  if (props.customer.riskLevel === 'HIGH') return '风险跟进'
  if (props.customer.customerTier === 'STRATEGIC') return '经营检视'
  return '常规维护'
})
</script>

<style scoped>
.customer-card {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  border: 1px solid var(--border-light);
  border-radius: 10px;
}
.customer-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 1px 2px rgba(17, 45, 64, 0.05);
}
.customer-card:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.customer-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}
.card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
/* V8.1: 下一步行动突出显示 */
.next-action {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.next-action__label {
  font-size: 11px;
  color: var(--v8-nav-text);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.next-action__text {
  font-size: 13px;
  font-weight: 500;
  color: var(--brand-primary);
}
.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.info-row .label {
  color: var(--v8-nav-text);
}
.info-row .value {
  color: var(--text-primary);
  font-weight: 500;
}
.info-row .tier {
  color: var(--color-warning, #836239);
}
.tags-row {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 4px;
}
</style>
