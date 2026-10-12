package com.gien.gits.api.e2e;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.gien.gits.adapter.filesystem.FilesystemActivationContractReader;
import com.gien.gits.adapter.filesystem.FilesystemAssetCatalogReader;
import com.gien.gits.adapter.filesystem.FilesystemKnowledgeMapReader;
import com.gien.gits.adapter.filesystem.FilesystemRoutePolicyReader;
import com.gien.gits.adapter.jena.JenaOntologyAdapter;
import com.gien.gits.adapter.llm.MockLlmClient;
import com.gien.gits.adapter.skill.FallbackSkillExecutionAdapter;
import com.gien.gits.api.metrics.BusinessMetrics;
import com.gien.gits.api.service.KnowledgeDrivenPrevisitReportGenerator;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.knowledge.ActivationPlan;
import com.gien.gits.knowledge.plan.ActivationPlanRequest;
import com.gien.gits.knowledge.plan.DefaultActivationPlanner;
import com.gien.gits.knowledge.plan.ExecutionMode;
import com.gien.gits.knowledge.plan.PlanDecision;
import com.gien.gits.knowledge.port.ActivationContractPort;
import com.gien.gits.knowledge.port.AssetCatalogPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import com.gien.gits.knowledge.port.RoutePolicyEvaluatorPort;
import com.gien.gits.knowledge.port.RoutePolicyPort;
import com.gien.gits.knowledge.route.DefaultRoutePolicyEvaluator;
import com.gien.gits.knowledge.route.RouteDecision;
import com.gien.gits.semantic.OntologyPort;
import com.gien.gits.semantic.OntologyPort.OntologyLoadResult;
import com.gien.gits.semantic.OntologyPort.OntologySnapshot;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.Map;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * GK17 / W6 · WP6.1 —— 判据 **V1** 的原始输出来源。
 *
 * <p>V1：{@code PRE_VISIT_PREPARATION}（路由 {@code ONTOLOGY_THEN_MAP}）跑通完整链：
 * ① 路由裁决 → ② 本体 → ③ 地图按结果定向激活资产 → ④ SKILL 调用 → ⑤ 输出证据。</p>
 *
 * <p><b>判据原文（`GK-KE-统一地图承担者论证-V1.0.md` §5）</b>：通过 = 有**可复核的原始输出**
 * （含 {@code planHash}、{@code versions.ontology}、**路由理由**）。</p>
 *
 * <p><b>装配与生产同源</b>：raw 用 {@code Filesystem*Reader} 读 {@code specs/knowledge-architecture/}，
 * 本体用**真实** {@link JenaOntologyAdapter} 读 {@code specs/semantic/gits-core.owl.ttl}
 * （与 {@code KnowledgeArchitectureConfig} 的 bean 同构，仅替换装配入口）。</p>
 *
 * <p><b>本类刻意常驻 {@code ./mvnw test}</b>（surefire，非 {@code *IT}）：链路一旦退化即失败。
 * 证据制品的写出需显式指定 {@code -Dgk17.evidence.dir=<相对仓根目录>}，
 * 未指定时只写 {@code target/} 并打印到 stdout —— **跑测试不会改动仓库**。</p>
 *
 * <p><b>非声明</b>：本类**不**声称真实 dsh/KERT 平台已接通（见 {@code step4_skill} 的策略性
 * fail-closed）；亦**不**声称 A-Box 实体/关系查询可用（本体 {@code individuals=0}）。</p>
 */
class V1PrevisitChainTest {

    private static final String ONTOLOGY_CONTRACT_REF = "CTR-SEM-002";
    private static final String EXPECTED_ONTOLOGY_VERSION = "CTR-SEM-002@sha256:705578d6324abd0c";
    private static final String TASK_TYPE = "PRE_VISIT_PREPARATION";
    private static final String CUSTOMER_ID = "CUST-E2E-0001";
    private static final String POLICY_ID = "RP-CORP-RM-001";
    private static final Instant AS_OF = Instant.parse("2026-09-15T00:00:00Z");

    private static Path repoRoot;
    private static Path knowledgeArchitecture;
    private static Path ontologyPath;

