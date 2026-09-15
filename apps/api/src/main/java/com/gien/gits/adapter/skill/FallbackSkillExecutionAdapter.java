package com.gien.gits.adapter.skill;

import com.gien.gits.engagement.port.LlmClient;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Fallback SKILL 适配器 — 未配置 DKWS 或显式 fallback 模式时的兜底。
 *
 * <p>R1 / 外联 / 会面 / 供应链图谱 / 产品推荐禁止本地补数：直接 {@code SKILL_ERROR}。
 * 其它 skill 可回落本地 {@link LlmClient}。</p>
 */
public class FallbackSkillExecutionAdapter implements SkillExecutionPort {

    private static final Logger log = LoggerFactory.getLogger(FallbackSkillExecutionAdapter.class);

    private final LlmClient llmClient;
    private final String systemPrompt;

    public FallbackSkillExecutionAdapter(LlmClient llmClient, String systemPrompt) {
        this.llmClient = llmClient;
        this.systemPrompt = systemPrompt;
    }

    private static final Set<String> NO_LOCAL_FILL = Set.of(
            "skill-customer-previsit-report",
            "skill-customer-outreach-script",
            "skill-customer-meeting-script",
            "bank-front-supply-chain-graph",
            "bank-front-product-recommendation");

    @Override
    public SkillExecutionResult execute(SkillExecutionCommand command) {
        if (NO_LOCAL_FILL.contains(command.skillId())) {
            log.warn("[SKILL-FALLBACK] 禁止本地补数 skillId={} requestId={}",
                    command.skillId(), command.requestId());
            return new SkillExecutionResult(
                    SkillExecutionStatus.SKILL_ERROR,
                    command.requestId(),
                    Map.of(),
                    List.of(new SkillExecutionResult.ErrorItem(
                            "DKWS_REQUIRED", "须由 DKWS Skill 按 customerId 取数，未使用本地种子")),
                    List.of(new SkillExecutionResult.TraceStep(
                            "dkws", "failed", "DKWS 未配置或不可达，未使用本地种子补数")),
                    List.of());
        }
        log.warn("[SKILL-FALLBACK] 使用本地 LlmClient 回落 skillId={} requestId={}",
                 command.skillId(), command.requestId());
        try {
            String userPrompt = buildUserPrompt(command);
            String content = llmClient.complete(systemPrompt, userPrompt);
            Map<String, Object> data = Map.of(
                "fallback", true,
                "skillId", command.skillId(),
                "content", content);
            return new SkillExecutionResult(
                SkillExecutionStatus.OK,
                command.requestId(),
                data,
                List.of(),
                List.of(new SkillExecutionResult.TraceStep(
                    "compose", "ok", "本地 LlmClient 回落完成")),
                List.of(new SkillExecutionResult.ModelCall(
                    "deterministic_fallback", 0, 0, 0)));
        } catch (Exception e) {
            log.error("[SKILL-FALLBACK] 本地 LlmClient 也失败 skillId={}: {}", command.skillId(),
                      e.getMessage());
            return new SkillExecutionResult(
                SkillExecutionStatus.SKILL_ERROR,
                command.requestId(),
                Map.of(),
                List.of(new SkillExecutionResult.ErrorItem("FALLBACK_FAILED",
                    "本地回落失败: " + e.getMessage())),
                List.of(new SkillExecutionResult.TraceStep("compose", "failed",
                    "本地回落失败: " + e.getMessage())),
                List.of());
        }
    }

    private String buildUserPrompt(SkillExecutionCommand command) {
        StringBuilder sb = new StringBuilder();
        sb.append("技能 ").append(command.skillId())
          .append("\n客户: ").append(command.customerId()).append('\n');
        if (!command.request().isEmpty()) {
            try {
                sb.append("上下文: ")
                  .append(new com.fasterxml.jackson.databind.ObjectMapper()
                      .writeValueAsString(command.request())).append('\n');
            } catch (Exception ignore) {
                sb.append("上下文: ").append(command.request()).append('\n');
            }
        }
        return sb.toString();
    }
}