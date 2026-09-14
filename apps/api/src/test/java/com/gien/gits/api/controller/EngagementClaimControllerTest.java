package com.gien.gits.api.controller;

import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.port.CustomerJourneyRepository;
import com.gien.gits.ontology.Claim;
import com.gien.gits.ontology.ClaimStatus;
import com.gien.gits.ontology.ClaimType;
import com.gien.gits.ontology.port.ClaimRepository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(EngagementClaimController.class)
@AutoConfigureMockMvc(addFilters = false)
class EngagementClaimControllerTest {

    @Autowired MockMvc mockMvc;

    @MockitoBean ClaimRepository claimRepo;
    @MockitoBean CustomerJourneyRepository journeyRepo;
    @MockitoBean AuditLogPort auditLogPort;

    private static final UUID CASE_ID = UUID.fromString("a1b2c3d4-e5f6-7890-abcd-100000000003");
    private static final UUID JOURNEY_ID = UUID.fromString("a1b2c3d4-e5f6-7890-abcd-000000000003");

    private CustomerJourney sampleJourney() {
        return new CustomerJourney(
                JOURNEY_ID, CASE_ID, "CUST-CORP-0003", "北京绿源环保集团",
                JourneyPhase.POSTVISIT_REVIEW,
                Instant.parse("2026-06-20T08:30:00Z"),
                Instant.parse("2026-08-15T11:00:00Z"));
    }

    private Claim sampleClaim() {
        return new Claim(
                UUID.fromString("c1a1b2c3-d4e5-f678-90ab-cd0000000021"),
                CASE_ID,
                ClaimType.CUSTOMER_STATEMENT,
                ClaimStatus.HUMAN_CONFIRMED,
                "客户表示未来3年将投入5亿元用于碳中和技术改造",
                Instant.parse("2026-06-25T10:00:00Z"),
                null,
                Instant.parse("2026-06-25T10:00:00Z"),
                null);
    }

    @Test
    void listClaims_returnsClaimsWithCustomerId() throws Exception {
        when(journeyRepo.findJourneysByCustomerId("CUST-CORP-0003"))
                .thenReturn(List.of(sampleJourney()));
        when(claimRepo.findByCaseId(CASE_ID)).thenReturn(List.of(sampleClaim()));

        mockMvc.perform(get("/api/v1/engagement/claims")
                        .param("customerId", "CUST-CORP-0003"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].claimId").value("c1a1b2c3-d4e5-f678-90ab-cd0000000021"))
                .andExpect(jsonPath("$[0].customerId").value("CUST-CORP-0003"))
                .andExpect(jsonPath("$[0].content").value("客户表示未来3年将投入5亿元用于碳中和技术改造"))
                .andExpect(jsonPath("$[0].status").value("HUMAN_CONFIRMED"));
    }

    @Test
    void listClaims_emptyWhenCustomerIdMissing() throws Exception {
        mockMvc.perform(get("/api/v1/engagement/claims"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$").isEmpty());
    }

    @Test
    void listClaims_emptyWhenNoJourneys() throws Exception {
        when(journeyRepo.findJourneysByCustomerId("CUST-CORP-9999")).thenReturn(List.of());

        mockMvc.perform(get("/api/v1/engagement/claims")
                        .param("customerId", "CUST-CORP-9999"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$").isEmpty());
    }

    @Test
    void getClaim_returnsClaim() throws Exception {
        UUID claimId = UUID.fromString("c1a1b2c3-d4e5-f678-90ab-cd0000000021");
        when(claimRepo.findById(claimId)).thenReturn(Optional.of(sampleClaim()));
        when(journeyRepo.findJourneysByCaseId(CASE_ID)).thenReturn(List.of(sampleJourney()));

        mockMvc.perform(get("/api/v1/engagement/claims/{claimId}", claimId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.claimId").value("c1a1b2c3-d4e5-f678-90ab-cd0000000021"))
                .andExpect(jsonPath("$.customerId").value("CUST-CORP-0003"));
    }

    @Test
    void getClaim_returns404WhenNotFound() throws Exception {
        UUID claimId = UUID.fromString("c1a1b2c3-d4e5-f678-90ab-cd0000000099");
        when(claimRepo.findById(claimId)).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/v1/engagement/claims/{claimId}", claimId))
                .andExpect(status().isNotFound());
    }
}
