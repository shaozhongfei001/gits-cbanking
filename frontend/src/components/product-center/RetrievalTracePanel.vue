<script setup lang="ts">
/**
 * 请求跟踪控制带：展示产品详情加载的请求链路和 LightRAG 检索过程。
 *
 * 位置：产品中心右侧栏下方。
 * 功能：
 * - 展示请求链路步骤（分类法 → 产品卡 → 章节投影 → LightRAG 检索）
 * - 展示 LightRAG 检索详情（查询、模式、实体数、关系数、引用数、耗时）
 * - 状态指示：OK / UNAVAILABLE / ERROR
 */
import { computed, ref } from 'vue'
import { NCollapse, NCollapseItem, NTag, NTooltip, NIcon } from 'naive-ui'
import type { RetrievalTrace, TraceStep, LightRagTrace } from '../../api/productCenter'

const props = defineProps<{
  trace: RetrievalTrace | null
}>()

const expanded = ref(true)

const stepStatusType = computed(() => {
  const map: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    OK: 'success',
    UNAVAILABLE: 'warning',
    ERROR: 'error',
  }
  return (status: string) => map[status] ?? 'default'
})

const stepStatusLabel = computed(() => {
  const map: Record<string, string> = {
    OK: 'OK',
    UNAVAILABLE: '不可用',
    ERROR: '异常',
  }
  return (status: string) => map[status] ?? status
})

function formatMs(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

const lightragSummary = computed(() => {
  if (!props.trace?.lightrag) return null
  const lr = props.trace.lightrag
  return `${lr.entityCount} 实体 · ${lr.relationCount} 关系 · ${lr.citationCount} 引用`
})
</script>

<template>
  <div v-if="trace" class="rt-panel" data-testid="retrieval-trace-panel">
    <div class="rt-header" @click="expanded = !expanded">
      <span class="rt-title">请求跟踪</span>
      <span class="rt-total">{{ formatMs(trace.totalMs) }}</span>
      <span class="rt-toggle">{{ expanded ? '▾' : '▸' }}</span>
    </div>

    <div v-if="expanded" class="rt-body">
      <!-- 请求链路步骤 -->
      <div class="rt-steps">
        <div
          v-for="(step, idx) in trace.steps"
          :key="idx"
          class="rt-step"
          data-testid="trace-step"
        >
          <div class="rt-step-left">
            <div class="rt-step-dot" :class="`rt-dot-${stepStatusType(step.status)}`" />
            <div v-if="idx < trace.steps.length - 1" class="rt-step-line" />
          </div>
          <div class="rt-step-content">
            <div class="rt-step-row">
              <span class="rt-step-name">{{ step.name }}</span>
              <NTag
                :type="stepStatusType(step.status)"
                size="tiny"
                :bordered="false"
                round
              >
                {{ stepStatusLabel(step.status) }}
              </NTag>
            </div>
            <div class="rt-step-desc">{{ step.description }}</div>
            <div class="rt-step-ms">{{ formatMs(step.durationMs) }}</div>
          </div>
        </div>
      </div>

      <!-- LightRAG 检索详情 -->
      <div v-if="trace.lightrag" class="rt-lightrag" data-testid="lightrag-detail">
        <div class="rt-lr-header">
          <span class="rt-lr-title">LightRAG 检索</span>
          <span class="rt-lr-ms">{{ formatMs(trace.lightrag.retrievalMs) }}</span>
        </div>
        <div class="rt-lr-body">
          <div class="rt-lr-row">
            <span class="rt-lr-label">查询</span>
            <span class="rt-lr-value rt-lr-query">{{ trace.lightrag.query }}</span>
          </div>
          <div class="rt-lr-row">
            <span class="rt-lr-label">模式</span>
            <span class="rt-lr-value">{{ trace.lightrag.mode }}</span>
          </div>
          <div class="rt-lr-row">
            <span class="rt-lr-label">召回</span>
            <span class="rt-lr-value">{{ lightragSummary }}</span>
          </div>
          <div v-if="trace.lightrag.evidenceClass" class="rt-lr-row">
            <span class="rt-lr-label">证据类</span>
            <span class="rt-lr-value">{{ trace.lightrag.evidenceClass }}</span>
          </div>
          <div v-if="trace.lightrag.simulationOnly !== null" class="rt-lr-row">
            <span class="rt-lr-label">模拟</span>
            <NTag :type="trace.lightrag.simulationOnly ? 'warning' : 'success'" size="tiny" :bordered="false" round>
              {{ trace.lightrag.simulationOnly ? '仅模拟' : '生产' }}
            </NTag>
          </div>
          <div v-if="trace.lightrag.entityNames.length > 0" class="rt-lr-entities">
            <span class="rt-lr-label">实体</span>
            <div class="rt-lr-entity-list">
              <NTag
                v-for="name in trace.lightrag.entityNames"
                :key="name"
                size="tiny"
                :bordered="true"
                round
                class="rt-lr-entity-tag"
              >
                {{ name }}
              </NTag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rt-panel {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 10px;
  overflow: hidden;
  font-size: 12px;
}

.rt-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-page, #f3f6f9);
  cursor: pointer;
  user-select: none;
}

.rt-title {
  font-weight: 600;
  color: var(--gits-navy-800);
  flex: 1;
}

.rt-total {
  color: var(--gits-muted);
  font-size: 11px;
  font-variant-numeric: tabular-nums;
}

.rt-toggle {
  color: var(--gits-muted);
  font-size: 10px;
}

.rt-body {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Steps */
.rt-steps {
  display: flex;
  flex-direction: column;
}

.rt-step {
  display: flex;
  gap: 8px;
  min-height: 44px;
}

.rt-step-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 14px;
  flex-shrink: 0;
}

.rt-step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
}

.rt-dot-success { background: #18a058; }
.rt-dot-warning { background: #f0a020; }
.rt-dot-error { background: #d03050; }
.rt-dot-default { background: #c0c4cc; }

.rt-step-line {
  width: 1px;
  flex: 1;
  background: var(--border-light, #d8e2ec);
  margin: 2px 0;
}

.rt-step-content {
  flex: 1;
  padding-bottom: 6px;
}

.rt-step-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rt-step-name {
  font-weight: 500;
  color: var(--gits-navy-800);
  font-size: 12px;
}

.rt-step-desc {
  color: var(--gits-muted);
  font-size: 11px;
  line-height: 1.5;
  margin-top: 1px;
}

.rt-step-ms {
  color: var(--gits-muted);
  font-size: 10px;
  font-variant-numeric: tabular-nums;
  margin-top: 1px;
}

/* LightRAG detail */
.rt-lightrag {
  background: var(--bg-page, #f8f9fb);
  border-radius: 8px;
  padding: 8px 10px;
}

.rt-lr-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.rt-lr-title {
  font-weight: 600;
  color: var(--gits-navy-800);
  font-size: 11px;
  flex: 1;
}

.rt-lr-ms {
  color: var(--gits-muted);
  font-size: 10px;
  font-variant-numeric: tabular-nums;
}

.rt-lr-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rt-lr-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rt-lr-label {
  color: var(--gits-muted);
  font-size: 11px;
  width: 40px;
  flex-shrink: 0;
}

.rt-lr-value {
  color: var(--gits-navy-800);
  font-size: 11px;
  flex: 1;
}

.rt-lr-query {
  font-size: 10px;
  color: var(--gits-muted);
  word-break: break-all;
}

.rt-lr-entities {
  display: flex;
  gap: 6px;
  margin-top: 2px;
}

.rt-lr-entity-list {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  flex: 1;
}

.rt-lr-entity-tag {
  font-size: 10px;
}
</style>
