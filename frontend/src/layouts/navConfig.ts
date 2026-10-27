export type ShellNavItem = {
  key: string
  label: string
  icon: string
  to: string
  domain: 'workbench' | 'commitments' | 'journeys' | 'accounts' | 'panorama' | 'signals' | 'needs' | 'product-center' | 'recommendation' | 'product-knowledge' | 'proposals' | 'collab' | 'approvals' | 'plans' | 'operating-metrics' | 'segments' | 'combo-query' | 'audit' | 'crm-writeback' | 'portfolio'
}

export type ShellNavGroup = {
  key: string
  label: string
  labelEn: string
  children: ShellNavItem[]
}

/**
 * V8 一级导航：「对公经营书桌」
 *
 * 5 组菜单：经营 / 客户 / 产品 / 方案 / 分析
 * 遵循客户经理工作路径：经营总览→客户档案→访前准备→访后跟进→持续经营
 * 产品入口保持「产品解读→客户体检→受控推荐」业务顺序
 * 访前/会中/写回/移动端等业务阶段不进入一级导航
 *
 * 图标使用 Lucide 风格 SVG path（stroke-based，viewBox 0 0 24 24）
 */
export const SHELL_NAV_GROUPS: ShellNavGroup[] = [
  {
    key: 'workspace',
    label: '经营',
    labelEn: 'WORKSPACE',
    children: [
      { key: 'workbench', label: '经营总览', icon: 'M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z M9 22V12h6v10', to: '/workbench', domain: 'workbench' },
      { key: 'commitments', label: '承诺事项', icon: 'M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11', to: '/commitments', domain: 'commitments' },
      { key: 'journeys', label: '经营旅程', icon: 'M22 12h-4l-3 9L9 3l-3 9H2', to: '/engagement', domain: 'journeys' },
      { key: 'crm-writeback', label: 'CRM 回写', icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15', to: '/engagement/crm-writeback', domain: 'crm-writeback' },
      { key: 'audit-trace', label: '审计追踪', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', to: '/audit-trace', domain: 'audit' },
    ],
  },
  {
    key: 'client',
    label: '客户',
    labelEn: 'CLIENT',
    children: [
      { key: 'portfolio', label: '客户组合', icon: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75', to: '/accounts', domain: 'accounts' },
      { key: 'portfolio-board', label: '组合看板', icon: 'M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1v-2zM14 12a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1h-4a1 1 0 01-1-1v-5z', to: '/accounts/portfolio', domain: 'portfolio' },
      { key: 'signals', label: '经营信号', icon: 'M13 17l5-5-5-5M6 17l5-5-5-5', to: '/signals', domain: 'signals' },
      { key: 'needs', label: '需求与机会', icon: 'M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.56 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z', to: '/needs', domain: 'needs' },
    ],
  },
  {
    key: 'product',
    label: '产品',
    labelEn: 'PRODUCT',
    children: [
      { key: 'product-center', label: '产品解读', icon: 'M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16zM3.27 6.96L12 12.01l8.73-5.05M12 22.08V12', to: '/product-center', domain: 'product-center' },
      { key: 'product-knowledge', label: '产品知识', icon: 'M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2zM22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z', to: '/product-knowledge/interpretation', domain: 'product-knowledge' },
      { key: 'recommendation', label: '受控推荐', icon: 'M22 12h-4l-3 9L9 3l-3 9H2', to: '/recommendation/new', domain: 'recommendation' },
    ],
  },
  {
    key: 'proposal',
    label: '方案',
    labelEn: 'PROPOSAL',
    children: [
      { key: 'proposals', label: '建议书', icon: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8', to: '/proposals', domain: 'proposals' },
      { key: 'approvals', label: '审批中心', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', to: '/approvals', domain: 'approvals' },
    ],
  },
  {
    key: 'analytics',
    label: '分析',
    labelEn: 'ANALYTICS',
    children: [
      { key: 'analytics-operating-metrics', label: '经营指标', icon: 'M18 20V10M12 20V4M6 20v-6', to: '/analytics/operating-metrics', domain: 'operating-metrics' },
      { key: 'analytics-segments', label: '客户分群', icon: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9', to: '/analytics/segments', domain: 'segments' },
      { key: 'analytics-combo', label: '组合查询', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z', to: '/analytics/combo-query', domain: 'combo-query' },
    ],
  },
]

export const SHELL_NAV_ITEMS: ShellNavItem[] = SHELL_NAV_GROUPS.flatMap(group => group.children)

export function navDomainForPath(path: string): ShellNavItem['domain'] {
  if (path.startsWith('/m/')) return 'workbench'
  if (path === '/' || path.startsWith('/workbench')) return 'workbench'
  if (path.startsWith('/commitments')) return 'commitments'
  if (path.startsWith('/signals')) return 'signals'
  // 特化路径必须**先于**通用前缀匹配，否则被下面的 `/engagement` 吞掉（D-1：原实现此处为不可达分支）
  if (path.startsWith('/engagement/crm-writeback')) return 'crm-writeback'
  if (path.startsWith('/engagements') || path.startsWith('/engagement') || path.startsWith('/in-meeting')) return 'journeys'
  if (path.startsWith('/external-events')) return 'signals'
  if (path.startsWith('/customers')) return 'panorama'
  if (path.startsWith('/accounts/portfolio')) return 'portfolio'
  if (path.startsWith('/accounts')) return 'accounts'
  if (path.startsWith('/needs')) return 'needs'
  if (path.startsWith('/product-center')) return 'product-center'
  if (path.startsWith('/recommendation')) return 'recommendation'
  if (path.startsWith('/claims') || path.startsWith('/knowledge-map') || path.startsWith('/product-knowledge')) return 'product-knowledge'
  if (path.startsWith('/proposals') || path.startsWith('/delivery')) return 'proposals'
  if (path.startsWith('/collab')) return 'collab'
  if (path.startsWith('/approvals')) return 'approvals'
  if (path.startsWith('/audit-trace')) return 'audit'
  if (path.startsWith('/account-plans') || path.startsWith('/value')) return 'plans'
  if (path.startsWith('/analytics/operating-metrics')) return 'operating-metrics'
  if (path.startsWith('/analytics/segments')) return 'segments'
  if (path.startsWith('/analytics/combo-query')) return 'combo-query'
  if (path.startsWith('/analytics')) return 'operating-metrics'
  if (path.startsWith('/degrade')) return 'approvals'
  return 'workbench'
}

// ── 结构性不变量守卫（DEV-ONLY）──────────────────────────────────
// 事故根因：多个菜单项共享同一 domain，导致 isItemActive() 同时匹配多项。
// 此守卫在模块加载时校验，违反即抛出，杜绝同类问题再次进入演示现场。
//
// 不变量清单：
//   INV-1 domain 全局唯一（每个菜单项必须有自己的 domain）
//   INV-2 key   全局唯一（每个菜单项必须有自己的 key）
//   INV-3 每个 nav item 的 to 路径经 navDomainForPath 回解必须命中自身 domain
//   INV-4 每个 group 的 key 全局唯一

function _validateNavConfigInvariants(): void {
  if (import.meta.env.PROD) return // 生产环境不校验

  // INV-1: domain 唯一性
  const domainCounts = new Map<string, string[]>()
  for (const item of SHELL_NAV_ITEMS) {
    const existing = domainCounts.get(item.domain) ?? []
    existing.push(`${item.label}(${item.key})`)
    domainCounts.set(item.domain, existing)
  }
  const duplicateDomains = [...domainCounts.entries()].filter(([, items]) => items.length > 1)
  if (duplicateDomains.length > 0) {
    const detail = duplicateDomains.map(([d, items]) => `  domain="${d}" → [${items.join(', ')}]`).join('\n')
    throw new Error(`[navConfig] INV-1 违反：domain 不唯一\n${detail}`)
  }

  // INV-2: key 唯一性
  const keyCounts = new Map<string, string[]>()
  for (const item of SHELL_NAV_ITEMS) {
    const existing = keyCounts.get(item.key) ?? []
    existing.push(item.label)
    keyCounts.set(item.key, existing)
  }
  const duplicateKeys = [...keyCounts.entries()].filter(([, items]) => items.length > 1)
  if (duplicateKeys.length > 0) {
    const detail = duplicateKeys.map(([k, items]) => `  key="${k}" → [${items.join(', ')}]`).join('\n')
    throw new Error(`[navConfig] INV-2 违反：key 不唯一\n${detail}`)
  }

  // INV-3: to 路径回解一致性（nav item 的 to 经 navDomainForPath 必须命中自身 domain）
  for (const item of SHELL_NAV_ITEMS) {
    const resolved = navDomainForPath(item.to)
    if (resolved !== item.domain) {
      throw new Error(
        `[navConfig] INV-3 违反："${item.label}" to="${item.to}" 期望 domain="${item.domain}"，实际 navDomainForPath 返回="${resolved}"`,
      )
    }
  }

  // INV-4: group key 唯一性
  const groupKeys = SHELL_NAV_GROUPS.map(g => g.key)
  const uniqueGroupKeys = new Set(groupKeys)
  if (uniqueGroupKeys.size !== groupKeys.length) {
    throw new Error(`[navConfig] INV-4 违反：group key 不唯一`)
  }
}

_validateNavConfigInvariants()

/** 根据 domain 查找所属组的 labelEn，用于顶栏面包屑 */
export function navGroupLabelForDomain(domain: ShellNavItem['domain']): string {
  for (const group of SHELL_NAV_GROUPS) {
    if (group.children.some(item => item.domain === domain)) {
      return group.label
    }
  }
  return ''
}

/** 根据 domain 查找当前激活的菜单项 label，用于面包屑 */
export function navItemLabelForPath(path: string): string {
  const domain = navDomainForPath(path)
  const item = SHELL_NAV_ITEMS.find(i => i.domain === domain)
  return item?.label ?? ''
}
