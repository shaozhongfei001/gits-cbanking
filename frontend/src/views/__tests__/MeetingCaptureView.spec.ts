import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import MeetingCaptureView from '../MeetingCaptureView.vue'
import type { CustomerJourney } from '../../api/engagement'
import type { RecordingConsent } from '../../api/v11'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchJourney: vi.fn(),
  }
})

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchLatestRecordingConsent: vi.fn(),
  }
})

const mockJourney: CustomerJourney = {
  journeyId: 'j1',
  operatingCaseId: 'oc1',
  customerId: 'c1',
  customerName: '企业A',
  phase: 'PREVISIT_PREP',
  startedAt: '2026-08-25T00:00:00Z',
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

async function mountP16() {
  setActivePinia(createPinia())
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/in-meeting/:id/capture', name: 'MeetingCapture', component: MeetingCaptureView }],
  })
  await router.push('/in-meeting/j1/capture')
  const wrapper = mount(MeetingCaptureView, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P16 MeetingCaptureView', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('enters successfully and labels the draft as a candidate not a formal Claim', async () => {
    const { fetchJourney } = await import('../../api/engagement')
    const { fetchLatestRecordingConsent } = await import('../../api/v11')
    ;(fetchJourney as ReturnType<typeof vi.fn>).mockResolvedValue(mockJourney)
    ;(fetchLatestRecordingConsent as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('stt unavailable'))
    const wrapper = await mountP16()
    expect(wrapper.get('[data-testid="p16-meeting-capture"]').text()).toContain('实时捕获')
    expect(wrapper.get('[data-testid="p16-candidate-label"]').text()).toMatch(/候选/)
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/转写失败|手工/)
  })

  it('shows empty success when there is no draft yet', async () => {
    const { fetchJourney } = await import('../../api/engagement')
    const { fetchLatestRecordingConsent } = await import('../../api/v11')
    ;(fetchJourney as ReturnType<typeof vi.fn>).mockResolvedValue(mockJourney)
    ;(fetchLatestRecordingConsent as ReturnType<typeof vi.fn>).mockResolvedValue({
      consentId: 'rc1',
      interactionId: 'j1',
      consentStatus: 'DENIED',
    } satisfies RecordingConsent)
    const wrapper = await mountP16()
    expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/暂无/)
  })

  it('shows error four-state when fetchJourney fails', async () => {
    const { fetchJourney } = await import('../../api/engagement')
    ;(fetchJourney as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('not found'))
    const wrapper = await mountP16()
    expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
  })

  it('disables submitting the draft as a formal Claim', async () => {
    const { fetchJourney } = await import('../../api/engagement')
    const { fetchLatestRecordingConsent } = await import('../../api/v11')
    ;(fetchJourney as ReturnType<typeof vi.fn>).mockResolvedValue(mockJourney)
    ;(fetchLatestRecordingConsent as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('stt'))
    const wrapper = await mountP16()
    const claimBtn = wrapper.findAll('button').find((b) => b.text().includes('提交正式 Claim'))
    expect(claimBtn).toBeTruthy()
    expect((claimBtn!.element as HTMLButtonElement).disabled).toBe(true)
  })
})
