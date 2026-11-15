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
    <!-- 页级大号标题已取消：只保留给屏幕阅读器与既有文本契约，不占任何视觉空间。 -->
    <h1 class="object-title-sr">{{ title }}</h1>
    <div class="object-copy">
      <p class="object-type">{{ objectType }}</p>
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
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--border-light);
}
/* 语义标题保留，视觉上完全移除；不影响 flex 行高。 */
.object-title-sr {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  border: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  clip-path: inset(50%);
  white-space: nowrap;
}
.object-copy {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
  min-width: 0;
}
.object-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
  margin-left: auto;
}
.object-type {
  margin: 0;
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}
.object-status {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
