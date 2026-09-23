import type { ProductCardSection } from '../api/productKnowledge'

/**
 * P38 产品卡章节定位与**承接位置**登记（PC-i1「章级承接」共用）。
 *
 * 背景：`R2 03_十二章四维映射.csv` 用 **C1–C12** 编号描述 P38 产品解读的 12 个章节；
 * 产品卡原文（合同 `CTR-PK-INT-001`，`/api/v1/product-knowledge/cards/{id}`）的 `sections[].title`
 * 形如 `6. 前置、互斥、替代与配套产品`。
 *
 * ⚠ **实测缺陷与修正（2026-09-23，W1-d 期发现）**：节号在卡间**不一致** ——
 *   · `PROD-CM-003`（现金管理）：11 节，`11. 不可变版本语义`
 *   · `PROD-FIN-003`（贸易金融）：12 节，`11. EvidenceRef（源文件与条款定位）`、`12. 不可变版本语义`
 * 原实现「节号前缀优先」在 FIN 卡上会把 `C11 不可变版本语义` 错配到 §11（EvidenceRef）。
 * ⇒ 现改为 **标题关键字优先、节号前缀兜底**（标题比编号更稳），并仍**只做定位**、不生成/改写任何业务文本。
 */
export interface CardChapterSpec {
  /** R2 映射中的章号（C1–C12）。 */
  id: string
  /** 参考节号（**仅作兜底与展示**；匹配以标题为准）。 */
  no: number
  /** 该节标题（与产品卡原文一致的表述）。 */
  title: string
  /** 承接位置（**指名引用**：该章在页面的落点或本区独立区块）。 */
  landing: string
}

/**
 * 需在**新版页面明确落位**的章节（依 R2 映射）：
 * - `C6`/`C9`：R2 记为「**无任何对应区块**」⇒ 本区**独立可见区块**（不得被比较表/版本徽章替代）；
 * - `C2`/`C3`/`C10`：R2 记为「部分承接」⇒ 与承接位置**指名引用**并列呈现原文；
 * - `C8`：对应「价格与协议」章**尚未接入**（契约 `pricingItems` 为空）⇒ 原样呈现原文，如实标注；
 * - `C12`：`EvidenceRef`，仅 `PROD-FIN-*` 3 张卡含该节。
 */
export const CARD_CHAPTER_LANDINGS: readonly CardChapterSpec[] = [
  { id: 'C2', no: 2, title: '适用客户与适用场景', landing: '本页「适用边界」章 + P38 原文' },
  { id: 'C3', no: 3, title: '产品能力', landing: '首屏能力标签（指名引用）+ P38 原文' },
  { id: 'C6', no: 6, title: '前置、互斥、替代与配套产品', landing: '本区独立区块（R2：无对应区块）' },
  { id: 'C8', no: 8, title: '价格边界', landing: '本页「价格与协议」章（待接入 PC3）+ P38 原文' },
  { id: 'C9', no: 9, title: '风险提示与人工复核', landing: '本区独立区块（R2：无对应区块）' },
  { id: 'C10', no: 10, title: '销售边界', landing: '首屏固定边界 + 右栏页面边界 + 合同字段 salesBoundaries' },
  { id: 'C12', no: 12, title: 'EvidenceRef', landing: '证据位（仅 PROD-FIN-* 3 卡含该节）' }
] as const

/** 不可变版本语义（C11）：须由**版本区**承载该节语义，不得仅以版本徽章敷衍。 */
export const IMMUTABLE_VERSION_CHAPTER: CardChapterSpec = {
  id: 'C11',
  no: 11,
  title: '不可变版本语义',
  landing: '右栏「版本语义（不可变版本）」区块'
}

/**
 * 在产品卡章节中定位目标节：**标题关键字优先**，其次 `${no}.` 前缀（见文件头缺陷说明）。
 *
 * @returns 命中章节；`sections` 为空或两者皆未命中 ⇒ `null`（**不得**返回占位内容）
 */
export function findCardSection(
  sections: ProductCardSection[] | null | undefined,
  spec: CardChapterSpec
): ProductCardSection | null {
  const list = sections ?? []
  return (
    list.find((section) => section.title.includes(spec.title)) ??
    list.find((section) => section.title.trim().startsWith(`${spec.no}.`)) ??
    null
  )
}

/** 该节在**本卡**的实际节号（卡间编号不一致 ⇒ 展示实际值，缺失时回落到登记值）。 */
export function actualSectionNo(section: ProductCardSection | null, spec: CardChapterSpec): number {
  const matched = section?.title.match(/^(\d+)\./)
  return matched ? Number(matched[1]) : spec.no
}
