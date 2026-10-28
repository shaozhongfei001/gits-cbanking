import { describe, it, expect } from 'vitest'
import {
  SHELL_NAV_GROUPS,
  SHELL_NAV_ITEMS,
  navDomainForPath,
  navGroupLabelForDomain,
  navItemLabelForPath,
} from '../navConfig'

/**
 * navConfig 结构性不变量测试
 *
 * 事故根因回顾（2026-09-27 演示现场发现）：
 *   "分析"组下三个菜单项（经营指标/客户分群/组合查询）共享 domain='analytics'，
 *   导致 isItemActive() 同时匹配多项，点击任一子菜单时三个背景同时渲染。
 *
 * 修复后建立四条不变量，本文件在 CI 中持续守护。
 * 若有人新增菜单项时违反任一不变量，测试立即失败，不可能再进入演示现场。
 */

describe('navConfig 结构性不变量', () => {
  // ── INV-1: domain 全局唯一 ──────────────────────────────────────
  it('INV-1: 每个 nav item 的 domain 全局唯一', () => {
    const domains = SHELL_NAV_ITEMS.map(item => item.domain)
    const unique = new Set(domains)
    if (unique.size !== domains.length) {
      // 找出重复项，方便定位
      const dupes = domains.filter((d, i) => domains.indexOf(d) !== i)
      const dupeItems = SHELL_NAV_ITEMS.filter(item => dupes.includes(item.domain))
        .map(item => `"${item.label}" domain="${item.domain}"`)
      expect.fail(`domain 不唯一: ${dupeItems.join(', ')}`)
    }
    expect(unique.size).toBe(domains.length)
  })

  // ── INV-2: key 全局唯一 ────────────────────────────────────────
  it('INV-2: 每个 nav item 的 key 全局唯一', () => {
    const keys = SHELL_NAV_ITEMS.map(item => item.key)
    const unique = new Set(keys)
    if (unique.size !== keys.length) {
      const dupes = keys.filter((k, i) => keys.indexOf(k) !== i)
      const dupeItems = SHELL_NAV_ITEMS.filter(item => dupes.includes(item.key))
        .map(item => `"${item.label}" key="${item.key}"`)
      expect.fail(`key 不唯一: ${dupeItems.join(', ')}`)
    }
    expect(unique.size).toBe(keys.length)
  })

  // ── INV-3: to 路径回解一致性 ───────────────────────────────────
  it('INV-3: 每个 nav item 的 to 路径经 navDomainForPath 回解必须命中自身 domain', () => {
    const violations: string[] = []
    for (const item of SHELL_NAV_ITEMS) {
      const resolved = navDomainForPath(item.to)
      if (resolved !== item.domain) {
        violations.push(`"${item.label}" to="${item.to}" 期望="${item.domain}" 实际="${resolved}"`)
      }
    }
    if (violations.length > 0) {
      expect.fail(`路径回解不一致:\n  ${violations.join('\n  ')}`)
    }
    expect(violations).toHaveLength(0)
  })

  // ── INV-4: group key 唯一 ──────────────────────────────────────
  it('INV-4: 每个 group 的 key 全局唯一', () => {
    const keys = SHELL_NAV_GROUPS.map(g => g.key)
    expect(new Set(keys).size).toBe(keys.length)
  })
})

