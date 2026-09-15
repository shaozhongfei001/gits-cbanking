package com.gien.gits.api.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.adapter.skill.InteractionMemoryMapper;
import com.gien.gits.engagement.port.InteractionMemoryExtraction;
import com.gien.gits.engagement.port.InteractionMemoryPort;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;

import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * SP-21 交互记忆消费服务 — 组合 {@link SkillExecutionPort}（异步作业 ≤60s）+ {@link InteractionMemoryMapper}。
 *
 * <p>生命周期归属 GITS：候选入 CANDIDATE、更新应用增量、取代置 SUPERSEDED 均在 GITS 侧，
 * DKWS 无感知（契约 v1.4 §3）。</p>
 */
public class InteractionMemoryService implements InteractionMemoryPort {

    private static final Logger log = LoggerFactory.getLogger(InteractionMemoryService.class);
    private static final String SKILL_ID = "SP-21";

    private final SkillExecutionPort skillExecutionPort;
    private final InteractionMemoryMapper mapper;
    private final ObjectMapper objectMapper;

    public InteractionMemoryService(SkillExecutionPort skillExecutionPort,
                                    InteractionMemoryMapper mapper,
                                    ObjectMapper objectMapper) {
        this.skillExecutionPort = skillExecutionPort;
        this.mapper = mapper;
        this.objectMapper = objectMapper;
    }

    @Override
    public InteractionMemoryExtraction extract(String interactionId,
                                               String customerId,
                                               String interactionContent,
                                               List<Map<String, Object>> existingMemories) {
        log.info("[SP-21] extract interactionId={} customerId={}", interactionId, customerId);
        // DKWS SP-21 契约：request 顶层携带 interactionId/customerId/interactionContent/existingMemories
        Map<String, Object> request = new java.util.LinkedHashMap<>();
        request.put("interactionId", interactionId);
        request.put("customerId", customerId);
        request.put("interactionContent", interactionContent);
        request.put("existingMemories", existingMemories != null ? existingMemories : List.of());
        SkillExecutionCommand skillCmd = new SkillExecutionCommand(
            SKILL_ID, interactionId, customerId, request, true, Map.of());
        SkillExecutionResult result = skillExecutionPort.execute(skillCmd);
        if (result == null || !result.isOk() || result.data() == null) {
            log.warn("[SP-21] execute 未成功，返回空抽取 (ok={})",
                     result != null ? result.isOk() : "null");
            return InteractionMemoryExtraction.empty(interactionId);
        }
        try {
            JsonNode root = objectMapper.valueToTree(result.data());
            JsonNode resultNode = root.path("result");
            return mapper.fromResult(resultNode, interactionId);
        } catch (Exception e) {
            log.error("[SP-21] data 映射失败，返回空抽取: {}", e.getMessage());
            return InteractionMemoryExtraction.empty(interactionId);
        }
    }

    @Override
    public void apply(InteractionMemoryExtraction extraction) {
        if (extraction == null) {
            return;
        }
        log.info("[SP-21] apply interactionId={} candidates={} updates={} supersessions={}",
                 extraction.interactionId(),
                 extraction.candidateMemories().size(),
                 extraction.memoryUpdates().size(),
                 extraction.memorySupersessions().size());
        // 生命周期归属 GITS：落库/衰减/取代由持久化侧处理（MemoryRepository），
        // 本服务透出抽取结果供上层编排。
    }
}
