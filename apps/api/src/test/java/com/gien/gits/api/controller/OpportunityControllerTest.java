package com.gien.gits.api.controller;

import com.gien.gits.api.service.OpportunityService;
import com.gien.gits.ontology.domain.Opportunity;
import com.gien.gits.action.port.AuditLogPort;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = OpportunityController.class,
        excludeAutoConfiguration = org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class)
class OpportunityControllerTest {

    @Autowired MockMvc mockMvc;

    @MockitoBean OpportunityService opportunityService;
    @MockitoBean AuditLogPort auditLogPort;

    private Opportunity sample() {
        return new Opportunity("OPP-1", "C-1", "INT-1", "OC-1", "CROSS_SELL",
                "PROD-1", "集团现金池", "desc", "QUALIFIED",
                "100万", "HIGH", "RM-1", "INTERACTION", List.of("跟进"), "2026-12-31");
    }

    @Test void listAll_returnsOk() throws Exception {
        when(opportunityService.findAll()).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/opportunities"))
                .andExpect(status().isOk());
    }

    @Test void getByCustomerId_returnsOk() throws Exception {
        when(opportunityService.findByCustomerId("C-1")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/opportunities").param("customerId", "C-1"))
                .andExpect(status().isOk());
    }

    @Test void getByStatus_returnsOk() throws Exception {
        when(opportunityService.findByStatus("QUALIFIED")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/opportunities").param("status", "QUALIFIED"))
                .andExpect(status().isOk());
    }

    @Test void getByType_returnsOk() throws Exception {
        when(opportunityService.findByOpportunityType("CROSS_SELL")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/opportunities").param("opportunityType", "CROSS_SELL"))
                .andExpect(status().isOk());
    }

    @Test void getByAssignedTo_returnsOk() throws Exception {
        when(opportunityService.findByAssignedTo("RM-1")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/opportunities").param("assignedTo", "RM-1"))
                .andExpect(status().isOk());
    }

    @Test void getById_found() throws Exception {
        when(opportunityService.findById("OPP-1")).thenReturn(Optional.of(sample()));
        mockMvc.perform(get("/api/v1/opportunities/OPP-1"))
                .andExpect(status().isOk());
    }

    @Test void getById_notFound() throws Exception {
        when(opportunityService.findById("MISSING")).thenReturn(Optional.empty());
        mockMvc.perform(get("/api/v1/opportunities/MISSING"))
                .andExpect(status().isNotFound());
    }

    @Test void getActiveByCustomerId_returnsOk() throws Exception {
        when(opportunityService.findActiveByCustomerId("C-1")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/opportunities/C-1/active"))
                .andExpect(status().isOk());
    }

    @Test void updateStage_found() throws Exception {
        when(opportunityService.updateStatus("OPP-1", "WON")).thenReturn(Optional.of(sample()));
        mockMvc.perform(put("/api/v1/opportunities/OPP-1/stage")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"stage\":\"WON\"}"))
                .andExpect(status().isOk());
    }

    @Test void updateStage_notFound() throws Exception {
        when(opportunityService.updateStatus("MISSING", "WON")).thenReturn(Optional.empty());
        mockMvc.perform(put("/api/v1/opportunities/MISSING/stage")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"stage\":\"WON\"}"))
                .andExpect(status().isNotFound());
    }
}
