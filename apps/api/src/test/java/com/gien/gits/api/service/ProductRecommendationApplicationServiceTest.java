package com.gien.gits.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.RecommendationAttempt;
import com.gien.gits.customerjourney.recommendation.RecommendationDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationFeedback;
import com.gien.gits.customerjourney.recommendation.RecommendationGatePreconditionException;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationVersionConflictException;
import com.gien.gits.customerjourney.recommendation.port.ProductRecommendationRepository;
import com.gien.gits.customerjourney.recommendation.port.RecommendationAuthorizationPort;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DuplicateKeyException;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * 产品推荐应用服务单元测试（WP4-2，CANDIDATE）。
 *
 * <p>覆盖：幂等同键两次→同 run 不重复执行、过期版本拒绝（语义等价 409）、
 * 状态推进（经领域对象）、KERT fail-closed / HELD 映射、权限与证据前置校验。</p>
 */
class ProductRecommendationApplicationServiceTest {

    private ProductRecommendationRepository repository;
    private SkillExecutionPort skillExecutionPort;
    private RecommendationAuthorizationPort authorizationPort;
    private ProductRecommendationApplicationService service;

    @BeforeEach
    void setUp() {
        repository = new FakeRepository();
        skillExecutionPort = mock(SkillExecutionPort.class);
        authorizationPort = (actorId, actorRole, gateId) -> true;
        service = new ProductRecommendationApplicationService(
            repository, skillExecutionPort, authorizationPort);
    }

