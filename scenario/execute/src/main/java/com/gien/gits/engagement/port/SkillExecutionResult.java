package com.gien.gits.engagement.port;

import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * SKILL 执行结果 — dsh 平台返回的结构化产出。
 *
 * <p>字段对齐契约 {@code docs/dd/skill-execute-api-contract.md} §4/§5/§6：</p>
 * <ul>
 *   <li>{@code requestId / status / data / errors / assemblyTrace / modelCalls}</li>
 *   <li>{@code assemblyTrace[]} 元素 = {@code {phase,status,message}}，可选 {@code kiId}（KI 级 evidence 步骤）</li>
 *   <li>{@code modelCalls[]} 元素 = {@code {model,inputTokens,outputTokens,latencyMs}}</li>
 * </ul>
 *
 * @param status     执行状态（ok / skill_error / exit_policy_no_new_evidence）
 * @param requestId  回执的请求 ID
 * @param data       Skill 业务结构化结果（成功时字段见各 skill）
 * @param errors     失败原因列表（每项 {code,message}；成功为空）
 * @param trace      装配轨迹（逐 phase）
 * @param modelCalls 模型调用元数据
 */
public record SkillExecutionResult(
        SkillExecutionStatus status,
        String requestId,
        Map<String, Object> data,
        List<ErrorItem> errors,
        List<TraceStep> trace,
        List<ModelCall> modelCalls) {

    public SkillExecutionResult {
        Objects.requireNonNull(status, "status");
        data = data == null ? Map.of() : Map.copyOf(data);
        errors = List.copyOf(errors != null ? errors : List.of());
        trace = List.copyOf(trace != null ? trace : List.of());
        modelCalls = List.copyOf(modelCalls != null ? modelCalls : List.of());
    }

    /** 是否成功。 */
    public boolean isOk() {
        return status == SkillExecutionStatus.OK;
    }

    /** 装配轨迹步骤（对齐契约：phase/status/message，可选 kiId）。 */
    public record TraceStep(String phase, String status, String message, String kiId) {
        public TraceStep(String phase, String status, String message) {
            this(phase, status, message, null);
        }
    }

    /** 模型调用元数据。 */
    public record ModelCall(String model, int inputTokens, int outputTokens, long latencyMs) {
    }

    /** 错误项。 */
    public record ErrorItem(String code, String message) {
    }
}