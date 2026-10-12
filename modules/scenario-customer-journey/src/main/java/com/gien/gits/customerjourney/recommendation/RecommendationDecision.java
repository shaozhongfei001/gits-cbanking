package com.gien.gits.customerjourney.recommendation;

/**
 * 客户经理对产品推荐方案的人工决定值（RecommendationDecision）。
 *
 * <p>与契约 {@code CTR-PR-DEC-001} / {@code recommendation-human-decision.schema.json}
 * 的闭集枚举一致：{@code APPROVE / MODIFY / REJECT / HOLD}。</p>
 *
 * <p><b>注意</b>：本枚举不得与通用 {@code com.gien.gits.ontology.GateDecision}
 * 混用（后者含 {@code DECLINE}）；{@code REJECT} 与 {@code DECLINE} 语义待
 * HumanGate Contract Owner 裁决，本枚举不自行解释。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public enum RecommendationDecision {
    APPROVE,
    MODIFY,
    REJECT,
    HOLD
}
