<script setup lang="ts">
import {
  ELIGIBILITY_STATUS_LABELS,
  type EligibilityResult,
  type ProductRecommendationStageResult,
} from '../../api/productRecommendation'

defineProps<{
  stages: ProductRecommendationStageResult | null
}>()

function eligibilityClass(status: EligibilityResult['eligibility']): string {
  return `elig-${status.toLowerCase()}`
}
</script>

<template>
  <section class="eligibility" data-testid="eligibility-result-panel">
    <h2>资格与缺口（第一段·硬约束过滤）</h2>

    <div v-if="stages?.eligibilityResults?.length" class="elig-list">
      <article
        v-for="item in stages.eligibilityResults"
        :key="`${item.productId}@${item.productVersion}`"
        class="elig-card"
        :data-testid="`eligibility-${item.productId}`"
      >
        <header>
          <span class="product">{{ item.productId }}@{{ item.productVersion }}</span>
          <span class="badge" :class="eligibilityClass(item.eligibility)">
            {{ ELIGIBILITY_STATUS_LABELS[item.eligibility] }}
          </span>
        </header>

        <ul v-if="item.ruleResults?.length" class="rules">
          <li v-for="(rule, idx) in item.ruleResults" :key="idx" class="rule">
            <span class="rule-result" :class="`rule-${rule.result.toLowerCase()}`">{{ rule.result }}</span>
            <span class="rule-id">{{ rule.ruleId }}@{{ rule.ruleVersion }}</span>
            <span class="rule-reason">{{ rule.reasonCode }}</span>
          </li>
        </ul>

        <div v-if="item.unknowns?.length" class="sub">
          <p class="sub-title">事实缺口</p>
          <ul>
            <li v-for="(u, idx) in item.unknowns" :key="idx">{{ u.question }}</li>
          </ul>
        </div>

        <div v-if="item.reviewRequirements?.length" class="sub">
          <p class="sub-title">专家复核要求</p>
          <ul>
            <li v-for="(r, idx) in item.reviewRequirements" :key="idx">
              {{ r.reason }}<span v-if="r.requiredExpertise">（{{ r.requiredExpertise }}）</span>
            </li>
          </ul>
        </div>
      </article>
    </div>
    <p v-else class="empty">暂无资格判定结果</p>

    <div v-if="stages?.unknowns?.length" class="gap-box" data-testid="eligibility-unknowns">
      <h3>运行级事实缺口</h3>
      <ul>
        <li v-for="(u, idx) in stages.unknowns" :key="idx">{{ u }}</li>
      </ul>
    </div>

    <div v-if="stages?.conflicts?.length" class="gap-box gap-conflict" data-testid="eligibility-conflicts">
      <h3>权威证据冲突</h3>
      <ul>
        <li v-for="(c, idx) in stages.conflicts" :key="idx">{{ c }}</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.eligibility h2 {
  font-size: 16px;
  margin: 0 0 12px;
}
.elig-list {
  display: grid;
  gap: 10px;
}
.elig-card {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}
.elig-card header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.product {
  font-weight: 600;
  font-size: 13px;
}
.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 10px;
}
.elig-eligible {
  color: #087771;
  background: rgba(18, 167, 160, 0.12);
}
.elig-ineligible {
  color: #b91c1c;
  background: rgba(220, 38, 38, 0.1);
}
.elig-unknown {
  color: #92400e;
  background: rgba(217, 119, 6, 0.12);
}
.elig-review_required {
  color: #6d28d9;
  background: rgba(124, 58, 237, 0.12);
}
.rules {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 6px;
}
.rule {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.rule-result {
  font-weight: 700;
  font-size: 11px;
}
.rule-pass {
  color: #087771;
}
.rule-fail {
  color: #b91c1c;
}
.rule-unknown,
.rule-review_required {
  color: #92400e;
}
.rule-id {
  font-family: monospace;
  color: var(--text-secondary);
}
.rule-reason {
  color: var(--text-tertiary);
  overflow-wrap: anywhere;
}
.sub {
  margin-top: 8px;
  font-size: 12px;
}
.sub-title {
  margin: 0 0 4px;
  color: var(--text-tertiary);
  font-size: 12px;
}
.sub ul,
.gap-box ul {
  margin: 0;
  padding-left: 18px;
}
.gap-box {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px dashed var(--border-light);
  border-radius: 8px;
  font-size: 13px;
}
.gap-box h3 {
  margin: 0 0 6px;
  font-size: 13px;
}
.gap-conflict {
  border-color: rgba(220, 38, 38, 0.4);
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
