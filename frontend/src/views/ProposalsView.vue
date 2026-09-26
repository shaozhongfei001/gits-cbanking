<script setup lang="ts">
/**
 * P23 建议书对象主页 — 非正式建议书列表（C2 降级）。
 *
 * 职责：
 * - 工具条：「新建建议书」跳转 P24 新建向导页；「导入草稿」禁用并给出降级原因；
 * - 列表：客户、建议书名称、生成时间、状态 + 建议书要素列（章数/技能/引用/待确认/边界）+ 查看详情；
 * - **对象可查看详情**：行点击、名称链接、「查看详情」按钮三种入口均进入 P25 详情页；
 * - 数据来源：`useProposalDraftStore`（KERT SP-20 已生成草稿的浏览器会话内暂存）。
 *
 * 红线（C2 降级）：
 * - **不调用建议书写接口**（不 POST/PUT proposal），不落库、不写入 G0–G5；
 * - 空列表显示空态，不编造建议书行（`loadProposalShellList` 恒返回 `[]`）。
 */
import { computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NDataTable, NEmpty, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import ProposalDegradeShell from '../components/shell/ProposalDegradeShell.vue'
import { PROPOSAL_SHELL_PAGES } from '../composables/proposalDegrade'
import { formatKertTimestamp, useProposalDraftStore, type ProposalDraftRecord } from '../stores/proposalDraft'

const page = PROPOSAL_SHELL_PAGES.P23
const router = useRouter()
const draftStore = useProposalDraftStore()

const columns = computed<DataTableColumns<ProposalDraftRecord>>(() => [
  {
    title: '客户',
    key: 'customerName',
    width: 200,
    ellipsis: { tooltip: true },
    render: row => row.customerName || row.customerId || '—',
  },
  {
    title: '建议书名称',
    key: 'proposalName',
    minWidth: 260,
    ellipsis: { tooltip: true },
    // 名称即详情入口：渲染为真实链接（支持中键/右键新开），左键走前端路由
    render(row) {
      return h(
        'a',
        {
          class: 'proposal-link',
          href: detailHref(row.id),
          'data-testid': `p23-proposal-link-${row.id}`,
          onClick: (event: MouseEvent) => {
            event.preventDefault()
            event.stopPropagation()
            openDraft(row.id)
          },
        },
        row.proposalName,
      )
    },
  },
  {
    title: '生成时间',
    key: 'generatedAt',
    width: 170,
    render: row => formatKertTimestamp(row.generatedAt),
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      const statusMap: Record<string, { type: 'default' | 'info' | 'success' | 'warning'; label: string }> = {
        INFORMAL: { type: 'info', label: '非正式草稿' },
        DRAFT: { type: 'warning', label: '草稿' },
        REVIEW: { type: 'default', label: '评审中' },
        APPROVED: { type: 'success', label: '已批准' },
      }
      const status = statusMap[row.status] ?? { type: 'default' as const, label: row.status }
      return h(NTag, { size: 'small', type: status.type, bordered: true }, () => status.label)
    },
  },
  {
    title: '章数',
    key: 'chapterCount',
    width: 70,
    align: 'center',
    render: row => row.chapterCount || 0,
  },
  {
    title: '技能',
    key: 'skillId',
    width: 80,
    render: row => row.skillId || '—',
  },
  {
    title: '引用',
    key: 'citationCount',
    width: 70,
    align: 'center',
    render: row => row.citationCount || 0,
  },
  {
    title: '待确认',
    key: 'unknownCount',
    width: 80,
    align: 'center',
    render(row) {
      const count = row.unknownCount || 0
      return count > 0
        ? h(NTag, { size: 'small', type: 'warning', bordered: true }, () => String(count))
        : '0'
    },
  },
  {
    title: '边界',
    key: 'limitationCount',
    width: 70,
    align: 'center',
    render: row => row.limitationCount || 0,
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render(row) {
      return h(
        NButton,
        {
          size: 'tiny',
          type: 'primary',
          secondary: true,
          'data-testid': `p23-view-detail-${row.id}`,
          onClick: (event: MouseEvent) => {
            event.stopPropagation()
            openDraft(row.id)
          },
        },
        () => '查看详情',
      )
    },
  },
])

/** 详情页 href（供链接语义与「新开标签」使用）。 */
function detailHref(id: string): string {
  return router.resolve({ name: 'ProposalRecord', params: { id } }).href
}

function openDraft(id: string) {
  router.push({ name: 'ProposalRecord', params: { id } })
}

/**
 * 行级交互：整行可点开详情；支持 Enter / 空格键盘操作（链接与按钮无需冒泡）。
 */
function rowProps(row: ProposalDraftRecord) {
  return {
    class: 'proposal-row',
    style: 'cursor: pointer;',
    tabindex: 0,
    title: '点击查看建议书详情',
    'data-testid': `p23-row-${row.id}`,
    onClick: () => openDraft(row.id),
    onKeydown: (event: KeyboardEvent) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        openDraft(row.id)
      }
    },
  }
}

function goNewProposal() {
  router.push({ name: 'ProposalWizard' })
}
</script>

<template>
  <ProposalDegradeShell v-bind="page">
    <!-- 工具条：「导入草稿」由降级壳的 DisabledAction 统一提供（含禁用原因），此处不重复渲染 -->
    <template #toolbar>
      <NButton type="primary" size="small" data-testid="p23-new-proposal" @click="goNewProposal">
        + 新建建议书
      </NButton>
    </template>

    <div class="proposal-list" data-testid="p23-proposal-list">
      <NDataTable
        v-if="draftStore.drafts.length > 0"
        :columns="columns"
        :data="draftStore.drafts"
        :bordered="false"
        :single-line="false"
        size="small"
        :row-key="(row: ProposalDraftRecord) => row.id"
        :row-props="rowProps"
        :max-height="620"
        :scroll-x="1240"
      />
      <NEmpty v-else data-testid="p23-empty" description="暂无建议书。点击「新建建议书」向 KERT 请求非正式草稿。" />
    </div>
  </ProposalDegradeShell>
</template>

<style scoped>
.proposals-page {
  max-width: 1240px;
  padding: 32px 34px 48px;
}
.proposal-list {
  margin-top: 12px;
}

.proposal-list :deep(.proposal-row:hover) {
  background: var(--brand-primary-lighter, #eaf4fe);
}

.proposal-list :deep(.proposal-row:focus-visible) {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: -2px;
}

.proposal-list :deep(.proposal-link) {
  color: var(--brand-primary);
  font-weight: 600;
  text-decoration: none;
}

.proposal-list :deep(.proposal-link:hover) {
  text-decoration: underline;
}

.proposal-list :deep(.proposal-link:focus-visible) {
  outline: 2px solid var(--v8-focus-on-light);
  outline-offset: 2px;
  border-radius: 2px;
}
</style>
