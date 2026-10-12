<script setup lang="ts">
/**
 * P25 建议书记录 — 非正式建议书草稿「详情页」（C3 阶段机降级）。
 *
 * 详情构成：
 * - 对象元数据：客户、建议书名称、生成时间、对象状态、运行标识（runId）；
 * - 正文详情：`ProposalDraftView` 的章节卡片 + 引用/待确认/边界/闸门/违规面板 + 原始 Markdown；
 * - 阶段说明：G0–G5 阶段机 C3 未授权（可折叠，不占版面）。
 *
 * 红线：
 * - 本页**只读**：不提供晋级、不提供回写、不调用建议书写接口；
 * - 未命中会话暂存时**不得编造正文**，只显示占位事实 + 明确出口（返回列表 / 重新生成）。
 */
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import ProposalDraftView from '../components/proposal/ProposalDraftView.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'
import { formatKertTimestamp, useProposalDraftStore } from '../stores/proposalDraft'

const page = PROPOSAL_SHELL_PAGES.P25

const route = useRoute()
const router = useRouter()
const draftStore = useProposalDraftStore()

/** 阶段说明是否折叠 */
const stageCollapsed = ref(false)

/**
 * 本次浏览器会话内由 P24 生成的非正式草稿。
 * 命中 ⇒ 展示完整详情；未命中（跨会话 / 直接深链）⇒ 占位事实 + 明确出口，不编造正文。
 */
const recordId = computed(() => String(route.params.id || ''))
const record = computed(() => draftStore.find(recordId.value))

const STATUS_LABEL: Record<string, string> = {
  INFORMAL: '非正式草稿（未落库）',
  DRAFT: '草稿',
  REVIEW: '评审中',
  APPROVED: '已批准',
}

const statusLabel = computed(() => {
  if (!record.value) return '—'
  return STATUS_LABEL[record.value.status] ?? record.value.status
})

/**
 * 打开推荐工作区（G2 消费已决定采用的推荐子方案）。
 * 本分支无持久化 run 关联：优先用 query.runId 打开既有运行；否则进入发起模式。
 */
function openRecommendationWorkspace() {
  const linkedRunId = String(route.query.runId || '')
  router.push({
    name: 'ProductRecommendationWorkspace',
    params: { runId: linkedRunId || 'new' },
    query: route.query.customerId ? { customerId: String(route.query.customerId) } : {},
  })
}

function goList() {
  router.push({ name: 'ProposalsHome' })
}

function goWizard() {
  const customerId = record.value?.customerId || String(route.query.customerId || '')
  router.push({
    name: 'ProposalWizard',
    query: customerId ? { customerId } : {},
  })
}
</script>

<template>
  <ProposalDegradeShell v-bind="page">
    <template #toolbar>
      <button
        type="button"
        class="open-rec"
        data-testid="p25-open-recommendation"
        @click="openRecommendationWorkspace"
      >
        打开推荐工作区
      </button>
      <NButton v-if="record" size="small" data-testid="p25-back-list" @click="goList">返回列表</NButton>
      <NButton v-if="record" size="small" data-testid="p25-regenerate" @click="goWizard">
        重新生成草稿
      </NButton>
    </template>

    <template #default="{ placeholder }">
    <!-- 命中会话暂存 ⇒ 完整详情 -->
    <section v-if="record" class="record-detail" data-testid="p25-skill-draft">
      <dl class="facts">
        <div>
          <dt>客户</dt>
          <dd>{{ record.customerName }}（{{ record.customerId }}）</dd>
        </div>
        <div>
          <dt>建议书名称</dt>
          <dd>{{ record.proposalName }}</dd>
        </div>
        <div>
          <dt>生成时间</dt>
          <dd>{{ formatKertTimestamp(record.generatedAt) }}</dd>
        </div>
        <div>
          <dt>对象状态</dt>
          <dd>{{ statusLabel }}</dd>
        </div>
        <div>
          <dt>运行标识（KERT runId）</dt>
          <dd class="mono">{{ record.id }}</dd>
        </div>
      </dl>
      <ProposalDraftView :proposal="record.proposal" />
    </section>

    <!-- 未命中会话暂存 ⇒ 占位事实 + 明确出口（不编造正文） -->
    <section v-else-if="placeholder" class="record">
      <dl class="facts">
        <div>
          <dt>占位对象 ID（路由 param，非正式）</dt>
          <dd>{{ placeholder.placeholderId }}</dd>
        </div>
        <div>
          <dt>对象标记</dt>
          <dd>{{ placeholder.degradeLabel }}</dd>
        </div>
      </dl>

      <p class="miss-note" data-testid="p25-not-cached">
        该对象不在本次浏览器会话的暂存中（C2 降级草稿不落库，关闭标签页或换浏览器即失效）。
        请返回列表选择已有草稿，或重新向 KERT 请求草稿。
      </p>
      <div class="miss-actions">
        <NButton size="small" data-testid="p25-miss-back-list" @click="goList">返回列表</NButton>
        <NButton size="small" type="primary" data-testid="p25-miss-regenerate" @click="goWizard">
          新建建议书
        </NButton>
      </div>
    </section>

    <!-- 可折叠阶段说明（两种分支都展示：本分支草稿一律不可晋级） -->
    <div class="stage-notice" :class="{ 'is-collapsed': stageCollapsed }" data-testid="p25-stage-notice">
      <div class="stage-summary" @click="stageCollapsed = !stageCollapsed">
        <span class="stage-icon">{{ stageCollapsed ? '▸' : '▾' }}</span>
        <span class="stage-text">阶段机 C3 未授权 — 点击{{ stageCollapsed ? '展开' : '收起' }}详情</span>
      </div>
      <div v-show="!stageCollapsed" class="stage-detail">
        <p>阶段机 C3 未授权。本页仅静态说明，不提供可点晋级或回写。</p>
        <p>G0–G5 不是本分支合同对象，禁止把占位 ID 或非正式草稿当作正式建议书阶段。</p>
      </div>
    </div>
    </template>
  </ProposalDegradeShell>
</template>

<style scoped>
.open-rec {
  border: 1px solid var(--brand-primary);
  background: var(--brand-primary);
  color: #fff;
  border-radius: 6px;
  padding: 5px 14px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.15s ease;
}
.open-rec:focus-visible {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
}

.record-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 10px;
  margin: 0 0 4px;
}

.facts div {
  padding: 10px 12px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 8px;
}

dt {
  font-size: 12px;
  color: var(--v8-nav-text);
}

dd {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  word-break: break-word;
}

dd.mono {
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 12px;
}

.miss-note {
  margin: 0 0 10px;
  font-size: 13px;
  line-height: 1.7;
  color: #92400e;
}

.miss-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

/* ── 可折叠阶段说明 ── */
.stage-notice {
  margin-bottom: 12px;
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.03);
  overflow: hidden;
  transition: all 0.2s ease;
}

.stage-notice.is-collapsed {
  background: transparent;
  border-color: transparent;
}

.stage-summary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
}

.stage-notice.is-collapsed .stage-summary {
  padding: 4px 0;
}

.stage-icon {
  flex-shrink: 0;
  font-size: 11px;
  color: var(--v8-nav-text);
}

.stage-text {
  font-size: 12px;
  line-height: 1.5;
  color: var(--v8-nav-text);
}

.stage-detail {
  padding: 0 12px 10px 28px;
}

.stage-detail p {
  margin: 0 0 6px;
  color: var(--text-secondary);
  font-size: 13px;
}

.stage-detail p:last-child {
  margin-bottom: 0;
}
</style>
