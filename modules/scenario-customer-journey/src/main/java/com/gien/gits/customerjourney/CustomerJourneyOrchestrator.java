package com.gien.gits.customerjourney;

import com.gien.gits.ontology.CaseStatus;
import com.gien.gits.ontology.Channel;
import com.gien.gits.ontology.Claim;
import com.gien.gits.ontology.ClaimStatus;
import com.gien.gits.ontology.Interaction;
import com.gien.gits.ontology.OperatingCase;

import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 编排 M17→M18→M20→M21→M22 客户经理访前访后智能体业务链。
 *
 * 每一步同时推进 OperatingCase 状态和产生对应的交互记录。
 * 交互记录是业务链的纽带：
 *   M17: 信号触发交互（AI→客户经理）
 *   M18: AI洞察推送交互（AI→客户经理）
 *   M20: 产品匹配交互（AI→客户经理，内部不直接面向客户）
 *   M21: 访前面谈交互（客户经理→客户，出站）
 *   M22: 访后回访交互（客户经理→客户，入站或出站）
 *
 * AI输出只能是 Candidate Claim；只有人工确认才能推进为 VERIFIED_FACT。
 */
public final class CustomerJourneyOrchestrator {

    private CustomerJourneyOrchestrator() {}

    // ── M17: 开户 + 信号触发交互 ────────────────────────────────

    public static JourneyStartResult openJourney(OperatingCase openCase,
                                                  String customerId, String customerName,
                                                  String signalDescription) {
        return openJourney(openCase, customerId, customerName, signalDescription, null);
    }

    /**
     * 开户（可带经营旅程名称）。
     *
     * @param journeyName 经营旅程名称；空白时置 null，由读取侧按
     *                    {@link CustomerJourneyNaming#defaultName} 统一派生
     */
    public static JourneyStartResult openJourney(OperatingCase openCase,
                                                  String customerId, String customerName,
                                                  String signalDescription,
                                                  String journeyName) {
        Objects.requireNonNull(openCase, "openCase");
        if (openCase.status() != CaseStatus.OPEN) {
            throw new IllegalStateException("案例必须为OPEN状态才能开户; 当前: " + openCase.status());
        }
        customerId = requireText(customerId, "customerId");

        Instant now = Instant.now();
        CustomerJourney journey = new CustomerJourney(
                UUID.randomUUID(), openCase.caseId(), customerId, customerName,
                JourneyPhase.KYC_COLLECT, now, now,
                (journeyName == null || journeyName.isBlank()) ? null : journeyName.trim());

        // M17交互：AI信号触发，推送给客户经理
        Interaction signalInteraction = new Interaction(
                UUID.randomUUID(), openCase.caseId(), journey.journeyId(),
                Interaction.InteractionType.SIGNAL_TRIGGER,
                Interaction.Direction.OUTBOUND,
                Channel.RISK_SIGNAL_ENGINE,
                new Interaction.Participant("AI-CUSTOMER-JOURNEY", Interaction.Participant.Role.AI_AGENT, "客户旅程智能体"),
                List.of(new Interaction.Participant("RM-" + customerId, Interaction.Participant.Role.RELATIONSHIP_MANAGER, "客户经理")),
                signalDescription,
                List.of(),
                Interaction.InteractionOutcome.INFORMATION_GATHERED,
                now, null,
                hashOf(signalDescription));

        return new JourneyStartResult(journey, signalInteraction);
    }

    public record JourneyStartResult(CustomerJourney journey, Interaction signalInteraction) {}

    // ── M18: AI洞察 + 推送交互 ──────────────────────────────────

    public static InsightResult analyzeInsight(Claim candidateClaim, String insightCategory,
                                                String insightSummary, UUID journeyId,
                                                String rmId, String rmName) {
        Objects.requireNonNull(candidateClaim, "candidateClaim");
        insightCategory = requireText(insightCategory, "insightCategory");
        insightSummary = requireText(insightSummary, "insightSummary");

        if (candidateClaim.status() != ClaimStatus.CANDIDATE) {
            throw new IllegalArgumentException(
                    "只有CANDIDATE状态的主张能生成洞察; 当前: " + candidateClaim.status());
        }

        InsightClaim insight = InsightClaim.fromClaim(candidateClaim, insightCategory, insightSummary);

        // M18交互：AI推送洞察给客户经理
        Interaction pushInteraction = new Interaction(
                UUID.randomUUID(), candidateClaim.caseId(), journeyId,
                Interaction.InteractionType.AI_INSIGHT_PUSH,
                Interaction.Direction.OUTBOUND,
                Channel.AI_INSIGHT_ENGINE,
                new Interaction.Participant("AI-INSIGHT", Interaction.Participant.Role.AI_AGENT, "洞察分析智能体"),
                List.of(new Interaction.Participant(rmId, Interaction.Participant.Role.RELATIONSHIP_MANAGER, rmName)),
                insightSummary,
                List.of(insight.insightId()),
                Interaction.InteractionOutcome.INFORMATION_GATHERED,
                insight.generatedAt(), null,
                hashOf(insightSummary));

        return new InsightResult(insight, pushInteraction);
    }

