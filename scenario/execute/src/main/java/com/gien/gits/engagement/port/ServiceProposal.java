package com.gien.gits.engagement.port;

import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * SP-20 服务建议书 — DKWS {@code data.result} 的强类型投影（契约 v1.4 §2.4）。
 *
 * <p>对齐真实样例 {@code docs/architecture/DKWS-V1.4-GITS-INTEGRATION-SAMPLES.md} §2.4：</p>
 * <ul>
 *   <li>content.proposalDraft = 8 章 Markdown 正文</li>
 *   <li>content.internalVersion = 内部版（含 factLabels 逐段标注 F/A/C/B/H/P）</li>
 *   <li>content.customerVersion = 对客版（仅 F/A，段落级过滤；releaseBlockedUntil 为空才可放行）</li>
 *   <li>gateRecommendations = 闸门建议（GITS 权威状态机输入，非最终闸门状态）</li>
 * </ul>
 *
 * @param schemaVersion 结果结构版本（1.0.0）
 * @param skillId       SP-20
 * @param runId         当次运行 ID（幂等重发不变）
 * @param status        SUCCESS / PARTIAL（PARTIAL 时 ruleViolations 非空）
 * @param timestamp     运行完成时间（UTC ISO-8601）
 * @param content       三版本内容
 * @param citations     引用清单（逐 claim：id/claim/source/date/factLabel/chapterRef）
 * @param unknowns      待确认项
 * @param limitations   能力边界说明
 * @param gateRecommendations 闸门建议（非权威）
 * @param ruleViolations SP-20 规则违规（BLOCKING 不回残缺成功）
 */
public record ServiceProposal(
        String schemaVersion,
        String skillId,
        String runId,
        String status,
        String timestamp,
        Content content,
        List<Citation> citations,
        List<Unknown> unknowns,
        List<String> limitations,
        GateRecommendations gateRecommendations,
        List<RuleViolation> ruleViolations) {

    public ServiceProposal {
        content = content == null ? Content.EMPTY : content;
        citations = List.copyOf(citations != null ? citations : List.of());
        unknowns = List.copyOf(unknowns != null ? unknowns : List.of());
        limitations = List.copyOf(limitations != null ? limitations : List.of());
        gateRecommendations = gateRecommendations == null ? GateRecommendations.EMPTY : gateRecommendations;
        ruleViolations = List.copyOf(ruleViolations != null ? ruleViolations : List.of());
    }

    /** 对客版是否已具备放行条件（releaseBlockedUntil 为空）。 */
    public boolean isCustomerVersionReleasable() {
        return content.customerVersion() != null
            && content.customerVersion().releaseBlockedUntil().isEmpty();
    }

    /** 三版本内容。 */
    public record Content(
            String proposalDraft,
            Version internalVersion,
            Version customerVersion,
            String customerVersionNote) {

        public static final Content EMPTY = new Content("", null, null, "");

        public Content {
            proposalDraft = proposalDraft == null ? "" : proposalDraft;
            customerVersionNote = customerVersionNote == null ? "" : customerVersionNote;
        }
    }

    /** 内部版 / 对客版。 */
    public record Version(
            String content,
            Map<String, String> factLabels,
            List<String> filteringNotes,
            List<String> includes,
            List<String> excludes,
            List<String> releaseBlockedUntil) {

        public static final Version EMPTY = new Version("", Map.of(), List.of(), List.of(), List.of(), List.of());

        public Version {
            content = content == null ? "" : content;
            factLabels = factLabels == null ? Map.of() : Map.copyOf(factLabels);
            filteringNotes = List.copyOf(filteringNotes != null ? filteringNotes : List.of());
            includes = List.copyOf(includes != null ? includes : List.of());
            excludes = List.copyOf(excludes != null ? excludes : List.of());
            releaseBlockedUntil = List.copyOf(releaseBlockedUntil != null ? releaseBlockedUntil : List.of());
        }
    }

    /** 引用项。 */
    public record Citation(String id, String claim, String source, String date, String factLabel, String chapterRef) {
    }

    /** 待确认项。 */
    public record Unknown(String id, String description, String suggestedAction, String relatedChapter) {
    }

    /** 闸门建议（DKWS 侧建议，非权威状态）。 */
    public record GateRecommendations(
            String currentGate,
            List<String> passedGates,
            String overallReadiness,
            List<GateCheck> checklist,
            List<String> nextGatePrerequisites) {

        public static final GateRecommendations EMPTY =
            new GateRecommendations("", List.of(), "", List.of(), List.of());

        public GateRecommendations {
            passedGates = List.copyOf(passedGates != null ? passedGates : List.of());
            checklist = List.copyOf(checklist != null ? checklist : List.of());
            nextGatePrerequisites = List.copyOf(nextGatePrerequisites != null ? nextGatePrerequisites : List.of());
        }
    }

    /** 闸门清单项（state：PASSED / READY_FOR_REVIEW / PENDING / BLOCKED）。 */
    public record GateCheck(
            String gate,
            String state,
            String name,
            Map<String, List<String>> checklist) {

        public static final GateCheck EMPTY = new GateCheck("", "", "", Map.of());

        public GateCheck {
            name = name == null ? "" : name;
            checklist = checklist == null ? Map.of() : Map.copyOf(checklist);
        }
    }

    /** SP-20 规则违规。 */
    public record RuleViolation(String code, String severity, String message, String ruleRef) {

        public static final RuleViolation EMPTY = new RuleViolation("", "", "", "");

        public RuleViolation {
            code = code == null ? "" : code;
            severity = severity == null ? "" : severity;
            message = message == null ? "" : message;
            ruleRef = ruleRef == null ? "" : ruleRef;
        }

        /** 是否 BLOCKING（BLOCKING 违规时不回残缺成功）。 */
        public boolean isBlocking() {
            return "BLOCKING".equalsIgnoreCase(severity);
        }
    }

    /** 静态工厂：契约对齐的空/默认实例。 */
    public static ServiceProposal empty() {
        return new ServiceProposal(
            "1.0.0", "SP-20", "", "SUCCESS", "",
            Content.EMPTY, List.of(), List.of(), List.of(),
            GateRecommendations.EMPTY, List.of());
    }
}
