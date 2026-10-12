<script setup lang="ts">
import { computed } from 'vue'
import type { ProductFitResult, ProductRecommendationStageResult } from '../../api/productRecommendation'
import { useProductRecommendationStore } from '../../stores/useProductRecommendationStore'

const props = defineProps<{
  stages: ProductRecommendationStageResult | null
}>()

const store = useProductRecommendationStore()

/** 只显示有排名的候选产品（过滤掉 INELIGIBLE 的空壳条目） */
const ranked = computed(() => {
  const list = props.stages?.fitResults ?? []
  return [...list]
    .filter((item) => item.rank != null && item.fitScore != null)
    .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
})

/** 产品ID → 中文名称 */
function productName(productId: string): string {
  return store.productNameMap[productId] ?? productId
}

/** 显示产品标题：中文名（产品ID@版本） */
function productTitle(item: ProductFitResult): string {
  const name = productName(item.productId)
  if (name !== item.productId) {
    return `${name}（${item.productId}@${item.productVersion}）`
  }
  return `${item.productId}@${item.productVersion}`
}

function scoreLabel(item: ProductFitResult): string {
  if (item.fitScore == null) return '—'
  return item.fitScore.toFixed(2)
}

/** 适配度星级（1-5） */
function scoreStars(item: ProductFitResult): string {
  if (item.fitScore == null) return ''
  const n = Math.round(item.fitScore * 5)
  return '★'.repeat(n) + '☆'.repeat(5 - n)
}

function dimensionLabel(dimension: string): string {
  const labels: Record<string, string> = {
    CORE_NEED_FIT: '核心需求匹配',
    SCENARIO_FIT: '场景匹配',
    EXECUTABILITY: '可执行性',
    RELATIONSHIP_INCREMENT: '关系增量',
    PORTFOLIO_SYNERGY: '组合协同',
    EVIDENCE_SUFFICIENCY: '证据充分度',
  }
  return labels[dimension] ?? dimension
}

function dimensionResultLabel(result: string): string {
  const labels: Record<string, string> = {
    STRONG: '强',
    MODERATE: '中',
    WEAK: '弱',
    UNKNOWN: '未知',
  }
  return labels[result] ?? result
}

/** 风险提示中文翻译 */
function riskLabel(risk: string): string {
  const labels: Record<string, string> = {
    REPAYMENT_CAPACITY_VOLATILITY: '还款能力波动',
    INDUSTRY_CYCLE_RISK: '行业周期风险',
    COLLATERAL_COVERAGE_INSUFFICIENT: '抵押覆盖不足',
    CONCENTRATION_RISK: '集中度风险',
    REGULATORY_COMPLIANCE_RISK: '合规风险',
    INTEREST_RATE_RISK: '利率风险',
    FOREIGN_EXCHANGE_RISK: '汇率风险',
    LIQUIDITY_RISK: '流动性风险',
    COUNTERPARTY_RISK: '交易对手风险',
    OPERATIONAL_RISK: '操作风险',
  }
  return labels[risk] ?? risk
}

/** 销售边界中文翻译 */
function boundaryLabel(boundary: string): string {
  const labels: Record<string, string> = {
    MAX_AMOUNT_EXPOSURE: '最大敞口限额',
    TENOR_LIMIT: '期限限制',
    RATE_FLOOR: '利率下限',
    INDUSTRY_RESTRICTION: '行业限制',
    GEOGRAPHIC_RESTRICTION: '地域限制',
    PRODUCT_COMBINATION_RESTRICTION: '产品组合限制',
    CUSTOMER_SEGMENT_RESTRICTION: '客群限制',
  }
  return labels[boundary] ?? boundary
}

/** 材料缺口中文翻译 */
function materialGapLabel(gap: string): string {
  const labels: Record<string, string> = {
    FINANCIAL_STATEMENT_REQUIRED: '需提供财务报表',
    COLLATERAL_APPRAISAL_REQUIRED: '需提供抵押评估报告',
    BUSINESS_LICENSE_REQUIRED: '需提供营业执照',
    TAX_RETURN_REQUIRED: '需提供纳税申报表',
    AUDIT_REPORT_REQUIRED: '需提供审计报告',
    BOARD_RESOLUTION_REQUIRED: '需提供董事会决议',
    GUARANTEE_LETTER_REQUIRED: '需提供担保函',
    ENVIRONMENTAL_ASSESSMENT_REQUIRED: '需提供环评报告',
    PROJECT_APPROVAL_REQUIRED: '需提供项目批文',
  }
  return labels[gap] ?? gap
}

/** 适用前提中文翻译 */
function conditionLabel(condition: string): string {
  const labels: Record<string, string> = {
    CREDIT_APPROVAL_REQUIRED: '需授信审批',
    RISK_COMMITTEE_APPROVAL: '需风控委员会审批',
    COLLATERAL_REQUIRED: '需提供抵押物',
    GUARANTEE_REQUIRED: '需提供担保',
    COMPLIANCE_REVIEW_REQUIRED: '需合规审查',
    SENIOR_MANAGEMENT_APPROVAL: '需高级管理层审批',
  }
  return labels[condition] ?? condition
}
</script>

