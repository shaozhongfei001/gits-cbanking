package com.gien.gits.knowledge.gkke.registry;

import static org.assertj.core.api.Assertions.assertThat;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.hash.CanonicalHash;
import com.gien.gits.knowledge.hash.CanonicalJson;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G1 规范化测试（CR-02 §4.1 语义版本 + C01 §4.3 规范化哈希复用）。
 */
class NormalizationTest {

    private final InMemoryAssetRegistry registry = new InMemoryAssetRegistry();

    @Test
    @DisplayName("语义版本按数值比较而非字典序：1.10.0 > 1.2.0 > 1.0.10")
    void semanticVersionOrdering() {
        registry.register(asset("KE-1", "1.0.10"));
        registry.register(asset("KE-1", "1.2.0"));
        registry.register(asset("KE-1", "1.10.0"));

        assertThat(registry.resolveLatest("KE-1")).get()
                .extracting(AssetVersionRecord::version)
                .isEqualTo("1.10.0");
    }

    @Test
    @DisplayName("缺省补丁位按 0 处理：1.2 == 1.2.0")
    void partialVersionDefaults() {
        registry.register(asset("KE-2", "1.2"));
        registry.register(asset("KE-2", "1.2.0"));

        assertThat(registry.resolveLatest("KE-2")).isPresent();
    }

    @Test
    @DisplayName("复用 CanonicalHash：同一 JSON 不同键序/空白产生相同 SHA-256")
    void canonicalHashIsOrderIndependent() {
        String compact = "{\"assetId\":\"KE-1\",\"version\":\"1.0.0\"}";
        String reordered = "{\n  \"version\": \"1.0.0\",\n  \"assetId\": \"KE-1\"\n}";

        String hashA = CanonicalHash.sha256Hex(CanonicalJson.canonicalizeJson(compact));
        String hashB = CanonicalHash.sha256Hex(CanonicalJson.canonicalizeJson(reordered));

        assertThat(hashA).isEqualTo(hashB);
        assertThat(hashA).hasSize(64).matches("[0-9a-f]{64}");
    }

    private static AssetVersionRecord asset(String id, String version) {
        return new AssetVersionRecord("gk-ke/v1", Boolean.FALSE, id, version,
                "FOUNDATIONAL_DATA", "PRODUCT_CARD", "title", "KERT", "PRODUCT_OWNER",
                "s3://" + id, "hash", "core-1.0.0",
                new Scope("T1", List.of(), List.of(), "INTERPRETATION"),
                List.of("INTERPRETATION"), "PUBLISHED", List.of());
    }
}
