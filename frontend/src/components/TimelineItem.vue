<template>
  <div class="timeline-item" :class="{ 'timeline-expanded': expanded }">
    <div class="timeline-marker">
      <div class="timeline-dot" :style="{ background: dotColor }" />
      <div class="timeline-line" />
    </div>
    <div class="timeline-content">
      <div class="timeline-header" @click="expanded = !expanded">
        <div class="timeline-title-row">
          <span class="timeline-title">{{ title }}</span>
          <span class="timeline-time">{{ formattedTime }}</span>
        </div>
        <span v-if="subtitle" class="timeline-subtitle">{{ subtitle }}</span>
      </div>
      <div v-if="expanded" class="timeline-detail">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  title: string
  subtitle?: string
  time?: string
  color?: string
}>()

const expanded = ref(false)

const dotColor = computed(() => props.color || '#1976D2')

const formattedTime = computed(() => {
  if (!props.time) return ''
  try {
    return new Date(props.time).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return props.time
  }
})
</script>

<style scoped>
.timeline-item {
  display: flex;
  gap: 16px;
  position: relative;
}
.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}
.timeline-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
  background: #fff;
  border: 2.5px solid #1976D2;
  box-sizing: border-box;
}
.timeline-line {
  width: 2px;
  flex: 1;
  background: #D8E2EC;
  min-height: 20px;
}
.timeline-content {
  flex: 1;
  padding-bottom: 20px;
  min-width: 0;
}
.timeline-header {
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}
.timeline-header:hover {
  background: #F3F6F9;
}
.timeline-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.timeline-title {
  font-weight: 600;
  font-size: 14px;
  color: #1B2632;
}
.timeline-time {
  font-size: 12px;
  color: #596779;
}
.timeline-subtitle {
  font-size: 13px;
  color: #596779;
  margin-top: 2px;
  display: block;
}
.timeline-detail {
  margin-top: 8px;
  padding: 12px;
  background: #F3F6F9;
  border-radius: 6px;
  border-left: 3px solid #12A7A0;
  font-size: 13px;
  color: #1B2632;
  line-height: 1.6;
}
</style>
