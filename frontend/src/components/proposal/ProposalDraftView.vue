<script setup lang="ts">
/**
 * 非正式建议书草稿 · 卡片式展示（P24 新建向导 / P25 记录页共用）。
 *
 * 呈现原则：
 * - 每章一张卡片（仿「企业金融产品中心」章节卡片风格），章内按「节 → 小节」分层展示；
 * - 内容 **100% 取自 KERT 回包**（`content.proposalDraft` / `citations` / `unknowns` / `limitations`），
 *   本组件只做结构排版，不新增、不改写任何业务文字；
 * - 引用 / 待确认按 `chapterRef` / `relatedChapter`（CH01…CH08）归到对应章；
 *   无法归章的项目仍全量出现在折叠面板中，不静默丢弃；
 * - 原始 Markdown 收入「原始文本」折叠面板（默认收起），供复制与逐字核对。
 */
import { computed } from 'vue'
import { NCollapse, NCollapseItem, NTag } from 'naive-ui'
import type { Citation, ServiceProposal, Unknown } from '../../api/v14'
import { draftParagraphs, normalizeChapterCode, splitProposalDraft, type DraftBlock } from '../../composables/proposalDraft'
import { formatKertTimestamp } from '../../stores/proposalDraft'

const props = withDefaults(
  defineProps<{
    proposal: ServiceProposal
    /** 卡片区标题；默认「非正式建议书草稿」 */
    heading?: string
  }>(),
  { heading: '非正式建议书草稿' },
)

const draft = computed(() => props.proposal?.content?.proposalDraft?.trim() ?? '')
const citations = computed<Citation[]>(() => props.proposal?.citations ?? [])
const unknowns = computed<Unknown[]>(() => props.proposal?.unknowns ?? [])
const limitations = computed<string[]>(() => props.proposal?.limitations ?? [])
const ruleViolations = computed(() => props.proposal?.ruleViolations ?? [])
const gates = computed(() => props.proposal?.gateRecommendations ?? null)

const outline = computed(() => splitProposalDraft(draft.value))

/** 章代码 → 引用（按 CH01…CH08 归章；未归章的引用仍在折叠面板全量呈现） */
const citationsByChapter = computed(() => {
  const map = new Map<string, Citation[]>()
  for (const item of citations.value) {
    const code = normalizeChapterCode(item.chapterRef)
    if (!code) continue
    const list = map.get(code) ?? []
    list.push(item)
    map.set(code, list)
  }
  return map
})

const unknownsByChapter = computed(() => {
  const map = new Map<string, Unknown[]>()
  for (const item of unknowns.value) {
    const code = normalizeChapterCode(item.relatedChapter)
    if (!code) continue
    const list = map.get(code) ?? []
    list.push(item)
    map.set(code, list)
  }
  return map
})

/** 无法归章（chapterRef 缺失/非 CH 形态）的引用与待确认，需显式提示，不得静默丢弃 */
const unassignedCitations = computed(() =>
  citations.value.filter(item => normalizeChapterCode(item.chapterRef) === null),
)
const unassignedUnknowns = computed(() =>
  unknowns.value.filter(item => normalizeChapterCode(item.relatedChapter) === null),
)

function chapterCitations(code: string): Citation[] {
  return citationsByChapter.value.get(code) ?? []
}

function chapterUnknowns(code: string): Unknown[] {
  return unknownsByChapter.value.get(code) ?? []
}

function blockParagraphs(block: DraftBlock): string[] {
  return draftParagraphs(block.paragraphs)
}

function chapterParagraphs(chapter: { paragraphs: string[] }): string[] {
  return draftParagraphs(chapter.paragraphs)
}

