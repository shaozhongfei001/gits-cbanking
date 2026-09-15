package com.gien.gits.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.api.dto.HumanGateDecisionRequest;
import com.gien.gits.api.dto.RecommendationHumanDecisionRequest;
import com.gien.gits.api.dto.StructuredModification;
import com.gien.gits.ontology.GateDecision;
import com.gien.gits.ontology.GateType;
import com.gien.gits.ontology.HumanGate;
import com.gien.gits.ontology.HumanGateStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationVersionConflictException;
import com.gien.gits.ontology.port.HumanGateRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * HG-D01 结构化人工决定服务单元测试（WP5-2，CANDIDATE）。
 *
 * <p>覆盖：结构化 modification 按 schema 校验（非法显式失败）、走应用服务决定、
 * 过期版本（并发 409 语义）异常透传、审计、非 D01 兼容透传。</p>
 */
class ProductRecommendationHumanGateServiceTest {

    private ProductRecommendationApplicationService applicationService;
    private HumanGateRepository humanGateRepository;
    private AuditLogPort auditLogPort;
    private ProductRecommendationHumanGateService service;

    @BeforeEach
    void setUp() {
        applicationService = mock(ProductRecommendationApplicationService.class);
        humanGateRepository = mock(HumanGateRepository.class);
        auditLogPort = mock(AuditLogPort.class);
        service = new ProductRecommendationHumanGateService(applicationService, humanGateRepository, auditLogPort);
    }

    private static RecommendationHumanDecisionRequest request(
            RecommendationDecision decision, List<StructuredModification> modifications) {
        return new RecommendationHumanDecisionRequest(
            "1.0.0", "run-1", "V1", "V1", decision, modifications,
            "reason", "RM-1", "RELATIONSHIP_MANAGER");
    }

    private static RecommendationHumanDecision decision() {
        return new RecommendationHumanDecision(
            "DEC-1", ProductRecommendationApplicationService.HG_D01, "run-1", "V1",
            RecommendationDecision.APPROVE, List.of(), "reason", "RM-1", "RELATIONSHIP_MANAGER");
    }

    @Test
    void decideRecommendationApprovesViaApplicationService() {
        when(applicationService.decide(any())).thenReturn(decision());

        RecommendationHumanDecision result =
            service.decideRecommendation(ProductRecommendationApplicationService.HG_D01,
                request(RecommendationDecision.APPROVE, List.of()));

        assertThat(result.decisionId()).isEqualTo("DEC-1");
        verify(applicationService).decide(any());
        verify(auditLogPort).log(eq("HUMAN_GATE_DECIDE"), eq("RM-1"),
            eq(ProductRecommendationApplicationService.HG_D01), eq("SUCCESS"), any());
    }

    @Test
    void decideRecommendationModifyMapsStructuredModificationsToCommand() {
        when(applicationService.decide(any())).thenReturn(decision());

        service.decideRecommendation(ProductRecommendationApplicationService.HG_D01,
            request(RecommendationDecision.MODIFY, List.of(
                new StructuredModification("REORDER_CANDIDATE", "PROD-1", null, 0, 2, null, "前移"),
                new StructuredModification("ADD_CONFIRMED_FACT", null, null, null, null, "已确认事实", null))));

        ArgumentCaptor<ProductRecommendationApplicationService.DecideCommand> captor =
            ArgumentCaptor.forClass(ProductRecommendationApplicationService.DecideCommand.class);
        verify(applicationService).decide(captor.capture());

        ProductRecommendationApplicationService.DecideCommand command = captor.getValue();
        assertThat(command.decision()).isEqualTo(RecommendationDecision.MODIFY);
        assertThat(command.proposalVersionId()).isEqualTo("V1");
        assertThat(command.expectedVersion()).isEqualTo("V1");
        assertThat(command.modifications()).hasSize(2);
        assertThat(command.modifications().get(0))
            .containsEntry("kind", "REORDER_CANDIDATE")
            .containsEntry("targetProductId", "PROD-1")
            .containsEntry("fromPosition", 0)
            .containsEntry("toPosition", 2);
        assertThat(command.modifications().get(1))
            .containsEntry("kind", "ADD_CONFIRMED_FACT")
            .containsEntry("value", "已确认事实");
    }

