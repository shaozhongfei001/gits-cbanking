<script setup lang="ts">
/**
 * 章级承接区：**八章契约未完整承接**的 P38 章节，按「原样呈现 + 指名引用」落位
 * （PC-i1 · W1-a/W1-b/W1-d/W1-e）。
 *
 * 为什么需要它（回源 `R2 03_十二章四维映射.csv`）：
 * - `C6`（前置、互斥、替代与配套产品）与 `C9`（风险提示与人工复核）在新版「**无任何对应区块**」
 *   ⇒ loop objective 明令两者「必须有**独立可见区块**，不得被比较表或版本徽章替代」；
 * - `C2`/`C3`/`C10` 为「**部分**承接」⇒ 须与承接位置**指名引用**并列；
 * - `C8` 对应章（价格与协议）**尚未接入**（契约 `pricingItems` 为空）⇒ 原样呈现原文并如实标注；
 * - `C12`（`EvidenceRef`）仅 `PROD-FIN-*` 3 张卡含该节。
 * 统一口径：**未实现/部分承接的章节必须原样呈现该章原文 + 相对来源标识 + 有效状态**，
 * 不得留空占位、不得以示意内容填充。
 *
 * 硬约束：
 * - 原文摘自既有合同 `CTR-PK-INT-001`（`/api/v1/product-knowledge/cards/{id}` 的 `sections`），
 *   本组件**只做定位与呈现**，不生成/不改写/不补全任何业务文本；
 * - 来源只呈现**相对路径**；定位不到该节 ⇒ 具名标注；
 * - `C10` 的**产品级**内容取合同字段 `salesBoundaries`（`PkcSalesBoundary`），为空时如实标注；
 * - 并列显示**有效状态**，不得暗示已生效/已审核。
 */
import { computed } from 'vue'
import { NTag } from 'naive-ui'
import type { PkcSalesBoundary } from '../../api/productCenter'
import type { ProductCardSection } from '../../api/productKnowledge'
import {
  CARD_CHAPTER_LANDINGS,
  actualSectionNo,
  findCardSection,
  type CardChapterSpec
} from '../../utils/cardChapter'

/** 产品卡数据可达性三态（PC-i1 · QA-B2）：**只有 ready 才可断言「该卡未包含该节」**。 */
type CardState = 'loading' | 'ready' | 'unavailable'

const props = withDefaults(
  defineProps<{
    sections: ProductCardSection[]
    sourceFile: string | null
    salesBoundaries?: PkcSalesBoundary[]
    versionStatus: string
    versionLabel: string
    effectiveFrom: string | null
    /** 产品卡可达性（默认 `ready`：既有夹具不传该 prop）。 */
    cardState?: CardState
  }>(),
  { cardState: 'ready' }
)

const contractBoundaries = computed(() => props.salesBoundaries ?? [])

const blocks = computed(() =>
  CARD_CHAPTER_LANDINGS.map((spec) => {
    const section = findCardSection(props.sections, spec)
    return {
      spec,
      section,
      key: spec.id.toLowerCase(),
      sectionNo: actualSectionNo(section, spec)
    }
  })
)

/**
 * meta 的「节号」表述（PC-i1 · QA-B1）：命中 ⇒ **实际节号**；未命中 ⇒ 明说**不可判/未含**，
 * **不得**回落 R2 登记章号冒充实际节号。
 */
function sectionNoLabel(section: ProductCardSection | null, spec: CardChapterSpec): string {
  const no = actualSectionNo(section, spec)
  if (no !== null) {
    return `第 ${no} 节`
  }
  if (props.cardState === 'unavailable') {
    return '来源不可得 · 节号不可判'
  }
  if (props.cardState === 'loading') {
    return '原文加载中 · 节号待判'
  }
  return `本卡未含该节 · R2 章号 ${spec.id}`
}

/**
 * 缺失文案（PC-i1 · QA-B1/B2）：**只有确实读到卡**时才可断言「未包含该节」；
 * 来源不可得 / 加载中 ⇒ 如实声明**无法判定**（不得对未验证事实作事实断言）。
 */
function absentText(spec: CardChapterSpec): string {
  if (props.cardState === 'unavailable') {
    return `产品卡来源不可得 ⇒ 无法判定该卡是否包含「${spec.title}」节（R2 章号 ${spec.id}）原文 —— 如实标注，不以示意内容填充。`
  }
  if (props.cardState === 'loading') {
    return `产品卡原文加载中 ⇒ 暂不判定该卡是否包含「${spec.title}」节（R2 章号 ${spec.id}）原文 —— 不以示意内容填充。`
  }
  return `该产品卡未包含「${spec.title}」节（R2 章号 ${spec.id}）原文 —— 如实标注，不以示意内容填充。`
}

