import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  MOBILE_C2_OBJECT,
  MOBILE_DEGRADE_PAGES,
  firstOnlineDeepLink,
  loadMobileDegradeShell,
  loadTodayActions,
} from '../mobileDegrade'
import type { Customer } from '../../api/engagement'

vi.mock('../../api/engagement', async () => {
  const actual = await vi.importActual<typeof import('../../api/engagement')>('../../api/engagement')
  return {
    ...actual,
    fetchCustomers: vi.fn(),
  }
})

const mockCustomers: Customer[] = [
  {
    customerId: 'c1',
    customerName: '企业A',
    industry: 'MANUFACTURING',
    enterpriseScale: 'LARGE',
    customerTier: 'STRATEGIC',
    riskLevel: 'HIGH',
  },
]

describe('mobileDegrade C2 shell model', () => {
  it('returns an empty informal shell and never fabricates offline packs or claims', async () => {
    const row = await loadMobileDegradeShell()
    expect(row).toEqual({ empty: true, informal: true })
    expect(row).not.toHaveProperty('offlinePackId')
    expect(row).not.toHaveProperty('claimId')
    expect(row).not.toHaveProperty('taskId')
  })

  it('derives today actions from online customers without writing localStorage tasks', async () => {
    const { fetchCustomers } = await import('../../api/engagement')
    vi.mocked(fetchCustomers).mockResolvedValue(mockCustomers)
    const setItem = vi.spyOn(Storage.prototype, 'setItem')
    const rows = await loadTodayActions()
    expect(rows).toEqual([
      {
        customerId: 'c1',
        customerName: '企业A',
        onlinePath: '/customers/c1',
      },
    ])
    expect(setItem).not.toHaveBeenCalled()
    setItem.mockRestore()
  })

  it('opens the first item only via existing online deep links', () => {
    expect(firstOnlineDeepLink([])).toBe('/workbench')
    expect(firstOnlineDeepLink([{ customerId: 'c1', customerName: '企业A', onlinePath: '/customers/c1' }])).toBe(
      '/customers/c1',
    )
    expect(firstOnlineDeepLink([{ customerId: 'c1', customerName: '企业A', onlinePath: '/customers/c1' }])).not.toMatch(
      /localStorage|offline|sw\.js/,
    )
  })

  it('keeps P41-P44 write labels without inventing mobile cache contracts', () => {
    expect(MOBILE_DEGRADE_PAGES.P41.disabledActions.map(item => item.label)).toEqual(['加入离线队列'])
    expect(MOBILE_DEGRADE_PAGES.P42.disabledActions.map(item => item.label)).toEqual(['开始拜访'])
    expect(MOBILE_DEGRADE_PAGES.P43.disabledActions.map(item => item.label)).toEqual(['新增速记'])
    expect(MOBILE_DEGRADE_PAGES.P44.disabledActions.map(item => item.label)).toEqual(['离线完成会谈'])
    expect(MOBILE_C2_OBJECT.P41).toContain('C2')
    expect(JSON.stringify(MOBILE_DEGRADE_PAGES)).not.toContain('NEED-826')
    expect(JSON.stringify(MOBILE_DEGRADE_PAGES)).not.toMatch(/Service Worker|Cache API/)
  })
})
