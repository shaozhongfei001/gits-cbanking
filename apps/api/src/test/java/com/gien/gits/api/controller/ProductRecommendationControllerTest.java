package com.gien.gits.api.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.dto.ProductRecommendationCreateRequest;
import com.gien.gits.api.service.ProductRecommendationApplicationService;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationGatePreconditionException;
import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;
import com.gien.gits.customerjourney.recommendation.port.ProductRecommendationRepository;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * 产品推荐 REST 控制器测试（CTR-PR-API-001，CANDIDATE）。
 * 模式与 HumanGateControllerTest 一致（@WebMvcTest + @MockitoBean）。
 */
@WebMvcTest(ProductRecommendationController.class)
@AutoConfigureMockMvc(addFilters = false)
class ProductRecommendationControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockitoBean
    private ProductRecommendationApplicationService applicationService;

    @MockitoBean
    private ProductRecommendationRepository repository;

    @MockitoBean
    private com.gien.gits.action.port.AuditLogPort auditLogPort;

    private static final Instant T0 = Instant.parse("2026-09-01T00:00:00Z");

    private ProductRecommendationRun run(ProductRecommendationRunStatus status) {
        return new ProductRecommendationRun(
                "RUN-001", "CUST-001", "JRN-001", null, List.of("NEED-001"),
                "补充流动资金融资方案", List.of("FINANCING"), T0,
                "IDEM-001", status, "VER-001", "KERT-JOB-1",
                Map.of("evidenceBundleId", "EVB-001"), T0, T0.plusSeconds(1));
    }

    private RecommendationProposalVersion version() {
        return new RecommendationProposalVersion(
                "VER-001", "RUN-001", null, "EVB-001", "sha256:abc",
                Map.of("eligibilityResults",
                        List.of(Map.of("productId", "PROD-1", "eligibility", "ELIGIBLE")),
                        "unknowns", List.of("NEED-RATING")),
                null, T0);
    }

    private String createBody() throws Exception {
        return objectMapper.writeValueAsString(new ProductRecommendationCreateRequest(
                "CUST-001", "JRN-001", null, List.of("NEED-001"),
                "补充流动资金融资方案", List.of("FINANCING"), T0,
                "CFS-001", "PKS-001", "RB-001", "PERM-001", "AC-PRODUCT-RECOMMEND-001"));
    }

    // ── createRun ──────────────────────────────────────────────────────

    @Test
    void createRun_success_passesIdempotencyKey() throws Exception {
        when(applicationService.createRun(any())).thenReturn(run(ProductRecommendationRunStatus.AWAITING_HUMAN));

        mockMvc.perform(post("/api/v1/product-recommendation-runs")
                        .header("Idempotency-Key", "IDEM-001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.runId").value("RUN-001"))
                .andExpect(jsonPath("$.status").value("AWAITING_HUMAN"));

        ArgumentCaptor<ProductRecommendationApplicationService.CreateRunCommand> captor =
                ArgumentCaptor.forClass(ProductRecommendationApplicationService.CreateRunCommand.class);
        verify(applicationService).createRun(captor.capture());
        org.assertj.core.api.Assertions.assertThat(captor.getValue().idempotencyKey()).isEqualTo("IDEM-001");
        org.assertj.core.api.Assertions.assertThat(captor.getValue().customerId()).isEqualTo("CUST-001");
        org.assertj.core.api.Assertions.assertThat(captor.getValue().productKnowledgeSnapshotRef()).isEqualTo("PKS-001");
        org.assertj.core.api.Assertions.assertThat(captor.getValue().permissionDecisionId()).isEqualTo("PERM-001");
    }

    @Test
    void createRun_missingIdempotencyKey_returns400() throws Exception {
        mockMvc.perform(post("/api/v1/product-recommendation-runs")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody()))
                .andExpect(status().isBadRequest());
    }

    @Test
    void createRun_replaySameKey_returnsSameRun() throws Exception {
        ProductRecommendationRun existing = run(ProductRecommendationRunStatus.AWAITING_HUMAN);
        when(applicationService.createRun(any())).thenReturn(existing);

        mockMvc.perform(post("/api/v1/product-recommendation-runs")
                        .header("Idempotency-Key", "IDEM-001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.runId").value("RUN-001"));
    }

    @Test
    void createRun_kertUnreachable_returnsFailedClosedRun() throws Exception {
        when(applicationService.createRun(any()))
                .thenReturn(run(ProductRecommendationRunStatus.FAILED_CLOSED));

        mockMvc.perform(post("/api/v1/product-recommendation-runs")
                        .header("Idempotency-Key", "IDEM-001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(createBody()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("FAILED_CLOSED"));
    }

    // ── getRun ─────────────────────────────────────────────────────────

    @Test
    void getRun_found_returnsRun() throws Exception {
        when(repository.findRunById("RUN-001")).thenReturn(Optional.of(run(ProductRecommendationRunStatus.PROPOSAL_READY)));

        mockMvc.perform(get("/api/v1/product-recommendation-runs/RUN-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.runId").value("RUN-001"))
                .andExpect(jsonPath("$.customerId").value("CUST-001"));
    }

    @Test
    void getRun_notFound_returns404() throws Exception {
        when(repository.findRunById("NOPE")).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/v1/product-recommendation-runs/NOPE"))
                .andExpect(status().isNotFound());
    }

    // ── getStages ──────────────────────────────────────────────────────

    @Test
    void getStages_returnsStageArraysFromVersionPayload() throws Exception {
        ProductRecommendationRun awaiting = run(ProductRecommendationRunStatus.AWAITING_HUMAN);
        when(repository.findRunById("RUN-001")).thenReturn(Optional.of(awaiting));
        when(repository.findVersionById("VER-001")).thenReturn(Optional.of(version()));

        mockMvc.perform(get("/api/v1/product-recommendation-runs/RUN-001/stages"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.runId").value("RUN-001"))
                .andExpect(jsonPath("$.status").value("AWAITING_HUMAN"))
                .andExpect(jsonPath("$.eligibilityResults[0].productId").value("PROD-1"))
                .andExpect(jsonPath("$.eligibilityResults[0].eligibility").value("ELIGIBLE"))
                .andExpect(jsonPath("$.unknowns[0]").value("NEED-RATING"));
    }

    @Test
    void getStages_notFound_returns404() throws Exception {
        when(repository.findRunById("NOPE")).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/v1/product-recommendation-runs/NOPE/stages"))
                .andExpect(status().isNotFound());
    }

    // ── getVersion ─────────────────────────────────────────────────────

    @Test
    void getVersion_found_returnsVersion() throws Exception {
        when(repository.findVersionById("VER-001")).thenReturn(Optional.of(version()));

        mockMvc.perform(get("/api/v1/product-recommendation-runs/RUN-001/versions/VER-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.versionId").value("VER-001"))
                .andExpect(jsonPath("$.contentHash").value("sha256:abc"));
    }

    @Test
    void getVersion_runMismatch_returns404() throws Exception {
        when(repository.findVersionById("VER-001")).thenReturn(Optional.of(version()));

        mockMvc.perform(get("/api/v1/product-recommendation-runs/OTHER-RUN/versions/VER-001"))
                .andExpect(status().isNotFound());
    }

    @Test
    void getVersion_notFound_returns404() throws Exception {
        when(repository.findVersionById("NOPE")).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/v1/product-recommendation-runs/RUN-001/versions/NOPE"))
                .andExpect(status().isNotFound());
    }

    // ── retry ──────────────────────────────────────────────────────────

    @Test
    void retry_success_returnsRun() throws Exception {
        when(repository.findRunById("RUN-001")).thenReturn(Optional.of(run(ProductRecommendationRunStatus.REQUESTED)));
        when(applicationService.retryRun("RUN-001")).thenReturn(run(ProductRecommendationRunStatus.AWAITING_HUMAN));

        mockMvc.perform(post("/api/v1/product-recommendation-runs/RUN-001/retry"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("AWAITING_HUMAN"));
    }

    @Test
    void retry_notRetryable_returns422() throws Exception {
        when(repository.findRunById("RUN-001")).thenReturn(Optional.of(run(ProductRecommendationRunStatus.FAILED_CLOSED)));
        when(applicationService.retryRun("RUN-001"))
                .thenThrow(new RecommendationGatePreconditionException("NOT_RETRYABLE", "仅 REQUESTED 可重试"));

        mockMvc.perform(post("/api/v1/product-recommendation-runs/RUN-001/retry"))
                .andExpect(status().isUnprocessableEntity());
    }

    @Test
    void retry_runNotFound_returns404() throws Exception {
        when(repository.findRunById("NOPE")).thenReturn(Optional.empty());

        mockMvc.perform(post("/api/v1/product-recommendation-runs/NOPE/retry"))
                .andExpect(status().isNotFound());
    }
}
