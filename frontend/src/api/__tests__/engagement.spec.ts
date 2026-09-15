import { describe, it, expect, vi, beforeEach } from 'vitest'
import type {
  RiskLevel,
  Industry,
  EnterpriseScale,
  CustomerTier,
  JourneyPhase,
  SignalType,
  SignalStatus,
  ReportType,
  InteractionType,
  InteractionOutcome,
  Customer,
  CustomerJourney,
  OpportunitySignal,
  Interaction,
  Claim,
  TransactionRecord,
} from '../engagement'

// Mock axios with inline mock functions (hoisted to top by vitest)
vi.mock('axios', () => {
  const get = vi.fn()
  const post = vi.fn()
  return {
    default: {
      create: vi.fn(() => ({
        get,
        post,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      })),
    },
    _mockGet: get,
    _mockPost: post,
  }
})

// Import after mock setup
import {
  INDUSTRY_LABELS,
  ENTERPRISE_SCALE_LABELS,
  CUSTOMER_TIER_LABELS,
  RISK_LEVEL_LABELS,
  JOURNEY_PHASE_LABELS,
  SIGNAL_TYPE_LABELS,
  SIGNAL_STATUS_LABELS,
  REPORT_TYPE_LABELS,
  INTERACTION_TYPE_LABELS,
  OUTCOME_LABELS,
  fetchCustomers,
  fetchCustomer,
  fetchOperatingView,
  fetchCustomerContext,
  fetchCustomerJourneys,
  fetchJourney,
  fetchJourneyInteractions,
  fetchJourneyClaims,
  fetchJourneySignals,
  fetchReport,
  fetchOperatingCases,
  executePrevisit,
  executePostvisit,
  generateOutreachScript,
  generateMeetingScript,
  fetchKycGapProfile,
  fetchOpportunitySignals,
  fetchTransactions,
  listInteractions,
  fetchInteractions,
  fetchAssembledKnowledgeMap,
  preparePrevisit,
  SKILL_HTTP_TIMEOUT_MS,
} from '../engagement'

// Get references to the mock functions from the mocked module
const mockGet = (vi.mocked(await import('axios')) as any)._mockGet
const mockPost = (vi.mocked(await import('axios')) as any)._mockPost