/** 详情页内跳转：滚动到指定章卡片（标题区留出吸顶高度）。 */
function scrollToChapter(anchor: string) {
  if (typeof document === 'undefined') return
  const target = document.getElementById(anchor)
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

function chapterLabel(chapter: { marker: string; index: number; title: string }): string {
  return `${chapter.marker || String(chapter.index + 1).padStart(2, '0')} ${chapter.title}`
}
</script>

<template>
  <div class="draft-view" data-testid="proposal-draft-view">
    <p v-if="!draft" class="draft-empty" data-testid="proposal-draft-empty">KERT 未返回建议书草稿</p>

    <template v-else>
      <!-- 顶部信息条 -->
      <section class="draft-header">
        <div class="header-main">
          <h3 class="draft-title">{{ outline.docTitle || heading }}</h3>
          <div class="draft-meta">
            <NTag size="small" type="info" :bordered="true">{{ proposal.skillId || 'SP-20' }}</NTag>
            <NTag size="small" type="warning" :bordered="true">非正式草稿</NTag>
            <NTag size="small" :bordered="true">{{ proposal.status || '—' }}</NTag>
            <span v-if="proposal.runId" class="meta-item">runId {{ proposal.runId }}</span>
            <span v-if="proposal.timestamp" class="meta-item">{{ formatKertTimestamp(proposal.timestamp) }}</span>
          </div>
          <p v-if="outline.meta" class="draft-meta-line">{{ outline.meta }}</p>
        </div>
      </section>

      <!-- 统计摘要 -->
      <section class="draft-stats" data-testid="proposal-draft-stats">
        <div class="stat-item">
          <span class="stat-value">{{ outline.chapters.length }}</span>
          <span class="stat-label">章节</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ citations.length }}</span>
          <span class="stat-label">引用</span>
        </div>
        <div class="stat-item stat-warning">
          <span class="stat-value">{{ unknowns.length }}</span>
          <span class="stat-label">待确认</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ limitations.length }}</span>
          <span class="stat-label">边界</span>
        </div>
        <div class="stat-item" :class="{ 'stat-error': ruleViolations.length > 0 }">
          <span class="stat-value">{{ ruleViolations.length }}</span>
          <span class="stat-label">规则违规</span>
        </div>
      </section>

      <!-- 章节目录（长文详情内快速跳转） -->
      <nav v-if="outline.chapters.length > 1" class="draft-toc" data-testid="proposal-toc">
        <span class="toc-label">章节目录</span>
        <button
          v-for="chapter in outline.chapters"
          :key="`toc-${chapter.anchor}`"
          type="button"
          class="toc-item"
          data-testid="proposal-toc-item"
          @click="scrollToChapter(chapter.anchor)"
        >
          {{ chapterLabel(chapter) }}
        </button>
      </nav>

      <!-- 章节卡片 -->
      <section class="draft-chapters">
        <article
          v-for="chapter in outline.chapters"
          :id="chapter.anchor"
          :key="chapter.anchor"
          class="draft-chapter"
          data-testid="proposal-chapter"
          :data-chapter-code="chapter.code"
        >
          <header class="chapter-head">
            <span class="chapter-no">{{ chapter.marker || String(chapter.index + 1).padStart(2, '0') }}</span>
            <h4 class="chapter-title" data-testid="proposal-chapter-title">{{ chapter.title }}</h4>
            <NTag size="tiny" :bordered="true">{{ chapter.code }}</NTag>
            <NTag
              v-if="chapterCitations(chapter.code).length > 0"
              size="tiny"
              type="info"
              :bordered="true"
            >
              {{ chapterCitations(chapter.code).length }} 条引用
            </NTag>
            <NTag
              v-if="chapterUnknowns(chapter.code).length > 0"
              size="tiny"
              type="warning"
              :bordered="true"
            >
              {{ chapterUnknowns(chapter.code).length }} 项待确认
            </NTag>
          </header>

          <!-- 章引言 -->
          <div v-if="chapterParagraphs(chapter).length > 0" class="chapter-body">
            <p v-for="(para, i) in chapterParagraphs(chapter)" :key="`lead-${i}`" class="chapter-text">
              {{ para }}
            </p>
          </div>

          <!-- 节 + 小节 -->
          <div
            v-for="section in chapter.sections"
            :key="section.key"
            class="chapter-section"
            data-testid="proposal-section"
          >
            <h5 v-if="section.heading" class="section-title">{{ section.heading }}</h5>
            <div class="chapter-body">
              <p v-for="(para, i) in blockParagraphs(section)" :key="`sec-${i}`" class="chapter-text">
                {{ para }}
              </p>
            </div>
            <div
              v-for="child in section.children"
              :key="child.key"
              class="section-child"
              data-testid="proposal-subsection"
            >
              <h6 v-if="child.heading" class="subsection-title">{{ child.heading }}</h6>
              <div class="chapter-body">
                <p v-for="(para, i) in blockParagraphs(child)" :key="`sub-${i}`" class="chapter-text">
                  {{ para }}
                </p>
              </div>
            </div>
          </div>

          <!-- 本章待确认项 -->
          <div v-if="chapterUnknowns(chapter.code).length > 0" class="chapter-unknowns">
            <div v-for="item in chapterUnknowns(chapter.code)" :key="item.id" class="unknown-item">
              <NTag size="tiny" type="warning" :bordered="true">待确认</NTag>
              <span class="unknown-text">{{ item.description }}</span>
              <span v-if="item.suggestedAction" class="unknown-action">建议：{{ item.suggestedAction }}</span>
            </div>
          </div>
        </article>
      </section>

      <!-- 引用 / 待确认 / 边界 / 闸门 / 违规 / 原文 -->
      <section class="draft-panels">
        <NCollapse>
          <NCollapseItem name="citations">
            <template #header>引用来源</template>
            <template #header-extra>
              <NTag size="small" :bordered="true">{{ citations.length }} 条</NTag>
            </template>
            <div v-if="citations.length > 0" class="panel-list">
              <div v-for="item in citations" :key="item.id" class="citation-item">
                <span class="citation-ref">{{ item.chapterRef || '未标章' }}</span>
                <span class="citation-claim">{{ item.claim }}</span>
                <span class="citation-source">来源：{{ item.source }}（{{ item.date }}）</span>
                <span v-if="item.factLabel" class="citation-label">{{ item.factLabel }}</span>
              </div>
            </div>
            <p v-else class="panel-empty">无引用</p>
          </NCollapseItem>

          <NCollapseItem name="unknowns">
            <template #header>待确认项</template>
            <template #header-extra>
              <NTag size="small" type="warning" :bordered="true">{{ unknowns.length }} 项</NTag>
            </template>
            <div v-if="unknowns.length > 0" class="panel-list">
              <div v-for="item in unknowns" :key="item.id" class="unknown-panel-item">
                <span class="citation-ref">{{ item.relatedChapter || '未标章' }}</span>
                <span class="unknown-text">{{ item.description }}</span>
                <span v-if="item.suggestedAction" class="unknown-action">建议：{{ item.suggestedAction }}</span>
              </div>
            </div>
            <p v-else class="panel-empty">无待确认项</p>
            <p v-if="unassignedUnknowns.length > 0" class="panel-empty">
              其中 {{ unassignedUnknowns.length }} 项未标注所属章，仅在本面板列出。
            </p>
          </NCollapseItem>

          <NCollapseItem name="limitations">
            <template #header>边界限制</template>
            <template #header-extra>
              <NTag size="small" :bordered="true">{{ limitations.length }} 项</NTag>
            </template>
            <div v-if="limitations.length > 0" class="panel-list">
              <div v-for="(text, i) in limitations" :key="`lim-${i}`" class="limitation-item">{{ text }}</div>
            </div>
            <p v-else class="panel-empty">无边界限制</p>
          </NCollapseItem>

          <NCollapseItem v-if="gates" name="gates">
            <template #header>闸门推荐</template>
            <div class="panel-list">
              <p class="gate-line">当前闸门：{{ gates.currentGate }} · 就绪度：{{ gates.overallReadiness }}</p>
              <p class="gate-line">已通过：{{ gates.passedGates.join('、') || '无' }}</p>
              <p v-for="prereq in gates.nextGatePrerequisites" :key="prereq" class="gate-line">
                前置：{{ prereq }}
              </p>
            </div>
          </NCollapseItem>

          <NCollapseItem v-if="ruleViolations.length > 0" name="violations">
            <template #header>规则违规</template>
            <template #header-extra>
              <NTag size="small" type="error" :bordered="true">{{ ruleViolations.length }} 项</NTag>
            </template>
            <div class="panel-list">
              <div v-for="item in ruleViolations" :key="item.code" class="violation-item">
                <NTag size="tiny" :type="item.severity === 'ERROR' ? 'error' : 'warning'" :bordered="true">
                  {{ item.severity }}
                </NTag>
                <span>{{ item.message }}</span>
                <span v-if="item.ruleRef" class="citation-source">（{{ item.ruleRef }}）</span>
              </div>
            </div>
          </NCollapseItem>

        </NCollapse>

        <!-- 原始 Markdown：默认收起，内容常驻 DOM 以便逐字核对与复制 -->
        <details class="raw-panel" data-testid="proposal-draft-raw-panel">
          <summary class="raw-summary">原始 Markdown（逐字核对 / 复制用）</summary>
          <pre class="raw-draft" data-testid="proposal-draft-raw">{{ draft }}</pre>
        </details>
      </section>
    </template>
  </div>
