package com.gien.gits.adapter.skill;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.engagement.port.ServiceProposal;
import org.junit.jupiter.api.Test;

/**
 * 对齐真实样例 {@code docs/architecture/DKWS-V1.4-GITS-INTEGRATION-SAMPLES.md} §2.4：
 * data.result → 强类型 ServiceProposal；未知字段忽略；缺失回退空实例。
 */
class ServiceProposalMapperTest {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final ServiceProposalMapper mapper = new ServiceProposalMapper(objectMapper);

    private static final String SAMPLE = """
        {
          "schemaVersion": "1.0.0",
          "skillId": "SP-20",
          "runId": "RUN-SP20-20260823-001",
          "status": "SUCCESS",
          "timestamp": "2026-08-23T10:15:00Z",
          "content": {
            "proposalDraft": "## 1. 客户经营现状与核心诉求",
            "internalVersion": {
              "content": "### 1.1 客户经营现状（内部）",
              "factLabels": {"F-001": "F", "I-001": "I"}
            },
            "customerVersion": {
              "content": "### 1.1 客户经营现状",
              "filteringNotes": ["仅保留 F/A 事实"],
              "includes": ["F-001"],
              "excludes": ["I-001"],
              "releaseBlockedUntil": []
            },
            "customerVersionNote": "对客版已按规则过滤"
          },
          "citations": [
            {"id": "C-001", "claim": "集团授信额度", "source": "CRM", "date": "2026-08-01", "factLabel": "F", "chapterRef": "CH1"}
          ],
          "unknowns": [
            {"id": "U-001", "description": "担保细节", "suggestedAction": "补充确认", "relatedChapter": "CH4"}
          ],
          "limitations": ["供应链图谱数据时效 T+1"],
          "gateRecommendations": {
            "currentGate": "G2",
            "passedGates": ["G0", "G1"],
            "overallReadiness": "READY_FOR_REVIEW",
            "checklist": [
              {"gate": "G1", "state": "PASSED", "name": "事实基础", "checklist": {"c1": ["ok"]}},
              {"gate": "G2", "state": "READY_FOR_REVIEW", "name": "规则合规", "checklist": {}}
            ],
            "nextGatePrerequisites": ["noBlockingViolations"]
          },
          "ruleViolations": []
        }
        """;

    @Test
    void mapsSampleResult() throws Exception {
        JsonNode result = objectMapper.readTree(SAMPLE);

        ServiceProposal proposal = mapper.fromResult(result);

        assertThat(proposal.schemaVersion()).isEqualTo("1.0.0");
        assertThat(proposal.skillId()).isEqualTo("SP-20");
        assertThat(proposal.status()).isEqualTo("SUCCESS");
        assertThat(proposal.content().proposalDraft()).contains("客户经营现状与核心诉求");
        assertThat(proposal.content().internalVersion().factLabels()).containsEntry("F-001", "F");
        assertThat(proposal.content().customerVersion().filteringNotes()).contains("仅保留 F/A 事实");
        assertThat(proposal.content().customerVersion().releaseBlockedUntil()).isEmpty();
        assertThat(proposal.citations()).hasSize(1);
        assertThat(proposal.citations().get(0).factLabel()).isEqualTo("F");
        assertThat(proposal.unknowns()).hasSize(1);
        assertThat(proposal.limitations()).contains("供应链图谱数据时效 T+1");
        assertThat(proposal.gateRecommendations().currentGate()).isEqualTo("G2");
        assertThat(proposal.gateRecommendations().passedGates()).containsExactly("G0", "G1");
        assertThat(proposal.gateRecommendations().checklist()).hasSize(2);
        assertThat(proposal.ruleViolations()).isEmpty();
        // 对客版 releaseBlockedUntil 为空 → 可放行
        assertThat(proposal.isCustomerVersionReleasable()).isTrue();
    }

    @Test
    void mapsBlockingViolationAsPartial() throws Exception {
        String partial = """
            {"schemaVersion":"1.0.0","skillId":"SP-20","runId":"R2","status":"PARTIAL","timestamp":"T",
             "content":{"proposalDraft":"","internalVersion":null,"customerVersion":null,"customerVersionNote":""},
             "citations":[],"unknowns":[],"limitations":[],
             "gateRecommendations":{"currentGate":"G2","passedGates":["G0"],"overallReadiness":"BLOCKED",
               "checklist":[{"gate":"G2","state":"BLOCKED","name":"规则合规","checklist":{}}],
               "nextGatePrerequisites":["noBlockingViolations"]},
             "ruleViolations":[{"code":"SP20-6","severity":"BLOCKING","message":"对客版含未授权事实","ruleRef":"R6"}]}
            """;
        ServiceProposal proposal = mapper.fromResult(objectMapper.readTree(partial));

        assertThat(proposal.status()).isEqualTo("PARTIAL");
        assertThat(proposal.ruleViolations()).hasSize(1);
        assertThat(proposal.ruleViolations().get(0).isBlocking()).isTrue();
        assertThat(proposal.isCustomerVersionReleasable()).isFalse();
    }

    @Test
    void missingResultReturnsEmpty() {
        ServiceProposal proposal = mapper.fromResult(null);
        assertThat(proposal.status()).isEqualTo("SUCCESS");
        assertThat(proposal.content().proposalDraft()).isEmpty();
    }

    @Test
    void unknownFieldsIgnored() throws Exception {
        String extra = """
            {"schemaVersion":"1.0.0","skillId":"SP-20","runId":"R3","status":"SUCCESS","timestamp":"T",
             "someFutureField":{"a":1},"content":{"proposalDraft":"x","internalVersion":null,
               "customerVersion":{"content":"","factLabels":{},"filteringNotes":[],"includes":[],"excludes":[],"releaseBlockedUntil":[]},
               "customerVersionNote":""},
             "citations":[],"unknowns":[],"limitations":[],"gateRecommendations":null,"ruleViolations":[]}
            """;
        ServiceProposal proposal = mapper.fromResult(objectMapper.readTree(extra));
        // 未知字段被忽略，不抛错
        assertThat(proposal.runId()).isEqualTo("R3");
        assertThat(proposal.content().proposalDraft()).isEqualTo("x");
    }
}
