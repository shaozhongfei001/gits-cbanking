package com.gien.gits.adapter.filesystem;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.gien.gits.adapter.jena.JenaOntologyAdapter;
import com.gien.gits.knowledge.ActivationPlan;
import com.gien.gits.knowledge.plan.ActivationPlanRequest;
import com.gien.gits.knowledge.plan.DefaultActivationPlanner;
import com.gien.gits.knowledge.plan.PlanDecision;
import com.gien.gits.knowledge.port.ActivationContractPort;
import com.gien.gits.knowledge.port.AssetCatalogPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import com.gien.gits.knowledge.port.RoutePolicyPort;
import com.gien.gits.knowledge.port.RoutePolicyEvaluatorPort;
import com.gien.gits.knowledge.route.DefaultRoutePolicyEvaluator;
import com.gien.gits.semantic.OntologyPort;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.Set;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * 端到端集成测试：用真实 filesystem readers 加载 P20 合同数据，验证
 * ActivationPlanner 产出与黄金计划的确定性字段一致。
 *
 * <p>数据源为仓库 {@code specs/knowledge-architecture/}；本体用**真实**
 * {@link JenaOntologyAdapter} 读 {@code specs/semantic/gits-core.owl.ttl}
 * （GK17 / WP2.2：本体真实进入路由）。</p>
 */
class DefaultActivationPlannerFilesystemIT {

    private static Path KA;
    private static Path ONTOLOGY;

    @BeforeAll
    static void resolveKnowledgeArchitectureDir() {
        KA = Path.of(".").toAbsolutePath().normalize();
        // 从模块工作目录逐级向上定位 specs/knowledge-architecture
        while (KA != null && !KA.resolve("specs/knowledge-architecture").toFile().isDirectory()) {
            KA = KA.getParent();
        }
        assertTrue(KA != null && KA.resolve("specs/knowledge-architecture").toFile().isDirectory(),
                "must locate specs/knowledge-architecture from workspace root");
        ONTOLOGY = KA.resolve("specs/semantic/gits-core.owl.ttl");
        assertTrue(Files.isRegularFile(ONTOLOGY), "must locate specs/semantic/gits-core.owl.ttl");
        KA = KA.resolve("specs/knowledge-architecture");
    }

    private static DefaultActivationPlanner planner() {
        return planner(ONTOLOGY);
    }

    /** 以指定的本体文件装配规划器（供"临时副本"对照使用）。 */
    private static DefaultActivationPlanner planner(Path ontologyPath) {
        RoutePolicyPort route = new FilesystemRoutePolicyReader(KA.resolve("routes"));
        RoutePolicyEvaluatorPort evaluator =
                new DefaultRoutePolicyEvaluator(route, "RP-CORP-RM-001");
        ActivationContractPort contract = new FilesystemActivationContractReader(KA.resolve("activations"));
        AssetCatalogPort assets = new FilesystemAssetCatalogReader(KA.resolve("assets"));
        KnowledgeMapPort map = new FilesystemKnowledgeMapReader(KA.resolve("maps"));
        OntologyPort ontology = new JenaOntologyAdapter(ontologyPath, "CTR-SEM-002");
        return new DefaultActivationPlanner(
                evaluator, contract, assets, map, ontology, () -> Instant.parse("2026-08-18T09:00:00Z"));
    }

    private static ActivationPlan planPreVisit(Path ontologyPath) {
        PlanDecision decision = planner(ontologyPath).plan(new ActivationPlanRequest(
                "PRE_VISIT_PREPARATION", "CUST-001", "RELATIONSHIP_MANAGER",
                "PD-ALLOW", Instant.parse("2026-08-18T09:00:00Z"), null));
        assertInstanceOf(PlanDecision.AllowPlan.class, decision, () -> "expected allow, got=" + decision);
        return decision.planOpt().orElseThrow();
    }

    @Test
    void preVisitPlanMatchesGoldenDeterministicFields() {
        DefaultActivationPlanner planner = planner();
        PlanDecision decision = planner.plan(new ActivationPlanRequest(
                "PRE_VISIT_PREPARATION", "CUST-001", "RELATIONSHIP_MANAGER",
                "PD-ALLOW", Instant.parse("2026-08-18T09:00:00Z"), null));

        assertInstanceOf(PlanDecision.AllowPlan.class, decision);
        ActivationPlan plan = decision.planOpt().orElseThrow();

        assertEquals("ONTOLOGY_THEN_MAP", plan.routeMode());
        assertEquals("PRE_VISIT_PREPARATION", plan.taskType());
        // 黄金 AP-PREVISIT 的确定性字段
        assertEquals(Set.of("SQ-CUSTOMER-RELATIONSHIP", "SQ-RELATED-LEGAL-ENTITIES", "SQ-KYC-GAPS",
                        "SQ-OPEN-COMMITMENTS", "SQ-ACTIVE-PRODUCT-VERSIONS"), Set.copyOf(plan.semanticQueries()));
        assertEquals(Set.of("CALLER_SCOPE_ALLOWED", "CLAIM_NOT_FACT", "SIGNAL_NOT_OPPORTUNITY",
                        "PRODUCT_VERSION_ACTIVE"), Set.copyOf(plan.ruleChecks()));
        assertEquals(Set.of("SP-02", "SP-05", "SP-15", "SP-10"), Set.copyOf(plan.skills()));
        assertEquals(12000, plan.context().maxTokens());
        assertEquals("CONTRACT_PRIORITY", plan.context().trimPolicy());
        // 9 个资产按 sequence 排序
        assertEquals(9, plan.selectedAssets().size());
        assertEquals(1, plan.selectedAssets().get(0).sequence());
    }

