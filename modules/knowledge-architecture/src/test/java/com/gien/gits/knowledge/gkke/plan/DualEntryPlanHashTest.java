package com.gien.gits.knowledge.gkke.plan;

import static org.assertj.core.api.Assertions.assertThat;

import com.gien.gits.knowledge.gkke.model.ActivationPlanRecord;
import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Budget;
import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.MapEdge;
import com.gien.gits.knowledge.gkke.model.MapNode;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import com.gien.gits.knowledge.gkke.plan.ActivationEntryPoint.ObjectEntry;
import com.gien.gits.knowledge.gkke.plan.ActivationEntryPoint.TaskContext;
import com.gien.gits.knowledge.gkke.plan.ActivationEntryPoint.WikiEntry;
import com.gien.gits.knowledge.gkke.registry.CapabilityRegistry;
import com.gien.gits.knowledge.gkke.registry.InMemoryAssetRegistry;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * T05 行为测试：Wiki 入口与对象入口是两个独立入口（不同入参类型、不同导航来源），在相同
 * TaskContext + 相同地图版本 + 相同发布快照下分别装配，产出的 canonical planHash 必须相等。
 *
 * <p>关键：两个入口是不同的 record 对象、携带不同导航字段，分别调用各自装配方法，
 * 不是同一 Java 对象哈希两次。
 */
class DualEntryPlanHashTest {

    private static final String TENANT = "TENANT-CBANK";
    private static final String RELEASE = "REL-2026Q3-001";
    private static final String CORE = "core-1.0.0";
    private static final int REVISION = 7;
    private static final String ROUTE_POLICY_VERSION = "1.0.0";
    private static final String PERMISSION_REF = "PD-2026Q3-001";
    private static final String PURPOSE = "INTERPRETATION";

    private InMemoryAssetRegistry registry;
    private CapabilityRegistry capabilities;
    private ActivationEntryPoint entryPoint;

    @BeforeEach
    void setUp() {
        registry = new InMemoryAssetRegistry();
        capabilities = new CapabilityRegistry();
        ActivationPlanner planner =
                new ActivationPlanner(registry, capabilities, new PlanCanonicalHasher());
        entryPoint = new ActivationEntryPoint(planner);
    }

    @Test
    @DisplayName("T05: Wiki 入口与对象入口（独立对象、不同导航来源）同 TaskContext → planHash 相等")
    void twoIndependentEntriesProduceSamePlanHash() {
        registry.register(published("KE-RULE-001"));
        capabilities.register("CAP-SEARCH", "1.0.0");
        KnowledgeMapRecord map = demoMap();
        TaskContext ctx = sharedTaskContext();

        WikiEntry wiki = new WikiEntry(ctx, map, RELEASE, CORE, REVISION, ROUTE_POLICY_VERSION,
                PERMISSION_REF, List.of(), "wiki://maps/KM-DUAL/1.0.0#N-TASK");
        ObjectEntry object = new ObjectEntry(ctx, map, RELEASE, CORE, REVISION, ROUTE_POLICY_VERSION,
                PERMISSION_REF, List.of(), "crm://customer/CUST-001", "knowledge-panel");

        ActivationPlanRecord fromWiki = entryPoint.fromWiki(wiki);
        ActivationPlanRecord fromObject = entryPoint.fromObject(object);

        // 两个独立计划对象，不是同一引用
        assertThat(fromWiki).isNotSameAs(fromObject);
        assertThat(fromWiki.planHash()).isNotBlank();
        // canonical planHash 逐字节相等
        assertThat(fromObject.planHash()).isEqualTo(fromWiki.planHash());
        // 载荷也一致（步骤、引用、用途、范围、预算）
        assertThat(fromObject.steps()).isEqualTo(fromWiki.steps());
        assertThat(fromObject.assetRefs()).isEqualTo(fromWiki.assetRefs());
        assertThat(fromObject.capabilityRefs()).isEqualTo(fromWiki.capabilityRefs());
        assertThat(fromObject.purpose()).isEqualTo(fromWiki.purpose());
    }

    @Test
    @DisplayName("入口导航来源（wikiPage/businessObjectRef）不进入载荷，不影响 planHash")
    void navigationSourceDoesNotAffectHash() {
        registry.register(published("KE-RULE-001"));
        capabilities.register("CAP-SEARCH", "1.0.0");
        KnowledgeMapRecord map = demoMap();
        TaskContext ctx = sharedTaskContext();

        ActivationPlanRecord a = entryPoint.fromWiki(new WikiEntry(ctx, map, RELEASE, CORE,
                REVISION, ROUTE_POLICY_VERSION, PERMISSION_REF, List.of(), "wiki://page-A"));
        ActivationPlanRecord b = entryPoint.fromWiki(new WikiEntry(ctx, map, RELEASE, CORE,
                REVISION, ROUTE_POLICY_VERSION, PERMISSION_REF, List.of(),
                "wiki://totally-different-page-B"));

        assertThat(b.planHash()).isEqualTo(a.planHash());
    }

