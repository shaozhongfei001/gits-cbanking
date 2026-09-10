package com.gien.gits.knowledge.gkke.permission;

import static org.assertj.core.api.Assertions.assertThat;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.registry.InMemoryAssetRegistry;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G3 访问决议测试（CR-02 §4.1 生命周期/用途短路，C06 决议可追溯）。
 */
class AccessDecisionTest {

    private static final String TENANT = "TENANT-CBANK";
    private final RegistryPermissionFilter filter = new RegistryPermissionFilter(new InMemoryAssetRegistry());

    @Test
    @DisplayName("全部匹配时决议 ALLOW")
    void allowWhenAllMatch() {
        AssetVersionRecord asset = published("KE-1", "PUBLISHED",
                new Scope(TENANT, List.of("ORG-001"), List.of("CUS-001"), "INTERPRETATION"),
                List.of("INTERPRETATION"));
        PermissionContext context =
                new PermissionContext(TENANT, List.of("ORG-001"), List.of("CUS-001"), "INTERPRETATION");

        PermissionDecision decision = filter.decide(asset, context);

        assertThat(decision.allowed()).isTrue();
        assertThat(decision.reason()).isEqualTo(PermissionDecision.ALLOW);
    }

    @Test
    @DisplayName("非 PUBLISHED 生命周期一律拒绝（DRAFT/REVIEW/DEPRECATED）")
    void denyNonPublishedLifecycle() {
        PermissionContext context =
                new PermissionContext(TENANT, List.of(), List.of(), "INTERPRETATION");
        for (String lifecycle : List.of("DRAFT", "REVIEW", "DEPRECATED")) {
            AssetVersionRecord asset = published("KE-1", lifecycle,
                    new Scope(TENANT, List.of(), List.of(), "INTERPRETATION"),
                    List.of("INTERPRETATION"));

            assertThat(filter.decide(asset, context).reason())
                    .isEqualTo(PermissionDecision.NOT_PUBLISHED);
        }
    }

    @Test
    @DisplayName("用途未在 purposeFlags 声明时拒绝")
    void denyUndeclaredPurpose() {
        AssetVersionRecord asset = published("KE-1", "PUBLISHED",
                new Scope(TENANT, List.of(), List.of(), "RESEARCH"),
                List.of("RESEARCH"));
        PermissionContext recommendation =
                new PermissionContext(TENANT, List.of(), List.of(), "RECOMMENDATION");

        assertThat(filter.decide(asset, recommendation).reason())
                .isEqualTo(PermissionDecision.PURPOSE_NOT_DECLARED);
    }

    @Test
    @DisplayName("决议短路：生命周期失败优先于租户/用途原因")
    void shortCircuitOrder() {
        AssetVersionRecord asset = published("KE-1", "DRAFT",
                new Scope("TENANT-OTHER", List.of(), List.of(), "RESEARCH"),
                List.of("RESEARCH"));
        PermissionContext context =
                new PermissionContext(TENANT, List.of(), List.of(), "INTERPRETATION");

        assertThat(filter.decide(asset, context).reason())
                .isEqualTo(PermissionDecision.NOT_PUBLISHED);
    }

    private static AssetVersionRecord published(String id, String lifecycle, Scope scope,
                                                List<String> purposes) {
        return new AssetVersionRecord(id, "1.0.0", "FOUNDATIONAL_DATA", "PRODUCT_CARD",
                "title-" + id, "KERT", "PRODUCT_OWNER", "s3://" + id, "hash-" + id,
                "core-1.0.0", scope, purposes, lifecycle, List.of());
    }
}
