/**
 * 建议书草稿暂存（C2 降级的**浏览器会话内**暂存，非正式对象）。
 *
 * 边界（红线，不得放宽）：
 * - **不写后端、不落库**：不调用任何建议书写接口（不 POST/PUT proposal），不写入 G0–G5 状态机；
 * - **不写 localStorage**：仅在 `sessionStorage` 做一份浏览器会话镜像，
 *   目的是刷新页面后仍能打开详情（否则列表为空、详情只剩占位壳）；
 *   关闭标签页即失效，且**不改变任何对象语义**；
 * - 记录中的 `status` 固定为 `INFORMAL`（非正式草稿），不得伪装成阶段机状态；
 * - 镜像数据需通过形状校验（`isProposalDraftRecord`）后才恢复，避免残留脏数据污染列表。
 */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { ServiceProposal } from '../api/v14'
import { formatDateTime } from '../utils/datetime'

export interface ProposalDraftRecord {
  /** 运行标识（KERT runId），列表行主键与详情页路由 param */
  id: string
  customerId: string
  customerName: string
  proposalName: string
  generatedAt: string
  status: string
  skillId: string
  /**
   * 以下计数均为**前端派生字段**（由 KERT 回包按同一规则计算），
   * 非后端新增合同字段；不得据此回写任何业务状态。
   */
  chapterCount: number
  citationCount: number
  unknownCount: number
  limitationCount: number
  /** KERT 原始回包（只读呈现，禁止改写） */
  proposal: ServiceProposal
}

/** 浏览器会话镜像键（版本化，便于结构变更后自然失效） */
export const PROPOSAL_DRAFT_SESSION_KEY = 'gits:proposal-drafts:v1'

/**
 * 展示用时间格式化：KERT 回包为 ISO（UTC），界面按本地时区展示为 `YYYY-MM-DD HH:mm:ss`。
 * 仅为显示格式化，不改变存储中的原始时间戳。
 */
export function formatKertTimestamp(source: string): string {
  return formatDateTime(source)
}

/** 形状校验：只有字段完整的记录才允许从会话镜像恢复（缺字段 ⇒ 丢弃，不猜）。 */
export function isProposalDraftRecord(value: unknown): value is ProposalDraftRecord {
  if (!value || typeof value !== 'object') return false
  const candidate = value as Partial<ProposalDraftRecord>
  if (typeof candidate.id !== 'string' || candidate.id.length === 0) return false
  if (typeof candidate.customerId !== 'string') return false
  if (typeof candidate.generatedAt !== 'string') return false
  const proposal = candidate.proposal as ServiceProposal | undefined
  if (!proposal || typeof proposal !== 'object') return false
  if (typeof proposal.content?.proposalDraft !== 'string') return false
  return true
}

function readSession(): ProposalDraftRecord[] {
  if (typeof sessionStorage === 'undefined') return []
  try {
    const raw = sessionStorage.getItem(PROPOSAL_DRAFT_SESSION_KEY)
    if (!raw) return []
    const parsed: unknown = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter(isProposalDraftRecord)
  } catch {
    // 镜像损坏时以空列表启动（不得让脏数据冒充建议书对象）
    return []
  }
}

function writeSession(list: ProposalDraftRecord[]): void {
  if (typeof sessionStorage === 'undefined') return
  try {
    if (list.length === 0) {
      sessionStorage.removeItem(PROPOSAL_DRAFT_SESSION_KEY)
      return
    }
    sessionStorage.setItem(PROPOSAL_DRAFT_SESSION_KEY, JSON.stringify(list))
  } catch {
    // 配额/隐私模式异常不得影响主流程
  }
}

export const useProposalDraftStore = defineStore('proposalDraft', () => {
  const drafts = ref<ProposalDraftRecord[]>(readSession())

  const total = computed(() => drafts.value.length)

  /** 新增草稿（同 runId 幂等，避免重复请求产生重复行）。 */
  function add(record: ProposalDraftRecord) {
    if (drafts.value.some(item => item.id === record.id)) return
    drafts.value = [record, ...drafts.value]
    writeSession(drafts.value)
  }

  function find(id: string): ProposalDraftRecord | null {
    if (!id) return null
    return drafts.value.find(item => item.id === id) ?? null
  }

  function clear() {
    drafts.value = []
    writeSession(drafts.value)
  }

  return { drafts, total, add, find, clear }
})