    @BeforeAll
    static void locateRepositorySources() {
        Path probe = Path.of(".").toAbsolutePath().normalize();
        while (probe != null && !probe.resolve("specs/semantic/gits-core.owl.ttl").toFile().isFile()) {
            probe = probe.getParent();
        }
        assertTrue(probe != null, "must locate repo root from workspace");
        repoRoot = probe;
        knowledgeArchitecture = repoRoot.resolve("specs/knowledge-architecture");
        ontologyPath = repoRoot.resolve("specs/semantic/gits-core.owl.ttl");
        assertTrue(Files.isDirectory(knowledgeArchitecture), "specs/knowledge-architecture must exist");
    }

    @Test
    void previsitOntologyThenMapRunsFullChainAndEmitsReviewableRawOutput() throws Exception {
        Supplier<Instant> clock = () -> AS_OF;

        // 装配：与 KnowledgeArchitectureConfig 同源的读法
        RoutePolicyPort routePolicyPort = new FilesystemRoutePolicyReader(knowledgeArchitecture.resolve("routes"));
        RoutePolicyEvaluatorPort routeEvaluator = new DefaultRoutePolicyEvaluator(routePolicyPort, POLICY_ID);
        ActivationContractPort contractPort = new FilesystemActivationContractReader(knowledgeArchitecture.resolve("activations"));
        AssetCatalogPort assetCatalogPort = new FilesystemAssetCatalogReader(knowledgeArchitecture.resolve("assets"));
        KnowledgeMapPort knowledgeMapPort = new FilesystemKnowledgeMapReader(knowledgeArchitecture.resolve("maps"));
        OntologyPort ontologyPort = new JenaOntologyAdapter(ontologyPath, ONTOLOGY_CONTRACT_REF);
        DefaultActivationPlanner planner = new DefaultActivationPlanner(
                routeEvaluator, contractPort, assetCatalogPort, knowledgeMapPort, ontologyPort, clock);

        // ── ① 路由裁决（须为 ONTOLOGY_THEN_MAP，且带可复核的 reason）────────────────
        RouteDecision routeDecision = routeEvaluator.evaluate(TASK_TYPE, ExecutionMode.SHADOW);
        RouteDecision.AllowRoute route = routeDecision.allow()
                .orElseThrow(() -> new AssertionError("PRE_VISIT_PREPARATION must be routed, got=" + routeDecision));
        assertEquals("ONTOLOGY_THEN_MAP", route.mode(), "V1 判据要求该任务走 ONTOLOGY_THEN_MAP");
        assertEquals("AC-PREVISIT-001", route.activationContractRef());
        assertFalse(route.reason().isBlank(), "路由理由不得为空（V1 判据点名要求）");

        // ── ② 本体：真实加载（不是占位串、不是计数 0）──────────────────────────────
        OntologyLoadResult ontologyResult = ontologyPort.load();
        assertTrue(ontologyResult.isLoaded(),
                () -> "ontology must load, failureReason=" + ontologyResult.failureReason());
        OntologySnapshot ontology = ontologyResult.snapshot();
        assertEquals(EXPECTED_ONTOLOGY_VERSION, ontology.ontologyVersion());
        // 反空转：读数必须等于实测基线，否则"加载成功"可能什么都没解析出来
        assertEquals(32, ontology.classCount(), "expected measured baseline 32 classes");
        assertEquals(34, ontology.objectPropertyCount(), "expected measured baseline 34 object properties");
        assertEquals(1, ontology.datatypePropertyCount());
        assertEquals(0, ontology.individualCount(), "A-Box 个体为 0：实体/关系查询只能到 T-Box（见非声明）");

        // ── ③ 地图按结果定向激活资产 + ⑤ 计划字段 ────────────────────────────────
        PlanDecision planDecision = planner.plan(new ActivationPlanRequest(
                TASK_TYPE, CUSTOMER_ID, "RELATIONSHIP_MANAGER", "PD-E2E-ALLOW", AS_OF, null));
        ActivationPlan plan = planDecision.planOpt()
                .orElseThrow(() -> new AssertionError("expected allow, got=" + planDecision));
        assertEquals(route.mode(), plan.routeMode(), "计划的主路径必须等于路由裁决");
        assertEquals(ontology.ontologyVersion(), plan.versions().ontology(), "计划本体版本必须来自真实加载");
        assertFalse(plan.selectedAssets().isEmpty(), "地图定向激活资产不得为空");
        assertFalse(plan.skills().isEmpty(), "激活合同声明的技能不得为空");
        assertFalse(plan.trace().planHash().isBlank());
        assertFalse(plan.trace().ontologyEvidence().isBlank(), "trace 必须带本体依据");

        // ── ④ SKILL 调用（真实端口调用）───────────────────────────────────────────
        BusinessMetrics metrics = new BusinessMetrics(new SimpleMeterRegistry());
        SkillExecutionPort skillPort = new FallbackSkillExecutionAdapter(
                new MockLlmClient(metrics), "GK17 V1 链路驱动");
        KnowledgeDrivenPrevisitReportGenerator reportGenerator =
                new KnowledgeDrivenPrevisitReportGenerator(skillPort);
        KnowledgeDrivenPrevisitReportGenerator.GenerationResult skillRun =
                reportGenerator.generate(CUSTOMER_ID, "客户准入条件与产品条款复核");

        // 防误判对照：previsit 技能在 NO_LOCAL_FILL 名单内 ⇒ 策略性 fail-closed（不补数）。
        // 必须能与"端口坏掉"区分开 —— 对策略外技能，回落应当成功。
        SkillExecutionResult portControl = skillPort.execute(new SkillExecutionCommand(
                "gk17-v1-port-probe", "REQ-GK17-V1-PROBE", CUSTOMER_ID, Map.of("probe", true)));
        assertTrue(portControl.isOk(),
                "SKILL 端口机制必须可用（策略外技能应回落成功），否则无法区分策略拒绝与端口故障");

        // ── 证据制品 ────────────────────────────────────────────────────────────
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new com.fasterxml.jackson.datatype.jsr310.JavaTimeModule());
        mapper.enable(SerializationFeature.INDENT_OUTPUT);
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

