<template>
  <div class="pk-list">
    <div class="list-header">
      <h3>{{ title }}</h3>
    </div>
    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="versions.length === 0" class="empty-state">暂无产品知识数据</div>
    <div v-else class="pk-items">
      <ProductKnowledgeCard
        v-for="v in versions"
        :key="v.versionId"
        :version="v"
        @click="$emit('select', v)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProductKnowledgeVersion } from '../api/v11'
import ProductKnowledgeCard from './ProductKnowledgeCard.vue'

defineProps<{
  versions: ProductKnowledgeVersion[]
  title?: string
  loading?: boolean
}>()

defineEmits<{
  select: [version: ProductKnowledgeVersion]
}>()
</script>

<style scoped>
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.list-header h3 { font-size: 16px; color: #1a2438; margin: 0; }
.loading-state, .empty-state { text-align: center; padding: 24px; color: #7a8899; }
.pk-items { display: flex; flex-direction: column; gap: 8px; }
</style>
