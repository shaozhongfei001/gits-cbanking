package com.gien.gits.knowledge.gkke.registry;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G1 依赖闭包测试（CR-02 §4.1 dependencyRefs 传递闭包）。
 */
class DependencyClosureTest {

    private final InMemoryAssetRegistry registry = new InMemoryAssetRegistry();

    @Test
    @DisplayName("传递依赖闭包：被依赖者在前、根资产在最后，重复依赖只出现一次")
    void transitiveClosureTopologicalOrder() {
        // A -> B -> D；A -> C -> D（D 被两条路径共享）
        registry.register(asset("KE-D", "1.0.0", List.of()));
        registry.register(asset("KE-B", "1.0.0", List.of(new VersionRef("KE-D", "1.0.0"))));
        registry.register(asset("KE-C", "1.0.0", List.of(new VersionRef("KE-D", "1.0.0"))));
        registry.register(asset("KE-A", "1.0.0",
                List.of(new VersionRef("KE-B", "1.0.0"), new VersionRef("KE-C", "1.0.0"))));

        List<AssetVersionRecord> closure = registry.dependencyClosure("KE-A", "1.0.0");

        assertThat(closure).extracting(AssetVersionRecord::assetId)
                .containsExactly("KE-D", "KE-B", "KE-C", "KE-A");
        assertThat(closure).extracting(AssetVersionRecord::assetId).doesNotHaveDuplicates();
    }

    @Test
    @DisplayName("无依赖资产闭包只含自身")
    void closureOfLeafIsItself() {
        registry.register(asset("KE-LEAF", "1.0.0", List.of()));

        assertThat(registry.dependencyClosure("KE-LEAF", "1.0.0"))
                .extracting(AssetVersionRecord::assetId)
                .containsExactly("KE-LEAF");
    }

    @Test
    @DisplayName("依赖环抛出 DependencyCycleException")
    void cycleDetected() {
        registry.register(asset("KE-X", "1.0.0", List.of(new VersionRef("KE-Y", "1.0.0"))));
        registry.register(asset("KE-Y", "1.0.0", List.of(new VersionRef("KE-X", "1.0.0"))));

        assertThatThrownBy(() -> registry.dependencyClosure("KE-X", "1.0.0"))
                .isInstanceOf(DependencyCycleException.class)
                .hasMessageContaining("cycle");
    }

    @Test
    @DisplayName("缺失依赖抛出 AssetNotFoundException；根资产缺失同样抛出")
    void missingDependencyFails() {
        registry.register(asset("KE-A", "1.0.0", List.of(new VersionRef("KE-GHOST", "1.0.0"))));

        assertThatThrownBy(() -> registry.dependencyClosure("KE-A", "1.0.0"))
                .isInstanceOf(AssetNotFoundException.class)
                .hasMessageContaining("KE-GHOST");
        assertThatThrownBy(() -> registry.dependencyClosure("KE-ROOT", "9.9.9"))
                .isInstanceOf(AssetNotFoundException.class);
    }

    private static AssetVersionRecord asset(String id, String version, List<VersionRef> deps) {
        return new AssetVersionRecord(id, version, "KNOWLEDGE_RULE", "POLICY",
                "title-" + id, "KERT", "POLICY_ADMIN", "s3://" + id, "hash-" + id,
                "core-1.0.0", new Scope("T1", List.of(), List.of(), "INTERPRETATION"),
                List.of("INTERPRETATION"), "PUBLISHED", deps);
    }
}
