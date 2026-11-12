<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { SHELL_NAV_GROUPS, type ShellNavGroup, type ShellNavItem, navDomainForPath } from '../../layouts/navConfig'

const route = useRoute()
const router = useRouter()

const activeDomain = computed(() => navDomainForPath(route.path))

const expandedGroups = ref<Set<string>>(new Set())

// 自动展开当前激活项所在的组
watch(activeDomain, (domain) => {
  for (const group of SHELL_NAV_GROUPS) {
    if (group.children.some(item => item.domain === domain)) {
      expandedGroups.value.add(group.key)
    }
  }
}, { immediate: true })

function toggleGroup(key: string) {
  const s = new Set(expandedGroups.value)
  if (s.has(key)) s.delete(key)
  else s.add(key)
  expandedGroups.value = s
}

function isGroupActive(group: ShellNavGroup): boolean {
  return group.children.some(item => item.domain === activeDomain.value)
}

function isItemActive(item: ShellNavItem): boolean {
  return item.domain === activeDomain.value
}

function navigateTo(item: ShellNavItem) {
  router.push(item.to)
}

const sidebarCollapsed = ref(false)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 用户信息（从 auth store 获取，此处用占位）
const userName = '张明远'
const userRole = '客户经理'
const userInitial = computed(() => userName.charAt(0))
</script>

<template>
  <aside
    class="app-sidebar"
    data-testid="shell-sidebar"
    :class="{ 'app-sidebar--collapsed': sidebarCollapsed }"
    role="navigation"
    aria-label="主导航"
  >
    <!-- ── 品牌区 ──────────────────────────── -->
    <div class="sidebar-brand" data-testid="shell-brand">
      <div class="brand-emblem">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <rect width="24" height="24" rx="6" fill="var(--v8-blue)" />
          <path d="M6.5 16L12 8L17.5 16" stroke="white" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
          <line x1="8.5" y1="13.5" x2="15.5" y2="13.5" stroke="white" stroke-width="1.4" stroke-linecap="round" />
        </svg>
      </div>
      <div v-if="!sidebarCollapsed" class="brand-text">
        <span class="brand-name">GITS Bank</span>
        <span class="brand-sub">对公经营书桌</span>
      </div>
    </div>

    <!-- ── 导航区 ──────────────────────────── -->
    <nav class="sidebar-nav custom-scrollbar">
      <div
        v-for="group in SHELL_NAV_GROUPS"
        :key="group.key"
        class="nav-group"
        :class="{ 'nav-group--active': isGroupActive(group) }"
      >
        <!-- 组标题 -->
        <button
          class="nav-group-header"
          :data-testid="`nav-group-${group.key}`"
          :class="{ 'nav-group-header--expanded': expandedGroups.has(group.key) }"
          @click="toggleGroup(group.key)"
          :aria-expanded="expandedGroups.has(group.key)"
          :title="sidebarCollapsed ? group.label : undefined"
        >
          <span v-if="!sidebarCollapsed" class="nav-group-label">{{ group.label }}</span>
          <span v-else class="nav-group-label-collapsed">{{ group.label.charAt(0) }}</span>
          <svg
            v-if="!sidebarCollapsed"
            class="nav-group-chevron"
            :class="{ 'nav-group-chevron--open': expandedGroups.has(group.key) }"
            width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>

        <!-- 子项列表 -->
        <Transition name="nav-expand">
          <div v-if="expandedGroups.has(group.key) && !sidebarCollapsed" class="nav-group-items">
            <button
              v-for="item in group.children"
              :key="item.key"
              class="nav-item"
              :data-testid="`nav-item-${item.key}`"
              :class="{
                'nav-item--active': isItemActive(item),
                'nav-item--focus-visible': false,
              }"
              @click="navigateTo(item)"
              :title="item.label"
              :aria-current="isItemActive(item) ? 'page' : undefined"
            >
              <svg
                class="nav-item-icon"
                :class="{ 'nav-item-icon--active': isItemActive(item) }"
                width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
              >
                <path :d="item.icon" />
              </svg>
              <span class="nav-item-label">{{ item.label }}</span>
            </button>
          </div>
        </Transition>
      </div>
    </nav>

    <!-- ── 收起/展开按钮 ──────────────────── -->
    <button
      class="sidebar-collapse-btn"
      @click="toggleSidebar"
      :title="sidebarCollapsed ? '展开导航' : '收起导航'"
      :aria-label="sidebarCollapsed ? '展开导航' : '收起导航'"
    >
      <svg
        width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        :style="{ transform: sidebarCollapsed ? 'rotate(180deg)' : 'none', transition: 'transform 200ms ease' }"
      >
        <polyline points="11 17 6 12 11 7" />
        <polyline points="18 17 13 12 18 7" />
      </svg>
    </button>

    <!-- ── 用户区 ──────────────────────────── -->
    <div class="sidebar-user" v-if="!sidebarCollapsed">
      <div class="user-avatar">{{ userInitial }}</div>
      <div class="user-info">
        <span class="user-name">{{ userName }}</span>
        <span class="user-role">{{ userRole }}</span>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* ── 侧边栏容器 ─────────────────────────── */