    private static SkillExecutionResult okResult() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("schemaVersion", "1.0.0");
        data.put("productKnowledgeSnapshotRef", "PKS-1");
        data.put("ruleExecutionRef", "RULE-1");
        data.put("evidenceBundleId", "EVB-1");
        data.put("contentHash", "sha256:abc");
        data.put("traceId", "TRACE-1");
        data.put("eligibilityResults", List.of());
        data.put("fitResults", List.of());
        data.put("portfolioCandidates", List.of());
        return new SkillExecutionResult(SkillExecutionStatus.OK, "REQ-1", data,
            List.of(), List.of(), List.of());
    }

    private static ProductRecommendationApplicationService.CreateRunCommand command(String idempotencyKey) {
        return new ProductRecommendationApplicationService.CreateRunCommand(
            "CALLER-1", "CUST-1", "JNY-1", null, List.of("NEEDV-1"),
            "补充流动资金与跨境结算方案", List.of("FINANCING", "SETTLEMENT"),
            Instant.parse("2026-08-31T09:00:00Z"), idempotencyKey);
    }

    @Test
    void createRunSameIdempotencyKeyReturnsSameRunWithoutReexecution() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class))).thenReturn(okResult());

        var first = service.createRun(command("IDEM-1"));
        var second = service.createRun(command("IDEM-1"));

        assertThat(first.runId()).isEqualTo(second.runId());
        assertThat(second.status()).isEqualTo(ProductRecommendationRunStatus.AWAITING_HUMAN);
        verify(skillExecutionPort, times(1)).execute(any(SkillExecutionCommand.class));
    }

    @Test
    void createRunRealDkwsNestedResultShapeReachesAwaitingHuman() {
        // DKWS 真实响应形状：data.result = ProductRecommendationResult（8 必填 + 数组在内层）
        Map<String, Object> resultPayload = new LinkedHashMap<>();
        resultPayload.put("schemaVersion", "1.0.0");
        resultPayload.put("productKnowledgeSnapshotRef", "PKS-1");
        resultPayload.put("ruleExecutionRef", "RULE-1");
        resultPayload.put("evidenceBundleId", "EVB-1");
        resultPayload.put("contentHash", "sha256:nested");
        resultPayload.put("traceId", "TRACE-1");
        resultPayload.put("eligibilityResults",
            List.of(Map.of("productId", "PROD-1", "eligibility", "ELIGIBLE")));
        resultPayload.put("fitResults", List.of());
        resultPayload.put("portfolioCandidates", List.of());
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("skillId", "SP-15");
        data.put("result", resultPayload);
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
            .thenReturn(new SkillExecutionResult(SkillExecutionStatus.OK, "REQ-NESTED", data,
                List.of(), List.of(), List.of()));

        ProductRecommendationRun run = service.createRun(command("IDEM-NESTED"));

        assertThat(run.status()).isEqualTo(ProductRecommendationRunStatus.AWAITING_HUMAN);
        RecommendationProposalVersion saved =
            repository.findVersionById(run.currentVersionId()).orElseThrow();
        assertThat(saved.contentHash()).isEqualTo("sha256:nested");
        assertThat(saved.payload().get("eligibilityResults"))
            .isEqualTo(List.of(Map.of("productId", "PROD-1", "eligibility", "ELIGIBLE")));
    }

    @Test
    void createRunConcurrentDuplicateKeyReReadsExistingRunWithoutReexecution() {
        // 模拟并发同键：首次 findRunByIdempotencyKey 返回空（两并发请求均尚未插入），
        // saveRun 命中唯一约束 uk_prr_idem 抛 DuplicateKeyException，catch 分支回读既有 run。
        ProductRecommendationRepository concurrentRepo = mock(ProductRecommendationRepository.class);
        ProductRecommendationRun existing = new ProductRecommendationRun(
            "run-existing", "CUST-1", "JNY-1", null, List.of("NEEDV-1"), "objective",
            List.of("FINANCING"), Instant.parse("2026-08-31T09:00:00Z"), "IDEM-CONCURRENT",
            ProductRecommendationRunStatus.AWAITING_HUMAN, "V-EXISTING", "KERT-JOB-1",
            Map.of("evidenceBundleId", "EVB-1"), Instant.now(), Instant.now());

        when(concurrentRepo.findRunByIdempotencyKey("IDEM-CONCURRENT"))
            .thenReturn(Optional.empty(), Optional.of(existing));
        doThrow(new DuplicateKeyException("uk_prr_idem"))
            .when(concurrentRepo).saveRun(any(ProductRecommendationRun.class));

        ProductRecommendationApplicationService concurrentService =
            new ProductRecommendationApplicationService(
                concurrentRepo, skillExecutionPort, authorizationPort);

        ProductRecommendationRun result = concurrentService.createRun(command("IDEM-CONCURRENT"));

        assertThat(result.runId()).isEqualTo("run-existing");
        verify(concurrentRepo, times(2)).findRunByIdempotencyKey("IDEM-CONCURRENT");
        // 并发冲突不得重复执行 KERT
        verify(skillExecutionPort, never()).execute(any(SkillExecutionCommand.class));
    }

    @Test
    void stateProgressionCreateThenApprove() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class))).thenReturn(okResult());

        ProductRecommendationRun run = service.createRun(command("IDEM-2"));
        assertThat(run.status()).isEqualTo(ProductRecommendationRunStatus.AWAITING_HUMAN);
        assertThat(run.currentVersionId()).isNotBlank();

        RecommendationHumanDecision decision = service.decide(
            new ProductRecommendationApplicationService.DecideCommand(
                run.runId(), ProductRecommendationApplicationService.HG_D01,
                run.currentVersionId(), run.currentVersionId(),
                RecommendationDecision.APPROVE, List.of(), "同意采纳",
                "RM-1", "RELATIONSHIP_MANAGER"));

        assertThat(decision.decision()).isEqualTo(RecommendationDecision.APPROVE);
        assertThat(repository.findRunById(run.runId())).isPresent();
        assertThat(repository.findRunById(run.runId()).get().status())
            .isEqualTo(ProductRecommendationRunStatus.APPROVED);
    }

    @Test
    void decideWithStaleProposalVersionRejectsAsConflict() {
        seedAwaitingHumanRun("run-stale", "V1");

        assertThatThrownBy(() -> service.decide(
            new ProductRecommendationApplicationService.DecideCommand(
                "run-stale", ProductRecommendationApplicationService.HG_D01,
                "V2", "V2", RecommendationDecision.APPROVE, List.of(), "ok",
                "RM-1", "RELATIONSHIP_MANAGER")))
            .isInstanceOf(RecommendationVersionConflictException.class);

        // 过期版本不得落决定
        assertThat(repository.findDecisionsByRun("run-stale")).isEmpty();
        assertThat(repository.findRunById("run-stale").get().status())
            .isEqualTo(ProductRecommendationRunStatus.AWAITING_HUMAN);
    }

    @Test
    void decideWithStaleIfMatchEtagRejectsAsConflict() {
        seedAwaitingHumanRun("run-etag", "V1");

        assertThatThrownBy(() -> service.decide(
            new ProductRecommendationApplicationService.DecideCommand(
                "run-etag", ProductRecommendationApplicationService.HG_D01,
                "V1", "V0", RecommendationDecision.APPROVE, List.of(), "ok",
                "RM-1", "RELATIONSHIP_MANAGER")))
            .isInstanceOf(RecommendationVersionConflictException.class);
    }

    @Test
    void createRunKertUnreachableFailsClosed() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
            .thenThrow(new SkillExecutionException("dsh down"));

        ProductRecommendationRun run = service.createRun(command("IDEM-3"));

        assertThat(run.status()).isEqualTo(ProductRecommendationRunStatus.FAILED_CLOSED);
        assertThat(repository.findAttemptsByRun(run.runId())).hasSize(1);
        assertThat(repository.findAttemptsByRun(run.runId()).get(0).errorCode())
            .isEqualTo("KERT_INTERNAL_ERROR");
    }

    @Test
    void createRunContextInsufficientHolds() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
            .thenReturn(new SkillExecutionResult(SkillExecutionStatus.SKILL_ERROR, "REQ-2",
                Map.of(), List.of(new SkillExecutionResult.ErrorItem(
                    "KERT_CONTEXT_INSUFFICIENT", "必须事实不足")), List.of(), List.of()));

        ProductRecommendationRun run = service.createRun(command("IDEM-4"));

        assertThat(run.status()).isEqualTo(ProductRecommendationRunStatus.HELD);
    }

    @Test
    void decidePermissionDeniedRejects() {
        seedAwaitingHumanRun("run-perm", "V1");
        service = new ProductRecommendationApplicationService(
            repository, skillExecutionPort, (actorId, actorRole, gateId) -> false);

        assertThatThrownBy(() -> service.decide(
            new ProductRecommendationApplicationService.DecideCommand(
                "run-perm", ProductRecommendationApplicationService.HG_D01,
                "V1", "V1", RecommendationDecision.APPROVE, List.of(), "ok",
                "RM-1", "RELATIONSHIP_MANAGER")))
            .isInstanceOfSatisfying(RecommendationGatePreconditionException.class,
                ex -> assertThat(ex.code()).isEqualTo("PERMISSION_DENIED"));
    }

    @Test
    void decideEvidenceIncompleteRejects() {
        seedAwaitingHumanRunWithoutEvidence("run-evidence", "V1");

        assertThatThrownBy(() -> service.decide(
            new ProductRecommendationApplicationService.DecideCommand(
                "run-evidence", ProductRecommendationApplicationService.HG_D01,
                "V1", "V1", RecommendationDecision.APPROVE, List.of(), "ok",
                "RM-1", "RELATIONSHIP_MANAGER")))
            .isInstanceOfSatisfying(RecommendationGatePreconditionException.class,
                ex -> assertThat(ex.code()).isEqualTo("EVIDENCE_INCOMPLETE"));
    }

    private void seedAwaitingHumanRun(String runId, String versionId) {
        repository.saveRun(new ProductRecommendationRun(
            runId, "CUST-1", "JNY-1", null, List.of("NEEDV-1"), "objective",
            List.of("FINANCING"), Instant.parse("2026-08-31T09:00:00Z"), "idem-" + runId,
            ProductRecommendationRunStatus.AWAITING_HUMAN, versionId, "KERT-JOB-1",
            Map.of("evidenceBundleId", "EVB-1"), Instant.now(), Instant.now()));
        repository.saveVersion(new RecommendationProposalVersion(
            versionId, runId, "TRACE-1", "EVB-1", "sha256:abc", Map.of("k", "v"), null));
    }

    private void seedAwaitingHumanRunWithoutEvidence(String runId, String versionId) {
        repository.saveRun(new ProductRecommendationRun(
            runId, "CUST-1", "JNY-1", null, List.of("NEEDV-1"), "objective",
            List.of("FINANCING"), Instant.parse("2026-08-31T09:00:00Z"), "idem-" + runId,
            ProductRecommendationRunStatus.AWAITING_HUMAN, versionId, "KERT-JOB-1",
            Map.of(), Instant.now(), Instant.now()));
        repository.saveVersion(new RecommendationProposalVersion(
            versionId, runId, "TRACE-1", null, "sha256:abc", Map.of("k", "v"), null));
    }

    /** 内存版仓储（仅测试用）。 */
    private static final class FakeRepository implements ProductRecommendationRepository {
        private final Map<String, ProductRecommendationRun> runs = new HashMap<>();
        private final Map<String, String> runByKey = new HashMap<>();
        private final Map<String, RecommendationProposalVersion> versions = new HashMap<>();
        private final Map<String, RecommendationHumanDecision> decisions = new HashMap<>();
        private final Map<String, List<RecommendationAttempt>> attempts = new HashMap<>();
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
