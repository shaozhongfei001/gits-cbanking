package com.gien.gits.api.controller;

import com.gien.gits.api.dto.JourneyCompleteResponse;
import com.gien.gits.api.dto.JourneyStartResponse;
import com.gien.gits.api.dto.NewEvidenceResponse;
import com.gien.gits.api.dto.PostvisitExecutionResponse;
import com.gien.gits.api.dto.PrevisitExecutionResponse;
import com.gien.gits.api.dto.PreparedPrevisitResponse;
import com.gien.gits.api.dto.AssemblyTraceStep;
import com.gien.gits.api.service.EngagementOrchestrator;
import com.gien.gits.api.service.MeetingScriptService;
import com.gien.gits.api.service.OutreachScriptService;
import com.gien.gits.api.service.PrevisitPreparationService;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.port.CustomerJourneyRepository;
import com.gien.gits.engagement.MeetingScript;
import com.gien.gits.engagement.OutreachScript;
import com.gien.gits.engagement.OutreachScript.OutreachChannel;
import com.gien.gits.engagement.port.OutreachScriptRepository;
import com.gien.gits.engagement.port.MeetingScriptRepository;
import com.gien.gits.ontology.KycGapProfile;
import com.gien.gits.ontology.RelationshipReport;
import com.gien.gits.ontology.port.RelationshipReportRepository;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * 旅程管理控制器 — 持续经营旅程生命周期
 */
@RestController
@RequestMapping("/api/v1/engagement/journey")
public class EngagementJourneyController {

    private final EngagementOrchestrator orchestrator;
    private final OutreachScriptService outreachScriptService;
    private final MeetingScriptService meetingScriptService;
    private final OutreachScriptRepository outreachScriptRepository;
    private final MeetingScriptRepository meetingScriptRepository;
    private final PrevisitPreparationService previsitPreparationService;
    private final CustomerJourneyRepository journeyRepository;
    private final RelationshipReportRepository reportRepository;

    public EngagementJourneyController(
            EngagementOrchestrator orchestrator,
            OutreachScriptService outreachScriptService,
            MeetingScriptService meetingScriptService,
            OutreachScriptRepository outreachScriptRepository,
            MeetingScriptRepository meetingScriptRepository,
            PrevisitPreparationService previsitPreparationService,
            CustomerJourneyRepository journeyRepository,
            RelationshipReportRepository reportRepository) {
        this.orchestrator = Objects.requireNonNull(orchestrator);
        this.outreachScriptService = Objects.requireNonNull(outreachScriptService);
        this.meetingScriptService = Objects.requireNonNull(meetingScriptService);
        this.outreachScriptRepository = Objects.requireNonNull(outreachScriptRepository);
        this.meetingScriptRepository = Objects.requireNonNull(meetingScriptRepository);
        this.previsitPreparationService = Objects.requireNonNull(previsitPreparationService);
        this.journeyRepository = Objects.requireNonNull(journeyRepository);
        this.reportRepository = Objects.requireNonNull(reportRepository);
    }

    /**
     * 根据客户ID查询该客户的旅程列表。
     */
    @GetMapping
    public ResponseEntity<List<CustomerJourney>> listJourneysByCustomer(
            @RequestParam("customerId") String customerId) {
        List<CustomerJourney> journeys = journeyRepository.findJourneysByCustomerId(customerId);
        return ResponseEntity.ok(journeys);
    }

