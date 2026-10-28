package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * 资产版本记录（CR-02 §4.1，AssetVersion.schema.json，additionalProperties=false）。
 *
 * <p>字段名/顺序/枚举严格对齐合同：lifecycle 固定
 * {@code CANDIDATE|IN_REVIEW|APPROVED|PUBLISHED|REVOKED}（历史实现中的 DRAFT 已删除）；
 * 顶层含合同信封字段 {@code contractVersion/simulationOnly}。</p>
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record AssetVersionRecord(
        String contractVersion,
        Boolean simulationOnly,
        String assetId,
        String version,
        String assetClass,
        String kind,
        String title,
        String ownerSystem,
        String ownerRole,
        String contentRef,
        String contentHash,
        String coreVersion,
        Scope scope,
        List<String> purposeFlags,
        String lifecycle,
        List<VersionRef> dependencyRefs) {

    public AssetVersionRecord {
        purposeFlags = purposeFlags == null ? List.of() : List.copyOf(purposeFlags);
        dependencyRefs = dependencyRefs == null ? List.of() : List.copyOf(dependencyRefs);
    }

    /** 仅 PUBLISHED 资产可进入发布快照与激活装配（CR-02 §4.1）。 */
    public boolean isPublished() {
        return "PUBLISHED".equals(lifecycle);
    }
}