<template>
  <section class="compare" data-testid="product-candidate-compare">
    <h2>候选产品比较（第二段·匹配与排序）</h2>

    <div v-if="ranked.length" class="cand-list">
      <article
        v-for="item in ranked"
        :key="`${item.productId}@${item.productVersion}`"
        class="cand-card"
        :data-testid="`candidate-${item.productId}`"
      >
        <header>
          <span class="product">{{ productTitle(item) }}</span>
          <span class="rank" data-testid="candidate-rank">第{{ item.rank }}名</span>
          <span class="score" data-testid="candidate-score">
            {{ scoreLabel(item) }} {{ scoreStars(item) }}
          </span>
        </header>

        <div v-if="item.dimensionMatches?.length" class="dims">
          <div v-for="(d, idx) in item.dimensionMatches" :key="idx" class="dim-row">
            <span class="dim-name">{{ dimensionLabel(d.dimension) }}</span>
            <span class="dim-result" :class="`dim-${d.result.toLowerCase()}`">
              {{ dimensionResultLabel(d.result) }}
            </span>
            <span v-if="d.rationale" class="dim-rationale">{{ d.rationale }}</span>
          </div>
        </div>

        <div v-if="item.recommendationReasons?.length" class="reasons">
          <div class="section-label">推荐理由</div>
          <ul>
            <li v-for="(r, idx) in item.recommendationReasons" :key="idx">
              {{ r.text }}
            </li>
          </ul>
        </div>

        <div v-if="item.conditions?.length" class="tags">
          <span class="tag-label">适用前提</span>
          <span v-for="(c, idx) in item.conditions" :key="idx" class="tag tag-condition">
            {{ conditionLabel(c) }}
          </span>
        </div>
        <div v-if="item.materialGaps?.length" class="tags">
          <span class="tag-label">材料缺口</span>
          <span v-for="(m, idx) in item.materialGaps" :key="idx" class="tag tag-gap">
            {{ materialGapLabel(m) }}
          </span>
        </div>
        <div v-if="item.riskNotes?.length" class="tags tags-risk">
          <span class="tag-label">风险提示</span>
          <span v-for="(r, idx) in item.riskNotes" :key="idx" class="tag tag-risk">
            {{ riskLabel(r) }}
          </span>
        </div>
        <div v-if="item.salesBoundaries?.length" class="tags tags-boundary">
          <span class="tag-label">销售边界</span>
          <span v-for="(b, idx) in item.salesBoundaries" :key="idx" class="tag tag-boundary">
            {{ boundaryLabel(b) }}
          </span>
        </div>
      </article>
    </div>
    <p v-else class="empty">暂无匹配与排序结果</p>
  </section>
</template>

<style scoped>
.compare h2 {
  font-size: 16px;
  margin: 0 0 12px;
}
.cand-list {
  display: grid;
  gap: 12px;
}
.cand-card {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 14px;
  background: var(--bg-surface);
}
.cand-card header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.product {
  font-weight: 600;
  font-size: 14px;
}
.rank {
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg-hover);
  padding: 1px 8px;
  border-radius: 10px;
}
.score {
  font-size: 13px;
  color: #087771;
  font-weight: 600;
}
.dims {
  display: grid;
  gap: 4px;
  margin-bottom: 10px;
  padding: 8px;
  background: rgba(0,0,0,0.02);
  border-radius: 6px;
}
.dim-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.dim-name {
  color: var(--text-tertiary);
  min-width: 96px;
}
.dim-result {
  font-weight: 700;
  font-size: 11px;
  padding: 0 6px;
  border-radius: 4px;
}
.dim-strong {
  color: #087771;
  background: rgba(8, 119, 113, 0.08);
}
.dim-moderate {
  color: #b45309;
  background: rgba(180, 83, 9, 0.08);
}
.dim-weak,
.dim-unknown {
  color: #b91c1c;
  background: rgba(185, 28, 28, 0.08);
}
.dim-rationale {
  color: var(--text-secondary);
  font-size: 11px;
}
.section-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}
.reasons {
  margin: 0 0 8px;
}
.reasons ul {
  margin: 0;
  padding-left: 18px;
  font-size: 12px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  margin-top: 6px;
  font-size: 12px;
}
.tag-label {
  color: var(--text-tertiary);
  font-size: 11px;
}
.tag {
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--bg-hover);
  color: var(--text-secondary);
  font-size: 11px;
}
.tag-condition {
  background: rgba(37, 99, 235, 0.08);
  color: #1e40af;
}
.tag-gap {
  background: rgba(217, 119, 6, 0.1);
  color: #92400e;
}
.tag-risk {
  background: rgba(217, 119, 6, 0.12);
  color: #92400e;
}
.tag-boundary {
  background: rgba(220, 38, 38, 0.1);
  color: #b91c1c;
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
