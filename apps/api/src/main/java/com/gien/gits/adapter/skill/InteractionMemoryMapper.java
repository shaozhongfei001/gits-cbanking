package com.gien.gits.adapter.skill;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.engagement.port.InteractionMemoryExtraction;

import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 将 DKWS SP-21 {@code data.result}（JsonNode）映射为强类型 {@link InteractionMemoryExtraction}。
 *
 * <p>对齐样例 {@code docs/architecture/DKWS-V1.4-GITS-INTEGRATION-SAMPLES.md} §3；
 * 未知字段忽略（契约 §5）；字段缺失回退空实例而非失败。</p>
 */
public class InteractionMemoryMapper {

    private static final Logger log = LoggerFactory.getLogger(InteractionMemoryMapper.class);

    private final ObjectMapper objectMapper;

    public InteractionMemoryMapper(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    /**
     * @param result DKWS {@code data.result} JsonNode
     * @param interactionId 交互 ID（result 缺失时用于空实例）
     * @return 强类型抽取结果；result 为 null/missing 时返回空抽取
     */
    public InteractionMemoryExtraction fromResult(JsonNode result, String interactionId) {
        if (result == null || result.isMissingNode() || result.isNull()) {
            log.warn("[SP-21] data.result 缺失，返回空抽取 interactionId={}", interactionId);
            return InteractionMemoryExtraction.empty(interactionId);
        }
        try {
            List<InteractionMemoryExtraction.CandidateMemory> candidates = new ArrayList<>();
            JsonNode cm = result.path("candidateMemories");
            if (cm.isArray()) {
                for (JsonNode item : cm) {
                    candidates.add(new InteractionMemoryExtraction.CandidateMemory(
                        item.path("memoryId").asText(),
                        item.path("category").asText(),
                        item.path("confidence").asDouble(0.0),
                        item.path("suggestedDecayRule").asText("NONE"),
                        item.path("evidenceQuote").asText(),
                        item.path("content").asText()));
                }
            }
            List<InteractionMemoryExtraction.MemoryUpdate> updates = new ArrayList<>();
            JsonNode mu = result.path("memoryUpdates");
            if (mu.isArray()) {
                for (JsonNode item : mu) {
                    updates.add(new InteractionMemoryExtraction.MemoryUpdate(
                        item.path("memoryId").asText(),
                        item.path("action").asText("REINFORCE"),
                        item.path("confidenceDelta").asDouble(0.0),
                        item.path("reason").asText()));
                }
            }
            List<InteractionMemoryExtraction.MemorySupersession> supersessions = new ArrayList<>();
            JsonNode ms = result.path("memorySupersessions");
            if (ms.isArray()) {
                for (JsonNode item : ms) {
                    supersessions.add(new InteractionMemoryExtraction.MemorySupersession(
                        item.path("supersededMemoryId").asText(),
                        item.path("newMemoryId").asText(),
                        item.path("reason").asText()));
                }
            }
            List<InteractionMemoryExtraction.RuleViolation> violations = new ArrayList<>();
            JsonNode rv = result.path("ruleViolations");
            if (rv.isArray()) {
                for (JsonNode item : rv) {
                    violations.add(new InteractionMemoryExtraction.RuleViolation(
                        item.path("code").asText(),
                        item.path("severity").asText(),
                        item.path("message").asText()));
                }
            }
            return new InteractionMemoryExtraction(
                result.path("schemaVersion").asText("1.0.0"),
                result.path("interactionId").asText(interactionId),
                result.path("status").asText("SUCCESS"),
                candidates, updates, supersessions, violations);
        } catch (Exception e) {
            log.error("[SP-21] data.result 强类型映射失败，返回空抽取: {}", e.getMessage());
            return InteractionMemoryExtraction.empty(interactionId);
        }
    }
}
