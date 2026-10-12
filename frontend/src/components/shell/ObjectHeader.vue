<script setup lang="ts">
import { NButton } from 'naive-ui'
import { useRouter } from 'vue-router'
import { usePageReferenceStore } from '../../stores/pageReference'

const props = defineProps<{
  objectType: string
  objectStatus: string
  title: string
  pageId: string
}>()

const router = useRouter()
const pageRefs = usePageReferenceStore()

function goBack() {
  const restored = pageRefs.restore(props.pageId, props.objectType)
  if (window.history.length > 1) {
    router.back()
    return
  }
  if (restored.workspaceTabId) {
    router.push('/workbench')
  }
}
</script>

<template>
  <header class="object-header" data-testid="object-header">
    <div class="object-copy">
      <p class="object-type">{{ objectType }}</p>
      <h1>{{ title }}</h1>
      <p class="object-status" data-testid="object-status">当前状态：{{ objectStatus }}</p>
    </div>
    <div class="object-actions">
      <slot name="actions">
        <n-button quaternary size="small" data-testid="page-reference-back" @click="goBack">
          返回并恢复位置
        </n-button>
      </slot>
    </div>
  </header>
</template>

<style scoped>
.object-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}
.object-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.object-type {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 600;
}
h1 {
  margin: 4px 0;
  font-size: 30px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  line-height: 1.25;
}
.object-status {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
