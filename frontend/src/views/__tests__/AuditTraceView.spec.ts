import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import AuditTraceView from '../AuditTraceView.vue'
import type { AuditTraceEntry } from '../../api/v11'

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchAuditTrace: vi.fn(),
  }
})

const entry: AuditTraceEntry = {
  traceId: 'tr-1',
  entityType: 'HumanGate',
  entityId: 'g-pending',
  operation: 'DECIDE',
  occurredAt: '2026-08-25T00:00:00Z',
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
  NInput: { template: '<input class="n-input" />' },
  NSpace: { template: '<div class="n-space"><slot /></div>' },
  NDataTable: { template: '<table data-testid="p39-table" />' },
}

async function mountP39() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/audit-trace', name: 'AuditTrace', component: AuditTraceView }],
  })
  await router.push('/audit-trace')
  const wrapper = mount(AuditTraceView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P39 AuditTraceView C0 upgrade', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully and consumes fetchAuditTrace', async () => {
    const { fetchAuditTrace } = await import('../../api/v11')
    ;(fetchAuditTrace as ReturnType<typeof vi.fn>).mockResolvedValue([entry])
    const wrapper = await mountP39()
    expect(wrapper.get('[data-testid="p39-audit-trace"]').text()).toContain('审计与权限')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="p39-table"]').exists()).toBe(true)
    expect(fetchAuditTrace).toHaveBeenCalled()
    expect(wrapper.text()).not.toContain('NEED-826')
  })

  it('shows empty success when there are no audit rows', async () => {
    const { fetchAuditTrace } = await import('../../api/v11')
    ;(fetchAuditTrace as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP39()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchAuditTrace fails', async () => {
    const { fetchAuditTrace } = await import('../../api/v11')
    ;(fetchAuditTrace as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('audit down'))
    const wrapper = await mountP39()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="retry-action"]').exists()).toBe(true)
  })

  it('keeps 导出审计包 and 验证权限 disabled', async () => {
    const { fetchAuditTrace } = await import('../../api/v11')
    ;(fetchAuditTrace as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP39()
    expect(wrapper.text()).toContain('导出审计包')
    expect(wrapper.text()).toContain('验证权限')
    const buttons = wrapper.findAll('[data-testid="gated-action"]')
    expect(buttons.length).toBe(2)
    for (const button of buttons) {
      expect((button.element as HTMLButtonElement).disabled).toBe(true)
    }
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })
})
