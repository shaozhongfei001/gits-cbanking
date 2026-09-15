<script setup lang="ts">
import { NButton, NTooltip } from 'naive-ui'

defineProps<{
  label: string
  disabled: boolean
  reason: string
  unlockPath: string
  buttonTestId?: string
}>()
</script>

<template>
  <div class="disabled-action" data-testid="disabled-action">
    <n-tooltip v-if="disabled" trigger="hover">
      <template #trigger>
        <n-button disabled type="primary" :data-testid="buttonTestId || 'gated-action'">{{ label }}</n-button>
      </template>
      {{ reason }}
    </n-tooltip>
    <n-button v-else type="primary" :data-testid="buttonTestId || 'gated-action'">{{ label }}</n-button>
    <p v-if="disabled" class="reason" data-testid="disabled-reason">
      原因：{{ reason }}。解除路径：{{ unlockPath }}
    </p>
  </div>
</template>

<style scoped>
.disabled-action {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}
.reason {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
  max-width: 420px;
}
</style>
