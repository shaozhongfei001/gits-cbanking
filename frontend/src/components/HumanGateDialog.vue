<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  NModal, NCard, NDescriptions, NDescriptionsItem, NTag, NButton,
  NSpace, NInput, NAlert, NSpin, NDivider, NIcon, NTooltip
} from 'naive-ui'
import {
  type HumanGate,
  type GateDecision,
  GATE_TYPE_LABELS,
  HUMAN_GATE_STATUS_LABELS,
  GATE_DECISION_LABELS
} from '../api/v11'
import {
  RECOMMENDATION_DECISION_LABELS,
  STRUCTURED_MODIFICATION_KIND_LABELS,
  type RecommendationDecision,
  type StructuredModification,
  type StructuredModificationKind
} from '../api/productRecommendation'

const props = defineProps<{
  show: boolean
  gate: HumanGate | null
  loading?: boolean
  error?: string | null
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'decide', gateId: string, decision: GateDecision, modification: Record<string, unknown> | undefined, reason: string): void
  (e: 'decide-structured', payload: {
    runId: string
    proposalVersionId: string
    expectedVersion?: string
    decision: RecommendationDecision
    modifications?: StructuredModification[]
    reason?: string
  }): void
}>()

const selectedDecision = ref<GateDecision | null>(null)
const modificationJson = ref('')
const reason = ref('')
const submitting = ref(false)

// ── D01（产品推荐）结构化决定状态 ──────────────────────────────────────
const D01_DECISIONS: RecommendationDecision[] = ['APPROVE', 'MODIFY', 'REJECT', 'HOLD']
const D01_MODIFICATION_KINDS = Object.keys(STRUCTURED_MODIFICATION_KIND_LABELS) as StructuredModificationKind[]

const d01Decision = ref<RecommendationDecision | null>(null)
const d01Reason = ref('')
const d01Modifications = ref<StructuredModification[]>([])
const d01ValidationError = ref('')

const d01ModKind = ref<StructuredModificationKind>('REMOVE_CANDIDATE')
const d01TargetProductId = ref('')
const d01TargetPortfolioId = ref('')
const d01FromPosition = ref<number | null>(null)
const d01ToPosition = ref<number | null>(null)
const d01Value = ref('')
const d01Note = ref('')

const gateTypeLabel = computed(() => {
  if (!props.gate) return ''
  return GATE_TYPE_LABELS[props.gate.gateType] || props.gate.gateType
})

const statusLabel = computed(() => {
  if (!props.gate) return ''
  return HUMAN_GATE_STATUS_LABELS[props.gate.status] || props.gate.status
})

const statusType = computed(() => {
  if (!props.gate) return 'default' as const
  switch (props.gate.status) {
    case 'PENDING': return 'warning' as const
    case 'APPROVED': return 'success' as const
    case 'REJECTED': return 'error' as const
    case 'MODIFIED': return 'info' as const
    default: return 'default' as const
  }
})

const isPending = computed(() => props.gate?.status === 'PENDING')

/** D01 门禁：显示结构化决定面板，不再编辑原始 JSON。 */
const isD01 = computed(() => props.gate?.gateType === 'D01_PRODUCT_RECOMMEND')

/** 从 HumanGate.proposal 提取产品推荐上下文（runId / proposalVersionId / expectedVersion）。 */
function proposalField(names: string[]): string | undefined {
  const p = props.gate?.proposal
  if (!p) return undefined
  for (const name of names) {
    const value = p[name]
    if (typeof value === 'string' && value) return value
  }
  return undefined
}

const recommendationContext = computed(() => ({
  runId: proposalField(['runId']),
  proposalVersionId: proposalField(['proposalVersionId', 'currentVersionId', 'versionId']),
  expectedVersion: proposalField(['expectedVersion', 'currentVersionId']),
}))

const decisionOptions = computed(() => {
  const options: Array<{ value: GateDecision; label: string; type: 'success' | 'error' | 'warning' | 'info' }> = [
    { value: 'APPROVE', label: GATE_DECISION_LABELS.APPROVE, type: 'success' },
    { value: 'REJECT', label: GATE_DECISION_LABELS.REJECT, type: 'error' },
    { value: 'MODIFY', label: GATE_DECISION_LABELS.MODIFY, type: 'info' },
    { value: 'HOLD', label: GATE_DECISION_LABELS.HOLD, type: 'warning' },
    { value: 'DECLINE', label: GATE_DECISION_LABELS.DECLINE, type: 'error' }
  ]
  return options
})

// ── 非 D01 决策（保持兼容） ────────────────────────────────────────────
function handleDecide(decision: GateDecision) {
  if (!props.gate) return
  selectedDecision.value = decision
  if (decision !== 'MODIFY') {
    submitDecision(decision)
  }
}