        ObjectNode root = mapper.createObjectNode();
        root.put("round", "GK17-W6-V1");
        root.put("loop", "GK17-ontology-unified-map");
        root.put("wave", "W6");
        root.put("judgement", "V1");
        root.put("generatedAt", Instant.now().toString());
        root.put("taskType", TASK_TYPE);
        root.put("customerId", CUSTOMER_ID);
        root.put("executionMode", "SHADOW");
        root.put("ontologyFileSha256", sha256Hex(Files.readAllBytes(ontologyPath)));

        ObjectNode step1 = root.putObject("step1_routeDecision");
        step1.put("policyId", route.policyId());
        step1.put("policyVersion", route.policyVersion());
        step1.put("mode", route.mode());
        step1.put("activationContractRef", route.activationContractRef());
        step1.put("priority", route.priority());
        step1.put("reason", route.reason());

        ObjectNode step2 = root.putObject("step2_ontology");
        step2.put("loaded", ontologyResult.isLoaded());
        step2.put("ontologyVersion", ontology.ontologyVersion());
        step2.put("sourceRef", ontology.sourceRef());
        step2.put("classCount", ontology.classCount());
        step2.put("objectPropertyCount", ontology.objectPropertyCount());
        step2.put("datatypePropertyCount", ontology.datatypePropertyCount());
        step2.put("individualCount", ontology.individualCount());
        step2.put("evidence", ontology.evidence());
        step2.put("aboxNote", "individuals=0：A-Box 个体在 W3 投影/W4，实体级查询当前不可用（不得读作已查）");

        ObjectNode step3 = root.putObject("step3_mapDirectedActivation");
        ArrayNode selected = step3.putArray("selectedAssets");
        for (ActivationPlan.SelectedAsset asset : plan.selectedAssets()) {
            ObjectNode node = selected.addObject();
            node.put("assetId", asset.assetId());
            node.put("version", asset.version());
            node.put("required", asset.required());
            node.put("sequence", asset.sequence());
        }
        step3.set("semanticQueries", mapper.valueToTree(plan.semanticQueries()));
        step3.set("ruleChecks", mapper.valueToTree(plan.ruleChecks()));
        step3.set("skills", mapper.valueToTree(plan.skills()));

