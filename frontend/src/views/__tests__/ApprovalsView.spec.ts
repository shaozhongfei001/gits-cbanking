import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ApprovalsView from '../ApprovalsView.vue'
import type { HumanGate } from '../../api/v11'

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchHumanGates: vi.fn(),
    decideHumanGate: vi.fn(),
  }
})

const pendingGate: HumanGate = {
  gateId: 'g-pending',
  gateType: 'C02_REPORT_APPROVE',
  status: 'PENDING',
  subject: '访后报告待确认',
  createdAt: '2026-08-25T00:00:00Z',
}

const creditLabelGate: HumanGate = {
  gateId: 'g-credit',
  gateType: 'F02_CREDIT_CHECK',
  status: 'PENDING',
  subject: '既有授信审查门禁',
  createdAt: '2026-08-25T00:00:00Z',
}

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NResult: { template: '<div class="n-result"><slot name="footer" /></div>' },
  NButton: {
    props: ['disabled'],
    template: '<button class="n-button" :disabled="disabled"><slot /></button>',
  },
  NEmpty: { props: ['description'], template: '<div class="n-empty">{{ description }}</div>' },
  NTooltip: { template: '<div><slot name="trigger" /><slot /></div>' },
  NCard: { template: '<div class="n-card"><slot /></div>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  HumanGateDialog: {
    props: ['show', 'gate'],
    emits: ['decide'],
    template:
      '<div v-if="show" data-testid="human-gate-dialog"><span>{{ gate?.gateId }}</span><button data-testid="stub-decide" @click="$emit(\'decide\', gate.gateId, \'APPROVE\', undefined, \'\')">decide</button></div>',
  },
}

async function mountP32() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/approvals', name: 'ApprovalsHome', component: ApprovalsView }],
  })
  await router.push('/approvals')
  const wrapper = mount(ApprovalsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P32 ApprovalsView C0 HumanGate', () => {
  beforeEach(async () => {
    sessionStorage.clear()
    const { fetchHumanGates, decideHumanGate } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockReset()
    ;(decideHumanGate as ReturnType<typeof vi.fn>).mockReset()
  })

  it('enters successfully and lists returned gates without a create-machine', async () => {
    const { fetchHumanGates } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([pendingGate, creditLabelGate])
    const wrapper = await mountP32()
    expect(wrapper.get('[data-testid="p32-approvals"]').text()).toContain('审批工作中心')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('g-pending')
    expect(wrapper.text()).toContain('授信审查')
    expect(wrapper.text()).not.toMatch(/发起授信|发起定价|新建授信|新建定价/)
    expect(wrapper.text()).not.toContain('NEED-826')
  })

  it('shows empty success when fetchHumanGates returns no gates', async () => {
    const { fetchHumanGates } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP32()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
    expect((wrapper.get('[data-testid="p32-open-first"]').element as HTMLButtonElement).disabled).toBe(true)
  })

  it('shows error four-state when fetchHumanGates fails', async () => {
    const { fetchHumanGates } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('gate down'))
    const wrapper = await mountP32()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('opens the first PENDING gate and decides only that returned gate', async () => {
    const { fetchHumanGates, decideHumanGate } = await import('../../api/v11')
    ;(fetchHumanGates as ReturnType<typeof vi.fn>).mockResolvedValue([pendingGate])
    ;(decideHumanGate as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...pendingGate,
      status: 'APPROVED',
      decision: 'APPROVE',
    })
    const wrapper = await mountP32()
    await wrapper.get('[data-testid="p32-open-first"]').trigger('click')
    await flushPromises()
    expect(wrapper.get('[data-testid="human-gate-dialog"]').text()).toContain('g-pending')
    await wrapper.get('[data-testid="stub-decide"]').trigger('click')
    await flushPromises()
    expect(decideHumanGate).toHaveBeenCalledWith(
      'g-pending',
      expect.objectContaining({ decision: 'APPROVE', actorId: 'current-user' }),
    )
  })
})
