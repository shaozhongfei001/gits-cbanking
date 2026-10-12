import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const THEME_KEY = 'gits-theme'

function readInitial(): boolean {
  if (typeof window === 'undefined') return false
  try {
    const stored = localStorage.getItem(THEME_KEY)
    if (stored === 'dark') return true
    if (stored === 'light') return false
  } catch {
    // localStorage unavailable (test env, sandboxed iframe, etc.)
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false
}

function applyTheme(dark: boolean) {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
}

export const useThemeStore = defineStore('gits-theme', () => {
  const isDark = ref(readInitial())
  applyTheme(isDark.value)

  function toggle() {
    isDark.value = !isDark.value
    try {
      localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
    } catch {
      // localStorage unavailable
    }
    applyTheme(isDark.value)
  }

  return { isDark, toggle }
})
