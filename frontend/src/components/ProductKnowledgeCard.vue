<template>
  <div class="pk-card">
    <div class="pk-header">
      <span class="version-badge">v{{ version.versionNumber }}</span>
      <span v-if="version.category" class="category-badge">{{ version.category }}</span>
    </div>
    <div class="pk-product">{{ version.productName }}</div>
    <div v-if="version.description" class="pk-content">{{ version.description }}</div>
    <div v-if="version.changeSummary" class="pk-change">
      变更: {{ version.changeSummary }}
    </div>
    <div class="pk-meta">
      <span v-if="version.riskLevel">风险: {{ version.riskLevel }}</span>
      <span v-if="formattedChangedAt">更新: {{ formattedChangedAt }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProductKnowledgeVersion } from '../api/v11'

const props = defineProps<{
  version: ProductKnowledgeVersion
}>()

const formattedChangedAt = computed(() => {
  const raw = props.version.changedAt
  if (!raw) return ''
  try { return new Date(raw).toLocaleDateString('zh-CN') }
  catch { return raw }
})
</script>

<style scoped>
.pk-card {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  background: #fff;
  border-left: 3px solid #722ed1;
  transition: box-shadow 0.2s;
}
.pk-card:hover { box-shadow: 0 2px 8px rgba(0, 51, 102, 0.1); }
.pk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.version-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f9f0ff;
  color: #722ed1;
  font-weight: 600;
}
.category-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #e6f7ff;
  color: #003366;
}
.pk-product {
  font-size: 13px;
  color: #003366;
  font-weight: 600;
  margin-bottom: 4px;
}
.pk-content {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 8px;
}
.pk-change {
  font-size: 12px;
  color: #722ed1;
  background: #f9f0ff;
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
}
.pk-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}
</style>
