<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  RECOMMENDATION_DECISION_LABELS,
  RECOMMENDATION_RUN_STATUS_LABELS,
  STRUCTURED_MODIFICATION_KIND_LABELS,
  type ProductRecommendationProposalVersion,
  type ProductRecommendationRun,
  type RecommendationDecision,
  type StructuredModification,
  type StructuredModificationKind,
} from '../../api/productRecommendation'

const props = defineProps<{
  run: ProductRecommendationRun | null
  version: ProductRecommendationProposalVersion | null
  stale: boolean
}>()

const emit = defineEmits<{
  decide: [payload: { decision: RecommendationDecision; modifications?: StructuredModification[]; reason?: string }]
  rerun: []
}>()

const DECISIONS: RecommendationDecision[] = ['APPROVE', 'MODIFY', 'REJECT', 'HOLD']
const MODIFICATION_KINDS = Object.keys(STRUCTURED_MODIFICATION_KIND_LABELS) as StructuredModificationKind[]

const selected = ref<RecommendationDecision | null>(null)
const reason = ref('')
const modifications = ref<StructuredModification[]>([])

// 结构化修改项表单（MODIFY 专用；不编辑原始 JSON）
const modKind = ref<StructuredModificationKind>('REMOVE_CANDIDATE')
const modTargetProductId = ref('')
const modTargetPortfolioId = ref('')
const modFromPosition = ref<number | null>(null)
const modToPosition = ref<number | null>(null)
const modValue = ref('')
const modNote = ref('')

const hasVersion = computed(() => props.version != null)
const isStale = computed(() => props.stale || props.run?.status === 'STALE_REQUIRES_RERUN')
const canDecide = computed(() => hasVersion.value && !isStale.value)
const needsReason = computed(() => selected.value === 'REJECT' || selected.value === 'HOLD')
const canSubmit = computed(() => canDecide.value && selected.value != null && (!needsReason.value || reason.value.trim() !== ''))

function choose(decision: RecommendationDecision): void {
  if (!canDecide.value || (decision === 'APPROVE' && isStale.value) || (decision === 'MODIFY' && isStale.value)) {
    return
  }
  selected.value = decision
  if (decision !== 'MODIFY') {
    modifications.value = []
  }
}

function addModification(): void {
  const mod: StructuredModification = { kind: modKind.value }
  if (modTargetProductId.value.trim()) mod.targetProductId = modTargetProductId.value.trim()
  if (modTargetPortfolioId.value.trim()) mod.targetPortfolioId = modTargetPortfolioId.value.trim()
  if (modFromPosition.value != null) mod.fromPosition = modFromPosition.value
  if (modToPosition.value != null) mod.toPosition = modToPosition.value
  if (modValue.value.trim()) mod.value = modValue.value.trim()
  if (modNote.value.trim()) mod.note = modNote.value.trim()
  modifications.value = [...modifications.value, mod]
  modTargetProductId.value = ''
  modTargetPortfolioId.value = ''
  modFromPosition.value = null
  modToPosition.value = null
  modValue.value = ''
  modNote.value = ''
}

function removeModification(index: number): void {
  modifications.value = modifications.value.filter((_, i) => i !== index)
}

function submit(): void {
  if (!canSubmit.value) {
    return
  }
  emit('decide', {
    decision: selected.value as RecommendationDecision,
    modifications: selected.value === 'MODIFY' ? modifications.value : undefined,
    reason: reason.value.trim() || undefined,
  })
}

function reasonPlaceholder(): string {
  if (selected.value === 'REJECT') {
    return '驳回原因分类＋说明（REJECT 必填）'
  }
  if (selected.value === 'HOLD') {
    return '暂缓原因（HOLD 必填）'
  }
  return '决定说明（可选；高风险采纳建议填写）'
}
</script>