        ObjectNode step4 = root.putObject("step4_skillInvocation");
        step4.put("skillId", "skill-customer-previsit-report");
        step4.put("invoked", true);
        step4.put("mode", "fallback(MockLlmClient) —— 非真实 dsh/KERT 平台");
        step4.put("policyNoLocalFill", true);
        step4.put("note", "previsit 技能在 NO_LOCAL_FILL 名单内 ⇒ 策略性 fail-closed（KERT_REQUIRED），不补数");
        ArrayNode trace = step4.putArray("trace");
        for (SkillExecutionResult.TraceStep step : skillRun.assemblyTrace()) {
            ObjectNode node = trace.addObject();
            node.put("phase", step.phase());
            node.put("status", step.status());
            node.put("kiId", step.kiId());
            node.put("message", step.message());
        }
        ObjectNode control = root.putObject("step4b_skillPortControl");
        control.put("skillId", "gk17-v1-port-probe");
        control.put("isOk", portControl.isOk());
        control.put("status", String.valueOf(portControl.status()));
        control.put("purpose", "证明端口机制可用 ⇒ previsit 的失败是策略拒绝，不是端口故障");

        ObjectNode step5 = root.putObject("step5_plan");
        step5.put("planId", plan.planId());
        step5.put("taskId", plan.taskId());
        step5.put("routeMode", plan.routeMode());
        step5.put("planHash", plan.trace().planHash());
        step5.put("plannerVersion", plan.trace().plannerVersion());
        step5.put("ontologyEvidence", plan.trace().ontologyEvidence());
        ObjectNode versions = step5.putObject("versions");
        versions.put("knowledgeMap", plan.versions().knowledgeMap());
        versions.put("routePolicy", plan.versions().routePolicy());
        versions.put("activationContract", plan.versions().activationContract());
        versions.put("ontology", plan.versions().ontology());

        ArrayNode coverageGaps = root.putArray("v1CoverageGaps");
        coverageGaps.add("② 本体查实体/关系：本链路只到『真实加载 T-Box + 计划声明 5 条语义查询 / 4 条规则检查』。"
                + "查询执行器 SemanticQueryPort 在 apps/api **未装配**（实测 grep apps/api/src/main 无命中），"
                + "且本体 individuals=0（A-Box 在 W3 投影/W4）⇒ **实体级查询未执行**。"
                + "是否影响 V1 通过须由 ACCEPT 裁定。");
        coverageGaps.add("④ SKILL 调用为**策略性 fail-closed**（skill-customer-previsit-report 在 NO_LOCAL_FILL 名单内）："
                + "调用真实发生且有轨迹，但**无业务产物**（真实 dsh/KERT 平台未接通）。");

        ArrayNode nonClaims = root.putArray("nonClaims");
        nonClaims.add("SKILL 侧为 fail-closed 调用：有轨迹、无业务产物（真实平台未接通）");
        nonClaims.add("A-Box 实体/关系查询不可用（individuals=0，属 WP3.2/W4）");
        nonClaims.add("本条不是 QA_PASS，不代表 PRODUCTION_READY");

        String json = mapper.writeValueAsString(root);

        String evidenceDir = System.getProperty("gk17.evidence.dir");
        Path outPath = evidenceDir == null
                ? Path.of("target", "gk17-v1-previsit-chain.json")
                : repoRoot.resolve(evidenceDir).resolve("gk17-v1-previsit-chain.json");
        if (outPath.getParent() != null) {
            Files.createDirectories(outPath.getParent());
        }
        Files.writeString(outPath, json, StandardCharsets.UTF_8);
        assertTrue(Files.size(outPath) > 0, "evidence artifact must be non-empty");

        System.out.println("===== GK17 W6 V1 raw output (" + outPath.toAbsolutePath() + ") =====");
        System.out.println(json);
        System.out.println("===== end GK17 W6 V1 raw output =====");

        // 制品自证：写出的 JSON 必须真的含判据点名的三个字段
        String written = Files.readString(outPath, StandardCharsets.UTF_8);
        assertTrue(written.contains(plan.trace().planHash()), "raw output must contain planHash");
        assertTrue(written.contains(ontology.ontologyVersion()), "raw output must contain versions.ontology");
        assertTrue(written.contains(route.reason()), "raw output must contain the routing reason");
    }

    private static String sha256Hex(byte[] bytes) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder sb = new StringBuilder(digest.length * 2);
        for (byte b : digest) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
