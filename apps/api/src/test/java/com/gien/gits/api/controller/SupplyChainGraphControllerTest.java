package com.gien.gits.api.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.api.dto.SupplyChainGraphExecuteRequest;
import com.gien.gits.api.dto.SupplyChainGraphInterpretation;
import com.gien.gits.api.dto.SupplyChainGraphReport;
import com.gien.gits.api.dto.SupplyChainGraphResult;
import com.gien.gits.api.service.SupplyChainGraphService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

/**
 * P24: SupplyChainGraphController WebMvc 契约测试（POST 执行 / GET 报告）。
 */
@WebMvcTest(SupplyChainGraphController.class)
@AutoConfigureMockMvc(addFilters = false)
class SupplyChainGraphControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;

    @MockitoBean SupplyChainGraphService supplyChainGraphService;
    @MockitoBean AuditLogPort auditLogPort;

    private SupplyChainGraphReport sampleReport() {
        SupplyChainGraphResult result = new SupplyChainGraphResult(
                "1.0", "ok", List.of(), List.of(),
                new SupplyChainGraphInterpretation(
                        "上游", "强", List.of(), "无重大变化", "整体稳健", List.of(), "HIGH"));
        return new SupplyChainGraphReport(
                "SCG-001", "C-1", "华东精工", "2026-08-24T00:00:00Z",
                "ok", "/supply-chain-report/SCG-001", result);
    }

    @Test
    void executeSupplyChainGraph_returnsOkReport() throws Exception {
        SupplyChainGraphReport report = sampleReport();
        when(supplyChainGraphService.execute(any(SupplyChainGraphExecuteRequest.class))).thenReturn(report);

        mockMvc.perform(post("/api/v1/engagement/supply-chain-graph")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(
                                new SupplyChainGraphExecuteRequest("C-1", "SCG-001"))))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.requestId").value("SCG-001"))
                .andExpect(jsonPath("$.status").value("ok"))
                .andExpect(jsonPath("$.result.buildStatus").value("ok"));

        verify(supplyChainGraphService).execute(any(SupplyChainGraphExecuteRequest.class));
    }

    @Test
    void getSupplyChainGraphReport_returnsReport() throws Exception {
        SupplyChainGraphReport report = sampleReport();
        when(supplyChainGraphService.getReport("SCG-001")).thenReturn(report);

        mockMvc.perform(get("/api/v1/engagement/supply-chain-graph/reports/{requestId}", "SCG-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.requestId").value("SCG-001"))
                .andExpect(jsonPath("$.customerName").value("华东精工"))
                .andExpect(jsonPath("$.result.schemaVersion").value("1.0"))
                .andExpect(jsonPath("$.result.interpretation.confidence").value("HIGH"));

        verify(supplyChainGraphService).getReport("SCG-001");
    }
}
