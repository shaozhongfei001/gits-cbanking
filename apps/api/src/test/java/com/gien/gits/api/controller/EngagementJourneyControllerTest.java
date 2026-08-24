package com.gien.gits.api.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.service.EngagementOrchestrator;
import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.api.service.MeetingScriptService;
import com.gien.gits.api.service.OutreachScriptService;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.engagement.port.MeetingScriptRepository;
import com.gien.gits.engagement.port.OutreachScriptRepository;
import com.gien.gits.api.service.PrevisitPreparationService;
import com.gien.gits.ontology.KycGapProfile;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.nullValue;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(EngagementJourneyController.class)
@AutoConfigureMockMvc(addFilters = false)
class EngagementJourneyControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;

    @MockitoBean EngagementOrchestrator engagementOrchestrator;
    @MockitoBean OutreachScriptService outreachScriptService;
    @MockitoBean MeetingScriptService meetingScriptService;
    @MockitoBean OutreachScriptRepository outreachScriptRepository;
    @MockitoBean MeetingScriptRepository meetingScriptRepository;
    @MockitoBean PrevisitPreparationService previsitPreparationService;
    @MockitoBean AuditLogPort auditLogPort;

    private CustomerJourney sampleJourney() {
        return new CustomerJourney(
            UUID.randomUUID(), UUID.randomUUID(), "CUST-001", "Test Customer",
            JourneyPhase.INSIGHT_ANALYSIS, Instant.now(), Instant.now());
    }

    @Test
    void testStartJourney() throws Exception {
        CustomerJourney journey = sampleJourney();
        KycGapProfile seedProfile = new KycGapProfile(
            "KYC-GAP-HDEG-20260705", "CUST-001", LocalDate.of(2026, 7, 5),
            List.of("集团股权结构(3家子公司)"),
            List.of("智能制造二期项目(已备案，投资额待确认)"),
            List.of("3000万需求的具体含义(上次提及但未明确)"),
            List.of(),
            List.of("二期项目实际投资额", "设备采购具体清单和时间表"),
            List.of("二期项目总投资和资金安排?", "3000万支持的具体用途?"));
        EngagementOrchestrator.JourneyStartResult startResult =
            new EngagementOrchestrator.JourneyStartResult(
                journey, UUID.randomUUID().toString(), Optional.of(seedProfile));
        when(engagementOrchestrator.startEngagementJourney("CUST-001"))
            .thenReturn(startResult);

        Map<String, String> body = Map.of("customerId", "CUST-001");
        mockMvc.perform(post("/api/v1/engagement/journey/start")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(body)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.customerId").value("CUST-001"))
            .andExpect(jsonPath("$.phase").value("INSIGHT_ANALYSIS"))
            .andExpect(jsonPath("$.operatingCaseId").isString())
            .andExpect(jsonPath("$.kycGapSummary").value(nullValue()))
            .andExpect(content().string(not(containsString("未知项"))))
            .andExpect(content().string(not(containsString("二期项目实际投资额"))))
            .andExpect(content().string(not(containsString("3000万支持的具体用途"))));
    }

    @Test
    void testCompleteJourney() throws Exception {
        String journeyId = UUID.randomUUID().toString();
        doNothing().when(engagementOrchestrator).completeJourney(journeyId);

        mockMvc.perform(post("/api/v1/engagement/journey/{journeyId}/complete", journeyId))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("COMPLETED"))
            .andExpect(jsonPath("$.journeyId").value(journeyId));
    }

    @Test
    void testListOutreachScripts() throws Exception {
        when(outreachScriptRepository.findByCustomerId("CUST-001")).thenReturn(java.util.List.of());

        mockMvc.perform(get("/api/v1/engagement/journey/outreach-scripts")
                .param("customerId", "CUST-001"))
            .andExpect(status().isOk());
    }

    @Test
    void testListMeetingScripts() throws Exception {
        when(meetingScriptRepository.findByCustomerId("CUST-001")).thenReturn(java.util.List.of());

        mockMvc.perform(get("/api/v1/engagement/journey/meeting-scripts")
                .param("customerId", "CUST-001"))
            .andExpect(status().isOk());
    }
}
