import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import ClaimsView from '../ClaimsView.vue'
import type { Claim } from '../../api/engagement'
import type { EvidenceVersion } from '../../api/v11'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    listClaims: vi.fn(),
  }
})

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchEvidenceVersions: vi.fn(),
  }
})

const claimWithEvidence: Claim = {
  claimId: 'clm-1',
  customerId: 'c1',
  claimType: 'CUSTOMER_STATEMENT',
  content: '客户口头提及扩产意向',
  status: 'CANDIDATE',
  evidenceRef: 'ev-1',
}

const claimWithoutEvidence: Claim = {
  claimId: 'clm-2',
  claimType: 'INTERNAL_NOTE',
  content: '内部备忘',
  status: 'CANDIDATE',
}

const version: EvidenceVersion = {
  versionId: 'ev-1-v1',
  evidenceId: 'ev-1',
  version: 1,
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
}

async function mountP37() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/claims', name: 'ClaimsHome', component: ClaimsView }],
  })
  await router.push('/claims')
  const wrapper = mount(ClaimsView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P37 ClaimsView C0 listClaims', () => {
  beforeEach(async () => {
    sessionStorage.clear()
    const { listClaims } = await import('../../api/engagement')
    const { fetchEvidenceVersions } = await import('../../api/v11')
    ;(listClaims as ReturnType<typeof vi.fn>).mockReset()
    ;(fetchEvidenceVersions as ReturnType<typeof vi.fn>).mockReset()
  })

  it('enters successfully using claimId and loads evidence versions only when refs exist', async () => {
    const { listClaims } = await import('../../api/engagement')
    const { fetchEvidenceVersions } = await import('../../api/v11')
    ;(listClaims as ReturnType<typeof vi.fn>).mockResolvedValue([claimWithEvidence, claimWithoutEvidence])
    ;(fetchEvidenceVersions as ReturnType<typeof vi.fn>).mockResolvedValue([version])
    const wrapper = await mountP37()
    expect(wrapper.get('[data-testid="p37-claims"]').text()).toContain('Claim / Evidence 中心')
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('clm-1')
    expect(wrapper.text()).toContain('clm-2')
    expect(wrapper.text()).toContain('ev-1-v1')
    expect(wrapper.text()).not.toContain('NEED-826')
    expect(fetchEvidenceVersions).toHaveBeenCalledWith('ev-1')
    expect(fetchEvidenceVersions).toHaveBeenCalledTimes(1)
  })

  it('shows empty success when listClaims returns no rows', async () => {
    const { listClaims } = await import('../../api/engagement')
    const { fetchEvidenceVersions } = await import('../../api/v11')
    ;(listClaims as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(fetchEvidenceVersions as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP37()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
    expect(fetchEvidenceVersions).not.toHaveBeenCalled()
  })

  it('shows error four-state when listClaims fails', async () => {
    const { listClaims } = await import('../../api/engagement')
    ;(listClaims as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('claims down'))
    const wrapper = await mountP37()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('keeps 登记证据 and 处理冲突 disabled', async () => {
    const { listClaims } = await import('../../api/engagement')
    ;(listClaims as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const wrapper = await mountP37()
    expect(wrapper.text()).toContain('登记证据')
    expect(wrapper.text()).toContain('处理冲突')
    const buttons = wrapper.findAll('[data-testid="gated-action"]')
    expect(buttons.length).toBe(2)
    for (const button of buttons) {
      expect((button.element as HTMLButtonElement).disabled).toBe(true)
    }
    expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
  })
})
