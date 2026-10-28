package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.Objects;

/**
 * 知识地图节点（严格对齐 {@code specs/gk-ke/v1/schemas/KnowledgeMap.schema.json} 的 nodes[]，
 * additionalProperties=false）。
 *
 * <p>字段严格限定为合同四元组，不发明合同外字段：
 * <ul>
 *   <li>{@code nodeId}：地图内节点 ID；</li>
 *   <li>{@code nodeType}：{@code Task|KnowledgeDomain|Asset|Capability}；</li>
 *   <li>{@code label}：展示名；</li>
 *   <li>{@code ref}：受控对象引用（{@link VersionRef}，id+version）。</li>
 * </ul>
 *
 * <p>节点引用资产还是能力由 {@link #nodeType()} 判定（{@code Asset}/{@code Capability}），
 * 引用目标由 {@link #ref()} 给出；不使用自创的 assetId/capabilityId 等扁平字段。
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record MapNode(
        String nodeId,
        String nodeType,
        String label,
        VersionRef ref) {

    /** 合同 nodeType 枚举。 */
    public static final String TYPE_TASK = "Task";
    public static final String TYPE_KNOWLEDGE_DOMAIN = "KnowledgeDomain";
    public static final String TYPE_ASSET = "Asset";
    public static final String TYPE_CAPABILITY = "Capability";

    public MapNode {
        Objects.requireNonNull(nodeId, "nodeId must not be null");
        Objects.requireNonNull(nodeType, "nodeType must not be null");
        Objects.requireNonNull(label, "label must not be null");
    }

    /** 是否引用资产版本（nodeType=Asset 且 ref 非空）。 */
    public boolean referencesAsset() {
        return TYPE_ASSET.equals(nodeType) && ref != null;
    }

    /** 是否引用能力版本（nodeType=Capability 且 ref 非空）。 */
    public boolean referencesCapability() {
        return TYPE_CAPABILITY.equals(nodeType) && ref != null;
    }
}
