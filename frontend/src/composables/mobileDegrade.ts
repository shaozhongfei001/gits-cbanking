import { fetchCustomers } from '../api/engagement'

/** C2 移动端降级对象类型。禁止写成合同对象或离线包。 */
export const MOBILE_C2_OBJECT = {
  P41: '非正式今日行动（C2 降级）',
  P42: '非正式访前包（C2 降级，无离线包）',
  P43: '非正式会中速记（C2 降级，非正式 Claim）',
  P44: '离场确认（移动端 C2；仅复用 E01）',
} as const

export type MobileDegradePageId = keyof typeof MOBILE_C2_OBJECT

export type MobileDegradeAction = {
  label: string
  reason: string
  unlockPath: string
}

export type MobileDegradePageCopy = {
  pageId: MobileDegradePageId
  title: string
  objectType: string
  objectStatus: string
  hint: string
  emptyText: string
  testId: string
  idleDescription: string
  disabledActions: MobileDegradeAction[]
}

export type MobileDegradeShellResult = {
  empty: true
  informal: true
}

export type TodayActionItem = {
  customerId: string
  customerName: string
  onlinePath: string
}

const OFFLINE_QUEUE_UNLOCK =
  '待 CCC 批准移动缓存/同步合同后由独立 Loop 启用；当前仅可打开已有在线深链'
const OFFLINE_PACK_UNLOCK =
  '待 CCC 批准访前离线包合同后由独立 Loop 启用；当前仅可只读查看桌面 /engagement/previsit/pack'
const NOTES_UNLOCK = '待 CCC 批准会中速记写回合同后由独立 Loop 启用；草稿不得当成正式 Claim'
const OFFLINE_EXIT_UNLOCK =
  '禁止离线完成会谈。仅当既有 HumanGate 类型 E01_EXIT_CONFIRM 处于 PENDING 时，才可走 decideHumanGate'

export const MOBILE_DEGRADE_PAGES: Record<MobileDegradePageId, MobileDegradePageCopy> = {
  P41: {
    pageId: 'P41',
    title: '移动端·今日客户行动',
    objectType: MOBILE_C2_OBJECT.P41,
    objectStatus: '在线只读',
    hint: 'C2 降级：本分支无移动缓存/离线队列。打开首项只跳已有在线深链，不把列表写成正式 Task。',
    emptyText: '暂无今日在线行动。本页不把空队列写成离线任务，也不使用 localStorage 作为正式任务源。',
    testId: 'p41-mobile-today',
    idleDescription: '尚未请求今日在线行动',
    disabledActions: [
      {
        label: '加入离线队列',
        reason: '无移动缓存/离线队列合同，禁止把今日行动写成离线任务',
        unlockPath: OFFLINE_QUEUE_UNLOCK,
      },
    ],
  },
  P42: {
    pageId: 'P42',
    title: '移动端·访前包',
    objectType: MOBILE_C2_OBJECT.P42,
    objectStatus: '离线包未授权',
    hint: 'C2 降级：开始拜访隐含缓存/离线包，本分支未授权。可只读查看桌面访前包。',
    emptyText: '离线访前包未授权。本页不下载离线包，也不开始离线拜访。',
    testId: 'p42-mobile-previsit',
    idleDescription: '尚未请求访前包降级壳层',
    disabledActions: [
      {
        label: '开始拜访',
        reason: '开始拜访依赖缓存/离线包，本分支未授权',
        unlockPath: OFFLINE_PACK_UNLOCK,
      },
    ],
  },
  P43: {
    pageId: 'P43',
    title: '移动端·会中速记',
    objectType: MOBILE_C2_OBJECT.P43,
    objectStatus: '草稿非正式',
    hint: 'C2 降级：新增速记属离线写。草稿不得当成正式 Claim。',
    emptyText: '暂无会中速记对象。本页不把草稿写成正式 Claim，也不提供离线写回。',
    testId: 'p43-mobile-notes',
    idleDescription: '尚未请求会中速记降级壳层',
    disabledActions: [
      {
        label: '新增速记',
        reason: '无会中速记写回合同，禁止离线新增速记；草稿不是正式 Claim',
        unlockPath: NOTES_UNLOCK,
      },
    ],
  },
  P44: {
    pageId: 'P44',
    title: '移动端·离场确认与任务',
    objectType: MOBILE_C2_OBJECT.P44,
    objectStatus: '在线门禁',
    hint: 'C2 降级：完成会谈默认禁用。仅当既有 PENDING E01_EXIT_CONFIRM 时走与桌面 P17 同一 decideHumanGate 合同。',
    emptyText: '无待处理 E01_EXIT_CONFIRM。禁止离线完成会谈。',
    testId: 'p44-mobile-checkout',
    idleDescription: '尚未加载离场确认门禁',
    disabledActions: [
      {
        label: '离线完成会谈',
        reason: '禁止离线完成会谈；无移动缓存写回合同',
        unlockPath: OFFLINE_EXIT_UNLOCK,
      },
    ],
  },
}

/**
 * 无移动缓存 / 离线包 / 速记写回合同。永远返回空壳，禁止编造正式对象。
 */
export async function loadMobileDegradeShell(): Promise<MobileDegradeShellResult> {
  return { empty: true, informal: true }
}

/**
 * C1 View Model：今日行动由既有客户列表派生。不是 Task/Commitment，禁止写入 localStorage。
 */
export async function loadTodayActions(): Promise<TodayActionItem[]> {
  const customers = await fetchCustomers()
  return customers.map(customer => ({
    customerId: customer.customerId,
    customerName: customer.customerName,
    onlinePath: `/customers/${customer.customerId}`,
  }))
}

export function firstOnlineDeepLink(items: TodayActionItem[]): string {
  return items[0]?.onlinePath || '/workbench'
}
