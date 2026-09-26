package com.gien.gits.api.service;

import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.gien.gits.ontology.port.WritableClaimRepository;
import com.gien.gits.ontology.port.WritableInteractionRepository;
import com.gien.gits.ontology.port.WritableOperatingCaseRepository;
import com.gien.gits.customerjourney.port.WritableCustomerJourneyRepository;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.CustomerJourneyOrchestrator;
import com.gien.gits.customerjourney.InsightClaim;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.OperatingCaseStateMachine;
import com.gien.gits.customerjourney.PostvisitAnalysis;
import com.gien.gits.customerjourney.PrevisitReport;
import com.gien.gits.customerjourney.ProductCandidateClaim;
import com.gien.gits.ontology.CaseStatus;
import com.gien.gits.ontology.Claim;
import com.gien.gits.ontology.ClaimStatus;
import com.gien.gits.ontology.ClaimType;
import com.gien.gits.ontology.Interaction;
import com.gien.gits.ontology.OperatingCase;

/**
 * 客户旅程业务服务：将CustomerJourneyOrchestrator的静态方法包装为Spring Bean实例方法，
 * 每步操作落库（调用Repository的save/find方法）。
 *
 * 保留原CustomerJourneyOrchestrator静态方法不变（兼容现有纯内存测试）。
 */
@Service
public class CustomerJourneyService {

    private final WritableOperatingCaseRepository caseRepo;
    private final WritableInteractionRepository interactionRepo;
    private final WritableClaimRepository claimRepo;
    private final WritableCustomerJourneyRepository journeyRepo;

    public CustomerJourneyService(WritableOperatingCaseRepository caseRepo,
                                  WritableInteractionRepository interactionRepo,
                                  WritableClaimRepository claimRepo,
                                  WritableCustomerJourneyRepository journeyRepo) {
        this.caseRepo = Objects.requireNonNull(caseRepo, "caseRepo");
        this.interactionRepo = Objects.requireNonNull(interactionRepo, "interactionRepo");
        this.claimRepo = Objects.requireNonNull(claimRepo, "claimRepo");
        this.journeyRepo = Objects.requireNonNull(journeyRepo, "journeyRepo");
    }

    // ── M17: 开户 + 信号触发交互 ────────────────────────────────

    /**
     * 开户：创建CustomerJourney + 信号交互，落库。
     * @return 新建的CustomerJourney
     */
    @Transactional
    public CustomerJourney openJourney(UUID operatingCaseId, String customerId,
                                       String customerName, String signalDescription) {
        return openJourney(operatingCaseId, customerId, customerName, signalDescription, null);
    }

    /**
     * 开户（可带经营旅程名称）。
     *
     * @param journeyName 经营旅程名称；空白时按 {@link CustomerJourneyNaming} 规则由读取侧派生
     */
    @Transactional
    public CustomerJourney openJourney(UUID operatingCaseId, String customerId,
                                       String customerName, String signalDescription,
                                       String journeyName) {
        OperatingCase operatingCase = caseRepo.findById(operatingCaseId)
                .orElseThrow(() -> new IllegalArgumentException("案例不存在: " + operatingCaseId));

        // 委托静态方法生成领域对象
        CustomerJourneyOrchestrator.JourneyStartResult result =
                CustomerJourneyOrchestrator.openJourney(operatingCase, customerId, customerName,
                        signalDescription, journeyName);

        // 推进案例状态 OPEN → IN_PROGRESS
        OperatingCase progressed = OperatingCaseStateMachine.transition(operatingCase, CaseStatus.IN_PROGRESS);
        caseRepo.updateStatus(progressed.caseId(), progressed.status());

        // 落库
        journeyRepo.saveJourney(result.journey());
        interactionRepo.save(result.signalInteraction());

        return result.journey();
    }

    // ── M18: AI洞察 + 推送交互 ──────────────────────────────────

    /**
     * AI洞察分析：基于Candidate Claim生成InsightClaim，落库。
     */
    @Transactional
    public InsightClaim analyzeInsight(UUID claimId, String insightCategory,
                                       String insightSummary, UUID journeyId,
                                       String rmId, String rmName) {
        Claim claim = claimRepo.findById(claimId)
                .orElseThrow(() -> new IllegalArgumentException("主张不存在: " + claimId));

        CustomerJourneyOrchestrator.InsightResult result =
                CustomerJourneyOrchestrator.analyzeInsight(claim, insightCategory, insightSummary, journeyId, rmId, rmName);

        // 落库
        journeyRepo.saveInsight(result.insight());
        interactionRepo.save(result.pushInteraction());

        // 推进JourneyPhase: KYC_COLLECT → INSIGHT_ANALYSIS
        journeyRepo.updateJourneyPhase(journeyId, JourneyPhase.INSIGHT_ANALYSIS);

        return result.insight();
    }

