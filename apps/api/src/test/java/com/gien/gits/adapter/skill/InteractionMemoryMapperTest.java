package com.gien.gits.adapter.skill;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.engagement.port.InteractionMemoryExtraction;
import org.junit.jupiter.api.Test;

/**
 * 对齐真实样例 {@code docs/architecture/DKWS-V1.4-GITS-INTEGRATION-SAMPLES.md} §3：
 * data.result → 强类型 InteractionMemoryExtraction；缺失回退空实例。
 */
class InteractionMemoryMapperTest {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final InteractionMemoryMapper mapper = new InteractionMemoryMapper(objectMapper);

    private static final String SAMPLE = """
        {
          "schemaVersion": "1.0.0",
          "interactionId": "INT-20260823-001",
          "status": "SUCCESS",
          "candidateMemories": [
            {"memoryId": "MEM-001", "category": "COMMITMENT", "confidence": 0.9,
             "suggestedDecayRule": "NONE", "evidenceQuote": "客户：下月提供担保函",
             "content": "客户承诺下月提交担保函"}
          ],
          "memoryUpdates": [
            {"memoryId": "MEM-007", "action": "REINFORCE", "confidenceDelta": 0.05,
             "reason": "本次交互再次确认授信偏好"}
          ],
          "memorySupersessions": [
            {"supersededMemoryId": "MEM-012", "newMemoryId": "MEM-013",
             "reason": "客户变更供应链融资方案"}
          ],
          "ruleViolations": []
        }
        """;

    @Test
    void mapsSampleResult() throws Exception {
        JsonNode result = objectMapper.readTree(SAMPLE);

        InteractionMemoryExtraction extraction = mapper.fromResult(result, "INT-20260823-001");

        assertThat(extraction.schemaVersion()).isEqualTo("1.0.0");
        assertThat(extraction.interactionId()).isEqualTo("INT-20260823-001");
        assertThat(extraction.candidateMemories()).hasSize(1);
        InteractionMemoryExtraction.CandidateMemory c = extraction.candidateMemories().get(0);
        assertThat(c.memoryId()).isEqualTo("MEM-001");
        assertThat(c.category()).isEqualTo("COMMITMENT");
        assertThat(c.confidence()).isEqualTo(0.9);
        assertThat(c.suggestedDecayRule()).isEqualTo("NONE");
        assertThat(c.evidenceQuote()).contains("担保函");
        assertThat(extraction.memoryUpdates()).hasSize(1);
        assertThat(extraction.memoryUpdates().get(0).confidenceDelta()).isEqualTo(0.05);
        assertThat(extraction.memorySupersessions()).hasSize(1);
        assertThat(extraction.memorySupersessions().get(0).supersededMemoryId()).isEqualTo("MEM-012");
        assertThat(extraction.ruleViolations()).isEmpty();
    }

    @Test
    void mapsBlockingViolation() throws Exception {
        String partial = """
            {"schemaVersion":"1.0.0","interactionId":"INT-X","status":"PARTIAL",
             "candidateMemories":[],"memoryUpdates":[],"memorySupersessions":[],
             "ruleViolations":[{"code":"SP21-1","severity":"BLOCKING","message":"记忆内容为空"}]}
            """;
        InteractionMemoryExtraction extraction = mapper.fromResult(objectMapper.readTree(partial), "INT-X");

        assertThat(extraction.status()).isEqualTo("PARTIAL");
        assertThat(extraction.ruleViolations()).hasSize(1);
        assertThat(extraction.ruleViolations().get(0).isBlocking()).isTrue();
    }

    @Test
    void missingResultReturnsEmpty() {
        InteractionMemoryExtraction extraction = mapper.fromResult(null, "INT-EMPTY");
        assertThat(extraction.interactionId()).isEqualTo("INT-EMPTY");
        assertThat(extraction.candidateMemories()).isEmpty();
        assertThat(extraction.status()).isEqualTo("SUCCESS");
    }

    @Test
    void unknownFieldsIgnored() throws Exception {
        String extra = """
            {"schemaVersion":"1.0.0","interactionId":"INT-Y","status":"SUCCESS",
             "candidateMemories":[],"memoryUpdates":[],"memorySupersessions":[],
             "someFutureField":42,"ruleViolations":[]}
            """;
        InteractionMemoryExtraction extraction = mapper.fromResult(objectMapper.readTree(extra), "INT-Y");
        assertThat(extraction.interactionId()).isEqualTo("INT-Y");
    }
}
