import { describe, expect, it } from 'vitest'
import type { ProductCardSection } from '../../api/productKnowledge'
import {
  CARD_CHAPTER_LANDINGS,
  IMMUTABLE_VERSION_CHAPTER,
  actualSectionNo,
  findCardSection
} from '../cardChapter'

/**
 * PC-i1 · W1-d 期发现并修复的**真实缺陷**回归：
 * 产品卡的**节号在卡间不一致** —— 现金管理卡 11 节（§11=不可变版本语义）；
 * 贸易金融卡 12 节（§11=EvidenceRef、§12=不可变版本语义）。
 * 原实现「节号前缀优先」会把 C11 错配到 §11（EvidenceRef）⇒ 现改为**标题优先**。
 */
const CM_SECTIONS: ProductCardSection[] = [
  { title: '1. 产品概览与客户价值', content: 'c1' },
  { title: '6. 前置、互斥、替代与配套产品', content: 'c6' },
  { title: '11. 不可变版本语义', content: 'c11-cm' }
]

const FIN_SECTIONS: ProductCardSection[] = [
  { title: '1. 产品概览与客户价值', content: 'c1' },
  { title: '11. EvidenceRef（源文件与条款定位）', content: 'c12-fin' },
  { title: '12. 不可变版本语义', content: 'c11-fin' }
]

describe('cardChapter（章节定位与承接位置）', () => {
  it('C11 在两套编号下都能命中「不可变版本语义」（不得被 §11=EvidenceRef 抢走）', () => {
    const cm = findCardSection(CM_SECTIONS, IMMUTABLE_VERSION_CHAPTER)
    expect(cm?.content).toBe('c11-cm')
    expect(actualSectionNo(cm, IMMUTABLE_VERSION_CHAPTER)).toBe(11)

    const fin = findCardSection(FIN_SECTIONS, IMMUTABLE_VERSION_CHAPTER)
    expect(fin?.content).toBe('c11-fin')
    expect(actualSectionNo(fin, IMMUTABLE_VERSION_CHAPTER)).toBe(12)
  })

  it('C12（EvidenceRef）只在含该节的卡上命中，且展示**实际**节号', () => {
    const spec = CARD_CHAPTER_LANDINGS.find((item) => item.id === 'C12')
    expect(spec).toBeDefined()
    const fin = findCardSection(FIN_SECTIONS, spec!)
    expect(fin?.content).toBe('c12-fin')
    expect(actualSectionNo(fin, spec!)).toBe(11)

    const cm = findCardSection(CM_SECTIONS, spec!)
    expect(cm).toBeNull()
    expect(actualSectionNo(null, spec!)).toBe(12)
  })

  it('每个承接章节都登记了具名「承接位置」（指名引用，不留空）', () => {
    for (const spec of CARD_CHAPTER_LANDINGS) {
      expect(spec.landing.trim().length, `${spec.id} 必须有承接位置`).toBeGreaterThan(0)
    }
    expect(IMMUTABLE_VERSION_CHAPTER.landing).toContain('版本语义')
  })

  it('定位不到 ⇒ 返回 null（不得返回占位内容）', () => {
    expect(findCardSection([], IMMUTABLE_VERSION_CHAPTER)).toBeNull()
    expect(findCardSection(null, IMMUTABLE_VERSION_CHAPTER)).toBeNull()
  })
})
