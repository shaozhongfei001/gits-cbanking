import { describe, it, expect } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { usePageReferenceStore } from '../pageReference'

describe('pageReference store', () => {
  it('captures filter/subtab/draft and restores them', () => {
    setActivePinia(createPinia())
    sessionStorage.clear()
    const store = usePageReferenceStore()
    store.capture('P01', {
      objectType: '客户经营应用',
      filter: '高风险',
      subtab: 'queue',
      scrollAnchor: 120,
      draftId: 'draft-1',
    })
    const restored = store.restore('P01', '客户经营应用')
    expect(restored.filter).toBe('高风险')
    expect(restored.subtab).toBe('queue')
    expect(restored.scrollAnchor).toBe(120)
    expect(restored.draftId).toBe('draft-1')
  })
})
