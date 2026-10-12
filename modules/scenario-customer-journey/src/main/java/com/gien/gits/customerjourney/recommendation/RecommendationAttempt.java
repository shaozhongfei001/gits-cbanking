package com.gien.gits.customerjourney.recommendation;

import java.time.Instant;
import java.util.Objects;

/**
 * 产品推荐 attempt（RecommendationAttempt）—— 每次调用 KERT 的执行轨迹，不覆盖旧轨迹。
 *
 * <p>字段与契约 {@code CTR-PR-RUN-001} 的 {@code RecommendationAttempt} 及迁移
 * {@code product_recommendation_attempt} 表对齐。每次重试产生新 {@code attemptId}，
 * 但保留同一业务 {@code runId}。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public record RecommendationAttempt(
        String attemptId,
        String runId,
        String kertRequestId,
        Instant startedAt,
        Instant finishedAt,
        RecommendationAttemptStatus status,
        String errorCode,
        boolean retryable) {

    public RecommendationAttempt {
        Objects.requireNonNull(attemptId, "attemptId");
        Objects.requireNonNull(runId, "runId");
        Objects.requireNonNull(kertRequestId, "kertRequestId");
        Objects.requireNonNull(startedAt, "startedAt");
        Objects.requireNonNull(status, "status");
    }

    /** 新建 attempt 的便捷构造：{@code startedAt} = now、{@code finishedAt} = null。 */
    public RecommendationAttempt(
            String attemptId,
            String runId,
            String kertRequestId,
            RecommendationAttemptStatus status,
            String errorCode,
            boolean retryable) {
        this(attemptId, runId, kertRequestId, Instant.now(), null, status, errorCode, retryable);
    }
}
