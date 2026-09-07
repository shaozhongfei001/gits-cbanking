import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../api/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { title: '登录', public: true }
    },
    {
      path: '/workbench',
      name: 'Workbench',
      alias: ['/'],
      component: () => import('../views/WorkbenchView.vue'),
      meta: { title: '我的客户经营', pageId: 'P01', objectType: '客户经营应用', objectStatus: '今日' }
    },
    {
      path: '/accounts/portfolio',
      name: 'PortfolioBoard',
      component: () => import('../views/PortfolioBoardView.vue'),
      meta: { title: '客户分层与组合看板', pageId: 'P03', objectType: '客户组合 Portfolio', objectStatus: '分层' }
    },
    {
      path: '/accounts',
      name: 'AccountsHome',
      component: () => import('../views/AccountsView.vue'),
      meta: { title: '客户对象主页', pageId: 'P02', objectType: '客户 Account', objectStatus: '列表' }
    },
    {
      path: '/customers/:id/group',
      name: 'CustomerGroupView',
      component: () => import('../views/CustomerGroupView.vue'),
      meta: { title: '客户记录·集团关系', pageId: 'P05', objectType: '客户 Account', objectStatus: '集团关系' }
    },
    {
      path: '/product-knowledge/interpretation',
      name: 'ProductInterpretation',
      component: () => import('../views/ProductInterpretationView.vue'),
      meta: {
        title: '产品解读·业务场景演示',
        objectType: '产品知识（KERT Release）',
        objectStatus: 'DEMO 演示',
        public: true,
      }
    },
    {
      path: '/supply-chain-report/:requestId',
      name: 'SupplyChainGraphReport',
      component: () => import('../views/SupplyChainGraphReport.vue'),
      meta: { title: '供应链图谱分析报告', objectType: '知识图谱（KERT）', objectStatus: 'Skill' }
    },
    {
      path: '/customers/:id/funds',
      name: 'CustomerFundsView',
      component: () => import('../views/CustomerFundsView.vue'),
      meta: { title: '客户记录·业务资金全景', pageId: 'P06', objectType: '客户 Account', objectStatus: '资金全景' }
    },
    {
      path: '/customers/:id/parties',
      name: 'CustomerPartiesView',
      component: () => import('../views/CustomerPartiesView.vue'),
      meta: { title: '客户记录·关系人情报', pageId: 'P07', objectType: '客户 Account', objectStatus: '关系人' }
    },
    {
      path: '/customers/:id',
      name: 'CustomerOperatingView',
      component: () => import('../views/CustomerOperatingView.vue'),
      meta: { title: '客户记录·经营总览', pageId: 'P04', objectType: '客户 Account', objectStatus: '经营总览' }
    },
    {
      path: '/signals/:id',
      name: 'SignalRecord',
      component: () => import('../views/SignalRecordView.vue'),
      meta: { title: '经营信号记录', pageId: 'P09', objectType: '经营信号 Signal', objectStatus: '记录' }
    },
    {
      path: '/signals',
      name: 'SignalsHome',
      component: () => import('../views/SignalsView.vue'),
      meta: { title: '经营信号对象主页', pageId: 'P08', objectType: '经营信号 Signal', objectStatus: '列表' }
    },
    {
      path: '/engagements',
      name: 'EngagementsHome',
      component: () => import('../views/EngagementsView.vue'),
      meta: { title: '互动对象主页', pageId: 'P10', objectType: '互动 Interaction', objectStatus: '列表' }
    },
    {
      path: '/journeys/:id',
      name: 'JourneyTimeline',
      component: () => import('../views/JourneyTimeline.vue'),
      meta: { title: '旅程时间线' }
    },
    {
      path: '/reports/:id',
      name: 'ReportDetail',
      component: () => import('../views/ReportDetail.vue'),
      meta: { title: '报告详情' }
    },
    {
      path: '/engagement/previsit/gaps',
      name: 'PrevisitGaps',
      component: () => import('../views/PrevisitGapsView.vue'),
      meta: { title: '访前目标与信息缺口', pageId: 'P12', objectType: '互动 Interaction', objectStatus: '访前缺口' }
    },
    {
      path: '/engagement/previsit/evidence',
      name: 'PrevisitEvidence',
      component: () => import('../views/PrevisitEvidenceView.vue'),
      meta: { title: '访前知识证据装配', pageId: 'P13', objectType: '互动 Interaction', objectStatus: '证据装配' }
    },
    {
      path: '/engagement/previsit/pack',
      name: 'PrevisitPack',
      component: () => import('../views/PrevisitPackView.vue'),
      meta: { title: '访前包预览', pageId: 'P14', objectType: '互动 Interaction', objectStatus: '访前包' }
    },
    {
      path: '/engagement/postvisit',
      name: 'PostvisitReconcile',
      component: () => import('../views/PostvisitReconcileView.vue'),
      meta: { title: '访后事实对账', pageId: 'P18', objectType: '互动 Interaction', objectStatus: '访后对账' }
    },
    {
      path: '/engagement/crm-writeback',
      name: 'CrmWriteback',
      component: () => import('../views/CrmWritebackView.vue'),
      meta: { title: 'CRM 受控回写', pageId: 'P19', objectType: '互动 Interaction', objectStatus: '写回确认' }
    },
    {
      path: '/engagement',
      name: 'EngagementWorkspace',
      component: () => import('../views/EngagementWorkspace.vue'),
      meta: { title: '互动记录·访前路径', pageId: 'P11', objectType: '互动 Interaction', objectStatus: '访前路径' }
    },
    {
      path: '/knowledge-map',
      name: 'KnowledgeMapView',
      component: () => import('../views/KnowledgeMapView.vue'),
      meta: { title: '知识卡与产品适用边界', pageId: 'P38', objectType: '知识要素 KE（只读）', objectStatus: '只读' }
    },
    {
      path: '/recommendation/:runId',
      name: 'ProductRecommendationWorkspace',
      component: () => import('../views/ProductRecommendationWorkspace.vue'),
      meta: { title: '产品推荐三段式工作区', objectType: '产品推荐 ProductRecommendationRun', objectStatus: '三段式' }
    },
    {
      path: '/needs/:id/plan',
      name: 'NeedPlan',
      component: () => import('../views/NeedPlanView.vue'),
      meta: { title: '机会与服务计划记录', pageId: 'P22', objectType: '非正式 Need（C2 降级）', objectStatus: '只读派生' }
    },
    {
      path: '/needs/:id',
      name: 'NeedRecord',
      component: () => import('../views/NeedRecordView.vue'),
      meta: { title: '需求记录', pageId: 'P21', objectType: '非正式 Need（C2 降级）', objectStatus: '记录' }
    },
    {
      path: '/needs',
      name: 'NeedsHome',
      component: () => import('../views/NeedsView.vue'),
      meta: { title: '需求与机会对象主页', pageId: 'P20', objectType: '非正式 Need（C2 降级）', objectStatus: '列表' }
    },
    {
      path: '/proposals/new',
      name: 'ProposalWizard',
      component: () => import('../views/ProposalWizardView.vue'),
      meta: { title: '新建建议书向导', pageId: 'P24', objectType: '非正式建议书（C2 降级）', objectStatus: '向导' }
    },
    {
      path: '/proposals/:id/editor',
      name: 'ProposalEditor',
      component: () => import('../views/ProposalEditorView.vue'),
      meta: { title: '建议书模块编辑器', pageId: 'P26', objectType: '非正式建议书（C2 降级）', objectStatus: '只读壳层' }
    },
    {
      path: '/proposals/:id/map',
      name: 'ProposalMap',
      component: () => import('../views/ProposalMapView.vue'),
      meta: { title: '需求—方案—产品映射', pageId: 'P27', objectType: '非正式建议书（C2 降级）', objectStatus: '只读壳层' }
    },
    {
      path: '/proposals/:id/evidence',
      name: 'ProposalEvidence',
      component: () => import('../views/ProposalEvidenceView.vue'),
      meta: { title: 'AI 内容依据反查', pageId: 'P28', objectType: '非正式建议书（C2 降级）', objectStatus: '只读壳层' }
    },
    {
      path: '/proposals/:id/project',
      name: 'ProposalProject',
      component: () => import('../views/ProposalProjectView.vue'),
      meta: { title: '内部版与客户版对照', pageId: 'P29', objectType: '非正式建议书（C2 降级）', objectStatus: '只读壳层' }
    },
    {
      path: '/proposals/:id/versions',
      name: 'ProposalVersions',
      component: () => import('../views/ProposalVersionsView.vue'),
      meta: { title: '版本比较与恢复', pageId: 'P30', objectType: '非正式建议书（C2 降级）', objectStatus: '只读壳层' }
    },
    {
      path: '/proposals/:id',
      name: 'ProposalRecord',
      component: () => import('../views/ProposalRecordView.vue'),
      meta: { title: '建议书记录', pageId: 'P25', objectType: '非正式建议书（C2 降级）', objectStatus: '阶段机未授权' }
    },
    {
      path: '/proposals',
      name: 'ProposalsHome',
      component: () => import('../views/ProposalsView.vue'),
      meta: { title: '建议书对象主页', pageId: 'P23', objectType: '非正式建议书（C2 降级）', objectStatus: '列表' }
    },
    {
      path: '/commitments',
      name: 'CommitmentDashboard',
      component: () => import('../views/CommitmentDashboard.vue'),
      meta: { title: '任务与承诺中心', pageId: 'P36', objectType: '任务与承诺 Commitment/Task', objectStatus: '中心' }
    },
    {
      path: '/collab',
      name: 'CollabHome',
      component: () => import('../views/CollabView.vue'),
      meta: { title: '专家协同记录', pageId: 'P31', objectType: '非正式专家协同（C2 降级）', objectStatus: '无合同对象' }
    },
    {
      path: '/approvals',
      name: 'ApprovalsHome',
      component: () => import('../views/ApprovalsView.vue'),
      meta: { title: '审批工作中心', pageId: 'P32', objectType: '人工门禁 HumanGate', objectStatus: '工作中心' }
    },
    {
      path: '/delivery',
      name: 'DeliveryHome',
      component: () => import('../views/DeliveryCenterView.vue'),
      meta: { title: '对客交付中心', pageId: 'P33', objectType: '非正式交付包（C2 降级）', objectStatus: '无 DeliveryPackage' }
    },
    {
      path: '/account-plans',
      name: 'AccountPlansHome',
      component: () => import('../views/AccountPlansView.vue'),
      meta: { title: '30/90/180 天账户计划', pageId: 'P34', objectType: '非正式账户计划（C2 降级）', objectStatus: '无 AccountPlan' }
    },
    {
      path: '/value',
      name: 'ValueHome',
      component: () => import('../views/ValueRealizationView.vue'),
      meta: { title: '客户价值实现', pageId: 'P35', objectType: '非正式价值口径（C2 降级）', objectStatus: '无价值口径' }
    },
    {
      path: '/claims',
      name: 'ClaimsHome',
      component: () => import('../views/ClaimsView.vue'),
      meta: { title: 'Claim / Evidence 中心', pageId: 'P37', objectType: 'Claim', objectStatus: '只读' }
    },
    {
      path: '/degrade',
      name: 'DegradeHome',
      component: () => import('../views/DegradeRecoveryView.vue'),
      meta: { title: '服务降级与异常恢复', pageId: 'P40', objectType: '服务降级（C2 离线包禁用）', objectStatus: '在线探测' }
    },
    {
      path: '/m/today',
      name: 'MobileToday',
      component: () => import('../views/MobileTodayView.vue'),
      meta: { title: '移动端·今日客户行动', pageId: 'P41', objectType: '非正式今日行动（C2 降级）', objectStatus: '在线只读' }
    },
    {
      path: '/m/previsit',
      name: 'MobilePrevisit',
      component: () => import('../views/MobilePrevisitView.vue'),
      meta: { title: '移动端·访前包', pageId: 'P42', objectType: '非正式访前包（C2 降级，无离线包）', objectStatus: '离线包未授权' }
    },
    {
      path: '/m/notes',
      name: 'MobileNotes',
      component: () => import('../views/MobileNotesView.vue'),
      meta: { title: '移动端·会中速记', pageId: 'P43', objectType: '非正式会中速记（C2 降级，非正式 Claim）', objectStatus: '草稿非正式' }
    },
    {
      path: '/m/checkout',
      name: 'MobileCheckout',
      component: () => import('../views/MobileCheckoutView.vue'),
      meta: { title: '移动端·离场确认与任务', pageId: 'P44', objectType: '离场确认（移动端 C2；仅复用 E01）', objectStatus: '在线门禁' }
    },
    {
      path: '/external-events',
      name: 'ExternalEventMonitor',
      component: () => import('../views/ExternalEventMonitor.vue'),
      meta: { title: '外部事件监控' }
    },
    {
      path: '/in-meeting/:id/capture',
      name: 'MeetingCapture',
      component: () => import('../views/MeetingCaptureView.vue'),
      meta: { title: '会中实时捕获', pageId: 'P16', objectType: '互动 Interaction', objectStatus: '实时捕获' }
    },
    {
      path: '/in-meeting/:id/checkout',
      name: 'MeetingCheckout',
      component: () => import('../views/MeetingCheckoutView.vue'),
      meta: { title: '离场确认', pageId: 'P17', objectType: '互动 Interaction', objectStatus: '离场确认' }
    },
    {
      path: '/in-meeting/:id?',
      name: 'InMeetingAssistant',
      component: () => import('../views/InMeetingAssistant.vue'),
      meta: { title: '会中工作区', pageId: 'P15', objectType: '互动 Interaction', objectStatus: '会中' }
    },
    {
      path: '/audit-trace',
      name: 'AuditTrace',
      component: () => import('../views/AuditTraceView.vue'),
      meta: { title: '审计与权限', pageId: 'P39', objectType: '审计追踪 AuditTrace', objectStatus: '查询' }
    }
  ]
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'GITS Bank'} - GITS Bank`

  // 公开页面不需要认证
  if (to.meta.public) {
    next()
    return
  }

  // 开发模式跳过认证（后端 api-key 为空时认证已关闭）
  if (import.meta.env.DEV) {
    next()
    return
  }

  // 未认证时跳转登录页
  if (!isAuthenticated()) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  next()
})

// 监听401事件，跳转登录页
window.addEventListener('auth:unauthorized', () => {
  router.push({ name: 'Login' })
})

export default router
