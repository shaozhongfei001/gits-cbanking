<template>
  <form class="commitment-form" @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>承诺类型</label>
      <select v-model="form.commitmentType" required>
        <option value="">请选择</option>
        <option v-for="(label, key) in COMMITMENT_TYPE_LABELS" :key="key" :value="key">
          {{ label }}
        </option>
      </select>
    </div>
    <div class="form-group">
      <label>承诺内容</label>
      <textarea v-model="form.content" rows="3" required placeholder="输入承诺内容"></textarea>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>负责人</label>
        <input v-model="form.owner" placeholder="输入负责人" />
      </div>
      <div class="form-group">
        <label>截止日期</label>
        <input v-model="form.dueDate" type="date" />
      </div>
    </div>
    <div class="form-group">
      <label>证据引用</label>
      <input v-model="form.evidenceRef" placeholder="输入证据引用ID" />
    </div>
    <div class="form-actions">
      <button type="submit" class="btn-primary" :disabled="submitting">
        {{ submitting ? '提交中...' : '创建承诺' }}
      </button>
      <button type="button" class="btn-secondary" @click="$emit('cancel')">取消</button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { COMMITMENT_TYPE_LABELS } from '../api/v11'
import type { CommitmentType } from '../api/v11'

const emit = defineEmits<{
  submit: [data: { commitmentType: CommitmentType; content: string; owner?: string; dueDate?: string; evidenceRef?: string }]
  cancel: []
}>()

const submitting = ref(false)
const form = reactive({
  commitmentType: '' as CommitmentType | '',
  content: '',
  owner: '',
  dueDate: '',
  evidenceRef: ''
})

async function handleSubmit() {
  if (!form.commitmentType || !form.content) return
  submitting.value = true
  try {
    emit('submit', {
      commitmentType: form.commitmentType as CommitmentType,
      content: form.content,
      owner: form.owner || undefined,
      dueDate: form.dueDate || undefined,
      evidenceRef: form.evidenceRef || undefined
    })
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.commitment-form {
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
