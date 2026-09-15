package com.gien.gits.engagement.port;

import java.util.List;
import java.util.Map;

/**
 * SP-21 交互记忆抽取结果 — DKWS {@code data.result} 的强类型投影（契约 v1.4 §3）。
 *
 * <p>对齐样例 {@code docs/architecture/DKWS-V1.4-GITS-INTEGRATION-SAMPLES.md} §3：</p>
 * <ul>
 *   <li>candidateMemories：候选记忆，默认 CANDIDATE 状态，待客户经理确认/修正/拒绝</li>
 *   <li>memoryUpdates：对既有记忆的强化（置信度增量），由 GITS 应用</li>
 *   <li>memorySupersessions：取代（旧记忆置 SUPERSEDED）</li>
 *   <li>生命周期归属 GITS（DKWS 不存记忆）</li>
 * </ul>
 *
 * @param schemaVersion 1.0.0
 * @param interactionId 交互 ID（GITS 生成）
 * @param status        SUCCESS / PARTIAL
 * @param candidateMemories 候选记忆
 * @param memoryUpdates 强化更新
 * @param memorySupersessions 取代
 * @param ruleViolations SP-21 规则违规（3 条规则）
 */
public record InteractionMemoryExtraction(
        String schemaVersion,
        String interactionId,
        String status,
        List<CandidateMemory> candidateMemories,
        List<MemoryUpdate> memoryUpdates,
        List<MemorySupersession> memorySupersessions,
        List<RuleViolation> ruleViolations) {

    public InteractionMemoryExtraction {
        candidateMemories = List.copyOf(candidateMemories != null ? candidateMemories : List.of());
        memoryUpdates = List.copyOf(memoryUpdates != null ? memoryUpdates : List.of());
        memorySupersessions = List.copyOf(memorySupersessions != null ? memorySupersessions : List.of());
        ruleViolations = List.copyOf(ruleViolations != null ? ruleViolations : List.of());
    }

    /**
     * 候选记忆。
     *
     * @param memoryId         DKWS 生成（可空，GITS 落库时生成）
     * @param category         BUSINESS_SIGNAL / PREFERENCE / DECISION_PATTERN / COMMITMENT / RISK
     * @param confidence       置信度 0-1
     * @param suggestedDecayRule NONE / LINEAR / STEP（GITS 采纳建议但生命周期归 GITS）
     * @param evidenceQuote    原始证据引用
     * @param content          记忆内容
     */
    public record CandidateMemory(
            String memoryId,
            String category,
            Double confidence,
            String suggestedDecayRule,
            String evidenceQuote,
            String content) {

        public static final CandidateMemory EMPTY = new CandidateMemory("", "", 0.0, "NONE", "", "");

        public CandidateMemory {
            memoryId = memoryId == null ? "" : memoryId;
            category = category == null ? "" : category;
            suggestedDecayRule = suggestedDecayRule == null ? "NONE" : suggestedDecayRule;
            evidenceQuote = evidenceQuote == null ? "" : evidenceQuote;
            content = content == null ? "" : content;
        }
    }

    /**
     * 强化更新。
     *
     * @param memoryId      既有记忆 ID
     * @param action        REINFORCE
     * @param confidenceDelta 置信度增量
     * @param reason        相似度/证据理由
     */
    public record MemoryUpdate(
            String memoryId,
            String action,
            Double confidenceDelta,
            String reason) {

        public static final MemoryUpdate EMPTY = new MemoryUpdate("", "REINFORCE", 0.0, "");

        public MemoryUpdate {
            action = action == null ? "REINFORCE" : action;
            reason = reason == null ? "" : reason;
        }
    }

    /**
     * 取代。
     *
     * @param supersededMemoryId 被取代旧记忆
     * @param newMemoryId        新记忆
     * @param reason             取代理由
     */
    public record MemorySupersession(
            String supersededMemoryId,
            String newMemoryId,
            String reason) {

        public static final MemorySupersession EMPTY = new MemorySupersession("", "", "");

        public MemorySupersession {
            reason = reason == null ? "" : reason;
        }
    }

    /** SP-21 规则违规（severity=BLOCKING 时 status=PARTIAL 不回残缺成功）。 */
    public record RuleViolation(String code, String severity, String message) {

        public static final RuleViolation EMPTY = new RuleViolation("", "", "");

        public RuleViolation {
            code = code == null ? "" : code;
            severity = severity == null ? "" : severity;
            message = message == null ? "" : message;
        }

        public boolean isBlocking() {
            return "BLOCKING".equalsIgnoreCase(severity);
        }
    }

    /** 供序列化辅助。 */
    public Map<String, Object> asMap() {
        return Map.of(
            "schemaVersion", schemaVersion,
            "interactionId", interactionId,
            "status", status,
            "candidateMemories", candidateMemories,
            "memoryUpdates", memoryUpdates,
            "memorySupersessions", memorySupersessions,
            "ruleViolations", ruleViolations);
    }

    public static InteractionMemoryExtraction empty(String interactionId) {
        return new InteractionMemoryExtraction(
            "1.0.0", interactionId, "SUCCESS", List.of(), List.of(), List.of(), List.of());
    }
}
