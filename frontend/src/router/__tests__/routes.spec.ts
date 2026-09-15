import { describe, it, expect } from 'vitest'
import router from '../index'

const PRESERVED_PATHS = [
  '/',
  '/workbench',
  '/accounts',
  '/accounts/portfolio',
  '/customers/c1',
  '/engagement',
  '/external-events',
  '/commitments',
  '/knowledge-map',
  '/in-meeting',
  '/audit-trace',
]

describe('P30 experience shell routes', () => {
  it('registers workbench, accounts and portfolio while keeping deep links', () => {
    const paths = router.getRoutes().map(route => route.path)
    expect(paths).toContain('/workbench')
    expect(paths).toContain('/accounts')
    expect(paths).toContain('/accounts/portfolio')
    expect(paths).toContain('/engagement')
    expect(paths).toContain('/customers/:id')
    expect(paths).toContain('/commitments')
    expect(paths).toContain('/knowledge-map')
    expect(router.hasRoute('Workbench')).toBe(true)
    const pathsIncludeRoot = router.getRoutes().some(route => route.path === '/' || route.aliasOf?.path === '/workbench')
    expect(pathsIncludeRoot || router.resolve('/').name === 'Workbench').toBe(true)
    expect(router.resolve('/').name).toBe('Workbench')
    expect(router.resolve('/workbench').name).toBe('Workbench')
  })
})

describe('P31 customer slice routes', () => {
  it('registers P04-P10 without colliding with /engagement', () => {
    expect(router.resolve('/customers/c1').name).toBe('CustomerOperatingView')
    expect(router.resolve('/customers/c1').meta.pageId).toBe('P04')
    expect(router.resolve('/customers/c1').meta.objectType).toBe('客户 Account')
    expect(router.resolve('/customers/c1/group').name).toBe('CustomerGroupView')
    expect(router.resolve('/customers/c1/group').meta.pageId).toBe('P05')
    expect(router.resolve('/customers/c1/funds').name).toBe('CustomerFundsView')
    expect(router.resolve('/customers/c1/funds').meta.pageId).toBe('P06')
    expect(router.resolve('/customers/c1/parties').name).toBe('CustomerPartiesView')
    expect(router.resolve('/customers/c1/parties').meta.pageId).toBe('P07')
    expect(router.resolve('/signals').name).toBe('SignalsHome')
    expect(router.resolve('/signals').meta.pageId).toBe('P08')
    expect(router.resolve('/signals/sig-1').name).toBe('SignalRecord')
    expect(router.resolve('/signals/sig-1').meta.pageId).toBe('P09')
    expect(router.resolve('/engagements').name).toBe('EngagementsHome')
    expect(router.resolve('/engagements').meta.pageId).toBe('P10')
    expect(router.resolve('/engagement').name).toBe('EngagementWorkspace')
    expect(router.resolve('/engagement').meta.pageId).not.toBe('P10')
  })

  it('keeps P30 deep links from 404', () => {
    for (const path of PRESERVED_PATHS) {
      const resolved = router.resolve(path)
      expect(resolved.matched.length, path).toBeGreaterThan(0)
      expect(String(resolved.name || '')).not.toBe('')
    }
  })
})

describe('P32 engagement slice routes', () => {
  it('registers P11-P19 without covering P10 /engagements', () => {
    expect(router.resolve('/engagement').name).toBe('EngagementWorkspace')
    expect(router.resolve('/engagement').meta.pageId).toBe('P11')
    expect(router.resolve('/engagements').name).toBe('EngagementsHome')
    expect(router.resolve('/engagements').meta.pageId).toBe('P10')
    expect(router.resolve('/engagement/previsit/gaps').name).toBe('PrevisitGaps')
    expect(router.resolve('/engagement/previsit/gaps').meta.pageId).toBe('P12')
    expect(router.resolve('/engagement/previsit/evidence').name).toBe('PrevisitEvidence')
    expect(router.resolve('/engagement/previsit/evidence').meta.pageId).toBe('P13')
    expect(router.resolve('/engagement/previsit/pack').name).toBe('PrevisitPack')
    expect(router.resolve('/engagement/previsit/pack').meta.pageId).toBe('P14')
    expect(router.resolve('/in-meeting').name).toBe('InMeetingAssistant')
    expect(router.resolve('/in-meeting').meta.pageId).toBe('P15')
    expect(router.resolve('/in-meeting/j1').name).toBe('InMeetingAssistant')
    expect(router.resolve('/in-meeting/j1').meta.pageId).toBe('P15')
    expect(router.resolve('/in-meeting/j1/capture').name).toBe('MeetingCapture')
    expect(router.resolve('/in-meeting/j1/capture').meta.pageId).toBe('P16')
    expect(router.resolve('/in-meeting/j1/checkout').name).toBe('MeetingCheckout')
    expect(router.resolve('/in-meeting/j1/checkout').meta.pageId).toBe('P17')
    expect(router.resolve('/engagement/postvisit').name).toBe('PostvisitReconcile')
    expect(router.resolve('/engagement/postvisit').meta.pageId).toBe('P18')
    expect(router.resolve('/engagement/crm-writeback').name).toBe('CrmWriteback')
    expect(router.resolve('/engagement/crm-writeback').meta.pageId).toBe('P19')
  })

  it('keeps P10, customer, signal, journey, workbench and accounts deep links', () => {
    expect(router.resolve('/engagements').name).toBe('EngagementsHome')
    expect(router.resolve('/customers/c1').name).toBe('CustomerOperatingView')
    expect(router.resolve('/signals').name).toBe('SignalsHome')
    expect(router.resolve('/journeys/j1').name).toBe('JourneyTimeline')
    expect(router.resolve('/workbench').name).toBe('Workbench')
    expect(router.resolve('/accounts').name).toBe('AccountsHome')
    expect(router.resolve('/engagement').name).toBe('EngagementWorkspace')
    expect(router.resolve('/in-meeting').name).toBe('InMeetingAssistant')
  })
})

