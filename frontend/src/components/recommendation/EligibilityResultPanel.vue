<script setup lang="ts">
import {
  ELIGIBILITY_STATUS_LABELS,
  type EligibilityResult,
  type ProductRecommendationStageResult,
} from '../../api/productRecommendation'
import { useProductRecommendationStore } from '../../stores/useProductRecommendationStore'

defineProps<{
  stages: ProductRecommendationStageResult | null
}>()

const store = useProductRecommendationStore()

function eligibilityClass(status: EligibilityResult['eligibility']): string {
  return `elig-${status.toLowerCase()}`
}

/** 产品ID → 中文名称 */
function productName(productId: string): string {
  return store.productNameMap[productId] ?? productId
}

/** 规则结果中文标签 */
function ruleResultLabel(result: string): string {
  const labels: Record<string, string> = {
    PASS: '通过',
    FAIL: '不通过',
    UNKNOWN: '待确认',
    REVIEW_REQUIRED: '需复核',
  }
  return labels[result] ?? result
}

/** reasonCode 中文翻译 — 覆盖 KERT 资格判定规则的全部 reasonCode */
function reasonCodeLabel(code: string): string {
  const labels: Record<string, string> = {
    // ---- 实际出现的 KERT reasonCode ----
    PRODUCT_VERSION_ACTIVE: '产品版本在售',
    INDUSTRY_NOT_PROHIBITED: '行业未受限',
    CUSTOMER_TYPE_ALLOWED: '客户类型允许',
    PREREQUISITE_SATISFIED: '前置条件已满足',
    MATERIALS_COMPLETE: '材料齐备',
    MATERIAL_GAP: '材料缺口',
    SALES_BOUNDARY_OK: '销售边界合规',
    // ---- 可能出现的其他 reasonCode ----
    CUSTOMER_TYPE_MISMATCH: '客户类型不符',
    INDUSTRY_RESTRICTED: '行业受限',
    RISK_RATING_EXCEEDED: '风险评级超限',
    COLLATERAL_INSUFFICIENT: '抵押不足',
    INCOME_INSUFFICIENT: '收入不足',
    CREDIT_HISTORY_ISSUE: '信用记录问题',
    REGULATORY_RESTRICTION: '监管限制',
    PRODUCT_NOT_AVAILABLE: '产品不可用',
    AMOUNT_BELOW_MINIMUM: '金额低于下限',
    TENOR_MISMATCH: '期限不匹配',
    CUSTOMER_TIER_QUALIFIED: '客户等级合格',
    RISK_PROFILE_ACCEPTABLE: '风险画像可接受',
    REGULATORY_COMPLIANT: '合规通过',
    PRODUCT_AVAILABLE: '产品可用',
    AMOUNT_WITHIN_RANGE: '金额在范围内',
    TENOR_MATCHED: '期限匹配',
    SALES_BOUNDARY_VIOLATION: '销售边界违规',
    PREREQUISITE_MISSING: '前置条件缺失',
  }
  return labels[code] ?? code
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
          <span class="product">{{ productName(item.productId) }}</span>
          <span class="product-id">{{ item.productId }}</span>
          <span class="badge" :class="eligibilityClass(item.eligibility)">
            {{ ELIGIBILITY_STATUS_LABELS[item.eligibility] }}
          </span>
        </header>

        <div v-if="item.ruleResults?.length" class="rules">
          <div v-for="(rule, idx) in item.ruleResults" :key="idx" class="rule">
            <span class="rule-result" :class="`rule-${rule.result.toLowerCase()}`">
              {{ ruleResultLabel(rule.result) }}
            </span>
            <span class="rule-reason">{{ reasonCodeLabel(rule.reasonCode) }}</span>
          </div>
        </div>

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
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.product {
  font-weight: 600;
  font-size: 14px;
}
.product-id {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: monospace;
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
  display: grid;
  gap: 4px;
  margin-bottom: 4px;
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
  padding: 0 6px;
  border-radius: 4px;
}
.rule-pass {
  color: #087771;
  background: rgba(8, 119, 113, 0.08);
}
.rule-fail {
  color: #b91c1c;
  background: rgba(185, 28, 28, 0.08);
}
.rule-unknown,
.rule-review_required {
  color: #92400e;
  background: rgba(146, 64, 14, 0.08);
}
.rule-reason {
  color: var(--text-secondary);
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
