package com.gien.gits.api.service;

import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.RecommendationAttempt;
import com.gien.gits.customerjourney.recommendation.RecommendationAttemptStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationGatePreconditionException;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationVersionConflictException;
import com.gien.gits.customerjourney.recommendation.port.ProductRecommendationRepository;
import com.gien.gits.customerjourney.recommendation.port.RecommendationAuthorizationPort;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DuplicateKeyException;

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * 产品推荐应用服务（WP4-2，CANDIDATE / FROZEN=NO / IMPLEMENTED=NO）。
 *
 * <p>编排：{@code createRun}（Idempotency-Key 幂等 + KERT SkillExecutionPort 编排 +
 * 经领域对象状态推进）与 {@code decide}（HG-D01 前置校验：证据/权限/版本，及
 * If-Match/ETag 并发校验 → 过期拒绝，语义等价 409）。</p>
 *
 * <p>本服务不接本地推荐回退（INV-07 fail-closed）：KERT 不可达或失败时关闭本轮，
 * 不启用旧 {@code ProductMatchingService} 作为回退。</p>
 */
public class ProductRecommendationApplicationService {

    private static final Logger log = LoggerFactory.getLogger(ProductRecommendationApplicationService.class);

    /** SP-15 在 DKWS 运行平台的 skillId（契约 vNext §3：SkillExecuteRequest 顶层 skillId 固定为 SP-15）。 */
    public static final String KERT_SKILL_ID = "SP-15";

    /** SP-15 固定激活合同（契约 vNext §3.1：activationContract 固定 AC-PRODUCT-RECOMMEND-001）。 */
    public static final String ACTIVATION_CONTRACT_PRODUCT_RECOMMEND = "AC-PRODUCT-RECOMMEND-001";

    /** request 中标注「契约 vNext §3.1 必填引用尚未接线、按契约显式缺省」的字段名。 */
    static final String DEFAULTED_CONTEXT_REFS_KEY = "defaultedContextRefs";

    /** HG-D01 / D01_PRODUCT_RECOMMEND 人工门禁标识。 */
    public static final String HG_D01 = "HG-D01";

    private static final String SCHEMA_VERSION = "1.0.0";

    private final ProductRecommendationRepository repository;
    private final SkillExecutionPort skillExecutionPort;
    private final RecommendationAuthorizationPort authorizationPort;

    public ProductRecommendationApplicationService(
            ProductRecommendationRepository repository,
            SkillExecutionPort skillExecutionPort,
            RecommendationAuthorizationPort authorizationPort) {
        this.repository = Objects.requireNonNull(repository, "repository");
        this.skillExecutionPort = Objects.requireNonNull(skillExecutionPort, "skillExecutionPort");
        this.authorizationPort = Objects.requireNonNull(authorizationPort, "authorizationPort");
    }

    // ── createRun ──────────────────────────────────────────────────────

    /**
     * 创建一次产品推荐运行。幂等：相同 {@code idempotencyKey} 返回同一 run，
     * 不重复调用 KERT。
     */
    public ProductRecommendationRun createRun(CreateRunCommand command) {
        Objects.requireNonNull(command, "command");
        validateCreate(command);

        Optional<ProductRecommendationRun> existing =
            repository.findRunByIdempotencyKey(command.idempotencyKey());
        if (existing.isPresent()) {
            log.info("[PR-RUN] idempotency hit idempotencyKey={} runId={}",
                     command.idempotencyKey(), existing.get().runId());
            return existing.get();
        }

        String runId = UUID.randomUUID().toString();
        ProductRecommendationRun run = new ProductRecommendationRun(
            runId, command.customerId(), command.journeyId(), command.operatingCaseId(),
            command.needVersionIds(), command.recommendationObjective(),
            command.requestedProductDomains(), command.asOf(), command.idempotencyKey());

        try {
            repository.saveRun(run);
        } catch (DuplicateKeyException ex) {
            // 并发同键：唯一约束命中，回读已存在 run（不得重复执行 KERT）
            log.warn("[PR-RUN] duplicate idempotencyKey={}, re-reading existing run", command.idempotencyKey());
            return repository.findRunByIdempotencyKey(command.idempotencyKey()).orElseThrow();
        }

        return executeKert(run, command);
    }

