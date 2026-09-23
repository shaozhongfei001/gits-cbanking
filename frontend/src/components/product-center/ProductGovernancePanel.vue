<script setup lang="ts">
/**
 * 右侧知识治理栏（需求 02 §6-5）。
 *
 * PC1 范围：当前知识版本、生效日与复审日、审核发布状态、固定边界声明。
 * 以下能力按批次接入，未接入时显式标注（不得以假数据或空白冒充）：
 * - 产品归属与知识责任人 → PC4（知识治理）
 * - 完整度与缺口明细 → PC4（PI-FR-082 确定性规则计算）
 * - 制度与证据、条款定位 → PC4
 * - 产品知识助手 → PC5
 */
import { computed } from 'vue'
import { NTag } from 'naive-ui'
import type { ProductCenterDetail } from '../../api/productCenter'

const props = defineProps<{
  detail: ProductCenterDetail
  /** C11 不可变版本语义：产品卡第 11 节原文（定位不到则 null ⇒ 具名标注）。 */
  immutableVersion?: { title: string; content: string } | null
  /** 产品卡来源（**相对路径**，用于"相对来源标识"）。 */
  cardSourceFile?: string | null
}>()

const PENDING_ITEMS = [
  { label: '知识完整度与缺口', loop: 'PC4' },
  { label: '制度与证据', loop: 'PC4' },
  { label: '知识责任人与归属', loop: 'PC4' }
]

/**
 * C11（不可变版本语义）在本区的承载（PC-i1 · W1-c）。
 *
 * 要求原文：「C11（不可变版本语义）须在版本区承载该节语义，**不得仅以版本徽章敷衍**」
 * ⇒ 本区并列给出：① 语义陈述；② 本页版本的**事实字段**；③ 产品卡第 11 节**原文** + 相对来源。
 * 不生成、不改写、不补全任何业务文本；缺失则具名标注。
 */
const immutableFacts = computed(
  () =>
    `${props.detail.version.versionStatus}（${props.detail.version.versionLabel}）｜` +
    `生效日：${props.detail.version.effectiveFrom || '未设定'}`
)

function orPending(value: string | null | undefined) {
  return value && value.trim().length > 0 ? value : null
}
</script>

