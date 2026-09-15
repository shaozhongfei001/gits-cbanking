<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'
import { fetchCustomers, formatApiError, type Customer } from '../api/engagement'
import { generateServiceProposal, type ServiceProposal } from '../api/v14'

const page = PROPOSAL_SHELL_PAGES.P24
const route = useRoute()
const customers = ref<Customer[]>([])
const customerId = ref('')
const loadingSkill = ref(false)
const skillError = ref('')
const proposal = ref<ServiceProposal | null>(null)

const draft = computed(() => proposal.value?.content?.proposalDraft?.trim() || '')
const citations = computed(() => proposal.value?.citations || [])
const unknowns = computed(() => proposal.value?.unknowns || [])
const limitations = computed(() => proposal.value?.limitations || [])

onMounted(async () => {
  try {
    customers.value = await fetchCustomers()
  } catch {
    customers.value = []
  }
  const fromQuery = String(route.query.customerId || '')
  const preferred = (fromQuery && customers.value.find(c => c.customerId === fromQuery)?.customerId)
    || customers.value.find(c => c.customerId === 'CUST-CORP-0001')?.customerId
    || customers.value[0]?.customerId
    || ''
  customerId.value = preferred
})

async function requestDraft() {
  if (!customerId.value || loadingSkill.value) {
    return
  }
  loadingSkill.value = true
  skillError.value = ''
  proposal.value = null
  try {
    const requestId = `REQ-SP20-${crypto.randomUUID()}`
    proposal.value = await generateServiceProposal(requestId, customerId.value, {})
  } catch (e: unknown) {
    skillError.value = formatApiError(e, 'DKWS 未返回建议书草稿')
  } finally {
    loadingSkill.value = false
  }
}
</script>

<template>
  <ProposalDegradeShell v-bind="page" v-slot="{ wizard }">
    <section v-if="wizard" class="wizard" data-testid="p24-empty-draft">
      <p>空草稿：未创建正式建议书对象。{{ wizard.degradeLabel }}。选择客户后可请求 DKWS <code>SP-20</code>。</p>
      <div class="row">
        <label for="p24-customer">客户</label>
        <select id="p24-customer" v-model="customerId" data-testid="p24-customer">
          <option value="" disabled>请选择客户</option>
          <option v-for="c in customers" :key="c.customerId" :value="c.customerId">
            {{ c.customerName }}（{{ c.customerId }}）
          </option>
        </select>
        <button
          type="button"
          class="gen-btn"
          data-testid="p24-generate"
          :disabled="!customerId || loadingSkill"
          @click="requestDraft"
        >
          {{ loadingSkill ? '正在请求 DKWS SP-20…' : '请求 DKWS 生成草稿' }}
        </button>
      </div>
      <p v-if="skillError" class="err" data-testid="p24-skill-error">{{ skillError }}</p>
      <p v-else-if="proposal && !draft" class="empty" data-testid="p24-skill-empty">DKWS 未返回建议书草稿</p>
      <article v-if="draft" class="draft" data-testid="p24-skill-draft">
        <h3>非正式草稿 · {{ proposal?.skillId || 'SP-20' }} · {{ proposal?.status || '' }}</h3>
        <pre>{{ draft }}</pre>
        <p v-if="unknowns.length"><b>待确认</b>：{{ unknowns.map(u => u.description).join('；') }}</p>
        <p v-if="citations.length"><b>引用</b>：{{ citations.length }} 条</p>
        <p v-if="limitations.length"><b>边界</b>：{{ limitations.join('；') }}</p>
      </article>
    </section>
  </ProposalDegradeShell>
</template>

<style scoped>
.wizard p {
  margin: 0 0 12px;
  color: var(--text-secondary);
}
.row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 16px;
}
.row label {
  font-size: 13px;
  color: var(--gits-muted, #596779);
}
.row select {
  min-width: 280px;
  height: 32px;
  border: 1px solid var(--gits-line, #d8e2ec);
  border-radius: 6px;
  padding: 0 8px;
}
.gen-btn {
  height: 32px;
  padding: 0 14px;
  border: 0;
  border-radius: 6px;
  background: var(--gits-blue-600, #1976d2);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}
.gen-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.err {
  color: #b42318;
  font-size: 13px;
}
.empty {
  color: var(--text-tertiary);
  font-size: 13px;
}
.draft {
  background: #fff;
  border: 1px solid var(--gits-line, #d8e2ec);
  border-left: 3px solid var(--gits-blue-600, #1976d2);
  border-radius: 6px;
  padding: 14px 16px;
}
.draft h3 {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--gits-navy-800, #0b2e4f);
}
.draft pre {
  margin: 0 0 12px;
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.6;
  color: var(--gits-text, #1b2632);
}
</style>
