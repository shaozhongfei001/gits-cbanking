/**
 * UAT1 路由矩阵（回源 `frontend/src/router/index.ts`，59 条路由逐条登记）。
 *
 * - `real`：使用运行时解析到的真实业务 ID；
 * - `synthetic`：暂无可用种子 ID，用占位 ID 巡检「无效参数下的降级表现」
 *   （不得白屏 / 不得 5xx / 不得未捕获异常）。占位事实在报告中显式标注，不冒充真实数据。
 */

export interface RouteCase {
  id: string;
  title: string;
  build: (ids: RouteIds) => string;
  synthetic?: boolean;
  /** 该页允许不发起后端请求（纯壳层/降级页）。 */
  allowNoApiCall?: boolean;
}

export interface RouteIds {
  customerId: string;
  journeyId: string;
  opportunityId: string;
  eventId: string;
  interactionId: string;
}

export const PLACEHOLDER = {
  signalId: 'UAT-SIGNAL-PLACEHOLDER',
  needId: 'UAT-NEED-PLACEHOLDER',
  proposalId: 'UAT-PROPOSAL-PLACEHOLDER',
  runId: 'UAT-RUN-PLACEHOLDER',
  requestId: 'UAT-SCG-PLACEHOLDER',
  reportId: 'UAT-REPORT-PLACEHOLDER',
};