function submitDecision(decision: GateDecision) {
  if (!props.gate) return
  submitting.value = true
  let mod: Record<string, unknown> | undefined
  if (decision === 'MODIFY' && modificationJson.value) {
    try {
      mod = JSON.parse(modificationJson.value)
    } catch {
      // 解析失败，忽略
    }
  }
  emit('decide', props.gate.gateId, decision, mod, reason.value)
  setTimeout(() => {
    submitting.value = false
    selectedDecision.value = null
    reason.value = ''
    modificationJson.value = ''
  }, 500)
}

// ── D01 结构化决定 ────────────────────────────────────────────────────
function handleD01Decide(decision: RecommendationDecision) {
  d01Decision.value = decision
  d01ValidationError.value = ''
  if (decision !== 'MODIFY') {
    d01Modifications.value = []
  }
}

function addD01Modification() {
  const mod: StructuredModification = { kind: d01ModKind.value }
  if (d01TargetProductId.value.trim()) mod.targetProductId = d01TargetProductId.value.trim()
  if (d01TargetPortfolioId.value.trim()) mod.targetPortfolioId = d01TargetPortfolioId.value.trim()
  if (d01FromPosition.value != null) mod.fromPosition = d01FromPosition.value
  if (d01ToPosition.value != null) mod.toPosition = d01ToPosition.value
  if (d01Value.value.trim()) mod.value = d01Value.value.trim()
  if (d01Note.value.trim()) mod.note = d01Note.value.trim()
  d01Modifications.value = [...d01Modifications.value, mod]
  d01TargetProductId.value = ''
  d01TargetPortfolioId.value = ''
  d01FromPosition.value = null
  d01ToPosition.value = null
  d01Value.value = ''
  d01Note.value = ''
}

function removeD01Modification(index: number) {
  d01Modifications.value = d01Modifications.value.filter((_, i) => i !== index)
}

/** 非法修改显式失败：返回错误信息，合法返回 null。 */
function validateD01Modification(mod: StructuredModification): string | null {
  if (!mod.kind) return '修改类型不能为空'
  const hasTarget = Boolean(mod.targetProductId?.trim() || mod.targetPortfolioId?.trim())
  switch (mod.kind) {
    case 'REORDER_CANDIDATE':
      if (!hasTarget) return '调整顺序需指定目标产品或组合'
      if (mod.fromPosition == null || mod.toPosition == null) return '调整顺序需填写原位置与新位置'
      break
    case 'CHANGE_NEXT_ACTION':
    case 'ADD_CONFIRMED_FACT':
      if (!mod.value?.trim()) return '该修改类型需填写值'
      break
    default:
      if (!hasTarget) return '该修改类型需指定目标产品或组合'
  }
  return null
}

function submitD01Decision() {
  if (!props.gate || !d01Decision.value) return
  const ctx = recommendationContext.value
  if (!ctx.runId || !ctx.proposalVersionId) {
    d01ValidationError.value = '缺少推荐上下文（runId / proposalVersionId），无法提交结构化决定'
    return
  }

  const decision = d01Decision.value
  if (decision === 'MODIFY') {
    if (d01Modifications.value.length === 0) {
      d01ValidationError.value = '修改后采纳需至少一条结构化修改项'
      return
    }
    for (const mod of d01Modifications.value) {
      const err = validateD01Modification(mod)
      if (err) {
        d01ValidationError.value = err
        return
      }
    }
  }
  if ((decision === 'REJECT' || decision === 'HOLD') && !d01Reason.value.trim()) {
    d01ValidationError.value = decision === 'REJECT' ? '驳回必须填写理由' : '暂缓必须填写理由'
    return
  }

  d01ValidationError.value = ''
  submitting.value = true
  emit('decide-structured', {
    runId: ctx.runId as string,
    proposalVersionId: ctx.proposalVersionId as string,
    expectedVersion: ctx.expectedVersion,
    decision,
    modifications: decision === 'MODIFY' ? d01Modifications.value : undefined,
    reason: d01Reason.value.trim() || undefined,
  })
  setTimeout(() => {
    submitting.value = false
    resetD01()
  }, 500)
}

function resetD01() {
  d01Decision.value = null
  d01Reason.value = ''
  d01Modifications.value = []
  d01ValidationError.value = ''
  d01ModKind.value = 'REMOVE_CANDIDATE'
  d01TargetProductId.value = ''
  d01TargetPortfolioId.value = ''
  d01FromPosition.value = null
  d01ToPosition.value = null
  d01Value.value = ''
  d01Note.value = ''
}

