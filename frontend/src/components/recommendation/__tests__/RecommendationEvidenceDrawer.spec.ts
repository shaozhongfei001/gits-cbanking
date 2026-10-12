import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RecommendationEvidenceDrawer from '../RecommendationEvidenceDrawer.vue'
import type {
  EligibilityResult,
  EvidenceBundle,
  CustomerFactSource,
  ExclusionReason,
} from '../types'

// naive-ui 组件 `name` 选项不带 N 前缀（如 NDrawer → Drawer），stubs 需按 name 匹配。
const stubs = {
  Drawer: { template: '<div class="n-drawer-stub"><slot /></div>' },
  DrawerContent: { template: '<div class="n-drawer-content-stub"><slot /></div>' },
  Descriptions: { template: '<div class="n-descriptions-stub"><slot /></div>' },
  DescriptionsItem: { template: '<div class="n-desc-item-stub"><slot /></div>' },
  Tag: { template: '<span class="n-tag-stub"><slot /></span>' },
  Empty: { template: '<div class="n-empty-stub"><slot /></div>' },
  Alert: { props: ['title'], template: '<div class="n-alert-stub"><slot />{{ title }}</div>' },
  Divider: { template: '<div class="n-divider-stub" />' },
}

function createCandidate(overrides: Partial<EligibilityResult> = {}): EligibilityResult {
  return {
    productId: 'PROD-1',
    productVersion: '2.2',
    eligibility: 'ELIGIBLE',
    ruleResults: [
      { ruleId: 'PR-ELIG-001', ruleVersion: '1.3', result: 'PASS', reasonCode: 'PRODUCT_VERSION_ACTIVE' },
      { ruleId: 'PR-ADM-004', ruleVersion: '2.0', result: 'FAIL', reasonCode: 'CUSTOMER_TYPE_NOT_ALLOWED' },
    ],
    ...overrides,
  }
}

const evidenceBundle: EvidenceBundle = {
  skillId: 'SP-15',
  skillVersion: '2.0.0-candidate',
  contentHash: 'sha256:abc123',
  traceId: 'TRACE-1',
  evidenceBundleId: 'EVB-1',
}

function mountDrawer(overrides: Record<string, unknown> = {}) {
  return mount(RecommendationEvidenceDrawer, {
    props: {
      show: true,
      candidate: createCandidate(),
      evidenceBundle,
      factSources: [],
      exclusionReasons: [],
      ...overrides,
    },
    global: { stubs },
  })
}

describe('RecommendationEvidenceDrawer', () => {
  it('renders product version and eligibility label', () => {
    const wrapper = mountDrawer()
    expect(wrapper.find('[data-testid="product-id"]').text()).toBe('PROD-1')
    expect(wrapper.find('[data-testid="product-version"]').text()).toBe('2.2')
    expect(wrapper.find('[data-testid="eligibility"]').text()).toContain('合格')
  })

  it('renders rule hits with ruleId, ruleVersion and reasonCode', () => {
    const wrapper = mountDrawer()
    const hits = wrapper.findAll('[data-testid="rule-hit"]')
    expect(hits).toHaveLength(2)
    expect(hits[0].find('[data-testid="rule-id"]').text()).toBe('PR-ELIG-001')
    expect(hits[0].find('[data-testid="rule-version"]').text()).toBe('v1.3')
    expect(hits[0].find('[data-testid="reason-code"]').text()).toContain('PRODUCT_VERSION_ACTIVE')
    expect(hits[1].find('[data-testid="reason-code"]').text()).toContain('CUSTOMER_TYPE_NOT_ALLOWED')
  })

  it('renders fact source content when the actor may view it', () => {
    const factSources: CustomerFactSource[] = [
      { ref: 'FACT-CUST-TYPE-001', canViewSource: true, content: '客户为制造业中型企业' },
    ]
    const wrapper = mountDrawer({ factSources })
    expect(wrapper.find('[data-testid="fact-ref"]').text()).toBe('FACT-CUST-TYPE-001')
    expect(wrapper.find('[data-testid="fact-content"]').text()).toBe('客户为制造业中型企业')
    expect(wrapper.find('[data-testid="fact-denied"]').exists()).toBe(false)
  })

  it('shows existence + permission note and never leaks original text when access denied', () => {
    const sensitive = '客户实控人为张三，身份证号 110101199001011234'
    const factSources: CustomerFactSource[] = [
      { ref: 'FACT-OWNER-001', canViewSource: false, content: sensitive },
    ]
    const wrapper = mountDrawer({ factSources })
    expect(wrapper.find('[data-testid="fact-denied"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="fact-denied"]').text()).toContain('证据存在')
    expect(wrapper.find('[data-testid="fact-denied"]').text()).toContain('无权查看')
    expect(wrapper.find('[data-testid="fact-content"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain(sensitive)
  })

  it('renders EvidenceBundle skillId/version/hash/traceId', () => {
    const wrapper = mountDrawer()
    expect(wrapper.find('[data-testid="bundle-skill-id"]').text()).toBe('SP-15')
    expect(wrapper.find('[data-testid="bundle-skill-version"]').text()).toBe('2.0.0-candidate')
    expect(wrapper.find('[data-testid="bundle-content-hash"]').text()).toBe('sha256:abc123')
    expect(wrapper.find('[data-testid="bundle-trace-id"]').text()).toBe('TRACE-1')
    expect(wrapper.find('[data-testid="bundle-id"]').text()).toBe('EVB-1')
  })

  it('renders exclusion reasons', () => {
    const exclusionReasons: ExclusionReason[] = [
      { reasonCode: 'REGULATORY_PROHIBITED_INDUSTRY', text: '监管禁止准入行业' },
    ]
    const wrapper = mountDrawer({ exclusionReasons })
    expect(wrapper.find('[data-testid="exclusion-reason"]').text()).toContain('监管禁止准入行业')
    expect(wrapper.find('[data-testid="exclusion-reason"]').text()).toContain('REGULATORY_PROHIBITED_INDUSTRY')
  })

  it('renders empty candidate hint when no candidate is selected', () => {
    const wrapper = mountDrawer({ candidate: null })
    expect(wrapper.text()).toContain('未选择候选或理由')
    expect(wrapper.find('[data-testid="product-id"]').exists()).toBe(false)
  })
})
