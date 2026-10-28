package com.gien.gits.knowledge.gkke.permission;

import static org.assertj.core.api.Assertions.assertThat;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.registry.InMemoryAssetRegistry;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G3 scope 匹配测试（CR-02 §4.1：tenant/org/customer 限制集合）。
 */
class ScopeMatchTest {

    private static final String TENANT = "TENANT-CBANK";
    private final RegistryPermissionFilter filter = new RegistryPermissionFilter(new InMemoryAssetRegistry());

    @Test
    @DisplayName("机构限制：授权集合与资产限制有交集才放行，空限制不约束")
    void enforcesOrgScope() {
        PermissionContext context =
                new PermissionContext(TENANT, List.of("ORG-001"), List.of(), "INTERPRETATION");
        AssetVersionRecord restricted = published("KE-1",
                new Scope(TENANT, List.of("ORG-999"), List.of(), "INTERPRETATION"));
        AssetVersionRecord intersecting = published("KE-2",
                new Scope(TENANT, List.of("ORG-001", "ORG-002"), List.of(), "INTERPRETATION"));
        AssetVersionRecord unrestricted = published("KE-3",
                new Scope(TENANT, List.of(), List.of(), "INTERPRETATION"));

        assertThat(filter.decide(restricted, context).reason())
                .isEqualTo(PermissionDecision.ORG_NOT_AUTHORIZED);
        assertThat(filter.decide(intersecting, context).allowed()).isTrue();
        assertThat(filter.decide(unrestricted, context).allowed()).isTrue();
    }

    @Test
    @DisplayName("客户限制：授权客户与资产限制有交集才放行，空限制不约束")
    void enforcesCustomerScope() {
        PermissionContext context =
                new PermissionContext(TENANT, List.of("ORG-001"), List.of("CUS-001"), "INTERPRETATION");
        AssetVersionRecord restricted = published("KE-1",
                new Scope(TENANT, List.of("ORG-001"), List.of("CUS-999"), "INTERPRETATION"));
        AssetVersionRecord intersecting = published("KE-2",
                new Scope(TENANT, List.of("ORG-001"), List.of("CUS-001", "CUS-002"), "INTERPRETATION"));
        AssetVersionRecord unrestricted = published("KE-3",
                new Scope(TENANT, List.of("ORG-001"), List.of(), "INTERPRETATION"));

        assertThat(filter.decide(restricted, context).reason())
                .isEqualTo(PermissionDecision.CUSTOMER_NOT_AUTHORIZED);
        assertThat(filter.decide(intersecting, context).allowed()).isTrue();
        assertThat(filter.decide(unrestricted, context).allowed()).isTrue();
    }

    @Test
    @DisplayName("租户必须精确相等")
    void enforcesTenant() {
        PermissionContext context =
                new PermissionContext(TENANT, List.of(), List.of(), "INTERPRETATION");
        AssetVersionRecord other = published("KE-1",
                new Scope("TENANT-OTHER", List.of(), List.of(), "INTERPRETATION"));

        assertThat(filter.decide(other, context).reason())
                .isEqualTo(PermissionDecision.TENANT_MISMATCH);
    }

    private static AssetVersionRecord published(String id, Scope scope) {
        return new AssetVersionRecord("gk-ke/v1", Boolean.FALSE, id, "1.0.0",
                "FOUNDATIONAL_DATA", "PRODUCT_CARD", "title-" + id, "KERT", "PRODUCT_OWNER",
                "s3://" + id, "hash-" + id, "core-1.0.0", scope,
                List.of("INTERPRETATION"), "PUBLISHED", List.of());
    }
}
