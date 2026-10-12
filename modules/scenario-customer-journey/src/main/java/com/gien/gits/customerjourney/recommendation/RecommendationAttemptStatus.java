package com.gien.gits.customerjourney.recommendation;

/**
 * 产品推荐 attempt 状态（RecommendationAttempt）。
 *
 * <p>与契约 {@code CTR-PR-RUN-001} 的 {@code RecommendationAttempt.status}
 * 闭集枚举一致：{@code SUBMITTED / RUNNING / SUCCEEDED / FAILED / TIMEOUT / CONTRACT_MISMATCH}。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public enum RecommendationAttemptStatus {
    SUBMITTED,
    RUNNING,
    SUCCEEDED,
    FAILED,
    TIMEOUT,
    CONTRACT_MISMATCH
}
