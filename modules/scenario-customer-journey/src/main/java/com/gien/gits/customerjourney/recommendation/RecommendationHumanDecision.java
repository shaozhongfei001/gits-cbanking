package com.gien.gits.customerjourney.recommendation;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * 人工决定记录对象（RecommendationHumanDecision）—— 结构化 HG-D01 决策。
 *
 * <p>字段与契约 {@code CTR-PR-DEC-001} / {@code recommendation-human-decision.schema.json}
 * 及迁移 {@code recommendation_human_decision} 表对齐。{@code decision} 指向明确的
 * {@code proposalVersionId}（INV-06）。并发校验（If-Match/ETag 的 {@code expectedVersion}）
 * 由应用服务在写入前校验，不落库。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public record RecommendationHumanDecision(
        String decisionId,
        String gateId,
        String runId,
        String proposalVersionId,
        RecommendationDecision decision,
        List<Map<String, Object>> modifications,
        String reason,
        String actorId,
        String actorRole,
        Instant decidedAt) {

    public RecommendationHumanDecision {
        Objects.requireNonNull(decisionId, "decisionId");
        Objects.requireNonNull(gateId, "gateId");
        Objects.requireNonNull(runId, "runId");
        Objects.requireNonNull(proposalVersionId, "proposalVersionId");
        Objects.requireNonNull(decision, "decision");
        Objects.requireNonNull(actorId, "actorId");
        Objects.requireNonNull(decidedAt, "decidedAt");
        modifications = copyMapList(modifications);
    }

    /** 新建决定的便捷构造：{@code decidedAt} = now。 */
    public RecommendationHumanDecision(
            String decisionId,
            String gateId,
            String runId,
            String proposalVersionId,
            RecommendationDecision decision,
            List<Map<String, Object>> modifications,
            String reason,
            String actorId,
            String actorRole) {
        this(decisionId, gateId, runId, proposalVersionId, decision, modifications,
                reason, actorId, actorRole, Instant.now());
    }

    private static List<Map<String, Object>> copyMapList(List<Map<String, Object>> input) {
        if (input == null) {
            return List.of();
        }
        List<Map<String, Object>> out = new ArrayList<>(input.size());
        for (Map<String, Object> m : input) {
            out.add(m == null ? Map.of() : Collections.unmodifiableMap(new LinkedHashMap<>(m)));
        }
        return Collections.unmodifiableList(out);
    }
}
