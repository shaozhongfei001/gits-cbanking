package com.gien.gits.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.adapter.skill.ServiceProposalMapper;
import com.gien.gits.engagement.port.ServiceProposal;
import com.gien.gits.engagement.port.ServiceProposalCommand;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import com.gien.gits.ontology.CreditFacility;
import com.gien.gits.ontology.Customer;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class ServiceProposalServiceTest {

    private static final String CUSTOMER_ID = "CUST-CORP-0001";

    @Mock
    private SkillExecutionPort skillExecutionPort;
    @Mock
    private ServiceProposalMapper mapper;
    @Mock
    private CustomerContextService customerContextService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    private ServiceProposalService service() {
        return new ServiceProposalService(skillExecutionPort, mapper, objectMapper, customerContextService);
    }

    private void stubOkExecution() {
        when(skillExecutionPort.execute(any())).thenReturn(new SkillExecutionResult(
            SkillExecutionStatus.OK, "rid",
            Map.of("result", Map.of()),
            List.of(), List.of(), List.of()));
        when(mapper.fromResult(any())).thenReturn(ServiceProposal.empty());
    }

    @Test
    void contextComplete_shouldPassthroughWithoutCustomerLookup() {
        Map<String, Object> complete = Map.of(
            "customerId", "CUST-X",
            "customerName", "客户X",
            "industry", "制造业",
            "enterpriseData", Map.of("basicInfo", Map.of()));
        stubOkExecution();

        service().generate(new ServiceProposalCommand("r1", "CUST-X", complete));

        verify(customerContextService, never()).findCustomer(any());
        ArgumentCaptor<SkillExecutionCommand> captor =
            ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillExecutionPort).execute(captor.capture());
        assertThat(captor.getValue().context()).isEqualTo(complete);
    }

    @Test
    void incompleteContext_shouldEnrichFromCustomerMaster() {
        Customer customer = new Customer(
            CUSTOMER_ID, "华东精工装备集团有限公司", "华东精工", "9133010077466XXXXX",
            LocalDate.of(2005, 3, 15), 500_000_000L, "MANUFACTURING", "浙江省杭州市",
            null, null, null, "RM-001", "张伟", "杭州分行",
            false, null, null, List.of("精密加工", "智能装备"), List.of(), "深耕客户");
        when(customerContextService.findCustomer(CUSTOMER_ID)).thenReturn(Optional.of(customer));
        when(customerContextService.buildOperatingView(CUSTOMER_ID))
            .thenReturn(new CustomerContextService.CustomerOperatingView(
                customer, List.of(), List.of(), Optional.empty(),
                List.of(new CreditFacility(
                    "CF-001", CUSTOMER_ID, "华东精工装备集团", LocalDate.of(2024, 1, 1),
                    LocalDate.of(2026, 1, 1), 80_000_000L, 55_000_000L, 25_000_000L,
                    55_000_000L, 0L, 0L, "厂房抵押",
                    List.of("流动资金"), List.of(), List.of(), null, null)),
                List.of()));
        stubOkExecution();

        service().generate(new ServiceProposalCommand(
            "r2", CUSTOMER_ID, Map.of("customerVersionLabel", "内部")));

        ArgumentCaptor<SkillExecutionCommand> captor =
            ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillExecutionPort).execute(captor.capture());
        Map<String, Object> ctx = captor.getValue().context();
        assertThat(ctx.get("customerId")).isEqualTo(CUSTOMER_ID);
        assertThat(ctx.get("customerName")).isEqualTo("华东精工装备集团有限公司");
        assertThat(ctx.get("industry")).isEqualTo("制造业");
        assertThat(ctx.get("schemaVersion")).isEqualTo("1.0.0");
        assertThat(ctx.get("customerVersionLabel")).isEqualTo("内部");
        assertThat(ctx).doesNotContainKey("financialSummary");
        @SuppressWarnings("unchecked")
        Map<String, Object> enterpriseData = (Map<String, Object>) ctx.get("enterpriseData");
        assertThat(enterpriseData).containsKey("basicInfo");
        @SuppressWarnings("unchecked")
        Map<String, Object> creditFacility =
            (Map<String, Object>) enterpriseData.get("creditFacility");
        assertThat(creditFacility.get("totalApproved")).isEqualTo(80_000_000L);
        assertThat(creditFacility.get("totalUsed")).isEqualTo(55_000_000L);
        @SuppressWarnings("unchecked")
        Map<String, Object> proposalContext = (Map<String, Object>) ctx.get("proposalContext");
        assertThat(proposalContext.get("proposalType")).isEqualTo("INITIAL");
    }

    @Test
    void customerMissing_shouldPassthroughOriginalContext() {
        when(customerContextService.findCustomer(CUSTOMER_ID)).thenReturn(Optional.empty());
        stubOkExecution();

        service().generate(new ServiceProposalCommand(
            "r3", CUSTOMER_ID, Map.of("customerVersionLabel", "内部")));

        ArgumentCaptor<SkillExecutionCommand> captor =
            ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillExecutionPort).execute(captor.capture());
        assertThat(captor.getValue().context()).isEqualTo(Map.of("customerVersionLabel", "内部"));
    }
}
