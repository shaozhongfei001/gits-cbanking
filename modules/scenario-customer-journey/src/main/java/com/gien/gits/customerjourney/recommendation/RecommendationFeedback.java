package com.gien.gits.customerjourney.recommendation;

import java.time.Instant;
import java.util.List;
import java.util.Objects;

/**
 * 产品推荐反馈（RecommendationFeedback）—— 供评测使用，不直接改正式规则。
 *
 * <p>字段与迁移 {@code recommendation_feedback} 表对齐。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public record RecommendationFeedback(
        String feedbackId,
        String runId,
        Boolean adopted,
        String rejectionReason,
        List<String> modifiedFields,
        String outcomeRef,
        Instant createdAt) {

    public RecommendationFeedback {
        Objects.requireNonNull(feedbackId, "feedbackId");
        Objects.requireNonNull(runId, "runId");
        modifiedFields = List.copyOf(modifiedFields != null ? modifiedFields : List.of());
        Objects.requireNonNull(createdAt, "createdAt");
    }

    /** 新建反馈的便捷构造：{@code createdAt} = now。 */
    public RecommendationFeedback(
            String feedbackId,
            String runId,
            Boolean adopted,
            String rejectionReason,
            List<String> modifiedFields,
            String outcomeRef) {
        this(feedbackId, runId, adopted, rejectionReason, modifiedFields, outcomeRef, Instant.now());
    }
}
