<script setup lang="ts">
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'

const page = PROPOSAL_SHELL_PAGES.P30
</script>

<template>
  <ProposalDegradeShell v-bind="page" v-slot="{ placeholder }">
    <dl v-if="placeholder" class="facts">
      <div>
        <dt>占位对象 ID（路由 param，非正式）</dt>
        <dd>{{ placeholder.placeholderId }}</dd>
      </div>
      <div>
        <dt>对象标记</dt>
        <dd>{{ placeholder.degradeLabel }}</dd>
      </div>
      <div>
        <dt>版本说明</dt>
        <dd>无 ProposalVersion 合同，不可创建或恢复版本。{{ placeholder.contractNote }}</dd>
      </div>
    </dl>
  </ProposalDegradeShell>
</template>

<style scoped>
.facts {
  display: grid;
  gap: 12px;
  margin: 0;
}
.facts div {
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
</style>
