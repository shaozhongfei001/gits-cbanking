package com.gien.gits.api.service;

import com.gien.gits.api.metrics.BusinessMetrics;
import com.gien.gits.customerjourney.port.WritableCustomerJourneyRepository;
import com.gien.gits.ontology.port.DomainEventPublisher;
import com.gien.gits.ontology.port.WritableOperatingCaseRepository;
import com.gien.gits.customerjourney.*;
import com.gien.gits.engagement.*;
import com.gien.gits.engagement.port.PostvisitAnalysisContentRepository;
import com.gien.gits.ontology.*;
import com.gien.gits.adapter.event.CloudEventFactory;

import java.time.Instant;
import java.util.*;

import org.springframework.transaction.annotation.Transactional;

/**
 * 持续经营编排器 — 端到端业务链编排
 * 经营触发→访前准备→互动记录→访后分析→持续经营→反馈评测
 * 
 * 设计原则: 本类只做编排（调用各Service），不混入业务逻辑。
 * 事务边界: 每个公开方法是一个事务单元。
 */
public class EngagementOrchestrator {

    private final CustomerContextService customerContextService;
    private final KycInsightService kycInsightService;
    private final KnowledgeDrivenPrevisitReportGenerator knowledgeDrivenPrevisitGenerator;
    private final PostvisitProcessingService postvisitService;
    private final ReportGenerationService reportService;
    private final CustomerJourneyService journeyService;
    private final PostvisitAnalysisContentRepository analysisContentRepo;
    private final WritableCustomerJourneyRepository journeyRepo;
    private final WritableOperatingCaseRepository operatingCaseRepo;
    private final DomainEventPublisher domainEventPublisher;
    private final BusinessMetrics businessMetrics;

    public EngagementOrchestrator(
            CustomerContextService customerContextService,
            KycInsightService kycInsightService,
            KnowledgeDrivenPrevisitReportGenerator knowledgeDrivenPrevisitGenerator,
            PostvisitProcessingService postvisitService,
            ReportGenerationService reportService,
            CustomerJourneyService journeyService,
            PostvisitAnalysisContentRepository analysisContentRepo,
            WritableCustomerJourneyRepository journeyRepo,
            WritableOperatingCaseRepository operatingCaseRepo,
            DomainEventPublisher domainEventPublisher,
            BusinessMetrics businessMetrics) {
        this.customerContextService = Objects.requireNonNull(customerContextService);
        this.kycInsightService = Objects.requireNonNull(kycInsightService);
        this.knowledgeDrivenPrevisitGenerator = Objects.requireNonNull(knowledgeDrivenPrevisitGenerator);
        this.postvisitService = Objects.requireNonNull(postvisitService);
        this.reportService = Objects.requireNonNull(reportService);
        this.journeyService = Objects.requireNonNull(journeyService);
        this.analysisContentRepo = Objects.requireNonNull(analysisContentRepo);
        this.journeyRepo = Objects.requireNonNull(journeyRepo);
        this.operatingCaseRepo = Objects.requireNonNull(operatingCaseRepo);
        this.domainEventPublisher = Objects.requireNonNull(domainEventPublisher);
        this.businessMetrics = Objects.requireNonNull(businessMetrics);
    }

