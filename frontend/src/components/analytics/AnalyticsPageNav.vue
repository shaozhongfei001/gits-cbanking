<script setup lang="ts">
/** 分析页左侧「页面内导航菜单」（Owner 口径 2026-09-22：点击二级菜单打开的
 *  分析页左侧应有导航面板，用于切换同组内的不同分析图表）。 */
export interface AnalyticsNavItem {
  id: string
  label: string
  children?: Array<{ id: string; label: string }>
}

const props = defineProps<{
  items: AnalyticsNavItem[]
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: string): void
}>()

function active(item: AnalyticsNavItem): boolean {
  return props.modelValue === item.id
    || (item.children ?? []).some((c) => c.id === props.modelValue)
}

function select(item: AnalyticsNavItem): void {
  // 有子项的父项（细分客户业务分析）默认落到第一个子项（存款业务）
  emit('update:modelValue', item.children?.length ? item.children[0].id : item.id)
}
</script>

<template>
  <nav class="page-nav" data-testid="analytics-page-nav" :aria-label="`分析图表切换`">
    <template v-for="item in items" :key="item.id">
      <a class="nav-item" :class="{ active: active(item) }" data-testid="analytics-nav-item"
         @click="select(item)">
        <span class="mark" aria-hidden="true">◧</span>{{ item.label }}
      </a>
      <a
        v-for="child in item.children ?? []"
        :key="child.id"
        class="nav-item sub"
        :class="{ active: modelValue === child.id }"
        data-testid="analytics-nav-subitem"
        @click="emit('update:modelValue', child.id)"
      >
        {{ child.label }}
      </a>
    </template>
  </nav>
</template>

<style scoped>
.page-nav {
  width: 196px;
  flex-shrink: 0;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 8px 0;
  align-self: flex-start;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 14px;
  font-size: 13px;
  color: var(--v8-nav-text);
  cursor: pointer;
  border-left: 3px solid transparent;
  user-select: none;
  transition: background 0.15s ease, color 0.15s ease;
}
.nav-item:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: -2px;
}
.nav-item:hover { background: #f0f6fc; color: var(--brand-primary) }
.nav-item.active {
  background: #e8f1fd;
  color: var(--brand-primary);
  font-weight: 700;
  border-left-color: var(--brand-primary);
}
.nav-item.sub {
  padding-left: 38px;
  height: 32px;
  font-size: 12.5px;
}
.mark { font-size: 12px; opacity: .7 }
</style>
