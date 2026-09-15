import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter, type RouteRecordRaw } from 'vue-router'
import type { Component } from 'vue'
import CollabView from '../CollabView.vue'
import DeliveryCenterView from '../DeliveryCenterView.vue'
import AccountPlansView from '../AccountPlansView.vue'
import ValueRealizationView from '../ValueRealizationView.vue'
import DegradeRecoveryView from '../DegradeRecoveryView.vue'
import { loadGovDegradeShell, probeDegradeServices } from '../../composables/govDegrade'

vi.mock('../../composables/govDegrade', async () => {
  const actual = await vi.importActual<typeof import('../../composables/govDegrade')>(
    '../../composables/govDegrade',
  )
  return {
    ...actual,
    loadGovDegradeShell: vi.fn(actual.loadGovDegradeShell),
    probeDegradeServices: vi.fn(actual.probeDegradeServices),
  }
})

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

type C2Case = {
  pageId: string
  path: string
  name: string
  component: Component
  testId: string
  objectNeedle: string
  actions: string[]
  emptyNeedle: string
}

const CASES: C2Case[] = [
  {
    pageId: 'P31',
    path: '/collab',
    name: 'CollabHome',
    component: CollabView,
    testId: 'p31-collab',
    objectNeedle: '非正式专家协同（C2 降级）',
    actions: ['补充材料', '提交意见'],
    emptyNeedle: '暂无专家协同',
  },
  {
    pageId: 'P33',
    path: '/delivery',
    name: 'DeliveryHome',
    component: DeliveryCenterView,
    testId: 'p33-delivery',
    objectNeedle: '非正式交付包（C2 降级）',
    actions: ['生成交付包', '确认发送'],
    emptyNeedle: 'DeliveryPackage',
  },
  {
    pageId: 'P34',
    path: '/account-plans',
    name: 'AccountPlansHome',
    component: AccountPlansView,
    testId: 'p34-account-plans',
    objectNeedle: '非正式账户计划（C2 降级）',
    actions: ['新增里程碑', '开始复盘'],
    emptyNeedle: 'AccountPlan',
  },
  {
    pageId: 'P35',
    path: '/value',
    name: 'ValueHome',
    component: ValueRealizationView,
    testId: 'p35-value',
    objectNeedle: '非正式价值口径（C2 降级）',
    actions: ['记录基线', '发起复盘'],
    emptyNeedle: '暂无价值实现',
  },
  {
    pageId: 'P40',
    path: '/degrade',
    name: 'DegradeHome',
    component: DegradeRecoveryView,
    testId: 'p40-degrade',
    objectNeedle: '服务降级（C2 离线包禁用）',
    actions: ['下载离线包'],
    emptyNeedle: '离线包',
  },
]

async function mountPage(page: C2Case) {
  setActivePinia(createPinia())
  const routes: RouteRecordRaw[] = [{ path: page.path, name: page.name, component: page.component }]
  const router = createRouter({ history: createMemoryHistory(), routes })
  await router.push(page.path)
  const wrapper = mount(page.component, { global: { plugins: [router], stubs } })
  await flushPromises()
  return wrapper
}

describe('P31/P33/P34/P35/P40 governance C2 degrade shells', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.mocked(loadGovDegradeShell).mockReset()
    vi.mocked(loadGovDegradeShell).mockResolvedValue({ empty: true, informal: true })
    vi.mocked(probeDegradeServices).mockReset()
    vi.mocked(probeDegradeServices).mockResolvedValue([
      { serviceId: 'human-gates', label: 'HumanGate', available: true, detail: '可查询' },
    ])
  })

  for (const page of CASES) {
    describe(page.pageId, () => {
      it('enters successfully with empty/explanation instead of fabricating objects', async () => {
        const wrapper = await mountPage(page)
        expect(wrapper.get(`[data-testid="${page.testId}"]`).text()).toContain(page.objectNeedle)
        expect(wrapper.find('[data-testid="success-state"]').exists()).toBe(true)
        expect(wrapper.text()).toMatch(new RegExp(page.emptyNeedle))
        expect(wrapper.text()).not.toContain('NEED-826')
        if (page.pageId === 'P34') {
          expect(wrapper.text()).toMatch(/Task\/Commitment/)
        }
      })

      it('shows error four-state when the loader fails', async () => {
        if (page.pageId === 'P40') {
          vi.mocked(probeDegradeServices).mockRejectedValueOnce(new Error('upstream'))
        } else {
          vi.mocked(loadGovDegradeShell).mockRejectedValueOnce(new Error('upstream'))
        }
        const wrapper = await mountPage(page)
        expect(wrapper.find('[data-testid="error-state"]').exists()).toBe(true)
        expect(wrapper.find('[data-testid="retry-action"]').exists()).toBe(true)
      })

      it(`keeps ${page.actions.join(' / ')} disabled with reason and unlock path`, async () => {
        const wrapper = await mountPage(page)
        for (const action of page.actions) {
          expect(wrapper.text()).toContain(action)
        }
        const buttons = wrapper.findAll('[data-testid="gated-action"]')
        expect(buttons.length).toBe(page.actions.length)
        for (const button of buttons) {
          expect((button.element as HTMLButtonElement).disabled).toBe(true)
        }
        expect(wrapper.get('[data-testid="disabled-reason"]').text()).toMatch(/原因|解除路径/)
      })
    })
  }
})
