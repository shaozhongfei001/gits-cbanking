import { describe, it, expect } from 'vitest'
import {
  loadProposalPlaceholder,
  loadProposalShellList,
  loadProposalWizardShell,
  PROPOSAL_OBJECT_TYPE,
  PROPOSAL_SHELL_PAGES,
} from '../proposalDegrade'

describe('proposalDegrade C2 shell model', () => {
  it('returns an empty list and never fabricates proposal rows or NEED-826', async () => {
    const rows = await loadProposalShellList()
    expect(rows).toEqual([])
    expect(rows).toHaveLength(0)
  })

  it('builds a route-param placeholder marked informal / C2, not a formal proposalId', async () => {
    const row = await loadProposalPlaceholder('ph-1')
    expect(row.placeholderId).toBe('ph-1')
    expect(row.informal).toBe(true)
    expect(row.degradeLabel).toBe('非正式 / C2 降级')
    expect(row).not.toHaveProperty('proposalId')
    expect(row).not.toHaveProperty('body')
    expect(row).not.toHaveProperty('content')
    expect(row).not.toHaveProperty('stage')
    expect(PROPOSAL_OBJECT_TYPE).toContain('C2 降级')
  })

  it('rejects an empty placeholder id so the four-state can show error', async () => {
    await expect(loadProposalPlaceholder('')).rejects.toThrow(/占位/)
  })

  it('loads an empty wizard draft without inventing proposal body', async () => {
    const wizard = await loadProposalWizardShell()
    expect(wizard.emptyDraft).toBe(true)
    expect(wizard.informal).toBe(true)
    expect(wizard).not.toHaveProperty('proposalId')
  })

  it('keeps write actions as copy only, without a G0-G5 enum', () => {
    expect(PROPOSAL_SHELL_PAGES.P23.actionLabel).toBe('导入草稿')
    expect(PROPOSAL_SHELL_PAGES.P24.actionLabel).toBe('保存并继续')
    expect(PROPOSAL_SHELL_PAGES.P25.actionLabel).toBe('预览客户版')
    expect(PROPOSAL_SHELL_PAGES.P26.actionLabel).toBe('提交评审')
    expect(PROPOSAL_SHELL_PAGES.P27.actionLabel).toBe('运行完整性检查')
    expect(PROPOSAL_SHELL_PAGES.P28.actionLabel).toBe('标记问题')
    expect(PROPOSAL_SHELL_PAGES.P29.actionLabel).toBe('查看隐藏规则')
    expect(PROPOSAL_SHELL_PAGES.P30.actionLabel).toBe('创建新版本')
    expect(Object.values(PROPOSAL_SHELL_PAGES).every(page => page.actionReason.length > 0)).toBe(true)
  })
})
