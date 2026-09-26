import axios from 'axios'
import { getApiKey, clearApiKey } from './auth'

// KERT 对公经营分析服务（CCRM-BA 落地，Owner 指令 2026-09-22）。
// dev 经 vite 代理 /kert-api → KERT_API（默认 127.0.0.1:8107）；生产经网关同路径。
const analyticsApi = axios.create({
  baseURL: '/kert-api/v1/analytics',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

analyticsApi.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-KEY'] = apiKey
  }
  return config
})

analyticsApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearApiKey()
      window.dispatchEvent(new CustomEvent('auth:unauthorized'))
    }
    return Promise.reject(error)
  }
)

// ===================== 类型（对齐 KERT operational_analytics） =====================

export type AnalyticsRow = Record<string, string | number | null>

export interface AnalyticsDimension {
  dimType: string
  label: string
  members: string[]
}

export interface AnalyticsOrg {
  orgId: string
  orgName: string
  orgLevel: number
  orgPath: string
}

export interface AnalyticsMetrics {
  screen: string
  screenLabel: string
  bizType: string | null
  dim: string
  orgId: string
  period: string
  rowAxis: 'ORG' | 'DIM'
  rows: AnalyticsRow[]
  alerts?: Array<{ dimValue: string; metric: string; direction: 'up' | 'down'; mom: number }>
}

export interface AnalyticsTrend {
  dimValue: string
  metric: string
  points: Array<{ period: string; value: number | null }>
}

export interface ComboQueryFilters {
  orgId?: string
  period?: string
  custName?: string
  custId?: string
  creditRating?: string[]
  entScale?: string[]
  industryCodes?: string[]
  custType?: string[]
  custCategory?: string[]
  amountRules?: Array<{ metric: string; op: '=' | '>' | '>=' | '<' | '<='; value: number }>
  isKeyCustHq?: boolean
  isKeyCustBranch?: boolean
  isStrategyCust?: boolean
  isSme?: boolean
}

export interface ComboQueryResult {
  rows: AnalyticsRow[]
  total: number
  page: { number: number; size: number }
  period: string
  orgId: string
}

// ===================== 屏幕列注册表（与 KERT 10 屏口径一致） =====================

export interface ScreenColumn {
  key: string
  label: string
  kind: 'dim' | 'value' | 'mom' | 'ytd' | 'pct' | 'sharePct' | 'count'
}

export interface ScreenDef {
  id: string
  label: string
  dims: string[]
  primary: string
  columns: ScreenColumn[]
  /** 行轴：ORG=行是机构（经营指标 4 屏），DIM=行是维度成员（默认）。 */
  rowAxis?: 'ORG' | 'DIM'
}

const mom = (key: string, label: string): ScreenColumn => ({ key: `${key}Mom`, label, kind: 'mom' })
const ytd = (key: string, label: string): ScreenColumn => ({ key: `${key}Ytd`, label, kind: 'ytd' })
const val = (key: string, label: string): ScreenColumn => ({ key, label, kind: 'value' })
const cnt = (key: string, label: string): ScreenColumn => ({ key, label, kind: 'count' })
const pctv = (key: string, label: string): ScreenColumn => ({ key, label, kind: 'pct' })
const share = (key: string, label: string): ScreenColumn => ({ key: `${key}Share`, label, kind: 'sharePct' })
const shareMom = (key: string, label: string): ScreenColumn => ({ key: `${key}ShareMom`, label, kind: 'mom' })
const shareYtd = (key: string, label: string): ScreenColumn => ({ key: `${key}ShareYtd`, label, kind: 'ytd' })

/** 全部可选分布维度（经营指标 4 屏作过滤条件；其余屏作行轴） */
export const ALL_DIMS = [
  'INDUSTRY', 'CREDIT_RATING', 'ENT_SCALE', 'CUST_TYPE', 'CUST_CATEGORY',
  'DEP_BAND', 'LOAN_BAND', 'SETTLE_BAND', 'PROFIT_BAND', 'KEY_CUST', 'SME',
] as const

export const MONITOR_DIMS = ['INDUSTRY', 'CUST_TYPE', 'CUST_CATEGORY'] as const