    // ── retryRun ───────────────────────────────────────────────────────

    /**
     * 重试（CTR-PR-API-001：POST /{runId}/retry）。
     *
     * <p>仅 {@code REQUESTED} 状态可重试：KERT_EXECUTION_TIMEOUT 时 run 保持原态
     * （{@code mapFailure} 返回 {@code runStatus=null}），因此 REQUESTED 恰好对应
     * "超时后保留原轨迹、可重试" 的语义（ADR-PR-009：新 attempt 不覆盖旧轨迹）。
     * 其它状态（含终态 FAILED_CLOSED/APPROVED/...）抛 {@code NOT_RETRYABLE}（语义 422）。</p>
     */
    public ProductRecommendationRun retryRun(String runId) {
        ProductRecommendationRun run = repository.findRunById(runId)
            .orElseThrow(() -> new RecommendationGatePreconditionException(
                "NO_RUN", "run not found: " + runId));
        if (run.status() != ProductRecommendationRunStatus.REQUESTED) {
            throw new RecommendationGatePreconditionException(
                "NOT_RETRYABLE",
                "仅 REQUESTED 状态可重试（KERT 超时保留原态）；当前 status=" + run.status());
        }
        CreateRunCommand command = new CreateRunCommand(
            null, run.customerId(), run.journeyId(), run.operatingCaseId(), run.needVersionIds(),
            run.recommendationObjective(), run.requestedProductDomains(), run.asOf(),
            run.idempotencyKey());
        log.info("[PR-RUN] retry runId={} idempotencyKey={} (new attempt, same run)",
                 run.runId(), run.idempotencyKey());
        return executeKert(run, command);
    }

    private void validateCreate(CreateRunCommand command) {
        if (command.customerId() == null || command.customerId().isBlank()) {
            throw new IllegalArgumentException("customerId must not be blank");
        }
        if (command.idempotencyKey() == null || command.idempotencyKey().isBlank()) {
            throw new IllegalArgumentException("idempotencyKey must not be blank");
        }
        if (command.recommendationObjective() == null || command.recommendationObjective().isBlank()) {
            throw new IllegalArgumentException("recommendationObjective must not be blank");
        }
        if (command.asOf() == null) {
            throw new IllegalArgumentException("asOf must not be null");
        }
        boolean hasScope = (command.journeyId() != null && !command.journeyId().isBlank())
            || (command.operatingCaseId() != null && !command.operatingCaseId().isBlank());
        if (!hasScope) {
            throw new IllegalArgumentException("journeyId or operatingCaseId is required");
        }
    }

    // ── KERT orchestration ─────────────────────────────────────────────

    private ProductRecommendationRun executeKert(ProductRecommendationRun run, CreateRunCommand command) {
        String attemptId = UUID.randomUUID().toString();
        String kertRequestId = "KERT-PR-" + run.runId() + "-" + attemptId;
        Map<String, Object> request = buildKertRequest(run, command);
        SkillExecutionCommand skillCommand =
            new SkillExecutionCommand(KERT_SKILL_ID, kertRequestId, command.customerId(), request);

        Instant startedAt = Instant.now();
        try {
            SkillExecutionResult result = skillExecutionPort.execute(skillCommand);
            if (result.isOk() && hasRequiredOutput(result)) {
                return onKertSuccess(run, result, attemptId, kertRequestId, startedAt);
            }
            return onKertFailure(run, firstErrorCode(result), resultMessage(result),
                                 attemptId, kertRequestId, startedAt);
        } catch (SkillExecutionException ex) {
            // INV-07：KERT 不可达 → 禁止本地回退，fail-closed
            log.warn("[PR-RUN] KERT unreachable runId={}: {}", run.runId(), ex.getMessage());
            return onKertFailure(run, "KERT_INTERNAL_ERROR", ex.getMessage(),
                                 attemptId, kertRequestId, startedAt);
        }
    }

