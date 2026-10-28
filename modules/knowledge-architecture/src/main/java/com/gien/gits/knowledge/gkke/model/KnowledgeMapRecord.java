package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * 知识地图不可变记录（严格对齐 {@code specs/gk-ke/v1/schemas/KnowledgeMap.schema.json}，
 * additionalProperties=false）。
 *
 * <p>字段名、顺序、必填性与冻结 schema 完全一致（12 字段），不发明合同外字段：
 * {@code contractVersion/simulationOnly/mapId/version/releaseId/taskTypes/entryNodes/
 * routePolicyRef/nodes/edges/purpose/scope}。历史实现中的 {@code name/status/entryNodeIds}
 * 已删除；{@code routePolicyRef} 为 {@code {id,version}} 对象，直接复用 {@link VersionRef}。
 *
 * @param entryNodes     入口节点 ID 列表（schema string[]）
 * @param routePolicyRef 路由策略引用（{@code {id,version}}，复用 {@link VersionRef}）
 * @param purpose        地图用途（RESEARCH/INTERPRETATION/RECOMMENDATION）
 * @param scope          地图授权范围
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record KnowledgeMapRecord(
        String contractVersion,
        Boolean simulationOnly,
        String mapId,
        String version,
        String releaseId,
        List<String> taskTypes,
        List<String> entryNodes,
        VersionRef routePolicyRef,
        List<MapNode> nodes,
        List<MapEdge> edges,
        String purpose,
        Scope scope) {

    public KnowledgeMapRecord {
        Objects.requireNonNull(mapId, "mapId must not be null");
        Objects.requireNonNull(version, "version must not be null");
        Objects.requireNonNull(releaseId, "releaseId must not be null");
        Objects.requireNonNull(routePolicyRef, "routePolicyRef must not be null");
        Objects.requireNonNull(purpose, "purpose must not be null");
        Objects.requireNonNull(scope, "scope must not be null");
        taskTypes = taskTypes == null ? List.of() : List.copyOf(taskTypes);
        entryNodes = entryNodes == null ? List.of() : List.copyOf(entryNodes);
        nodes = nodes == null ? List.of() : List.copyOf(nodes);
        edges = edges == null ? List.of() : List.copyOf(edges);
    }

    /** 路由策略版本（便捷访问）。 */
    public String routePolicyVersion() {
        return routePolicyRef.version();
    }

    /** 路由策略 ID（便捷访问）。 */
    public String routePolicyId() {
        return routePolicyRef.id();
    }

    /** 是否仅模拟（null 视为 false）。 */
    public boolean isSimulationOnly() {
        return Boolean.TRUE.equals(simulationOnly);
    }

    /** 按节点 ID 查找节点。 */
    public Optional<MapNode> nodeById(String nodeId) {
        return nodes.stream().filter(n -> n.nodeId().equals(nodeId)).findFirst();
    }

    /** 是否包含指定节点。 */
    public boolean hasNode(String nodeId) {
        return nodes.stream().anyMatch(n -> n.nodeId().equals(nodeId));
    }

    /** 所有节点 ID。 */
    public List<String> nodeIds() {
        return nodes.stream().map(MapNode::nodeId).toList();
    }
}
