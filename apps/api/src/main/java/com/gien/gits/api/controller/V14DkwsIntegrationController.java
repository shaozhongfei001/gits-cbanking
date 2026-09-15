package com.gien.gits.api.controller;

import com.gien.gits.engagement.port.GateAssets;
import com.gien.gits.engagement.port.InteractionMemoryExtraction;
import com.gien.gits.engagement.port.InteractionMemoryPort;
import com.gien.gits.engagement.port.ServiceProposal;
import com.gien.gits.engagement.port.ServiceProposalCommand;
import com.gien.gits.engagement.port.ServiceProposalPort;
import com.gien.gits.engagement.port.SkillGatePort;
import com.gien.gits.engagement.service.GateStateMachine;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * V1.4 DKWS 集成端点：SP-20 服务建议书、SP-21 交互记忆、闸门协作。
 *
 * <p>闸门权威状态机在 GITS：{@code GET /api/v14/gates/{customerId}/state} 返回权威快照；
 * 决策镜像走 {@code POST /api/v14/gates/audit}（失败不影响权威状态）。</p>
 */
@RestController
@RequestMapping("/api/v14")
public class V14DkwsIntegrationController {

    private final ServiceProposalPort serviceProposalPort;
    private final InteractionMemoryPort interactionMemoryPort;
    private final SkillGatePort skillGatePort;

    public V14DkwsIntegrationController(ServiceProposalPort serviceProposalPort,
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
