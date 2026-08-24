package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.CustomerTier;
import com.gien.gits.ontology.EnterpriseScale;
import com.gien.gits.ontology.Industry;
import com.gien.gits.ontology.ListedStatus;
import com.gien.gits.ontology.RiskLevel;
import com.gien.gits.ontology.port.CustomerRepository;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class ProductMatchingServiceTest {

    private SkillExecutionPort skillExecutionPort;
    private CustomerRepository customerRepo;
    private ProductMatchingService service;

    @BeforeEach
    void setUp() {
        skillExecutionPort = mock(SkillExecutionPort.class);
        customerRepo = mock(CustomerRepository.class);
        service = new ProductMatchingService(skillExecutionPort, customerRepo);
        when(customerRepo.findById("CUST-001")).thenReturn(Optional.of(createTestCustomer()));
    }

    private Customer createTestCustomer() {
        return new Customer(
            "CUST-001", "华东精工", "华东精工制造有限公司",
            "91330000MA27DEMO", LocalDate.of(2005, 3, 15), 50000000L,
            Industry.MANUFACTURING.name(), "浙江省",
            EnterpriseScale.LARGE.name(), CustomerTier.STRATEGIC.name(),
            LocalDate.of(2018, 1, 1), "RM-001", "张经理", "杭州分行",
            false, ListedStatus.UNLISTED.name(), RiskLevel.MEDIUM.name(),
            List.of("精密制造"), List.of("战略客户"), "长期合作");
    }

    @Test
    void requestCarriesCustomerIdWithoutLocalFacts() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
            .thenThrow(new SkillExecutionException("dsh down"));

        service.matchProducts("CUST-001");

        ArgumentCaptor<SkillExecutionCommand> captor = ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillExecutionPort).execute(captor.capture());
        SkillExecutionCommand command = captor.getValue();
        assertEquals(ProductMatchingService.SKILL_ID, command.skillId());
        Map<String, Object> request = command.request();
        assertEquals("CUST-001", request.get("customerId"));
        assertEquals(1, request.size());
        assertFalse(request.containsKey("structuredFacts"));
        assertFalse(request.containsKey("knowledgeContext"));
        assertFalse(request.containsKey("transactions"));
        assertFalse(request.containsKey("kyc"));
    }

    @Test
    void skillProductsMapsNames() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
            .thenReturn(new SkillExecutionResult(
                SkillExecutionStatus.OK, "REQ-1",
                Map.of("products", List.of(
                    Map.of("productId", "P-DKWS-1", "productName", "DKWS设备贷",
                            "reason", "设备更新窗口", "confidence", 80, "signal", "DKWS"),
                    Map.of("name", "DKWS票据通", "matchReason", "应收集中", "matchScore", 0.6))),
                List.of(), List.of(), List.of()));

        var matches = service.matchProducts("CUST-001");

        assertEquals(2, matches.size());
        assertEquals("P-DKWS-1", matches.get(0).productId());
        assertEquals("DKWS设备贷", matches.get(0).productName());
        assertEquals("设备更新窗口", matches.get(0).reason());
        assertEquals(0.8, matches.get(0).confidence());
        assertEquals("DKWS", matches.get(0).signal());
        assertEquals("PROD-DKWS-2", matches.get(1).productId());
        assertEquals("DKWS票据通", matches.get(1).productName());
        assertEquals("应收集中", matches.get(1).reason());
        assertEquals(0.6, matches.get(1).confidence());
        assertFalse(matches.stream().anyMatch(m -> m.productName().contains("流动资金贷款")));
        assertFalse(matches.stream().anyMatch(m -> m.productName().contains("供应链融资")));
    }

    @Test
    void skillDownReturnsEmptyWithoutSeedProducts() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
            .thenThrow(new SkillExecutionException("dsh down"));

        var matches = service.matchProducts("CUST-001");

        assertTrue(matches.isEmpty());
        assertFalse(matches.stream().anyMatch(m -> m.productName().contains("流动资金贷款")));
        assertFalse(matches.stream().anyMatch(m -> m.productName().contains("供应链融资")));
    }

    @Test
    void skillErrorReturnsEmptyWithoutSeedProducts() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
            .thenReturn(new SkillExecutionResult(
                SkillExecutionStatus.SKILL_ERROR, "REQ-ERR",
                Map.of(),
                List.of(new SkillExecutionResult.ErrorItem("DKWS_REQUIRED", "须由 DKWS Skill 取数")),
                List.of(), List.of()));

        var matches = service.matchProducts("CUST-001");

        assertTrue(matches.isEmpty());
        assertFalse(matches.stream().anyMatch(m -> m.productName().contains("流动资金贷款")));
        assertFalse(matches.stream().anyMatch(m -> m.productName().contains("供应链融资")));
    }

    @Test
    void unknownCustomerReturnsEmptyWithoutCallingSkill() {
        when(customerRepo.findById("CUST-UNKNOWN")).thenReturn(Optional.empty());

        var matches = service.matchProducts("CUST-UNKNOWN");

        assertTrue(matches.isEmpty());
        verify(skillExecutionPort, never()).execute(any(SkillExecutionCommand.class));
    }
}
