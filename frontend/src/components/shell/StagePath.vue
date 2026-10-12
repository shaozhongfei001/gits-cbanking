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
  background: var(--border-light);
}
.sp-step.sp-done:not(:last-child)::after {
  background: var(--v8-teal);
}
.sp-dot {
  position: relative;
  z-index: 1;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid var(--border-light);
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sp-done .sp-dot {
  border-color: var(--v8-teal);
}
.sp-current .sp-dot {
  border-color: var(--brand-primary);
}
.sp-check {
  font-size: 14px;
  font-weight: 700;
  color: #146e6b;
  line-height: 1;
}
.sp-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-primary);
  line-height: 1;
}
.sp-future .sp-num {
  color: var(--v8-nav-text);
}
.sp-label {
  margin-top: 8px;
  font-size: 12px;
  color: var(--v8-nav-text);
  font-weight: 500;
  white-space: nowrap;
}
.sp-done .sp-label,
.sp-current .sp-label {
  color: var(--text-primary);
}
.sp-current .sp-label {
  font-weight: 600;
}
</style>
