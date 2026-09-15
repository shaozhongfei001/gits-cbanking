package com.gien.gits.customerjourney.recommendation;

/**
 * 产品推荐“三段式决策”的阶段（GITS 主责业务阶段）。
 *
 * <p>状态块：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO（WP4-1）。</p>
 *
 * <p>权威依据：《GITS_KERT_产品推荐三段式决策》§4.1；
 * {@code ~/dev/Leibniz-KERT/docs/integration/DKWS_GITS_STATE_MAPPING_CANDIDATE.md} §1.2。</p>
 *
 * <p>阶段与 {@link ProductRecommendationRunStatus} 的对应（阶段是横切视角，非第二状态权威）：</p>
 * <ul>
 *   <li>{@link #HARD_FILTERING} → 运行状态 {@code HARD_FILTERING}（第一段硬过滤）</li>
 *   <li>{@link #MATCHING} → 运行状态 {@code MATCHING}（第二段需求-能力匹配）</li>
 *   <li>{@link #HUMAN_DECISION} → 运行状态 {@code AWAITING_HUMAN}（第三段客户经理人工决定）</li>
 * </ul>
 */
public enum RecommendationStage {
    /** 第一段：硬过滤（Eligibility 四态硬规则）。 */
    HARD_FILTERING,
    /** 第二段：需求-能力匹配（分维度匹配/排序）。 */
    MATCHING,
    /** 第三段：客户经理人工决定（HG-D01 / D01_PRODUCT_RECOMMEND）。 */
    HUMAN_DECISION
}
