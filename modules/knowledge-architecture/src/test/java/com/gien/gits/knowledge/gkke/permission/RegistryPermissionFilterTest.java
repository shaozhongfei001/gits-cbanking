package com.gien.gits.knowledge.gkke.permission;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import com.gien.gits.knowledge.gkke.registry.InMemoryAssetRegistry;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G3 权限过滤列表行为测试（CR-02 §4.1/§7，验收 T07）。
 */
class RegistryPermissionFilterTest {

    private static final String TENANT = "TENANT-CBANK";
    private static final PermissionContext FULL_ACCESS =
            new PermissionContext(TENANT, List.of("ORG-001"), List.of("CUS-001"), "INTERPRETATION");

    private InMemoryAssetRegistry registry;
    private RegistryPermissionFilter filter;

    @BeforeEach
    void setUp() {
        registry = new InMemoryAssetRegistry();
        filter = new RegistryPermissionFilter(registry);
    }

    @Test
    @DisplayName("过滤候选列表：只返回允许资产，保持候选顺序，无匹配返回空列表")
    void filtersCandidateList() {
        registry.register(published("KE-ALLOW",
                new Scope(TENANT, List.of("ORG-001"), List.of(), "INTERPRETATION")));
        registry.register(published("KE-DENY",
                new Scope(TENANT, List.of("ORG-999"), List.of(), "INTERPRETATION")));

        List<AssetView> views = filter.filter(registry.findByLifecycle("PUBLISHED"), FULL_ACCESS);

        assertThat(views).extracting(AssetView::assetId).containsExactly("KE-ALLOW");
        assertThat(filter.filter(registry.findByLifecycle("DRAFT"), FULL_ACCESS)).isEmpty();
    }

    @Test
    @DisplayName("按版本引用过滤：缺失引用被跳过不抛异常")
    void filtersRefsSkippingMissing() {
        registry.register(published("KE-1",
                new Scope(TENANT, List.of("ORG-001"), List.of(), "INTERPRETATION")));

        List<AssetView> views = filter.filterRefs(List.of(
                new VersionRef("KE-1", "1.0.0"),
                new VersionRef("KE-GHOST", "1.0.0")), FULL_ACCESS);

        assertThat(views).extracting(AssetView::assetId).containsExactly("KE-1");
    }

    @Test
    @DisplayName("null 上下文或 null 候选被拒绝")
    void rejectsNullArguments() {
        AssetVersionRecord asset = published("KE-1",
                new Scope(TENANT, List.of(), List.of(), "INTERPRETATION"));

        assertThatThrownBy(() -> filter.filter(List.of(asset), null))
                .isInstanceOf(NullPointerException.class);
        assertThatThrownBy(() -> new RegistryPermissionFilter(null))
                .isInstanceOf(NullPointerException.class);
    }

    private static AssetVersionRecord published(String id, Scope scope) {
        return new AssetVersionRecord(id, "1.0.0", "FOUNDATIONAL_DATA", "PRODUCT_CARD",
                "title-" + id, "KERT", "PRODUCT_OWNER",
                "s3://gits-ke/" + id + "/content.md", "secret-hash-" + id,
                "core-1.0.0", scope, List.of("INTERPRETATION"), "PUBLISHED", List.of());
    }
}
