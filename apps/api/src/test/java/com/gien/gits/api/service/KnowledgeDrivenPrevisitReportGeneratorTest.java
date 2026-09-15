package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class KnowledgeDrivenPrevisitReportGeneratorTest {

    private SkillExecutionPort skillExecutionPort;
    private KnowledgeDrivenPrevisitReportGenerator generator;

    @BeforeEach
    void setUp() {
        skillExecutionPort = mock(SkillExecutionPort.class);
        generator = new KnowledgeDrivenPrevisitReportGenerator(skillExecutionPort);
    }

    @Test
    void requestCarriesOnlyIdentityNotLocalFacts() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenThrow(new SkillExecutionException("dsh down"));

        generator.generate("CUST-001", "设备融资");

        ArgumentCaptor<SkillExecutionCommand> captor = ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillExecutionPort).execute(captor.capture());
        Map<String, Object> request = captor.getValue().request();
        assertEquals("CUST-001", request.get("customerId"));
        assertTrue(request.containsKey("evidenceTimestamp"));
        assertEquals("设备融资", request.get("visitObjective"));
        assertTrue(!request.containsKey("structuredFacts"));
        assertTrue(!request.containsKey("knowledgeContext"));
        assertTrue(!request.containsKey("supplyChainMarkdown"));
    }

    @Test
    void dshOkMapsSectionsWithoutLocalSeed() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenReturn(new SkillExecutionResult(
                        SkillExecutionStatus.OK, "REQ-1",
                        Map.of("reportTitle", "访前报告",
                                "executiveSummary", "以供应链金融切入，核对应收账期。",
                                "sections", List.of(
                                        Map.of("heading", "KI-009 企业客户基本信息", "content", "行业：制造"),
                                        Map.of("heading", "关键问题", "content", "确认核心供应商账期"))),
                        List.of(), List.of(), List.of()));

        var generated = generator.generate("CUST-001", "设备融资");
        PrevisitReportContent result = generated.report();

        assertEquals("以供应链金融切入，核对应收账期。", result.visitStrategy());
        assertTrue(result.keyQuestions().contains("确认核心供应商账期"));
        assertNull(result.customerOverview());
        assertTrue(result.productSchemes().isEmpty());
        assertEquals(2, generated.skillSections().size());
    }

    @Test
    void dshDownDoesNotFillFromLocalSeed() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenThrow(new SkillExecutionException("dsh down"));

        var generated = generator.generate("CUST-001", "设备融资");

        assertNull(generated.report().customerOverview());
        assertTrue(generated.report().visitStrategy() == null || generated.report().visitStrategy().isBlank());
        assertEquals("dkws", generated.assemblyTrace().get(0).phase());
        assertEquals("failed", generated.assemblyTrace().get(0).status());
    }

    @Test
    void dshOkForwardsAssemblyTrace() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class)))
                .thenReturn(new SkillExecutionResult(
                        SkillExecutionStatus.OK, "REQ-1",
                        Map.of("executiveSummary", "策略"),
                        List.of(),
                        List.of(new SkillExecutionResult.TraceStep("resolve", "ok", "定位 skill"),
                                new SkillExecutionResult.TraceStep("evidence", "skipped", "无知识", "KI-FRONT-002")),
                        List.of()));

        var generated = generator.generate("CUST-001", "设备融资");

        assertEquals(2, generated.assemblyTrace().size());
        assertEquals("KI-FRONT-002", generated.assemblyTrace().get(1).kiId());
        assertEquals("策略", generated.skillExecutiveSummary());
        assertTrue(generated.skillSections().isEmpty());
    }
}
