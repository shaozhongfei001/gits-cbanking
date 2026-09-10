package com.gien.gits.knowledge.gkke.registry;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.ReleaseManifestRecord;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * GK-KE v1 内存知识资产注册中心（CR-02 §4.1，验收 T05）。
 *
 * <p>只追加、不可变：{@code assetId + version} 唯一；查询返回的 record 不可变，
 * 集合返回不可变副本。发布快照在解析时刻固化，不随后续登记变化。
 */
public final class InMemoryAssetRegistry implements AssetRegistryPort {

    private static final Logger LOG = LoggerFactory.getLogger(InMemoryAssetRegistry.class);
    private static final String LIFECYCLE_PUBLISHED = "PUBLISHED";

    private final Map<String, Map<String, AssetVersionRecord>> assets = new LinkedHashMap<>();

    @Override
    public void register(AssetVersionRecord asset) {
        Objects.requireNonNull(asset, "asset must not be null");
        Map<String, AssetVersionRecord> versions =
                assets.computeIfAbsent(asset.assetId(), key -> new LinkedHashMap<>());
        if (versions.containsKey(asset.version())) {
            throw new DuplicateAssetVersionException(asset.assetId(), asset.version());
        }
        versions.put(asset.version(), asset);
        LOG.info("Asset registered: assetId={}, version={}, lifecycle={}",
                asset.assetId(), asset.version(), asset.lifecycle());
    }

    @Override
    public Optional<AssetVersionRecord> resolve(String assetId, String version) {
        return Optional.ofNullable(assets.getOrDefault(assetId, Map.of()).get(version));
    }

    @Override
    public Optional<AssetVersionRecord> resolveLatest(String assetId) {
        return assets.getOrDefault(assetId, Map.of()).values().stream()
                .max(Comparator.comparing(AssetVersionRecord::version, SemanticVersion.COMPARATOR));
    }

    @Override
    public List<AssetVersionRecord> findByAssetClass(String assetClass) {
        return filter(asset -> Objects.equals(asset.assetClass(), assetClass));
    }

    @Override
    public List<AssetVersionRecord> findByKind(String kind) {
        return filter(asset -> Objects.equals(asset.kind(), kind));
    }

    @Override
    public List<AssetVersionRecord> findByLifecycle(String lifecycle) {
        return filter(asset -> Objects.equals(asset.lifecycle(), lifecycle));
    }

    @Override
    public List<AssetVersionRecord> findByOwnerSystem(String ownerSystem) {
        return filter(asset -> Objects.equals(asset.ownerSystem(), ownerSystem));
    }

    @Override
    public List<AssetVersionRecord> findPublishedByPurpose(String purpose) {
        return filter(asset -> LIFECYCLE_PUBLISHED.equals(asset.lifecycle())
                && asset.purposeFlags() != null && asset.purposeFlags().contains(purpose));
    }

    @Override
    public List<AssetVersionRecord> snapshotRelease(ReleaseManifestRecord manifest) {
        Objects.requireNonNull(manifest, "manifest must not be null");
        Map<String, AssetVersionRecord> snapshot = new LinkedHashMap<>();
        for (VersionRef ref : manifest.assetRefs()) {
            AssetVersionRecord asset = resolve(ref.id(), ref.version())
                    .orElseThrow(() -> new AssetNotFoundException(ref.id(), ref.version()));
            requirePublished(asset);
            snapshot.putIfAbsent(asset.assetId() + ":" + asset.version(), asset);
        }
        LOG.info("Release snapshot resolved: releaseId={}, assets={}",
                manifest.releaseId(), snapshot.size());
        return List.copyOf(snapshot.values());
    }

    @Override
    public List<AssetVersionRecord> dependencyClosure(String assetId, String version) {
        AssetVersionRecord root = resolve(assetId, version)
                .orElseThrow(() -> new AssetNotFoundException(assetId, version));
        LinkedHashSet<AssetVersionRecord> closure = new LinkedHashSet<>();
        Set<String> visiting = new LinkedHashSet<>();
        collectDependencies(root, visiting, closure);
        closure.add(root);
        LOG.info("Dependency closure computed: root={}:{}, size={}",
                assetId, version, closure.size());
        return List.copyOf(closure);
    }

    private void collectDependencies(AssetVersionRecord asset, Set<String> visiting,
                                     LinkedHashSet<AssetVersionRecord> closure) {
        String key = asset.assetId() + ":" + asset.version();
        if (visiting.contains(key)) {
            throw new DependencyCycleException(asset.assetId(), asset.version());
        }
        if (closure.contains(asset)) {
            return;
        }
        visiting.add(key);
        for (VersionRef ref : asset.dependencyRefs()) {
            AssetVersionRecord dependency = resolve(ref.id(), ref.version())
                    .orElseThrow(() -> new AssetNotFoundException(ref.id(), ref.version()));
            collectDependencies(dependency, visiting, closure);
        }
        visiting.remove(key);
        closure.add(asset);
    }

    private List<AssetVersionRecord> filter(Predicate<AssetVersionRecord> predicate) {
        return assets.values().stream()
                .flatMap(versions -> versions.values().stream())
                .filter(predicate)
                .collect(Collectors.toUnmodifiableList());
    }

    private static void requirePublished(AssetVersionRecord asset) {
        if (!LIFECYCLE_PUBLISHED.equals(asset.lifecycle())) {
            throw new AssetNotAvailableException(asset.assetId(), asset.version());
        }
    }

    /** 当前登记的资产版本总数（加载器日志用）。 */
    int size() {
        return assets.values().stream().mapToInt(Map::size).sum();
    }
}
