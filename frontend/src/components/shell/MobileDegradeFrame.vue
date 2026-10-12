<script setup lang="ts">
import ObjectHeader from './ObjectHeader.vue'

defineProps<{
  pageId: string
  title: string
  objectType: string
  objectStatus: string
  testId: string
  hint: string
}>()
</script>

<template>
  <div class="mobile-degrade" :data-testid="testId" :data-page-id="pageId">
    <ObjectHeader
      :page-id="pageId"
      :object-type="objectType"
      :object-status="objectStatus"
      :title="title"
    />
    <div class="toolbar">
      <slot name="toolbar" />
    </div>
    <p class="hint">{{ hint }}</p>
    <slot />
  </div>
</template>

<style scoped>
.mobile-degrade {
  max-width: 430px;
  margin: 0 auto;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 16px;
}
.hint {
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
