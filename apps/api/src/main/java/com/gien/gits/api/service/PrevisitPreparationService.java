package com.gien.gits.api.service;

import com.gien.gits.engagement.MeetingScript;
import com.gien.gits.engagement.OutreachScript;
import com.gien.gits.engagement.OutreachScript.OutreachChannel;
import com.gien.gits.engagement.QuickBattleCard;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 访前自动准备编排（P23/G6）：进入访前准备阶段后，按知识地图任务映射一键生成完整访前包。
 *
 * <p>合并"生成外联脚本 / 生成会面脚本 / 执行访前准备"三个动作为一次调用：
 * <ol>
 *   <li>外联脚本（知识地图 KI-FRONT-004 沟通话术驱动）</li>
 *   <li>会面脚本（KI-FRONT-002/003/004 经营/对账/话术驱动）</li>
 *   <li>访前报告 R1 + 速战卡 R2（KI-009 客户信息 + KI-FRONT-001~006 全条目驱动）</li>
 * </ol>
 * 三项互不依赖，并行打 DKWS，避免串行墙钟超过浏览器超时。
 * 任一环节抛异常按 fail-closed 不返回部分结果。客户目录未命中仍抛错。
 * Skill 失败或空 data 时外联/会面返回空结构（不抛），以便 R1 仍可执行。</p>
 */
public final class PrevisitPreparationService {

    private static final Logger log = LoggerFactory.getLogger(PrevisitPreparationService.class);

    private static final Executor SKILL_FANOUT = Executors.newFixedThreadPool(3, runnable -> {
        Thread thread = new Thread(runnable, "prepare-previsit-dkws");
        thread.setDaemon(true);
        return thread;
    });

    private final OutreachScriptService outreachScriptService;
    private final MeetingScriptService meetingScriptService;
    private final EngagementOrchestrator orchestrator;

    public PrevisitPreparationService(
            OutreachScriptService outreachScriptService,
            MeetingScriptService meetingScriptService,
            EngagementOrchestrator orchestrator) {
        this.outreachScriptService = Objects.requireNonNull(outreachScriptService);
        this.meetingScriptService = Objects.requireNonNull(meetingScriptService);
        this.orchestrator = Objects.requireNonNull(orchestrator);
    }

    /**
     * 一键生成完整访前包。
     *
     * @return 外联脚本 + 会面脚本 + 访前报告 + 速战卡
     */
    public PreparedPrevisit prepare(
            String journeyId, String customerId, String rmId,
            String operatingCaseId, String visitObjective, OutreachChannel channel) {

        Objects.requireNonNull(journeyId, "journeyId");
        Objects.requireNonNull(customerId, "customerId");
        Objects.requireNonNull(operatingCaseId, "operatingCaseId");

        log.info("[PREPARE-PREVISIT] DKWS fan-out customerId={} journeyId={} skills={},{},{}",
                customerId, journeyId,
                OutreachScriptService.OUTREACH_SKILL_ID,
                MeetingScriptService.MEETING_SKILL_ID,
                KnowledgeDrivenPrevisitReportGenerator.PREVISIT_SKILL_ID);

        CompletableFuture<OutreachScript> outreachF = CompletableFuture.supplyAsync(
                () -> outreachScriptService.generateScript(
                        customerId, rmId, operatingCaseId, journeyId, channel),
                SKILL_FANOUT);
        CompletableFuture<MeetingScript> meetingF = CompletableFuture.supplyAsync(
                () -> meetingScriptService.generateScript(
                        customerId, rmId, operatingCaseId, journeyId),
                SKILL_FANOUT);
        CompletableFuture<EngagementOrchestrator.PrevisitWorkflowResult> previsitF =
                CompletableFuture.supplyAsync(
                        () -> orchestrator.executePrevisitPhase(
                                journeyId, customerId, operatingCaseId, visitObjective),
                        SKILL_FANOUT);

        try {
            CompletableFuture.allOf(outreachF, meetingF, previsitF).join();
        } catch (CompletionException ex) {
            Throwable cause = ex.getCause() == null ? ex : ex.getCause();
            if (cause instanceof RuntimeException runtime) {
                throw runtime;
            }
            throw ex;
        }

        OutreachScript outreach = outreachF.join();
        MeetingScript meeting = meetingF.join();
        EngagementOrchestrator.PrevisitWorkflowResult previsit = previsitF.join();

        return new PreparedPrevisit(
                outreach, meeting, previsit.previsitReport(), previsit.battleCard(), previsit.assemblyTrace(),
                previsit.skillReportTitle(), previsit.skillExecutiveSummary(), previsit.skillSections());
    }

    /** 完整访前包（外联 + 会面 + R1 + R2 + DSH 轨迹）。 */
    public record PreparedPrevisit(
            OutreachScript outreachScript,
            MeetingScript meetingScript,
            com.gien.gits.engagement.PrevisitReportContent previsitReport,
            QuickBattleCard battleCard,
            List<com.gien.gits.engagement.port.SkillExecutionResult.TraceStep> assemblyTrace,
            String skillReportTitle,
            String skillExecutiveSummary,
            List<com.gien.gits.api.dto.SkillReportSection> skillSections) {
        public PreparedPrevisit {
            assemblyTrace = assemblyTrace == null ? List.of() : List.copyOf(assemblyTrace);
            skillSections = skillSections == null ? List.of() : List.copyOf(skillSections);
        }
    }
}
