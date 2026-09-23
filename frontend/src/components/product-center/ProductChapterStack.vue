<script setup lang="ts">
/**
 * 八章正文栈（需求 02 §6-4、§七）。
 *
 * 诚实性规则（PC-I1 · W-1 起）：
 * - 有契约数据的章节按契约渲染（OVERVIEW / 核心条款 / 适用边界 / 办理流程 / 申请材料 / 同类比较）；
 *   本组件只做「按契约字段呈现」，**业务内容一律取自产品中心合同数据**，不在此硬编码；
 * - 无契约数据的章节显示**具名未接入状态**（契约对象 + 计划批次），
 *   不得以示意内容、占位文案或"看起来像真实数据"的假值填充（需求 01 §3.2 / PI-BR-005）；
 * - 契约字段缺失 ⇒ 逐项显式「待核验」（缺失不得伪装成有值）。
 */
import { NTag } from 'naive-ui'
import type { PkcComparisonRow, ProductCenterDetail } from '../../api/productCenter'
import {
  PRODUCT_SECTIONS,
  SECTION_CONTRACT_OBJECTS,
  SECTION_PLANNED_LOOP,
  type ProductSectionKey
} from './sections'

const props = defineProps<{ detail: ProductCenterDetail }>()

const LIST_PAYLOAD: Partial<Record<ProductSectionKey, keyof ProductCenterDetail>> = {
  TERMS: 'terms',
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
  // FIT 章的契约数据 = PkcBoundary[] + PkcPrerequisite[] ⇒ **二者任一非空即为已接入**；
  // 只看 boundaries 会在「有前置条件、无典型场景」时错报「未接入」（反向的不诚实）。
  if (key === 'FIT') {
    return props.detail.boundaries.length > 0 || props.detail.prerequisites.length > 0
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

/** 比较表单元格取值：缺失/空白 ⇒ null（渲染为「待核验」，不填假值）。 */
function comparisonCell(row: PkcComparisonRow, dimensionId: string) {
  const raw = row.values ? row.values[dimensionId] : undefined
  if (raw === null || raw === undefined) {
    return null
  }
  const text = String(raw).trim()
  return text.length > 0 ? text : null
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
        <dl class="pc-overview" data-testid="pc-chapter-body">
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

      <!-- 无契约数据 ⇒ 具名未接入状态（不填假数据） -->
      <p v-else-if="!hasPayload(section.key)" class="pc-chapter-pending" data-testid="pc-chapter-pending">
        本章内容契约（{{ SECTION_CONTRACT_OBJECTS[section.key] }}）已就绪，数据由
        {{ SECTION_PLANNED_LOOP[section.key] }} 接入；当前不展示任何示意内容。
      </p>

      <!-- 有契约数据 ⇒ 按契约渲染（PC-I1 · W-1：此前缺此分支 ⇒ 5 章空壳） -->
      <div v-else class="pc-chapter-body" data-testid="pc-chapter-body">
        <!-- 02 核心条款（PkcTerm[]） -->
        <div v-if="section.key === 'TERMS'" class="pc-items">
          <article v-for="term in detail.terms" :key="term.termId" class="pc-item" data-testid="pc-term">
            <header class="pc-item-head">
              <span class="pc-item-key">{{ term.termKey }}</span>
              <n-tag size="tiny" :bordered="true">确定性 {{ term.certaintyType }}</n-tag>
              <n-tag v-if="term.conflictId" size="tiny" type="warning" :bordered="true">
                存在冲突 {{ term.conflictId }}
              </n-tag>
              <span class="pc-item-aux">依据 {{ term.evidenceRefs ? term.evidenceRefs.length : 0 }} 条</span>
            </header>
            <dl class="pc-fields">
              <div class="pc-field">
                <dt>业务定义</dt>
                <dd :class="{ 'is-missing': !value(term.businessDefinition) }">
                  {{ value(term.businessDefinition) || '待核验' }}
                </dd>
              </div>
              <div class="pc-field">
                <dt>对客 / RM 解释</dt>
                <dd :class="{ 'is-missing': !value(term.explanationForRm) }">
                  {{ value(term.explanationForRm) || '待核验' }}
                </dd>
              </div>
            </dl>
          </article>
        </div>

        <!-- 03 适用边界（PkcBoundary[] + PkcPrerequisite[]） -->
        <div v-else-if="section.key === 'FIT'" class="pc-items">
          <article v-for="b in detail.boundaries" :key="b.boundaryId" class="pc-item" data-testid="pc-boundary">
            <header class="pc-item-head">
              <span class="pc-item-key">{{ b.scenarioName }}</span>
              <n-tag size="tiny" :bordered="true">{{ b.boundaryType }}</n-tag>
            </header>
            <p class="pc-item-text" :class="{ 'is-missing': !value(b.scenarioDescription) }">
              {{ value(b.scenarioDescription) || '待核验' }}
            </p>
            <p v-if="value(b.alternativeDirection)" class="pc-item-aux">
              替代方向：{{ b.alternativeDirection }}
            </p>
          </article>
          <article
            v-for="p in detail.prerequisites"
            :key="p.prerequisiteId"
            class="pc-item"
            data-testid="pc-prerequisite"
          >
            <header class="pc-item-head">
              <span class="pc-item-key">前置条件</span>
              <n-tag size="tiny" :bordered="true">{{ p.prerequisiteType }}</n-tag>
              <n-tag v-if="p.conditional" size="tiny" :bordered="true">有条件</n-tag>
            </header>
            <p class="pc-item-text" :class="{ 'is-missing': !value(p.requirementText) }">
              {{ value(p.requirementText) || '待核验' }}
            </p>
          </article>
        </div>

        <!-- 04 办理流程（PkcProcessStep[]） -->
        <ol v-else-if="section.key === 'PROCESS'" class="pc-steps">
          <li v-for="step in detail.processSteps" :key="step.stepId" class="pc-item" data-testid="pc-step">
            <header class="pc-item-head">
              <span class="pc-item-key">{{ step.sequence }}. {{ step.stepName }}</span>
              <n-tag v-if="step.humanDecisionRequired" size="tiny" type="warning" :bordered="true">
                需人工决策
              </n-tag>
              <span v-if="value(step.slaReference)" class="pc-item-aux">时效：{{ step.slaReference }}</span>
            </header>
            <p class="pc-item-text" :class="{ 'is-missing': !value(step.summary) }">
              {{ value(step.summary) || '待核验' }}
            </p>
            <p class="pc-item-aux">
              参与方：{{ step.actors && step.actors.length ? step.actors.join('、') : '待核验' }} ·
              输入：{{ step.inputs && step.inputs.length ? step.inputs.join('、') : '待核验' }} ·
              产出：{{ step.outputs && step.outputs.length ? step.outputs.join('、') : '待核验' }}
            </p>
          </li>
        </ol>

        <!-- 05 申请材料（PkcMaterialGroup[]） -->
        <div v-else-if="section.key === 'MATERIALS'" class="pc-items">
          <article
            v-for="group in detail.materialGroups"
            :key="group.groupType"
            class="pc-item"
            data-testid="pc-material-group"
          >
            <header class="pc-item-head">
              <span class="pc-item-key">{{ group.groupType }}</span>
              <span class="pc-item-aux">{{ (group.items || []).length }} 项</span>
            </header>
            <ul class="pc-list">
              <li v-for="item in group.items" :key="item.materialId" data-testid="pc-material-item">
                <span class="pc-item-key">{{ item.materialName }}</span>
                <n-tag size="tiny" :bordered="true">{{ item.requirementLevel }}</n-tag>
                <span class="pc-item-text">{{ value(item.purpose) || '待核验' }}</span>
                <span v-if="value(item.conditionExpression)" class="pc-item-aux">
                  （适用条件：{{ item.conditionExpression }}）
                </span>
                <span v-if="value(item.validityRule)" class="pc-item-aux">
                  （有效期：{{ item.validityRule }}）
                </span>
              </li>
            </ul>
          </article>
        </div>

        <!-- 07 同类产品比较（PkcComparisonSet） -->
        <div v-else-if="section.key === 'COMPARE'" class="pc-compare" data-testid="pc-compare">
          <p class="pc-item-aux">
            比较基准日：{{ value(detail.comparison?.comparisonAsOf) || '待核验' }} ·
            复核状态：{{ value(detail.comparison?.reviewState) || '待核验' }}
          </p>
          <table class="pc-compare-table">
            <thead>
              <tr>
                <th>产品</th>
                <th v-for="dim in detail.comparison?.dimensions || []" :key="dim.dimensionId">
                  {{ dim.dimensionName }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in detail.comparison?.rows || []" :key="`${row.productId}-${idx}`">
                <td>{{ row.productId }}</td>
                <td v-for="dim in detail.comparison?.dimensions || []" :key="dim.dimensionId">
                  <span :class="{ 'is-missing': !comparisonCell(row, dim.dimensionId) }">
                    {{ comparisonCell(row, dim.dimensionId) || '待核验' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
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

/* ── PC-I1 · W-1：有数据章节的正文样式（数据来自合同，样式只负责呈现）── */

.pc-chapter-body {
  display: block;
}

.pc-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pc-item {
  padding: 8px 0;
  border-bottom: 1px dashed var(--border-light, #d8e2ec);
}

.pc-item:last-child {
  border-bottom: 0;
}

.pc-item-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 4px;
}

.pc-item-key {
  font-size: 13px;
  font-weight: 600;
  color: var(--gits-navy-800);
}

.pc-item-aux {
  font-size: 12px;
  color: var(--gits-muted);
}

.pc-item-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--gits-text);
}

.pc-item-text.is-missing,
.pc-field dd.is-missing,
.pc-compare-table .is-missing {
  color: var(--color-warning, #7a4b00);
}

.pc-fields {
  display: grid;
  gap: 4px;
  margin: 0;
}

.pc-field {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  gap: 10px;
}

.pc-field dt {
  font-size: 12px;
  color: var(--gits-muted);
}

.pc-field dd {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--gits-text);
}

.pc-list {
  margin: 0;
  padding-left: 16px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--gits-text);
}

.pc-list li {
  margin-bottom: 2px;
}

.pc-list .pc-item-key {
  margin-right: 6px;
}

.pc-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  padding-left: 18px;
}

.pc-compare-table {
  width: 100%;
  font-size: 12px;
  border-collapse: collapse;
}

.pc-compare-table th,
.pc-compare-table td {
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
  border-bottom: 1px solid var(--border-light, #d8e2ec);
}

.pc-compare-table th {
  font-weight: 600;
  color: var(--gits-muted);
}
</style>