    /**
     * 启动持续经营场景 — 创建经营案例 + 旅程 + KYC洞察
     */
    @Transactional
    public JourneyStartResult startEngagementJourney(String customerId) {
        // 1. 验证客户存在
        Customer customer = customerContextService.findCustomer(customerId)
            .orElseThrow(() -> new IllegalArgumentException("Customer not found: " + customerId));

        // 2. 创建经营案例并保存到数据库
        OperatingCase operatingCase = new OperatingCase(
            UUID.randomUUID(), CaseType.CONTINUOUS_ENGAGEMENT,
            CaseStatus.OPEN,
            "持续经营: " + customer.customerName(),
            Instant.now(), null, Instant.now(), customer.rmId());
        operatingCaseRepo.save(operatingCase);

        // 3. 创建客户旅程
        CustomerJourney journey = journeyService.openJourney(
            operatingCase.caseId(), customerId, customer.customerName(),
            "持续经营场景启动: " + customer.customerName() + "持续经营");

        // 4. 推进到洞察分析阶段
        journeyRepo.updateJourneyPhase(journey.journeyId(), JourneyPhase.INSIGHT_ANALYSIS);
        CustomerJourney updatedJourney = new CustomerJourney(
            journey.journeyId(), journey.operatingCaseId(), journey.customerId(),
            journey.customerName(), JourneyPhase.INSIGHT_ANALYSIS,
            journey.startedAt(), Instant.now());

        // 5. 获取KYC缺口画像（为后续访前准备提供输入）
        Optional<KycGapProfile> kycProfile = kycInsightService.getKycGapProfile(customerId);

        // 6. 发布领域事件: controlledActionRequested
        domainEventPublisher.publish(
            CloudEventFactory.controlledActionRequested(
                operatingCase.caseId().toString(),
                Map.of("customerId", customerId, "action", "startEngagementJourney")));

        businessMetrics.recordJourneyStarted();

        return new JourneyStartResult(updatedJourney, operatingCase.caseId().toString(), kycProfile);
    }

    // --- 结果记录 ---

    public record JourneyStartResult(CustomerJourney journey, String operatingCaseId,
                                      Optional<KycGapProfile> kycProfile) {}

    /**
     * 执行访前准备 — 生成R1/R2
     */
    @Transactional
    public PrevisitWorkflowResult executePrevisitPhase(
            String journeyId, String customerId, String operatingCaseId, String visitObjective) {

        // 推进旅程到访前准备阶段
        journeyRepo.updateJourneyPhase(UUID.fromString(journeyId), JourneyPhase.PREVISIT_PREP);

        KnowledgeDrivenPrevisitReportGenerator.GenerationResult generated =
            knowledgeDrivenPrevisitGenerator.generate(customerId, visitObjective);

        String customerName = "";
        String customerTier = "";
        String riskLevel = "";
        Optional<Customer> customer = customerContextService.findCustomer(customerId);
        if (customer.isPresent()) {
            Customer c = customer.get();
            customerName = c.customerName() == null ? "" : c.customerName();
            customerTier = c.customerTier() == null ? "" : c.customerTier().name();
            riskLevel = c.riskLevel() == null ? "" : c.riskLevel().name();
        }

        QuickBattleCard card = QuickBattleCardFromSkill.map(
                generated.skillSections(),
                customerName,
                visitObjective,
                customerTier,
                riskLevel);

        return new PrevisitWorkflowResult(
                generated.report(), card, generated.assemblyTrace(),
                generated.skillReportTitle(), generated.skillExecutiveSummary(), generated.skillSections());
    }

    /**
     * 执行访后处理 — 转录处理 + 事实对账 + R4/R5/R6
     */
    @Transactional
    public PostvisitWorkflowResult executePostvisitPhase(
            String journeyId, String operatingCaseId, String customerId, String rawTranscript) {

        // 推进旅程到访后回顾阶段
        journeyRepo.updateJourneyPhase(UUID.fromString(journeyId), JourneyPhase.POSTVISIT_REVIEW);

        // 1. 处理会议记录
        MeetingTranscript transcript = postvisitService.processTranscript(
            journeyId, rawTranscript, operatingCaseId);

        // 2. 生成访后分析 (R4)
        PostvisitAnalysisContent analysis = postvisitService.generatePostvisitAnalysis(
            journeyId, operatingCaseId, transcript);

        // 3. 生成内部关系报告 (R5A)
        RelationshipReport internalReport = reportService.generateInternalRelationshipReport(
            operatingCaseId, journeyId, customerId, analysis);

        // 4. 生成CRM通话报告 (R5B)
        RelationshipReport crmReport = reportService.generateCrmCallReport(
            operatingCaseId, journeyId, customerId, analysis);

        // 5. 生成CRM回写命令 (全部require_human_confirm)
        List<CrmWritebackCommand> crmCommands = reportService.generateCrmWritebackCommands(
            operatingCaseId, journeyId, analysis);

        return new PostvisitWorkflowResult(
            transcript, analysis, internalReport, crmReport, crmCommands);
    }

