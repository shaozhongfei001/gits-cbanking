package com.gien.gits.knowledge.gkke.permission;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.MapEdge;
import com.gien.gits.knowledge.gkke.model.MapNode;
import com.gien.gits.knowledge.gkke.registry.AssetRegistryPort;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * 权限感知目录（CR-02 §4.1/§5/§7，验收 T07）。
 *
 * <p>在注册中心之上叠加运行时权限过滤，对四类目录出口统一收口，确保无权主体对秘密资产
 * <b>零泄漏</b>——既不泄漏资产存在性，也不泄漏标题、关系或计数：
 * <ol>
 *   <li>{@link #discover}：目录列表（资产 ID/版本/标题等安全投影）；</li>
 *   <li>{@link #summaries}：标题摘要（节点 nodeId→label）；</li>
 *   <li>{@link #neighbors}：关系邻居（相邻且可见的节点 ID）；</li>
 *   <li>{@link #countVisibleNodes}：节点计数（仅可见节点）。</li>
 * </ol>
 *
 * <p>可见资产集合按 {@link PermissionContext#cacheKey()} 五要素缓存；不同租户/主体范围/
 * 目的/发布快照/目录修订得到不同缓存槽，从结构上杜绝串缓存。默认拒绝：任何未显式放行的
 * 资产一律不可见。
 */
public final class PermissionAwareCatalog {

    private final AssetRegistryPort registry;
    private final RegistryPermissionFilter filter;
    private final Map<String, Set<String>> visibleAssetCache = new ConcurrentHashMap<>();

    public PermissionAwareCatalog(AssetRegistryPort registry, RegistryPermissionFilter filter) {
        this.registry = Objects.requireNonNull(registry, "registry must not be null");
        this.filter = Objects.requireNonNull(filter, "filter must not be null");
    }

    /** 出口 1：目录列表——仅返回可见资产的安全投影（秘密资产不出现，不泄漏存在性）。 */
    public List<AssetView> discover(PermissionContext ctx) {
        Objects.requireNonNull(ctx, "ctx must not be null");
        Set<String> visible = visibleAssetIds(ctx);
        return registry.findAll().stream()
                .filter(a -> visible.contains(a.assetId()))
                .map(this::project)
                .toList();
    }

    /** 出口 2：标题摘要——仅返回可见节点的 nodeId→label（秘密节点标题不泄漏）。 */
    public Map<String, String> summaries(KnowledgeMapRecord map, PermissionContext ctx) {
        Objects.requireNonNull(map, "map must not be null");
        Objects.requireNonNull(ctx, "ctx must not be null");
        Set<String> visibleNodes = visibleNodeIds(map, visibleAssetIds(ctx));
        Map<String, String> out = new LinkedHashMap<>();
        for (MapNode node : map.nodes()) {
            if (visibleNodes.contains(node.nodeId())) {
                out.put(node.nodeId(), node.label());
            }
        }
        return out;
    }

    /** 出口 3：关系邻居——仅返回与给定节点相邻且自身可见的节点 ID（秘密邻居不泄漏）。 */
    public List<String> neighbors(KnowledgeMapRecord map, String nodeId, PermissionContext ctx) {
        Objects.requireNonNull(map, "map must not be null");
        Objects.requireNonNull(nodeId, "nodeId must not be null");
        Objects.requireNonNull(ctx, "ctx must not be null");
        Set<String> visibleNodes = visibleNodeIds(map, visibleAssetIds(ctx));
        if (!visibleNodes.contains(nodeId)) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        for (MapEdge edge : map.edges()) {
            collectNeighborIfVisible(edge, nodeId, visibleNodes, out);
        }
        return List.copyOf(out);
    }

    /** 出口 4：节点计数——只统计可见节点（秘密节点不计入，不泄漏数量）。 */
    public int countVisibleNodes(KnowledgeMapRecord map, PermissionContext ctx) {
        Objects.requireNonNull(map, "map must not be null");
        Objects.requireNonNull(ctx, "ctx must not be null");
        return visibleNodeIds(map, visibleAssetIds(ctx)).size();
    }

    /** 仅供测试：清空可见资产缓存。 */
    void clearCacheForTest() {
        visibleAssetCache.clear();
    }

    private void collectNeighborIfVisible(MapEdge edge, String self, Set<String> visibleNodes,
                                          List<String> out) {
        String other = null;
        if (edge.from().equals(self)) {
            other = edge.to();
        } else if (edge.to().equals(self)) {
            other = edge.from();
        }
        if (other != null && visibleNodes.contains(other) && !out.contains(other)) {
            out.add(other);
        }
    }

    /**
     * 地图内可见节点 ID：不引用受控版本的节点（Task/KnowledgeDomain）恒可见；
     * 引用资产/能力版本的节点仅当其引用资产通过权限决议时可见。
     */
    private Set<String> visibleNodeIds(KnowledgeMapRecord map, Set<String> visibleAssetIds) {
        return map.nodes().stream()
                .filter(n -> !referencesVersion(n) || visibleAssetIds.contains(n.ref().id()))
                .map(MapNode::nodeId)
                .collect(Collectors.toUnmodifiableSet());
    }

    private static boolean referencesVersion(MapNode node) {
        return node.ref() != null
                && (node.referencesAsset() || node.referencesCapability());
    }

    private Set<String> visibleAssetIds(PermissionContext ctx) {
        return visibleAssetCache.computeIfAbsent(ctx.cacheKey(), key ->
                registry.findAll().stream()
                        .filter(a -> filter.decide(a, ctx).allowed())
                        .map(AssetVersionRecord::assetId)
                        .collect(Collectors.toUnmodifiableSet()));
    }

    private AssetView project(AssetVersionRecord asset) {
        return new AssetView(asset.assetId(), asset.version(), asset.assetClass(), asset.kind(),
                asset.title(), asset.lifecycle(), asset.purposeFlags(), asset.coreVersion());
    }
}