    @Test
    @DisplayName("不同发布快照（releaseId）产生不同 planHash")
    void differentReleaseProducesDifferentHash() {
        registry.register(published("KE-RULE-001"));
        capabilities.register("CAP-SEARCH", "1.0.0");
        KnowledgeMapRecord map = demoMap();
        TaskContext ctx = sharedTaskContext();

        ActivationPlanRecord p1 = entryPoint.fromWiki(new WikiEntry(ctx, map, "REL-1", CORE,
                REVISION, ROUTE_POLICY_VERSION, PERMISSION_REF, List.of(), "wiki://a"));
        ActivationPlanRecord p2 = entryPoint.fromObject(new ObjectEntry(ctx, map, "REL-2", CORE,
                REVISION, ROUTE_POLICY_VERSION, PERMISSION_REF, List.of(), "crm://x", "anchor"));

        assertThat(p2.planHash()).isNotEqualTo(p1.planHash());
    }

    @Test
    @DisplayName("不同 TaskContext（purpose）产生不同 planHash")
    void differentTaskContextProducesDifferentHash() {
        registry.register(published("KE-RULE-001"));
        capabilities.register("CAP-SEARCH", "1.0.0");
        KnowledgeMapRecord map = demoMap();
        Scope scope = new Scope(TENANT, List.of(), List.of(), PURPOSE);
        TaskContext interpretation =
                new TaskContext("TASK-001", "INTERPRETATION", scope, new Budget(8, 4000, 30000L));
        TaskContext recommendation =
                new TaskContext("TASK-001", "RECOMMENDATION", scope, new Budget(8, 4000, 30000L));

        ActivationPlanRecord p1 = entryPoint.fromWiki(new WikiEntry(interpretation, map, RELEASE,
                CORE, REVISION, ROUTE_POLICY_VERSION, PERMISSION_REF, List.of(), "wiki://a"));
        ActivationPlanRecord p2 = entryPoint.fromObject(new ObjectEntry(recommendation, map,
                RELEASE, CORE, REVISION, ROUTE_POLICY_VERSION, PERMISSION_REF, List.of(),
                "crm://x", "anchor"));

        assertThat(p2.planHash()).isNotEqualTo(p1.planHash());
    }

    private TaskContext sharedTaskContext() {
        Scope scope = new Scope(TENANT, List.of(), List.of(), PURPOSE);
        return new TaskContext("TASK-001", PURPOSE, scope, new Budget(8, 4000, 30000L));
    }

    private KnowledgeMapRecord demoMap() {
        MapNode task = new MapNode("N-TASK", MapNode.TYPE_TASK, "任务节点", null);
        MapNode rule = new MapNode("N-RULE", MapNode.TYPE_ASSET, "规则节点",
                new VersionRef("KE-RULE-001", "1.0.0"));
        MapNode cap = new MapNode("N-CAP", MapNode.TYPE_CAPABILITY, "能力节点",
                new VersionRef("CAP-SEARCH", "1.0.0"));
        MapEdge e1 = new MapEdge("E1", "N-TASK", "N-RULE", MapEdge.REL_DEPENDS_ON, null, null);
        MapEdge e2 = new MapEdge("E2", "N-TASK", "N-CAP", MapEdge.REL_USES, null, null);
        return new KnowledgeMapRecord("gk-ke/v1", Boolean.FALSE, "KM-DUAL", "1.0.0", RELEASE,
                List.of("TASK-A"), List.of("N-TASK"),
                new VersionRef("RP-DUAL", ROUTE_POLICY_VERSION),
                List.of(task, rule, cap), List.of(e1, e2), PURPOSE,
                new Scope(TENANT, List.of(), List.of(), PURPOSE));
    }

    private AssetVersionRecord published(String id) {
        Scope scope = new Scope(TENANT, List.of(), List.of(), PURPOSE);
        return new AssetVersionRecord("gk-ke/v1", Boolean.FALSE, id, "1.0.0",
                "KNOWLEDGE_RULE", "POLICY", "title-" + id, "KERT", "POLICY_OWNER",
                "s3://gits-ke/" + id + "/content.md", "hash-" + id, CORE,
                scope, List.of(PURPOSE), "PUBLISHED", List.of());
    }
}
