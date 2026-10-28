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
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <rect x="2" y="2" width="24" height="24" rx="6" fill="rgba(255,255,255,0.12)" />
          <path d="M8 18L14 9L20 18" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          <line x1="10" y1="15.5" x2="18" y2="15.5" stroke="white" stroke-width="1.5" stroke-linecap="round" />
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
  width: 220px;
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
  width: 60px;
}

/* ── 品牌区 ─────────────────────────────── */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: var(--v8-dark);
  min-height: 62px;
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
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
  letter-spacing: 0.02em;
}

.brand-sub {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.06em;
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
  padding: 7px 8px 5px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--v8-sidebar-caption);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: var(--font-sans);
  transition: color var(--transition-fast);
  border-radius: var(--radius-sm);
}

.nav-group-header:hover {
  color: var(--v8-muted);
  background: var(--v8-nav-hover-bg);
}

.nav-group-header:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: -2px;
}

.nav-group--active .nav-group-header {
  color: var(--v8-dark);
}

.nav-group-label-collapsed {
  font-size: 11px;
  font-weight: 700;
  color: var(--v8-muted);
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
  gap: 9px;
  width: 100%;
  padding: 0 10px;
  min-height: 40px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--v8-nav-text);
  font-size: 13px;
  font-weight: 400;
  font-family: var(--font-sans);
  line-height: 1.4;
  border-radius: 9px;
  transition: all var(--transition-fast);
  position: relative;
  text-align: left;
}

.nav-item:hover {
  background: rgba(17, 45, 64, 0.06);
  color: var(--v8-ink);
}

.nav-item:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

.nav-item--active {
  background: var(--v8-dark);
  color: #FFFFFF;
  font-weight: 500;
  box-shadow: 0 6px 15px rgba(17, 45, 64, 0.13);
}

.nav-item--active:hover {
  background: var(--v8-dark-hover);
}

.nav-item--active:focus-visible {
  outline: 2px solid #FFFFFF;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px var(--v8-focus-on-light), 0 6px 15px rgba(17, 45, 64, 0.13);
}

/* 选中项图标继承白色 */

.nav-item-icon {
  flex-shrink: 0;
  opacity: 0.55;
  transition: opacity var(--transition-fast);
}

.nav-item:hover .nav-item-icon {
  opacity: 0.8;
}

.nav-item-icon--active {
  opacity: 1;
  color: #FFFFFF;
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
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid var(--v8-sidebar-border);
  background: rgba(17, 45, 64, 0.03);
  flex-shrink: 0;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--v8-dark);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
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
