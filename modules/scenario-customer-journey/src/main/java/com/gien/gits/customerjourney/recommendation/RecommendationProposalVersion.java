package com.gien.gits.customerjourney.recommendation;

import java.time.Instant;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;

/**
 * 产品推荐方案版本（RecommendationProposalVersion）——不可变（immutable）的方案快照。
 *
 * <p>状态块：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO（WP4-1 权威 + FO-02 唯一归属合并）。</p>
 *
 * <p>权威依据：</p>
 * <ul>
 *   <li>{@code specs/openapi/product-recommendation.openapi.json} → {@code ProductRecommendationProposalVersion}</li>
 *   <li>{@code docs/adr/ADR-PR-IDEMPOTENCY_CANDIDATE.md} §2（ADR-PR-009 版本化）</li>
 *   <li>{@code adapters/persistence-relational/.../V020__product_recommendation.sql}（{@code payload} JSON 列）</li>
 * </ul>
 *
 * <p>不可变语义：record 全字段 final；被新版本取代时通过 {@link #withSupersededBy(String)} 返回新实例，
 * 不改写本实例（不漂移、不覆盖已审核版本）。旧版本“SUPERSEDED”以 {@code supersededBy} 指针表达，
 * 而非独立状态枚举。</p>
 *
 * <p>FO-02 唯一归属合并：本类是唯一权威定义。原
 * {@code modules/operational-ontology/.../domain/RecommendationProposalVersion.java}（WP4-2 重复定义）已删除，
 * 其 {@code payload}（KERT 结果载荷，落 V020 {@code payload} JSON 列）合并入本类；
 * {@code runId} 对齐 schema 与迁移为字符串（{@code CHAR(36)}）。</p>
 */
public record RecommendationProposalVersion(
        String versionId,
        String runId,
        String resultRef,
        String evidenceBundleId,
        String contentHash,
        Map<String, Object> payload,
        String supersededBy,
        Instant createdAt) {

    public RecommendationProposalVersion {
        versionId = requireText(versionId, "versionId");
        Objects.requireNonNull(runId, "runId");
        contentHash = requireText(contentHash, "contentHash");
        payload = payload == null
                ? Map.of()
                : Collections.unmodifiableMap(new LinkedHashMap<>(payload));
        Objects.requireNonNull(createdAt, "createdAt");
        // resultRef、evidenceBundleId、supersededBy 允许为空。
    }

    /**
     * 新建方案版本的便捷构造：{@code createdAt} = now。
     */
    public RecommendationProposalVersion(
            String versionId,
            String runId,
            String resultRef,
            String evidenceBundleId,
            String contentHash,
            Map<String, Object> payload,
            String supersededBy) {
        this(versionId, runId, resultRef, evidenceBundleId, contentHash, payload,
                supersededBy, Instant.now());
    }

    /**
     * 便捷工厂：创建一个尚未被取代、无 payload 的版本。
     */
    public static RecommendationProposalVersion create(String versionId, String runId, String resultRef,
                                                       String evidenceBundleId, String contentHash, Instant createdAt) {
        return new RecommendationProposalVersion(versionId, runId, resultRef, evidenceBundleId,
                contentHash, null, null, createdAt);
    }

    /**
     * 返回被 {@code newSupersededBy} 取代后的新实例（本实例保持不变）。
     *
     * @param newSupersededBy 取代本版本的新版本 ID；不得为空白，不得指向自身。
     */
    public RecommendationProposalVersion withSupersededBy(String newSupersededBy) {
        if (newSupersededBy != null && newSupersededBy.isBlank()) {
            throw new IllegalArgumentException("supersededBy must not be blank");
        }
        if (Objects.equals(this.versionId, newSupersededBy)) {
            throw new IllegalArgumentException("a proposal version cannot supersede itself: " + versionId);
        }
        return new RecommendationProposalVersion(versionId, runId, resultRef, evidenceBundleId,
                contentHash, payload, newSupersededBy, createdAt);
    }

    /**
     * 是否已被后续版本取代（supersededBy 非空）。
     */
    public boolean isSuperseded() {
        return supersededBy != null;
    }

    private static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " must not be blank");
        }
        return value;
    }
}
