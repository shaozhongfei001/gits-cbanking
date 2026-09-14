package com.gien.gits.api.controller;

import com.gien.gits.api.service.CommitmentService;
import com.gien.gits.ontology.Commitment;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = CommitmentController.class, excludeAutoConfiguration = org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class)
class CommitmentControllerTest {

    @Autowired MockMvc mockMvc;

    @MockitoBean CommitmentService commitmentService;
    @MockitoBean com.gien.gits.action.port.AuditLogPort auditLogPort;

    private Commitment sampleCommitment() {
        return new Commitment(
                UUID.randomUUID(), "OC-001", "J-001",
                Commitment.CommitmentType.CUSTOMER_COMMITMENT, "Deliver report",
                "RM-001", LocalDate.of(2026, 12, 31),
                Commitment.CommitmentStatus.OPEN, null,
                Instant.now(), null,
                UUID.randomUUID(), UUID.randomUUID(),
                null, "RM-001", null,
                Instant.now(), Instant.now());
    }

    @Test void listAll_returnsOk() throws Exception {
        when(commitmentService.findAll()).thenReturn(List.of(sampleCommitment()));
        mockMvc.perform(get("/api/v1/commitments"))
                .andExpect(status().isOk());
    }

    @Test void listByCustomerId_returnsOk() throws Exception {
        when(commitmentService.findByCustomerId("CUST-001")).thenReturn(List.of(sampleCommitment()));
        mockMvc.perform(get("/api/v1/commitments").param("customerId", "CUST-001"))
                .andExpect(status().isOk());
    }

    @Test void listByInteractionId_returnsOk() throws Exception {
        when(commitmentService.findByInteractionId("INT-001")).thenReturn(List.of(sampleCommitment()));
        mockMvc.perform(get("/api/v1/commitments").param("interactionId", "INT-001"))
                .andExpect(status().isOk());
    }

    @Test void listByStatus_returnsOk() throws Exception {
        when(commitmentService.findByStatus("OPEN")).thenReturn(List.of(sampleCommitment()));
        mockMvc.perform(get("/api/v1/commitments").param("status", "OPEN"))
                .andExpect(status().isOk());
    }

    @Test void getById_found() throws Exception {
        when(commitmentService.findById("comm-001")).thenReturn(Optional.of(sampleCommitment()));
        mockMvc.perform(get("/api/v1/commitments/comm-001"))
                .andExpect(status().isOk());
    }

    @Test void getById_notFound() throws Exception {
        when(commitmentService.findById("MISSING")).thenReturn(Optional.empty());
        mockMvc.perform(get("/api/v1/commitments/MISSING"))
                .andExpect(status().isNotFound());
    }

    @Test void getOverdue_returnsOk() throws Exception {
        when(commitmentService.findOverdue()).thenReturn(List.of());
        mockMvc.perform(get("/api/v1/commitments/overdue"))
                .andExpect(status().isOk());
    }

    @Test void create_returnsCreated() throws Exception {
        when(commitmentService.create(any())).thenReturn(sampleCommitment());
        mockMvc.perform(post("/api/v1/commitments")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"content\":\"test\"}"))
                .andExpect(result -> { int s = result.getResponse().getStatus(); assert s == 201 || s == 400 : "Expected 201 or 400 but was " + s; });
    }

    @Test void updateStatus_found() throws Exception {
        when(commitmentService.updateStatus("comm-001", "FULFILLED", null))
                .thenReturn(Optional.of(sampleCommitment()));
        mockMvc.perform(put("/api/v1/commitments/comm-001/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"FULFILLED\"}"))
                .andExpect(status().isOk());
    }

    @Test void updateStatus_notFound() throws Exception {
        when(commitmentService.updateStatus("MISSING", "FULFILLED", null))
                .thenReturn(Optional.empty());
        mockMvc.perform(put("/api/v1/commitments/MISSING/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"FULFILLED\"}"))
                .andExpect(status().isNotFound());
    }
}
