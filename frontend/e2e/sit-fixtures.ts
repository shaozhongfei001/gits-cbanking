import type { Page, Route } from '@playwright/test';

/** Shared SIT mocks. These are C0/C2 page fixtures, not V3.2 formal objects. */

export const mockCustomers = [
  {
    customerId: 'cust-001',
    customerName: '测试企业A',
    riskLevel: 'HIGH',
    customerTier: 'STRATEGIC',
    industry: 'MANUFACTURING',
    enterpriseScale: 'LARGE',
    region: '华东',
    registeredCapitalCny: 50000000,
    listedStatus: 'LISTED',
    relationshipSince: '2020-01-01',
    rmName: '张经理',
    managingBranch: '总行营业部',
  },
  {
    customerId: 'cust-002',
    customerName: '测试企业B',
    riskLevel: 'LOW',
    customerTier: 'GROWTH',
    industry: 'TECHNOLOGY',
    enterpriseScale: 'MEDIUM',
    region: '华北',
  },
];

export const mockKyc = {
  profileId: 'kgp-001',
  customerId: 'cust-001',
  asOf: '2026-08-05',
  knownItems: ['企业基本信息', '股权结构'],
  partialKnownItems: ['财务数据'],
  staleItems: ['行业分析'],
  conflictingOrAmbiguousItems: [],
  unknownItems: ['实控人信息'],
  priorityQuestions: ['请补充实控人变更信息'],
};

export const mockSignals = [
  {
    signalId: 'sig-001',
    signalType: 'FINANCING_NEED',
    content: '企业有新增融资需求',
    sourceType: 'INTERACTION',
    status: 'DETECTED',
    detectedAt: '2026-08-01',
  },
];

export const mockCommitments = [
  {
    commitmentId: 'cm-001',
    commitmentType: 'RM_COMMITMENT',
    content: '提供三年期融资结构建议',
    status: 'OPEN',
  },
];

export const mockTasks = [
  {
    taskId: 'tk-001',
    taskType: 'FOLLOW_UP',
    title: '跟进设备清单',
    status: 'PENDING',
  },
];

export const mockOpportunities = [
  {
    opportunityId: 'opp-001',
    customerId: 'cust-001',
    opportunityType: 'FINANCING',
    stage: 'IDENTIFIED',
    description: '设备升级融资',
  },
];

export const mockGates = [
  {
    gateId: 'g-pending',
    gateType: 'E01_EXIT_CONFIRM',
    status: 'PENDING',
    subject: '离场确认',
    createdAt: '2026-08-25T00:00:00Z',
  },
];

export const mockJourney = {
  journeyId: 'jrn-001',
  operatingCaseId: 'case-001',
  customerId: 'cust-001',
  customerName: '测试企业A',
  phase: 'INSIGHT_ANALYSIS',
  startedAt: '2026-08-01',
};

export const mockJourneyInteractions = [
  {
    interactionId: 'int-001',
    caseId: 'case-001',
    journeyId: 'jrn-001',
    type: 'PHONE_CALL',
    direction: 'OUTBOUND',
    channel: '电话',
    initiator: { participantId: 'rm-001', role: 'RM', displayName: '张经理' },
    contentSummary: '了解企业融资需求',
    outcome: 'INFORMATION_GATHERED',
    occurredAt: '2026-08-02',
  },
];

export const mockClaims = [
  {
    claimId: 'clm-001',
    operatingCaseId: 'case-001',
    journeyId: 'jrn-001',
    claimType: 'FINANCING_NEED',
    content: '企业有5000万新增融资需求',
    status: 'CANDIDATE',
    createdAt: '2026-08-02',
  },
];

export const mockListedInteractions = [
  {
    interactionId: 'int-001',
    customerId: 'cust-001',
    channel: 'PHONE',
    summary: '了解企业融资需求',
    interactionDate: '2026-08-02',
  },
];

export const mockEvents = [
  {
    eventId: 'evt-001',
    eventDate: '2026-08-20',
    sourceType: 'NEWS',
    title: '行业产能公告',
    content: '公开新闻摘要（SIT mock）',
    confidence: 'HIGH',
    bankUseAllowed: true,
  },
];

export type ApiMockMode = 'success' | 'error';

