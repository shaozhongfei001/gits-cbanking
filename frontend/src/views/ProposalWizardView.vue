<script setup lang="ts">
/**
 * P24 新建建议书向导 — 选择客户 → 请求 KERT SP-20 → 卡片式草稿展示。
 *
 * 流程（单页内完成，不再使用弹窗）：
 * 1. 选择客户（支持 `/proposals/new?customerId=…` 深链）；
 * 2. 点击「请求 KERT 生成草稿」调用 SP-20（`POST /api/v14/proposals`）；
 * 3. 回包后把非正式草稿写入 `useProposalDraftStore`（内存暂存，供 P23 列表与 P25 记录页读取），
 *    并在本页以**章节卡片**呈现（`ProposalDraftView`）。
 *
 * 红线（C2 降级）：
 * - 「保存并继续」保持置灰：本分支无建议书工厂合同，禁止把草稿落库为正式建议书对象；
 * - 失败必须显式报错（`p24-skill-error`），不得静默降级为「无草稿」。
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NSpin, NTag } from 'naive-ui'
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import ProposalDraftView from '../components/proposal/ProposalDraftView.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'
import { splitProposalDraft } from '../composables/proposalDraft'
import { fetchCustomers, formatApiError, type Customer } from '../api/engagement'
import { generateServiceProposal, type ServiceProposal } from '../api/v14'
import { useProposalDraftStore } from '../stores/proposalDraft'

const page = PROPOSAL_SHELL_PAGES.P24
const route = useRoute()
const router = useRouter()
const draftStore = useProposalDraftStore()

const customers = ref<Customer[]>([])
const customerId = ref('')
const loadingSkill = ref(false)
const skillError = ref('')
const proposal = ref<ServiceProposal | null>(null)
/** 本次生成在会话暂存中的记录 ID（详情页路由 param） */
const recordId = ref('')

const draft = computed(() => proposal.value?.content?.proposalDraft?.trim() || '')
const hasDraft = computed(() => draft.value.length > 0)

onMounted(async () => {
  try {
    customers.value = await fetchCustomers()
  } catch {
    customers.value = []
  }
  const fromQuery = String(route.query.customerId || '')
  customerId.value = (fromQuery && customers.value.find(c => c.customerId === fromQuery)?.customerId)
    || customers.value.find(c => c.customerId === 'CUST-CORP-0001')?.customerId
    || customers.value[0]?.customerId
    || ''
})

async function requestDraft() {
  if (!customerId.value || loadingSkill.value) return
  loadingSkill.value = true
  skillError.value = ''
  proposal.value = null
  try {
    const requestId = `REQ-SP20-${crypto.randomUUID()}`
    const result = await generateServiceProposal(requestId, customerId.value, {})
    proposal.value = result
    recordId.value = registerDraft(result)
  } catch (e: unknown) {
    skillError.value = formatApiError(e, 'KERT 未返回建议书草稿')
  } finally {
    loadingSkill.value = false
  }
}

/** 把非正式草稿写入会话暂存（供列表/详情页读取，不落库、不调写接口），并返回记录 ID。 */
function registerDraft(result: ServiceProposal): string {
  const customer = customers.value.find(c => c.customerId === customerId.value)
  const customerName = customer?.customerName || customerId.value
  const outline = splitProposalDraft(result.content?.proposalDraft || '')
  const id = result.runId || `REQ-SP20-${Date.now()}`
  draftStore.add({
    id,
    customerId: customerId.value,
    customerName,
    proposalName: `${customerName} — 非正式建议书草稿`,
    generatedAt: result.timestamp || new Date().toISOString().slice(0, 19).replace('T', ' '),
    status: 'INFORMAL',
    skillId: result.skillId || 'SP-20',
    chapterCount: outline.chapters.length,
    citationCount: result.citations?.length || 0,
    unknownCount: result.unknowns?.length || 0,
    limitationCount: result.limitations?.length || 0,
    proposal: result,
  })
  return id
}

function goList() {
  router.push({ name: 'ProposalsHome' })
}

/** 打开详情页（P25）；记录 ID 由 registerDraft 保证非空。 */
function goRecord() {
  if (!recordId.value) return
  router.push({ name: 'ProposalRecord', params: { id: recordId.value } })
}
</script>

<template>
  <ProposalDegradeShell v-bind="page" v-slot="{ wizard }">
    <section v-if="wizard" class="wizard" data-testid="p24-empty-draft">
      <!-- 1 选择客户 + 请求草稿 -->
      <div class="wizard-form">
        <div class="form-row">
          <NTag size="small" type="warning" :bordered="true" data-testid="p24-degrade-label">
            {{ wizard.degradeLabel }}
          </NTag>
          <label for="p24-customer" class="form-label">选择客户</label>
          <select id="p24-customer" v-model="customerId" class="form-select" data-testid="p24-customer">
            <option value="" disabled>请选择客户</option>
            <option v-for="c in customers" :key="c.customerId" :value="c.customerId">
              {{ c.customerName }}（{{ c.customerId }}）
            </option>
          </select>
          <NButton
            type="primary"
            :disabled="!customerId || loadingSkill"
            :loading="loadingSkill"
            data-testid="p24-generate"
            @click="requestDraft"
          >
            {{ loadingSkill ? '正在请求 KERT SP-20…' : (hasDraft ? '重新生成草稿' : '请求 KERT 生成草稿') }}
          </NButton>
          <NButton v-if="hasDraft" data-testid="p24-back-list" @click="goList">返回列表</NButton>
          <NButton v-if="hasDraft" data-testid="p24-open-record" @click="goRecord">查看详情</NButton>
        </div>
        <p class="form-note">
          草稿由 KERT SP-20 基于客户知识生成，属<b>非正式草稿</b>，仅供人工审阅；正式保存需建议书工厂合同批准后由独立 Loop 启用。
        </p>
        <p v-if="skillError" class="err" data-testid="p24-skill-error">{{ skillError }}</p>
      </div>

      <!-- 2 加载中 -->
      <div v-if="loadingSkill" class="loading-state" data-testid="p24-loading">
        <NSpin size="medium" />
        <span class="loading-text">正在请求 KERT SP-20 生成建议书草稿…</span>
      </div>

      <!-- 3 回包但草稿为空 -->
      <p v-else-if="proposal && !hasDraft" class="empty" data-testid="p24-skill-empty">
        KERT 未返回建议书草稿
      </p>

      <!-- 4 卡片式草稿 -->
      <div v-if="hasDraft && proposal" class="draft-container" data-testid="p24-skill-draft">
        <ProposalDraftView :proposal="proposal" />
      </div>
    </section>
  </ProposalDegradeShell>
</template>

<style scoped>
.wizard {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1240px;
  padding: 32px 34px 48px;
}

/* ── 表单区 ── */
.wizard-form {
  padding: 16px 18px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.form-label {
  font-size: 13px;
  color: var(--v8-nav-text);
}

.form-select {
  min-width: 280px;
  height: 34px;
  padding: 0 10px;
  font-size: 13px;
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 6px;
}

.form-note {
  margin: 10px 0 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--v8-nav-text);
}

.err {
  margin: 10px 0 0;
  font-size: 13px;
  color: #b42318;
}

.empty {
  font-size: 13px;
  color: var(--v8-nav-text);
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 0;
}

.loading-text {
  font-size: 14px;
  color: var(--v8-nav-text);
}

.draft-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