<template>
  <section class="decision" data-testid="recommendation-decision-panel">
    <h2>人工决定（第三段·HG-D01）</h2>

    <div v-if="isStale" class="stale-banner" data-testid="decision-stale-banner">
      <p>推荐已过期（STALE_REQUIRES_RERUN），须先重跑后才能批准。</p>
      <button type="button" class="rerun" data-testid="decision-rerun" @click="emit('rerun')">重跑推荐</button>
    </div>

    <dl v-if="run" class="meta">
      <div>
        <dt>运行状态</dt>
        <dd data-testid="decision-run-status">{{ RECOMMENDATION_RUN_STATUS_LABELS[run.status] }}</dd>
      </div>
      <div>
        <dt>方案版本</dt>
        <dd data-testid="decision-version">{{ version?.versionId || '尚未生成' }}</dd>
      </div>
    </dl>

    <div class="decision-buttons" data-testid="decision-buttons">
      <button
        v-for="d in DECISIONS"
        :key="d"
        type="button"
        class="decision-btn"
        :class="[`decision-${d.toLowerCase()}`, { active: selected === d }]"
        :data-testid="`decision-${d.toLowerCase()}`"
        :disabled="!canDecide || (isStale && (d === 'APPROVE' || d === 'MODIFY'))"
        @click="choose(d)"
      >
        {{ RECOMMENDATION_DECISION_LABELS[d] }}
      </button>
    </div>
    <p class="approve-note">
      APPROVE 仅表示允许候选进入 G2 方案装配，不代表产品/授信/价格/建议书审批。
    </p>

    <div v-if="selected === 'MODIFY'" class="modify-builder" data-testid="modify-builder">
      <h3>结构化修改项（不编辑原始 JSON）</h3>
      <div class="modify-row">
        <select v-model="modKind" data-testid="modify-kind" aria-label="修改类型">
          <option v-for="k in MODIFICATION_KINDS" :key="k" :value="k">
            {{ STRUCTURED_MODIFICATION_KIND_LABELS[k] }}
          </option>
        </select>
        <input v-model="modTargetProductId" type="text" placeholder="目标产品 ID（可选）" data-testid="modify-product-id" />
        <input v-model="modTargetPortfolioId" type="text" placeholder="目标组合 ID（可选）" data-testid="modify-portfolio-id" />
      </div>
      <div class="modify-row">
        <input v-model.number="modFromPosition" type="number" placeholder="原位置（可选）" data-testid="modify-from" />
        <input v-model.number="modToPosition" type="number" placeholder="新位置（可选）" data-testid="modify-to" />
        <input v-model="modValue" type="text" placeholder="值（后续行动/已确认事实，可选）" data-testid="modify-value" />
      </div>
      <div class="modify-row">
        <input v-model="modNote" type="text" placeholder="修改说明（可选）" data-testid="modify-note" />
        <button type="button" class="add" data-testid="modify-add" @click="addModification">添加修改项</button>
      </div>

      <ul v-if="modifications.length" class="mod-list" data-testid="modify-list">
        <li v-for="(m, idx) in modifications" :key="idx" class="mod-item">
          <span class="mod-kind">{{ STRUCTURED_MODIFICATION_KIND_LABELS[m.kind] }}</span>
          <span class="mod-detail">
            {{ [m.targetProductId, m.targetPortfolioId, m.value, m.note].filter(Boolean).join(' · ') || '—' }}
          </span>
          <button type="button" class="remove" :data-testid="`modify-remove-${idx}`" @click="removeModification(idx)">
            移除
          </button>
        </li>
      </ul>
    </div>

    <div v-if="needsReason" class="reason-box" data-testid="decision-reason-box">
      <label for="decision-reason">决定理由（必填）</label>
      <textarea
        id="decision-reason"
        v-model="reason"
        rows="2"
        :placeholder="reasonPlaceholder()"
        data-testid="decision-reason"
      />
    </div>

    <div class="submit-row">
      <button
        type="button"
        class="submit"
        data-testid="decision-submit"
        :disabled="!canSubmit"
        @click="submit"
      >
        确认决定
      </button>
      <span v-if="!hasVersion" class="hint" data-testid="decision-no-version-hint">尚未生成不可变方案版本，无法决定。</span>
      <span v-else-if="isStale" class="hint">推荐已过期，须先重跑。</span>
    </div>
  </section>
</template>

<style scoped>
.decision h2 {
  font-size: 16px;
  margin: 0 0 12px;
}
.stale-banner {
  margin-bottom: 12px;
  padding: 10px 12px;
  border: 1px solid rgba(217, 119, 6, 0.5);
  border-radius: 8px;
  background: rgba(217, 119, 6, 0.08);
  font-size: 13px;
  color: #92400e;
  display: flex;
  align-items: center;
  gap: 10px;
}
.stale-banner p {
  margin: 0;
}
.rerun {
  border: 1px solid #92400e;
  background: transparent;
  color: #92400e;
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 12px;
}
.meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 0 0 12px;
}
.meta div {
  padding: 8px 10px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}
dt {
  font-size: 12px;
  color: var(--text-tertiary);
}
dd {
  margin: 2px 0 0;
  font-size: 13px;
}
.decision-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.decision-btn {
  border: 1px solid var(--border-light);
  background: var(--bg-surface);
  border-radius: 8px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
}
.decision-btn.active {
  border-color: var(--gits-blue-600, #1976d2);
  color: var(--gits-blue-600, #1976d2);
}
.decision-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
.decision-approve.active {
  border-color: #087771;
  color: #087771;
}
.approve-note {
  margin: 8px 0 12px;
  font-size: 12px;
  color: var(--text-tertiary);
}
.modify-builder {
  margin: 12px 0;
  padding: 12px;
  border: 1px dashed var(--border-light);
  border-radius: 8px;
}
.modify-builder h3 {
  margin: 0 0 8px;
  font-size: 13px;
}
.modify-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}
.modify-row input,
.modify-row select {
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background: var(--bg-surface);
}
.modify-row select {
  min-width: 160px;
}
.add,
.submit {
  border: 1px solid var(--gits-blue-600, #1976d2);
  background: var(--gits-blue-600, #1976d2);
  color: #fff;
  border-radius: 6px;
  padding: 5px 12px;
  cursor: pointer;
  font-size: 12px;
}
.mod-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 6px;
}
.mod-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 6px 8px;
  background: var(--bg-hover);
  border-radius: 6px;
}
.mod-kind {
  font-weight: 600;
}
.mod-detail {
  color: var(--text-secondary);
  overflow-wrap: anywhere;
  flex: 1;
}
.remove {
  border: none;
  background: transparent;
  color: #b91c1c;
  cursor: pointer;
  font-size: 12px;
}
.reason-box {
  margin: 12px 0;
  display: grid;
  gap: 4px;
}
.reason-box label {
  font-size: 12px;
  color: var(--text-tertiary);
}
.reason-box textarea {
  font-size: 12px;
  padding: 6px 8px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  resize: vertical;
  background: var(--bg-surface);
}
.submit-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.hint {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
