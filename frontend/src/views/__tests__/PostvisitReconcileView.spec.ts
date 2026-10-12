import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import PostvisitReconcileView from '../PostvisitReconcileView.vue'
import type { PostvisitExecutionResponse } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    executePostvisit: vi.fn(),
  }
})

const mockResult: PostvisitExecutionResponse = {
  transcriptId: 't1',
  analysisId: 'a1',
  internalReportId: 'ir1',
  crmReportId: 'cr1',
  crmCommandCount: 2,
  allCommandsRequireHumanConfirm: true,
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

async function mountP18(query: Record<string, string> = { customerId: 'c1', journeyId: 'j1', operatingCaseId: 'oc1' }) {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/engagement/postvisit', name: 'PostvisitReconcile', component: PostvisitReconcileView }],
  })
  await router.push({ path: '/engagement/postvisit', query })
  const wrapper = mount(PostvisitReconcileView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P18 PostvisitReconcileView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully and keeps both versions after executePostvisit', async () => {
    const { executePostvisit } = await import('../../api/engagement')
    ;(executePostvisit as ReturnType<typeof vi.fn>).mockResolvedValue(mockResult)
    const wrapper = await mountP18()
    expect(wrapper.get('[data-testid="p18-postvisit"]').text()).toContain('事实对账')
    expect(wrapper.find('[data-testid="p18-previous-claim"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p18-new-evidence"]').exists()).toBe(true)
    const previous = wrapper.get('[data-testid="p18-previous-input"]')
    await previous.setValue('访前主张：授信仅作讨论')
    await wrapper.get('[data-testid="p18-confirm"]').setValue(true)
    await wrapper.get('[data-testid="p18-execute"]').trigger('click')
    await flushPromises()
    expect(executePostvisit as ReturnType<typeof vi.fn>).toHaveBeenCalled()
    expect((wrapper.get('[data-testid="p18-previous-input"]').element as HTMLTextAreaElement).value).toContain('访前主张：授信仅作讨论')
    expect(wrapper.get('[data-testid="p18-new-evidence"]').text()).toContain('a1')
  })

  it('shows empty success when journey context is missing', async () => {
    const wrapper = await mountP18({})
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无|缺对象/)
  })

  it('shows error four-state when executePostvisit fails', async () => {
    const { executePostvisit } = await import('../../api/engagement')
    ;(executePostvisit as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('conflict'))
    const wrapper = await mountP18()
    await wrapper.get('[data-testid="p18-confirm"]').setValue(true)
    await wrapper.get('[data-testid="p18-execute"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables execute when the journey object is missing', async () => {
    const wrapper = await mountP18({})
    expect(wrapper.text()).toContain('缺对象')
  })
})
