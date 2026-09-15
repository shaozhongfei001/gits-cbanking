package com.gien.gits.api.service;

import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.api.dto.HumanGateDecisionRequest;
import com.gien.gits.api.dto.RecommendationHumanDecisionRequest;
import com.gien.gits.api.dto.StructuredModification;
import com.gien.gits.ontology.HumanGate;
import com.gien.gits.customerjourney.recommendation.RecommendationDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.ontology.port.HumanGateRepository;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * HG-D01 结构化人工决定服务（WP5-2，CANDIDATE / FROZEN=NO / IMPLEMENTED=NO）。
 *
 * <p>把通用 HumanGate 的 {@code decide} 入口按门禁类型分流：</p>
 * <ul>
 *   <li><b>D01_PRODUCT_RECOMMEND</b> → 结构化 payload（{@link RecommendationHumanDecisionRequest}）：
 *       按 {@code recommendation-human-decision.schema.json} 校验 modification（非法修改显式拒绝，不静默忽略），
 *       再走 {@link ProductRecommendationApplicationService#decide(ProductRecommendationApplicationService.DecideCommand)}
 *       完成权限校验、{@code proposalVersionId} 并发版本检查（过期 → {@code RecommendationVersionConflictException}，
 *       语义等价 409）、证据校验与落决定，最后写审计。</li>
 *   <li><b>其他 GateType</b> → 保持与旧 {@code HumanGateRepository.decide} 兼容。</li>
 * </ul>
 */
public class ProductRecommendationHumanGateService {

    private static final Logger log = LoggerFactory.getLogger(ProductRecommendationHumanGateService.class);

    /** StructuredModification.kind 七值闭集（对齐 schema $defs/StructuredModification）。 */
    private static final Set<String> VALID_MODIFICATION_KINDS = Set.of(
        "REMOVE_CANDIDATE", "REORDER_CANDIDATE", "MOVE_TO_REVIEW",
        "ADD_SUPPORTING_PRODUCT", "REMOVE_SUPPORTING_PRODUCT",
        "CHANGE_NEXT_ACTION", "ADD_CONFIRMED_FACT");

    private static final String SCHEMA_VERSION = "1.0.0";

    private final ProductRecommendationApplicationService applicationService;
    private final HumanGateRepository humanGateRepository;
    private final AuditLogPort auditLogPort;

    public ProductRecommendationHumanGateService(
            ProductRecommendationApplicationService applicationService,
            HumanGateRepository humanGateRepository,
            AuditLogPort auditLogPort) {
        this.applicationService = Objects.requireNonNull(applicationService, "applicationService");
        this.humanGateRepository = Objects.requireNonNull(humanGateRepository, "humanGateRepository");
        this.auditLogPort = Objects.requireNonNull(auditLogPort, "auditLogPort");
    }

    /**
     * D01 结构化决定：校验 schema version + 结构化 modification 后走应用服务决定。
     *
     * @param gateId  门禁 ID（HG-D01 的 gateId）
     * @param request 结构化决定 payload
     * @return 已落库的人工决定记录
     * @throws IllegalArgumentException                非法 modification / schemaVersion（语义 400）
     * @throws com.gien.gits.customerjourney.recommendation.RecommendationVersionConflictException 过期版本/并发（语义 409）
     * @throws com.gien.gits.customerjourney.recommendation.RecommendationGatePreconditionException 权限/证据等前置失败
     */
    public RecommendationHumanDecision decideRecommendation(String gateId,
                                                            RecommendationHumanDecisionRequest request) {
        Objects.requireNonNull(request, "request");
        validateSchemaVersion(request.schemaVersion());
        validateModifications(request.decision(), request.modifications());

        RecommendationHumanDecision decision = applicationService.decide(
            new ProductRecommendationApplicationService.DecideCommand(
                request.runId(), gateId, request.proposalVersionId(), request.expectedVersion(),
                request.decision(), toMapList(request.modifications()),
                request.reason(), request.actorId(), request.actorRole()));

        auditLogPort.log("HUMAN_GATE_DECIDE", request.actorId(), gateId, "SUCCESS",
            Map.of("gateType", "D01_PRODUCT_RECOMMEND",
                   "decision", decision.decision().name(),
                   "runId", decision.runId(),
                   "proposalVersionId", decision.proposalVersionId()));
        log.info("[HG-D01] gateId={} decided {} by {} runId={} proposalVersionId={}",
                 gateId, decision.decision(), request.actorId(),
                 decision.runId(), decision.proposalVersionId());
        return decision;
    }

    /**
     * 非 D01 门禁决策：保持与旧 {@code HumanGateRepository.decide} 兼容。
     */
    public HumanGate decideLegacy(String gateId, HumanGateDecisionRequest request) {
        Objects.requireNonNull(request, "request");
        HumanGate updated = humanGateRepository.decide(
            gateId, request.decision(), request.modification(), request.reason(), request.actorId());

        auditLogPort.log("HUMAN_GATE_DECIDE", request.actorId(), gateId, "SUCCESS",
            Map.of("decision", request.decision().name()));
        log.info("HumanGate decided: gateId={}, decision={}, actor={}",
                 gateId, request.decision(), request.actorId());
        return updated;
    }

    // ── schema / modification 校验 ─────────────────────────────────────

    private void validateSchemaVersion(String schemaVersion) {
        if (schemaVersion != null && !schemaVersion.isBlank() && !SCHEMA_VERSION.equals(schemaVersion)) {
            throw new IllegalArgumentException(
                "schemaVersion must be " + SCHEMA_VERSION + " but was " + schemaVersion);
        }
    }

    /**
     * 结构化 modification 校验：非法修改显式失败，不静默忽略。
     * <ul>
     *   <li>decision=MODIFY 时 modifications 必填（至少一条）；非 MODIFY 时不得携带 modifications。</li>
     *   <li>kind 必须为七值闭集之一；REORDER_CANDIDATE 需 target + from/to 位置；
     *       CHANGE_NEXT_ACTION / ADD_CONFIRMED_FACT 需 value；其余需 targetProductId 或 targetPortfolioId。</li>
     * </ul>
     */
    private void validateModifications(RecommendationDecision decision, List<StructuredModification> modifications) {
        boolean hasModifications = modifications != null && !modifications.isEmpty();
        if (decision == RecommendationDecision.MODIFY && !hasModifications) {
            throw new IllegalArgumentException("modifications is required when decision=MODIFY");
        }
        if (decision != RecommendationDecision.MODIFY && hasModifications) {
            throw new IllegalArgumentException("modifications is only allowed when decision=MODIFY");
        }
        if (modifications == null) {
            return;
        }
        for (StructuredModification modification : modifications) {
            if (modification == null || isBlank(modification.kind())) {
                throw new IllegalArgumentException("modification.kind is required");
            }
            if (!VALID_MODIFICATION_KINDS.contains(modification.kind())) {
                throw new IllegalArgumentException("illegal modification kind: " + modification.kind());
            }
            validateKindFields(modification);
        }
    }

    private void validateKindFields(StructuredModification modification) {
        String kind = modification.kind();
        boolean hasTarget = !isBlank(modification.targetProductId())
            || !isBlank(modification.targetPortfolioId());
        switch (kind) {
            case "REORDER_CANDIDATE" -> {
                if (!hasTarget) {
                    throw new IllegalArgumentException(
                        "REORDER_CANDIDATE requires targetProductId or targetPortfolioId");
                }
                if (modification.fromPosition() == null || modification.toPosition() == null) {
                    throw new IllegalArgumentException(
                        "REORDER_CANDIDATE requires fromPosition and toPosition");
                }
            }
            case "CHANGE_NEXT_ACTION", "ADD_CONFIRMED_FACT" -> {
                if (isBlank(modification.value())) {
                    throw new IllegalArgumentException(kind + " requires value");
                }
            }
            default -> {
                // REMOVE_CANDIDATE / MOVE_TO_REVIEW / ADD_SUPPORTING_PRODUCT / REMOVE_SUPPORTING_PRODUCT
                if (!hasTarget) {
                    throw new IllegalArgumentException(
                        kind + " requires targetProductId or targetPortfolioId");
                }
            }
        }
    }

    // ── helpers ────────────────────────────────────────────────────────

    /** StructuredModification → Map（与应用服务 DecideCommand.modifications 的 List&lt;Map&gt; 对齐）。 */
    private static List<Map<String, Object>> toMapList(List<StructuredModification> modifications) {
        if (modifications == null || modifications.isEmpty()) {
            return List.of();
        }
        return modifications.stream().map(modification -> {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("kind", modification.kind());
            putIfPresent(map, "targetProductId", modification.targetProductId());
            putIfPresent(map, "targetPortfolioId", modification.targetPortfolioId());
            putIfPresent(map, "fromPosition", modification.fromPosition());
            putIfPresent(map, "toPosition", modification.toPosition());
            putIfPresent(map, "value", modification.value());
            putIfPresent(map, "note", modification.note());
            return map;
        }).toList();
    }

    private static void putIfPresent(Map<String, Object> target, String key, Object value) {
        if (value != null) {
            target.put(key, value);
        }
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
