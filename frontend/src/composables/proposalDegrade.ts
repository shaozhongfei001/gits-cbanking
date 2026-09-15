/** ObjectHeader 文案：非正式建议书壳层，禁止写成合同对象。 */
export const PROPOSAL_OBJECT_TYPE = '非正式建议书（C2 降级）'

export const PROPOSAL_UNLOCK_PATH =
  '待 CCC 完成 CC2 并批准建议书工厂 / ProposalVersion 合同后由独立 Loop 启用受控写'

export const PROPOSAL_WRITE_REASON =
  '本分支无建议书工厂合同；禁止 POST proposal API，禁止把降级壳当作可回写 G0-G5 状态机'

export type ProposalPlaceholder = {
  placeholderId: string
  informal: true
  degradeLabel: '非正式 / C2 降级'
  contractNote: string
}

export type ProposalWizardShell = {
  informal: true
  emptyDraft: true
  degradeLabel: '非正式 / C2 降级'
}

export type ProposalShellLoadMode = 'list' | 'wizard' | 'placeholder'

export type ProposalShellPageId = 'P23' | 'P24' | 'P25' | 'P26' | 'P27' | 'P28' | 'P29' | 'P30'

export type ProposalShellCopy = {
  pageId: ProposalShellPageId
  title: string
  objectStatus: string
  actionLabel: string
  actionReason: string
  hint: string
  testId: string
  idleDescription: string
  loadMode: ProposalShellLoadMode
}

const PLACEHOLDER_NOTE =
  '本分支无建议书工厂合同。占位 ID 仅来自路由参数，非正式事实，禁止当作正式 Proposal 正文或阶段。'

/**
 * 无建议书合同。永远返回空列表，禁止编造建议书行或 POST。
 */
export async function loadProposalShellList(): Promise<[]> {
  return []
}

export async function loadProposalWizardShell(): Promise<ProposalWizardShell> {
  return {
    informal: true,
    emptyDraft: true,
    degradeLabel: '非正式 / C2 降级',
  }
}

export async function loadProposalPlaceholder(id: string): Promise<ProposalPlaceholder> {
  const placeholderId = id.trim()
  if (!placeholderId) {
    throw new Error('缺少占位对象 ID，无法装配非正式建议书壳层')
  }
  return {
    placeholderId,
    informal: true,
    degradeLabel: '非正式 / C2 降级',
    contractNote: PLACEHOLDER_NOTE,
  }
}

export const PROPOSAL_SHELL_PAGES: Record<ProposalShellPageId, ProposalShellCopy> = {
  P23: {
    pageId: 'P23',
    title: '建议书对象主页',
    objectStatus: '列表',
    actionLabel: '导入草稿',
    actionReason: `${PROPOSAL_WRITE_REASON}；导入草稿会写入非正式对象`,
    hint: 'C2：正式建议书列表与导入草稿未授权。本页「新建建议书」进入向导，可向 DKWS SP-20 请求非正式草稿，不可保存为 G0–G5 对象。',
    testId: 'p23-proposals',
    idleDescription: '尚未请求建议书降级列表',
    loadMode: 'list',
  },
  P24: {
    pageId: 'P24',
    title: '新建建议书向导',
    objectStatus: '向导',
    actionLabel: '保存并继续',
    actionReason: `${PROPOSAL_WRITE_REASON}；保存并继续会创建非正式草稿`,
    hint: 'C2：保存并继续会创建正式建议书，本波禁止。可选择客户后请求 DKWS SP-20 生成非正式草稿，失败保持空态。',
    testId: 'p24-proposal-wizard',
    idleDescription: '尚未装配新建向导降级壳',
    loadMode: 'wizard',
  },
  P25: {
    pageId: 'P25',
    title: '建议书记录',
    objectStatus: '阶段机未授权',
    actionLabel: '预览客户版',
    actionReason: `${PROPOSAL_WRITE_REASON}；预览客户版依赖未授权的客户版对象`,
    hint: 'C3 降级：路由 param 只作占位对象 ID，标明非正式 / C2 降级。阶段机未授权，不可晋级。',
    testId: 'p25-proposal-record',
    idleDescription: '尚未装配建议书记录降级壳',
    loadMode: 'placeholder',
  },
  P26: {
    pageId: 'P26',
    title: '建议书模块编辑器',
    objectStatus: '只读壳层',
    actionLabel: '提交评审',
    actionReason: `${PROPOSAL_WRITE_REASON}；提交评审会启动未授权的评审写路径`,
    hint: 'C2 降级：模块编辑器不可提交。占位 ID 非正式。',
    testId: 'p26-proposal-editor',
    idleDescription: '尚未装配模块编辑器降级壳',
    loadMode: 'placeholder',
  },
  P27: {
    pageId: 'P27',
    title: '需求—方案—产品映射',
    objectStatus: '只读壳层',
    actionLabel: '运行完整性检查',
    actionReason: `${PROPOSAL_WRITE_REASON}；完整性检查会写入未授权的映射结果`,
    hint: 'C2 降级：无需求—方案—产品映射合同，不可运行检查。',
    testId: 'p27-proposal-map',
    idleDescription: '尚未装配映射降级壳',
    loadMode: 'placeholder',
  },
  P28: {
    pageId: 'P28',
    title: 'AI 内容依据反查',
    objectStatus: '只读壳层',
    actionLabel: '标记问题',
    actionReason: `${PROPOSAL_WRITE_REASON}；标记问题会写入未授权的依据异议`,
    hint: 'C2 降级：当前不可反查。无建议书正文合同，无 AI 内容与 Evidence 绑定接口。',
    testId: 'p28-proposal-evidence',
    idleDescription: '尚未装配依据反查降级壳',
    loadMode: 'placeholder',
  },
  P29: {
    pageId: 'P29',
    title: '内部版与客户版对照',
    objectStatus: '只读壳层',
    actionLabel: '查看隐藏规则',
    actionReason: `${PROPOSAL_WRITE_REASON}；隐藏规则属于未授权的对客披露合同`,
    hint: 'C2 降级：内部版/客户版对照不可查看隐藏规则。占位 ID 非正式。',
    testId: 'p29-proposal-project',
    idleDescription: '尚未装配对照降级壳',
    loadMode: 'placeholder',
  },
  P30: {
    pageId: 'P30',
    title: '版本比较与恢复',
    objectStatus: '只读壳层',
    actionLabel: '创建新版本',
    actionReason: `${PROPOSAL_WRITE_REASON}；创建新版本依赖未授权的 ProposalVersion`,
    hint: 'C2 降级：无 ProposalVersion 合同，不可创建或恢复版本。',
    testId: 'p30-proposal-versions',
    idleDescription: '尚未装配版本降级壳',
    loadMode: 'placeholder',
  },
}
