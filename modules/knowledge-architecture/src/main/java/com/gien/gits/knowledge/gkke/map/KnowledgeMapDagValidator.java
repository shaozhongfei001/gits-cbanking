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
import java.util.Objects;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * GK-KE v1 知识地图 DAG 校验器（CR-02 §4.2，验收 T06）。
 *
 * <p>校验规则：
 * <ol>
 *   <li>至少一个入口节点，且每个入口节点必须存在；</li>
 *   <li>每条边的 from/to 端点必须存在；</li>
 *   <li>边方向 {@code from -> to} 构成有向无环图（DFS 三色检测）。</li>
 * </ol>
 * 另提供按入口节点提取可达子图（闭包）能力，供激活装配使用。
 */
public final class KnowledgeMapDagValidator {

    private static final Logger LOG = LoggerFactory.getLogger(KnowledgeMapDagValidator.class);

    /** 校验地图：入口、边端点、无环；失败抛出 {@link MapValidationException}。 */
    public void validate(KnowledgeMapRecord map) {
        Objects.requireNonNull(map, "map must not be null");
        Map<String, MapNode> nodes = indexNodes(map);
        validateEntries(map, nodes);
        validateEdges(map, nodes);
        validateAcyclic(map, nodes);
        LOG.info("Knowledge map DAG validated: mapId={}, version={}, nodes={}, edges={}",
                map.mapId(), map.version(), nodes.size(), map.edges().size());
    }

    /**
     * 从指定入口节点提取可达子图（BFS），返回节点 ID 有序集合（入口优先）。
     *
     * @param map       已校验地图
     * @param entryNodeIds 入口节点 ID
     * @return 可达节点 ID 不可变列表（BFS 顺序，去重）
     */
    public List<String> reachableSubgraph(KnowledgeMapRecord map, List<String> entryNodeIds) {
        Map<String, MapNode> nodes = indexNodes(map);
        Map<String, List<String>> adjacency = adjacency(map);
        Set<String> visited = new LinkedHashSet<>(entryNodeIds);
        Deque<String> queue = new ArrayDeque<>(entryNodeIds);
        while (!queue.isEmpty()) {
            String current = queue.poll();
            if (!nodes.containsKey(current)) {
                throw new MapValidationException("entry node not found: nodeId=" + current);
            }
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
        for (MapNode node : map.nodes()) {
            if (nodes.put(node.nodeId(), node) != null) {
                throw new MapValidationException("duplicate nodeId: " + node.nodeId());
            }
        }
        return nodes;
    }

    private void validateEntries(KnowledgeMapRecord map, Map<String, MapNode> nodes) {
        if (map.entryNodeIds() == null || map.entryNodeIds().isEmpty()) {
            throw new MapValidationException("map must declare at least one entry node: mapId=" + map.mapId());
        }
        for (String entryId : map.entryNodeIds()) {
            if (!nodes.containsKey(entryId)) {
                throw new MapValidationException("entry node not found: nodeId=" + entryId);
            }
        }
    }

    private void validateEdges(KnowledgeMapRecord map, Map<String, MapNode> nodes) {
        for (MapEdge edge : map.edges()) {
            if (!nodes.containsKey(edge.from())) {
                throw new MapValidationException("edge from-node not found: " + edge.from() + "->" + edge.to());
            }
            if (!nodes.containsKey(edge.to())) {
                throw new MapValidationException("edge to-node not found: " + edge.from() + "->" + edge.to());
            }
        }
    }

    private void validateAcyclic(KnowledgeMapRecord map, Map<String, MapNode> nodes) {
        Map<String, List<String>> adjacency = adjacency(map);
        Set<String> done = new LinkedHashSet<>();
        Set<String> onStack = new LinkedHashSet<>();
        for (String nodeId : nodes.keySet()) {
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
                throw new MapValidationException("cycle detected at edge: " + nodeId + "->" + next);
            }
            if (!done.contains(next)) {
                dfs(next, adjacency, done, onStack);
            }
        }
        onStack.remove(nodeId);
        done.add(nodeId);
    }

    private Map<String, List<String>> adjacency(KnowledgeMapRecord map) {
        Map<String, List<String>> adjacency = new LinkedHashMap<>();
        for (MapEdge edge : map.edges()) {
            adjacency.computeIfAbsent(edge.from(), key -> new ArrayList<>()).add(edge.to());
        }
        return adjacency;
    }
}