function jsonForPath(pathname: string): unknown {
  if (pathname === '/api/v1/engagement/customer') {
    return mockCustomers;
  }
  if (pathname.endsWith('/operating-view')) {
    return {
      customer: mockCustomers[0],
      entities: [
        {
          entityId: 'ENT-GRP-0001',
          name: '测试企业A',
          role: '集团本部/母公司',
          ownership: '100%',
          relationshipStatus: 'ACTIVE',
          evidenceRef: 'EV-SIT-001',
          bankCustomerId: 'cust-001',
        },
        {
          entityId: 'ENT-SUB-0001',
          name: '测试企业A智能制造',
          role: '核心子公司',
          ownership: '60%',
          relationshipStatus: 'ACTIVE',
          evidenceRef: 'EV-SIT-001',
          bankCustomerId: 'cust-002',
        },
      ],
      groupRelationships: [
        {
          id: 'rel-001',
          groupId: 'cust-001',
          fromEntityId: 'ENT-GRP-0001',
          toEntityId: 'ENT-SUB-0001',
          relationshipType: 'OWNS',
          ownershipRatio: 60,
        },
      ],
      creditFacilities: [{ facilityId: 'FAC-SIT-1', borrowerEntity: '测试企业A' }],
    }
  }
  if (pathname.includes('/kyc/') && pathname.endsWith('/gap-profile')) {
    return mockKyc;
  }
  if (pathname.includes('/engagement/signal/')) {
    return mockSignals;
  }
  if (pathname.endsWith('/transactions')) {
    return [];
  }
  if (pathname === '/api/v1/engagement/claims') {
    return mockClaims;
  }
  if (pathname === '/api/v1/commitments/overdue') {
    return [];
  }
  if (pathname === '/api/v1/commitments') {
    return mockCommitments;
  }
  if (pathname === '/api/v1/tasks/overdue') {
    return [];
  }
  if (pathname === '/api/v1/tasks') {
    return mockTasks;
  }
  if (pathname === '/api/v1/opportunities') {
    return mockOpportunities;
  }
  if (pathname === '/api/v1/human-gates') {
    return mockGates;
  }
  if (pathname === '/api/v1/interactions') {
    return mockListedInteractions;
  }
  if (pathname === '/api/v1/external-events/recent' || pathname === '/api/v1/external-events') {
    return mockEvents;
  }
  if (pathname === '/api/v1/product-knowledge/recent') {
    return [];
  }
  if (pathname.endsWith('/knowledge-map') && pathname.includes('/engagement/customer/')) {
    return {
      customerId: 'cust-001',
      skillReportTitle: 'DKWS 知识地图',
      skillExecutiveSummary: 'SIT mock Skill',
      skillSections: [
        { heading: 'KI-009 企业客户基本信息', content: '行业：装备制造（DKWS）' },
        { heading: 'KI-FRONT-006 产品候选组合', content: '供应链金融（DKWS）' },
      ],
      assemblyTrace: [
        { phase: 'retrieve', status: 'ok', message: 'SIT mock assembly', kiId: 'KI-009' },
      ],
    }
  }
  if (pathname.startsWith('/api/v1/engagement/journey/')) {
    // fetchJourney / fetchJourneyReports 共用；reports 由前端 Array.isArray 兜底返回 []
    return mockJourney;
  }
  if (pathname.startsWith('/api/journey/')) {
    return mockJourney;
  }
  if (pathname === '/api/interaction') {
    return mockJourneyInteractions;
  }
  if (pathname.startsWith('/api/claim/')) {
    return mockClaims;
  }
  return [];
}

/** Intercept backend HTTP only. Must not match Vite modules under /src/api/. */
function isBackendApi(url: URL): boolean {
  return url.pathname === '/api' || url.pathname.startsWith('/api/');
}

const mockSupplyChainGraph = {
  requestId: 'SCG-SIT-001',
  customerId: 'cust-001',
  customerName: '测试企业A',
  status: 'ok',
  result: {
    schemaVersion: '1.0',
    buildStatus: 'ok',
    nodes: [
      { id: 'n-core', name: '测试企业A', layer: 'enterprise', type: 'core', dataSource: 'DKWS' },
      { id: 'n-up', name: 'DKWS上游钢厂', layer: 'supplier', type: 'supplier', dataSource: 'DKWS' },
    ],
    edges: [{ source: 'n-up', target: 'n-core', relation: 'purchase' }],
    interpretation: {},
  },
}

const mockProductMatches = [
  { productId: 'PROD-DKWS-1', productName: '供应链金融', matchScore: 0.8, matchReasons: ['DKWS Skill'] },
]

/** Intercept browser API calls. Does not authorize C2/C3 writes. */
export async function installApiMocks(page: Page, mode: ApiMockMode = 'success'): Promise<void> {
  await page.route(url => isBackendApi(url), async (route: Route) => {
    if (mode === 'error') {
      await route.fulfill({ status: 500, body: 'upstream failed' });
      return;
    }
    const pathname = new URL(route.request().url()).pathname;
    const method = route.request().method();
    if (method === 'POST' && pathname.endsWith('/supply-chain-graph')) {
      await route.fulfill({ json: mockSupplyChainGraph });
      return;
    }
    if (method === 'POST' && pathname.endsWith('/product-matching')) {
      await route.fulfill({ json: mockProductMatches });
      return;
    }
    if (method !== 'GET') {
      await route.fulfill({
        status: 403,
        json: { message: 'SIT mock refuses unapproved writes' },
      });
      return;
    }
    await route.fulfill({ json: jsonForPath(pathname) });
  });
}
