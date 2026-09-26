<script setup lang="ts">
/**
 * 产品首屏（需求 02 §6-3 / PI-FR-024、025、028、031、032、035）。
 *
 * 硬性要求：
 * - 缺失字段显示「待核验」，不得用空白或推测文案冒充（PI-FR-038）；
 * - 操作区只保留：收藏 / 下载内部说明 / 生成客观产品讲解提纲；
 *   **不得**出现「立即推荐」「加入客户方案」「测算适配度」（PI-BR-003）；
 * - 固定边界语句必须常驻展示，不得折叠隐藏（PI-FR-049/095）。
 */
import { NTag } from 'naive-ui'
import type { ProductCenterDetail } from '../../api/productCenter'

defineProps<{ detail: ProductCenterDetail }>()

/** 操作能力交付批次（PC1 未实现 ⇒ 显式禁用并标注，避免"看起来能用"）。 */
const ACTION_PLANNED_LOOP = 'PC5'
</script>

<template>
  <section class="pc-hero" data-testid="pc-hero">
    <div class="pc-hero-head">
      <div class="pc-hero-id">
        <h1 class="pc-hero-name">{{ detail.productName }}</h1>
        <div class="pc-hero-meta">
          <span data-testid="pc-hero-product-id">{{ detail.productId }}</span>
          <span class="pc-dot">·</span>
          <span>{{ detail.productCode }}</span>
          <span class="pc-dot">·</span>
          <span>{{ detail.familyName }}</span>
        </div>
      </div>
      <div class="pc-hero-tags">
        <n-tag size="small" :bordered="true" type="warning" data-testid="pc-publish-status">
          {{ detail.publishStatus === 'DRAFT' ? '未发布受控版本' : detail.publishStatus }}
        </n-tag>
        <n-tag
          v-for="tag in detail.tags"
          :key="tag"
          size="small"
          :bordered="true"
        >
          {{ tag }}
        </n-tag>
      </div>
    </div>

    <dl class="pc-hero-fields">
      <div class="pc-field">
        <dt>产品目的</dt>
        <dd :class="{ 'is-missing': !detail.summary?.productPurpose }">
          {{ detail.summary?.productPurpose || '待核验' }}
        </dd>
      </div>
      <div class="pc-field">
        <dt>使用方式</dt>
        <dd :class="{ 'is-missing': !detail.summary?.usageMode }">
          {{ detail.summary?.usageMode || '待核验' }}
        </dd>
      </div>
      <div class="pc-field">
        <dt>计息口径</dt>
        <dd :class="{ 'is-missing': !detail.summary?.interestSummary }">
          {{ detail.summary?.interestSummary || '待核验' }}
        </dd>
      </div>
      <div class="pc-field">
        <dt>适用主体</dt>
        <dd :class="{ 'is-missing': !detail.summary?.eligibleEntitySummary }">
          {{ detail.summary?.eligibleEntitySummary || '待核验' }}
        </dd>
      </div>
    </dl>

    <div class="pc-actions" data-testid="pc-hero-actions">
      <button type="button" class="pc-action" disabled :title="`收藏能力由 ${ACTION_PLANNED_LOOP} 接入`">
        收藏<span class="pc-action-loop">{{ ACTION_PLANNED_LOOP }}</span>
      </button>
      <button type="button" class="pc-action" disabled :title="`下载能力由 ${ACTION_PLANNED_LOOP} 接入`">
        下载内部说明<span class="pc-action-loop">{{ ACTION_PLANNED_LOOP }}</span>
      </button>
      <button type="button" class="pc-action" disabled :title="`提纲生成由 ${ACTION_PLANNED_LOOP} 接入`">
        生成客观产品讲解提纲<span class="pc-action-loop">{{ ACTION_PLANNED_LOOP }}</span>
      </button>
    </div>

    <ul class="pc-boundaries" data-testid="pc-fixed-boundaries">
      <li v-for="statement in detail.fixedBoundaryStatements" :key="statement">{{ statement }}</li>
    </ul>
  </section>
</template>

<style scoped>
.pc-hero {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
}

.pc-hero-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.pc-hero-name {
  margin: 0;
  font-family: var(--font-display);
  font-size: 30px;
  font-weight: 700;
  color: var(--text-primary);
  border-bottom: 2px solid var(--brand-primary);
  padding-bottom: 4px;
  display: inline-block;
  line-height: 1.25;
}

.pc-hero-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.pc-dot {
  color: var(--border-strong);
}

.pc-hero-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}

.pc-hero-fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin: 0;
}

.pc-field {
  padding: 8px 10px;
  background: var(--bg-surface-soft);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
}

.pc-field dt {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.pc-field dd {
  margin: 4px 0 0;
  font-size: var(--text-sm);
  line-height: 1.55;
  color: var(--text-primary);
}

.pc-field dd.is-missing {
  color: var(--color-warning);
}

.pc-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pc-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  background: var(--bg-surface-soft);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  cursor: not-allowed;
}

.pc-action-loop {
  padding: 0 5px;
  font-size: var(--text-xs);
  color: var(--text-brand);
  background: var(--brand-primary-lighter);
  border-radius: var(--radius-xs);
}

.pc-boundaries {
  margin: 0;
  padding: 8px 12px;
  list-style: none;
  border-left: 3px solid var(--v8-amber);
  background: var(--color-warning-bg);
  border-radius: var(--radius-sm);
}

.pc-boundaries li {
  font-size: var(--text-sm);
  line-height: 1.6;
  color: var(--color-warning);
}
</style>
