package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 发布清单（CTR-GKKE-004 / CR-02 §4.3）。
 *
 * @param releaseId       发布 ID
 * @param catalogRevision 目录版本号
 * @param mapRefs         地图引用
 * @param assetRefs       资产引用（发布快照，不可变）
 * @param routePolicyVersion 路由策略版本
 * @param createdAt       创建时间（ISO-8601）
 * @param status          发布状态（STAGED/PUBLISHED/REVOKED）
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record ReleaseManifestRecord(
        String releaseId,
        Integer catalogRevision,
        List<VersionRef> mapRefs,
        List<VersionRef> assetRefs,
        String routePolicyVersion,
        String createdAt,
        String status) {
}
