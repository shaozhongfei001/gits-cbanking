import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface WorkspaceTab {
  id: string
  title: string
  path: string
  routeName: string
  objectType: string
  recordId?: string
  dirty: boolean
}

export const useWorkspaceTabsStore = defineStore('workspaceTabs', () => {
  const tabs = ref<WorkspaceTab[]>([])
  const activeId = ref<string | null>(null)

  const activeTab = computed(() => tabs.value.find(tab => tab.id === activeId.value) ?? null)

  function openTab(input: Omit<WorkspaceTab, 'dirty'> & { dirty?: boolean }): void {
    const existing = tabs.value.find(tab => tab.path === input.path)
    if (existing) {
      activeId.value = existing.id
      existing.title = input.title
      existing.objectType = input.objectType
      existing.recordId = input.recordId
      return
    }
    const tab: WorkspaceTab = { ...input, dirty: input.dirty ?? false }
    tabs.value = [...tabs.value, tab]
    activeId.value = tab.id
  }

  function closeTab(id: string): WorkspaceTab | null {
    const index = tabs.value.findIndex(tab => tab.id === id)
    if (index < 0) {
      return activeTab.value
    }
    const closing = tabs.value[index]
    tabs.value = tabs.value.filter(tab => tab.id !== id)
    if (activeId.value === id) {
      const neighbor = tabs.value[index] ?? tabs.value[index - 1] ?? null
      activeId.value = neighbor?.id ?? null
      return neighbor
    }
    return activeTab.value
  }

  function markDirty(id: string, dirty: boolean): void {
    const tab = tabs.value.find(item => item.id === id)
    if (tab) {
      tab.dirty = dirty
    }
  }

  return { tabs, activeId, activeTab, openTab, closeTab, markDirty }
})