    /**
     * 处理新证据 — R7更新报告 + R8下次访前报告
     */
    @Transactional
    public NewEvidenceWorkflowResult handleNewEvidence(
            String journeyId, String operatingCaseId, String customerId,
            String newEvidenceDescription, String previousReportId) {

        // 构建客户经营视图 (由ReportGenerationService内部调用)

        // 1. 生成更新关系报告 (R7)
        RelationshipReport updatedReport = reportService.generateUpdatedRelationshipReport(
            operatingCaseId, journeyId, customerId, newEvidenceDescription, previousReportId);

        // 2. 尝试从DB查询上次访后分析
        Optional<PostvisitAnalysisContent> previousAnalysis = loadPreviousAnalysis(operatingCaseId);

        // 3. 生成下次访前报告 (R8) — 上下文继承
        RelationshipReport nextPrevisit = reportService.generateNextPrevisitReport(
            operatingCaseId, journeyId, customerId, previousAnalysis.orElse(null), updatedReport.reportId().toString());

        // 4. 发布领域事件: claimCandidateRecorded
        domainEventPublisher.publish(
            CloudEventFactory.claimCandidateRecorded(
                operatingCaseId,
                Map.of("journeyId", journeyId, "evidence", newEvidenceDescription)));

        return new NewEvidenceWorkflowResult(updatedReport, nextPrevisit);
    }

    /**
     * 加载上次访后分析 — 从持久化存储查询
     */
    private Optional<PostvisitAnalysisContent> loadPreviousAnalysis(String operatingCaseId) {
        return analysisContentRepo.findLatestByOperatingCaseId(operatingCaseId);
    }

    /**
     * 完成旅程
     */
    @Transactional
    public void completeJourney(String journeyId) {
        CustomerJourney journey = journeyService.findJourneyById(UUID.fromString(journeyId));
        if (journey == null) {
            throw new IllegalArgumentException("Journey not found: " + journeyId);
        }
        if (journey.phase() == JourneyPhase.COMPLETED) {
            throw new IllegalStateException("Journey already completed: " + journeyId);
        }
        journeyRepo.updateJourneyPhase(UUID.fromString(journeyId), JourneyPhase.COMPLETED);
        businessMetrics.recordJourneyCompleted();
    }

    // --- 结果记录 ---

    public record PrevisitWorkflowResult(
        PrevisitReportContent previsitReport,
        QuickBattleCard battleCard,
        List<com.gien.gits.engagement.port.SkillExecutionResult.TraceStep> assemblyTrace,
        String skillReportTitle,
        String skillExecutiveSummary,
        List<com.gien.gits.api.dto.SkillReportSection> skillSections) {
        public PrevisitWorkflowResult {
            assemblyTrace = assemblyTrace == null ? List.of() : List.copyOf(assemblyTrace);
            skillSections = skillSections == null ? List.of() : List.copyOf(skillSections);
        }

        public PrevisitWorkflowResult(PrevisitReportContent previsitReport, QuickBattleCard battleCard) {
            this(previsitReport, battleCard, List.of(), null, null, List.of());
        }
    }

    public record PostvisitWorkflowResult(
        MeetingTranscript transcript,
        PostvisitAnalysisContent analysis,
        RelationshipReport internalReport,
        RelationshipReport crmReport,
        List<CrmWritebackCommand> crmCommands) {}

    public record NewEvidenceWorkflowResult(
        RelationshipReport updatedReport,
        RelationshipReport nextPrevisitReport) {}
}
