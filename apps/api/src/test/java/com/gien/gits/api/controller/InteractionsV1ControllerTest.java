package com.gien.gits.api.controller;

import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.port.CustomerJourneyRepository;
import com.gien.gits.ontology.Channel;
import com.gien.gits.ontology.Interaction;
import com.gien.gits.ontology.port.InteractionRepository;
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
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(InteractionsV1Controller.class)
@AutoConfigureMockMvc(addFilters = false)
class InteractionsV1ControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private InteractionRepository interactionRepository;

    @MockitoBean
    private CustomerJourneyRepository journeyRepository;

    @MockitoBean
    private AuditLogPort auditLogPort;

    @Test
    void listInteractions_empty_returnsEmptyArray() throws Exception {
        when(interactionRepository.findAll()).thenReturn(List.of());

        mockMvc.perform(get("/api/v1/interactions"))
                .andExpect(status().isOk())
                .andExpect(content().json("[]"));
    }

    @Test
    void listInteractions_mapsJourneyCustomerAndContractChannel() throws Exception {
        UUID journeyId = UUID.randomUUID();
        UUID caseId = UUID.randomUUID();
        UUID interactionId = UUID.randomUUID();
        Interaction interaction = sampleInteraction(
                interactionId, caseId, journeyId, Channel.PHONE,
                new Interaction.Participant("RM-001", Interaction.Participant.Role.RELATIONSHIP_MANAGER, "王磊"),
                List.of());
        when(interactionRepository.findAll()).thenReturn(List.of(interaction));
        when(journeyRepository.findJourneyById(journeyId)).thenReturn(Optional.of(
                new CustomerJourney(journeyId, caseId, "CUST-CORP-0001", "华东精工",
                        JourneyPhase.KYC_COLLECT, Instant.parse("2026-08-01T00:00:00Z"), Instant.parse("2026-08-01T00:00:00Z"))));

        mockMvc.perform(get("/api/v1/interactions"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].interactionId").value(interactionId.toString()))
                .andExpect(jsonPath("$[0].customerId").value("CUST-CORP-0001"))
                .andExpect(jsonPath("$[0].channel").value("PHONE"))
                .andExpect(jsonPath("$[0].summary").value("例行回访"));
    }

    @Test
    void listInteractions_skipsRowsWithoutCustomerAndFiltersByQuery() throws Exception {
        UUID mappedId = UUID.randomUUID();
        UUID skippedId = UUID.randomUUID();
        UUID caseId = UUID.randomUUID();
        Interaction mapped = sampleInteraction(
                mappedId, caseId, null, Channel.INSTANT_MESSAGE,
                new Interaction.Participant("CUST-CORP-0002", Interaction.Participant.Role.CUSTOMER, "深圳创新"),
                List.of());
        Interaction skipped = sampleInteraction(
                skippedId, caseId, null, Channel.PHONE,
                new Interaction.Participant("RM-001", Interaction.Participant.Role.RELATIONSHIP_MANAGER, "王磊"),
                List.of());
        when(interactionRepository.findAll()).thenReturn(List.of(mapped, skipped));

        mockMvc.perform(get("/api/v1/interactions").param("customerId", "CUST-CORP-0002"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].interactionId").value(mappedId.toString()))
                .andExpect(jsonPath("$[0].channel").value("WECHAT"));

        mockMvc.perform(get("/api/v1/interactions").param("customerId", "CUST-MISSING"))
                .andExpect(status().isOk())
                .andExpect(content().json("[]"));
    }

    @Test
    void getInteraction_returnsMappedRow() throws Exception {
        UUID interactionId = UUID.randomUUID();
        UUID caseId = UUID.randomUUID();
        Interaction interaction = sampleInteraction(
                interactionId, caseId, null, Channel.FACE_TO_FACE,
                new Interaction.Participant("CUST-CORP-0001", Interaction.Participant.Role.CUSTOMER, "华东精工"),
                List.of());
        when(interactionRepository.findById(interactionId)).thenReturn(Optional.of(interaction));

        mockMvc.perform(get("/api/v1/interactions/{id}", interactionId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customerId").value("CUST-CORP-0001"))
                .andExpect(jsonPath("$.channel").value("IN_PERSON"));
    }

    @Test
    void getInteraction_missing_returns404() throws Exception {
        UUID missing = UUID.randomUUID();
        when(interactionRepository.findById(missing)).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/v1/interactions/{id}", missing))
                .andExpect(status().isNotFound());
    }

    private static Interaction sampleInteraction(
            UUID interactionId,
            UUID caseId,
            UUID journeyId,
            Channel channel,
            Interaction.Participant initiator,
            List<Interaction.Participant> participants) {
        return new Interaction(
                interactionId,
                caseId,
                journeyId,
                Interaction.InteractionType.PHONE_CALL,
                Interaction.Direction.OUTBOUND,
                channel,
                initiator,
                participants,
                "例行回访",
                List.of(),
                Interaction.InteractionOutcome.COMPLETED,
                Instant.parse("2026-08-01T00:00:00Z"),
                Instant.parse("2026-08-01T01:00:00Z"),
                "sha256:test-hash");
    }
}