    private Map<String, Object> buildKertRequest(ProductRecommendationRun run, CreateRunCommand command) {
        Map<String, Object> context = new LinkedHashMap<>();
        context.put("schemaVersion", SCHEMA_VERSION);
        context.put("runId", run.runId());
        context.put("callerId", command.callerId());
        String customerId = command.customerId();
        context.put("customerId", customerId);
        // OQ-02：C2 降级 shell 无正式 Need 版本时，注入确定性演示引用（非生产路径）。
        // 生产化需由正式 Need 系统回填，移除本 demo 缺省。
        List<String> needVersionIds = (run.needVersionIds() == null || run.needVersionIds().isEmpty())
                ? List.of("NEEDV-" + customerId)
                : run.needVersionIds();
        context.put("needVersionIds", needVersionIds);
        context.put("recommendationObjective", run.recommendationObjective());
        context.put("requestedProductDomains", run.requestedProductDomains());
        context.put("asOf", run.asOf().toString());
        // 业务幂等键随上下文透传（wire 层幂等键 requestId 由 kertRequestId 承载，见 executeKert）
        context.put("idempotencyKey", run.idempotencyKey());

        // 契约 vNext §3.1 必填引用：快照引用（3/3）+ 权限决策 + 激活合同。
        // OQ-02：引用缺失时回退确定性演示值（非空），并在 request 标注 defaultedContextRefs。
        List<String> defaultedRefs = new ArrayList<>();
        context.put("customerFactSnapshotId",
                demoRefOrDefault(command.customerFactSnapshotId(), "CFS-" + customerId,
                        "customerFactSnapshotId", defaultedRefs));
        context.put("productKnowledgeSnapshotRef",
                demoRefOrDefault(command.productKnowledgeSnapshotRef(), "PKS-" + customerId,
                        "productKnowledgeSnapshotRef", defaultedRefs));
        context.put("ruleBundleRef",
                demoRefOrDefault(command.ruleBundleRef(), "RB-PR-20260831-0001",
                        "ruleBundleRef", defaultedRefs));
        context.put("permissionDecisionId",
                demoRefOrDefault(command.permissionDecisionId(), "PERM-" + customerId,
                        "permissionDecisionId", defaultedRefs));
        context.put("activationContract", activationContractOrDefault(command.activationContract()));

        Map<String, Object> request = new LinkedHashMap<>();
        request.put("context", context);
        if (!defaultedRefs.isEmpty()) {
            request.put(DEFAULTED_CONTEXT_REFS_KEY, defaultedRefs);
        }
        return request;
    }

    /** OQ-02：快照/权限引用缺失时回退确定性演示值（C2 降级 shell 专用），并登记到标注列表。 */
    private static String demoRefOrDefault(String value, String demoValue, String fieldName, List<String> defaultedRefs) {
        if (value == null || value.isBlank()) {
            defaultedRefs.add(fieldName);
            return demoValue;
        }
        return value;
    }

    /** 契约 vNext §3.1：activationContract 固定 AC-PRODUCT-RECOMMEND-001（未提供时回退固定值）。 */
    private static String activationContractOrDefault(String value) {
        return value == null || value.isBlank() ? ACTIVATION_CONTRACT_PRODUCT_RECOMMEND : value;
    }

