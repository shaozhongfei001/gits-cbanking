<script setup lang="ts">
import { computed } from 'vue'
import type { ProductFitResult, ProductRecommendationStageResult } from '../../api/productRecommendation'

const props = defineProps<{
  stages: ProductRecommendationStageResult | null
}>()

const ranked = computed(() => {
  const list = props.stages?.fitResults ?? []
  return [...list].sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
})

function scoreLabel(item: ProductFitResult): string {
  if (item.fitScore == null) {
    return '—'
  }
  return item.fitScore.toFixed(2)
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
          <span class="product">{{ item.productId }}@{{ item.productVersion }}</span>
          <span class="rank" data-testid="candidate-rank">#{{ item.rank ?? '—' }}</span>
          <span class="score" data-testid="candidate-score">fitScore {{ scoreLabel(item) }}</span>
        </header>

        <ul v-if="item.dimensionMatches?.length" class="dims">
          <li v-for="(d, idx) in item.dimensionMatches" :key="idx" class="dim">
            <span class="dim-name">{{ dimensionLabel(d.dimension) }}</span>
            <span class="dim-result" :class="`dim-${d.result.toLowerCase()}`">{{ d.result }}</span>
            <span v-if="d.rationale" class="dim-rationale">{{ d.rationale }}</span>
          </li>
        </ul>

        <ul v-if="item.recommendationReasons?.length" class="reasons">
          <li v-for="(r, idx) in item.recommendationReasons" :key="idx">
            {{ r.text }}
            <span class="ev" v-if="r.evidenceRefs?.length">（依据：{{ r.evidenceRefs.join('、') }}）</span>
          </li>
        </ul>

        <div v-if="item.conditions?.length" class="tags">
          <span class="tag-label">适用前提</span>
          <span v-for="(c, idx) in item.conditions" :key="idx" class="tag">{{ c }}</span>
        </div>
        <div v-if="item.materialGaps?.length" class="tags">
          <span class="tag-label">材料缺口</span>
          <span v-for="(m, idx) in item.materialGaps" :key="idx" class="tag">{{ m }}</span>
        </div>
        <div v-if="item.riskNotes?.length" class="tags tags-risk">
          <span class="tag-label">风险提示</span>
          <span v-for="(r, idx) in item.riskNotes" :key="idx" class="tag">{{ r }}</span>
        </div>
        <div v-if="item.salesBoundaries?.length" class="tags tags-boundary">
          <span class="tag-label">销售边界</span>
          <span v-for="(b, idx) in item.salesBoundaries" :key="idx" class="tag">{{ b }}</span>
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
  gap: 10px;
}
.cand-card {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}
.cand-card header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.product {
  font-weight: 600;
  font-size: 13px;
}
.rank {
  font-size: 12px;
  color: var(--text-secondary);
}
.score {
  font-size: 12px;
  color: #087771;
  font-weight: 600;
}
.dims {
  list-style: none;
  margin: 0 0 8px;
  padding: 0;
  display: grid;
  gap: 4px;
}
.dim {
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
}
.dim-strong {
  color: #087771;
}
.dim-moderate {
  color: #b45309;
}
.dim-weak,
.dim-unknown {
  color: #b91c1c;
}
.dim-rationale {
  color: var(--text-secondary);
}
.reasons {
  margin: 0 0 8px;
  padding-left: 18px;
  font-size: 12px;
}
.ev {
  color: var(--text-tertiary);
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
}
.tag {
  padding: 1px 8px;
  border-radius: 10px;
  background: var(--bg-hover);
  color: var(--text-secondary);
}
.tags-risk .tag {
  background: rgba(217, 119, 6, 0.12);
  color: #92400e;
}
.tags-boundary .tag {
  background: rgba(220, 38, 38, 0.1);
  color: #b91c1c;
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
