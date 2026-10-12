<script setup lang="ts">
/**
 * 顶部环境条（需求 02 §6-1 / PI-FR-001、002、003）。
 *
 * 硬性要求：
 * - DEMO / UAT / PROD 环境标识**持续可见**，不得被业务配置关闭（PI-BR-009）；
 * - 展示知识基准日；缺失时显示「基准日待维护」，不得用系统日期冒充（AT-002）；
 * - 全局搜索：PC1 仅支持「产品名 / 编号 / 能力词」筛选（走 /products?keyword）；
 *   条款、材料、流程与制度题名搜索为 PI-FR-005/006，由 PC2 的搜索端点接入。
 */
import { NTag } from 'naive-ui'

defineProps<{
  environment: string
  isDemo: boolean
  /** 知识基准日；null = 待维护 */
  knowledgeAsOf: string | null
  keyword: string
  identityNote: string
}>()

const emit = defineEmits<{
  (e: 'update:keyword', value: string): void
}>()

function onInput(event: Event) {
  emit('update:keyword', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <header class="pc-env" data-testid="pc-env-banner">
    <div class="pc-env-left">
      <span class="pc-brand">企业金融产品中心</span>
      <n-tag
        size="small"
        :type="isDemo ? 'warning' : 'success'"
        :bordered="true"
        data-testid="pc-env-tag"
      >
        {{ environment }}{{ isDemo ? ' · 演示数据' : '' }}
      </n-tag>
      <span class="pc-kas" data-testid="pc-knowledge-as-of">
        知识基准日：{{ knowledgeAsOf || '基准日待维护' }}
      </span>
    </div>

    <div class="pc-env-right">
      <label class="pc-search">
        <span class="pc-search-label">产品筛选</span>
        <input
          class="pc-search-input"
          type="search"
          placeholder="产品名称 / 编号 / 能力词"
          :value="keyword"
          data-testid="pc-search-input"
          @input="onInput"
        >
      </label>
      <span class="pc-identity" data-testid="pc-identity">{{ identityNote }}</span>
    </div>
  </header>
</template>

<style scoped>
.pc-env {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 20px;
  background: var(--bg-header, #fff);
  border-bottom: 1px solid var(--border-light, #d8e2ec);
}

.pc-env-left,
.pc-env-right {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.pc-brand {
  font-size: 15px;
  font-weight: 700;
  color: var(--gits-navy-800);
  white-space: nowrap;
}

.pc-kas {
  font-size: 12px;
  color: var(--gits-muted);
  white-space: nowrap;
}

.pc-search {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pc-search-label {
  font-size: 12px;
  color: var(--gits-muted);
}

.pc-search-input {
  width: 220px;
  height: 28px;
  padding: 0 8px;
  font-size: 12px;
  color: var(--gits-text);
  border: 1px solid var(--gits-line);
  border-radius: 6px;
  background: #fff;
}

.pc-identity {
  font-size: 12px;
  color: var(--gits-muted);
  white-space: nowrap;
}
</style>