describe('navConfig 功能正确性', () => {
  it('navDomainForPath 对关键路由返回正确 domain', () => {
    expect(navDomainForPath('/workbench')).toBe('workbench')
    expect(navDomainForPath('/commitments')).toBe('commitments')
    expect(navDomainForPath('/engagement')).toBe('journeys')
    expect(navDomainForPath('/engagement/crm-writeback')).toBe('crm-writeback')
    expect(navDomainForPath('/audit-trace')).toBe('audit')
    expect(navDomainForPath('/accounts')).toBe('accounts')
    expect(navDomainForPath('/accounts/portfolio')).toBe('portfolio')
    expect(navDomainForPath('/signals')).toBe('signals')
    expect(navDomainForPath('/needs')).toBe('needs')
    expect(navDomainForPath('/product-center')).toBe('product-center')
    expect(navDomainForPath('/recommendation/new')).toBe('recommendation')
    expect(navDomainForPath('/proposals')).toBe('proposals')
    expect(navDomainForPath('/approvals')).toBe('approvals')
    expect(navDomainForPath('/analytics/operating-metrics')).toBe('operating-metrics')
    expect(navDomainForPath('/analytics/segments')).toBe('segments')
    expect(navDomainForPath('/analytics/combo-query')).toBe('combo-query')
  })

  it('特化路径优先于通用前缀（D-1 回归守卫）', () => {
    // /engagement/crm-writeback 不能被 /engagement 吞掉
    expect(navDomainForPath('/engagement/crm-writeback')).toBe('crm-writeback')
    expect(navDomainForPath('/engagement/crm-writeback/123')).toBe('crm-writeback')
    // /accounts/portfolio 不能被 /accounts 吞掉
    expect(navDomainForPath('/accounts/portfolio')).toBe('portfolio')
    expect(navDomainForPath('/accounts/portfolio/ABC')).toBe('portfolio')
  })

  it('navGroupLabelForDomain 返回正确的组标签', () => {
    expect(navGroupLabelForDomain('workbench')).toBe('经营')
    expect(navGroupLabelForDomain('accounts')).toBe('客户')
    expect(navGroupLabelForDomain('product-center')).toBe('产品')
    expect(navGroupLabelForDomain('proposals')).toBe('方案')
    expect(navGroupLabelForDomain('operating-metrics')).toBe('分析')
  })

  it('navItemLabelForPath 返回正确的菜单项标签', () => {
    expect(navItemLabelForPath('/analytics/combo-query')).toBe('组合查询')
    expect(navItemLabelForPath('/analytics/operating-metrics')).toBe('经营指标')
    expect(navItemLabelForPath('/analytics/segments')).toBe('客户分群')
    expect(navItemLabelForPath('/engagement/crm-writeback')).toBe('CRM 回写')
    expect(navItemLabelForPath('/audit-trace')).toBe('审计追踪')
  })

  it('未知路径 fallback 到 workbench', () => {
    expect(navDomainForPath('/unknown-path')).toBe('workbench')
    expect(navDomainForPath('/')).toBe('workbench')
  })
})

describe('navConfig 菜单归属正确性', () => {
  it('"审计追踪"和"CRM 回写"属于"经营"组，不属于"分析"组', () => {
    const workspaceGroup = SHELL_NAV_GROUPS.find(g => g.key === 'workspace')!
    const analyticsGroup = SHELL_NAV_GROUPS.find(g => g.key === 'analytics')!

    const workspaceLabels = workspaceGroup.children.map(i => i.label)
    const analyticsLabels = analyticsGroup.children.map(i => i.label)

    expect(workspaceLabels).toContain('审计追踪')
    expect(workspaceLabels).toContain('CRM 回写')
    expect(analyticsLabels).not.toContain('审计追踪')
    expect(analyticsLabels).not.toContain('CRM 回写')
  })

  it('"组合看板"属于"客户"组，不属于"分析"组', () => {
    const clientGroup = SHELL_NAV_GROUPS.find(g => g.key === 'client')!
    const analyticsGroup = SHELL_NAV_GROUPS.find(g => g.key === 'analytics')!

    const clientLabels = clientGroup.children.map(i => i.label)
    const analyticsLabels = analyticsGroup.children.map(i => i.label)

    expect(clientLabels).toContain('组合看板')
    expect(analyticsLabels).not.toContain('组合看板')
  })

  it('"分析"组只包含分析功能（经营指标/客户分群/组合查询/指标监视器）', () => {
    const analyticsGroup = SHELL_NAV_GROUPS.find(g => g.key === 'analytics')!
    const analyticsLabels = analyticsGroup.children.map(i => i.label)

    expect(analyticsLabels).toEqual(['经营指标', '客户分群', '组合查询', '指标监视器'])
  })
})
