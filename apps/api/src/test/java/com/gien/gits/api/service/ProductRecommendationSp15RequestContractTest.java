package com.gien.gits.api.service;

import static org.assertj.core.api.Assertions.assertThat;

import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationAttempt;
import com.gien.gits.customerjourney.recommendation.RecommendationFeedback;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;
import com.gien.gits.customerjourney.recommendation.port.ProductRecommendationRepository;
import com.gien.gits.customerjourney.recommendation.port.RecommendationAuthorizationPort;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;

import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * SP-15 调用接线请求契约测试（WP6-4，CANDIDATE）。
 *
 * <p>对齐契约 {@code Leibniz-KERT docs/skill-execute-api-contract-vNext.md} §3（SP-15 执行契约）：</p>
 * <ul>
 *   <li>{@link ProductRecommendationApplicationService} 对 KERT 的 Skill 调用 skillId = {@code SP-15}
 *       （顶层 SkillExecuteRequest.skillId 固定 SP-15，而非 GITS 侧路由 id）；</li>
 *   <li>{@code request.context} 必填字段齐备（含 3 个快照引用 + permissionDecisionId + activationContract）；</li>
 *   <li>业务幂等键随上下文透传；</li>
 *   <li>缺快照引用时按契约显式缺省为空串，并在 {@code request.defaultedContextRefs} 标注；</li>
 *   <li>DKWS 不可达（fake 抛 {@link SkillExecutionException}）→ run = FAILED_CLOSED，且无本地推荐回退（不产生方案版本）。</li>
 * </ul>
 *
 * <p>用 fake {@link SkillExecutionPort} 捕获调用载荷（不启动 Spring 上下文、不经 HTTP 适配器）。</p>
 *
 * <pre>{@code
 * DOC_STATUS=CANDIDATE
 * FROZEN=NO
 * IMPLEMENTED=NO
 * REAL_E2E_PASS=NO
 * }</pre>
 */
class ProductRecommendationSp15RequestContractTest {

    private static final Instant AS_OF = Instant.parse("2026-08-31T09:00:00Z");
    private static final String AS_OF_STRING = "2026-08-31T09:00:00Z";

    /** 9 参兼容构造（快照引用尚未接线）。 */
    private static ProductRecommendationApplicationService.CreateRunCommand command(String idempotencyKey) {
        return new ProductRecommendationApplicationService.CreateRunCommand(
                "CALLER-1", "CUST-1", "JNY-1", null, List.of("NEEDV-1"),
                "补充流动资金与跨境结算方案", List.of("FINANCING", "SETTLEMENT"),
                AS_OF, idempotencyKey);
    }

    /** 14 参构造（快照引用 / 权限决策 / 激活合同齐备）。 */
    private static ProductRecommendationApplicationService.CreateRunCommand fullCommand(String idempotencyKey) {
        return new ProductRecommendationApplicationService.CreateRunCommand(
                "CALLER-1", "CUST-1", "JNY-1", null, List.of("NEEDV-1"),
                "补充流动资金与跨境结算方案", List.of("FINANCING", "SETTLEMENT"),
                AS_OF, idempotencyKey,
                "CFS-1", "PKS-1", "RB-1", "PERM-1", "AC-PRODUCT-RECOMMEND-001");
    }

