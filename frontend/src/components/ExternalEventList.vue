<template>
  <div class="event-list">
    <div class="list-header">
      <h3>{{ title }}</h3>
      <div class="filter-bar">
        <select v-model="typeFilter" class="filter-select">
          <option value="">全部类型</option>
          <option v-for="(label, key) in EXTERNAL_EVENT_TYPE_LABELS" :key="key" :value="key">
            {{ label }}
          </option>
        </select>
      </div>
    </div>
    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="filteredEvents.length === 0" class="empty-state">暂无外部事件数据</div>
    <div v-else class="event-items">
      <ExternalEventCard
        v-for="e in filteredEvents"
        :key="e.eventId"
        :event="e"
        @click="$emit('select', e)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ExternalEvent, ExternalEventType } from '../api/v11'
import { EXTERNAL_EVENT_TYPE_LABELS } from '../api/v11'
import ExternalEventCard from './ExternalEventCard.vue'

const props = defineProps<{
  events: ExternalEvent[]
  title?: string
  loading?: boolean
}>()

defineEmits<{
  select: [event: ExternalEvent]
}>()

const typeFilter = ref('')

const filteredEvents = computed(() => {
  if (!typeFilter.value) return props.events
  return props.events.filter(e => e.sourceType === typeFilter.value)
})
</script>

<style scoped>
.event-list { }
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
.event-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
