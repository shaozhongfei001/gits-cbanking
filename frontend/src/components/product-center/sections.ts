/**
 * 八个固定章节定义（CTR-PKC-API-001 · PkcSectionKey）。
 *
 * 说明：章节「键与顺序」是受控契约（PI-FR-026 顺序不得个性化），
 * 因此以常量集中登记；章节内的**业务内容**一律来自产品中心合同数据，
 * 不得在本文件或组件中硬编码（需求 02 §八）。
 */
export const PRODUCT_SECTIONS = [
  { key: 'OVERVIEW', title: '60 秒读懂', anchor: 'pc-sec-overview' },
  { key: 'TERMS', title: '核心条款', anchor: 'pc-sec-terms' },
  { key: 'FIT', title: '适用边界', anchor: 'pc-sec-fit' },
  { key: 'PROCESS', title: '办理流程', anchor: 'pc-sec-process' },
  { key: 'MATERIALS', title: '申请材料', anchor: 'pc-sec-materials' },
  { key: 'PRICING', title: '价格与协议', anchor: 'pc-sec-pricing' },
  { key: 'COMPARE', title: '同类产品比较', anchor: 'pc-sec-compare' },
  { key: 'FAQ', title: '常见问题', anchor: 'pc-sec-faq' }
] as const

export type ProductSectionKey = (typeof PRODUCT_SECTIONS)[number]['key']

/** 各章节的内容契约对象名（用于未接入状态的具名提示，不用于渲染业务内容）。 */
export const SECTION_CONTRACT_OBJECTS: Record<ProductSectionKey, string> = {
  OVERVIEW: 'PkcProductSummary',
  TERMS: 'PkcTerm[]',
  FIT: 'PkcBoundary[] + PkcPrerequisite[]',
  PROCESS: 'PkcProcessStep[]',
  MATERIALS: 'PkcMaterialGroup[]',
  PRICING: 'PkcPricingItem[] + PkcAgreementClause[] + PkcSalesBoundary[]',
  COMPARE: 'PkcComparisonSet',
  FAQ: 'PkcFAQ[]'
}

/** 交付批次登记（用于「未接入」状态的具名说明，避免读者误判为缺陷或已实现）。 */
export const SECTION_PLANNED_LOOP: Record<ProductSectionKey, string> = {
  OVERVIEW: 'PC2',
  TERMS: 'PC2',
  FIT: 'PC2',
  PROCESS: 'PC2',
  MATERIALS: 'PC3',
  PRICING: 'PC3',
  COMPARE: 'PC4',
  FAQ: 'PC4'
}
