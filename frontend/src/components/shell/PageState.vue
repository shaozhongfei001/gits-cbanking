<script setup lang="ts">
import { NButton, NEmpty, NResult, NSpin } from 'naive-ui'
import type { ResourceStatus } from '../../composables/useResourceStatus'

defineProps<{
  status: ResourceStatus
  error?: string
  idleDescription?: string
}>()

const emit = defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="page-state" :data-testid="`page-state-${status}`">
    <div v-if="status === 'idle'" class="idle-state" data-testid="idle-state">
      <n-empty :description="idleDescription || '尚未加载'" />
    </div>
    <div v-else-if="status === 'loading'" class="loading-state" data-testid="loading-state">
      <n-spin size="large" />
      <span>加载中…</span>
    </div>
    <div v-else-if="status === 'error'" class="error-state" data-testid="error-state">
      <n-result status="error" title="加载失败" :description="error || '请求失败'">
        <template #footer>
          <n-button data-testid="retry-action" @click="emit('retry')">重试</n-button>
        </template>
      </n-result>
    </div>
    <div v-else class="success-state" data-testid="success-state">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.loading-state,
.idle-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 0;
  color: var(--text-tertiary);
}
</style>