    // ── M20: 产品匹配 ──────────────────────────────────────────

    /**
     * 产品匹配：基于InsightClaim生成ProductCandidateClaim，落库。
     */
    @Transactional
    public ProductCandidateClaim matchProduct(UUID insightId, String productCode,
                                               String productName, String matchReason,
                                               String rmId, String rmName) {
        InsightClaim insight = journeyRepo.findInsightById(insightId)
                .orElseThrow(() -> new IllegalArgumentException("洞察不存在: " + insightId));

        CustomerJourneyOrchestrator.ProductMatchResult result =
                CustomerJourneyOrchestrator.matchProduct(insight, productCode, productName, matchReason, rmId, rmName);

        // 同时创建产品候选对应的Claim（使用独立的claimId，避免与原始Claim冲突）
        claimRepo.save(new Claim(UUID.randomUUID(), insight.operatingCaseId(),
                ClaimType.PRODUCT_CANDIDATE, ClaimStatus.CANDIDATE, "产品候选: " + productName,
                Instant.now(), null, Instant.now(), null));

        // 落库
        journeyRepo.saveProductCandidate(result.product());
        interactionRepo.save(result.matchInteraction());

        return result.product();
    }

    // ── M21: 访前报告 + 面谈交互 ────────────────────────────────

    /**
     * 执行访前报告：生成PrevisitReport + 面谈交互，落库。
     */
    @Transactional
    public PrevisitReport executePrevisit(UUID operatingCaseId, UUID journeyId,
                                           String rmId, String rmName,
                                           String customerId, String customerContact,
                                           String summary) {
        // 查询该案例下所有交互作为前置交互
        List<Interaction> priorInteractions = interactionRepo.findByCaseId(operatingCaseId);

        CustomerJourneyOrchestrator.PrevisitResult result =
                CustomerJourneyOrchestrator.executePrevisit(operatingCaseId, journeyId,
                        priorInteractions, rmId, rmName, customerId, customerContact, summary);

        // 落库
        journeyRepo.savePrevisitReport(result.report());
        interactionRepo.save(result.visitInteraction());

        // 推进JourneyPhase: INSIGHT_ANALYSIS → PREVISIT_PREP
        journeyRepo.updateJourneyPhase(journeyId, JourneyPhase.PREVISIT_PREP);

        return result.report();
    }

    // ── M22: 访后分析 + 回访交互 ────────────────────────────────

    /**
     * 访后分析：生成PostvisitAnalysis + 回访交互，落库。
     */
    @Transactional
    public PostvisitAnalysis closeWithPostvisit(UUID operatingCaseId, UUID journeyId,
                                                 UUID previsitReportId,
                                                 String outcome, String followUpAction,
                                                 String rmId, String rmName,
                                                 String customerId, String customerContact,
                                                 boolean customerAgreed) {
        CustomerJourneyOrchestrator.PostvisitResult result =
                CustomerJourneyOrchestrator.closeWithPostvisit(operatingCaseId, journeyId,
                        previsitReportId, outcome, followUpAction, rmId, rmName,
                        customerId, customerContact, customerAgreed);

        // 落库
        journeyRepo.savePostvisitAnalysis(result.analysis());
        interactionRepo.save(result.followUpInteraction());

        // 推进JourneyPhase: PREVISIT_PREP → COMPLETED
        journeyRepo.updateJourneyPhase(journeyId, JourneyPhase.COMPLETED);

        return result.analysis();
    }

    // ── 查询辅助方法 ──────────────────────────────────────────────

    /** 按ID查询CustomerJourney */
    public CustomerJourney findJourneyById(UUID journeyId) {
        return journeyRepo.findJourneyById(journeyId).orElse(null);
    }

    /** 按caseId查询所有Journey */
    public List<CustomerJourney> findJourneysByCaseId(UUID caseId) {
        return journeyRepo.findJourneysByCaseId(caseId);
    }
}