function handleClose() {
  emit('update:show', false)
  selectedDecision.value = null
  reason.value = ''
  modificationJson.value = ''
  resetD01()
}
</script>

<template>
  <NModal :show="show" @update:show="handleClose" preset="card" style="width: 680px" :title="`门禁审批 - ${gateTypeLabel}`">
    <NSpin :show="loading">
      <NAlert v-if="error" type="error" :title="error" style="margin-bottom: 16px" />

      <template v-if="gate">
        <NDescriptions bordered :column="2" label-placement="left" size="small">
          <NDescriptionsItem label="门禁类型">
            <NTag size="small">{{ gateTypeLabel }}</NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="状态">
            <NTag :type="statusType" size="small">{{ statusLabel }}</NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="主题" :span="2">
            {{ gate.subject }}
          </NDescriptionsItem>
          <NDescriptionsItem v-if="gate.journeyId" label="旅程ID" :span="2">
            {{ gate.journeyId }}
          </NDescriptionsItem>
          <NDescriptionsItem v-if="gate.customerId" label="客户ID" :span="2">
            {{ gate.customerId }}
          </NDescriptionsItem>
        </NDescriptions>

        <NDivider>AI 提案</NDivider>

        <div v-if="gate.proposal" class="proposal-section">
          <pre class="proposal-content">{{ JSON.stringify(gate.proposal, null, 2) }}</pre>
        </div>
        <NAlert v-else type="info" title="无AI提案" />

        <div v-if="gate.evidenceRefs?.length" style="margin-top: 12px">
          <NDivider>证据引用</NDivider>
          <NSpace>
            <NTag v-for="ref in gate.evidenceRefs" :key="ref" size="small" type="info">
              {{ ref }}
            </NTag>
          </NSpace>
        </div>

        <!-- 决策区域 -->
        <template v-if="isPending">
          <template v-if="isD01">
            <NDivider>审批决策（结构化）</NDivider>
            <NAlert v-if="d01ValidationError" type="error" :title="d01ValidationError" style="margin-bottom: 12px" />
            <NAlert type="warning" style="margin-bottom: 12px">
              采纳仅表示允许候选进入方案装配，不代表产品/授信/建议书审批。
            </NAlert>

            <div class="d01-decision-buttons" data-testid="d01-decision-buttons">
              <button
                v-for="d in D01_DECISIONS"
                :key="d"
                type="button"
                class="d01-decision-btn"
                :class="{ active: d01Decision === d }"
                :data-testid="`d01-decision-${d.toLowerCase()}`"
                @click="handleD01Decide(d)"
              >
                {{ RECOMMENDATION_DECISION_LABELS[d] }}
              </button>
            </div>

            <div v-if="d01Decision === 'MODIFY'" class="d01-modify-builder" data-testid="d01-modify-builder">
              <p class="d01-section-title">结构化修改项（不编辑原始 JSON）</p>
              <div class="d01-modify-row">
                <select v-model="d01ModKind" data-testid="d01-mod-kind" aria-label="修改类型">
                  <option v-for="k in D01_MODIFICATION_KINDS" :key="k" :value="k">
                    {{ STRUCTURED_MODIFICATION_KIND_LABELS[k] }}
                  </option>
                </select>
                <input v-model="d01TargetProductId" type="text" placeholder="目标产品 ID（可选）" data-testid="d01-mod-product-id" />
                <input v-model="d01TargetPortfolioId" type="text" placeholder="目标组合 ID（可选）" data-testid="d01-mod-portfolio-id" />
              </div>
              <div class="d01-modify-row">
                <input v-model.number="d01FromPosition" type="number" placeholder="原位置（可选）" data-testid="d01-mod-from" />
                <input v-model.number="d01ToPosition" type="number" placeholder="新位置（可选）" data-testid="d01-mod-to" />
                <input v-model="d01Value" type="text" placeholder="值（后续行动/已确认事实，可选）" data-testid="d01-mod-value" />
              </div>
              <div class="d01-modify-row">
                <input v-model="d01Note" type="text" placeholder="修改说明（可选）" data-testid="d01-mod-note" />
                <button type="button" class="d01-add" data-testid="d01-mod-add" @click="addD01Modification">
                  添加修改项
                </button>
              </div>

              <ul v-if="d01Modifications.length" class="d01-mod-list" data-testid="d01-mod-list">
                <li v-for="(m, idx) in d01Modifications" :key="idx" class="d01-mod-item">
                  <span class="d01-mod-kind">{{ STRUCTURED_MODIFICATION_KIND_LABELS[m.kind] }}</span>
                  <span class="d01-mod-detail">
                    {{ [m.targetProductId, m.targetPortfolioId, m.value, m.note].filter(Boolean).join(' · ') || '—' }}
                  </span>
                  <button type="button" class="d01-remove" :data-testid="`d01-mod-remove-${idx}`" @click="removeD01Modification(idx)">
                    移除
                  </button>
                </li>
              </ul>
            </div>

            <div v-if="d01Decision === 'REJECT' || d01Decision === 'HOLD'" class="d01-reason-box" data-testid="d01-reason-box">
              <textarea
                v-model="d01Reason"
                rows="2"
                :placeholder="d01Decision === 'REJECT' ? '驳回原因分类＋说明（必填）' : '暂缓原因（必填）'"
                data-testid="d01-reason"
              />
            </div>

            <div v-if="d01Decision" class="d01-submit-row">
              <button type="button" class="d01-submit" :disabled="submitting" data-testid="d01-submit" @click="submitD01Decision">
                确认决定
              </button>
            </div>
          </template>

          <template v-else>
            <NDivider>审批决策</NDivider>

            <NInput
              v-model:value="reason"
              type="textarea"
              placeholder="请输入决策原因（可选）"
              :rows="2"
              style="margin-bottom: 12px"
            />

            <template v-if="selectedDecision === 'MODIFY'">
              <NInput
                v-model:value="modificationJson"
                type="textarea"
                placeholder="请输入修改内容（JSON格式）"
                :rows="4"
                style="margin-bottom: 12px"
              />
              <NButton type="info" :loading="submitting" @click="submitDecision('MODIFY')">
                确认修改
              </NButton>
            </template>

            <NSpace v-else justify="center" style="margin-top: 8px">
              <NButton
                v-for="opt in decisionOptions"
                :key="opt.value"
                :type="opt.type"
                :loading="submitting && selectedDecision === opt.value"
                @click="handleDecide(opt.value)"
              >
                {{ opt.label }}
              </NButton>
            </NSpace>
          </template>
        </template>

        <!-- 已决策信息 -->
        <template v-else-if="gate.decision">
          <NDivider>决策结果</NDivider>
          <NDescriptions bordered :column="2" label-placement="left" size="small">
            <NDescriptionsItem label="决策">
              <NTag :type="gate.decision === 'APPROVE' ? 'success' : 'error'" size="small">
                {{ GATE_DECISION_LABELS[gate.decision] }}
              </NTag>
            </NDescriptionsItem>
            <NDescriptionsItem label="决策人">
              {{ gate.actorId || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem v-if="gate.decisionReason" label="原因" :span="2">
              {{ gate.decisionReason }}
            </NDescriptionsItem>
            <NDescriptionsItem v-if="gate.modification" label="修改内容" :span="2">
              <pre>{{ JSON.stringify(gate.modification, null, 2) }}</pre>
            </NDescriptionsItem>
          </NDescriptions>
        </template>
      </template>

      <NAlert v-else type="info" title="未选择门禁" />
    </NSpin>

    <template #footer>
      <NSpace justify="end">
        <NButton @click="handleClose">关闭</NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<style scoped>
.proposal-section {
  max-height: 300px;
  overflow-y: auto;
  background: #f5f5f5;
  border-radius: 4px;
  padding: 12px;
}

.proposal-content {
  margin: 0;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
}

.d01-decision-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.d01-modify-builder {
  margin: 12px 0;
  padding: 12px;
  border: 1px dashed #ccc;
  border-radius: 8px;
}

.d01-section-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
}

.d01-modify-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.d01-modify-row input,
.d01-modify-row select {
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
}

.d01-modify-row select {
  min-width: 160px;
}

.d01-mod-list {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: grid;
  gap: 6px;
}

.d01-mod-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 6px 8px;
  background: #f7f7f7;
  border-radius: 6px;
}

.d01-mod-kind {
  font-weight: 600;
}

.d01-mod-detail {
  color: #666;
  overflow-wrap: anywhere;
  flex: 1;
}

.d01-reason-box {
  margin: 12px 0;
}

.d01-reason-box textarea {
  width: 100%;
  font-size: 12px;
  padding: 6px 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
  resize: vertical;
}

.d01-submit-row {
  margin-top: 8px;
}

.d01-decision-btn,
.d01-add,
.d01-submit {
  border: 1px solid #1976d2;
  background: #1976d2;
  color: #fff;
  border-radius: 6px;
  padding: 5px 12px;
  cursor: pointer;
  font-size: 12px;
}

.d01-decision-btn {
  background: #fff;
  color: #1976d2;
}

.d01-decision-btn.active {
  background: #1976d2;
  color: #fff;
}

.d01-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.d01-remove {
  border: none;
  background: transparent;
  color: #b91c1c;
  cursor: pointer;
  font-size: 12px;
}
</style>