    private ProductRecommendationRun onKertSuccess(ProductRecommendationRun run,
                                                   SkillExecutionResult result,
                                                   String attemptId, String kertRequestId,
                                                   Instant startedAt) {
        Map<String, Object> payload = kertResultPayload(result);
        String versionId = UUID.randomUUID().toString();
        String contentHash = stringField(payload, "contentHash");
        String evidenceBundleId = stringField(payload, "evidenceBundleId");
        String traceId = stringField(payload, "traceId");
        Map<String, String> snapshotRefs = new LinkedHashMap<>();
        putIfPresent(snapshotRefs, "productKnowledgeSnapshotRef",
                     stringField(payload, "productKnowledgeSnapshotRef"));
        putIfPresent(snapshotRefs, "ruleBundleRef",
                     stringField(payload, "ruleExecutionRef"));
        putIfPresent(snapshotRefs, "evidenceBundleId", evidenceBundleId);

        RecommendationProposalVersion version = new RecommendationProposalVersion(
            versionId, run.runId(), blankToNull(traceId), blankToNull(evidenceBundleId),
            contentHash, payload, null);
        repository.saveVersion(version);

        ProductRecommendationRun progressed = run
            .transitionTo(ProductRecommendationRunStatus.CONTEXT_ASSEMBLING)
            .transitionTo(ProductRecommendationRunStatus.HARD_FILTERING)
            .transitionTo(ProductRecommendationRunStatus.MATCHING)
            .transitionTo(ProductRecommendationRunStatus.PROPOSAL_READY)
            .withProposal(versionId, kertRequestId, snapshotRefs)
            .transitionTo(ProductRecommendationRunStatus.AWAITING_HUMAN);
        repository.updateRun(progressed);
        repository.saveAttempt(new RecommendationAttempt(
            attemptId, run.runId(), kertRequestId, startedAt, Instant.now(),
            RecommendationAttemptStatus.SUCCEEDED, null, false));
        log.info("[PR-RUN] runId={} succeeded, proposalVersionId={}, status=AWAITING_HUMAN",
                 run.runId(), versionId);
        return progressed;
    }

    private ProductRecommendationRun onKertFailure(ProductRecommendationRun run,
                                                   String errorCode, String message,
                                                   String attemptId, String kertRequestId,
                                                   Instant startedAt) {
        String code = errorCode == null || errorCode.isBlank() ? "KERT_INTERNAL_ERROR" : errorCode;
        KertFailure failure = mapFailure(code);
        repository.saveAttempt(new RecommendationAttempt(
            attemptId, run.runId(), kertRequestId, startedAt, Instant.now(),
            failure.attemptStatus(), code, failure.retryable()));

        if (failure.runStatus() == null) {
            // KERT_EXECUTION_TIMEOUT：保留 attempt，run 状态不变，可按策略重试
            log.warn("[PR-RUN] runId={} KERT timeout, run stays {}", run.runId(), run.status());
            return run;
        }
        // FO-02 权威状态机：REQUESTED 唯一后继为 CONTEXT_ASSEMBLING（§3.1 权威迁移表）。
        // KERT 失败发生在提交后的上下文装配阶段，因此先 REQUESTED -> CONTEXT_ASSEMBLING，
        // 再从 CONTEXT_ASSEMBLING 转入 HELD / FAILED_CLOSED（均为合法迁移）。
        ProductRecommendationRun inPipeline = run.status() == ProductRecommendationRunStatus.REQUESTED
            ? run.transitionTo(ProductRecommendationRunStatus.CONTEXT_ASSEMBLING)
            : run;
        ProductRecommendationRun closed = inPipeline.transitionTo(failure.runStatus());
        repository.updateRun(closed);
        log.warn("[PR-RUN] runId={} failed-closed status={} errorCode={} message={}",
                 run.runId(), closed.status(), code, message);
        return closed;
    }

    private static KertFailure mapFailure(String code) {
        return switch (code) {
            case "KERT_PERMISSION_DENIED" -> new KertFailure(
                ProductRecommendationRunStatus.FAILED_CLOSED, RecommendationAttemptStatus.FAILED, false);
            case "KERT_CONTEXT_INSUFFICIENT" -> new KertFailure(
                ProductRecommendationRunStatus.HELD, RecommendationAttemptStatus.FAILED, false);
            case "KERT_PRODUCT_KNOWLEDGE_STALE" -> new KertFailure(
                ProductRecommendationRunStatus.FAILED_CLOSED, RecommendationAttemptStatus.FAILED, false);
            case "KERT_RULE_VERSION_MISSING" -> new KertFailure(
                ProductRecommendationRunStatus.FAILED_CLOSED, RecommendationAttemptStatus.FAILED, false);
            case "KERT_EXECUTION_TIMEOUT" -> new KertFailure(
                null, RecommendationAttemptStatus.TIMEOUT, true);
            case "KERT_CONTRACT_MISMATCH" -> new KertFailure(
                ProductRecommendationRunStatus.FAILED_CLOSED, RecommendationAttemptStatus.CONTRACT_MISMATCH, false);
            case "KERT_EVIDENCE_INCOMPLETE" -> new KertFailure(
                ProductRecommendationRunStatus.FAILED_CLOSED, RecommendationAttemptStatus.FAILED, false);
            default -> new KertFailure(
                ProductRecommendationRunStatus.FAILED_CLOSED, RecommendationAttemptStatus.FAILED, true);
        };
    }

