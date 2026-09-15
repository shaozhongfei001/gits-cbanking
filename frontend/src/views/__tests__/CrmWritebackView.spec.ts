import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import CrmWritebackView from '../CrmWritebackView.vue'
import type { CrmWritebackCommand } from '../../api/v11'

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchCrmWritebackCommands: vi.fn(),
    decideCrmWritebackCommand: vi.fn(),
  }
})

const mockCommand: CrmWritebackCommand = {
  commandId: 'WB-260824-031',
  journeyId: 'j1',
  customerId: 'c1',
  operation: 'UPSERT_CALL_REPORT',
  targetEntity: 'CallReport',
  payload: { summary: '例行回访', visitDate: '2026-08-24' },
  status: 'PENDING',
  humanConfirmationRequired: true,
  createdAt: '2026-08-25T00:00:00Z',
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
  CrmWritebackApproval: {
    props: ['show', 'command'],
    template: '<div data-testid="p19-approval">{{ command && command.commandId }}</div>',
  },
}

async function mountP19() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/engagement/crm-writeback', name: 'CrmWriteback', component: CrmWritebackView }],
  })
  await router.push('/engagement/crm-writeback')
  const wrapper = mount(CrmWritebackView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P19 CrmWritebackView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully and previews payload without inventing fields', async () => {
    const { fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([mockCommand])
    const wrapper = await mountP19()
    expect(wrapper.get('[data-testid="p19-crm-writeback"]').text()).toContain('CRM')
    expect(wrapper.text()).toContain('WB-260824-031')
    expect(wrapper.text()).toContain('summary')
    expect(wrapper.text()).not.toContain('inventedField')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    await wrapper.get('[data-testid="p19-preview-action"]').trigger('click')
    expect(wrapper.get('[data-testid="p19-approval"]').text()).toContain('WB-260824-031')
  })

  it('shows empty success when there are no writeback commands', async () => {
    const { fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP19()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchCrmWritebackCommands fails', async () => {
    const { fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('crm down'))
    const wrapper = await mountP19()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables unsigned writeback that skips preview', async () => {
    const { fetchCrmWritebackCommands } = await import('../../api/v11')
    ;(fetchCrmWritebackCommands as ReturnType<typeof vi.fn>).mockResolvedValue([mockCommand])
    const wrapper = await mountP19()
    const directWrite = wrapper.findAll('button').find((b) => b.text().includes('直接写回'))
    expect(directWrite).toBeTruthy()
    expect((directWrite!.element as HTMLButtonElement).disabled).toBe(true)
  })
})
