import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import PrevisitGapsView from '../PrevisitGapsView.vue'
import type { KycGapProfile } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchKycGapProfile: vi.fn(),
  }
})

const mockProfile: KycGapProfile = {
  profileId: 'gap-1',
  customerId: 'c1',
  asOf: '2026-08-25T00:00:00Z',
  knownItems: ['统一社会信用代码'],
  partialKnownItems: ['实控人'],
  staleItems: [],
  conflictingOrAmbiguousItems: [],
  unknownItems: ['近12个月结算结构'],
  priorityQuestions: ['本轮扩产资金缺口确认？'],
}

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { template: '<div class="n-empty" />' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
}

async function mountP12(query: Record<string, string> = { customerId: 'c1' }) {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/engagement/previsit/gaps', name: 'PrevisitGaps', component: PrevisitGapsView },
      { path: '/engagement/previsit/evidence', name: 'PrevisitEvidence', component: { template: '<div/>' } },
    ],
  })
  await router.push({ path: '/engagement/previsit/gaps', query })
  await router.isReady()
  const wrapper = mount(PrevisitGapsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return { wrapper, router }
}

describe('P12 PrevisitGapsView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully via fetchKycGapProfile', async () => {
    const { fetchKycGapProfile } = await import('../../api/engagement')
    ;(fetchKycGapProfile as ReturnType<typeof vi.fn>).mockResolvedValue(mockProfile)
    const { wrapper } = await mountP12()
    expect(wrapper.get('[data-testid="p12-previsit-gaps"]').text()).toContain('访前目标')
    expect(wrapper.text()).toContain('近12个月结算结构')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
  })

  it('shows empty success when the gap profile has no items', async () => {
    const { fetchKycGapProfile } = await import('../../api/engagement')
    ;(fetchKycGapProfile as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...mockProfile,
      knownItems: [],
      partialKnownItems: [],
      staleItems: [],
      conflictingOrAmbiguousItems: [],
      unknownItems: [],
      priorityQuestions: [],
    })
    const { wrapper } = await mountP12()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchKycGapProfile fails', async () => {
    const { fetchKycGapProfile } = await import('../../api/engagement')
    ;(fetchKycGapProfile as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('upstream'))
    const { wrapper } = await mountP12()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables auto-fill and can navigate to P13', async () => {
    const { fetchKycGapProfile } = await import('../../api/engagement')
    ;(fetchKycGapProfile as ReturnType<typeof vi.fn>).mockResolvedValue(mockProfile)
    const { wrapper, router } = await mountP12()
    // "自动填补缺口" 是禁用的分支动作
    const autoFill = wrapper.findAll('button').find((b) => b.text().includes('自动填补缺口'))
    expect(autoFill).toBeTruthy()
    expect((autoFill!.element as HTMLButtonElement).disabled).toBe(true)
    await wrapper.get('[data-testid="p12-go-evidence"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/engagement/previsit/evidence')
  })
})