</template>

<style scoped>
.draft-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.draft-empty {
  margin: 0;
  font-size: 13px;
  color: var(--v8-nav-text);
}

/* ── 顶部信息条 ── */
.draft-header {
  padding: 14px 18px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
}

.draft-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.draft-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-item {
  font-size: 12px;
  color: var(--v8-nav-text);
}

.draft-meta-line {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--v8-nav-text);
}

/* ── 统计摘要 ── */
.draft-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.stat-item {
  flex: 1 1 90px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 4px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 10px;
}

.stat-item.stat-warning {
  border-left: 3px solid #e8a838;
}

.stat-item.stat-error {
  border-left: 3px solid #d03050;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-warning .stat-value {
  color: #b45309;
}

.stat-error .stat-value {
  color: #b42318;
}

.stat-label {
  margin-top: 2px;
  font-size: 11px;
  color: var(--v8-nav-text);
}

/* ── 章节目录 ── */
.draft-toc {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 10px;
}

.toc-label {
  margin-right: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--v8-nav-text);
}

.toc-item {
  max-width: 260px;
  padding: 3px 10px;
  overflow: hidden;
  font-size: 12px;
  color: var(--brand-primary);
  text-overflow: ellipsis;
  white-space: nowrap;
  background: var(--brand-primary-lighter, #eaf4fe);
  border: 1px solid transparent;
  border-radius: 999px;
  cursor: pointer;
}

.toc-item:hover {
  border-color: var(--brand-primary);
}

/* ── 章节卡片 ── */
.draft-chapters {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.draft-chapter {
  padding: 14px 16px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
  scroll-margin-top: 108px;
}

.chapter-head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding-bottom: 8px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border-light, #d8e2ec);
}

.chapter-no {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 700;
  color: var(--brand-primary);
  background: var(--brand-primary-lighter, #eaf4fe);
  border-radius: 6px;
  white-space: nowrap;
}

.chapter-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.chapter-section {
  margin-top: 4px;
}

.section-title {
  margin: 12px 0 6px;
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-child {
  margin: 8px 0 8px 12px;
  padding-left: 10px;
  border-left: 2px solid var(--border-light, #d8e2ec);
}

.subsection-title {
  margin: 6px 0 4px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--v8-nav-text);
}

.chapter-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chapter-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.75;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.chapter-unknowns {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--border-light, #d8e2ec);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.unknown-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  line-height: 1.5;
}

.unknown-text {
  color: #92400e;
}

.unknown-action {
  color: var(--v8-nav-text);
  font-style: italic;
}

/* ── 折叠面板区 ── */
.draft-panels {
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
  padding: 4px 12px;
}

.panel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 420px;
  overflow: auto;
}

.citation-item,
.unknown-panel-item {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px;
  padding: 6px 0;
  font-size: 12px;
  border-bottom: 1px dashed var(--border-light, #d8e2ec);
}

.citation-item:last-child,
.unknown-panel-item:last-child {
  border-bottom: 0;
}

.citation-ref {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  color: var(--brand-primary);
}

.citation-claim {
  font-weight: 600;
  color: var(--text-primary);
}

.citation-source {
  color: var(--v8-nav-text);
}

.citation-label {
  color: var(--brand-primary);
}

.limitation-item {
  padding: 4px 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-primary);
  border-bottom: 1px dashed var(--border-light, #d8e2ec);
}

.limitation-item:last-child {
  border-bottom: 0;
}

.gate-line {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-primary);
}

.violation-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 0;
}

.panel-empty {
  margin: 0;
  font-size: 12px;
  color: var(--v8-nav-text);
}

.raw-panel {
  margin-top: 8px;
  padding: 8px 0;
  border-top: 1px solid var(--border-light, #d8e2ec);
}

.raw-summary {
  font-size: 12px;
  color: var(--v8-nav-text);
  cursor: pointer;
  user-select: none;
}

.raw-draft {
  max-height: 420px;
  margin: 8px 0 0;
  padding: 10px 12px;
  overflow: auto;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  background: rgba(15, 23, 42, 0.03);
  border-radius: 8px;
}
</style>
