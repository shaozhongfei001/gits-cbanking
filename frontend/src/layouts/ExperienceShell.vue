<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NLayout, NLayoutContent, NLayoutHeader, NLayoutSider } from 'naive-ui'
import AppSidebar from '../components/shell/AppSidebar.vue'
import WorkspaceTabs from '../components/shell/WorkspaceTabs.vue'
import { useWorkspaceTabsStore } from '../stores/workspaceTabs'

defineProps<{
  isDark: boolean
}>()

const emit = defineEmits<{ 'update:isDark': [value: boolean] }>()

const route = useRoute()
const router = useRouter()
const tabs = useWorkspaceTabsStore()
const search = ref('')

const pageTitle = computed(() => String(route.meta.title || 'GITS Bank'))
const objectType = computed(() => String(route.meta.objectType || '工作区'))

watch(
  () => route.fullPath,
  () => {
    if (route.meta.public) {
      return
    }
    tabs.openTab({
      id: String(route.name || route.path),
      title: pageTitle.value,
      path: route.path,
      routeName: String(route.name || ''),
      objectType: objectType.value,
      recordId: typeof route.params.id === 'string' ? route.params.id : undefined,
    })
  },
  { immediate: true },
)

function submitSearch() {
  const q = search.value.trim()
  router.push({ path: '/accounts', query: q ? { q } : {} })
}
</script>

<template>
  <n-layout class="experience-shell" data-testid="experience-shell" has-sider>
    <n-layout-sider
      :width="226"
      :collapsed-width="64"
      :show-trigger="false"
      :bordered="false"
      :native-scrollbar="true"
      content-style="padding: 0; background: #08233B;"
      class="shell-sider"
    >
      <AppSidebar />
    </n-layout-sider>
    <n-layout class="shell-main">
      <n-layout-header class="shell-header" bordered>
        <form class="shell-search" data-testid="shell-search" @submit.prevent="submitSearch">
          <span class="search-glyph" aria-hidden="true">⌕</span>
          <input
            v-model="search"
            type="search"
            placeholder="搜索客户、关系人、互动、建议书、知识或命令"
            aria-label="全局搜索"
          />
        </form>
        <button type="button" class="global-new" data-testid="global-new" disabled title="全局新建写未授权；解除路径：CC2 后独立合同 Loop">
          ＋ 全局新建
        </button>
        <span class="header-spacer" />
        <button type="button" class="header-icon" aria-label="帮助">？</button>
        <button type="button" class="header-icon" aria-label="通知">♢</button>
        <button
          type="button"
          class="theme-toggle"
          data-testid="theme-toggle"
          @click="emit('update:isDark', !isDark)"
        >
          {{ isDark ? '暗色' : '亮色' }}
        </button>
        <div class="header-user" data-testid="shell-header-user">
          <span class="header-avatar">开</span>
          <span class="header-user-copy">
            <span>开发会话</span>
            <span>总行公司金融部</span>
          </span>
        </div>
      </n-layout-header>
      <div class="shell-tabbar">
        <WorkspaceTabs />
      </div>
      <n-layout-content class="shell-content">
        <slot />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.experience-shell {
  min-height: 100vh;
  background: var(--gits-page);
}
.shell-sider {
  background: #08233b;
}
.shell-main {
  background: var(--gits-page);
}
.shell-header {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 56px;
  padding: 0 16px 0 20px;
  background: #fff;
  border-bottom: 1px solid var(--gits-line);
}
.shell-search {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 514px;
  height: 36px;
  padding: 0 14px;
  border: 1px solid var(--gits-line);
  border-radius: 18px;
  background: #f7f9fc;
}
.search-glyph {
  color: var(--gits-muted);
}
.shell-search input {
  flex: 1;
  border: 0;
  background: transparent;
  font-size: 12px;
  color: var(--gits-text);
  outline: none;
}
.global-new {
  height: 32px;
  padding: 0 14px;
  border: 0;
  border-radius: 4px;
  background: var(--gits-blue-600);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}
.global-new:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.header-spacer {
  flex: 1;
}
.header-icon,
.theme-toggle {
  border: 0;
  background: transparent;
  color: var(--gits-muted);
  cursor: pointer;
  font-size: 13px;
}
.header-user {
  display: flex;
  align-items: center;
  gap: 8px;
}
.header-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--gits-teal-500);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: var(--gits-teal-700);
}
.header-user-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
  font-size: 9px;
  color: var(--gits-text);
}
.header-user-copy span:last-child {
  color: var(--gits-muted);
}
.shell-tabbar {
  height: 42px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-bottom: 1px solid var(--gits-line);
}
.shell-content {
  padding: 20px 24px 32px;
  background: var(--gits-page);
  min-height: calc(100vh - 98px);
}
</style>
