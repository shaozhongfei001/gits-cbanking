<script setup lang="ts">
import { NButton, NTag } from 'naive-ui'
import { useRouter } from 'vue-router'
import { useWorkspaceTabsStore } from '../../stores/workspaceTabs'

const store = useWorkspaceTabsStore()
const router = useRouter()

function activate(path: string) {
  router.push(path)
}

function onClose(id: string) {
  const tab = store.tabs.find(item => item.id === id)
  if (tab?.dirty && typeof window !== 'undefined') {
    const ok = window.confirm('当前工作区有未提交草稿，确认关闭？')
    if (!ok) {
      return
    }
  }
  const next = store.closeTab(id)
  if (next) {
    router.push(next.path)
  }
}
</script>

<template>
  <div class="workspace-tabs" data-testid="workspace-tabs">
    <button
      v-for="tab in store.tabs"
      :key="tab.id"
      type="button"
      class="tab"
      :class="{ active: store.activeId === tab.id }"
      :data-testid="`workspace-tab-${tab.id}`"
      @click="activate(tab.path)"
    >
      <span>{{ tab.title }}</span>
      <n-tag v-if="tab.dirty" size="small" type="warning">草稿</n-tag>
      <n-button
        size="tiny"
        quaternary
        :data-testid="`workspace-tab-close-${tab.id}`"
        @click.stop="onClose(tab.id)"
      >
        ×
      </n-button>
    </button>
  </div>
</template>

<style scoped>
.workspace-tabs {
  display: flex;
  gap: 4px;
  align-items: center;
  min-height: 36px;
  overflow-x: auto;
}
.tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border-light);
  background: var(--bg-surface);
  color: var(--text-secondary);
  border-radius: 6px 6px 0 0;
  padding: 6px 8px 6px 12px;
  cursor: pointer;
  font-size: 13px;
}
.tab.active {
  color: var(--brand-primary);
  border-bottom-color: transparent;
  background: var(--bg-page);
  font-weight: 600;
}
</style>
