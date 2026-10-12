import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { NCard, NTag } from 'naive-ui'
import CustomerCard from '../CustomerCard.vue'
import RiskBadge from '../RiskBadge.vue'
import type { Customer } from '../../api/engagement'

function createCustomer(overrides: Partial<Customer> = {}): Customer {
  return {
    customerId: 'cust-001',
    customerName: '测试企业有限公司',
    industry: 'MANUFACTURING',
    enterpriseScale: 'LARGE',
    customerTier: 'STRATEGIC',
    riskLevel: 'MEDIUM',
    coreTags: ['制造业龙头', '上市公司'],
    ...overrides,
  }
}

function mountCard(customer: Customer) {
  return mount(CustomerCard, {
    props: { customer },
    global: {
      components: { NCard, NTag, RiskBadge },
    },
  })
}

describe('CustomerCard', () => {
  it('renders customer name', () => {
    const wrapper = mountCard(createCustomer({ customerName: '华科技术集团' }))
    expect(wrapper.find('.customer-name').text()).toBe('华科技术集团')
  })

  it('renders industry label', () => {
    const wrapper = mountCard(createCustomer({ industry: 'FINANCE' }))
    expect(wrapper.text()).toContain('金融业')
  })

  it('renders next action for high-risk customer', () => {
    const wrapper = mountCard(createCustomer({ riskLevel: 'HIGH' }))
    expect(wrapper.text()).toContain('风险跟进')
  })

  it('renders next action for strategic customer', () => {
    const wrapper = mountCard(createCustomer({ customerTier: 'STRATEGIC', riskLevel: 'LOW' }))
    expect(wrapper.text()).toContain('经营检视')
  })

  it('renders customer tier label', () => {
    const wrapper = mountCard(createCustomer({ customerTier: 'KEY' }))
    expect(wrapper.text()).toContain('重点客户')
  })

  it('renders risk badge with correct level', () => {
    const wrapper = mountCard(createCustomer({ riskLevel: 'HIGH' }))
    const badge = wrapper.findComponent(RiskBadge)
    expect(badge.props('level')).toBe('HIGH')
  })

  it('renders core tags (up to 3)', () => {
    const wrapper = mountCard(createCustomer({
      coreTags: ['标签A', '标签B', '标签C', '标签D'],
    }))
    const tags = wrapper.findAllComponents(NTag)
    expect(tags).toHaveLength(3)
  })

  it('renders no tags when coreTags is empty', () => {
    const wrapper = mountCard(createCustomer({ coreTags: [] }))
    expect(wrapper.find('.tags-row').exists()).toBe(false)
  })

  it('renders no tags when coreTags is undefined', () => {
    const wrapper = mountCard(createCustomer({ coreTags: undefined }))
    expect(wrapper.find('.tags-row').exists()).toBe(false)
  })

  it('emits click event when card is clicked', async () => {
    const wrapper = mountCard(createCustomer())
    await wrapper.findComponent(NCard).vm.$emit('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('shows dash for missing customer tier', () => {
    const wrapper = mountCard(createCustomer({ customerTier: undefined }))
    const rows = wrapper.findAll('.info-row')
    const tierRow = rows.find(r => r.text().includes('层级'))
    expect(tierRow?.find('.value').text()).toBe('-')
  })

  it('shows dash for missing industry', () => {
    const wrapper = mountCard(createCustomer({ industry: undefined }))
    const rows = wrapper.findAll('.info-row')
    const industryRow = rows.find(r => r.text().includes('行业'))
    expect(industryRow?.find('.value').text()).toBe('-')
  })
})
