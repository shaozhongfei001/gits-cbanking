package com.gien.gits.api.e2e;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
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
import com.gien.gits.knowledge.ActivationPlan;
import com.gien.gits.knowledge.plan.ActivationPlanRequest;
import com.gien.gits.knowledge.plan.DefaultActivationPlanner;
import com.gien.gits.knowledge.plan.PlanDecision;
import com.gien.gits.knowledge.port.ActivationContractPort;
import com.gien.gits.knowledge.port.AssetCatalogPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import com.gien.gits.knowledge.port.RoutePolicyEvaluatorPort;
import com.gien.gits.knowledge.port.RoutePolicyPort;
import com.gien.gits.knowledge.route.DefaultRoutePolicyEvaluator;
import com.gien.gits.semantic.OntologyPort;
import com.gien.gits.semantic.OntologyPort.OntologyLoadResult;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * GK17 / W6 · WP6.2 —— 判据 **V2**（反例 1）：**只改本体、不动地图 ⇒ 计划必须变化**。
 *
 * <p>判据原文：*"只改本体（如给客户加一条互斥关系），不动地图 ⇒ 计划**必须变化**。
 * 若不变 ⇒ 本体未被消费 ⇒ A 不成立且 C 未落地。"*</p>
 *
 * <p><b>本类同时是"非空转"证明</b>：
 * <ul>
 *   <li><b>前提可核</b>：以 {@code specs/knowledge-architecture/maps/**} 全部文件的 sha256 指纹，
 *       证明"地图真的没动"；</li>
 *   <li><b>变异可核</b>：本体副本内容 sha256 必须变化（否则"计划变了"另有原因）；</li>
 *   <li><b>可重放</b>：恢复副本后计划必须回到基线；</li>
 *   <li><b>判据本身的变异对照</b>：另有**源码级**变异（从 {@code deterministicContent} 移除本体版本），
 *       施加后本类必须 **FAIL** —— 见 {@code evidence/} 中的变异日志。</li>
 * </ul>
 *
 * <p><b>⚠ V2 语义强度声明（必须随证据一并读）</b>：本类断言的"计划变化"体现为
 * {@code trace.planHash} 与 {@code versions.ontology}。本体内容的**语义**（如互斥关系本身）
 * **当前未参与**资产 / 规则 / 技能的选择 —— 主用例末尾有**绊线断言**把这一点钉住
 * （注释标注"语义强度绊线"；将来本体内容真的参与选择时它会失败，从而强制更新本声明）。
 * 若 ACCEPT 要求"互斥关系必须改变被测资产集或规则集"，则 V2 **未达标**，须由 ACCEPT 裁定。</p>
 */
class V2OntologyOnlyChangeTest {

    private static final String TASK_TYPE = "PRE_VISIT_PREPARATION";
    private static final String CUSTOMER_ID = "CUST-V2-0001";
    private static final Instant AS_OF = Instant.parse("2026-09-15T00:00:00Z");

    private static Path repoRoot;
    private static Path knowledgeArchitecture;
    private static Path canonicalOntology;
    private static Path mapsDir;

    @BeforeAll
    static void locate() {
        Path probe = Path.of(".").toAbsolutePath().normalize();
        while (probe != null && !probe.resolve("specs/semantic/gits-core.owl.ttl").toFile().isFile()) {
            probe = probe.getParent();
        }
        assertTrue(probe != null, "must locate repo root");
        repoRoot = probe;
        knowledgeArchitecture = repoRoot.resolve("specs/knowledge-architecture");
        canonicalOntology = repoRoot.resolve("specs/semantic/gits-core.owl.ttl");
        mapsDir = knowledgeArchitecture.resolve("maps");
    }

    @Test
    void changingOntologyOnlyChangesThePlanWhileTheMapStaysUntouched(@TempDir Path tempDir) throws Exception {
        String mapFingerprintBefore = mapFingerprint();
        assertTrue(!mapFingerprintBefore.isBlank(), "map fingerprint must not be blank");

        Path copy = tempDir.resolve("gits-core.owl.ttl");
        Files.copy(canonicalOntology, copy, StandardCopyOption.REPLACE_EXISTING);

        Variant baseline = runVariant(copy);
        String copyShaBefore = sha256Hex(Files.readAllBytes(copy));
        assertEquals(sha256Hex(Files.readAllBytes(canonicalOntology)), copyShaBefore,
                "临时副本必须与权威源逐字节一致");

        // 变异 A（合法 T-Box 改动）：新增一个类声明
        Files.writeString(copy, Files.readString(copy) + "\ngits:gk17V2ProbeClass a owl:Class .\n");
        Variant addedClass = runVariant(copy);
        assertNotEquals(copyShaBefore, sha256Hex(Files.readAllBytes(copy)), "本体副本内容必须真的变了");

        // 变异 B（判据字面例）：给客户加一条互斥关系
        Files.copy(canonicalOntology, copy, StandardCopyOption.REPLACE_EXISTING);
        Files.writeString(copy, Files.readString(copy)
                + "\ngits:gk17V2CustProbe gits:mutuallyExclusiveWith gits:prod_set_001 .\n");
        Variant addedExclusion = runVariant(copy);

        // 恢复
        Files.copy(canonicalOntology, copy, StandardCopyOption.REPLACE_EXISTING);
        Variant restored = runVariant(copy);

        // ── 前提：地图全程未动 ────────────────────────────────────────────────
        assertEquals(mapFingerprintBefore, mapFingerprint(),
                "本反例的前提是『不动地图』—— 地图指纹变了则本用例不成立");

        // ── 判据：计划必须变化（两种变异各自独立成立）──────────────────────────
        assertNotEquals(baseline.planHash, addedClass.planHash,
                "只改本体（新增类）而计划未变 ⇒ 本体未被消费 ⇒ V2 不成立");
        assertNotEquals(baseline.ontologyVersion, addedClass.ontologyVersion);
        assertNotEquals(baseline.planHash, addedExclusion.planHash,
                "只改本体（加互斥关系）而计划未变 ⇒ 本体未被消费 ⇒ V2 不成立");
        assertNotEquals(baseline.ontologyVersion, addedExclusion.ontologyVersion);

        // ── 可重放：恢复后必须回到基线 ────────────────────────────────────────
        assertEquals(baseline.ontologyVersion, restored.ontologyVersion, "恢复本体后版本必须回到基线");
        assertEquals(baseline.planHash, restored.planHash, "恢复本体后计划必须回到基线（可重放）");

        // ── 语义强度绊线（不是"通过"，是**显式限制**）────────────────────────
        // 本体内容目前**不驱动**资产/规则/技能选择：只经版本号影响计划。
        // 一旦将来本体内容真的参与选择，这条断言会失败 ⇒ 强制更新此声明，避免声明腐化。
        assertEquals(baseline.selectedAssets, addedExclusion.selectedAssets,
                "绊线：本体内容未驱动资产选择（V2 语义强度声明，见类注释）");
        assertEquals(baseline.ruleChecks, addedExclusion.ruleChecks,
                "绊线：本体内容未驱动规则检查选择");
        assertEquals(baseline.skills, addedExclusion.skills,
                "绊线：本体内容未驱动技能选择");

        writeEvidence(baseline, addedClass, addedExclusion, restored, mapFingerprintBefore);
    }

    // ── 驱动 ────────────────────────────────────────────────────────────────

    private record Variant(
            String label,
            String ontologyVersion,
            String planHash,
            String ontologyEvidence,
            int classCount,
            int individualCount,
            String planVersionsOntology,
            List<String> selectedAssets,
            List<String> ruleChecks,
            List<String> skills) {}

    private static Variant runVariant(Path ontologyCopy) {
        Supplier<Instant> clock = () -> AS_OF;
        RoutePolicyPort routePolicyPort = new FilesystemRoutePolicyReader(knowledgeArchitecture.resolve("routes"));
        RoutePolicyEvaluatorPort evaluator = new DefaultRoutePolicyEvaluator(routePolicyPort, "RP-CORP-RM-001");
        ActivationContractPort contracts = new FilesystemActivationContractReader(knowledgeArchitecture.resolve("activations"));
        AssetCatalogPort assets = new FilesystemAssetCatalogReader(knowledgeArchitecture.resolve("assets"));
        KnowledgeMapPort maps = new FilesystemKnowledgeMapReader(mapsDir);
        OntologyPort ontologyPort = new JenaOntologyAdapter(ontologyCopy, "CTR-SEM-002");
        DefaultActivationPlanner planner =
                new DefaultActivationPlanner(evaluator, contracts, assets, maps, ontologyPort, clock);

        OntologyLoadResult loaded = ontologyPort.load();
        assertTrue(loaded.isLoaded(), () -> "ontology must load: " + loaded.failureReason());

        PlanDecision decision = planner.plan(new ActivationPlanRequest(
                TASK_TYPE, CUSTOMER_ID, "RELATIONSHIP_MANAGER", "PD-V2-ALLOW", AS_OF, null));
        ActivationPlan plan = decision.planOpt()
                .orElseThrow(() -> new AssertionError("expected allow, got=" + decision));

        List<String> selected = new ArrayList<>();
        for (ActivationPlan.SelectedAsset asset : plan.selectedAssets()) {
            selected.add(asset.assetId() + "@" + asset.version() + (asset.required() ? "!" : ""));
        }
        return new Variant(
                ontologyCopy.getFileName().toString(),
                loaded.snapshot().ontologyVersion(),
                plan.trace().planHash(),
                plan.trace().ontologyEvidence(),
                loaded.snapshot().classCount(),
                loaded.snapshot().individualCount(),
                plan.versions().ontology(),
                selected,
                new ArrayList<>(plan.ruleChecks()),
                new ArrayList<>(plan.skills()));
    }

    /** 地图目录全部文件的确定性指纹（相对路径 + 内容 sha256，按路径排序）。 */
    private static String mapFingerprint() throws Exception {
        List<Path> files = new ArrayList<>();
        try (Stream<Path> walk = Files.walk(mapsDir)) {
            walk.filter(Files::isRegularFile).forEach(files::add);
        }
        files.sort((a, b) -> mapsDir.relativize(a).toString().compareTo(mapsDir.relativize(b).toString()));
        StringBuilder sb = new StringBuilder();
        for (Path file : files) {
            sb.append(mapsDir.relativize(file)).append('=')
              .append(sha256Hex(Files.readAllBytes(file))).append('\n');
        }
        return sb.toString();
    }

    private static void writeEvidence(
            Variant baseline, Variant addedClass, Variant addedExclusion, Variant restored,
            String mapFingerprint) throws IOException {
        ObjectMapper mapper = new ObjectMapper();
        mapper.enable(SerializationFeature.INDENT_OUTPUT);
        ObjectNode root = mapper.createObjectNode();
        root.put("round", "GK17-W6-V2");
        root.put("judgement", "V2");
        root.put("statement", "只改本体、不动地图 ⇒ 计划必须变化");
        root.put("generatedAt", Instant.now().toString());
        root.put("mapFingerprintSha256", sha256Hex(mapFingerprint.getBytes(StandardCharsets.UTF_8)));
        root.put("mapFingerprintUnchanged", true);
        root.put("mapFiles", mapFingerprint);

        ArrayNode variants = root.putArray("variants");
        for (Variant variant : List.of(baseline, addedClass, addedExclusion, restored)) {
            ObjectNode node = variants.addObject();
            node.put("label", variant.label());
            node.put("ontologyVersion", variant.ontologyVersion());
            node.put("planVersionsOntology", variant.planVersionsOntology());
            node.put("planHash", variant.planHash());
            node.put("classCount", variant.classCount());
            node.put("individualCount", variant.individualCount());
            node.set("selectedAssets", mapper.valueToTree(variant.selectedAssets()));
            node.set("ruleChecks", mapper.valueToTree(variant.ruleChecks()));
            node.set("skills", mapper.valueToTree(variant.skills()));
        }

        ArrayNode statements = root.putArray("claims");
        statements.add("变异A（新增类）与变异B（加互斥关系）各自使 planHash 与 versions.ontology 变化 ⇒ 判据 V2 的『计划必须变化』成立");
        statements.add("地图指纹全程未变 ⇒ 满足『不动地图』前提");
        statements.add("恢复本体 ⇒ planHash 与版本回到基线 ⇒ 可重放");

        ArrayNode limits = root.putArray("limitations");
        limits.add("语义强度：本体内容的语义（如互斥关系）当前未驱动资产/规则/技能选择，"
                + "只经版本号影响计划；若 ACCEPT 要求语义驱动，则 V2 未达标（绊线断言已钉住）");
        limits.add("变异B 的关系实例形态若落在权威源上，会被 V4/D1 判为『本体承载关系实例』越权写 —— "
                + "本用例用临时副本，不触碰权威源");

        String dir = System.getProperty("gk17.evidence.dir");
        Path out = dir == null
                ? Path.of("target", "gk17-v2-ontology-only-change.json")
                : repoRoot.resolve(dir).resolve("gk17-v2-ontology-only-change.json");
        if (out.getParent() != null) {
            Files.createDirectories(out.getParent());
        }
        String json = mapper.writeValueAsString(root);
        Files.writeString(out, json, StandardCharsets.UTF_8);
        System.out.println("===== GK17 W6 V2 raw output (" + out.toAbsolutePath() + ") =====");
        System.out.println(json);
        System.out.println("===== end GK17 W6 V2 raw output =====");
    }

    private static String sha256Hex(byte[] bytes) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
            StringBuilder sb = new StringBuilder(digest.length * 2);
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (java.security.NoSuchAlgorithmException ex) {
            throw new IllegalStateException("SHA-256 must be available", ex);
        }
    }
}