describe('P33 need degrade and P36 commitment routes', () => {
  it('registers P20-P22 C2 needs and keeps P36 /commitments', () => {
    expect(router.resolve('/needs').name).toBe('NeedsHome')
    expect(router.resolve('/needs').meta.pageId).toBe('P20')
    expect(router.resolve('/needs').meta.objectType).toBe('非正式 Need（C2 降级）')
    expect(router.resolve('/needs/sig-1').name).toBe('NeedRecord')
    expect(router.resolve('/needs/sig-1').meta.pageId).toBe('P21')
    expect(router.resolve('/needs/sig-1/plan').name).toBe('NeedPlan')
    expect(router.resolve('/needs/sig-1/plan').meta.pageId).toBe('P22')
    expect(router.resolve('/commitments').name).toBe('CommitmentDashboard')
    expect(router.resolve('/commitments').meta.pageId).toBe('P36')
  })

  it('keeps commitments, workbench, signals and engagement deep links', () => {
    expect(router.resolve('/commitments').name).toBe('CommitmentDashboard')
    expect(router.resolve('/workbench').name).toBe('Workbench')
    expect(router.resolve('/signals').name).toBe('SignalsHome')
    expect(router.resolve('/engagement').name).toBe('EngagementWorkspace')
    expect(router.resolve('/engagements').name).toBe('EngagementsHome')
  })
})

describe('P34 proposal degrade routes', () => {
  it('registers P23-P30 with /proposals/new before /proposals/:id', () => {
    const registered = router.options.routes.map(route => route.path)
    const newIdx = registered.indexOf('/proposals/new')
    const idIdx = registered.indexOf('/proposals/:id')
    expect(newIdx).toBeGreaterThanOrEqual(0)
    expect(idIdx).toBeGreaterThan(newIdx)

    expect(router.resolve('/proposals').name).toBe('ProposalsHome')
    expect(router.resolve('/proposals').meta.pageId).toBe('P23')
    expect(router.resolve('/proposals').meta.objectType).toBe('非正式建议书（C2 降级）')

    expect(router.resolve('/proposals/new').name).toBe('ProposalWizard')
    expect(router.resolve('/proposals/new').meta.pageId).toBe('P24')
    expect(router.resolve('/proposals/new').params.id).toBeUndefined()

    expect(router.resolve('/proposals/ph-1').name).toBe('ProposalRecord')
    expect(router.resolve('/proposals/ph-1').meta.pageId).toBe('P25')
    expect(router.resolve('/proposals/ph-1').params.id).toBe('ph-1')
    expect(router.resolve('/proposals/ph-1/editor').name).toBe('ProposalEditor')
    expect(router.resolve('/proposals/ph-1/editor').meta.pageId).toBe('P26')
    expect(router.resolve('/proposals/ph-1/map').name).toBe('ProposalMap')
    expect(router.resolve('/proposals/ph-1/map').meta.pageId).toBe('P27')
    expect(router.resolve('/proposals/ph-1/evidence').name).toBe('ProposalEvidence')
    expect(router.resolve('/proposals/ph-1/evidence').meta.pageId).toBe('P28')
    expect(router.resolve('/proposals/ph-1/project').name).toBe('ProposalProject')
    expect(router.resolve('/proposals/ph-1/project').meta.pageId).toBe('P29')
    expect(router.resolve('/proposals/ph-1/versions').name).toBe('ProposalVersions')
    expect(router.resolve('/proposals/ph-1/versions').meta.pageId).toBe('P30')
  })

  it('keeps needs, commitments, engagement, engagements, workbench and signals deep links', () => {
    expect(router.resolve('/needs').name).toBe('NeedsHome')
    expect(router.resolve('/commitments').name).toBe('CommitmentDashboard')
    expect(router.resolve('/engagement').name).toBe('EngagementWorkspace')
    expect(router.resolve('/engagements').name).toBe('EngagementsHome')
    expect(router.resolve('/workbench').name).toBe('Workbench')
    expect(router.resolve('/signals').name).toBe('SignalsHome')
  })
})

