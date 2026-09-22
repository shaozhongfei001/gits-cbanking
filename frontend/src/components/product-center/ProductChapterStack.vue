<script setup lang="ts">
/**
 * 八章正文栈（需求 02 §6-4、§七）。
 *
 * PC1 诚实性规则：
 * - 有契约数据的章节按契约渲染（当前仅 OVERVIEW 的摘要字段可用）；
 * - 无契约数据的章节显示**具名未接入状态**（契约对象 + 计划批次），
 *   不得以示意内容、占位文案或"看起来像真实数据"的假值填充（需求 01 §3.2 / PI-BR-005）。
 */
import { NTag } from 'naive-ui'
import type { ProductCenterDetail } from '../../api/productCenter'
import {
  PRODUCT_SECTIONS,
  SECTION_CONTRACT_OBJECTS,
  SECTION_PLANNED_LOOP,
  type ProductSectionKey
} from './sections'

const props = defineProps<{ detail: ProductCenterDetail }>()

const LIST_PAYLOAD: Partial<Record<ProductSectionKey, keyof ProductCenterDetail>> = {
  TERMS: 'terms',
  FIT: 'boundaries',
  PROCESS: 'processSteps',
  MATERIALS: 'materialGroups',
  PRICING: 'pricingItems',
  FAQ: 'faqs'
}

/** 该章节是否已有契约数据（false ⇒ 显示未接入状态）。 */
function hasPayload(key: ProductSectionKey): boolean {
  if (key === 'OVERVIEW') {
    return props.detail.summary !== null
  }
  if (key === 'COMPARE') {
    return props.detail.comparison !== null
  }
  const field = LIST_PAYLOAD[key]
  if (!field) {
    return false
  }
  const value = props.detail[field]
  return Array.isArray(value) && value.length > 0
}

function value(source: string | null | undefined) {
  return source && source.trim().length > 0 ? source : null
}
</script>

<template>
  <div class="pc-chapters" data-testid="pc-chapters">
    <section
      v-for="(section, index) in PRODUCT_SECTIONS"
      :id="section.anchor"
      :key="section.key"
      class="pc-chapter"
      data-testid="pc-chapter"
      :data-section-key="section.key"
    >
      <header class="pc-chapter-head">
        <span class="pc-chapter-no">{{ String(index + 1).padStart(2, '0') }}</span>
        <h2 class="pc-chapter-title">{{ section.title }}</h2>
        <n-tag v-if="!hasPayload(section.key)" size="tiny" :bordered="true" type="default">
          待接入 {{ SECTION_PLANNED_LOOP[section.key] }}
        </n-tag>
      </header>

      <!-- OVERVIEW：摘要字段（有值渲染、缺失标注「待核验」） -->
      <template v-if="section.key === 'OVERVIEW'">
        <dl class="pc-overview">
          <div class="pc-ov-item">
            <dt>一句话定义</dt>
            <dd :class="{ 'is-missing': !value(detail.summary?.oneSentenceDefinition) }">
              {{ value(detail.summary?.oneSentenceDefinition) || '待核验' }}
            </dd>
          </div>
          <div class="pc-ov-item">
            <dt>审批与协议边界</dt>
            <dd :class="{ 'is-missing': !value(detail.summary?.boundaryStatement) }">
              {{ value(detail.summary?.boundaryStatement) || '待核验' }}
            </dd>
          </div>
          <div class="pc-ov-item">
            <dt>解决什么业务问题</dt>
            <dd :class="{ 'is-missing': !value(detail.summary?.solves) }">
              {{ value(detail.summary?.solves) || '待核验' }}
            </dd>
          </div>
          <div class="pc-ov-item">
            <dt>产品不是什么</dt>
            <dd :class="{ 'is-missing': !value(detail.summary?.isNot) }">
              {{ value(detail.summary?.isNot) || '待核验' }}
            </dd>
          </div>
          <div class="pc-ov-item">
            <dt>与相邻产品的客观差异</dt>
            <dd :class="{ 'is-missing': !value(detail.summary?.nearestDifference) }">
              {{ value(detail.summary?.nearestDifference) || '待核验' }}
            </dd>
          </div>
        </dl>
      </template>

      <!-- 其余章节：契约未接入 ⇒ 具名状态（不填假数据） -->
      <p v-else-if="!hasPayload(section.key)" class="pc-chapter-pending" data-testid="pc-chapter-pending">
        本章内容契约（{{ SECTION_CONTRACT_OBJECTS[section.key] }}）已就绪，数据由
        {{ SECTION_PLANNED_LOOP[section.key] }} 接入；当前不展示任何示意内容。
      </p>
    </section>
  </div>
</template>

<style scoped>
.pc-chapters {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pc-chapter {
  padding: 14px 16px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
  scroll-margin-top: 108px;
}

.pc-chapter-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.pc-chapter-no {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 20px;
  font-size: 11px;
  font-weight: 700;
  color: var(--gits-blue-600);
  background: var(--brand-primary-lighter, #eaf4fe);
  border-radius: 6px;
}

.pc-chapter-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--gits-navy-800);
}

.pc-chapter-pending {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--gits-muted);
}

.pc-overview {
  display: grid;
  gap: 8px;
  margin: 0;
}

.pc-ov-item {
  display: grid;
  grid-template-columns: 168px minmax(0, 1fr);
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border-light, #d8e2ec);
}

.pc-ov-item:last-child {
  border-bottom: 0;
}

.pc-ov-item dt {
  font-size: 12px;
  color: var(--gits-muted);
}

.pc-ov-item dd {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--gits-text);
}

.pc-ov-item dd.is-missing {
  color: var(--color-warning, #7a4b00);
}
</style>
