package com.gien.gits.knowledge.gkke.permission;

import static org.assertj.core.api.Assertions.assertThat;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.MapEdge;
import com.gien.gits.knowledge.gkke.model.MapNode;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import com.gien.gits.knowledge.gkke.registry.InMemoryAssetRegistry;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

/**
 * T07 行为测试：权限感知目录四类出口对无权主体零泄漏，以及五要素缓存键的隔离性。
 *
 * <p>秘密资产 SECRET 限定在 ORG-SECRET 机构；无权主体（仅持 ORG-001）在目录列表、标题摘要、
 * 关系邻居、节点计数四类出口都不得感知到该秘密资产的存在。
 */
class PermissionAwareCatalogTest {

    private static final String TENANT = "TENANT-CBANK";
    private static final String PURPOSE = "INTERPRETATION";
    private static final String RELEASE = "REL-2026Q3-001";
    private static final int REVISION = 7;

    private InMemoryAssetRegistry registry;
    private PermissionAwareCatalog catalog;

    /** 无权主体：仅授权 ORG-001，看不到限定 ORG-SECRET 的秘密资产。 */
    private PermissionContext unauthorized;
    /** 有权主体：同时授权 ORG-SECRET。 */
    private PermissionContext authorized;

    @BeforeEach
    void setUp() {
        registry = new InMemoryAssetRegistry();
        catalog = new PermissionAwareCatalog(registry, new RegistryPermissionFilter(registry));

        registry.register(asset("KE-PUBLIC", "公开资产", List.of()));
        registry.register(asset("KE-SECRET", "秘密资产标题", List.of("ORG-SECRET")));

        unauthorized = context(List.of("ORG-001"), RELEASE, REVISION);
        authorized = context(List.of("ORG-001", "ORG-SECRET"), RELEASE, REVISION);
    }

    private PermissionContext context(List<String> orgs, String releaseId, int revision) {
        String scopeHash = PermissionContext.scopeHash(TENANT, orgs, List.of());
        return new PermissionContext(TENANT, orgs, List.of(), PURPOSE, scopeHash, releaseId, revision);
    }

    @Nested
    @DisplayName("四类出口零泄漏")
    class ZeroLeakage {

        @Test
        @DisplayName("出口1 目录列表：无权主体 discover 不含秘密资产（存在性零泄漏）")
        void discoverHidesSecret() {
            List<AssetView> views = catalog.discover(unauthorized);

            assertThat(views).extracting(AssetView::assetId).containsExactly("KE-PUBLIC");
            assertThat(views).noneSatisfy(v -> assertThat(v.title()).contains("秘密"));
            // 有权主体仍能看到两个
            assertThat(catalog.discover(authorized)).extracting(AssetView::assetId)
                    .containsExactlyInAnyOrder("KE-PUBLIC", "KE-SECRET");
        }

        @Test
        @DisplayName("出口2 标题摘要：无权主体 summaries 不含秘密节点标题")
        void summariesHideSecret() {
            KnowledgeMapRecord map = mapWithPublicAndSecret();

            Map<String, String> denied = catalog.summaries(map, unauthorized);
            assertThat(denied).containsKey("N-PUBLIC");
            assertThat(denied).doesNotContainKey("N-SECRET");
            assertThat(denied).doesNotContainValue("秘密资产标题");

            Map<String, String> allowed = catalog.summaries(map, authorized);
            assertThat(allowed).containsKeys("N-PUBLIC", "N-SECRET");
        }

        @Test
        @DisplayName("出口3 关系邻居：无权主体从公开节点看不到秘密邻居")
        void neighborsHideSecret() {
            KnowledgeMapRecord map = mapWithPublicAndSecret();

            List<String> denied = catalog.neighbors(map, "N-PUBLIC", unauthorized);
            assertThat(denied).isEmpty();

            // 有权主体可见秘密邻居
            assertThat(catalog.neighbors(map, "N-PUBLIC", authorized)).containsExactly("N-SECRET");
        }

        @Test
        @DisplayName("出口3b 关系邻居：无权主体直接查询秘密节点返回空（不确认节点存在）")
        void neighborsOfSecretNodeEmptyForUnauthorized() {
            KnowledgeMapRecord map = mapWithPublicAndSecret();

            assertThat(catalog.neighbors(map, "N-SECRET", unauthorized)).isEmpty();
        }

        @Test
        @DisplayName("出口4 节点计数：无权主体计数不含秘密节点")
        void countExcludesSecret() {
            KnowledgeMapRecord map = mapWithPublicAndSecret();

            assertThat(catalog.countVisibleNodes(map, unauthorized)).isEqualTo(2);
            assertThat(catalog.countVisibleNodes(map, authorized)).isEqualTo(3);
        }
    }