<template>
  <aside class="pc-gov" data-testid="pc-governance">
    <section class="pc-gov-block">
      <h2 class="pc-gov-title">当前知识版本</h2>
      <dl class="pc-gov-list">
        <div><dt>版本标识</dt><dd data-testid="pc-gov-version-id">{{ detail.version.versionId }}</dd></div>
        <div><dt>版本标签</dt><dd>{{ detail.version.versionLabel }}</dd></div>
        <div>
          <dt>发布状态</dt>
          <dd>
            <n-tag size="tiny" :bordered="true" type="warning">{{ detail.version.versionStatus }}</n-tag>
          </dd>
        </div>
        <div>
          <dt>知识基准日</dt>
          <dd :class="{ 'is-missing': !orPending(detail.version.knowledgeAsOf) }">
            {{ orPending(detail.version.knowledgeAsOf) || '基准日待维护' }}
          </dd>
        </div>
        <div>
          <dt>生效日</dt>
          <dd :class="{ 'is-missing': !orPending(detail.version.effectiveFrom) }">
            {{ orPending(detail.version.effectiveFrom) || '未设定' }}
          </dd>
        </div>
        <div>
          <dt>复审日</dt>
          <dd :class="{ 'is-missing': !orPending(detail.version.nextReviewAt) }">
            {{ orPending(detail.version.nextReviewAt) || '未设定' }}
          </dd>
        </div>
        <div>
          <dt>审核记录</dt>
          <dd :class="{ 'is-missing': detail.version.reviewedBy.length === 0 }">
            {{ detail.version.reviewedBy.length > 0 ? detail.version.reviewedBy.join('、') : '无审核记录（不得视为已审核）' }}
          </dd>
        </div>
        <div><dt>版本说明</dt><dd>{{ detail.version.changeSummary }}</dd></div>
      </dl>
    </section>

    <section class="pc-gov-block" data-testid="pc-immutable-version">
      <h2 class="pc-gov-title">版本语义（不可变版本）</h2>
      <p class="pc-gov-note" data-testid="pc-immutable-statement">
        受控版本不可变：内容变更须发布新版本，历史版本与废止/失效状态须可追溯，不得就地覆盖。
      </p>
      <p class="pc-gov-note" data-testid="pc-immutable-facts">
        本页当前版本状态：{{ immutableFacts }}
      </p>
      <template v-if="immutableVersion">
        <p class="pc-gov-source" data-testid="pc-immutable-source">
          第 11 节原文 · 来源：{{ cardSourceFile || '来源标识不可得' }}
        </p>
        <pre class="pc-gov-content" data-testid="pc-immutable-content">{{ immutableVersion.content }}</pre>
      </template>
      <p v-else class="pc-gov-note" data-testid="pc-immutable-absent">
        该产品卡未包含第 11 节（不可变版本语义）原文 —— 如实标注，不以示意内容填充。
      </p>
    </section>

    <section class="pc-gov-block">
      <h2 class="pc-gov-title">治理与证据</h2>
      <ul class="pc-gov-pending">
        <li v-for="item in PENDING_ITEMS" :key="item.label" data-testid="pc-gov-pending">
          <span>{{ item.label }}</span>
          <n-tag size="tiny" :bordered="true">待接入 {{ item.loop }}</n-tag>
        </li>
      </ul>
    </section>

    <section class="pc-gov-block">
      <h2 class="pc-gov-title">数据来源声明</h2>
      <dl class="pc-gov-list">
        <div>
          <dt>数据环境</dt>
          <dd data-testid="pc-data-environment">
            {{ detail.version.environment }}{{ detail.version.isDemo ? '（演示数据）' : '' }}
          </dd>
        </div>
      </dl>
      <p class="pc-gov-note" data-testid="pc-data-provenance">
        演示数据不代表真实银行制度、价目或协议，禁止对客引用；
        演示数据试图进入生产正式版本时，发布流程应当阻断。
      </p>
    </section>

    <section class="pc-gov-block">
      <h2 class="pc-gov-title">产品知识助手</h2>
      <p v-if="!detail.assistant.enabled" class="pc-gov-note" data-testid="pc-assistant-disabled">
        助手由 PC5 接入：无证据必须拒答、回答必须回链证据并携带产品版本与证据快照。
        助手不可用时，本页产品知识内容保持完整可用。
      </p>
      <p v-else class="pc-gov-note">助手已启用。</p>
    </section>

    <section class="pc-gov-block">
      <h2 class="pc-gov-title">页面边界</h2>
      <ul class="pc-gov-boundary">
        <li v-for="statement in detail.fixedBoundaryStatements" :key="statement">{{ statement }}</li>
        <li>本页不构成对具体客户的推荐、适配结论或授信判断。</li>
      </ul>
    </section>
  </aside>
</template>

<style scoped>
.pc-gov {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pc-gov-block {
  padding: 12px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
}

.pc-gov-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 700;
  color: var(--gits-navy-800);
}

.pc-gov-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
}

.pc-gov-list > div {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  gap: 8px;
}

.pc-gov-list dt {
  font-size: 11px;
  color: var(--gits-muted);
}

.pc-gov-list dd {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--gits-text);
  word-break: break-word;
}

.pc-gov-list dd.is-missing {
  color: var(--color-warning, #7a4b00);
}

.pc-gov-pending {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.pc-gov-pending li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  font-size: 12px;
  color: var(--gits-muted);
}

.pc-gov-note {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--gits-muted);
}

.pc-gov-boundary {
  margin: 0;
  padding-left: 16px;
}

.pc-gov-boundary li {
  font-size: 12px;
  line-height: 1.6;
  color: var(--gits-muted);
}

/* ── C11 不可变版本语义（PC-i1 · W1-c）：相对来源 + 原文 ── */

.pc-gov-source {
  margin: 4px 0 4px;
  font-size: 11px;
  color: var(--gits-muted);
  word-break: break-all;
}

.pc-gov-content {
  margin: 0;
  font-family: inherit;
  font-size: 12px;
  line-height: 1.7;
  color: var(--gits-text);
  white-space: pre-wrap;
}
</style>
