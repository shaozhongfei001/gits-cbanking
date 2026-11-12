<template>
  <div class="commitment-list">
    <div class="list-header">
      <h3>{{ title }}</h3>
      <div class="filter-bar">
        <select v-model="statusFilter" class="filter-select">
          <option value="">全部状态</option>
          <option v-for="(label, key) in COMMITMENT_STATUS_LABELS" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
      </div>
    </div>
    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="filteredCommitments.length === 0" class="empty-state">暂无承诺数据</div>
    <div v-else class="commitment-items">
      <CommitmentCard
        v-for="c in filteredCommitments"
        :key="c.commitmentId"
        :commitment="c"
        @click="$emit('select', c)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Commitment, CommitmentStatus } from '../api/v11'
import { COMMITMENT_STATUS_LABELS } from '../api/v11'
import CommitmentCard from './CommitmentCard.vue'

const props = defineProps<{
  commitments: Commitment[]
  title?: string
  loading?: boolean
}>()

defineEmits<{
  select: [commitment: Commitment]
}>()

const statusFilter = ref('')

const filteredCommitments = computed(() => {
  if (!statusFilter.value) return props.commitments
  return props.commitments.filter(c => c.status === statusFilter.value)
})
</script>

<style scoped>
.commitment-list { }
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.list-header h3 {
  font-size: 16px;
  color: #1a2438;
  margin: 0;
}
.filter-bar { display: flex; gap: 8px; }
.filter-select {
  padding: 4px 8px;
  border: 1px solid #d0d6e0;
  border-radius: 4px;
  font-size: 13px;
}
.loading-state, .empty-state {
  text-align: center;
  padding: 24px;
  color: #7a8899;
}
.commitment-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