.app-sidebar {
  display: flex;
  flex-direction: column;
  width: var(--sidebar-w);
  height: 100vh;
  background: var(--v8-sidebar-bg);
  border-right: 1px solid var(--v8-sidebar-border);
  position: fixed;
  left: 0;
  top: 0;
  z-index: var(--z-sticky);
  transition: width var(--transition-normal);
  overflow: hidden;
}

.app-sidebar--collapsed {
  width: var(--sidebar-w-collapsed);
}

/* ── 品牌区：白底 + 蓝色方形标记（模板 .appbar .brandmark） ── */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 0 14px;
  background: transparent;
  min-height: var(--topbar-h);
  border-bottom: 1px solid var(--v8-line);
  flex-shrink: 0;
}

.brand-emblem {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-family: var(--font-sans);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--v8-ink);
  line-height: 1.25;
  letter-spacing: 0;
}

.brand-sub {
  font-size: 10.5px;
  color: var(--v8-faint);
  letter-spacing: 0.04em;
  margin-top: 1px;
}

/* ── 导航区 ─────────────────────────────── */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 8px 8px;
}

/* ── 导航组 ─────────────────────────────── */
.nav-group {
  margin-bottom: 2px;
}

.nav-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 13px 9px 5px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--ink-500);
  font-size: 13.5px;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: uppercase;
  font-family: var(--font-sans);
  transition: color var(--transition-fast);
  border-radius: var(--radius-xs);
}

.nav-group-header:hover {
  color: var(--ink-600);
  background: transparent;
}

.nav-group-header:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: -2px;
}

.nav-group--active .nav-group-header {
  color: var(--ink-600);
}

.nav-group-label-collapsed {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-500);
}

.nav-group-chevron {
  flex-shrink: 0;
  transition: transform var(--transition-normal);
  opacity: 0.5;
}

.nav-group-chevron--open {
  transform: rotate(180deg);
  opacity: 0.8;
}

/* ── 子项列表 ───────────────────────────── */
.nav-group-items {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding-bottom: 4px;
}

/* ── 导航项 ─────────────────────────────── */
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0 9px;
  min-height: 34px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--v8-nav-text);
  font-size: 12.5px;
  font-weight: 400;
  font-family: var(--font-sans);
  line-height: 1.4;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  position: relative;
  text-align: left;
}

.nav-item:hover {
  background: var(--v8-nav-hover-bg);
  color: var(--ink-900);
}

.nav-item:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

/* 选中态：浅蓝底 + 深蓝字 + 左侧 3px 竖条（模板 .rail-item.on） */
.nav-item--active {
  background: var(--brand-50);
  color: var(--brand-700);
  font-weight: 600;
  box-shadow: none;
}

.nav-item--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  bottom: 6px;
  width: 3px;
  border-radius: 0 var(--radius-xs) var(--radius-xs) 0;
  background: var(--brand-600);
}

.nav-item--active:hover {
  background: var(--brand-50);
}

.nav-item--active:focus-visible {
  outline: 2px solid var(--brand-600);
  outline-offset: 2px;
  box-shadow: none;
}

.nav-item-icon {
  flex-shrink: 0;
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}

.nav-item:hover .nav-item-icon {
  opacity: 1;
}

.nav-item-icon--active {
  opacity: 1;
  color: var(--brand-600);
}

.nav-item-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── 收起/展开按钮 ──────────────────────── */
.sidebar-collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--v8-faint);
  border-top: 1px solid var(--v8-sidebar-border);
  transition: color var(--transition-fast), background var(--transition-fast);
}

.sidebar-collapse-btn:hover {
  color: var(--v8-muted);
  background: var(--v8-nav-hover-bg);
}

.sidebar-collapse-btn:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: -2px;
}

/* ── 用户区 ─────────────────────────────── */
.sidebar-user {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 14px;
  border-top: 1px solid var(--v8-sidebar-border);
  background: var(--ink-50);
  flex-shrink: 0;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--brand-600);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-sans);
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--v8-ink);
  line-height: 1.3;
}

.user-role {
  font-size: 11px;
  color: var(--v8-sidebar-caption);
}

/* ── 展开动画 ───────────────────────────── */
.nav-expand-enter-active,
.nav-expand-leave-active {
  transition: all var(--transition-normal);
  overflow: hidden;
}

.nav-expand-enter-from,
.nav-expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.nav-expand-enter-to,
.nav-expand-leave-from {
  opacity: 1;
  max-height: 300px;
}

/* ── 移动端抽屉模式 ─────────────────────── */
@media (max-width: 768px) {
  .app-sidebar {
    transform: translateX(-100%);
    box-shadow: var(--shadow-lg);
    width: 272px;
    transition: transform var(--transition-slow);
  }

  .app-sidebar--mobile-open {
    transform: translateX(0);
  }
}
</style>
