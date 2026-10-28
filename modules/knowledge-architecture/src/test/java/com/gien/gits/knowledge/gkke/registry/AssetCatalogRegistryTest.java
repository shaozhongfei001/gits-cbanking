package com.gien.gits.knowledge.gkke.registry;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.ReleaseManifestRecord;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G1 资产目录装载测试（CR-02 §4.1/§4.3，验收 T05）。
 */
class AssetCatalogRegistryTest {

    private final ObjectMapper objectMapper =
            new ObjectMapper().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    @Test
    @DisplayName("从目录装载全部 AssetVersion JSON，字段完整映射")
    void loadsAssetDirectory() throws IOException, URISyntaxException {
        InMemoryAssetRegistry registry =
                new InMemoryAssetRegistryLoader(objectMapper).loadDirectory(resource("gk-ke-registry/assets"));

        assertThat(registry.resolve("KE-PROD-001", "1.0.0")).isPresent();
        assertThat(registry.resolve("KE-PROD-001", "1.1.0")).isPresent();
        assertThat(registry.resolve("KE-RUL-001", "1.0.0")).isPresent();
        assertThat(registry.resolve("KE-SKILL-001", "0.9.0")).isPresent();
        assertThat(registry.resolveLatest("KE-PROD-001"))
                .get()
                .extracting(AssetVersionRecord::version)
                .isEqualTo("1.1.0");
        assertThat(registry.findByLifecycle("PUBLISHED")).hasSize(3);

        AssetVersionRecord rule = registry.resolve("KE-RUL-001", "1.0.0").orElseThrow();
        assertThat(rule.scope().tenantId()).isEqualTo("TENANT-CBANK");
        assertThat(rule.dependencyRefs()).singleElement()
                .extracting(ref -> ref.id())
                .isEqualTo("KE-PROD-001");
        assertThat(rule.purposeFlags()).containsExactly("INTERPRETATION");
    }

    @Test
    @DisplayName("装载 ReleaseManifest JSON 并解析不可变发布快照")
    void loadsReleaseManifestAndSnapshots() throws Exception {
        InMemoryAssetRegistry registry =
                new InMemoryAssetRegistryLoader(objectMapper).loadDirectory(resource("gk-ke-registry/assets"));
        ReleaseManifestRecord manifest = objectMapper.readValue(
                Files.readString(resource("gk-ke-registry/releases/REL-2026Q3-001.json")),
                ReleaseManifestRecord.class);

        assertThat(manifest.releaseId()).isEqualTo("REL-2026Q3-001");
        assertThat(manifest.catalogRevision()).isEqualTo(1);
        assertThat(manifest.assetRefs()).hasSize(3);

        var snapshot = registry.snapshotRelease(manifest);
        assertThat(snapshot)
                .extracting(asset -> asset.assetId() + ":" + asset.version())
                .containsExactly("KE-PROD-001:1.0.0", "KE-RUL-001:1.0.0");
    }

    private static Path resource(String name) throws URISyntaxException {
        return Paths.get(AssetCatalogRegistryTest.class.getResource("/" + name).toURI());
    }
}