export const DIM_LABELS: Record<string, string> = {
  INDUSTRY: '行业', CREDIT_RATING: '信用等级', ENT_SCALE: '企业规模',
  CUST_TYPE: '客户类型', CUST_CATEGORY: '客户类别', DEP_BAND: '存款余额分段',
  LOAN_BAND: '贷款余额分段', SETTLE_BAND: '结算量分段', PROFIT_BAND: '利润贡献分段',
  KEY_CUST: '重点客户', SME: '中小企业',
}

/** 经营指标分析 4 屏（行=机构，原文口径） */
export const OPERATING_SCREENS: ScreenDef[] = [
  {
    id: 'operating-customer', rowAxis: 'ORG', label: '客户指标分析', dims: [...ALL_DIMS], primary: 'custCnt',
    columns: [
      { key: 'dimValue', label: '机构名称', kind: 'dim' },
      cnt('custCnt', '客户数'), mom('custCnt', '比上月'), ytd('custCnt', '比年初'),
      cnt('custCntNew', '新增客户数'),
      val('incomeTotal', '客户收入总额'), val('incomeSme', '小企业贡献度'), val('incomeNonSme', '非小企业贡献度'),
      cnt('acctCnt', '账户总数'), cnt('acctClosedCnt', '销户数'), val('acctClosedBal', '销户余额'),
      cnt('custCntInactive', '不动户数'),
    ],
  },
  {
    id: 'operating-overview', rowAxis: 'ORG', label: '业务概况分析', dims: [...ALL_DIMS], primary: 'depBal',
    columns: [
      { key: 'dimValue', label: '机构名称', kind: 'dim' },
      val('depBal', '一般存款余额'), mom('depBal', '比上月'), ytd('depBal', '比年初'),
      val('loanBal', '非贴现贷款余额'), mom('loanBal', '比上月'), ytd('loanBal', '比年初'),
      val('feeTotal', '中间业务收入'), mom('feeTotal', '比上月'),
    ],
  },
  {
    id: 'operating-profit', rowAxis: 'ORG', label: '利润贡献分析', dims: [...ALL_DIMS], primary: 'profitTotal',
    columns: [
      { key: 'dimValue', label: '机构名称', kind: 'dim' },
      val('profitTotal', '综合利润贡献'), share('profitTotal', '占比'), mom('profitTotal', '比上月'), ytd('profitTotal', '比年初'),
      val('profitDep', '存款利润贡献'), share('profitDep', '占比'), mom('profitDep', '比上月'), ytd('profitDep', '比年初'),
      val('profitLoan', '贷款利润贡献'), share('profitLoan', '占比'), mom('profitLoan', '比上月'), ytd('profitLoan', '比年初'),
      val('profitFee', '中收利润贡献'), share('profitFee', '占比'), mom('profitFee', '比上月'), ytd('profitFee', '比年初'),
    ],
  },
  {
    id: 'operating-risk', rowAxis: 'ORG', label: '风险指标分析', dims: [...ALL_DIMS], primary: 'nplBal',
    columns: [
      { key: 'dimValue', label: '机构名称', kind: 'dim' },
      pctv('roa', '资产利润率'), pctv('roe', '资本利润率'),
      pctv('nplRatio', '不良贷款率'), mom('nplRatio', '比上月'),
      val('nplBal', '不良贷款金额'), mom('nplBal', '比上月'), ytd('nplBal', '比年初'),
    ],
  },
]

/** 细分客群分析 2 屏 + segment-business 4 tab（行=维度成员） */
export const SEGMENT_SCREENS: ScreenDef[] = [
  {
    id: 'segment-distribution', label: '客户分布特征分析', dims: [...ALL_DIMS], primary: 'custCnt',
    columns: [
      { key: 'dimValue', label: '维度成员', kind: 'dim' },
      cnt('custCnt', '客户数'), share('custCnt', '占比'), mom('custCnt', '比上月'), ytd('custCnt', '比年初'),
      val('avgDep', '平均存款余额'), val('avgLoan', '平均贷款余额'),
      val('avgSett', '平均结算金额'), val('avgProfit', '平均利润贡献'),
      val('avgProd', '平均持有产品数'), cnt('basicCnt', '基本户数'), cnt('acctCnt', '账户数'),
    ],
  },
]