describe('engagement API - Enum mappings', () => {
  it('INDUSTRY_LABELS covers all Industry values', () => {
    const industries: Industry[] = [
      'MANUFACTURING', 'FINANCE', 'TECHNOLOGY', 'REAL_ESTATE',
      'ENERGY', 'HEALTHCARE', 'AGRICULTURE', 'LOGISTICS', 'RETAIL', 'OTHER',
    ]
    for (const ind of industries) {
      expect(INDUSTRY_LABELS[ind]).toBeDefined()
      expect(typeof INDUSTRY_LABELS[ind]).toBe('string')
    }
  })

  it('RISK_LEVEL_LABELS covers all RiskLevel values', () => {
    const levels: RiskLevel[] = ['HIGH', 'MEDIUM', 'LOW']
    for (const level of levels) {
      expect(RISK_LEVEL_LABELS[level]).toBeDefined()
    }
    expect(RISK_LEVEL_LABELS.HIGH).toBe('高风险')
    expect(RISK_LEVEL_LABELS.MEDIUM).toBe('中风险')
    expect(RISK_LEVEL_LABELS.LOW).toBe('低风险')
  })

  it('ENTERPRISE_SCALE_LABELS covers all EnterpriseScale values', () => {
    const scales: EnterpriseScale[] = ['LARGE', 'MEDIUM', 'SMALL', 'MICRO']
    for (const scale of scales) {
      expect(ENTERPRISE_SCALE_LABELS[scale]).toBeDefined()
    }
  })

  it('CUSTOMER_TIER_LABELS covers all CustomerTier values', () => {
    const tiers: CustomerTier[] = ['STRATEGIC', 'KEY', 'GROWTH', 'GENERAL']
    for (const tier of tiers) {
      expect(CUSTOMER_TIER_LABELS[tier]).toBeDefined()
    }
  })

  it('JOURNEY_PHASE_LABELS covers all JourneyPhase values', () => {
    const phases: JourneyPhase[] = [
      'KYC_COLLECT', 'INSIGHT_ANALYSIS', 'PRODUCT_MATCHING',
      'PREVISIT_PREP', 'POSTVISIT_REVIEW', 'COMPLETED',
    ]
    for (const phase of phases) {
      expect(JOURNEY_PHASE_LABELS[phase]).toBeDefined()
    }
  })

  it('SIGNAL_TYPE_LABELS covers all SignalType values', () => {
    const types: SignalType[] = ['FINANCING_NEED', 'PRODUCT_OPPORTUNITY', 'RELATIONSHIP_CHANGE']
    for (const type of types) {
      expect(SIGNAL_TYPE_LABELS[type]).toBeDefined()
    }
  })

  it('SIGNAL_STATUS_LABELS covers all SignalStatus values', () => {
    const statuses: SignalStatus[] = ['DETECTED', 'CONFIRMED', 'DISMISSED', 'CONVERTED']
    for (const status of statuses) {
      expect(SIGNAL_STATUS_LABELS[status]).toBeDefined()
    }
  })

  it('REPORT_TYPE_LABELS covers all ReportType values', () => {
    const types: ReportType[] = [
      'INTERNAL_RELATIONSHIP', 'CRM_CALL', 'UPDATED_RELATIONSHIP', 'NEXT_PREVISIT',
    ]
    for (const type of types) {
      expect(REPORT_TYPE_LABELS[type]).toBeDefined()
    }
  })

  it('INTERACTION_TYPE_LABELS covers all InteractionType values', () => {
    const types: InteractionType[] = [
      'SIGNAL_TRIGGER', 'AI_INSIGHT_PUSH', 'PHONE_CALL', 'FACE_TO_FACE_VISIT',
      'VIDEO_CONFERENCE', 'INSTANT_MESSAGE', 'EMAIL', 'PRODUCT_PRESENTATION',
      'CUSTOMER_COMPLAINT', 'FOLLOW_UP',
    ]
    for (const type of types) {
      expect(INTERACTION_TYPE_LABELS[type]).toBeDefined()
    }
  })

  it('OUTCOME_LABELS covers all InteractionOutcome values', () => {
    const outcomes: InteractionOutcome[] = [
      'COMPLETED', 'CUSTOMER_AGREED', 'CUSTOMER_DECLINED', 'CUSTOMER_DEFERRED',
      'FOLLOW_UP_REQUIRED', 'INTERRUPTED', 'INFORMATION_GATHERED',
    ]
    for (const outcome of outcomes) {
      expect(OUTCOME_LABELS[outcome]).toBeDefined()
    }
  })
})

describe('engagement API - TypeScript interface definitions', () => {
  it('Customer interface is usable', () => {
    const customer: Customer = {
      customerId: 'c1',
      customerName: 'Test Corp',
    }
    expect(customer.customerId).toBe('c1')
  })

  it('CustomerJourney interface is usable', () => {
    const journey: CustomerJourney = {
      journeyId: 'j1',
      operatingCaseId: 'oc1',
      customerId: 'c1',
      customerName: 'Test',
      phase: 'KYC_COLLECT',
      startedAt: '2025-01-01',
    }
    expect(journey.phase).toBe('KYC_COLLECT')
  })

  it('OpportunitySignal interface is usable', () => {
    const signal: OpportunitySignal = {
      signalId: 's1',
      signalType: 'FINANCING_NEED',
      content: 'test',
      sourceType: 'INTERACTION',
      status: 'DETECTED',
      detectedAt: '2025-01-01',
    }
    expect(signal.signalType).toBe('FINANCING_NEED')
  })

  it('Interaction interface is usable', () => {
    const interaction: Interaction = {
      interactionId: 'i1',
      caseId: 'oc1',
      type: 'PHONE_CALL',
      direction: 'OUTBOUND',
      channel: 'phone',
      initiator: { participantId: 'p1', role: 'RM', displayName: 'Zhang' },
      outcome: 'COMPLETED',
      occurredAt: '2025-01-01',
    }
    expect(interaction.type).toBe('PHONE_CALL')
  })

  it('Claim interface is usable', () => {
    const claim: Claim = {
      claimId: 'cl1',
      claimType: 'FINANCIAL',
      content: 'test claim',
      status: 'ACTIVE',
    }
    expect(claim.claimType).toBe('FINANCIAL')
  })

  it('TransactionRecord interface is usable', () => {
    const tx: TransactionRecord = {
      transactionId: 't1',
      customerId: 'c1',
      amount: 10000,
      currency: 'CNY',
      transactionType: 'DEPOSIT',
      occurredAt: '2025-01-01',
    }
    expect(tx.amount).toBe(10000)
  })
})