    @Test
    void decideRecommendationModifyWithoutModificationsFailsExplicitly() {
        assertThatThrownBy(() -> service.decideRecommendation(
            ProductRecommendationApplicationService.HG_D01, request(RecommendationDecision.MODIFY, List.of())))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("modifications is required");
        verify(applicationService, never()).decide(any());
    }

    @Test
    void decideRecommendationNonModifyWithModificationsFailsExplicitly() {
        assertThatThrownBy(() -> service.decideRecommendation(
            ProductRecommendationApplicationService.HG_D01, request(RecommendationDecision.APPROVE,
                List.of(new StructuredModification("REMOVE_CANDIDATE", "PROD-1", null, null, null, null, null)))))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("only allowed when decision=MODIFY");
        verify(applicationService, never()).decide(any());
    }

    @Test
    void decideRecommendationIllegalKindFailsExplicitly() {
        assertThatThrownBy(() -> service.decideRecommendation(
            ProductRecommendationApplicationService.HG_D01, request(RecommendationDecision.MODIFY,
                List.of(new StructuredModification("DELETE_EVERYTHING", "PROD-1", null, null, null, null, null)))))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("illegal modification kind");
        verify(applicationService, never()).decide(any());
    }

    @Test
    void decideRecommendationReorderMissingPositionsFailsExplicitly() {
        assertThatThrownBy(() -> service.decideRecommendation(
            ProductRecommendationApplicationService.HG_D01, request(RecommendationDecision.MODIFY,
                List.of(new StructuredModification("REORDER_CANDIDATE", "PROD-1", null, null, null, null, null)))))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("fromPosition and toPosition");
        verify(applicationService, never()).decide(any());
    }

    @Test
    void decideRecommendationChangeNextActionMissingValueFailsExplicitly() {
        assertThatThrownBy(() -> service.decideRecommendation(
            ProductRecommendationApplicationService.HG_D01, request(RecommendationDecision.MODIFY,
                List.of(new StructuredModification("CHANGE_NEXT_ACTION", null, null, null, null, null, null)))))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("requires value");
        verify(applicationService, never()).decide(any());
    }

    @Test
    void decideRecommendationStaleVersionPropagatesConflict() {
        when(applicationService.decide(any()))
            .thenThrow(new RecommendationVersionConflictException("stale proposal version"));

        assertThatThrownBy(() -> service.decideRecommendation(
            ProductRecommendationApplicationService.HG_D01, request(RecommendationDecision.APPROVE, List.of())))
            .isInstanceOf(RecommendationVersionConflictException.class);
        // 过期决定不得审计为 SUCCESS
        verify(auditLogPort, never()).log(anyString(), anyString(), anyString(), eq("SUCCESS"), any());
    }

    @Test
    void decideLegacyDelegatesToRepositoryAndAudits() {
        HumanGate updated = new HumanGate(
            "gate-1", GateType.C01_PREVISIT_APPROVE, "j-1", "c-1", "oc-1",
            HumanGateStatus.APPROVED, "访前审批", Map.of(), List.of(),
            GateDecision.APPROVE, null, "ok", "u-1", Instant.now(), Instant.now());
        when(humanGateRepository.decide(eq("gate-1"), eq(GateDecision.APPROVE), eq(null), eq("ok"), eq("u-1")))
            .thenReturn(updated);

        HumanGate result = service.decideLegacy("gate-1",
            new HumanGateDecisionRequest(GateDecision.APPROVE, null, "ok", "u-1"));

        assertThat(result.status()).isEqualTo(HumanGateStatus.APPROVED);
        verify(humanGateRepository).decide("gate-1", GateDecision.APPROVE, null, "ok", "u-1");
        verify(applicationService, never()).decide(any());
        verify(auditLogPort).log(eq("HUMAN_GATE_DECIDE"), eq("u-1"), eq("gate-1"), eq("SUCCESS"), any());
    }
}
