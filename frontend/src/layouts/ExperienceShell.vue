<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppSidebar from '../components/shell/AppSidebar.vue'
import { navDomainForPath, navGroupLabelForDomain, navItemLabelForPath } from './navConfig'

const route = useRoute()
const router = useRouter()

// ── 面包屑 ──────────────────────────────
const breadcrumbGroup = computed(() => navGroupLabelForDomain(navDomainForPath(route.path)))
const breadcrumbItem = computed(() => navItemLabelForPath(route.path))
const breadcrumbPageTitle = computed(() => {
  // 尝试从路由 meta 获取页面标题
  return (route.meta?.title as string) || breadcrumbItem.value || ''
})

// V8.1: 对象详情页面包屑含对象名，如"客户 / 客户组合 / XX公司"
const breadcrumbObjectName = computed(() => {
  // 详情页从 route params 或 meta 提取对象名
  // 当前仅提供结构；对象名需从各页面 store/composable 获取
  return ''
})

// ── 移动端抽屉 ──────────────────────────
const mobileDrawerOpen = ref(false)
const mobileBreakpoint = 768
const hamburgerBtn = ref<HTMLElement | null>(null)
const sidebarRef = ref<InstanceType<typeof AppSidebar> | null>(null)

function toggleMobileDrawer() {
  mobileDrawerOpen.value = !mobileDrawerOpen.value
  // V8.1: 抽屉打开时焦点进入侧栏第一个可聚焦元素
  if (mobileDrawerOpen.value) {
    hamburgerBtn.value = document.activeElement as HTMLElement
    requestAnimationFrame(() => {
      const firstFocusable = document.querySelector('.app-sidebar [tabindex="0"], .app-sidebar a, .app-sidebar button') as HTMLElement
      firstFocusable?.focus()
    })
  }
}

function closeMobileDrawer() {
  mobileDrawerOpen.value = false
  // V8.1: 抽屉关闭时焦点返回触发按钮
  requestAnimationFrame(() => {
    hamburgerBtn.value?.focus()
  })
}

function handleEscKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && mobileDrawerOpen.value) {
    closeMobileDrawer()
  }
}

// ── 响应式检测 ───────────────────────────
const isMobile = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth < mobileBreakpoint
  if (!isMobile.value) mobileDrawerOpen.value = false
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  window.addEventListener('keydown', handleEscKey)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  window.removeEventListener('keydown', handleEscKey)
})

// 路由变化时关闭移动端抽屉
watch(() => route.path, () => {
  if (isMobile.value) closeMobileDrawer()
})

// ── 用户操作 ─────────────────────────────
function handleLogout() {
  router.push('/login')
}

// ── 侧边栏宽度 ──────────────────────────
const sidebarWidth = computed(() => isMobile.value ? '0px' : '220px')
</script>

<template>
  <div class="shell" :class="{ 'shell--mobile': isMobile }">
    <!-- ── 移动端遮罩 ──────────────────────── -->
    <Transition name="overlay-fade">
      <div
        v-if="isMobile && mobileDrawerOpen"
        class="mobile-overlay"
        aria-hidden="true"
        @click="closeMobileDrawer"
      />
    </Transition>

    <!-- ── 侧边栏 ──────────────────────────── -->
    <AppSidebar
      :class="{ 'app-sidebar--mobile-open': mobileDrawerOpen }"
    />

    <!-- ── 主内容区 ────────────────────────── -->
    <div class="shell-main" :style="{ marginLeft: sidebarWidth }">
      <!-- ── 顶栏 ──────────────────────────── -->
      <header class="shell-header">
        <div class="header-left">
          <!-- 移动端汉堡按钮 -->
          <button
            v-if="isMobile"
            class="header-hamburger"
            @click="toggleMobileDrawer"
            aria-label="打开导航菜单"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>

          <!-- 面包屑 -->
          <nav class="header-breadcrumb" aria-label="面包屑">
            <span class="breadcrumb-group">{{ breadcrumbGroup }}</span>
            <svg class="breadcrumb-sep" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <polyline points="9 6 15 12 9 18" />
            </svg>
            <span class="breadcrumb-item">{{ breadcrumbItem }}</span>
            <template v-if="breadcrumbObjectName">
              <svg class="breadcrumb-sep" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <polyline points="9 6 15 12 9 18" />
              </svg>
              <span class="breadcrumb-object">{{ breadcrumbObjectName }}</span>
            </template>
          </nav>
        </div>

        <div class="header-right">
          <!-- 通知 -->
          <button class="header-icon-btn" aria-label="通知" title="通知">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 01-3.46 0" />
            </svg>
          </button>

          <!-- 帮助 -->
          <button class="header-icon-btn" aria-label="帮助" title="帮助">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </button>

          <!-- 用户头像 -->
          <button class="header-user-btn" @click="handleLogout" aria-label="用户菜单" title="张明远 · 客户经理">
            <div class="header-avatar">张</div>
          </button>
        </div>
      </header>

      <!-- ── 页面内容 ──────────────────────── -->
      <main class="shell-content custom-scrollbar">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* ── Shell 容器 ─────────────────────────── */
.shell {
  display: flex;
  min-height: 100vh;
  background: var(--v8-canvas);
}

.shell--mobile {
  flex-direction: column;
}

/* ── 移动端遮罩 ─────────────────────────── */
.shell-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg-overlay);
  z-index: var(--z-overlay);
  transition: opacity var(--transition-slow);
}

.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity var(--transition-slow);
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* ── 主内容区 ───────────────────────────── */
.shell-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left var(--transition-normal);
}

/* ── 顶栏 ───────────────────────────────── */
.shell-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 62px;
  padding: 0 20px;
  background: var(--bg-header);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--v8-line);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

/* ── 汉堡按钮 ───────────────────────────── */
.header-hamburger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--v8-muted);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.header-hamburger:hover {
  background: var(--v8-nav-hover-bg);
  color: var(--v8-ink);
}

.header-hamburger:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

/* ── 面包屑 ─────────────────────────────── */
.header-breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  min-width: 0;
}

.breadcrumb-group {
  color: var(--v8-faint);
  font-weight: 400;
  white-space: nowrap;
}

.breadcrumb-sep {
  flex-shrink: 0;
  color: var(--v8-line-strong);
}

.breadcrumb-item {
  color: var(--v8-ink);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.breadcrumb-object {
  color: var(--v8-steel);
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

/* ── 顶栏图标按钮 ──────────────────────── */
.header-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--v8-faint);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.header-icon-btn:hover {
  background: var(--v8-nav-hover-bg);
  color: var(--v8-ink);
}

.header-icon-btn:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

/* ── 顶栏用户按钮 ──────────────────────── */
.header-user-btn {
  display: flex;
  align-items: center;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  transition: all var(--transition-fast);
}

.header-user-btn:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

.header-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--v8-dark);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-sans);
}

/* ── 页面内容 ───────────────────────────── */
.shell-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* ── 响应式 ─────────────────────────────── */
@media (max-width: 768px) {
  .shell-main {
    margin-left: 0 !important;
  }

  .shell-header {
    padding: 0 12px;
    height: 52px;
  }

  .shell-content {
    padding: 12px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .shell-content {
    padding: 16px;
  }
}
</style>
