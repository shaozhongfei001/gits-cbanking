<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NMenu, NLayout, NLayoutHeader, NLayoutContent, NButton, NIcon, NMessageProvider, NSwitch, NConfigProvider, darkTheme } from 'naive-ui'
import type { MenuOption } from 'naive-ui'

const router = useRouter()
const route = useRoute()

const isDark = ref(false)

function initTheme() {
  const saved = localStorage.getItem('gits-theme')
  if (saved === 'dark') {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
}

function toggleTheme(dark: boolean) {
  isDark.value = dark
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : '')
  localStorage.setItem('gits-theme', dark ? 'dark' : 'light')
}

onMounted(initTheme)

const menuOptions: MenuOption[] = [
  { label: '客户经营概览', key: 'Dashboard' },
  { label: '持续经营工作台', key: 'EngagementWorkspace' },
  { label: '知识地图', key: 'KnowledgeMapView' },
  { label: '承诺与任务', key: 'CommitmentDashboard' },
  { label: '外部事件监控', key: 'ExternalEventMonitor' }
]

const activeKey = ref('Dashboard')

function handleMenuUpdate(key: string) {
  activeKey.value = key
  router.push({ name: key })
}

watch(() => route.name, (name) => {
  if (name && typeof name === 'string') {
    activeKey.value = name === 'SupplyChainGraphReport' ? 'EngagementWorkspace' : name
  }
}, { immediate: true })
</script>

<template>
  <n-config-provider :theme="isDark ? darkTheme : undefined">
    <n-layout class="app-layout">
      <n-layout-header v-if="route.name !== 'SupplyChainGraphReport'" class="app-header" bordered>
        <div class="header-left">
          <div class="brand-mark">G</div>
          <div class="brand-text">
            <span class="brand-name" @click="router.push('/')">GITS</span>
            <span class="brand-sub">客户经营闭环</span>
          </div>
        </div>
        <n-menu
          mode="horizontal"
          :value="activeKey"
          :options="menuOptions"
          @update:value="handleMenuUpdate"
          class="header-menu"
        />
        <div class="header-right">
          <n-switch :value="isDark" size="small" @update:value="toggleTheme">
            <template #checked>暗色</template>
            <template #unchecked>亮色</template>
          </n-switch>
        </div>
      </n-layout-header>
      <n-layout-content class="app-content">
        <n-message-provider>
          <router-view />
        </n-message-provider>
      </n-layout-content>
    </n-layout>
  </n-config-provider>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--bg-page);
}

.app-header {
  display: flex;
  align-items: center;
  padding: 0 var(--space-6);
  height: 52px;
  background: var(--bg-header);
  border-bottom: 1px solid var(--border-light) !important;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-right: var(--space-6);
  flex-shrink: 0;
}

.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--brand-primary);
  color: var(--text-inverse);
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 0;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  cursor: pointer;
  letter-spacing: 1px;
}

.brand-sub {
  font-size: 10px;
  color: var(--text-tertiary);
  letter-spacing: 0.5px;
}

.header-menu {
  background: transparent;
  flex: 1;
}

::deep(.header-menu .n-menu-item) {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

::deep(.header-menu .n-menu-item--selected) {
  color: var(--brand-primary) !important;
  font-weight: 500;
}

::deep(.header-menu .n-menu-item:hover) {
  color: var(--brand-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
  margin-left: var(--space-4);
}

.app-content {
  padding: 0;
  min-height: calc(100vh - 52px);
}
</style>