export const SEGMENT_BIZ_TABS: Array<{ bizType: 'DEPOSIT' | 'LOAN' | 'FEE' | 'SETTLEMENT'; label: string; def: ScreenDef }> = [
  {
    bizType: 'DEPOSIT', label: '存款业务',
    def: {
      id: 'segment-business', label: '存款业务', dims: ['INDUSTRY', 'CREDIT_RATING', 'ENT_SCALE'], primary: 'depBal',
      columns: [
        { key: 'dimValue', label: '行业名称', kind: 'dim' },
        val('depBal', '存款余额'), mom('depBal', '比上月'), ytd('depBal', '比年初'),
        val('depAvgDay', '存款日均余额'), mom('depAvgDay', '比上月'), ytd('depAvgDay', '比年初'),
        val('depDemandBal', '活期余额'), mom('depDemandBal', '比上月'),
        val('depTimeBal', '定期余额'), mom('depTimeBal', '比上月'),
        val('depMarginBal', '保证金存款余额'), mom('depMarginBal', '比上月'),
        val('depDueMtd', '本月到期存款'), val('depDueNext', '下月到期存款'),
      ],
    },
  },
  {
    bizType: 'LOAN', label: '贷款业务',
    def: {
      id: 'segment-business', label: '贷款业务', dims: ['INDUSTRY', 'CREDIT_RATING', 'ENT_SCALE'], primary: 'loanBal',
      columns: [
        { key: 'dimValue', label: '行业名称', kind: 'dim' },
        val('loanBal', '贷款余额'), share('loanBal', '占比'), mom('loanBal', '比上月'), ytd('loanBal', '比年初'),
        val('loanAvgDay', '贷款日均余额'), mom('loanAvgDay', '比上月'),
        val('loanDisbMtd', '本月发放贷款金额'), mom('loanDisbMtd', '比上月'),
        val('loanDueMtd', '本月到期贷款金额'), mom('loanDueMtd', '比上月'),
        val('loanClsSubstandard', '次级贷款余额'), mom('loanClsSubstandard', '比上月'),
        val('loanClsDoubtful', '可疑贷款余额'), mom('loanClsDoubtful', '比上月'),
        val('loanClsLoss', '损失贷款余额'), mom('loanClsLoss', '比上月'),
      ],
    },
  },
  {
    bizType: 'FEE', label: '中间业务',
    def: {
      id: 'segment-business', label: '中间业务', dims: ['INDUSTRY', 'CREDIT_RATING', 'ENT_SCALE'], primary: 'feeTotal',
      columns: [
        { key: 'dimValue', label: '行业名称', kind: 'dim' },
        val('feeSettle', '支付结算收入'), mom('feeSettle', '比上月'),
        val('feeGuarantee', '担保业务收入'), mom('feeGuarantee', '比上月'),
        val('feeCommission', '委托收入'), mom('feeCommission', '比上月'),
        val('feeCustody', '托管收入'), mom('feeCustody', '比上月'),
        val('feeConsult', '咨询服务收入'), mom('feeConsult', '比上月'),
        val('feeAgency', '代理收入'), mom('feeAgency', '比上月'),
        val('feeDebitCard', '借记卡收入'), mom('feeDebitCard', '比上月'),
        val('feeCreditCard', '信用卡收入'), mom('feeCreditCard', '比上月'),
        val('feeEbank', '电子银行收入'), mom('feeEbank', '比上月'),
        val('feeFactoring', '保理收入'), mom('feeFactoring', '比上月'),
        val('feeOther', '其他中收'), mom('feeOther', '比上月'),
      ],
    },
  },
  {
    bizType: 'SETTLEMENT', label: '结算量业务',
    def: {
      id: 'segment-business', label: '结算量业务', dims: ['INDUSTRY', 'CREDIT_RATING', 'ENT_SCALE'], primary: 'settTotalAmt',
      columns: [
        { key: 'dimValue', label: '行业名称', kind: 'dim' },
        val('settDebitAmt', '本月发生额(借)'), mom('settDebitAmt', '比上月'),
        val('settCreditAmt', '本月发生额(贷)'), mom('settCreditAmt', '比上月'),
        val('settTotalAmt', '借贷累加'), mom('settTotalAmt', '比上月'),
        val('settNetAmt', '借贷差'), mom('settNetAmt', '比上月'),
      ],
    },
  },
]

