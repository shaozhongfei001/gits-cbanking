package com.gien.gits.api.dto;

import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * 产品推荐运行响应（对齐 specs/openapi/product-recommendation.openapi.json
 * → {@code ProductRecommendationRun}；CTR-PR-API-001）。
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public record ProductRecommendationRunDto(
        String runId,
        String customerId,
        String journeyId,
        String operatingCaseId,
        List<String> needVersionIds,
        String recommendationObjective,
        List<String> requestedProductDomains,
        Instant asOf,
        String idempotencyKey,
        ProductRecommendationRunStatus status,
        String currentVersionId,
        String kertJobRef,
        Map<String, String> snapshotRefs,
        Instant createdAt,
        Instant updatedAt) {

    public static ProductRecommendationRunDto from(ProductRecommendationRun run) {
        return new ProductRecommendationRunDto(
                run.runId(), run.customerId(), run.journeyId(), run.operatingCaseId(),
                run.needVersionIds(), run.recommendationObjective(), run.requestedProductDomains(),
                run.asOf(), run.idempotencyKey(), run.status(), run.currentVersionId(),
                run.kertJobRef(), run.snapshotRefs(), run.createdAt(), run.updatedAt());
    }
}