    private static SkillExecutionResult okResult() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("contentHash", "sha256:abc");
        data.put("evidenceBundleId", "EVB-1");
        data.put("traceId", "TRACE-1");
        data.put("productKnowledgeSnapshotRef", "PKS-1");
        data.put("ruleExecutionRef", "RULE-1");
        return new SkillExecutionResult(SkillExecutionStatus.OK, "REQ-1", data,
                List.of(), List.of(), List.of());
    }

    @Test
    void createRunUsesSp15SkillIdAndFullContextContract() {
        FakeRepository repo = new FakeRepository();
        CapturingSkillExecutionPort port = new CapturingSkillExecutionPort();
        ProductRecommendationApplicationService service =
                new ProductRecommendationApplicationService(repo, port, allowAll());

        service.createRun(command("IDEM-1"));

        assertThat(port.commands()).hasSize(1);
        SkillExecutionCommand cmd = port.commands().get(0);

        // 契约 vNext §3：顶层 skillId 固定 SP-15
        assertThat(cmd.skillId()).isEqualTo("SP-15");
        assertThat(cmd.skillId()).isEqualTo(ProductRecommendationApplicationService.KERT_SKILL_ID);

        Map<String, Object> request = cmd.request();
        assertThat(request).containsKey("context");
        // 契约 vNext §3.1：request 不应内嵌 skillId（skillId 由顶层 SkillExecutionCommand 承载）
        assertThat(request).doesNotContainKey("skillId");

        @SuppressWarnings("unchecked")
        Map<String, Object> context = (Map<String, Object>) request.get("context");
        // 契约 vNext §3.1 必填字段齐备
        assertThat(context).containsKeys(
                "schemaVersion", "customerId", "needVersionIds", "recommendationObjective",
                "requestedProductDomains", "asOf", "customerFactSnapshotId",
                "productKnowledgeSnapshotRef", "ruleBundleRef", "permissionDecisionId",
                "activationContract");
        assertThat(context.get("schemaVersion")).isEqualTo("1.0.0");
        assertThat(context.get("customerId")).isEqualTo("CUST-1");
        assertThat(context.get("needVersionIds")).isEqualTo(List.of("NEEDV-1"));
        assertThat(context.get("recommendationObjective")).isEqualTo("补充流动资金与跨境结算方案");
        assertThat(context.get("requestedProductDomains")).isEqualTo(List.of("FINANCING", "SETTLEMENT"));
        assertThat(context.get("asOf")).isEqualTo(AS_OF_STRING);
    }

    @Test
    void createRunPassesIdempotencyKeyThrough() {
        FakeRepository repo = new FakeRepository();
        CapturingSkillExecutionPort port = new CapturingSkillExecutionPort();
        ProductRecommendationApplicationService service =
                new ProductRecommendationApplicationService(repo, port, allowAll());

        service.createRun(command("IDEM-PASS-THROUGH"));

        SkillExecutionCommand cmd = port.commands().get(0);
        @SuppressWarnings("unchecked")
        Map<String, Object> context = (Map<String, Object>) cmd.request().get("context");
        assertThat(context.get("idempotencyKey")).isEqualTo("IDEM-PASS-THROUGH");
        // wire 层幂等键（requestId）非空
        assertThat(cmd.requestId()).isNotBlank();
    }

    @Test
    void missingSnapshotRefsDefaultedExplicitlyAndAnnotated() {
        FakeRepository repo = new FakeRepository();
        CapturingSkillExecutionPort port = new CapturingSkillExecutionPort();
        ProductRecommendationApplicationService service =
                new ProductRecommendationApplicationService(repo, port, allowAll());

        service.createRun(command("IDEM-2"));

        SkillExecutionCommand cmd = port.commands().get(0);
        Map<String, Object> request = cmd.request();
        @SuppressWarnings("unchecked")
        Map<String, Object> context = (Map<String, Object>) request.get("context");

        // OQ-02：缺失引用 → 回退确定性演示值（C2 降级 shell），并保留 defaultedContextRefs 标注
        assertThat(context.get("customerFactSnapshotId")).isEqualTo("CFS-CUST-1");
        assertThat(context.get("productKnowledgeSnapshotRef")).isEqualTo("PKS-CUST-1");
        assertThat(context.get("ruleBundleRef")).isEqualTo("RB-PR-20260831-0001");
        assertThat(context.get("permissionDecisionId")).isEqualTo("PERM-CUST-1");
        // activationContract 固定值
        assertThat(context.get("activationContract"))
                .isEqualTo(ProductRecommendationApplicationService.ACTIVATION_CONTRACT_PRODUCT_RECOMMEND);

        // 缺省引用在 request 中标注
        @SuppressWarnings("unchecked")
        List<String> defaultedRefs =
                (List<String>) request.get(ProductRecommendationApplicationService.DEFAULTED_CONTEXT_REFS_KEY);
        assertThat(defaultedRefs).containsExactlyInAnyOrder(
                "customerFactSnapshotId", "productKnowledgeSnapshotRef",
                "ruleBundleRef", "permissionDecisionId");
    }

    @Test
    void providedSnapshotRefsArePassedThroughWithoutDefaultAnnotation() {
        FakeRepository repo = new FakeRepository();
        CapturingSkillExecutionPort port = new CapturingSkillExecutionPort();
        ProductRecommendationApplicationService service =
                new ProductRecommendationApplicationService(repo, port, allowAll());

        service.createRun(fullCommand("IDEM-3"));

        SkillExecutionCommand cmd = port.commands().get(0);
        Map<String, Object> request = cmd.request();
        @SuppressWarnings("unchecked")
        Map<String, Object> context = (Map<String, Object>) request.get("context");

        assertThat(context.get("customerFactSnapshotId")).isEqualTo("CFS-1");
        assertThat(context.get("productKnowledgeSnapshotRef")).isEqualTo("PKS-1");
        assertThat(context.get("ruleBundleRef")).isEqualTo("RB-1");
        assertThat(context.get("permissionDecisionId")).isEqualTo("PERM-1");
        assertThat(context.get("activationContract")).isEqualTo("AC-PRODUCT-RECOMMEND-001");
        // 全部引用齐备 → 不产生缺省标注
        assertThat(request).doesNotContainKey(ProductRecommendationApplicationService.DEFAULTED_CONTEXT_REFS_KEY);
    }

    @Test
    void createRunKertUnreachableFailsClosedNoLocalFallback() {
        FakeRepository repo = new FakeRepository();
        CapturingSkillExecutionPort port = new CapturingSkillExecutionPort();
        port.failWith(new SkillExecutionException("dsh down"));
        ProductRecommendationApplicationService service =
                new ProductRecommendationApplicationService(repo, port, allowAll());

        ProductRecommendationRun run = service.createRun(command("IDEM-4"));

        // INV-07：KERT 不可达 → fail-closed，禁止本地推荐回退
        assertThat(run.status()).isEqualTo(ProductRecommendationRunStatus.FAILED_CLOSED);
        assertThat(port.commands()).hasSize(1);
        // 无本地推荐回退：不产生任何方案版本（推荐未产出）
        assertThat(repo.findVersionsByRun(run.runId())).isEmpty();
        List<RecommendationAttempt> attempts = repo.findAttemptsByRun(run.runId());
        assertThat(attempts).hasSize(1);
        assertThat(attempts.get(0).errorCode()).isEqualTo("KERT_INTERNAL_ERROR");
    }

    private static RecommendationAuthorizationPort allowAll() {
        return (actorId, actorRole, gateId) -> true;
    }

    /** 捕获调用载荷的 fake SkillExecutionPort。 */
    private static final class CapturingSkillExecutionPort implements SkillExecutionPort {
        private final List<SkillExecutionCommand> commands = new ArrayList<>();
        private SkillExecutionException failure;

        void failWith(SkillExecutionException ex) {
            this.failure = ex;
        }

        List<SkillExecutionCommand> commands() {
            return commands;
        }

        @Override
        public SkillExecutionResult execute(SkillExecutionCommand command) {
            commands.add(command);
            if (failure != null) {
                throw failure;
            }
            return okResult();
        }
    }

    /** 内存版仓储（仅测试用）。 */
    private static final class FakeRepository implements ProductRecommendationRepository {
        private final Map<String, ProductRecommendationRun> runs = new HashMap<>();
        private final Map<String, String> runByKey = new HashMap<>();
        private final Map<String, RecommendationProposalVersion> versions = new HashMap<>();
        private final Map<String, List<RecommendationAttempt>> attempts = new HashMap<>();
        private final Map<String, RecommendationHumanDecision> decisions = new HashMap<>();
        private final Map<String, List<RecommendationFeedback>> feedback = new HashMap<>();

        @Override
        public void saveRun(ProductRecommendationRun run) {
            runs.put(run.runId(), run);
            runByKey.put(run.idempotencyKey(), run.runId());
        }

        @Override
        public void updateRun(ProductRecommendationRun run) {
            runs.put(run.runId(), run);
            runByKey.put(run.idempotencyKey(), run.runId());
        }

        @Override
        public Optional<ProductRecommendationRun> findRunById(String runId) {
            return Optional.ofNullable(runs.get(runId));
        }

        @Override
        public Optional<ProductRecommendationRun> findRunByIdempotencyKey(String idempotencyKey) {
            String runId = runByKey.get(idempotencyKey);
            return runId == null ? Optional.empty() : Optional.ofNullable(runs.get(runId));
        }

        @Override
        public void saveAttempt(RecommendationAttempt attempt) {
            attempts.computeIfAbsent(attempt.runId(), k -> new ArrayList<>()).add(attempt);
        }

        @Override
        public List<RecommendationAttempt> findAttemptsByRun(String runId) {
            return attempts.getOrDefault(runId, List.of());
        }

        @Override
        public void saveVersion(RecommendationProposalVersion version) {
            versions.put(version.versionId(), version);
        }

        @Override
        public Optional<RecommendationProposalVersion> findVersionById(String versionId) {
            return Optional.ofNullable(versions.get(versionId));
        }

        @Override
        public List<RecommendationProposalVersion> findVersionsByRun(String runId) {
            return versions.values().stream().filter(v -> v.runId().equals(runId)).toList();
        }

        @Override
        public void saveDecision(RecommendationHumanDecision decision) {
            decisions.put(decision.decisionId(), decision);
        }

        @Override
        public Optional<RecommendationHumanDecision> findDecisionById(String decisionId) {
            return Optional.ofNullable(decisions.get(decisionId));
        }

        @Override
        public Optional<RecommendationHumanDecision> findDecisionByProposalVersion(String proposalVersionId) {
            return decisions.values().stream()
                    .filter(d -> d.proposalVersionId().equals(proposalVersionId)).findFirst();
        }

        @Override
        public List<RecommendationHumanDecision> findDecisionsByRun(String runId) {
            return decisions.values().stream().filter(d -> d.runId().equals(runId)).toList();
        }

        @Override
        public void saveFeedback(RecommendationFeedback f) {
            feedback.computeIfAbsent(f.runId(), k -> new ArrayList<>()).add(f);
        }

        @Override
        public List<RecommendationFeedback> findFeedbackByRun(String runId) {
            return feedback.getOrDefault(runId, List.of());
        }
    }
}
