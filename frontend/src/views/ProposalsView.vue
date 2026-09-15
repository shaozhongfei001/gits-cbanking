<script setup lang="ts">
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'

const page = PROPOSAL_SHELL_PAGES.P23
</script>

<template>
  <ProposalDegradeShell v-bind="page">
    <template #toolbar>
      <router-link class="new-btn" to="/proposals/new" data-testid="p23-open-wizard">
        新建建议书
      </router-link>
    </template>
    <p class="empty" data-testid="p23-empty">暂无正式建议书对象。请点右上「新建建议书」向 DKWS 请求非正式草稿。</p>
  </ProposalDegradeShell>
</template>

<style scoped>
.empty {
  display: block;
  color: var(--text-tertiary);
  font-size: 13px;
  margin: 0 0 12px;
}
.new-btn {
  display: inline-flex;
  align-items: center;
  height: 32px;
  padding: 0 14px;
  border: 1px solid var(--gits-blue-600, #1976d2);
  border-radius: 6px;
  color: var(--gits-blue-600, #1976d2);
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}
.new-btn:hover {
  background: #eaf4fe;
}
</style>
