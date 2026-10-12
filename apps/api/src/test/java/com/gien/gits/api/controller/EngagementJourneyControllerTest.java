package com.gien.gits.api.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.service.EngagementOrchestrator;
import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.api.service.MeetingScriptService;
import com.gien.gits.api.service.OutreachScriptService;
import com.gien.gits.api.service.PrevisitPreparationService;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.port.CustomerJourneyRepository;
import com.gien.gits.engagement.port.OutreachScriptRepository;
import com.gien.gits.engagement.port.MeetingScriptRepository;
import com.gien.gits.ontology.port.RelationshipReportRepository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

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
    @MockitoBean CustomerJourneyRepository journeyRepository;
    @MockitoBean RelationshipReportRepository reportRepository;
    @MockitoBean AuditLogPort auditLogPort;

    private CustomerJourney sampleJourney() {
        return new CustomerJourney(
            UUID.randomUUID(), UUID.randomUUID(), "CUST-001", "Test Customer",
            JourneyPhase.INSIGHT_ANALYSIS, Instant.now(), Instant.now());
    }

    private CustomerJourney journey(String customerId, String customerName, String name,
                                    Instant startedAt, JourneyPhase phase) {
        return new CustomerJourney(
            UUID.randomUUID(), UUID.randomUUID(), customerId, customerName,
            phase, startedAt, startedAt, name);
    }

    @Test
    void testStartJourney() throws Exception {
        CustomerJourney journey = sampleJourney();
        EngagementOrchestrator.JourneyStartResult startResult =
            new EngagementOrchestrator.JourneyStartResult(journey, UUID.randomUUID().toString(), Optional.empty());
        when(engagementOrchestrator.startEngagementJourney(eq("CUST-001"), isNull()))
            .thenReturn(startResult);

        Map<String, String> body = Map.of("customerId", "CUST-001");
        mockMvc.perform(post("/api/v1/engagement/journey/start")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(body)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.customerId").value("CUST-001"))
            .andExpect(jsonPath("$.phase").value("INSIGHT_ANALYSIS"))
            .andExpect(jsonPath("$.operatingCaseId").isString());
    }

    @Test
    void testStartJourneyPassesRequestedNameAndReturnsDerivedName() throws Exception {
        Instant startedAt = Instant.parse("2026-09-25T06:00:00Z");
        CustomerJourney journey = journey("CUST-001", "Test Customer",
                "Test Customer 经营旅程 #1", startedAt, JourneyPhase.INSIGHT_ANALYSIS);
        EngagementOrchestrator.JourneyStartResult startResult =
            new EngagementOrchestrator.JourneyStartResult(journey, UUID.randomUUID().toString(), Optional.empty());
        when(engagementOrchestrator.startEngagementJourney("CUST-001", "扩产融资专题旅程"))
            .thenReturn(startResult);

        mockMvc.perform(post("/api/v1/engagement/journey/start")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(
                        Map.of("customerId", "CUST-001", "journeyName", "扩产融资专题旅程"))))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.journeyName").value("Test Customer 经营旅程 #1"));

        verify(engagementOrchestrator).startEngagementJourney("CUST-001", "扩产融资专题旅程");
    }

    @Test
    void listJourneysWithoutCustomerIdReturnsAllWithResolvedNames() throws Exception {
        Instant base = Instant.parse("2026-09-25T06:00:00Z");
        CustomerJourney first = journey("CUST-001", "甲客户", null, base, JourneyPhase.KYC_COLLECT);
        CustomerJourney second = journey("CUST-001", "甲客户", null,
                base.plus(1, ChronoUnit.HOURS), JourneyPhase.PREVISIT_PREP);
        CustomerJourney other = journey("CUST-002", "乙客户", "乙客户 手工命名", base, JourneyPhase.COMPLETED);
        when(journeyRepository.findAllJourneys()).thenReturn(List.of(second, other, first));

        mockMvc.perform(get("/api/v1/engagement/journey"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.length()").value(3))
            // 入参顺序保持：列表顺序不被重排
            .andExpect(jsonPath("$[0].customerId").value("CUST-001"))
            .andExpect(jsonPath("$[0].journeyName").value("甲客户 经营旅程 #2"))
            .andExpect(jsonPath("$[1].journeyName").value("乙客户 手工命名"))
            .andExpect(jsonPath("$[2].journeyName").value("甲客户 经营旅程 #1"));

        verify(journeyRepository, never()).findJourneysByCustomerId(anyString());
    }

    @Test
    void listJourneysWithCustomerIdScopesToThatCustomer() throws Exception {
        CustomerJourney only = journey("CUST-001", "甲客户", null, Instant.now(), JourneyPhase.KYC_COLLECT);
        when(journeyRepository.findJourneysByCustomerId("CUST-001")).thenReturn(List.of(only));

        mockMvc.perform(get("/api/v1/engagement/journey").param("customerId", "CUST-001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.length()").value(1))
            .andExpect(jsonPath("$[0].journeyName").value("甲客户 经营旅程 #1"));

        verify(journeyRepository, never()).findAllJourneys();
    }

    @Test
    void listJourneysReturnsEmptyArrayWhenNoData() throws Exception {
        when(journeyRepository.findAllJourneys()).thenReturn(List.of());

        mockMvc.perform(get("/api/v1/engagement/journey"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void getJourneyDerivesNameUsingCustomerScopedOrdinal() throws Exception {
        Instant base = Instant.parse("2026-09-25T06:00:00Z");
        CustomerJourney first = journey("CUST-001", "甲客户", null, base, JourneyPhase.KYC_COLLECT);
        CustomerJourney third = journey("CUST-001", "甲客户", null,
                base.plus(2, ChronoUnit.HOURS), JourneyPhase.PREVISIT_PREP);
        when(journeyRepository.findJourneyById(third.journeyId())).thenReturn(Optional.of(third));
        when(journeyRepository.findJourneysByCustomerId("CUST-001"))
                .thenReturn(List.of(first, third));

        mockMvc.perform(get("/api/v1/engagement/journey/{journeyId}", third.journeyId()))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.journeyName").value("甲客户 经营旅程 #2"));
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