    // ── decide (HG-D01) ────────────────────────────────────────────────

    /**
     * 创建 HG-D01 人工决定。前置校验：版本（INV-06 + If-Match/ETag）、证据、权限；
     * 过期版本提交抛 {@link RecommendationVersionConflictException}（语义等价 409）。
     */
    public RecommendationHumanDecision decide(DecideCommand command) {
        Objects.requireNonNull(command, "command");
        validateDecide(command);

        ProductRecommendationRun run = repository.findRunById(command.runId())
            .orElseThrow(() -> new RecommendationGatePreconditionException(
                "NO_RUN", "run not found: " + command.runId()));

        // 版本校验：proposalVersionId 必须等于 run.currentVersionId（INV-06）
        if (run.currentVersionId() == null || !run.currentVersionId().equals(command.proposalVersionId())) {
            throw new RecommendationVersionConflictException(
                "stale proposal version: expected currentVersionId=" + run.currentVersionId()
                    + " but decision targets " + command.proposalVersionId());
        }
        // If-Match/ETag：expectedVersion 提供时必须匹配当前版本
        if (command.expectedVersion() != null && !command.expectedVersion().isBlank()
                && !command.expectedVersion().equals(run.currentVersionId())) {
            throw new RecommendationVersionConflictException(
                "If-Match/ETag mismatch: expectedVersion=" + command.expectedVersion()
                    + " but currentVersionId=" + run.currentVersionId());
        }
        // 状态校验：仅 AWAITING_HUMAN 可决定（覆盖重复决定场景）
        if (run.status() != ProductRecommendationRunStatus.AWAITING_HUMAN) {
            throw new RecommendationVersionConflictException(
                "run not awaiting human decision (current status=" + run.status() + ")");
        }

        // 证据校验：方案版本存在且携带证据（contentHash + evidenceBundleId）
        RecommendationProposalVersion version = repository.findVersionById(command.proposalVersionId())
            .orElseThrow(() -> new RecommendationGatePreconditionException(
                "EVIDENCE_INCOMPLETE", "proposal version not found: " + command.proposalVersionId()));
        if (version.evidenceBundleId() == null || version.evidenceBundleId().isBlank()) {
            throw new RecommendationGatePreconditionException(
                "EVIDENCE_INCOMPLETE", "proposal version has no evidenceBundleId");
        }

        // 权限校验
        if (!authorizationPort.isAuthorized(command.actorId(), command.actorRole(), command.gateId())) {
            throw new RecommendationGatePreconditionException(
                "PERMISSION_DENIED", "actor not authorized for gate " + command.gateId());
        }

        RecommendationHumanDecision decision = new RecommendationHumanDecision(
            UUID.randomUUID().toString(), command.gateId(), command.runId(),
            command.proposalVersionId(), command.decision(), command.modifications(),
            command.reason(), command.actorId(), command.actorRole());
        repository.saveDecision(decision);

        ProductRecommendationRun updated = run.applyDecision(command.decision());
        repository.updateRun(updated);
        log.info("[PR-RUN] runId={} decided {} by {} -> status={}",
                 run.runId(), command.decision(), command.actorId(), updated.status());
        return decision;
    }

    private void validateDecide(DecideCommand command) {
        if (command.runId() == null || command.runId().isBlank()) {
            throw new IllegalArgumentException("runId must not be blank");
        }
        if (command.gateId() == null || command.gateId().isBlank()) {
            throw new IllegalArgumentException("gateId must not be blank");
        }
        if (command.proposalVersionId() == null || command.proposalVersionId().isBlank()) {
            throw new IllegalArgumentException("proposalVersionId must not be blank");
        }
        Objects.requireNonNull(command.decision(), "decision");
        if (command.actorId() == null || command.actorId().isBlank()) {
            throw new IllegalArgumentException("actorId must not be blank");
        }
        boolean reasonRequired = command.decision() == RecommendationDecision.REJECT
            || command.decision() == RecommendationDecision.HOLD;
        if (reasonRequired && (command.reason() == null || command.reason().isBlank())) {
            throw new RecommendationGatePreconditionException(
                "REASON_REQUIRED", "reason is required for " + command.decision());
        }
    }