/** 指标监视器 3 屏（分组柱状图/饼图 + 趋势图，原型截图口径） */
export const MONITOR_SCREENS: ScreenDef[] = [
  {
    id: 'monitor-balance', label: '业务增减变化监控', dims: [...MONITOR_DIMS], primary: 'depBal',
    columns: [
      { key: 'dimValue', label: '行业名称', kind: 'dim' },
      val('depBal', '存款余额'), mom('depBal', '比上月'), ytd('depBal', '比年初'),
      val('loanBal', '贷款余额'), mom('loanBal', '比上月'), ytd('loanBal', '比年初'),
      val('loanDisbMtd', '发放贷款金额'), mom('loanDisbMtd', '比上月'),
      val('settTotalAmt', '结算量金额'), mom('settTotalAmt', '比上月'),
    ],
  },
  {
    id: 'monitor-ldr', label: '存贷比变化监控', dims: [...MONITOR_DIMS], primary: 'ldr',
    columns: [
      { key: 'dimValue', label: '行业名称', kind: 'dim' },
      pctv('ldr', '存贷比'), mom('ldr', '比上月'), ytd('ldr', '比年初'),
      val('depBal', '存款余额'), mom('depBal', '比上月'), ytd('depBal', '比年初'),
      val('loanBal', '贷款余额'), mom('loanBal', '比上月'), ytd('loanBal', '比年初'),
    ],
  },
  {
    id: 'monitor-npl', label: '不良贷款分布变化监控', dims: [...MONITOR_DIMS], primary: 'nplBal',
    columns: [
      { key: 'dimValue', label: '行业名称', kind: 'dim' },
      val('nplBal', '不良贷款余额'), mom('nplBal', '比上月'), ytd('nplBal', '比年初'),
      share('nplBal', '占比'), shareMom('nplBal', '比上月'), shareYtd('nplBal', '比年初'),
    ],
  },
]

/** 组合查询客户清单列 */
export const COMBO_COLUMNS: ScreenColumn[] = [
  { key: 'custId', label: '客户编号', kind: 'dim' },
  { key: 'custName', label: '客户名称', kind: 'dim' },
  { key: 'orgName', label: '机构', kind: 'dim' },
  { key: 'industry', label: '所属行业', kind: 'dim' },
  { key: 'creditRating', label: '信用等级', kind: 'dim' },
  { key: 'entScale', label: '企业规模', kind: 'dim' },
  val('depBal', '存款时点金额'),
  val('loanBal', '贷款时点金额'),
  val('settAmtYear', '年结算累计金额'),
  val('feeYear', '年中间业务收入'),
  val('profitTotalYear', '年利润贡献'),
]

// ===================== API 函数 =====================

export function fetchDimensions(): Promise<AnalyticsDimension[]> {
  return analyticsApi.get('/dimensions').then((r) => r.data.data.dimensions)
}

export function fetchOrgs(): Promise<AnalyticsOrg[]> {
  return analyticsApi.get('/orgs').then((r) => r.data.data.orgs)
}

export function fetchPeriods(): Promise<string[]> {
  return analyticsApi.get('/periods').then((r) => r.data.data.periods)
}

export function fetchMetrics(params: {
  screen: string
  dim: string
  orgId: string
  period: string
  bizType?: string
}): Promise<AnalyticsMetrics> {
  return analyticsApi.get('/metrics', { params }).then((r) => r.data.data)
}

export function fetchTrend(params: {
  screen: string
  dim: string
  dimValue: string
  orgId: string
  metric: string
  months?: number
}): Promise<AnalyticsTrend> {
  return analyticsApi.get('/trend', { params }).then((r) => r.data.data)
}

export function postComboQuery(filters: ComboQueryFilters,
                                pageNumber: number,
                                pageSize: number): Promise<ComboQueryResult> {
  return analyticsApi.post('/combo-query', { filters, pageNumber, pageSize })
    .then((r) => r.data.data)
}
