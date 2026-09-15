export type ShellNavItem = {
  key: string
  label: string
  icon: string
  to: string
  domain: 'workbench' | 'commitments' | 'accounts' | 'panorama' | 'signals' | 'needs' | 'proposals' | 'recommendation' | 'collab' | 'plans' | 'evidence' | 'audit'
}

export type ShellNavGroup = {
  key: string
  label: string
  children: ShellNavItem[]
}

/**
 * V3.2 一级导航：只切换稳定对象域。
 * 访前/会中/写回/移动端等业务阶段不得进入一级导航。
 * 权威：设计系统 Token、页面 01 PNG、generate_gits_bank_ux_v32.py NAV_GROUPS。
 */
export const SHELL_NAV_GROUPS: ShellNavGroup[] = [
  {
    key: 'daily',
    label: '日常作业',
    children: [
      { key: 'workbench', label: '客户经营作战台', icon: '▦', to: '/workbench', domain: 'workbench' },
      { key: 'commitments', label: '我的任务与承诺', icon: '✓', to: '/commitments', domain: 'commitments' },
    ],
  },
  {
    key: 'accounts',
    label: '客户经营',
    children: [
      { key: 'portfolio', label: '客户组合', icon: '◎', to: '/accounts', domain: 'accounts' },
      { key: 'panorama', label: '客户全景', icon: '◉', to: '/accounts', domain: 'panorama' },
      { key: 'signals', label: '信号与互动', icon: '↗', to: '/engagement', domain: 'signals' },
      { key: 'needs', label: '需求与机会', icon: '◇', to: '/needs', domain: 'needs' },
    ],
  },
  {
    key: 'delivery',
    label: '方案与交付',
    children: [
      { key: 'proposals', label: '服务建议书', icon: '▤', to: '/proposals', domain: 'proposals' },
      { key: 'recommendation', label: '产品推荐', icon: '★', to: '/recommendation/new', domain: 'recommendation' },
      { key: 'collab', label: '专家协同', icon: '♙', to: '/collab', domain: 'collab' },
      { key: 'plans', label: '账户计划与价值', icon: '▱', to: '/account-plans', domain: 'plans' },
    ],
  },
  {
    key: 'governance',
    label: '知识与治理',
    children: [
      { key: 'evidence', label: '产品解读与知识', icon: '⌁', to: '/knowledge-map', domain: 'evidence' },
      { key: 'audit', label: '审批与审计', icon: '◌', to: '/approvals', domain: 'audit' },
    ],
  },
]

export const SHELL_NAV_ITEMS: ShellNavItem[] = SHELL_NAV_GROUPS.flatMap(group => group.children)

export function navDomainForPath(path: string): ShellNavItem['domain'] {
  if (path.startsWith('/m/')) return 'workbench'
  if (path === '/' || path.startsWith('/workbench')) return 'workbench'
  if (path.startsWith('/commitments')) return 'commitments'
  if (path.startsWith('/customers')) return 'panorama'
  if (path.startsWith('/accounts')) return 'accounts'
  if (
    path.startsWith('/signals')
    || path.startsWith('/engagements')
    || path.startsWith('/engagement')
    || path.startsWith('/in-meeting')
    || path.startsWith('/external-events')
  ) {
    return 'signals'
  }
  if (path.startsWith('/needs')) return 'needs'
  if (path.startsWith('/proposals') || path.startsWith('/delivery')) return 'proposals'
  if (path.startsWith('/recommendation')) return 'recommendation'
  if (path.startsWith('/collab')) return 'collab'
  if (path.startsWith('/account-plans') || path.startsWith('/value')) return 'plans'
  if (path.startsWith('/claims') || path.startsWith('/knowledge-map')) return 'evidence'
  if (path.startsWith('/approvals') || path.startsWith('/audit-trace') || path.startsWith('/degrade')) return 'audit'
  return 'workbench'
}
