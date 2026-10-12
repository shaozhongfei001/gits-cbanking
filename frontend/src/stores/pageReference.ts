import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { PageReference } from '../types/pageReference'
import { PAGE_REFERENCE_STORAGE_KEY } from '../types/pageReference'

function emptyRef(objectType: string): PageReference {
  return { objectType }
}

function readAll(): Record<string, PageReference> {
  if (typeof sessionStorage === 'undefined') {
    return {}
  }
  try {
    const raw = sessionStorage.getItem(PAGE_REFERENCE_STORAGE_KEY)
    return raw ? JSON.parse(raw) as Record<string, PageReference> : {}
  } catch {
    return {}
  }
}

function writeAll(map: Record<string, PageReference>): void {
  if (typeof sessionStorage === 'undefined') {
    return
  }
  sessionStorage.setItem(PAGE_REFERENCE_STORAGE_KEY, JSON.stringify(map))
}

export const usePageReferenceStore = defineStore('pageReference', () => {
  const byPageId = ref<Record<string, PageReference>>(readAll())

  function capture(pageId: string, patch: PageReference): void {
    const next = { ...(byPageId.value[pageId] ?? emptyRef(patch.objectType)), ...patch }
    byPageId.value = { ...byPageId.value, [pageId]: next }
    writeAll(byPageId.value)
  }

  function restore(pageId: string, fallbackObjectType: string): PageReference {
    return byPageId.value[pageId] ?? emptyRef(fallbackObjectType)
  }

  const hasAny = computed(() => Object.keys(byPageId.value).length > 0)

  return { byPageId, capture, restore, hasAny }
})
