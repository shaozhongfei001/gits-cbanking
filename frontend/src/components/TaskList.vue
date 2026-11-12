<template>
  <div class="task-list">
    <div class="list-header">
      <h3>{{ title }}</h3>
      <div class="filter-bar">
        <select v-model="statusFilter" class="filter-select">
          <option value="">全部状态</option>
          <option v-for="(label, key) in TASK_STATUS_LABELS" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
      </div>
    </div>
    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="filteredTasks.length === 0" class="empty-state">暂无任务数据</div>
    <div v-else class="task-items">
      <TaskCard
        v-for="t in filteredTasks"
        :key="t.taskId"
        :task="t"
        @click="$emit('select', t)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Task, TaskStatus } from '../api/v11'
import { TASK_STATUS_LABELS } from '../api/v11'
import TaskCard from './TaskCard.vue'

const props = defineProps<{
  tasks: Task[]
  title?: string
  loading?: boolean
}>()

defineEmits<{
  select: [task: Task]
}>()

const statusFilter = ref('')

const filteredTasks = computed(() => {
  if (!statusFilter.value) return props.tasks
  return props.tasks.filter(t => t.status === statusFilter.value)
})
</script>

<style scoped>
.task-list { }
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
.task-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