describe('P35 governance C0/C2 routes', () => {
  it('registers P31-P40 except keeping P36 /commitments', () => {
    expect(router.resolve('/collab').name).toBe('CollabHome')
    expect(router.resolve('/collab').meta.pageId).toBe('P31')
    expect(router.resolve('/approvals').name).toBe('ApprovalsHome')
    expect(router.resolve('/approvals').meta.pageId).toBe('P32')
    expect(router.resolve('/delivery').name).toBe('DeliveryHome')
    expect(router.resolve('/delivery').meta.pageId).toBe('P33')
    expect(router.resolve('/account-plans').name).toBe('AccountPlansHome')
    expect(router.resolve('/account-plans').meta.pageId).toBe('P34')
    expect(router.resolve('/value').name).toBe('ValueHome')
    expect(router.resolve('/value').meta.pageId).toBe('P35')
    expect(router.resolve('/commitments').name).toBe('CommitmentDashboard')
    expect(router.resolve('/commitments').meta.pageId).toBe('P36')
    expect(router.resolve('/claims').name).toBe('ClaimsHome')
    expect(router.resolve('/claims').meta.pageId).toBe('P37')
    expect(router.resolve('/knowledge-map').name).toBe('KnowledgeMapView')
    expect(router.resolve('/knowledge-map').meta.pageId).toBe('P38')
    expect(router.resolve('/audit-trace').name).toBe('AuditTrace')
    expect(router.resolve('/audit-trace').meta.pageId).toBe('P39')
    expect(router.resolve('/degrade').name).toBe('DegradeHome')
    expect(router.resolve('/degrade').meta.pageId).toBe('P40')
  })

  it('keeps proposals, needs, commitments, engagement, engagements, workbench, signals, knowledge-map and audit-trace', () => {
    expect(router.resolve('/proposals').name).toBe('ProposalsHome')
    expect(router.resolve('/needs').name).toBe('NeedsHome')
    expect(router.resolve('/commitments').name).toBe('CommitmentDashboard')
    expect(router.resolve('/commitments').meta.pageId).toBe('P36')
    expect(router.resolve('/engagement').name).toBe('EngagementWorkspace')
    expect(router.resolve('/engagements').name).toBe('EngagementsHome')
    expect(router.resolve('/workbench').name).toBe('Workbench')
    expect(router.resolve('/signals').name).toBe('SignalsHome')
    expect(router.resolve('/knowledge-map').name).toBe('KnowledgeMapView')
    expect(router.resolve('/audit-trace').name).toBe('AuditTrace')
  })
})

describe('P36 loop mobile degrade routes (pages P41-P44)', () => {
  it('registers /m/today /m/previsit /m/notes /m/checkout without changing /commitments', () => {
    expect(router.resolve('/m/today').name).toBe('MobileToday')
    expect(router.resolve('/m/today').meta.pageId).toBe('P41')
    expect(router.resolve('/m/previsit').name).toBe('MobilePrevisit')
    expect(router.resolve('/m/previsit').meta.pageId).toBe('P42')
    expect(router.resolve('/m/notes').name).toBe('MobileNotes')
    expect(router.resolve('/m/notes').meta.pageId).toBe('P43')
    expect(router.resolve('/m/checkout').name).toBe('MobileCheckout')
    expect(router.resolve('/m/checkout').meta.pageId).toBe('P44')
    expect(router.resolve('/commitments').name).toBe('CommitmentDashboard')
    expect(router.resolve('/commitments').meta.pageId).toBe('P36')
    expect(router.resolve('/commitments').path).toBe('/commitments')
  })

  it('keeps workbench, engagement, in-meeting, commitments, approvals and claims deep links', () => {
    expect(router.resolve('/workbench').name).toBe('Workbench')
    expect(router.resolve('/engagement').name).toBe('EngagementWorkspace')
    expect(router.resolve('/in-meeting').name).toBe('InMeetingAssistant')
    expect(router.resolve('/commitments').name).toBe('CommitmentDashboard')
    expect(router.resolve('/commitments').meta.pageId).toBe('P36')
    expect(router.resolve('/approvals').name).toBe('ApprovalsHome')
    expect(router.resolve('/claims').name).toBe('ClaimsHome')
  })
})

