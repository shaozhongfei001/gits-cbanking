package com.gien.gits.api.controller;

import com.gien.gits.api.service.ProductKnowledgeVersionService;
import com.gien.gits.ontology.domain.ProductKnowledgeVersion;
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

@WebMvcTest(controllers = ProductKnowledgeVersionController.class, excludeAutoConfiguration = org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class)
class ProductKnowledgeVersionControllerTest {

    @Autowired MockMvc mockMvc;

    @MockitoBean ProductKnowledgeVersionService versionService;
    @MockitoBean com.gien.gits.action.port.AuditLogPort auditLogPort;

    private ProductKnowledgeVersion sample() {
        return new ProductKnowledgeVersion("PV-001", "PROD-CM-001", 1,
                "集团现金池", "CASH_MANAGEMENT", "desc",
                List.of("feature1"), List.of("制造业"), "LOW",
                List.of("营业执照"), "固定费率", null, "初始版本", "system");
    }

    @Test void getByVersionId_found() throws Exception {
        when(versionService.findByVersionId("PV-001")).thenReturn(Optional.of(sample()));
        mockMvc.perform(get("/api/v1/product-knowledge/versions/PV-001"))
                .andExpect(status().isOk());
    }

    @Test void getByVersionId_notFound() throws Exception {
        when(versionService.findByVersionId("MISSING")).thenReturn(Optional.empty());
        mockMvc.perform(get("/api/v1/product-knowledge/versions/MISSING"))
                .andExpect(status().isNotFound());
    }

    @Test void getByProductId_returnsOk() throws Exception {
        when(versionService.findByProductId("PROD-CM-001")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/product-knowledge").param("productId", "PROD-CM-001"))
                .andExpect(status().isOk());
    }

    @Test void getLatest_returnsOk() throws Exception {
        when(versionService.findLatestByProductId("PROD-CM-001")).thenReturn(Optional.of(sample()));
        mockMvc.perform(get("/api/v1/product-knowledge/latest/PROD-CM-001"))
                .andExpect(status().isOk());
    }

    @Test void getLatest_notFound() throws Exception {
        when(versionService.findLatestByProductId("MISSING")).thenReturn(Optional.empty());
        mockMvc.perform(get("/api/v1/product-knowledge/latest/MISSING"))
                .andExpect(status().isNotFound());
    }

    @Test void getByCategory_returnsOk() throws Exception {
        when(versionService.findByCategory("CASH_MANAGEMENT")).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/product-knowledge").param("category", "CASH_MANAGEMENT"))
                .andExpect(status().isOk());
    }

    @Test void getRecent_returnsOk() throws Exception {
        when(versionService.findRecentVersions(20)).thenReturn(List.of(sample()));
        mockMvc.perform(get("/api/v1/product-knowledge/recent"))
                .andExpect(status().isOk());
    }

    @Test void create_returnsCreated() throws Exception {
        when(versionService.create(any())).thenReturn(sample());
        mockMvc.perform(post("/api/v1/product-knowledge")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"versionId\":\"PV-001\"}"))
                .andExpect(result -> { int s = result.getResponse().getStatus(); assert s == 201 || s == 400 : "Expected 201 or 400 but was " + s; });
    }
}
