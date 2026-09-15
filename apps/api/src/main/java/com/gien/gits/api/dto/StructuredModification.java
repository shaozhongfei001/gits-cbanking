package com.gien.gits.api.dto;

/**
 * 结构化修改项 DTO（HG-D01 / RecommendationHumanDecision.modifications）。
 *
 * <p>字段对齐 {@code specs/product-recommendation/recommendation-human-decision.schema.json}
 * （CTR-PR-DEC-001）的 {@code StructuredModification}：{@code kind} 必填，其余字段按
 * {@code kind} 可选。非法修改由 {@code ProductRecommendationHumanGateService} 显式校验并
 * 拒绝，不静默忽略。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 *
 * @param kind              修改类型（七值闭集枚举）
 * @param targetProductId   目标产品 ID（REMOVE_CANDIDATE / REORDER_CANDIDATE / MOVE_TO_REVIEW / ADD/REMOVE_SUPPORTING_PRODUCT）
 * @param targetPortfolioId 目标组合 ID（同上，二选一）
 * @param fromPosition      原位置（REORDER_CANDIDATE 必填）
 * @param toPosition        新位置（REORDER_CANDIDATE 必填）
 * @param value             值（CHANGE_NEXT_ACTION / ADD_CONFIRMED_FACT 必填）
 * @param note              修改说明（可选）
 */
public record StructuredModification(
        String kind,
        String targetProductId,
        String targetPortfolioId,
        Integer fromPosition,
        Integer toPosition,
        String value,
        String note) {
}
