<template>
  <form class="task-form" @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>任务类型</label>
      <select v-model="form.taskType" required>
        <option value="">请选择</option>
        <option v-for="(label, key) in TASK_TYPE_LABELS" :key="key" :value="key">
          {{ label }}
        </option>
      </select>
    </div>
    <div class="form-group">
      <label>任务标题</label>
      <input v-model="form.title" required placeholder="输入任务标题" />
    </div>
    <div class="form-group">
      <label>任务描述</label>
      <textarea v-model="form.description" rows="2" placeholder="输入任务描述"></textarea>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>指派给</label>
        <input v-model="form.assignedTo" placeholder="输入负责人" />
      </div>
      <div class="form-group">
        <label>截止日期</label>
        <input v-model="form.dueDate" type="date" />
      </div>
    </div>
    <div class="form-actions">
      <button type="submit" class="btn-primary" :disabled="submitting">
        {{ submitting ? '提交中...' : '创建任务' }}
      </button>
      <button type="button" class="btn-secondary" @click="$emit('cancel')">取消</button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { TASK_TYPE_LABELS } from '../api/v11'
import type { TaskType } from '../api/v11'

const emit = defineEmits<{
  submit: [data: { taskType: TaskType; title: string; description?: string; assignedTo?: string; dueDate?: string }]
  cancel: []
}>()

const submitting = ref(false)
const form = reactive({
  taskType: '' as TaskType | '',
  title: '',
  description: '',
  assignedTo: '',
  dueDate: ''
})

async function handleSubmit() {
  if (!form.taskType || !form.title) return
  submitting.value = true
  try {
    emit('submit', {
      taskType: form.taskType as TaskType,
      title: form.title,
      description: form.description || undefined,
      assignedTo: form.assignedTo || undefined,
      dueDate: form.dueDate || undefined
    })
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.task-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-group label {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}
.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #d0d6e0;
  border-radius: 4px;
  font-size: 14px;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #1a2438;
  outline: none;
}
.form-row {
  display: flex;
  gap: 12px;
}
.form-row .form-group { flex: 1; }
.form-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
.btn-primary {
  padding: 8px 16px;
  background: #1a2438;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary {
  padding: 8px 16px;
  background: #fff;
  color: #333;
  border: 1px solid #d0d6e0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
</style>
