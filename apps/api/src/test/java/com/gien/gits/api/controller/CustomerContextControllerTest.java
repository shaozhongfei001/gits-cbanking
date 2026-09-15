package com.gien.gits.api.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.dto.SkillReportSection;
import com.gien.gits.api.service.CustomerContextService;
import com.gien.gits.api.service.KnowledgeDrivenPrevisitReportGenerator;
import com.gien.gits.api.service.ProductMatchingService;
import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.action.port.AuditLogPort;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.port.TransactionRepository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(CustomerContextController.class)
@AutoConfigureMockMvc(addFilters = false)
class CustomerContextControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;

    @MockitoBean CustomerContextService customerContextService;
    @MockitoBean TransactionRepository transactionRepo;
    @MockitoBean ProductMatchingService productMatchingService;
    @MockitoBean KnowledgeDrivenPrevisitReportGenerator knowledgeDrivenPrevisitReportGenerator;
    @MockitoBean AuditLogPort auditLogPort;

    private Customer sampleCustomer() {
        return new Customer("CUST-001", "Test Customer", null, null, null,
            0, null, null, null, null, null, "RM-001", "RM Name", "Branch",
            false, null, null, List.of(), List.of(), null);
    }

    private CustomerContextService.CustomerOperatingView sampleView() {
        return new CustomerContextService.CustomerOperatingView(
            sampleCustomer(), List.of(), List.of(), Optional.empty(), List.of(), List.of());
    }

    @Test
    void testGetOperatingView() throws Exception {
        when(customerContextService.buildOperatingView("CUST-001")).thenReturn(sampleView());

        mockMvc.perform(get("/api/v1/engagement/customer/{customerId}/operating-view", "CUST-001"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.customer.customerId").value("CUST-001"));
    }

    @Test
    void testCreateCustomer() throws Exception {
        Customer customer = sampleCustomer();

        mockMvc.perform(post("/api/v1/engagement/customer")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(customer)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.customerId").value("CUST-001"))
            .andExpect(jsonPath("$.status").value("CREATED"));

        verify(customerContextService).saveCustomer(any(Customer.class));
    }

    @Test
    void testListCustomersByRm() throws Exception {
        when(customerContextService.findCustomersByRm("RM-001")).thenReturn(List.of());

        mockMvc.perform(get("/api/v1/engagement/customer")
                .param("rmId", "RM-001"))
            .andExpect(status().isOk());
    }

    @Test
    void testGetTransactions() throws Exception {
        when(transactionRepo.findByCustomerId("CUST-001")).thenReturn(List.of());

        mockMvc.perform(get("/api/v1/engagement/customer/{customerId}/transactions", "CUST-001"))
            .andExpect(status().isOk());
    }

    @Test
    void testGetTransactionsWithLimit() throws Exception {
        when(transactionRepo.findRecentByCustomerId("CUST-001", 5)).thenReturn(List.of());

        mockMvc.perform(get("/api/v1/engagement/customer/{customerId}/transactions", "CUST-001")
                .param("limit", "5"))
            .andExpect(status().isOk());
    }

    @Test
    void testMatchProducts() throws Exception {
        when(productMatchingService.matchProducts("CUST-001")).thenReturn(List.of());

        mockMvc.perform(post("/api/v1/engagement/customer/{customerId}/product-matching", "CUST-001"))
            .andExpect(status().isOk());
    }

    @Test
    void assembledKnowledgeMap_returnsSkillSectionsNotGitSnapshot() throws Exception {
        PrevisitReportContent emptyReport = new PrevisitReportContent(
                "R1-x", "CUST-001", "", "", "", null,
                new PrevisitReportContent.KycGapSummary(List.of(), List.of(), List.of(), List.of()),
                List.of(), List.of(), List.of(), "");
        when(knowledgeDrivenPrevisitReportGenerator.generate("CUST-001", ""))
                .thenReturn(new KnowledgeDrivenPrevisitReportGenerator.GenerationResult(
                        emptyReport,
                        List.of(),
                        "DKWS 知识地图",
                        "按客户装配",
                        List.of(new SkillReportSection("KI-009 企业客户基本信息", "行业：制造"))));

        mockMvc.perform(get("/api/v1/engagement/customer/{customerId}/knowledge-map", "CUST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customerId").value("CUST-001"))
                .andExpect(jsonPath("$.skillReportTitle").value("DKWS 知识地图"))
                .andExpect(jsonPath("$.skillSections[0].heading").value("KI-009 企业客户基本信息"))
                .andExpect(jsonPath("$.skillSections[0].content").value("行业：制造"));
    }

    @Test
    void assembledKnowledgeMap_emptyWhenDkwsDown() throws Exception {
        PrevisitReportContent emptyReport = new PrevisitReportContent(
                "R1-x", "CUST-001", "", "", "", null,
                new PrevisitReportContent.KycGapSummary(List.of(), List.of(), List.of(), List.of()),
                List.of(), List.of(), List.of(), "");
        when(knowledgeDrivenPrevisitReportGenerator.generate("CUST-001", ""))
                .thenReturn(new KnowledgeDrivenPrevisitReportGenerator.GenerationResult(
                        emptyReport,
                        List.of(),
                        null,
                        null,
                        List.of()));

        mockMvc.perform(get("/api/v1/engagement/customer/{customerId}/knowledge-map", "CUST-001"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.skillSections").isArray())
                .andExpect(jsonPath("$.skillSections").isEmpty())
                .andExpect(jsonPath("$.assemblyTrace").isArray());
    }
}