    public record InsightResult(InsightClaim insight, Interaction pushInteraction) {}

    // ── M20: 产品匹配（内部AI交互，不直接面向客户） ──────────────

    public static ProductMatchResult matchProduct(InsightClaim insight, String productCode,
                                                   String productName, String matchReason,
                                                   String rmId, String rmName) {
        Objects.requireNonNull(insight, "insight");
        productCode = requireText(productCode, "productCode");
        matchReason = requireText(matchReason, "matchReason");

        ProductCandidateClaim product = ProductCandidateClaim.fromInsight(
                insight, productCode, productName, matchReason);

        // M20交互：AI内部匹配，结果推送给客户经理
        Interaction matchInteraction = new Interaction(
                UUID.randomUUID(), insight.operatingCaseId(), insight.insightId(),
                Interaction.InteractionType.AI_INSIGHT_PUSH,
                Interaction.Direction.OUTBOUND,
                Channel.PRODUCT_MATCH_ENGINE,
                new Interaction.Participant("AI-PRODUCT", Interaction.Participant.Role.AI_AGENT, "产品匹配智能体"),
                List.of(new Interaction.Participant(rmId, Interaction.Participant.Role.RELATIONSHIP_MANAGER, rmName)),
                "匹配产品: " + productName + "，理由: " + matchReason,
                List.of(product.productId()),
                Interaction.InteractionOutcome.INFORMATION_GATHERED,
                product.proposedAt(), null,
                hashOf(matchReason));

        return new ProductMatchResult(product, matchInteraction);
    }

    public record ProductMatchResult(ProductCandidateClaim product, Interaction matchInteraction) {}

    // ── M21: 访前报告 + 面谈交互 ────────────────────────────────

    public static PrevisitResult executePrevisit(UUID operatingCaseId, UUID journeyId,
                                                  List<Interaction> priorInteractions,
                                                  String rmId, String rmName,
                                                  String customerId, String customerContact,
                                                  String summary) {
        Objects.requireNonNull(operatingCaseId, "operatingCaseId");
        Objects.requireNonNull(journeyId, "journeyId");
        summary = requireText(summary, "summary");

        // 从前置交互中提取洞察ID和产品候选ID
        List<UUID> insightIds = priorInteractions.stream()
                .filter(i -> i.type() == Interaction.InteractionType.AI_INSIGHT_PUSH)
                .flatMap(i -> i.producedClaimIds().stream())
                .toList();
        List<UUID> productIds = priorInteractions.stream()
                .filter(i -> i.type() == Interaction.InteractionType.AI_INSIGHT_PUSH && i.channel() == Channel.PRODUCT_MATCH_ENGINE)
                .flatMap(i -> i.producedClaimIds().stream())
                .toList();

        PrevisitReport report = new PrevisitReport(
                UUID.randomUUID(), operatingCaseId, journeyId,
                insightIds, productIds, summary, Instant.now());

        // M21交互：客户经理实地拜访客户（出站面谈）
        Instant visitStart = Instant.now();
        Interaction visitInteraction = new Interaction(
                UUID.randomUUID(), operatingCaseId, journeyId,
                Interaction.InteractionType.FACE_TO_FACE_VISIT,
                Interaction.Direction.OUTBOUND,
                Channel.FACE_TO_FACE,
                new Interaction.Participant(rmId, Interaction.Participant.Role.RELATIONSHIP_MANAGER, rmName),
                List.of(new Interaction.Participant(customerId, Interaction.Participant.Role.CUSTOMER, customerContact)),
                summary,
                List.of(report.reportId()),
                Interaction.InteractionOutcome.CUSTOMER_DEFERRED, // 默认：客户需考虑，访后才能确定最终结果
                visitStart, null,
                hashOf(summary));

        return new PrevisitResult(report, visitInteraction);
    }

    public record PrevisitResult(PrevisitReport report, Interaction visitInteraction) {}

    // ── M22: 访后分析 + 回访交互 ────────────────────────────────