    /**
     * 根据旅程ID查询旅程详情。
     */
    @GetMapping("/{journeyId}")
    public ResponseEntity<CustomerJourney> getJourney(@PathVariable String journeyId) {
        try {
            return journeyRepository.findJourneyById(UUID.fromString(journeyId))
                    .map(ResponseEntity::ok)
                    .orElse(ResponseEntity.notFound().build());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    /**
     * 根据旅程ID查询关联的报告列表（访前报告、访后报告等）。
     */
    @GetMapping("/{journeyId}/reports")
    public ResponseEntity<List<RelationshipReport>> getJourneyReports(@PathVariable String journeyId) {
        try {
            return journeyRepository.findJourneyById(UUID.fromString(journeyId))
                    .map(journey -> {
                        List<RelationshipReport> reports = reportRepository.findByOperatingCaseId(
                                journey.operatingCaseId().toString());
                        return ResponseEntity.ok(reports);
                    })
                    .orElse(ResponseEntity.ok(List.of()));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PostMapping("/start")
    public ResponseEntity<JourneyStartResponse> startJourney(@RequestBody StartJourneyRequest request) {
        if (request.customerId() == null || request.customerId().isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        EngagementOrchestrator.JourneyStartResult result = orchestrator.startEngagementJourney(request.customerId());
        CustomerJourney journey = result.journey();
        String kycSummary = result.kycProfile().map(p ->
            "未知项:" + p.unknownItems().size() + ",待确认:" + p.priorityQuestions().size()).orElse(null);
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(new JourneyStartResponse(
                journey.journeyId().toString(),
                journey.customerId(),
                result.operatingCaseId(),
                journey.phase().name(),
                journey.startedAt().toString(),
                kycSummary));
    }

    @PostMapping("/{journeyId}/previsit")
    public ResponseEntity<PrevisitExecutionResponse> executePrevisit(
            @PathVariable String journeyId,
            @RequestBody PrevisitRequest request) {
        if (request.customerId() == null || request.customerId().isBlank()
                || request.operatingCaseId() == null || request.operatingCaseId().isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        EngagementOrchestrator.PrevisitWorkflowResult result = orchestrator.executePrevisitPhase(
            journeyId, request.customerId(), request.operatingCaseId(), request.visitObjective());
        return ResponseEntity.ok(new PrevisitExecutionResponse(
            result.previsitReport(), result.battleCard(), null,
            AssemblyTraceStep.from(result.assemblyTrace()),
            result.skillReportTitle(), result.skillExecutiveSummary(), result.skillSections()));
    }

    /**
     * P23/G6：一键访前自动准备（知识地图任务映射驱动）。
     * 合并外联脚本 + 会面脚本 + 访前报告 R1 + 速战卡 R2 为一次调用。
     */
    @PostMapping("/{journeyId}/prepare-previsit")
    public ResponseEntity<PreparedPrevisitResponse> preparePrevisit(
            @PathVariable String journeyId,
            @RequestBody PreparedPrevisitRequest request) {
        if (request.operatingCaseId() == null || request.operatingCaseId().isBlank()
                || request.customerId() == null || request.customerId().isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        OutreachChannel channel;
        try {
            channel = request.channel() == null || request.channel().isBlank()
                    ? OutreachChannel.EMAIL
                    : OutreachChannel.valueOf(request.channel());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
        PrevisitPreparationService.PreparedPrevisit prepared = previsitPreparationService.prepare(
                journeyId, request.customerId(), request.rmId(),
                request.operatingCaseId(), request.visitObjective(), channel);
        return ResponseEntity.ok(new PreparedPrevisitResponse(
                prepared.outreachScript(),
                prepared.meetingScript(),
                prepared.previsitReport(),
                prepared.battleCard(),
                null,
                AssemblyTraceStep.from(prepared.assemblyTrace()),
                prepared.skillReportTitle(),
                prepared.skillExecutiveSummary(),
                prepared.skillSections()));
    }

    @PostMapping("/{journeyId}/postvisit")
    public ResponseEntity<PostvisitExecutionResponse> executePostvisit(
            @PathVariable String journeyId,
            @RequestBody PostvisitRequest request) {
        if (request.operatingCaseId() == null || request.operatingCaseId().isBlank()
                || request.customerId() == null || request.customerId().isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        EngagementOrchestrator.PostvisitWorkflowResult result = orchestrator.executePostvisitPhase(
            journeyId, request.operatingCaseId(), request.customerId(), request.rawTranscript());
        return ResponseEntity.ok(new PostvisitExecutionResponse(
            result.transcript().transcriptId(),
            result.analysis().analysisId(),
            result.internalReport().reportId().toString(),
            result.crmReport().reportId().toString(),
            result.crmCommands().size(),
            true));
    }

    @PostMapping("/{journeyId}/new-evidence")
    public ResponseEntity<NewEvidenceResponse> handleNewEvidence(
            @PathVariable String journeyId,
            @RequestBody NewEvidenceRequest request) {
        if (request.operatingCaseId() == null || request.operatingCaseId().isBlank()
                || request.customerId() == null || request.customerId().isBlank()
                || request.evidenceDescription() == null || request.evidenceDescription().isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        EngagementOrchestrator.NewEvidenceWorkflowResult result = orchestrator.handleNewEvidence(
            journeyId, request.operatingCaseId(), request.customerId(),
            request.evidenceDescription(), request.previousReportId());
        return ResponseEntity.ok(new NewEvidenceResponse(
            result.updatedReport().reportId().toString(),
            result.nextPrevisitReport().reportId().toString()));
    }

    @PostMapping("/{journeyId}/complete")
    public ResponseEntity<JourneyCompleteResponse> completeJourney(@PathVariable String journeyId) {
        orchestrator.completeJourney(journeyId);
        return ResponseEntity.ok(new JourneyCompleteResponse("COMPLETED", journeyId));
    }

    // --- P9 Loop G4: 外联脚本生成 ---

    @PostMapping("/outreach-script")
    public ResponseEntity<OutreachScript> generateOutreachScript(
            @RequestBody OutreachScriptRequest request) {
        OutreachChannel channel;
        try {
            if (request.channel() == null || request.channel().isBlank()) {
                return ResponseEntity.badRequest().build();
            }
            channel = OutreachChannel.valueOf(request.channel());
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
        OutreachScript script = outreachScriptService.generateScript(
            request.customerId(), request.rmId(),
            request.operatingCaseId(), request.journeyId(),
            channel);
        return ResponseEntity.ok(script);
    }

    // --- P9 Loop G5: 会面脚本生成 ---

    @PostMapping("/meeting-script")
    public ResponseEntity<MeetingScript> generateMeetingScript(
            @RequestBody MeetingScriptRequest request) {
        MeetingScript script = meetingScriptService.generateScript(
            request.customerId(), request.rmId(),
            request.operatingCaseId(), request.journeyId());
        return ResponseEntity.ok(script);
    }

    // --- P10: 脚本持久化查询 ---

    @GetMapping("/outreach-scripts")
    public ResponseEntity<List<OutreachScript>> listOutreachScripts(
            @RequestParam String customerId) {
        return ResponseEntity.ok(outreachScriptRepository.findByCustomerId(customerId));
    }

    @GetMapping("/meeting-scripts")
    public ResponseEntity<List<MeetingScript>> listMeetingScripts(
            @RequestParam String customerId) {
        return ResponseEntity.ok(meetingScriptRepository.findByCustomerId(customerId));
    }

    // ========== 请求DTO ==========

    public record StartJourneyRequest(String customerId) {}
    public record PrevisitRequest(String customerId, String operatingCaseId, String visitObjective) {}
    public record PostvisitRequest(String customerId, String operatingCaseId, String rawTranscript) {}
    public record NewEvidenceRequest(String customerId, String operatingCaseId, String evidenceDescription, String previousReportId) {}
    public record OutreachScriptRequest(String customerId, String rmId, String operatingCaseId, String journeyId, String channel) {}
    public record MeetingScriptRequest(String customerId, String rmId, String operatingCaseId, String journeyId) {}
    public record PreparedPrevisitRequest(String customerId, String rmId, String operatingCaseId, String journeyId, String channel, String visitObjective) {}
}
