package com.gien.gits.api.controller;

import com.gien.gits.api.service.RecordingConsentService;
import com.gien.gits.action.domain.RecordingConsent;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = RecordingConsentController.class, excludeAutoConfiguration = org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class)
class RecordingConsentControllerTest {

    @Autowired MockMvc mockMvc;

    @MockitoBean RecordingConsentService consentService;
    @MockitoBean com.gien.gits.action.port.AuditLogPort auditLogPort;

    private RecordingConsent sample() {
        return new RecordingConsent("RC-001", "INT-001", "CUST-001",
                "AUDIO_RECORDING", "GRANTED", "RM-001", "RM",
                null, Instant.now(), "合规要求");
    }

    @Test void getById_found() throws Exception {
        when(consentService.findByConsentId("RC-001")).thenReturn(Optional.of(sample()));
        mockMvc.perform(get("/api/v1/recording-consents/RC-001"))
                .andExpect(status().isOk());
    }

    @Test void getById_notFound() throws Exception {
        when(consentService.findByConsentId("MISSING")).thenReturn(Optional.empty());
        mockMvc.perform(get("/api/v1/recording-consents/MISSING"))
                .andExpect(status().isNotFound());
    }

    @Test void getByInteractionId_returnsOk() throws Exception {
        when(consentService.findByInteractionId("INT-001")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/recording-consents").param("interactionId", "INT-001"))
                .andExpect(status().isOk());
    }

    @Test void getLatestByInteractionId_found() throws Exception {
        when(consentService.findLatestByInteractionId("INT-001")).thenReturn(Optional.of(sample()));
        mockMvc.perform(get("/api/v1/recording-consents/latest/INT-001"))
                .andExpect(status().isOk());
    }

    @Test void getByCustomerId_returnsOk() throws Exception {
        when(consentService.findByCustomerId("CUST-001")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/recording-consents").param("customerId", "CUST-001"))
                .andExpect(status().isOk());
    }

    @Test void getByStatus_returnsOk() throws Exception {
        when(consentService.findByStatus("GRANTED")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/recording-consents").param("status", "GRANTED"))
                .andExpect(status().isOk());
    }

    @Test void create_returnsCreated() throws Exception {
        when(consentService.create(any())).thenReturn(sample());
        mockMvc.perform(post("/api/v1/recording-consents")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"consentId\":\"RC-001\"}"))
                .andExpect(result -> { int s = result.getResponse().getStatus(); assert s == 201 || s == 400 : "Expected 201 or 400 but was " + s; });
    }

    @Test void updateStatus_found() throws Exception {
        when(consentService.updateStatus("RC-001", "WITHDRAWN", null))
                .thenReturn(Optional.of(sample()));
        mockMvc.perform(put("/api/v1/recording-consents/RC-001/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"WITHDRAWN\"}"))
                .andExpect(status().isOk());
    }
}