export const ROUTES: RouteCase[] = [
  // ── 经营域 ──
  { id: 'P01', title: '经营总览', build: () => '/workbench' },
  { id: 'P36', title: '我的任务', build: () => '/commitments' },
  { id: 'P45', title: '经营旅程', build: () => '/engagement' },
  { id: 'P45-enter', title: '进入经营旅程', build: ids => `/engagement/enter?customerId=${ids.customerId}` },
  { id: 'P11', title: '互动工作区', build: ids => `/engagement/workspace/${ids.journeyId}` },

  // ── 客户域 ──
  { id: 'P02', title: '客户组合', build: () => '/accounts' },
  { id: 'P03', title: '客户分层与组合看板', build: () => '/accounts/portfolio' },
  { id: 'P04', title: '客户全景·经营总览', build: ids => `/customers/${ids.customerId}` },
  { id: 'P05', title: '客户档案·集团关系', build: ids => `/customers/${ids.customerId}/group` },
  { id: 'P06', title: '客户档案·业务资金', build: ids => `/customers/${ids.customerId}/funds` },
  { id: 'P07', title: '客户档案·关系人', build: ids => `/customers/${ids.customerId}/parties` },
  { id: 'P08', title: '经营信号', build: () => '/signals' },
  { id: 'P09', title: '经营信号记录', build: () => `/signals/${PLACEHOLDER.signalId}`, synthetic: true },
  { id: 'P10', title: '互动对象主页', build: () => '/engagements' },
  { id: 'P20', title: '需求与机会', build: () => '/needs' },
  { id: 'P21', title: '需求记录', build: () => `/needs/${PLACEHOLDER.needId}`, synthetic: true },
  { id: 'P22', title: '机会与服务计划', build: () => `/needs/${PLACEHOLDER.needId}/plan`, synthetic: true },

  // ── 产品域 ──
  { id: 'PC-01', title: '企业金融产品中心', build: () => '/product-center' },
  { id: 'PC-02', title: '产品中心·指定产品', build: () => '/product-center/PROD-UAT-PLACEHOLDER', synthetic: true },
  { id: 'P38', title: '产品解读与知识', build: () => '/product-knowledge/interpretation' },
  { id: 'P38-map', title: '知识卡与产品适用边界', build: () => '/knowledge-map' },
  { id: 'REC-01', title: '受控推荐工作区', build: () => `/recommendation/${PLACEHOLDER.runId}`, synthetic: true },
  { id: 'SCG-01', title: '供应链图谱报告', build: () => `/supply-chain-report/${PLACEHOLDER.requestId}`, synthetic: true },

  // ── 方案域 ──
  { id: 'P23', title: '建议书对象主页', build: () => '/proposals' },
  { id: 'P24', title: '新建建议书向导', build: () => '/proposals/new' },
  { id: 'P25', title: '建议书记录', build: () => `/proposals/${PLACEHOLDER.proposalId}`, synthetic: true },
  { id: 'P26', title: '建议书模块编辑器', build: () => `/proposals/${PLACEHOLDER.proposalId}/editor`, synthetic: true },
  { id: 'P27', title: '需求—方案—产品映射', build: () => `/proposals/${PLACEHOLDER.proposalId}/map`, synthetic: true },
  { id: 'P28', title: 'AI 内容依据反查', build: () => `/proposals/${PLACEHOLDER.proposalId}/evidence`, synthetic: true },
  { id: 'P29', title: '内部版与客户版对照', build: () => `/proposals/${PLACEHOLDER.proposalId}/project`, synthetic: true },
  { id: 'P30', title: '版本比较与恢复', build: () => `/proposals/${PLACEHOLDER.proposalId}/versions`, synthetic: true },
  { id: 'P31', title: '专家协同记录', build: () => '/collab' },
  { id: 'P32', title: '审批工作中心', build: () => '/approvals' },
  { id: 'P34', title: '账户计划', build: () => '/account-plans' },
  { id: 'P33', title: '对客交付中心', build: () => '/delivery' },
  { id: 'P35', title: '客户价值实现', build: () => '/value' },

  // ── 分析域（KERT） ──
  { id: 'AN-01', title: '经营指标分析', build: () => '/analytics/operating-metrics' },
  { id: 'AN-02', title: '细分客群分析', build: () => '/analytics/segments' },
  { id: 'AN-03', title: '组合条件查询分析', build: () => '/analytics/combo-query' },
  { id: 'AN-04', title: '指标监视器', build: () => '/analytics/monitors' },

  // ── 旅程阶段页 ──
  { id: 'P12', title: '访前目标与信息缺口', build: () => '/engagement/previsit/gaps' },
  { id: 'P13', title: '访前知识证据装配', build: () => '/engagement/previsit/evidence' },
  { id: 'P14', title: '访前包预览', build: () => '/engagement/previsit/pack' },
  { id: 'P15', title: '会中工作区', build: ids => `/in-meeting/${ids.journeyId}` },
  { id: 'P16', title: '会中实时捕获', build: ids => `/in-meeting/${ids.journeyId}/capture` },
  { id: 'P17', title: '离场确认', build: ids => `/in-meeting/${ids.journeyId}/checkout` },
  { id: 'P18', title: '访后事实对账', build: () => '/engagement/postvisit' },
  { id: 'P19', title: 'CRM 受控回写', build: () => '/engagement/crm-writeback' },
  { id: 'JT-01', title: '旅程时间线', build: ids => `/journeys/${ids.journeyId}` },
  { id: 'RP-01', title: '报告详情', build: () => `/reports/${PLACEHOLDER.reportId}`, synthetic: true },

  // ── 治理与移动端 ──
  { id: 'P37', title: 'Claim / Evidence 中心', build: () => '/claims' },
  { id: 'P39', title: '审计与权限', build: () => '/audit-trace' },
  { id: 'P40', title: '服务降级与异常恢复', build: () => '/degrade' },
  { id: 'EV-01', title: '外部事件监控', build: () => '/external-events' },
  { id: 'P41', title: '移动端·今日客户行动', build: () => '/m/today' },
  { id: 'P42', title: '移动端·访前包', build: () => '/m/previsit' },
  { id: 'P43', title: '移动端·会中速记', build: () => '/m/notes' },
  { id: 'P44', title: '移动端·离场确认与任务', build: () => '/m/checkout' },
  { id: 'LG-01', title: '登录页', build: () => '/login', allowNoApiCall: true },
];
