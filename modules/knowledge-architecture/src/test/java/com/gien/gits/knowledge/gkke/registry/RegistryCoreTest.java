package com.gien.gits.knowledge.gkke.registry;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.ReleaseManifestRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G1 注册中心核心行为测试（CR-02 §4.1，验收 T05）。
 */
class RegistryCoreTest {

    private InMemoryAssetRegistry registry;

    @BeforeEach
    void setUp() {
        registry = new InMemoryAssetRegistry();
    }

    @Test
    @DisplayName("登记后可按 ID+版本精确解析，未登记返回空 Optional")
    void registerAndResolve() {
        registry.register(asset("KE-1", "1.0.0", "PUBLISHED"));

        Optional<AssetVersionRecord> resolved = registry.resolve("KE-1", "1.0.0");
        assertThat(resolved).isPresent();
        assertThat(resolved.get().contentHash()).isEqualTo("hash-1.0.0");
        assertThat(registry.resolve("KE-X", "1.0.0")).isEmpty();
    }

    @Test
    @DisplayName("同一 assetId+version 重复登记被拒绝，null 入参被拒绝")
    void rejectDuplicateAndNull() {
        registry.register(asset("KE-1", "1.0.0", "PUBLISHED"));

        assertThatThrownBy(() -> registry.register(asset("KE-1", "1.0.0", "PUBLISHED")))
                .isInstanceOf(DuplicateAssetVersionException.class)
                .hasMessageContaining("KE-1")
                .hasMessageContaining("1.0.0");
        assertThatThrownBy(() -> registry.register(null))
                .isInstanceOf(NullPointerException.class);
    }

    @Test
    @DisplayName("resolveLatest 按语义版本返回最高版本（1.10.0 > 1.2.0）")
    void resolveLatestBySemanticVersion() {
        registry.register(asset("KE-1", "1.0.0", "PUBLISHED"));
        registry.register(asset("KE-1", "1.10.0", "PUBLISHED"));
        registry.register(asset("KE-1", "1.2.0", "PUBLISHED"));

        assertThat(registry.resolveLatest("KE-1"))
                .isPresent()
                .get()
                .extracting(AssetVersionRecord::version)
                .isEqualTo("1.10.0");
        assertThat(registry.resolveLatest("KE-X")).isEmpty();
    }

    @Test
    @DisplayName("多维过滤：大类/类型/生命周期/所有系统/用途，无匹配返回空列表")
    void filterByDimensions() {
        registry.register(asset("KE-1", "1.0.0", "PUBLISHED", "FOUNDATIONAL_DATA",
                "PRODUCT_CARD", "KERT", List.of("INTERPRETATION", "RECOMMENDATION")));
        registry.register(asset("KE-2", "1.0.0", "PUBLISHED", "KNOWLEDGE_RULE",
                "POLICY", "KERT", List.of("INTERPRETATION")));
        registry.register(asset("KE-3", "0.9.0", "DRAFT", "PROCESS_TOOL",
                "SKILL", "GITS", List.of("RESEARCH")));

        assertThat(registry.findByAssetClass("KNOWLEDGE_RULE")).extracting(AssetVersionRecord::assetId)
                .containsExactly("KE-2");
        assertThat(registry.findByKind("PRODUCT_CARD")).extracting(AssetVersionRecord::assetId)
                .containsExactly("KE-1");
        assertThat(registry.findByLifecycle("DRAFT")).extracting(AssetVersionRecord::assetId)
                .containsExactly("KE-3");
        assertThat(registry.findByOwnerSystem("GITS")).extracting(AssetVersionRecord::assetId)
                .containsExactly("KE-3");
        assertThat(registry.findPublishedByPurpose("INTERPRETATION"))
                .extracting(AssetVersionRecord::assetId)
                .containsExactlyInAnyOrder("KE-1", "KE-2");
        assertThat(registry.findPublishedByPurpose("RESEARCH")).isEmpty();
        assertThat(registry.findByKind("UNKNOWN")).isEmpty();
    }

    @Test
    @DisplayName("发布快照：去重保序、时刻固化不可变、缺失/未发布资产失败")
    void releaseSnapshot() {
        registry.register(asset("KE-1", "1.0.0", "PUBLISHED"));
        registry.register(asset("KE-2", "1.0.0", "PUBLISHED"));
        ReleaseManifestRecord manifest = manifest(List.of(
                new VersionRef("KE-1", "1.0.0"),
                new VersionRef("KE-2", "1.0.0"),
                new VersionRef("KE-1", "1.0.0")));

        List<AssetVersionRecord> snapshot = registry.snapshotRelease(manifest);
        assertThat(snapshot)
                .extracting(asset -> asset.assetId() + ":" + asset.version())
                .containsExactly("KE-1:1.0.0", "KE-2:1.0.0");

        registry.register(asset("KE-1", "2.0.0", "PUBLISHED"));
        assertThat(snapshot).hasSize(2);
        assertThat(snapshot.get(0).version()).isEqualTo("1.0.0");
        assertThatThrownBy(() -> snapshot.add(asset("KE-9", "1.0.0", "PUBLISHED")))
                .isInstanceOf(UnsupportedOperationException.class);

        assertThatThrownBy(() -> registry.snapshotRelease(
                manifest(List.of(new VersionRef("KE-X", "1.0.0")))))
                .isInstanceOf(AssetNotFoundException.class);

        registry.register(asset("KE-3", "0.9.0", "DRAFT"));
        assertThatThrownBy(() -> registry.snapshotRelease(
                manifest(List.of(new VersionRef("KE-3", "0.9.0")))))
                .isInstanceOf(IllegalStateException.class);
    }

    private static AssetVersionRecord asset(String id, String version, String lifecycle) {
        return asset(id, version, lifecycle, "FOUNDATIONAL_DATA", "PRODUCT_CARD", "KERT",
                List.of("INTERPRETATION"));
    }

    private static AssetVersionRecord asset(String id, String version, String lifecycle,
                                            String assetClass, String kind, String ownerSystem,
                                            List<String> purposes) {
        return new AssetVersionRecord(id, version, assetClass, kind, "title-" + id, ownerSystem,
                "PRODUCT_OWNER", "s3://" + id, "hash-" + version, "core-1.0.0",
                new Scope("TENANT-1", List.of(), List.of(), "INTERPRETATION"),
                purposes, lifecycle, List.of());
    }

    private static ReleaseManifestRecord manifest(List<VersionRef> assetRefs) {
        return new ReleaseManifestRecord("REL-1", 1, List.of(), assetRefs,
                "RP-1", "2026-09-01T00:00:00Z", "PUBLISHED");
    }
}
