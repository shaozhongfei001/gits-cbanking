import type { ProductCardSection } from '../api/productKnowledge'

/**
 * P38 产品卡章节定位（PC-i1「章级承接」共用）。
 *
 * 背景：`R2 03_十二章四维映射.csv` 用 **C1–C12** 编号描述 P38 产品解读的 12 个章节；
 * 产品卡原文（合同 `CTR-PK-INT-001`，`/api/v1/product-knowledge/cards/{id}`）的 `sections[].title`
 * 形如 `6. 前置、互斥、替代与配套产品`。本工具按「节号前缀 → 标题关键字」两级匹配，
 * 供未在八章契约中承接的章节**原样呈现原文**时定位使用。
 *
 * 纪律：只做**定位**，不生成、不改写、不补全任何业务文本；匹配不到 ⇒ 返回 null（调用方如实标注"无此节"）。
 */
export interface CardChapterSpec {
  /** R2 映射中的章号（C1–C12）。 */
  id: string
  /** 产品卡原文中的节号（1–12）。 */
  no: number
  /** 该节标题（与产品卡原文一致的表述）。 */
  title: string
}

/** 需在**新版页面独立可见**承接的章节（R2 映射：C6/C9 记「无任何对应区块」）。 */
export const INHERITED_CARD_CHAPTERS: readonly CardChapterSpec[] = [
  { id: 'C6', no: 6, title: '前置、互斥、替代与配套产品' },
  { id: 'C9', no: 9, title: '风险提示与人工复核' }
] as const

/** 不可变版本语义（C11）：须由**版本区**承载该节语义，不得仅以版本徽章敷衍。 */
export const IMMUTABLE_VERSION_CHAPTER: CardChapterSpec = {
  id: 'C11',
  no: 11,
  title: '不可变版本语义'
}

/**
 * 在产品卡章节中定位目标节：先按 `${no}.` 前缀，再退回标题关键字包含。
 *
 * @returns 命中章节；`sections` 为空或两者皆未命中 ⇒ `null`（**不得**返回占位内容）
 */
export function findCardSection(
  sections: ProductCardSection[] | null | undefined,
  spec: CardChapterSpec
): ProductCardSection | null {
  const list = sections ?? []
  return (
    list.find((section) => section.title.trim().startsWith(`${spec.no}.`)) ??
    list.find((section) => section.title.includes(spec.title)) ??
    null
  )
}
