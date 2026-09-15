<script setup lang="ts">
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'

const page = PROPOSAL_SHELL_PAGES.P28
</script>

<template>
  <ProposalDegradeShell v-bind="page" v-slot="{ placeholder }">
    <section v-if="placeholder" class="evidence">
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
      <p class="note" data-testid="p28-evidence-note">
        当前不可反查：无建议书正文合同、无 AI 内容与 Evidence 绑定接口；AI 输出仍为候选
        Claim，不得当作正式依据。{{ placeholder.contractNote }}
      </p>
    </section>
  </ProposalDegradeShell>
</template>

<style scoped>
.facts {
  display: grid;
  gap: 12px;
  margin: 0 0 16px;
}
.facts div,
.note {
  padding: 12px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 8px;
}
dt {
  font-size: 12px;
  color: var(--text-tertiary);
}
dd {
  margin: 4px 0 0;
}
.note {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
