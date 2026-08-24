package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.gien.gits.engagement.MeetingScript;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import com.gien.gits.engagement.port.WritableMeetingScriptRepository;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.CustomerTier;
import com.gien.gits.ontology.EnterpriseScale;
import com.gien.gits.ontology.Industry;
import com.gien.gits.ontology.ListedStatus;
import com.gien.gits.ontology.RiskLevel;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class MeetingScriptServiceTest {

    private CustomerContextService customerContextService;
    private WritableMeetingScriptRepository scriptRepo;
    private SkillExecutionPort skillExecutionPort;
    private MeetingScriptService service;
    private Customer seedCustomer;

    @BeforeEach
    void setUp() {
        customerContextService = mock(CustomerContextService.class);
        scriptRepo = mock(WritableMeetingScriptRepository.class);
        skillExecutionPort = mock(SkillExecutionPort.class);
        service = new MeetingScriptService(customerContextService, scriptRepo, skillExecutionPort);
        seedCustomer = new Customer(
                "CUST-001", "华东精工", "华东精工制造有限公司",
                "91330000MA27DEMO", LocalDate.of(2005, 3, 15), 50000000L,
                Industry.MANUFACTURING.name(), "浙江省",
                EnterpriseScale.LARGE.name(), CustomerTier.STRATEGIC.name(),
                LocalDate.of(2018, 1, 1), "RM-001", "张经理", "杭州分行",
                false, ListedStatus.UNLISTED.name(), RiskLevel.MEDIUM.name(),
                List.of("精密制造"), List.of("战略客户"), "长期合作");
        when(customerContextService.findCustomer("CUST-001")).thenReturn(Optional.of(seedCustomer));
    }

    @Test
    void requestCarriesOnlyCustomerIdWithoutLocalFacts() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenThrow(new SkillExecutionException("dsh down"));

        service.generateScript("CUST-001", "RM-001", "case-001", "journey-001");

        ArgumentCaptor<SkillExecutionCommand> captor = ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillExecutionPort).execute(captor.capture());
        SkillExecutionCommand command = captor.getValue();
        assertEquals(MeetingScriptService.MEETING_SKILL_ID, command.skillId());
        Map<String, Object> request = command.request();
        assertEquals("CUST-001", request.get("customerId"));
        assertEquals(1, request.size());
        assertFalse(request.containsKey("structuredFacts"));
        assertFalse(request.containsKey("knowledgeContext"));
        assertFalse(request.containsKey("kyc"));
        assertFalse(request.containsKey("visitGoals"));
        assertFalse(request.containsKey("channel"));
    }

    @Test
    void skillOkMapsAgendaAndTalkingPoints() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenReturn(new SkillExecutionResult(
                        SkillExecutionStatus.OK, "REQ-1",
                        Map.of(
                                "talkingPoints", List.of(
                                        Map.of("title", "开场对齐目标", "detail", "确认本周融资节奏"),
                                        Map.of("title", "KYC核实", "detail", "实际控制人是否变更？"),
                                        Map.of("title", "产品方案", "detail", "从账期切入供应链融资")),
                                "agenda", List.of(
                                        Map.of("time", "5分钟", "topic", "开场"),
                                        Map.of("time", "15分钟", "topic", "KYC核实"),
                                        Map.of("time", "20分钟", "topic", "产品方案")),
                                "sensitivePoints", List.of("勿承诺未批额度"),
                                "actionItems", List.of("会后纪要", "确认补件清单")),
                        List.of(), List.of(), List.of()));

        MeetingScript script = service.generateScript("CUST-001", "RM-001", "case-001", "journey-001");

        assertEquals("开场对齐目标", script.meetingObjective());
        assertEquals("", script.previsitSummary());
        assertEquals(3, script.agendaItems().size());
        assertEquals("KYC核实", script.agendaItems().get(1).topic());
        assertEquals(0, script.agendaItems().get(1).durationMinutes());
        assertEquals("15分钟", script.agendaItems().get(1).keyPoints());
        assertEquals("", script.agendaItems().get(1).expectedOutcome());
        assertEquals(1, script.kycQuestions().size());
        assertEquals("实际控制人是否变更？", script.kycQuestions().get(0).question());
        assertEquals(1, script.productDiscussions().size());
        assertEquals("产品方案", script.productDiscussions().get(0).productName());
        assertTrue(script.riskPoints().contains("勿承诺未批额度"));
        assertEquals("会后纪要；确认补件清单", script.closingSummary());
        verify(scriptRepo).save(script);
    }

    @Test
    void skillDownPersistsEmptyFieldsWithoutSeedPhrases() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenThrow(new SkillExecutionException("dsh down"));

        MeetingScript script = service.generateScript("CUST-001", "RM-001", "case-001", "journey-001");

        assertTrue(script.scriptId().startsWith("MS-"));
        assertEquals("CUST-001", script.customerId());
        assertEquals("", script.meetingObjective());
        assertEquals("", script.previsitSummary());
        assertTrue(script.agendaItems().isEmpty());
        assertTrue(script.kycQuestions().isEmpty());
        assertTrue(script.productDiscussions().isEmpty());
        assertTrue(script.riskPoints().isEmpty());
        assertEquals("", script.closingSummary());
        assertFalse(script.meetingObjective().contains("华东精工"));
        verify(scriptRepo).save(script);
    }

    @Test
    void skillErrorPersistsEmptyScriptWithUnsetRmId() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenReturn(new SkillExecutionResult(
                        SkillExecutionStatus.SKILL_ERROR, "REQ-E", Map.of(),
                        List.of(), List.of(), List.of()));

        MeetingScript script = service.generateScript("CUST-001", "  ", "case-001", "journey-001");

        assertEquals("UNSET", script.rmId());
        assertTrue(script.agendaItems().isEmpty());
        verify(scriptRepo).save(script);
    }

    @Test
    void customerNotFoundThrowsAndDoesNotCallSkill() {
        when(customerContextService.findCustomer("CUST-UNKNOWN")).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () ->
                service.generateScript("CUST-UNKNOWN", "RM-001", "case-001", "journey-001"));

        verifyNoInteractions(skillExecutionPort);
        verify(scriptRepo, never()).save(any());
    }
}