    // ── helpers ────────────────────────────────────────────────────────

    private static boolean hasRequiredOutput(SkillExecutionResult result) {
        Map<String, Object> payload = kertResultPayload(result);
        return !stringField(payload, "contentHash").isBlank()
            && !stringField(payload, "evidenceBundleId").isBlank();
    }

    /**
     * 提取 KERT(SP-15) 响应中的结果载荷。
     *
     * <p>DKWS 真实响应形状：{@code data.result} = ProductRecommendationResult
     * （contentHash/evidenceBundleId 等 8 必填字段与 eligibilityResults[] 等数组都在
     * {@code result} 内层）；为兼容测试 fake 的顶层形状，当 {@code data.result} 非 Map
     * 时回退到 {@code data} 本身。</p>
     */
    @SuppressWarnings("unchecked")
    private static Map<String, Object> kertResultPayload(SkillExecutionResult result) {
        Object nested = result.data().get("result");
        if (nested instanceof Map<?, ?> map) {
            Map<String, Object> converted = new LinkedHashMap<>();
            map.forEach((k, v) -> converted.put(String.valueOf(k), v));
            return converted;
        }
        return result.data();
    }

    private static String firstErrorCode(SkillExecutionResult result) {
        if (result.errors() == null || result.errors().isEmpty()) {
            return null;
        }
        return result.errors().get(0).code();
    }

    private static String resultMessage(SkillExecutionResult result) {
        if (result.errors() == null || result.errors().isEmpty()) {
            return result.status().name();
        }
        return result.errors().get(0).message();
    }

    private static String stringField(Map<String, Object> data, String key) {
        Object value = data.get(key);
        return value == null ? "" : String.valueOf(value).trim();
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value;
    }

    private static void putIfPresent(Map<String, String> target, String key, String value) {
        if (value != null && !value.isBlank()) {
            target.put(key, value);
        }
    }

    /** KERT 失败码 → run/attempt 处置（README §4 + ADR-PR-009）。 */
    private record KertFailure(ProductRecommendationRunStatus runStatus,
                               RecommendationAttemptStatus attemptStatus,
                               boolean retryable) {}

    // ── commands ───────────────────────────────────────────────────────

    public record CreateRunCommand(
            String callerId,
            String customerId,
            String journeyId,
            String operatingCaseId,
            List<String> needVersionIds,
            String recommendationObjective,
            List<String> requestedProductDomains,
            Instant asOf,
            String idempotencyKey,
            String customerFactSnapshotId,
            String productKnowledgeSnapshotRef,
            String ruleBundleRef,
            String permissionDecisionId,
            String activationContract) {

        /**
         * 兼容构造：快照引用 / 权限决策 / 激活合同尚未接线（WP6-4 之前调用点沿用 9 参形式）。
         * 这些引用缺省为 {@code null}，由 {@code buildKertRequest} 按契约显式缺省并标注。
         */
        public CreateRunCommand(
                String callerId,
                String customerId,
                String journeyId,
                String operatingCaseId,
                List<String> needVersionIds,
                String recommendationObjective,
                List<String> requestedProductDomains,
                Instant asOf,
                String idempotencyKey) {
            this(callerId, customerId, journeyId, operatingCaseId, needVersionIds,
                 recommendationObjective, requestedProductDomains, asOf, idempotencyKey,
                 null, null, null, null, null);
        }
    }

    public record DecideCommand(
            String runId,
            String gateId,
            String proposalVersionId,
            String expectedVersion,
            RecommendationDecision decision,
            List<Map<String, Object>> modifications,
            String reason,
            String actorId,
            String actorRole) {}
}
