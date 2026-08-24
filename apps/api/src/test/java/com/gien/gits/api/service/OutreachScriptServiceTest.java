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

import com.gien.gits.engagement.OutreachScript;
import com.gien.gits.engagement.OutreachScript.OutreachChannel;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import com.gien.gits.engagement.port.WritableOutreachScriptRepository;
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

class OutreachScriptServiceTest {

    private CustomerContextService customerContextService;
    private WritableOutreachScriptRepository scriptRepo;
    private SkillExecutionPort skillExecutionPort;
    private OutreachScriptService service;
    private Customer seedCustomer;

    @BeforeEach
    void setUp() {
        customerContextService = mock(CustomerContextService.class);
        scriptRepo = mock(WritableOutreachScriptRepository.class);
        skillExecutionPort = mock(SkillExecutionPort.class);
        service = new OutreachScriptService(customerContextService, scriptRepo, skillExecutionPort);
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
    void requestCarriesCustomerIdAndChannelWithoutLocalFacts() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenThrow(new SkillExecutionException("dsh down"));

        service.generateScript("CUST-001", "RM-001", "case-001", "journey-001", OutreachChannel.PHONE);

        ArgumentCaptor<SkillExecutionCommand> captor = ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillExecutionPort).execute(captor.capture());
        SkillExecutionCommand command = captor.getValue();
        assertEquals(OutreachScriptService.OUTREACH_SKILL_ID, command.skillId());
        Map<String, Object> request = command.request();
        assertEquals("CUST-001", request.get("customerId"));
        assertEquals("PHONE", request.get("channel"));
        assertFalse(request.containsKey("structuredFacts"));
        assertFalse(request.containsKey("knowledgeContext"));
        assertFalse(request.containsKey("kyc"));
        assertFalse(request.containsKey("visitGoals"));
    }

    @Test
    void skillOkMapsSectionsAndObjectives() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenReturn(new SkillExecutionResult(
                        SkillExecutionStatus.OK, "REQ-1",
                        Map.of(
                                "scriptTitle", "约访华东精工",
                                "callObjectives", List.of("确认周四下午是否方便"),
                                "keyMessages", List.of("张总您好，打扰两分钟。"),
                                "sections", List.of(
                                        Map.of("heading", "约访", "content", "确认周四下午"),
                                        Map.of("heading", "风险提醒", "content", "勿承诺额度"),
                                        Map.of("heading", "收口", "content", "您看周四还是周五？"),
                                        Map.of("heading", "后续", "content", "发日历邀请"))),
                        List.of(), List.of(), List.of()));

        OutreachScript script = service.generateScript(
                "CUST-001", "RM-001", "case-001", "journey-001", OutreachChannel.WECHAT);

        assertEquals("确认周四下午是否方便", script.objective());
        assertEquals("张总您好，打扰两分钟。", script.openingLine());
        assertEquals(4, script.talkingPoints().size());
        assertEquals("约访", script.talkingPoints().get(0).topic());
        assertEquals("确认周四下午", script.talkingPoints().get(0).detail());
        assertEquals("", script.talkingPoints().get(0).suggestedQuestion());
        assertTrue(script.riskReminders().contains("勿承诺额度"));
        assertEquals("您看周四还是周五？", script.closingLine());
        assertEquals("发日历邀请", script.followUpAction());
        assertEquals("WECHAT", script.channel().name());
        verify(scriptRepo).save(script);
    }

    @Test
    void skillDownPersistsEmptyFieldsWithoutSeedPhrases() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenThrow(new SkillExecutionException("dsh down"));

        OutreachScript script = service.generateScript(
                "CUST-001", "RM-001", "case-001", "journey-001", OutreachChannel.PHONE);

        assertTrue(script.scriptId().startsWith("OS-"));
        assertEquals("CUST-001", script.customerId());
        assertEquals("RM-001", script.rmId());
        assertEquals("", script.objective());
        assertEquals("", script.openingLine());
        assertTrue(script.talkingPoints().isEmpty());
        assertTrue(script.riskReminders().isEmpty());
        assertEquals("", script.closingLine());
        assertEquals("", script.followUpAction());
        assertFalse(script.openingLine().contains("华东精工"));
        assertFalse(script.objective().contains("华东精工"));
        verify(scriptRepo).save(script);
    }

    @Test
    void skillErrorPersistsEmptyScript() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenReturn(new SkillExecutionResult(
                        SkillExecutionStatus.SKILL_ERROR, "REQ-E", Map.of(),
                        List.of(), List.of(), List.of()));

        OutreachScript script = service.generateScript(
                "CUST-001", "", "case-001", "journey-001", OutreachChannel.EMAIL);

        assertEquals("UNSET", script.rmId());
        assertEquals("", script.openingLine());
        assertTrue(script.talkingPoints().isEmpty());
        verify(scriptRepo).save(script);
    }

    @Test
    void customerNotFoundThrowsAndDoesNotCallSkill() {
        when(customerContextService.findCustomer("CUST-UNKNOWN")).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () ->
                service.generateScript("CUST-UNKNOWN", "RM-001", "case-001", "journey-001", OutreachChannel.PHONE));

        verifyNoInteractions(skillExecutionPort);
        verify(scriptRepo, never()).save(any());
    }
}
