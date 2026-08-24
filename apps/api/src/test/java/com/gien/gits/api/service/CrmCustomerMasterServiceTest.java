package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.gien.gits.api.dto.CrmCustomerMaster;
import com.gien.gits.api.dto.CrmCustomerMasterReloadResponse;
import com.gien.gits.api.dto.CrmCustomerUpsertResponse;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.CustomerTier;
import com.gien.gits.ontology.EnterpriseScale;
import com.gien.gits.ontology.Industry;
import com.gien.gits.ontology.ListedStatus;
import com.gien.gits.ontology.RiskLevel;
import com.gien.gits.ontology.port.WritableCustomerRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.core.io.DefaultResourceLoader;

class CrmCustomerMasterServiceTest {

    @Mock private WritableCustomerRepository customerRepo;

    private CrmCustomerMasterService service;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        ObjectMapper mapper = JsonMapper.builder()
                .addModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
                .build();
        service = new CrmCustomerMasterService(
                customerRepo,
                mapper,
                new DefaultResourceLoader(),
                "docs/dd/fixtures/gits-crm-customer-master.json");
    }

    @Test
    void upsert_createsNewCustomer() {
        when(customerRepo.findById("CUST-NEW-1")).thenReturn(Optional.empty());

        CrmCustomerUpsertResponse response = service.upsert("CUST-NEW-1", master(
                "CUST-NEW-1", "新客户", "91330000NEW", "RM-ZW-001"));

        assertEquals("CUST-NEW-1", response.customerId());
        assertEquals("新客户", response.customerName());
        assertEquals("CREATED", response.status());
        verify(customerRepo).save(argThat(c ->
                "CUST-NEW-1".equals(c.customerId()) && "新客户".equals(c.customerName())));
        verify(customerRepo, never()).update(any());
    }

    @Test
    void upsert_updatesName_whenCreditCodeUnchanged() {
        Customer existing = existing("CUST-CORP-0001", "华东精工旧名", "91330000MA27DEMO");
        when(customerRepo.findById("CUST-CORP-0001")).thenReturn(Optional.of(existing));

        CrmCustomerUpsertResponse response = service.upsert("CUST-CORP-0001", master(
                "CUST-CORP-0001", "华东精工装备集团有限公司", "91330000MA27DEMO", "RM-ZW-001"));

        assertEquals("UPDATED", response.status());
        assertEquals("华东精工装备集团有限公司", response.customerName());
        verify(customerRepo).update(argThat(c ->
                "CUST-CORP-0001".equals(c.customerId())
                        && "华东精工装备集团有限公司".equals(c.customerName())
                        && "91330000MA27DEMO".equals(c.unifiedSocialCreditCode())));
        verify(customerRepo, never()).save(any());
    }

    @Test
    void upsert_creditCodeClash_throwsIllegalState() {
        Customer existing = existing("CUST-CORP-0001", "华东精工装备集团有限公司", "91330000MA27DEMO");
        when(customerRepo.findById("CUST-CORP-0001")).thenReturn(Optional.of(existing));

        assertThrows(IllegalStateException.class, () -> service.upsert(
                "CUST-CORP-0001",
                master("CUST-CORP-0001", "华东精工装备集团有限公司", "99999999CLASH", "RM-ZW-001")));
        verify(customerRepo, never()).update(any());
        verify(customerRepo, never()).save(any());
    }

    @Test
    void upsert_pathMismatch_throwsIllegalArgument() {
        assertThrows(IllegalArgumentException.class, () -> service.upsert(
                "CUST-A",
                master("CUST-B", "名称", "91330000MA27DEMO", "RM-ZW-001")));
        verify(customerRepo, never()).findById(any());
    }

    @Test
    void upsert_blankPath_throwsIllegalArgument() {
        assertThrows(IllegalArgumentException.class, () -> service.upsert(
                "  ",
                master("CUST-B", "名称", "91330000MA27DEMO", "RM-ZW-001")));
    }

    @Test
    void reloadFromFixture_upsertsPrimaryDemoCustomer() {
        when(customerRepo.findById(any())).thenReturn(Optional.empty());

        CrmCustomerMasterReloadResponse response = service.reloadFromFixture();

        assertTrue(response.upsertedCount() >= 1);
        assertTrue(response.customerIds().contains("CUST-CORP-0001"));
        verify(customerRepo, atLeastOnce()).save(argThat(c ->
                "CUST-CORP-0001".equals(c.customerId())
                        && "华东精工装备集团有限公司".equals(c.customerName())
                        && "RM-ZW-001".equals(c.rmId())));
        verify(customerRepo, never()).update(any());
    }

    @Test
    void toCustomer_defaultsNullNumericAndBoolean() {
        CrmCustomerMaster body = new CrmCustomerMaster(
                "CUST-NULL-1", "空值客户", null, null, null, null,
                null, null, null, null, null,
                "RM-ZW-001", "张伟", "杭州城西支行",
                null, null, null,
                List.of(), List.of(), null);

        Customer customer = service.toCustomer(
                body, Instant.parse("2026-01-01T00:00:00Z"), Instant.parse("2026-01-01T00:00:00Z"));

        assertEquals(0L, customer.registeredCapitalCny());
        assertFalse(customer.groupFlag());
        assertNull(customer.industry());
        assertNull(customer.enterpriseScale());
        assertNull(customer.customerTier());
        assertNull(customer.listedStatus());
        assertNull(customer.riskLevel());
    }

    @Test
    void toCustomer_invalidEnum_throwsIllegalArgument() {
        CrmCustomerMaster body = new CrmCustomerMaster(
                "CUST-BAD-1", "坏枚举客户", "短名", "91330000BAD", null, null,
                "NOT_A_REAL_INDUSTRY", "杭州", "LARGE", "STRATEGIC",
                null, "RM-ZW-001", "张伟", "杭州城西支行",
                true, "UNLISTED", "MEDIUM",
                List.of(), List.of(), "摘要");

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class,
                () -> service.toCustomer(body, Instant.now(), Instant.now()));
        assertEquals("Invalid Industry: NOT_A_REAL_INDUSTRY", ex.getMessage());
    }

    @Test
    void reloadFromFixture_missingFixture_returnsEmpty() {
        CrmCustomerMasterService svc = new CrmCustomerMasterService(
                customerRepo, new ObjectMapper(), new DefaultResourceLoader(),
                "__missing__/not-exists.json");

        CrmCustomerMasterReloadResponse response = svc.reloadFromFixture();

        assertEquals(0, response.upsertedCount());
        assertTrue(response.customerIds().isEmpty());
        verify(customerRepo, never()).save(any());
    }

    @Test
    void reloadFromFixture_notJson_throwsIllegalArgument() {
        ObjectMapper mapper = JsonMapper.builder()
                .addModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
                .build();
        CrmCustomerMasterService svc = new CrmCustomerMasterService(
                customerRepo, mapper, new DefaultResourceLoader(),
                "src/test/java/com/gien/gits/api/service/CrmCustomerMasterServiceTest.java");

        assertThrows(IllegalArgumentException.class, svc::reloadFromFixture);
        verify(customerRepo, never()).save(any());
    }

    @Test
    void reloadFromFixture_noCustomersArray_returnsEmpty() throws IOException {
        ObjectMapper mockMapper = mock(ObjectMapper.class);
        when(mockMapper.readTree(any(byte[].class)))
                .thenReturn(JsonNodeFactory.instance.objectNode());
        CrmCustomerMasterService svc = new CrmCustomerMasterService(
                customerRepo, mockMapper, new DefaultResourceLoader(),
                "docs/dd/fixtures/gits-crm-customer-master.json");

        CrmCustomerMasterReloadResponse response = svc.reloadFromFixture();

        assertEquals(0, response.upsertedCount());
        assertTrue(response.customerIds().isEmpty());
    }

    @Test
    void reloadFromFixture_customerMissingId_throwsIllegalArgument() throws IOException {
        ObjectMapper mockMapper = mock(ObjectMapper.class);
        ArrayNode customers = JsonNodeFactory.instance.arrayNode();
        customers.addObject();
        ObjectNode root = JsonNodeFactory.instance.objectNode();
        root.set("customers", customers);
        when(mockMapper.readTree(any(byte[].class))).thenReturn(root);
        CrmCustomerMasterService svc = new CrmCustomerMasterService(
                customerRepo, mockMapper, new DefaultResourceLoader(),
                "docs/dd/fixtures/gits-crm-customer-master.json");

        assertThrows(IllegalArgumentException.class, svc::reloadFromFixture);
    }

    private static CrmCustomerMaster master(String id, String name, String credit, String rmId) {
        return new CrmCustomerMaster(
                id, name, "短名", credit,
                LocalDate.of(2005, 3, 15), 500000000L,
                "MANUFACTURING", "浙江省杭州市",
                "LARGE", "STRATEGIC",
                LocalDate.of(2018, 6, 1),
                rmId, "张伟", "杭州城西支行",
                true, "UNLISTED", "MEDIUM",
                List.of("精密加工"), List.of("制造业"),
                "摘要");
    }

    private static Customer existing(String id, String name, String credit) {
        return new Customer(
                id, name, "短名", credit,
                LocalDate.of(2005, 3, 15), 500000000L,
                Industry.MANUFACTURING, "浙江省杭州市",
                EnterpriseScale.LARGE, CustomerTier.STRATEGIC,
                LocalDate.of(2018, 6, 1),
                "RM-ZW-001", "张伟", "杭州城西支行",
                true, ListedStatus.UNLISTED, RiskLevel.MEDIUM,
                List.of(), List.of(), "旧摘要",
                Instant.parse("2020-01-01T00:00:00Z"), Instant.parse("2020-01-01T00:00:00Z"));
    }
}
