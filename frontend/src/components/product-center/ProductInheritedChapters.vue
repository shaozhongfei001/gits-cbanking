<script setup lang="ts">
/**
 * 章级承接区：**未在八章契约中承接**的 P38 章节，按「原样呈现」落位（PC-i1 · W1-a/W1-b）。
 *
 * 为什么需要它（回源）：`R2 03_十二章四维映射.csv` 记 `C6`（前置、互斥、替代与配套产品）与
 * `C9`（风险提示与人工复核）在新版**「无任何对应区块」**；而 loop objective 明令
 * 「未实现章节必须原样呈现该章原文 + 相对来源标识 + 有效状态，**不得留空占位**、不得以示意内容填充」，
 * 且 `C6`/`C9`「必须有独立可见区块，不得被比较表或版本徽章替代」。
 *
 * 硬约束：
 * - 原文摘自既有合同 `CTR-PK-INT-001`（`/api/v1/product-knowledge/cards/{id}` 的 `sections`），
 *   本组件**只做定位与呈现**，**不生成/不改写/不补全**任何业务文本；
 * - 来源只呈现**相对路径**（不拼接、不暴露本机绝对路径）；
 * - 必须并列显示**有效状态**，不得暗示该内容已生效/已审核；
 * - 定位不到该节 ⇒ 具名「未包含第 N 节」，**不得**以空白或示意内容填充。
 */
import { computed } from 'vue'
import { NTag } from 'naive-ui'
import type { ProductCardSection } from '../../api/productKnowledge'
import { INHERITED_CARD_CHAPTERS, findCardSection } from '../../utils/cardChapter'

const props = defineProps<{
  sections: ProductCardSection[]
  sourceFile: string | null
  versionStatus: string
  versionLabel: string
  effectiveFrom: string | null
}>()

const blocks = computed(() =>
  INHERITED_CARD_CHAPTERS.map((spec) => ({ spec, section: findCardSection(props.sections, spec) }))
)

/** 有效状态（事实字段拼接，不做判断性改写）。 */
const validityState = computed(
  () =>
    `${props.versionStatus}（${props.versionLabel}）｜生效日：${props.effectiveFrom || '未设定'}`
)
</script>

<template>
  <section class="pc-inherited" data-testid="pc-inherited-chapters">
    <header class="pc-inherited-head">
      <h2 class="pc-inherited-title">P38 章级承接（原样呈现）</h2>
      <span class="pc-inherited-note">
        R2 映射中记为「无对应区块」的章节；以下为该章**原文**，未受控、未经审核。
      </span>
    </header>

    <article
      v-for="block in blocks"
      :key="block.spec.id"
      class="pc-inherited-block"
      :data-testid="`pc-inherited-${block.spec.id.toLowerCase()}`"
    >
      <header class="pc-inherited-block-head">
        <h3 class="pc-inherited-block-title">
          {{ block.spec.no }}. {{ block.spec.title }}
        </h3>
        <n-tag size="tiny" :bordered="true">原文</n-tag>
      </header>

      <p class="pc-inherited-meta" :data-testid="`pc-inherited-${block.spec.id.toLowerCase()}-meta`">
        来源：{{ sourceFile || '来源标识不可得' }}（第 {{ block.spec.no }} 节）｜
        有效状态：{{ validityState }}
      </p>

      <pre
        v-if="block.section"
        class="pc-inherited-content"
        :data-testid="`pc-inherited-${block.spec.id.toLowerCase()}-content`"
      >{{ block.section.content }}</pre>
      <p
        v-else
        class="pc-inherited-absent"
        :data-testid="`pc-inherited-${block.spec.id.toLowerCase()}-absent`"
      >
        该产品卡未包含第 {{ block.spec.no }} 节（{{ block.spec.title }}）原文 —— 如实标注，不以示意内容填充。
      </p>
    </article>
  </section>
</template>

<style scoped>
.pc-inherited {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  background: var(--bg-surface, #fff);
  border: 1px solid var(--border-light, #d8e2ec);
  border-radius: 13px;
}

.pc-inherited-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
}

.pc-inherited-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--gits-navy-800);
}

.pc-inherited-note {
  font-size: 11px;
  color: var(--gits-muted);
}

.pc-inherited-block {
  padding: 10px 0;
  border-top: 1px dashed var(--border-light, #d8e2ec);
}

.pc-inherited-block:first-of-type {
  border-top: 0;
}

.pc-inherited-block-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.pc-inherited-block-title {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: var(--gits-navy-800);
}

.pc-inherited-meta {
  margin: 0 0 6px;
  font-size: 11px;
  line-height: 1.6;
  color: var(--gits-muted);
  word-break: break-all;
}

.pc-inherited-content {
  margin: 0;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.7;
  color: var(--gits-text);
  white-space: pre-wrap;
}

.pc-inherited-absent {
  margin: 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--color-warning, #7a4b00);
}
</style>
