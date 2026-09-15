package com.gien.gits.api.dto;

import java.time.Instant;
import java.util.List;

/**
 * 创建产品推荐运行请求（对齐 specs/openapi/product-recommendation.openapi.json
 * → {@code ProductRecommendationCreateRequest}；CTR-PR-API-001）。
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public record ProductRecommendationCreateRequest(
        String customerId,
        String journeyId,
        String operatingCaseId,
        List<String> needVersionIds,
        String recommendationObjective,
        List<String> requestedProductDomains,
        Instant asOf,
        String customerFactSnapshotId,
        String productKnowledgeSnapshotRef,
        String ruleBundleRef,
        String permissionDecisionId,
        String activationContract) {
}
