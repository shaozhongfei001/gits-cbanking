package com.gien.gits.api.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.dto.CrmCustomerMaster;
import com.gien.gits.api.dto.CrmCustomerMasterReloadResponse;
import com.gien.gits.api.dto.CrmCustomerUpsertResponse;
import com.gien.gits.api.service.CrmCustomerMasterService;
import com.gien.gits.api.service.CustomerContextService;
import com.gien.gits.api.service.ProductMatchingService;
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
    @MockitoBean CrmCustomerMasterService crmCustomerMasterService;
    @MockitoBean TransactionRepository transactionRepo;
    @MockitoBean ProductMatchingService productMatchingService;
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
    void upsertCrmCustomer_returnsCreatedThenUpdated() throws Exception {
        CrmCustomerMaster body = new CrmCustomerMaster(
                "CUST-CORP-0001", "华东精工装备集团有限公司", "华东精工集团",
                "91330000MA27DEMO", null, 500000000L,
                "MANUFACTURING", "浙江省杭州市", "LARGE", "STRATEGIC",
                null, "RM-ZW-001", "张伟", "杭州城西支行",
                true, "UNLISTED", "MEDIUM", List.of(), List.of(), "摘要");

        when(crmCustomerMasterService.upsert(eq("CUST-CORP-0001"), any(CrmCustomerMaster.class)))
                .thenReturn(new CrmCustomerUpsertResponse(
                        "CUST-CORP-0001", "华东精工装备集团有限公司", "CREATED"))
                .thenReturn(new CrmCustomerUpsertResponse(
                        "CUST-CORP-0001", "华东精工装备集团有限公司", "UPDATED"));

        mockMvc.perform(put("/api/v1/engagement/customer/{customerId}", "CUST-CORP-0001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customerId").value("CUST-CORP-0001"))
                .andExpect(jsonPath("$.status").value("CREATED"));

        mockMvc.perform(put("/api/v1/engagement/customer/{customerId}", "CUST-CORP-0001")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(body)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.customerId").value("CUST-CORP-0001"))
                .andExpect(jsonPath("$.status").value("UPDATED"));
    }

    @Test
    void reloadCrmCustomerMaster_returnsOk() throws Exception {
        when(crmCustomerMasterService.reloadFromFixture())
                .thenReturn(new CrmCustomerMasterReloadResponse(
                        3, List.of("CUST-CORP-0001", "CUST-CORP-0002", "CUST-CORP-0003")));

        mockMvc.perform(post("/api/v1/engagement/crm-customer-master/reload"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.upsertedCount").value(3))
                .andExpect(jsonPath("$.customerIds[0]").value("CUST-CORP-0001"));
    }
}
