import { describe, it, expect, vi } from 'vitest'
import {
  GOV_C2_OBJECT,
  GOV_DEGRADE_PAGES,
  loadGovDegradeShell,
  probeDegradeServices,
} from '../govDegrade'

vi.mock('../../api/v11', async () => {
  const actual = await vi.importActual<typeof import('../../api/v11')>('../../api/v11')
  return {
    ...actual,
    fetchHumanGates: vi.fn().mockResolvedValue([]),
    fetchAuditTrace: vi.fn().mockResolvedValue([]),
  }
})

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    listClaims: vi.fn().mockResolvedValue([]),
  }
})

describe('govDegrade C2 shell model', () => {
  it('returns an empty informal shell and never fabricates collab/delivery/account-plan/value objects', async () => {
    const row = await loadGovDegradeShell()
    expect(row).toEqual({ empty: true, informal: true })
    expect(row).not.toHaveProperty('collabId')
    expect(row).not.toHaveProperty('deliveryPackageId')
    expect(row).not.toHaveProperty('accountPlanId')
    expect(row).not.toHaveProperty('baselineId')
  })

  it('keeps P31/P33/P34/P35/P40 write labels without inventing contract objects or NEED-826', () => {
    expect(GOV_DEGRADE_PAGES.P31.actions.map(item => item.label)).toEqual(['补充材料', '提交意见'])
    expect(GOV_DEGRADE_PAGES.P33.actions.map(item => item.label)).toEqual(['生成交付包', '确认发送'])
    expect(GOV_DEGRADE_PAGES.P34.actions.map(item => item.label)).toEqual(['新增里程碑', '开始复盘'])
    expect(GOV_DEGRADE_PAGES.P35.actions.map(item => item.label)).toEqual(['记录基线', '发起复盘'])
    expect(GOV_DEGRADE_PAGES.P40.actions.map(item => item.label)).toEqual(['下载离线包'])
    expect(GOV_C2_OBJECT.P34).toContain('C2')
    expect(GOV_DEGRADE_PAGES.P34.emptyText).toMatch(/Task\/Commitment/)
    expect(JSON.stringify(GOV_DEGRADE_PAGES)).not.toContain('NEED-826')
  })

  it('probes existing C0 queries and records per-service availability', async () => {
    const rows = await probeDegradeServices()
    expect(rows.map(item => item.serviceId)).toEqual(['human-gates', 'claims', 'audit-trace'])
    expect(rows.every(item => item.available)).toBe(true)
  })
})
