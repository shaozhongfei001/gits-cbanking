package com.gien.gits.api.controller;

import com.gien.gits.api.dto.ErrorResponse;
import com.gien.gits.engagement.port.GateAssets;
import com.gien.gits.engagement.port.InteractionMemoryExtraction;
import com.gien.gits.engagement.port.InteractionMemoryPort;
import com.gien.gits.engagement.port.KertContractMismatchException;
import com.gien.gits.engagement.port.ServiceProposal;
import com.gien.gits.engagement.port.ServiceProposalCommand;
import com.gien.gits.engagement.port.ServiceProposalPort;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import com.gien.gits.engagement.port.SkillGatePort;
import com.gien.gits.engagement.service.GateStateMachine;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * V1.4 KERT 集成端点：SP-20 服务建议书、SP-21 交互记忆、闸门协作。
 *
 * <p>闸门权威状态机在 GITS：{@code GET /api/v14/gates/{customerId}/state} 返回权威快照；
 * 决策镜像走 {@code POST /api/v14/gates/audit}（失败不影响权威状态）。</p>
 */
@RestController
@RequestMapping("/api/v14")
public class V14KertIntegrationController {

    private static final Logger log = LoggerFactory.getLogger(V14KertIntegrationController.class);

    private final ServiceProposalPort serviceProposalPort;
    private final InteractionMemoryPort interactionMemoryPort;
    private final SkillGatePort skillGatePort;

    public V14KertIntegrationController(ServiceProposalPort serviceProposalPort,
                                        InteractionMemoryPort interactionMemoryPort,
                                        SkillGatePort skillGatePort) {
        this.serviceProposalPort = Objects.requireNonNull(serviceProposalPort);
        this.interactionMemoryPort = Objects.requireNonNull(interactionMemoryPort);
        this.skillGatePort = Objects.requireNonNull(skillGatePort);
    }

    // --- SP-20: 服务建议书 ---

    @PostMapping("/proposals")
    public ResponseEntity<ServiceProposal> generateProposal(
            @RequestBody ServiceProposalCommand command) {
        return ResponseEntity.ok(serviceProposalPort.generate(command));
    }

    // ── P1：SP-20 失败语义（**不静默降级**；此前为「HTTP 200 + SUCCESS 空壳」）─────────
    // 契约（ServiceProposalPort）明示「失败必须抛异常（不静默降级）」；此处把三类失败如实映射为 HTTP 错误，
    // 前端才能区分：KERT 不可用（503，可重试）/ 契约不符（502，重试无用）/ 策略拒绝（409，业务态）。
    // **不**引入本地兜底、**不**写权威制品 ⇒ 与 fail-closed 方向一致。

    @ExceptionHandler(KertContractMismatchException.class)
    public ResponseEntity<ErrorResponse> kertContractMismatch(KertContractMismatchException ex) {
        log.error("[v14][SP-20] KERT 契约不符（502）: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(new ErrorResponse(
                "KERT_CONTRACT_MISMATCH", ex.getMessage(), Instant.now().toString()));
    }

    @ExceptionHandler(SkillExecutionException.class)
    public ResponseEntity<ErrorResponse> skillExecutionFailed(SkillExecutionException ex) {
        boolean policyExit = ex.status() == SkillExecutionStatus.EXIT_POLICY_NO_NEW_EVIDENCE;
        HttpStatus status = policyExit ? HttpStatus.CONFLICT : HttpStatus.SERVICE_UNAVAILABLE;
        String code = policyExit ? "EXIT_POLICY_NO_NEW_EVIDENCE" : "KERT_UNAVAILABLE";
        log.error("[v14][SP-20] KERT 执行失败（{} {}）: {}", status.value(), code, ex.getMessage());
        return ResponseEntity.status(status).body(new ErrorResponse(
                code, ex.getMessage(), Instant.now().toString()));
    }

    // --- SP-21: 交互记忆抽取 ---

    @PostMapping("/memories/extract")
    public ResponseEntity<InteractionMemoryExtraction> extractMemories(
            @RequestBody Map<String, Object> body) {
        String interactionId = String.valueOf(
            body.getOrDefault("interactionId", "INT-" + UUID.randomUUID()));
        String customerId = String.valueOf(body.getOrDefault("customerId", ""));
        String content = String.valueOf(body.getOrDefault("interactionContent", ""));
        List<Map<String, Object>> existingMemories = (List<Map<String, Object>>)
            body.getOrDefault("existingMemories", List.of());
        return ResponseEntity.ok(
            interactionMemoryPort.extract(interactionId, customerId, content, existingMemories));
    }

    // --- 闸门协作（权威状态机在 GITS） ---

    @GetMapping("/gates/assets/{customerId}")
    public ResponseEntity<GateAssets> fetchGateAssets(@PathVariable String customerId) {
        return ResponseEntity.ok(skillGatePort.fetchGateAssets(customerId));
    }

    @GetMapping("/gates/state/{customerId}")
    public ResponseEntity<Map<String, Object>> gateState(@PathVariable String customerId) {
        GateAssets assets = skillGatePort.fetchGateAssets(customerId);
        GateStateMachine machine = new GateStateMachine(customerId, assets);
        return ResponseEntity.ok(machine.snapshot());
    }

    @PostMapping("/gates/audit")
    public ResponseEntity<Map<String, Object>> mirrorAudit(
            @RequestBody Map<String, Object> auditEntry) {
        String customerId = String.valueOf(auditEntry.getOrDefault("customerId", ""));
        boolean recorded = skillGatePort.mirrorGateAudit(customerId, auditEntry);
        return ResponseEntity.ok(Map.of("recorded", recorded));
    }
}
