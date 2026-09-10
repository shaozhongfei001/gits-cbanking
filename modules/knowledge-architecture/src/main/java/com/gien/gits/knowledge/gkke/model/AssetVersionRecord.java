package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 资产版本不可变记录（CTR-GKKE-001 / CR-02 §4.1）。
 *
 * <p>字段与 {@code specs/gk-ke/v1/schemas/AssetVersion.schema.json} 对齐，
 * 不发明合同未定义字段。
 *
 * @param assetId        资产 ID
 * @param version        语义版本
 * @param assetClass     资产大类（FOUNDATIONAL_DATA/KNOWLEDGE_RULE/PROCESS_TOOL/RUNTIME_FEEDBACK）
 * @param kind           资产类型（PRODUCT_CARD/POLICY/METRIC/SKILL 等）
 * @param title          标题
 * @param ownerSystem    所有系统（KERT/SEMANTIC_SERVICE/GITS/SIMULATION_PLATFORM）
 * @param ownerRole      所有角色
 * @param contentRef     内容引用
 * @param contentHash    内容 SHA-256
 * @param coreVersion    公共核心版本
 * @param scope          授权范围
 * @param purposeFlags   用途标记
 * @param lifecycle      生命周期（DRAFT/REVIEW/PUBLISHED/DEPRECATED）
 * @param dependencyRefs 依赖引用
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record AssetVersionRecord(
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
}
