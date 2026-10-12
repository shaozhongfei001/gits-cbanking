import { describe, it, expect, vi } from 'vitest'
import { loadNeedApproxRows, rowsFromContext } from '../needApprox'
import type { Claim, Customer, CustomerContext, OpportunitySignal } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
    fetchCustomerContext: vi.fn(),
  }
})

const customer: Customer = { customerId: 'c1', customerName: '企业A' }
const signal: OpportunitySignal = {
  signalId: 'sig-1',
  signalType: 'FINANCING_NEED',
  content: '周转压力',
  sourceType: 'ANALYSIS',
  status: 'DETECTED',
  detectedAt: '2026-08-01T00:00:00Z',
}
const claim: Claim = {
  claimId: 'clm-1',
  claimType: 'CUSTOMER_STATEMENT',
  content: '扩产意向',
  status: 'CANDIDATE',
}
const ctx: CustomerContext = {
  customer,
  opportunitySignals: [signal],
  claims: [claim],
  recentInteractions: [],
  activeJourneys: [],
  recentTransactions: [],
}

describe('needApprox C1 view-model', () => {
  it('uses signalId and claimId rather than inventing needId', () => {
    const rows = rowsFromContext(customer, ctx)
    expect(rows.map(row => row.sourceId)).toEqual(['sig-1', 'clm-1'])
    expect(rows.every(row => !('needId' in row))).toBe(true)
  })

  it('loads rows from fetchCustomers and fetchCustomerContext', async () => {
    const { fetchCustomers, fetchCustomerContext } = await import('../../api/engagement')
    ;(fetchCustomers as ReturnType<typeof vi.fn>).mockResolvedValue([customer])
    ;(fetchCustomerContext as ReturnType<typeof vi.fn>).mockResolvedValue(ctx)
    const rows = await loadNeedApproxRows()
    expect(rows).toHaveLength(2)
    expect(rows[0].sourceKind).toBe('signal')
    expect(rows[1].sourceKind).toBe('claim')
  })
})
