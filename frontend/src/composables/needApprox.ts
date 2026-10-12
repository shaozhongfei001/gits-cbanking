import {
  fetchCustomerContext,
  fetchCustomers,
  type Claim,
  type Customer,
  type CustomerContext,
  type KycGapProfile,
  type OpportunitySignal,
} from '../api/engagement'

/** ObjectHeader 文案：非正式 Need，禁止写成合同对象。 */
export const NEED_OBJECT_TYPE = '非正式 Need（C2 降级）'

/** C1 视图模型来源：既有机会信号或 Claim，不是 Need schema。 */
export type NeedApproxKind = 'signal' | 'claim'

/**
 * C1 只读近似行。主键为既有 signalId / claimId，禁止 needId / NEED-826。
 * 本地字段（sourceKind、kindLabel）仅用于展示，不得回写。
 */
export type NeedApproxRow = {
  sourceKind: NeedApproxKind
  sourceId: string
  customerId: string
  customerName: string
  summary: string
  kindLabel: string
  signal?: OpportunitySignal
  claim?: Claim
  kyc?: KycGapProfile
}

export function rowsFromContext(customer: Customer, ctx: CustomerContext): NeedApproxRow[] {
  const rows: NeedApproxRow[] = []
  for (const signal of ctx.opportunitySignals ?? []) {
    rows.push({
      sourceKind: 'signal',
      sourceId: signal.signalId,
      customerId: customer.customerId,
      customerName: customer.customerName,
      summary: signal.content,
      kindLabel: '机会信号（只读近似）',
      signal,
      kyc: ctx.kycGapProfile,
    })
  }
  for (const claim of ctx.claims ?? []) {
    rows.push({
      sourceKind: 'claim',
      sourceId: claim.claimId,
      customerId: customer.customerId,
      customerName: customer.customerName,
      summary: claim.content ?? claim.statement ?? '',
      kindLabel: 'Claim（只读近似）',
      claim,
      kyc: ctx.kycGapProfile,
    })
  }
  return rows
}

export async function loadNeedApproxRows(): Promise<NeedApproxRow[]> {
  const customers = await fetchCustomers()
  const rows: NeedApproxRow[] = []
  for (const customer of customers) {
    const ctx = await fetchCustomerContext(customer.customerId)
    rows.push(...rowsFromContext(customer, ctx))
  }
  return rows
}

export async function loadNeedApproxById(id: string): Promise<NeedApproxRow | null> {
  const rows = await loadNeedApproxRows()
  return rows.find(row => row.sourceId === id) ?? null
}
