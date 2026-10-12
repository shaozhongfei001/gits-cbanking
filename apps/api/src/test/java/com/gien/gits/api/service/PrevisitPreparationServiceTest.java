package com.gien.gits.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.util.List;

import com.gien.gits.api.dto.SkillReportSection;
import com.gien.gits.engagement.MeetingScript;
import com.gien.gits.engagement.OutreachScript;
import com.gien.gits.engagement.OutreachScript.OutreachChannel;
import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.engagement.QuickBattleCard;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.api.service.EngagementOrchestrator.PrevisitWorkflowResult;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

/**
 * P24: PrevisitPreparationService 单元测试（fail-closed 参数校验 + 三依赖编排）。
 */
class PrevisitPreparationServiceTest {

    @Mock private OutreachScriptService outreachScriptService;
    @Mock private MeetingScriptService meetingScriptService;
    @Mock private EngagementOrchestrator orchestrator;

    private PrevisitPreparationService service;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        service = new PrevisitPreparationService(outreachScriptService, meetingScriptService, orchestrator);
    }

    @Test
    void prepare_nullJourneyId_throwsNpe() {
        assertThatThrownBy(() -> service.prepare(null, "C-1", "RM-1", "OC-1", "目标", OutreachChannel.PHONE))
                .isInstanceOf(NullPointerException.class)
                .hasMessage("journeyId");
    }

    @Test
    void prepare_nullCustomerId_throwsNpe() {
        assertThatThrownBy(() -> service.prepare("J-1", null, "RM-1", "OC-1", "目标", OutreachChannel.PHONE))
                .isInstanceOf(NullPointerException.class)
                .hasMessage("customerId");
    }

    @Test
    void prepare_nullOperatingCaseId_throwsNpe() {
        assertThatThrownBy(() -> service.prepare("J-1", "C-1", "RM-1", null, "目标", OutreachChannel.PHONE))
                .isInstanceOf(NullPointerException.class)
                .hasMessage("operatingCaseId");
    }

    @Test
    void prepare_delegatesInOrderAndAssemblesPrevisit() {
        OutreachScript outreach = new OutreachScript(
                "OS-1", "C-1", "RM-1", "OC-1", "J-1", OutreachChannel.PHONE,
                "目标", "开场", List.of(), List.of(), "收尾", "跟进", Instant.parse("2026-08-24T00:00:00Z"));
        MeetingScript meeting = new MeetingScript(
                "MS-1", "C-1", "RM-1", "OC-1", "J-1",
                "目标", "摘要", List.of(), List.of(), List.of(), List.of(), "收尾", Instant.parse("2026-08-24T00:00:00Z"));
        List<SkillExecutionResult.TraceStep> trace = List.of(
                new SkillExecutionResult.TraceStep("init", "OK", "初始化", "KI-001"));
        List<SkillReportSection> sections = List.of(new SkillReportSection("行业定位", "上游以制造业为主"));
        PrevisitWorkflowResult previsit = new PrevisitWorkflowResult(
                mock(PrevisitReportContent.class), mock(QuickBattleCard.class),
                trace, "R1 访前报告", "摘要", sections);

        when(outreachScriptService.generateScript("C-1", "RM-1", "OC-1", "J-1", OutreachChannel.PHONE))
                .thenReturn(outreach);
        when(meetingScriptService.generateScript("C-1", "RM-1", "OC-1", "J-1"))
                .thenReturn(meeting);
        when(orchestrator.executePrevisitPhase("J-1", "C-1", "OC-1", "目标"))
                .thenReturn(previsit);

        PrevisitPreparationService.PreparedPrevisit result =
                service.prepare("J-1", "C-1", "RM-1", "OC-1", "目标", OutreachChannel.PHONE);

        assertThat(result.outreachScript()).isSameAs(outreach);
        assertThat(result.meetingScript()).isSameAs(meeting);
        assertThat(result.previsitReport()).isSameAs(previsit.previsitReport());
        assertThat(result.battleCard()).isSameAs(previsit.battleCard());
        assertThat(result.assemblyTrace()).containsExactlyElementsOf(trace);
        assertThat(result.skillReportTitle()).isEqualTo("R1 访前报告");
        assertThat(result.skillExecutiveSummary()).isEqualTo("摘要");
        assertThat(result.skillSections()).containsExactlyElementsOf(sections);

        verify(outreachScriptService).generateScript("C-1", "RM-1", "OC-1", "J-1", OutreachChannel.PHONE);
        verify(meetingScriptService).generateScript("C-1", "RM-1", "OC-1", "J-1");
        verify(orchestrator).executePrevisitPhase("J-1", "C-1", "OC-1", "目标");
    }
}