    @Nested
    @DisplayName("五要素缓存键隔离")
    class CacheIsolation {

        @Test
        @DisplayName("不同主体范围（principalScopeHash）不串缓存")
        void differentPrincipalNotShared() {
            assertThat(catalog.discover(unauthorized)).extracting(AssetView::assetId)
                    .doesNotContain("KE-SECRET");
            // 先填了无权主体缓存，再查有权主体，必须重新计算而非命中前者缓存
            assertThat(catalog.discover(authorized)).extracting(AssetView::assetId)
                    .contains("KE-SECRET");
        }

        @Test
        @DisplayName("不同 purpose 不串缓存")
        void differentPurposeNotShared() {
            PermissionContext research = new PermissionContext(TENANT,
                    List.of("ORG-001", "ORG-SECRET"), List.of(), "RESEARCH",
                    PermissionContext.scopeHash(TENANT, List.of("ORG-001", "ORG-SECRET"), List.of()),
                    RELEASE, REVISION);
            // 秘密资产只声明 INTERPRETATION 用途，RESEARCH 主体不应看到
            assertThat(catalog.discover(research)).extracting(AssetView::assetId)
                    .doesNotContain("KE-SECRET");
            assertThat(catalog.discover(authorized)).extracting(AssetView::assetId)
                    .contains("KE-SECRET");
        }

        @Test
        @DisplayName("不同 releaseId 不串缓存（缓存键不同）")
        void differentReleaseNotShared() {
            PermissionContext otherRelease = context(List.of("ORG-001", "ORG-SECRET"),
                    "REL-OTHER", REVISION);
            assertThat(otherRelease.cacheKey()).isNotEqualTo(authorized.cacheKey());
        }

        @Test
        @DisplayName("不同 catalogRevision 不串缓存（缓存键不同）")
        void differentRevisionNotShared() {
            PermissionContext otherRevision = context(List.of("ORG-001", "ORG-SECRET"),
                    RELEASE, REVISION + 1);
            assertThat(otherRevision.cacheKey()).isNotEqualTo(authorized.cacheKey());
        }

        @Test
        @DisplayName("不同 tenant 不串缓存（缓存键不同）")
        void differentTenantNotShared() {
            PermissionContext otherTenant = new PermissionContext("TENANT-OTHER",
                    List.of("ORG-001"), List.of(), PURPOSE,
                    PermissionContext.scopeHash("TENANT-OTHER", List.of("ORG-001"), List.of()),
                    RELEASE, REVISION);
            assertThat(otherTenant.cacheKey()).isNotEqualTo(unauthorized.cacheKey());
        }

        @Test
        @DisplayName("相同五要素得到相同缓存键（缓存可复用）")
        void sameFactorsSameKey() {
            PermissionContext again = context(List.of("ORG-001"), RELEASE, REVISION);
            assertThat(again.cacheKey()).isEqualTo(unauthorized.cacheKey());
        }
    }

    private KnowledgeMapRecord mapWithPublicAndSecret() {
        MapNode task = new MapNode("N-TASK", MapNode.TYPE_TASK, "任务", null);
        MapNode pub = new MapNode("N-PUBLIC", MapNode.TYPE_ASSET, "公开节点",
                new VersionRef("KE-PUBLIC", "1.0.0"));
        MapNode secret = new MapNode("N-SECRET", MapNode.TYPE_ASSET, "秘密资产标题",
                new VersionRef("KE-SECRET", "1.0.0"));
        MapEdge edge = new MapEdge("E1", "N-PUBLIC", "N-SECRET", MapEdge.REL_RELATED_TO, null, null);
        return new KnowledgeMapRecord("gk-ke/v1", Boolean.FALSE, "KM-T07", "1.0.0", RELEASE,
                List.of("TASK-A"), List.of("N-TASK"),
                new VersionRef("RP-T07", "1.0.0"),
                List.of(task, pub, secret), List.of(edge), PURPOSE,
                new Scope(TENANT, List.of(), List.of(), PURPOSE));
    }

    private AssetVersionRecord asset(String id, String title, List<String> orgRestriction) {
        Scope scope = new Scope(TENANT, orgRestriction, List.of(), PURPOSE);
        return new AssetVersionRecord("gk-ke/v1", Boolean.FALSE, id, "1.0.0",
                "FOUNDATIONAL_DATA", "PRODUCT_CARD", title, "KERT", "PRODUCT_OWNER",
                "s3://gits-ke/" + id + "/content.md", "hash-" + id, "core-1.0.0",
                scope, List.of(PURPOSE), "PUBLISHED", List.of());
    }
}