    @Test
    void factReconciliationPlanMatchesGoldenDeterministicFields() {
        DefaultActivationPlanner planner = planner();
        PlanDecision decision = planner.plan(new ActivationPlanRequest(
                "FACT_RECONCILIATION_30M", "CUST-001", "RELATIONSHIP_MANAGER",
                "PD-ALLOW", Instant.parse("2026-08-18T09:05:00Z"), "CLM-3000W"));

        assertInstanceOf(PlanDecision.AllowPlan.class, decision);
        ActivationPlan plan = decision.planOpt().orElseThrow();

        assertEquals("ONTOLOGY_FIRST", plan.routeMode());
        assertEquals(Set.of("SQ-CLAIM-SUBJECT-RELATIONS", "SQ-CREDIT-AND-PROJECT-AMOUNTS",
                "SQ-PROJECT-AND-BORROWER-ENTITY"), Set.copyOf(plan.semanticQueries()));
        assertEquals(Set.of("CLAIM_NOT_FACT", "AVAILABLE_CREDIT_NOT_NEW_NEED", "PROJECT_NOT_BORROWER",
                "SIGNAL_NOT_OPPORTUNITY", "BANKABILITY_NOT_APPROVAL"), Set.copyOf(plan.ruleChecks()));
        assertEquals(Set.of("SP-02", "SP-07"), Set.copyOf(plan.skills()));
        assertEquals(8000, plan.context().maxTokens());
        assertEquals("FAIL_ON_OVERFLOW", plan.context().trimPolicy());
        // 6 个资产全部登记并按 sequence 排序
        assertEquals(6, plan.selectedAssets().size());
        assertEquals("ASSET-DATA-CUSTOMER-PROFILE", plan.selectedAssets().get(0).assetId());
        assertEquals("ASSET-KNOW-CLAIM-RECONCILIATION", plan.selectedAssets().get(5).assetId());
    }

    @Test
    void unknownTaskDenied() {
        DefaultActivationPlanner planner = planner();
        PlanDecision decision = planner.plan(new ActivationPlanRequest(
                "UNKNOWN_TASK", "CUST-001", "AGENT", "PD-ALLOW",
                Instant.parse("2026-08-18T09:00:00Z"), null));

        assertInstanceOf(PlanDecision.Deny.class, decision);
        assertEquals("DENY_UNMAPPED_TASK", ((PlanDecision.Deny) decision).decisionCode());
    }

    // --- GK17 / WP2.2 + WP2.3：本体真实进入路由（端到端，真实文件 + 真实 Jena 解析）---

    @Test
    void realOntologyIsLoadedAndEvidencedInPlanTrace() {
        ActivationPlan plan = planPreVisit(ONTOLOGY);

        // 版本与黄金计划 versions.ontology 同源（合同先行：黄金已钉住该取值）
        assertEquals("CTR-SEM-002@sha256:705578d6324abd0c", plan.versions().ontology());
        // 真实本体读数（W1 实测基线 32/34/1/0）——解析若静默失效会当场失败
        String evidence = plan.trace().ontologyEvidence();
        assertTrue(evidence.contains("classes=32"), evidence);
        assertTrue(evidence.contains("objectProperties=34"), evidence);
        assertTrue(evidence.contains("datatypeProperties=1"), evidence);
        assertTrue(evidence.contains("individuals=0"), evidence);
        assertTrue(evidence.contains("gits-core.owl.ttl"), evidence);
    }

    @Test
    void planHashChangesWhenOntologyContentChangesAndReturnsWhenRestored(@TempDir Path tempDir)
            throws IOException {
        // 负例 2（判据 V2，端到端 · 真实文件）：
        // 同一请求下**改动本体内容（临时副本，不动权威源）⇒ planHash 必变**；内容不变 ⇒ 不变。
        Path copy = tempDir.resolve("gits-core.owl.ttl");
        Files.copy(ONTOLOGY, copy, StandardCopyOption.REPLACE_EXISTING);
        ActivationPlan baseline = planPreVisit(copy);

        // 变异：追加一个类声明（32 类 → 33 类）
        Files.writeString(copy, Files.readString(copy) + "\ngits:gk17V2Probe a owl:Class .\n");
        ActivationPlan mutated = planPreVisit(copy);

        // 恢复：逐字节复制回权威源内容
        Files.copy(ONTOLOGY, copy, StandardCopyOption.REPLACE_EXISTING);
        ActivationPlan restored = planPreVisit(copy);

        // 反空转前置：先证明变异**确实改变了本体读数**，否则"哈希变了"可能有别的原因
        assertNotEquals(baseline.versions().ontology(), mutated.versions().ontology(),
                "变异必须改变本体版本，否则本用例证明不了 V2");
        assertTrue(mutated.trace().ontologyEvidence().contains("classes=33"),
                mutated.trace().ontologyEvidence());

        assertNotEquals(baseline.trace().planHash(), mutated.trace().planHash(),
                "本体内容变而 planHash 未变 ⇒ 判据 V2 在构造上不成立");
        assertEquals(baseline.versions().ontology(), restored.versions().ontology(),
                "恢复本体后版本必须回到基线");
        assertEquals(baseline.trace().planHash(), restored.trace().planHash(),
                "恢复本体后 planHash 必须回到基线（可重放）");
    }
}
