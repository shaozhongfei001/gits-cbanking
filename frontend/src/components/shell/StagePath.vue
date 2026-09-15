<script setup lang="ts">
export interface StagePathStage {
  key: string
  label: string
}

const props = defineProps<{
  stages: StagePathStage[]
  currentKey: string
  completedKeys?: string[]
}>()

function stateOf(key: string): 'done' | 'current' | 'future' {
  if (props.completedKeys?.includes(key)) return 'done'
  if (props.currentKey === key) return 'current'
  return 'future'
}
</script>

<template>
  <nav class="stage-path" data-testid="stage-path" aria-label="阶段路径">
    <div
      v-for="(s, i) in stages"
      :key="s.key"
      class="sp-step"
      :class="`sp-${stateOf(s.key)}`"
    >
      <span class="sp-dot">
        <span v-if="stateOf(s.key) === 'done'" class="sp-check">✓</span>
        <span v-else class="sp-num">{{ i + 1 }}</span>
      </span>
      <span class="sp-label">{{ s.label }}</span>
    </div>
  </nav>
</template>

<style scoped>
.stage-path {
  display: flex;
  margin-bottom: 20px;
}
.sp-step {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
/* 连接线：从当前圆圈中心延伸到下一个圆圈中心（完成段青绿，未完成段灰） */
.sp-step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 13px; /* 圆圈中心 = 28/2 - 1.5 */
  left: 50%;
  width: 100%;
  height: 3px;
  background: var(--gits-line, #d8e2ec);
}
.sp-step.sp-done:not(:last-child)::after {
  background: var(--gits-teal-500, #12a7a0);
}
.sp-dot {
  position: relative;
  z-index: 1;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid var(--gits-line, #d8e2ec);
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sp-done .sp-dot {
  border-color: var(--gits-teal-500, #12a7a0);
}
.sp-current .sp-dot {
  border-color: var(--gits-blue-600, #1976d2);
}
.sp-check {
  font-size: 14px;
  font-weight: 700;
  color: var(--gits-teal-700, #087771);
  line-height: 1;
}
.sp-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--gits-blue-600, #1976d2);
  line-height: 1;
}
.sp-future .sp-num {
  color: var(--text-tertiary, #7a8795);
}
.sp-label {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary, #7a8795);
  font-weight: 500;
  white-space: nowrap;
}
.sp-done .sp-label,
.sp-current .sp-label {
  color: var(--gits-text, #1b2632);
}
.sp-current .sp-label {
  font-weight: 600;
}
</style>
