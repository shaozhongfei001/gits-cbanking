import { describe, expect, it, beforeEach } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { createPinia, setActivePinia } from 'pinia'
import {
  PROPOSAL_DRAFT_SESSION_KEY,
  formatKertTimestamp,
  isProposalDraftRecord,
  useProposalDraftStore,
  type ProposalDraftRecord,
} from '../proposalDraft'
import type { ServiceProposal } from '../../api/v14'

function proposal(): ServiceProposal {
  return {
    schemaVersion: '1.0.0',
    skillId: 'SP-20',
    runId: 'RUN-1',
    status: 'SUCCESS',
    timestamp: '2026-09-25T06:11:25Z',
    content: { proposalDraft: '# 标题\n\n# 第一章 概况\n\n正文。', internalVersion: null, customerVersion: null, customerVersionNote: '' },
    citations: [],
    unknowns: [],
    limitations: [],
    gateRecommendations: null,
    ruleViolations: [],
  }
}

function record(id: string): ProposalDraftRecord {
  return {
    id,
    customerId: 'CUST-CORP-0001',
    customerName: '华东精工装备集团',
    proposalName: '华东精工装备集团 — 非正式建议书草稿',
    generatedAt: '2026-09-25T06:11:25Z',
    status: 'INFORMAL',
    skillId: 'SP-20',
    chapterCount: 1,
    citationCount: 0,
    unknownCount: 0,
    limitationCount: 0,
    proposal: proposal(),
  }
}

describe('useProposalDraftStore', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
  })

  it('新增后置顶（最新在前）并可查找', () => {
    const store = useProposalDraftStore()
    store.add(record('RUN-1'))
    store.add(record('RUN-2'))
    expect(store.drafts.map(item => item.id)).toEqual(['RUN-2', 'RUN-1'])
    expect(store.total).toBe(2)
    expect(store.find('RUN-1')?.id).toBe('RUN-1')
  })

  it('同 runId 幂等，不产生重复行', () => {
    const store = useProposalDraftStore()
    store.add(record('RUN-1'))
    store.add(record('RUN-1'))
    expect(store.drafts).toHaveLength(1)
  })

  it('未命中返回 null（不编造记录）', () => {
    const store = useProposalDraftStore()
    expect(store.find('RUN-NOT-EXIST')).toBeNull()
    expect(store.find('')).toBeNull()
  })

  it('clear 清空全部暂存（不落库）', () => {
    const store = useProposalDraftStore()
    store.add(record('RUN-1'))
    store.clear()
    expect(store.drafts).toHaveLength(0)
    expect(store.total).toBe(0)
    expect(sessionStorage.getItem(PROPOSAL_DRAFT_SESSION_KEY)).toBeNull()
  })
})

describe('useProposalDraftStore · 浏览器会话镜像', () => {
  beforeEach(() => {
    sessionStorage.clear()
    setActivePinia(createPinia())
  })

  it('新增后写入会话镜像，刷新（新 store 实例）仍可查看详情', () => {
    useProposalDraftStore().add(record('RUN-PERSIST-1'))
    expect(sessionStorage.getItem(PROPOSAL_DRAFT_SESSION_KEY)).toContain('RUN-PERSIST-1')

    // 模拟刷新：重建 pinia ⇒ 新 store 实例从会话镜像恢复
    setActivePinia(createPinia())
    const restored = useProposalDraftStore()
    expect(restored.drafts).toHaveLength(1)
    expect(restored.find('RUN-PERSIST-1')?.proposalName).toContain('非正式建议书草稿')
    expect(restored.find('RUN-PERSIST-1')?.status).toBe('INFORMAL')
  })

  it('只写 sessionStorage，源码不得出现 localStorage（红线守卫）', () => {
    useProposalDraftStore().add(record('RUN-PERSIST-1'))
    expect(sessionStorage.getItem(PROPOSAL_DRAFT_SESSION_KEY)).not.toBeNull()

    // localStorage 一旦被引入即构成「持久化」，与 C2 降级红线冲突 ⇒ 源码级守卫
    const source = readFileSync(resolve(process.cwd(), 'src/stores/proposalDraft.ts'), 'utf-8')
    const code = source.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*$/gm, '')
    expect(code).not.toContain('localStorage')
  })

  it('镜像损坏时以空列表启动，不抛异常、不冒充对象', () => {
    sessionStorage.setItem(PROPOSAL_DRAFT_SESSION_KEY, '{ not json')
    const store = useProposalDraftStore()
    expect(store.drafts).toHaveLength(0)
  })

  it('镜像为非数组时丢弃', () => {
    sessionStorage.setItem(PROPOSAL_DRAFT_SESSION_KEY, JSON.stringify({ id: 'RUN-1' }))
    expect(useProposalDraftStore().drafts).toHaveLength(0)
  })

  it('形状不完整的记录被丢弃，只恢复合法记录', () => {
    sessionStorage.setItem(
      PROPOSAL_DRAFT_SESSION_KEY,
      JSON.stringify([record('RUN-OK-1'), { id: 'RUN-BAD-1' }, null, { id: 42 }]),
    )
    const store = useProposalDraftStore()
    expect(store.drafts.map(item => item.id)).toEqual(['RUN-OK-1'])
  })
})

describe('isProposalDraftRecord', () => {
  it('接受形状完整的记录', () => {
    expect(isProposalDraftRecord(record('RUN-1'))).toBe(true)
  })

  it('拒绝缺字段 / 非对象 / 无草稿正文的记录', () => {
    expect(isProposalDraftRecord(null)).toBe(false)
    expect(isProposalDraftRecord('RUN-1')).toBe(false)
    expect(isProposalDraftRecord({ id: '', customerId: 'C', generatedAt: 'x', proposal: {} })).toBe(false)
    expect(
      isProposalDraftRecord({
        id: 'RUN-1',
        customerId: 'CUST-1',
        generatedAt: '2026-09-25T00:00:00Z',
        proposal: { content: {} },
      }),
    ).toBe(false)
  })
})

describe('formatKertTimestamp', () => {
  it('ISO(UTC) 转为本地 `YYYY-MM-DD HH:mm:ss`', () => {
    const formatted = formatKertTimestamp('2026-09-25T06:11:25Z')
    expect(formatted).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)
    expect(formatted.startsWith('2026-09-25')).toBe(true)
  })

  it('空值返回占位符，非法值原样返回（不伪装成合法时间）', () => {
    expect(formatKertTimestamp('')).toBe('—')
    expect(formatKertTimestamp('not-a-date')).toBe('not-a-date')
  })
})
