package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.gien.gits.engagement.port.SkillExecutionResult;
import java.util.List;

/**
 * DSH skill 装配轨迹一步（对齐契约 v1.1：phase/status/message，可选 kiId）。
 */
@JsonInclude(JsonInclude.Include.NON_EMPTY)
public record AssemblyTraceStep(String phase, String status, String message, String kiId) {

    public AssemblyTraceStep(String phase, String status, String message) {
        this(phase, status, message, null);
    }

    public static List<AssemblyTraceStep> from(List<SkillExecutionResult.TraceStep> steps) {
        if (steps == null || steps.isEmpty()) {
            return List.of();
        }
        return steps.stream()
                .map(step -> new AssemblyTraceStep(
                        step.phase(), step.status(), step.message(), step.kiId()))
                .toList();
    }
}
