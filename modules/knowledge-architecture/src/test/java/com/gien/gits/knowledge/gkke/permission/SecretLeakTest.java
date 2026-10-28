package com.gien.gits.knowledge.gkke.permission;

import static org.assertj.core.api.Assertions.assertThat;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.registry.InMemoryAssetRegistry;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G3 敏感信息不泄露测试（CR-02 §7：运行时不直接访问存储，不暴露内部位置）。
 */
class SecretLeakTest {

    private static final String TENANT = "TENANT-CBANK";
    private final RegistryPermissionFilter filter = new RegistryPermissionFilter(new InMemoryAssetRegistry());

    @Test
    @DisplayName("安全投影不携带 contentRef/contentHash/ownerSystem 等内部字段")
    void projectionHidesInternalStorage() {
        AssetVersionRecord asset = new AssetVersionRecord(
                "gk-ke/v1", Boolean.FALSE, "KE-SECRET", "1.0.0",
                "FOUNDATIONAL_DATA", "PRODUCT_CARD", "产品卡",
                "KERT", "PRODUCT_OWNER",
                "s3://gits-ke/KE-SECRET/1.0.0/content.md",
                "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                "core-1.0.0",
                new Scope(TENANT, List.of("ORG-001"), List.of("CUS-001"), "INTERPRETATION"),
                List.of("INTERPRETATION"), "PUBLISHED", List.of());
        PermissionContext context =
                new PermissionContext(TENANT, List.of("ORG-001"), List.of("CUS-001"), "INTERPRETATION");

        AssetView view = filter.filter(List.of(asset), context).get(0);

        assertThat(view.assetId()).isEqualTo("KE-SECRET");
        assertThat(view.lifecycle()).isEqualTo("PUBLISHED");
        assertThat(view.toString())
                .doesNotContain("s3://")
                .doesNotContain("9f86d081884c7d65")
                .doesNotContain("KERT");
    }

    @Test
    @DisplayName("被拒绝资产不出现在投影结果中（拒绝即不可见，而非返回脱敏对象）")
    void deniedAssetNotProjected() {
        AssetVersionRecord secret = new AssetVersionRecord(
                "gk-ke/v1", Boolean.FALSE, "KE-SECRET", "1.0.0",
                "FOUNDATIONAL_DATA", "PRODUCT_CARD", "机密产品卡",
                "KERT", "PRODUCT_OWNER", "s3://secret", "secret-hash", "core-1.0.0",
                new Scope(TENANT, List.of("ORG-999"), List.of(), "INTERPRETATION"),
                List.of("INTERPRETATION"), "PUBLISHED", List.of());
        PermissionContext context =
                new PermissionContext(TENANT, List.of("ORG-001"), List.of(), "INTERPRETATION");

        List<AssetView> views = filter.filter(List.of(secret), context);

        assertThat(views).isEmpty();
    }
}
