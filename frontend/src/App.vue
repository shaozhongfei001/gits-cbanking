<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NConfigProvider, NMessageProvider, darkTheme } from 'naive-ui'
import ExperienceShell from './layouts/ExperienceShell.vue'
import { gitsThemeFor } from './theme/naiveTheme'

const route = useRoute()

const THEME_STORAGE_KEY = 'gits-theme'

function readStoredIsDark(): boolean {
  if (typeof localStorage === 'undefined') {
    return false
  }
  return localStorage.getItem(THEME_STORAGE_KEY) === 'dark'
}

/** 在 setup 阶段解析主题，使其在首帧渲染前生效，避免亮→暗闪烁。 */
const isDark = ref(readStoredIsDark())
const isPublic = computed(() => route.meta.public === true)
const themeOverrides = computed(() => gitsThemeFor(isDark.value))

function applyDataTheme(dark: boolean) {
  if (typeof document === 'undefined') {
    return
  }
  if (dark) {
    document.documentElement.setAttribute('data-theme', 'dark')
    return
  }
  document.documentElement.removeAttribute('data-theme')
}

applyDataTheme(isDark.value)

function toggleTheme(dark: boolean) {
  isDark.value = dark
  applyDataTheme(dark)
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(THEME_STORAGE_KEY, dark ? 'dark' : 'light')
  }
}
</script>

<template>
  <n-config-provider :theme="isDark ? darkTheme : undefined" :theme-overrides="themeOverrides">
    <n-message-provider>
      <ExperienceShell v-if="!isPublic" :is-dark="isDark" @update:is-dark="toggleTheme">
        <router-view />
      </ExperienceShell>
      <router-view v-else />
    </n-message-provider>
  </n-config-provider>
</template>
