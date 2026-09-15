<script setup lang="ts">
import {
  PORTFOLIO_CATEGORY_LABELS,
  type PortfolioConflict,
  type PortfolioDependency,
  type PortfolioMember,
  type ProductRecommendationStageResult,
} from '../../api/productRecommendation'

defineProps<{
  stages: ProductRecommendationStageResult | null
}>()

function memberLabel(member: PortfolioMember): string {
  const role = member.role === 'PRIMARY' ? '核心' : '配套'
  return `${member.productId}@${member.productVersion}（${role}）`
}

function dependencyLabel(dep: PortfolioDependency): string {
  const typeLabels: Record<PortfolioDependency['type'], string> = {
    PREREQUISITE: '前置',
    SEQUENCE: '顺序',
    COMPLEMENTARY: '互补',
  }
  return `${dep.from} → ${dep.to}（${typeLabels[dep.type]}）`
}

function conflictLabel(conflict: PortfolioConflict): string {
  const kindLabels: Record<PortfolioConflict['kind'], string> = {
    MUTUAL_EXCLUSION: '互斥',
    DUPLICATE: '重复',
    SALES_BOUNDARY: '销售边界',
  }
  return `${conflict.productA} × ${conflict.productB}（${kindLabels[conflict.kind]}）`
}
</script>

<template>
  <section class="portfolio" data-testid="product-portfolio-panel">
    <h2>产品组合候选（第二段·组合校验）</h2>

    <div v-if="stages?.portfolioCandidates?.length" class="port-list">
      <article
        v-for="p in stages.portfolioCandidates"
        :key="p.portfolioId"
        class="port-card"
        :data-testid="`portfolio-${p.portfolioId}`"
      >
        <header>
          <span class="port-id">{{ p.portfolioId }}</span>
          <span v-if="p.recommendationCategory" class="badge">
            {{ PORTFOLIO_CATEGORY_LABELS[p.recommendationCategory] }}
          </span>
        </header>

        <dl class="port-facts">
          <div>
            <dt>核心产品</dt>
            <dd>{{ memberLabel(p.primaryProduct) }}</dd>
          </div>
          <div v-if="p.supportingProducts?.length">
            <dt>配套产品</dt>
            <dd>
              <ul class="plain">
                <li v-for="(m, idx) in p.supportingProducts" :key="idx">{{ memberLabel(m) }}</li>
              </ul>
            </dd>
          </div>
          <div v-if="p.dependencies?.length">
            <dt>依赖与顺序</dt>
            <dd>
              <ul class="plain">
                <li v-for="(d, idx) in p.dependencies" :key="idx">{{ dependencyLabel(d) }}</li>
              </ul>
            </dd>
          </div>
          <div v-if="p.conflicts?.length">
            <dt>冲突校验</dt>
            <dd>
              <ul class="plain plain-conflict">
                <li v-for="(c, idx) in p.conflicts" :key="idx">{{ conflictLabel(c) }}</li>
              </ul>
            </dd>
          </div>
        </dl>

        <p v-if="p.rationale" class="rationale">{{ p.rationale }}</p>
      </article>
    </div>
    <p v-else class="empty">暂无组合候选</p>
  </section>
</template>

<style scoped>
.portfolio h2 {
  font-size: 16px;
  margin: 0 0 12px;
}
.port-list {
  display: grid;
  gap: 10px;
}
.port-card {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}
.port-card header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.port-id {
  font-weight: 600;
  font-size: 13px;
  font-family: monospace;
}
.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 10px;
  color: #087771;
  background: rgba(18, 167, 160, 0.12);
}
.port-facts {
  display: grid;
  gap: 8px;
  margin: 0;
}
.port-facts div {
  font-size: 12px;
}
dt {
  color: var(--text-tertiary);
}
dd {
  margin: 2px 0 0;
}
.plain {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 2px;
}
.plain-conflict {
  color: #b91c1c;
}
.rationale {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
