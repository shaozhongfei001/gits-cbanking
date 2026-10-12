package com.gien.gits.api.controller;

import com.gien.gits.knowledge.port.KnowledgeElementPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import com.gien.gits.action.port.AuditLogPort;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = KnowledgeMapController.class,
        excludeAutoConfiguration = org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class)
@org.springframework.test.context.TestPropertySource(properties = "gits.knowledge.enabled=true")
class KnowledgeMapControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired RequestMappingHandlerMapping handlerMapping;

    @MockitoBean KnowledgeElementPort elementPort;
    @MockitoBean KnowledgeMapPort mapPort;
    @MockitoBean AuditLogPort auditLogPort;

    @BeforeEach
    void printMappings() {
        handlerMapping.getHandlerMethods().forEach((key, value) -> {
            if (key.getPatternsCondition() != null) {
                key.getPatternsCondition().getPatterns().forEach(p ->
                    System.out.println("[MAPPING] " + p + " -> " + value.getBeanType().getSimpleName()));
            }
        });
    }

    @Test void allElements_returnsOk() throws Exception {
        when(elementPort.listAll()).thenReturn(List.of());
        mockMvc.perform(get("/api/v1/knowledge/elements"))
                .andExpect(status().isOk());
    }

    @Test void byKnowledgeItem_returnsOk() throws Exception {
        when(elementPort.listByKnowledgeItem("KI-FRONT-001")).thenReturn(List.of());
        mockMvc.perform(get("/api/v1/knowledge/items/KI-FRONT-001"))
                .andExpect(status().isOk());
    }

    @Test void map_returnsOk() throws Exception {
        when(elementPort.listAll()).thenReturn(List.of());
        mockMvc.perform(get("/api/v1/knowledge/map"))
                .andExpect(status().isOk());
    }

    @Test void items_returnsOk() throws Exception {
        when(elementPort.listAll()).thenReturn(List.of());
        mockMvc.perform(get("/api/v1/knowledge/items"))
                .andExpect(status().isOk());
    }

    @Test void allElements_empty_returnsEmptyArray() throws Exception {
        when(elementPort.listAll()).thenReturn(List.of());
        mockMvc.perform(get("/api/v1/knowledge/elements"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$").isEmpty());
    }
}
