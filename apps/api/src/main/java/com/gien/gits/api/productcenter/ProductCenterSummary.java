package com.gien.gits.api.productcenter;

/**
 * 产品摘要（CTR-PKC-DOM-001 · PkcProductSummary）。
 *
 * <p>字段为 null 表示「待维护 / 待核验」，前端必须显示待核验状态，
 * <b>不得</b>用空白或推测文案冒充（PI-FR-038 / PI-BR-005）。</p>
 *
 * @param oneSentenceDefinition 一句话定义
 * @param boundaryStatement     审批与协议边界（不得放 tooltip，PI-FR-031）
 * @param productPurpose        产品目的
 * @param usageMode             使用方式
 * @param interestSummary       计息口径
 * @param eligibleEntitySummary 适用主体（须保留「符合准入与授信条件」语义，PI-FR-025）
 * @param solves                产品解决什么业务问题
 * @param isNot                 产品不是什么
 * @param nearestDifference     与相邻产品的客观差异（不含推荐结论）
 */
public record ProductCenterSummary(
        String oneSentenceDefinition,
        String boundaryStatement,
        String productPurpose,
        String usageMode,
        String interestSummary,
        String eligibleEntitySummary,
        String solves,
        String isNot,
        String nearestDifference) {
}
