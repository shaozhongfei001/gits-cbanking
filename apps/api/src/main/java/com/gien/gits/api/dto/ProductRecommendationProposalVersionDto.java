package com.gien.gits.api.dto;

import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;

import java.time.Instant;

/**
 * 产品推荐方案版本响应（对齐 specs/openapi/product-recommendation.openapi.json
 * → {@code ProductRecommendationProposalVersion}；CTR-PR-API-001）。
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public record ProductRecommendationProposalVersionDto(
        String versionId,
        String runId,
        String resultRef,
        String evidenceBundleId,
        String contentHash,
        String supersededBy,
        Instant createdAt) {

    public static ProductRecommendationProposalVersionDto from(RecommendationProposalVersion version) {
        return new ProductRecommendationProposalVersionDto(
                version.versionId(), version.runId(), version.resultRef(),
                version.evidenceBundleId(), version.contentHash(),
                version.supersededBy(), version.createdAt());
    }
}
