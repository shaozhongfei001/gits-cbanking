package com.gien.gits.knowledge.gkke.map;

import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.MapEdge;
import com.gien.gits.knowledge.gkke.model.MapNode;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 任务知识地图结构校验（CR-02 §4.2，验收 T20）。
 *
 * <p>校验项：入口节点存在、边端点存在、relation 属合同枚举、<b>可执行依赖子图无环</b>。</p>
 *
 * <p><b>关键语义（Q1/T20）：</b>只有执行依赖关系（{@code dependsOn/requires/uses}，见
 * {@link MapRelation#isExecutableDependency()}）参与 DAG 环检测；{@code optional} 为可选
 * 增强不阻断执行，{@code covers}、{@code relatedTo} 是导航/语义边允许成环，三者均不参与
 * 执行环判定。历史实现对全部边建图，会把导航环误判为执行环，已修正。</p>
 */
public final class KnowledgeMapDagValidator {

    /** 校验整张地图；非法时抛 {@link MapValidationException}（携带稳定错误码）。 */
    public void validate(KnowledgeMapRecord map) {
        if (map == null) {
            throw MapValidationException.invalid("knowledge map must not be null");
        }
        Map<String, MapNode> nodes = indexNodes(map);
        validateEntries(map, nodes);
        validateEdges(map, nodes);
        validateExecutableSubgraphAcyclic(map);
    }

    /**
     * 从给定入口沿全部边（含导航边）提取可达节点 ID（BFS，保序去重）。
     * 用于 T20 入口可达子图裁剪；不可达分支不进入激活范围。
     */
    public List<String> reachableSubgraph(KnowledgeMapRecord map, List<String> entryNodeIds) {
        Map<String, List<String>> adjacency = adjacency(map, false);
        Set<String> visited = new LinkedHashSet<>(entryNodeIds);
        Deque<String> queue = new ArrayDeque<>(entryNodeIds);
        while (!queue.isEmpty()) {
            String current = queue.poll();
            for (String next : adjacency.getOrDefault(current, List.of())) {
                if (visited.add(next)) {
                    queue.add(next);
                }
            }
        }
        return List.copyOf(visited);
    }

    private Map<String, MapNode> indexNodes(KnowledgeMapRecord map) {
        Map<String, MapNode> nodes = new LinkedHashMap<>();
        for (MapNode node : safeList(map.nodes())) {
            if (nodes.putIfAbsent(node.nodeId(), node) != null) {
                throw MapValidationException.invalid(
                        "duplicate nodeId in map: " + node.nodeId() + ", mapId=" + map.mapId());
            }
        }
        return nodes;
    }

    private void validateEntries(KnowledgeMapRecord map, Map<String, MapNode> nodes) {
        if (map.entryNodes() == null || map.entryNodes().isEmpty()) {
            throw MapValidationException.invalid(
                    "map must declare at least one entry node: mapId=" + map.mapId());
        }
        for (String entryId : map.entryNodes()) {
            if (!nodes.containsKey(entryId)) {
                throw MapValidationException.invalid("entry node not found: nodeId=" + entryId);
            }
        }
    }

    private void validateEdges(KnowledgeMapRecord map, Map<String, MapNode> nodes) {
        for (MapEdge edge : safeList(map.edges())) {
            resolveRelation(edge);
            if (!nodes.containsKey(edge.from())) {
                throw MapValidationException.invalid(
                        "edge from-node not found: " + edge.edgeId() + " "
                                + edge.from() + "->" + edge.to());
            }
            if (!nodes.containsKey(edge.to())) {
                throw MapValidationException.invalid(
                        "edge to-node not found: " + edge.edgeId() + " "
                                + edge.from() + "->" + edge.to());
            }
        }
    }

    /**
     * 仅对执行依赖边（dependsOn/requires/uses）构建邻接表并做三色 DFS 环检测。
     * 导航边 covers/relatedTo 与 optional 被显式忽略，因此导航环不会被误判（Q1/T20）。
     */
    private void validateExecutableSubgraphAcyclic(KnowledgeMapRecord map) {
        Map<String, List<String>> adjacency = adjacency(map, true);
        Set<String> done = new LinkedHashSet<>();
        Set<String> onStack = new LinkedHashSet<>();
        for (String nodeId : adjacency.keySet()) {
            if (!done.contains(nodeId)) {
                dfs(nodeId, adjacency, done, onStack);
            }
        }
    }

    private void dfs(String nodeId, Map<String, List<String>> adjacency,
                     Set<String> done, Set<String> onStack) {
        onStack.add(nodeId);
        for (String next : adjacency.getOrDefault(nodeId, List.of())) {
            if (onStack.contains(next)) {
                throw MapValidationException.cycle(
                        "executable dependency cycle at edge: " + nodeId + "->" + next);
            }
            if (!done.contains(next)) {
                dfs(next, adjacency, done, onStack);
            }
        }
        onStack.remove(nodeId);
        done.add(nodeId);
    }

    /**
     * 构建邻接表。
     *
     * @param executableOnly true 只收执行依赖边（DAG 检测用）；false 收全部边（可达性用）
     */
    private Map<String, List<String>> adjacency(KnowledgeMapRecord map, boolean executableOnly) {
        Map<String, List<String>> adjacency = new LinkedHashMap<>();
        for (MapEdge edge : safeList(map.edges())) {
            MapRelation relation = resolveRelation(edge);
            if (!executableOnly || relation.isExecutableDependency()) {
                adjacency.computeIfAbsent(edge.from(), key -> new ArrayList<>()).add(edge.to());
            }
        }
        return adjacency;
    }

    private MapRelation resolveRelation(MapEdge edge) {
        try {
            return MapRelation.fromWire(edge.relation());
        } catch (IllegalArgumentException ex) {
            throw MapValidationException.invalid(
                    "edge relation not in contract enum: edgeId=" + edge.edgeId()
                            + ", relation=" + edge.relation());
        }
    }

    private <T> List<T> safeList(List<T> list) {
        return list == null ? List.of() : list;
    }
}
