import { fetchAuditTrace, fetchHumanGates } from '../api/v11'
import { listClaims } from '../api/engagement'

/** C2 治理降级对象类型。禁止写成合同对象。 */
export const GOV_C2_OBJECT = {
  P31: '非正式专家协同（C2 降级）',
  P33: '非正式交付包（C2 降级）',
  P34: '非正式账户计划（C2 降级）',
  P35: '非正式价值口径（C2 降级）',
  P40: '服务降级（C2 离线包禁用）',
} as const

export type GovDegradePageId = keyof typeof GOV_C2_OBJECT

export type GovDegradeLoadMode = 'empty' | 'probe'

export type GovDegradeAction = {
  label: string
  reason: string
  unlockPath: string
}

export type GovDegradePageCopy = {
  pageId: GovDegradePageId
  title: string
  objectType: string
  objectStatus: string
  hint: string
  emptyText: string
  testId: string
  idleDescription: string
  loadMode: GovDegradeLoadMode
  actions: GovDegradeAction[]
}

export type GovDegradeShellResult = {
  empty: true
  informal: true
}

export type ServiceProbe = {
  serviceId: string
  label: string
  available: boolean
  detail: string
}

/**
 * 无专家协同 / DeliveryPackage / AccountPlan / 价值口径合同。
 * 永远返回空壳，禁止编造正式对象或 POST。
 */
export async function loadGovDegradeShell(): Promise<GovDegradeShellResult> {
  return { empty: true, informal: true }
}

/**
 * 用既有 C0 查询探测治理服务是否可访问。单路失败记为不可用，不发明新 OpenAPI。
 */
export async function probeDegradeServices(): Promise<ServiceProbe[]> {
  const probes: Array<[string, string, () => Promise<unknown>]> = [
    ['human-gates', 'HumanGate', () => fetchHumanGates({})],
    ['claims', 'Claim', () => listClaims()],
    ['audit-trace', 'AuditTrace', () => fetchAuditTrace({})],
  ]
  const results: ServiceProbe[] = []
  for (const [serviceId, label, run] of probes) {
    try {
      await run()
      results.push({ serviceId, label, available: true, detail: '可查询' })
    } catch (e: unknown) {
      results.push({
        serviceId,
        label,
        available: false,
        detail: e instanceof Error ? e.message : '查询失败',
      })
    }
  }
  return results
}

const COLLAB_UNLOCK = '待 CCC 完成专家协同合同后由独立 Loop 启用受控写'
const DELIVERY_UNLOCK = '待 CCC 批准 DeliveryPackage 合同后由独立 Loop 启用'
const ACCOUNT_PLAN_UNLOCK = '待 CCC 批准 AccountPlan 合同后由独立 Loop 启用；Task/Commitment 不能替代账户计划'
const VALUE_UNLOCK = '待 CCC 批准客户价值口径合同后由独立 Loop 启用'
const OFFLINE_UNLOCK = '离线包写回属 Loop P36 / 页面 P41–P44；本页禁用下载与离线写'

export const GOV_DEGRADE_PAGES: Record<GovDegradePageId, GovDegradePageCopy> = {
  P31: {
    pageId: 'P31',
    title: '专家协同记录',
    objectType: GOV_C2_OBJECT.P31,
    objectStatus: '无合同对象',
    hint: 'C2 降级：本分支无专家协同合同。空态不是失败；禁止编造协同记录或提交意见。',
    emptyText: '暂无专家协同对象。本页不编造协同记录，也不提供补充材料/提交意见写回。',
    testId: 'p31-collab',
    idleDescription: '尚未请求专家协同降级壳层',
    loadMode: 'empty',
    actions: [
      {
        label: '补充材料',
        reason: '无专家协同合同，禁止上传或回写补充材料',
        unlockPath: COLLAB_UNLOCK,
      },
      {
        label: '提交意见',
        reason: '无专家协同合同，禁止提交意见写回',
        unlockPath: COLLAB_UNLOCK,
      },
    ],
  },
  P33: {
    pageId: 'P33',
    title: '对客交付中心',
    objectType: GOV_C2_OBJECT.P33,
    objectStatus: '无 DeliveryPackage',
    hint: 'C2 降级：无 DeliveryPackage 合同。禁止生成或发送交付包。',
    emptyText: '暂无交付包对象。本页不编造 DeliveryPackage，也不启用生成/发送。',
    testId: 'p33-delivery',
    idleDescription: '尚未请求对客交付降级壳层',
    loadMode: 'empty',
    actions: [
      {
        label: '生成交付包',
        reason: '无 DeliveryPackage 合同，禁止生成交付包',
        unlockPath: DELIVERY_UNLOCK,
      },
      {
        label: '确认发送',
        reason: '无 DeliveryPackage 合同，禁止确认发送',
        unlockPath: DELIVERY_UNLOCK,
      },
    ],
  },
  P34: {
    pageId: 'P34',
    title: '30/90/180 天账户计划',
    objectType: GOV_C2_OBJECT.P34,
    objectStatus: '无 AccountPlan',
    hint: 'C2 降级：无 AccountPlan 合同。禁止用 Task 或 Commitment 冒充账户计划。',
    emptyText: '暂无账户计划对象。Task/Commitment 不能替代 AccountPlan；本页不编造里程碑。',
    testId: 'p34-account-plans',
    idleDescription: '尚未请求账户计划降级壳层',
    loadMode: 'empty',
    actions: [
      {
        label: '新增里程碑',
        reason: '无 AccountPlan 合同，禁止新增里程碑；不得把 Task/Commitment 写成账户计划',
        unlockPath: ACCOUNT_PLAN_UNLOCK,
      },
      {
        label: '开始复盘',
        reason: '无 AccountPlan 合同，禁止发起账户计划复盘',
        unlockPath: ACCOUNT_PLAN_UNLOCK,
      },
    ],
  },
  P35: {
    pageId: 'P35',
    title: '客户价值实现',
    objectType: GOV_C2_OBJECT.P35,
    objectStatus: '无价值口径',
    hint: 'C2 降级：无客户价值口径合同。禁止记录基线或发起价值复盘写回。',
    emptyText: '暂无价值实现对象。本页不编造价值基线或口径数字。',
    testId: 'p35-value',
    idleDescription: '尚未请求价值实现降级壳层',
    loadMode: 'empty',
    actions: [
      {
        label: '记录基线',
        reason: '无价值口径合同，禁止记录基线写回',
        unlockPath: VALUE_UNLOCK,
      },
      {
        label: '发起复盘',
        reason: '无价值口径合同，禁止发起价值复盘',
        unlockPath: VALUE_UNLOCK,
      },
    ],
  },
  P40: {
    pageId: 'P40',
    title: '服务降级与异常恢复',
    objectType: GOV_C2_OBJECT.P40,
    objectStatus: '在线探测',
    hint: 'C2 降级：查询失败可重试。下载离线包与离线写回未授权。',
    emptyText: '离线包未授权。查询失败时使用重试；禁止把探测结果当成离线包。',
    testId: 'p40-degrade',
    idleDescription: '尚未探测治理服务可用性',
    loadMode: 'probe',
    actions: [
      {
        label: '下载离线包',
        reason: '离线包写回未授权，禁止下载离线包',
        unlockPath: OFFLINE_UNLOCK,
      },
    ],
  },
}