/** 有效状态（事实字段拼接，不做判断性改写）。 */
const validityState = computed(
  () =>
    `${props.versionStatus}（${props.versionLabel}）｜生效日：${props.effectiveFrom || '未设定'}`
)
</script>

<template>
  <section class="pc-inherited" data-testid="pc-inherited-chapters">
    <header class="pc-inherited-head">
      <h2 class="pc-inherited-title">P38 章级承接（原样呈现 + 指名引用）</h2>
      <span class="pc-inherited-note">
        R2 映射中「无对应区块 / 仅部分承接 / 尚未接入」的章节；以下为该章**原文**，未受控、未经审核。
      </span>
    </header>

    <article
      v-for="block in blocks"
      :key="block.spec.id"
      class="pc-inherited-block"
      :data-testid="`pc-inherited-${block.key}`"
    >
      <!-- 标题：**章节标题**（R2 章号由右侧 tag 承载；命中时并列**卡内实际节号**）
           QA-B1：不得把 R2 登记章号写成「12.」当作节号 -->
      <header class="pc-inherited-block-head">
        <h3 class="pc-inherited-block-title">
          {{ block.spec.title }}
          <span v-if="block.sectionNo !== null" class="pc-inherited-block-no">
            （卡内第 {{ block.sectionNo }} 节）
          </span>
        </h3>
        <n-tag size="tiny" :bordered="true">{{ block.spec.id }}</n-tag>
        <n-tag v-if="block.section" size="tiny" :bordered="true">原文</n-tag>
      </header>

      <p class="pc-inherited-meta" :data-testid="`pc-inherited-${block.key}-meta`">
        承接位置：{{ block.spec.landing }}｜来源：{{ sourceFile || '来源标识不可得' }}
        （{{ sectionNoLabel(block.section, block.spec) }}）｜有效状态：{{ validityState }}
      </p>

      <pre
        v-if="block.section"
        class="pc-inherited-content"
        :data-testid="`pc-inherited-${block.key}-content`"
      >{{ block.section.content }}</pre>
      <p
        v-else
        class="pc-inherited-absent"
        :data-testid="`pc-inherited-${block.key}-absent`"
      >
        {{ absentText(block.spec) }}
      </p>

      <!-- C10：产品级销售边界取合同字段（不得只留通用声明） -->
      <div
        v-if="block.spec.id === 'C10' && contractBoundaries.length > 0"
        class="pc-inherited-contract"
        :data-testid="`pc-inherited-${block.key}-contract`"
      >
        <p class="pc-inherited-meta">
          产品级销售边界（合同字段 `salesBoundaries`，{{ contractBoundaries.length }} 条）：
        </p>
        <ul class="pc-inherited-list">
          <li
            v-for="boundary in contractBoundaries"
            :key="boundary.boundaryId"
            :data-testid="`pc-inherited-${block.key}-boundary`"
          >
            <n-tag size="tiny" :bordered="true">{{ boundary.boundaryKind }}</n-tag>
            <n-tag size="tiny" :bordered="true">{{ boundary.riskCategory }}</n-tag>
            <n-tag v-if="boundary.mandatoryDisplay" size="tiny" type="warning" :bordered="true">
              强制展示
            </n-tag>
            <span class="pc-inherited-text">{{ boundary.text }}</span>
          </li>
        </ul>
      </div>
      <p
        v-else-if="block.spec.id === 'C10'"
        class="pc-inherited-meta"
        :data-testid="`pc-inherited-${block.key}-contract-empty`"
      >
        合同字段 `salesBoundaries` 为空 ⇒ 产品级销售边界暂无受控内容（不以示意内容填充）。
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

/* 卡内实际节号（与 R2 章号区分；未命中不渲染）*/
.pc-inherited-block-no {
  font-size: 11px;
  font-weight: 400;
  color: var(--gits-muted);
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

.pc-inherited-contract {
  margin-top: 6px;
  padding: 8px 10px;
  background: var(--bg-subtle, #f7fafc);
  border-radius: 8px;
}

.pc-inherited-list {
  margin: 0;
  padding-left: 16px;
  font-size: 12px;
  line-height: 1.8;
  color: var(--gits-text);
}

.pc-inherited-text {
  margin-left: 6px;
}
</style>
