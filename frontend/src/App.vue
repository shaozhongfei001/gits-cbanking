<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { NConfigProvider, NMessageProvider, darkTheme } from 'naive-ui'
import type { GlobalThemeOverrides } from 'naive-ui'
import ExperienceShell from './layouts/ExperienceShell.vue'

const route = useRoute()
const isDark = ref(false)
const isPublic = computed(() => route.meta.public === true)

const gitsTheme: GlobalThemeOverrides = {
  common: {
    primaryColor: '#1976D2',
    primaryColorHover: '#48A7E8',
    primaryColorPressed: '#0B2E4F',
    primaryColorSuppl: '#1976D2',
    borderRadius: '4px',
  },
}

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
</script>

<template>
  <n-config-provider :theme="isDark ? darkTheme : undefined" :theme-overrides="gitsTheme">
    <n-message-provider>
      <ExperienceShell v-if="!isPublic" :is-dark="isDark" @update:is-dark="toggleTheme">
        <router-view />
      </ExperienceShell>
      <router-view v-else />
    </n-message-provider>
  </n-config-provider>
</template>
