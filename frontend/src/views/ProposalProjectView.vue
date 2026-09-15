<script setup lang="ts">
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'

const page = PROPOSAL_SHELL_PAGES.P29
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
        <dt>对照说明</dt>
        <dd>内部版与客户版对照仅为降级壳，隐藏规则不可查看。{{ placeholder.contractNote }}</dd>
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
