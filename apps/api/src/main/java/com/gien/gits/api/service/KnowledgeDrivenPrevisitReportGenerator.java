package com.gien.gits.api.service;

import com.gien.gits.api.dto.SkillReportSection;
import com.gien.gits.engagement.PrevisitReportContent;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 访前报告：只调用 DKWS Skill，由平台按 customerId 取数。
 * gits 不组装 knowledgeContext / structuredFacts / 本地种子；缺数留空。
 */
public final class KnowledgeDrivenPrevisitReportGenerator {

    static final String PREVISIT_SKILL_ID = "skill-customer-previsit-report";

    private static final Logger log = LoggerFactory.getLogger(KnowledgeDrivenPrevisitReportGenerator.class);

    private final SkillExecutionPort skillExecutionPort;

    public KnowledgeDrivenPrevisitReportGenerator(SkillExecutionPort skillExecutionPort) {
        this.skillExecutionPort = Objects.requireNonNull(skillExecutionPort);
    }

    public GenerationResult generate(String customerId, String visitObjective) {
        SkillAttempt skill = trySkill(customerId, visitObjective);
        if (skill.report() != null) {
            return new GenerationResult(
                    skill.report(), skill.trace(), skill.reportTitle(), skill.executiveSummary(), skill.sections());
        }
        return new GenerationResult(
                emptyReport(customerId, visitObjective), skill.trace(), null, null, List.of());
    }

    public record GenerationResult(
            PrevisitReportContent report,
            List<SkillExecutionResult.TraceStep> assemblyTrace,
            String skillReportTitle,
            String skillExecutiveSummary,
            List<SkillReportSection> skillSections) {
        public GenerationResult {
            Objects.requireNonNull(report, "report");
            assemblyTrace = List.copyOf(assemblyTrace != null ? assemblyTrace : List.of());
            skillSections = List.copyOf(skillSections != null ? skillSections : List.of());
        }
    }

    private record SkillAttempt(
            PrevisitReportContent report,
            List<SkillExecutionResult.TraceStep> trace,
            String reportTitle,
            String executiveSummary,
            List<SkillReportSection> sections) {
        private SkillAttempt {
            trace = List.copyOf(trace != null ? trace : List.of());
            sections = List.copyOf(sections != null ? sections : List.of());
        }
    }

    private SkillAttempt trySkill(String customerId, String visitObjective) {
        try {
            SkillExecutionResult result = skillExecutionPort.execute(skillCommand(customerId, visitObjective));
            result.trace().forEach(step ->
                    log.info("[PREVISIT-SKILL] trace phase={} status={} kiId={} message={}",
                            step.phase(), step.status(), step.kiId(), step.message()));
            if (!result.isOk()) {
                log.warn("[PREVISIT-SKILL] dsh status={}，不回填本地种子", result.status());
                return new SkillAttempt(null, result.trace(), null, null, List.of());
            }
            List<SkillReportSection> sections = parseSections(result.data().get("sections"));
            String title = stringValue(result.data().get("reportTitle"));
            String summary = stringValue(result.data().get("executiveSummary"));
            return new SkillAttempt(
                    reportFromSkill(customerId, visitObjective, title, summary, sections),
                    result.trace(), title, summary, sections);
        } catch (SkillExecutionException ex) {
            log.warn("[PREVISIT-SKILL] DKWS 不可达，不使用本地种子: {}", ex.getMessage());
            return new SkillAttempt(null, List.of(new SkillExecutionResult.TraceStep(
                    "dkws", "failed", "DKWS 不可达，未使用本地种子补数")), null, null, List.of());
        }
    }

    private SkillExecutionCommand skillCommand(String customerId, String visitObjective) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("customerId", customerId);
        request.put("evidenceTimestamp", Instant.now().toString());
        if (visitObjective != null && !visitObjective.isBlank()) {
            request.put("visitObjective", visitObjective);
        }
        return new SkillExecutionCommand(
                PREVISIT_SKILL_ID, "REQ-PREVISIT-" + UUID.randomUUID(), customerId, request);
    }

    private static PrevisitReportContent reportFromSkill(
            String customerId, String visitObjective,
            String title, String summary, List<SkillReportSection> sections) {
        String strategy = firstNonBlank(summary, title);
        List<String> questions = headings(sections, "问题");
        List<String> risks = headings(sections, "风险");
        return new PrevisitReportContent(
                "R1-" + UUID.randomUUID().toString().substring(0, 8),
                customerId, "", "",
                visitObjective == null ? "" : visitObjective,
                null,
                new PrevisitReportContent.KycGapSummary(List.of(), List.of(), List.of(), List.of()),
                List.of(),
                questions,
                risks,
                strategy == null ? "" : strategy);
    }

    private static PrevisitReportContent emptyReport(String customerId, String visitObjective) {
        return reportFromSkill(customerId, visitObjective, null, null, List.of());
    }

    private static List<SkillReportSection> parseSections(Object raw) {
        if (!(raw instanceof List<?> list)) {
            return List.of();
        }
        List<SkillReportSection> out = new ArrayList<>();
        for (Object item : list) {
            if (item instanceof Map<?, ?> map) {
                Object heading = map.get("heading");
                Object content = map.get("content");
                out.add(new SkillReportSection(
                        heading instanceof String h ? h : "",
                        content instanceof String c ? c : ""));
            }
        }
        return out;
    }

    private static List<String> headings(List<SkillReportSection> sections, String keyword) {
        List<String> out = new ArrayList<>();
        for (SkillReportSection section : sections) {
            if (section.heading() != null && section.heading().contains(keyword)
                    && section.content() != null && !section.content().isBlank()) {
                out.add(section.content());
            }
        }
        return out;
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return "";
    }

    private static String stringValue(Object value) {
        return value instanceof String s ? s : null;
    }
}
