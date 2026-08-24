import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import CustomerOperatingView from '../CustomerOperatingView.vue'
import type { CustomerContext, ProductMatch } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomerContext: vi.fn(),
    matchProducts: vi.fn(),
  }
})

const seedUnknown = '二期项目实际投资额'
const seedPartial = '智能制造二期项目(已备案，投资额待确认)'
const seedStale = '3000万需求的具体含义(上次提及但未明确)'
const seedQuestion = '二期项目总投资和资金安排?'
const seedTxDesc = '货款回笼-数控机床订单'

const fakeContext: CustomerContext = {
  customer: {
    customerId: 'CUST-CORP-0001',
    customerName: '华东精工装备集团有限公司',
    industry: 'MANUFACTURING',
    rmName: '张伟',
    unifiedSocialCreditCode: '91330000MA2XXXXX',
  },
  kycGapProfile: {
    profileId: 'KYC-GAP-HDEG-20260705',
    customerId: 'CUST-CORP-0001',
    asOf: '2026-07-05',
    knownItems: ['集团股权结构(3家子公司)'],
    partialKnownItems: [seedPartial],
    staleItems: [seedStale],
    conflictingOrAmbiguousItems: [],
    unknownItems: [seedUnknown],
    priorityQuestions: [seedQuestion],
  },
  opportunitySignals: [],
  recentInteractions: [],
  activeJourneys: [],
  recentTransactions: [
    {
      transactionId: 'TXN-20250801',
      customerId: 'CUST-CORP-0001',
      amount: 15000000,
      currency: 'CNY',
      transactionType: 'DEPOSIT',
      occurredAt: '2025-08-03',
      description: seedTxDesc,
    },
  ],
}

const stubs = {
  NSpin: { template: '<div class="n-spin" />' },
  NGrid: { template: '<div class="n-grid"><slot /></div>' },
  NGi: { template: '<div class="n-gi"><slot /></div>' },
  NCard: { template: '<div class="n-card"><slot /></div>' },
  NTag: { template: '<span class="n-tag"><slot /></span>' },
  NEmpty: { template: '<div class="n-empty" />' },
  NDataTable: { template: '<div class="n-data-table" />' },
  RiskBadge: { template: '<span class="risk-badge" />' },
  SignalCard: { template: '<div class="signal-card-stub" />' },
}

async function mountView(context: CustomerContext = fakeContext, products: ProductMatch[] = []) {
  const { fetchCustomerContext, matchProducts } = await import('../../api/engagement')
  ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(context)
  ;(matchProducts as ReturnType<typeof vi.fn>).mockResolvedValue(products)

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/customers/:id', name: 'CustomerOperatingView', component: CustomerOperatingView },
      { path: '/journeys/:id', name: 'JourneyTimeline', component: { template: '<div />' } },
    ],
  })
  await router.push('/customers/CUST-CORP-0001')
  await router.isReady()

  const wrapper = mount(CustomerOperatingView, {
    global: { plugins: [router], stubs },
  })
  await flushPromises()
  return wrapper
}

describe('CustomerOperatingView', () => {
  it('shows KI-FRONT-005 hint and does not render seed KYC unknown-item tags', async () => {
    const wrapper = await mountView()
    expect(wrapper.text()).toContain('DKWS 未返回该条目，请在访前报告 KI-FRONT-005 查看')
    expect(wrapper.text()).not.toContain(seedUnknown)
    expect(wrapper.text()).not.toContain(seedPartial)
    expect(wrapper.text()).not.toContain(seedStale)
    expect(wrapper.text()).not.toContain(seedQuestion)
    expect(wrapper.find('.gap-unknown').exists()).toBe(false)
    expect(wrapper.find('.n-data-table').exists()).toBe(false)
    expect(wrapper.text()).not.toContain(seedTxDesc)
  })

  it('keeps CRM master fields after load', async () => {
    const wrapper = await mountView()
    expect(wrapper.text()).toContain('华东精工装备集团有限公司')
    expect(wrapper.text()).toContain('张伟')
    expect(wrapper.text()).toContain('91330000MA2XXXXX')
  })

  it('shows KI-FRONT-006 hint when product matching is empty', async () => {
    const wrapper = await mountView()
    expect(wrapper.text()).toContain('DKWS 未返回该条目，请在访前报告 KI-FRONT-006 查看')
    expect(wrapper.text()).not.toContain('流动资金贷款')
    expect(wrapper.text()).not.toContain('供应链融资')
  })

  it('shows productName and reason when Skill returns matches', async () => {
    const wrapper = await mountView(fakeContext, [
      {
        productId: 'P-DKWS-1',
        productName: 'DKWS设备贷',
        reason: '设备更新窗口',
        confidence: 0.8,
        signal: 'DKWS',
      },
    ])
    expect(wrapper.text()).toContain('DKWS设备贷')
    expect(wrapper.text()).toContain('设备更新窗口')
    expect(wrapper.text()).not.toContain('请在访前报告 KI-FRONT-006 查看')
  })
})
