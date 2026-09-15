package com.gien.gits.api.dto;

import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.engagement.QuickBattleCard;
import java.util.List;

/**
 * 访前准备执行响应。R1 正文来自 DKWS Skill。
 */
public record PrevisitExecutionResponse(
        PrevisitReportContent previsitReport,
        QuickBattleCard battleCard,
        String supplyChainMarkdown,
        List<AssemblyTraceStep> assemblyTrace,
        String skillReportTitle,
        String skillExecutiveSummary,
        List<SkillReportSection> skillSections) {

    public PrevisitExecutionResponse {
        assemblyTrace = assemblyTrace == null ? List.of() : List.copyOf(assemblyTrace);
        skillSections = skillSections == null ? List.of() : List.copyOf(skillSections);
    }

    public PrevisitExecutionResponse(PrevisitReportContent previsitReport,
                                     QuickBattleCard battleCard,
                                     String supplyChainMarkdown,
                                     List<AssemblyTraceStep> assemblyTrace) {
        this(previsitReport, battleCard, supplyChainMarkdown, assemblyTrace, null, null, List.of());
    }

    public PrevisitExecutionResponse(PrevisitReportContent previsitReport, QuickBattleCard battleCard) {
        this(previsitReport, battleCard, null, List.of(), null, null, List.of());
    }
}
