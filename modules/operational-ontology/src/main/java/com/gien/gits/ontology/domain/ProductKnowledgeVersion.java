package com.gien.gits.ontology.domain;

import java.time.Instant;
import java.util.List;
import java.util.Objects;

/**
 * 产品知识版本 — 产品信息的版本化管理
 */
public record ProductKnowledgeVersion(
    String versionId,
    String productId,
    Integer versionNumber,
    String productName,
    String category,          // CREDIT, DEPOSIT, TRADE_FINANCE, INVESTMENT, INSURANCE
    String description,
    List<String> keyFeatures,
    List<String> targetIndustries,
    String riskLevel,         // LOW, MEDIUM, HIGH
    List<String> requiredMaterials,
    String pricingBasis,
    String previousVersionId,
    String changeSummary,
    String changedBy,
    Instant changedAt) {

    public ProductKnowledgeVersion {
        Objects.requireNonNull(versionId, "versionId");
        Objects.requireNonNull(productId, "productId");
        Objects.requireNonNull(productName, "productName");
        keyFeatures = List.copyOf(keyFeatures != null ? keyFeatures : List.of());
        targetIndustries = List.copyOf(targetIndustries != null ? targetIndustries : List.of());
        requiredMaterials = List.copyOf(requiredMaterials != null ? requiredMaterials : List.of());
    }

    public ProductKnowledgeVersion(String versionId, String productId, Integer versionNumber,
                                    String productName, String category, String description,
                                    List<String> keyFeatures, List<String> targetIndustries,
                                    String riskLevel, List<String> requiredMaterials,
                                    String pricingBasis, String previousVersionId,
                                    String changeSummary, String changedBy) {
        this(versionId, productId, versionNumber, productName, category, description,
             keyFeatures, targetIndustries, riskLevel, requiredMaterials, pricingBasis,
             previousVersionId, changeSummary, changedBy, Instant.now());
    }
}