    public static PostvisitResult closeWithPostvisit(UUID operatingCaseId, UUID journeyId,
                                                      UUID previsitReportId,
                                                      String outcome, String followUpAction,
                                                      String rmId, String rmName,
                                                      String customerId, String customerContact,
                                                      boolean customerAgreed) {
        Objects.requireNonNull(operatingCaseId, "operatingCaseId");
        Objects.requireNonNull(journeyId, "journeyId");
        outcome = requireText(outcome, "outcome");

        PostvisitAnalysis analysis = new PostvisitAnalysis(
                UUID.randomUUID(), operatingCaseId, journeyId, previsitReportId,
                outcome, followUpAction, Instant.now());

        // M22交互：访后回访确认（方向取决于客户是否主动回复）
        Interaction followUpInteraction = new Interaction(
                UUID.randomUUID(), operatingCaseId, journeyId,
                customerAgreed ? Interaction.InteractionType.FOLLOW_UP : Interaction.InteractionType.FACE_TO_FACE_VISIT,
                customerAgreed ? Interaction.Direction.INBOUND : Interaction.Direction.OUTBOUND,
                customerAgreed ? Channel.PHONE_CALL : Channel.FACE_TO_FACE,
                customerAgreed
                        ? new Interaction.Participant(customerId, Interaction.Participant.Role.CUSTOMER, customerContact)
                        : new Interaction.Participant(rmId, Interaction.Participant.Role.RELATIONSHIP_MANAGER, rmName),
                customerAgreed
                        ? List.of(new Interaction.Participant(rmId, Interaction.Participant.Role.RELATIONSHIP_MANAGER, rmName))
                        : List.of(new Interaction.Participant(customerId, Interaction.Participant.Role.CUSTOMER, customerContact)),
                outcome,
                List.of(analysis.analysisId()),
                customerAgreed ? Interaction.InteractionOutcome.CUSTOMER_AGREED : Interaction.InteractionOutcome.CUSTOMER_DECLINED,
                Instant.now(), null,
                hashOf(outcome));

        return new PostvisitResult(analysis, followUpInteraction);
    }

    public record PostvisitResult(PostvisitAnalysis analysis, Interaction followUpInteraction) {}

    // ── 完整链路一键执行 ─────────────────────────────────────────

    /**
     * 执行完整 M17→M22 链路，每步产生交互记录。
     * 返回结果包含所有域对象和5次交互记录。
     *
     * 状态转换：OPEN → IN_PROGRESS → WAITING_FOR_HUMAN → IN_PROGRESS → CLOSED
     */
    public static FullChainResult executeFullChain(OperatingCase operatingCase,
                                                    String customerId, String customerName,
                                                    Claim initialClaim,
                                                    String insightCategory, String insightSummary,
                                                    String productCode, String productName, String matchReason,
                                                    String previsitSummary,
                                                    String postvisitOutcome, String followUpAction,
                                                    String rmId, String rmName,
                                                    boolean customerAgreed) {
        Objects.requireNonNull(operatingCase, "operatingCase");
        if (operatingCase.status() != CaseStatus.OPEN) {
            throw new IllegalStateException(
                    "OperatingCase必须为OPEN状态; 当前: " + operatingCase.status());
        }

        // M17: 开户 + 信号交互
        JourneyStartResult m17 = openJourney(operatingCase, customerId, customerName, initialClaim.statement());
        OperatingCase current = OperatingCaseStateMachine.transition(operatingCase, CaseStatus.IN_PROGRESS);

        // M18: 洞察 + 推送交互
        InsightResult m18 = analyzeInsight(initialClaim, insightCategory, insightSummary,
                m17.journey.journeyId(), rmId, rmName);

        // M20: 产品匹配 + 内部交互
        ProductMatchResult m20 = matchProduct(m18.insight, productCode, productName, matchReason,
                rmId, rmName);

        // M21: 访前报告 + 面谈交互 → WAITING_FOR_HUMAN
        PrevisitResult m21 = executePrevisit(
                current.caseId(), m17.journey.journeyId(),
                List.of(m18.pushInteraction, m20.matchInteraction),
                rmId, rmName, customerId, customerName, previsitSummary);
        current = OperatingCaseStateMachine.transition(current, CaseStatus.WAITING_FOR_HUMAN);

        // 人工确认：WAITING_FOR_HUMAN → IN_PROGRESS
        current = OperatingCaseStateMachine.transition(current, CaseStatus.IN_PROGRESS);

        // M22: 访后分析 + 回访交互 → CLOSED
        PostvisitResult m22 = closeWithPostvisit(
                current.caseId(), m17.journey.journeyId(), m21.report.reportId(),
                postvisitOutcome, followUpAction,
                rmId, rmName, customerId, customerName, customerAgreed);
        current = OperatingCaseStateMachine.transition(current, CaseStatus.CLOSED);

        return new FullChainResult(
                m17.journey, m18.insight, m20.product, m21.report, m22.analysis, current,
                List.of(m17.signalInteraction, m18.pushInteraction, m20.matchInteraction,
                        m21.visitInteraction, m22.followUpInteraction));
    }

    public record FullChainResult(
            CustomerJourney journey,
            InsightClaim insight,
            ProductCandidateClaim product,
            PrevisitReport report,
            PostvisitAnalysis analysis,
            OperatingCase closedCase,
            List<Interaction> interactions) {}

    // ── 工具方法 ─────────────────────────────────────────────────

    private static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " 不能为空");
        }
        return value;
    }

    private static String hashOf(String content) {
        // 简易哈希——生产环境应使用SHA-256
        return Integer.toHexString(content.hashCode());
    }
}