describe('engagement API - API function signatures', () => {
  beforeEach(() => {
    mockGet.mockClear()
    mockPost.mockClear()
  })

  it('fetchCustomers calls GET /customer with params', async () => {
    mockGet.mockResolvedValue({ data: [{ customerId: 'c1' }] })
    const result = await fetchCustomers()
    expect(mockGet).toHaveBeenCalledWith('/customer', expect.objectContaining({ params: expect.any(Object) }))
    expect(result).toEqual([{ customerId: 'c1' }])
  })

  it('fetchCustomer calls GET /customer/:id/operating-view', async () => {
    mockGet.mockResolvedValue({ data: { customer: { customerId: 'c1' } } })
    const result = await fetchCustomer('c1')
    expect(mockGet).toHaveBeenCalledWith('/customer/c1/operating-view')
    expect(result.customerId).toBe('c1')
  })

  it('fetchOperatingView keeps LegalEntity and GroupRelationship from the live payload', async () => {
    mockGet.mockResolvedValue({
      data: {
        customer: { customerId: 'c1', customerName: '企业A' },
        entities: [{ entityId: 'ENT-1', name: '母公司', role: '集团本部/母公司' }],
        groupRelationships: [{ id: 'r1', groupId: 'c1', fromEntityId: 'ENT-1', toEntityId: 'ENT-1' }],
        creditFacilities: [],
      },
    })
    const view = await fetchOperatingView('c1')
    expect(view.entities).toHaveLength(1)
    expect(view.groupRelationships).toHaveLength(1)
    expect(view.customer.customerName).toBe('企业A')
  })

  it('fetchCustomerContext calls multiple GET endpoints', async () => {
    mockGet.mockResolvedValue({ data: { customerId: 'c1' } })
    await fetchCustomerContext('c1')
    // fetchCustomerContext makes multiple calls
    expect(mockGet).toHaveBeenCalled()
  })

  it('fetchCustomerJourneys calls GET /journey with customerId and returns empty on empty data', async () => {
    mockGet.mockClear()
    mockGet.mockResolvedValue({ data: [] })
    const journeys = await fetchCustomerJourneys('c1')
    expect(journeys).toEqual([])
    expect(mockGet).toHaveBeenCalled()
  })

  it('fetchJourney calls GET with journey id', async () => {
    mockGet.mockResolvedValue({ data: { journeyId: 'j1' } })
    await fetchJourney('j1')
    expect(mockGet).toHaveBeenCalled()
  })

  it('fetchJourneyInteractions calls GET with journey id', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await fetchJourneyInteractions('j1')
    expect(mockGet).toHaveBeenCalled()
  })

  it('fetchJourneyClaims calls GET with journey id', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await fetchJourneyClaims('j1')
    expect(mockGet).toHaveBeenCalled()
  })

  it('fetchJourneySignals calls GET with journey id', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await fetchJourneySignals('j1')
    expect(mockGet).toHaveBeenCalled()
  })

  it('fetchReport returns placeholder', async () => {
    const result = await fetchReport('r1')
    expect(result).toBeDefined()
  })

  it('fetchOperatingCases calls GET with customer id', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await fetchOperatingCases('c1')
    expect(mockGet).toHaveBeenCalled()
  })

  it('executePrevisit calls POST /journey/:id/previsit', async () => {
    mockPost.mockResolvedValue({ data: { reportId: 'r1' } })
    await executePrevisit('j1', 'c1', 'oc1', 'test note')
    expect(mockPost).toHaveBeenCalledWith('/journey/j1/previsit', expect.objectContaining({
      customerId: 'c1',
      operatingCaseId: 'oc1',
    }), expect.objectContaining({ timeout: SKILL_HTTP_TIMEOUT_MS }))
  })

  it('executePostvisit calls POST /journey/:id/postvisit', async () => {
    mockPost.mockResolvedValue({ data: { analysisId: 'a1' } })
    await executePostvisit('j1', 'c1', 'oc1', 'interaction notes')
    expect(mockPost).toHaveBeenCalledWith('/journey/j1/postvisit', expect.objectContaining({
      customerId: 'c1',
      operatingCaseId: 'oc1',
    }))
  })

  it('generateOutreachScript calls POST /journey/outreach-script', async () => {
    mockPost.mockResolvedValue({ data: { objective: 'test' } })
    await generateOutreachScript('c1', 'rm1', 'oc1', 'j1', 'PHONE')
    expect(mockPost).toHaveBeenCalledWith('/journey/outreach-script', expect.objectContaining({
      customerId: 'c1',
      channel: 'PHONE',
    }), expect.objectContaining({ timeout: SKILL_HTTP_TIMEOUT_MS }))
  })

  it('generateMeetingScript calls POST /journey/meeting-script', async () => {
    mockPost.mockResolvedValue({ data: { meetingObjective: 'test' } })
    await generateMeetingScript('c1', 'rm1', 'oc1', 'j1')
    expect(mockPost).toHaveBeenCalledWith('/journey/meeting-script', expect.objectContaining({
      customerId: 'c1',
    }), expect.objectContaining({ timeout: SKILL_HTTP_TIMEOUT_MS }))
  })

  it('fetchKycGapProfile calls GET /kyc/:id/gap-profile', async () => {
    mockGet.mockResolvedValue({ data: { profileId: 'p1' } })
    await fetchKycGapProfile('c1')
    expect(mockGet).toHaveBeenCalledWith('/kyc/c1/gap-profile')
  })

  it('fetchOpportunitySignals calls GET /signal/:id', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await fetchOpportunitySignals('c1')
    expect(mockGet).toHaveBeenCalledWith('/signal/c1')
  })

  it('fetchTransactions calls GET /customer/:id/transactions', async () => {
    mockGet.mockResolvedValue({ data: [] })
    await fetchTransactions('c1')
    expect(mockGet).toHaveBeenCalledWith('/customer/c1/transactions')
  })

  it('listInteractions calls GET /api/v1/interactions with optional customerId', async () => {
    mockGet.mockResolvedValue({ data: [{ interactionId: 'int-1', customerId: 'c1', channel: 'PHONE' }] })
    const result = await listInteractions('c1')
    expect(mockGet).toHaveBeenCalledWith('/api/v1/interactions', expect.objectContaining({
      params: { customerId: 'c1' },
    }))
    expect(result[0]?.interactionId).toBe('int-1')
    expect(fetchInteractions).toBe(listInteractions)
  })

  it('fetchAssembledKnowledgeMap calls GET /customer/:id/knowledge-map', async () => {
    mockGet.mockResolvedValue({
      data: {
        customerId: 'c1',
        skillSections: [{ heading: 'KI-009', content: '制造' }],
        assemblyTrace: [],
      },
    })
    const result = await fetchAssembledKnowledgeMap('c1')
    expect(mockGet).toHaveBeenCalledWith(
      '/customer/c1/knowledge-map',
      expect.objectContaining({ timeout: SKILL_HTTP_TIMEOUT_MS }),
    )
    expect(result.skillSections).toHaveLength(1)
    expect(result.assemblyTrace).toEqual([])
  })

  it('preparePrevisit waits 180s for DKWS Skill fan-out', async () => {
    mockPost.mockResolvedValue({
      data: {
        outreachScript: {},
        meetingScript: {},
        previsitReport: {},
        battleCard: {},
        assemblyTrace: [],
        skillSections: [],
      },
    })
    await preparePrevisit('j1', 'c1', 'oc1', '访前调研', 'rm1')
    expect(mockPost).toHaveBeenCalledWith(
      '/journey/j1/prepare-previsit',
      expect.objectContaining({ customerId: 'c1', operatingCaseId: 'oc1' }),
      expect.objectContaining({ timeout: SKILL_HTTP_TIMEOUT_MS }),
    )
  })
})
