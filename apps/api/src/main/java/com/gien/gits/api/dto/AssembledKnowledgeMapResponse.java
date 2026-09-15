package com.gien.gits.api.dto;

import java.util.List;

/**
 * P38 知识地图：DKWS {@code skill-customer-previsit-report} 装配结果。
 * 不含 GITS 仓库 KI/KE 快照。
 */
public record AssembledKnowledgeMapResponse(
        String customerId,
        String skillReportTitle,
        String skillExecutiveSummary,
        List<SkillReportSection> skillSections,
        List<AssemblyTraceStep> assemblyTrace) {

    public AssembledKnowledgeMapResponse {
        skillSections = skillSections == null ? List.of() : List.copyOf(skillSections);
        assemblyTrace = assemblyTrace == null ? List.of() : List.copyOf(assemblyTrace);
    }
}
