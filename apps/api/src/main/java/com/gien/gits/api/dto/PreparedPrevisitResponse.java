package com.gien.gits.api.dto;

import com.gien.gits.engagement.MeetingScript;
import com.gien.gits.engagement.OutreachScript;
import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.engagement.QuickBattleCard;
import java.util.List;

/**
 * 一键访前自动准备响应。R1 正文来自 DKWS Skill；supplyChainMarkdown 不再由 gits 种子拼装。
 */
public record PreparedPrevisitResponse(
        OutreachScript outreachScript,
        MeetingScript meetingScript,
        PrevisitReportContent previsitReport,
        QuickBattleCard battleCard,
        String supplyChainMarkdown,
        List<AssemblyTraceStep> assemblyTrace,
        String skillReportTitle,
        String skillExecutiveSummary,
        List<SkillReportSection> skillSections) {

    public PreparedPrevisitResponse {
        assemblyTrace = assemblyTrace == null ? List.of() : List.copyOf(assemblyTrace);
        skillSections = skillSections == null ? List.of() : List.copyOf(skillSections);
    }

    public PreparedPrevisitResponse(
            OutreachScript outreachScript,
            MeetingScript meetingScript,
            PrevisitReportContent previsitReport,
            QuickBattleCard battleCard,
            String supplyChainMarkdown,
            List<AssemblyTraceStep> assemblyTrace) {
        this(outreachScript, meetingScript, previsitReport, battleCard, supplyChainMarkdown,
                assemblyTrace, null, null, List.of());
    }
}
