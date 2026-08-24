package com.gien.gits.adapter.skill;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;

import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
import org.springframework.test.web.client.MockRestServiceServer;

/**
 * 验证 {@link DshHttpSkillExecutionAdapter} 按契约
 * {@code docs/dd/skill-execute-api-contract.md} 解析 dsh 响应。
 */
class DshHttpSkillExecutionAdapterTest {

    private RestClient.Builder builder;
    private MockRestServiceServer server;
    private DshHttpSkillExecutionAdapter adapter;

    @BeforeEach
    void setUp() {
        builder = RestClient.builder();
        server = MockRestServiceServer.bindTo(builder).build();
        adapter = new DshHttpSkillExecutionAdapter(builder, "http://dsh.local:3080");
    }

    private SkillExecutionCommand cmd() {
        return new SkillExecutionCommand(
            "skill-customer-previsit-report", "req-abc", "CUST-CORP-0001",
            Map.of("visitObjective", "供应链金融"));
    }

    @Test
    void executeOkParsesContract() {
        server.expect(requestTo("http://dsh.local:3080/api/skill/execute"))
            .andRespond(withSuccess(
                "{\"requestId\":\"req-abc\",\"status\":\"ok\","
                + "\"data\":{\"reportId\":\"R-001\",\"visitStrategy\":\"...\"},"
                + "\"errors\":[],"
                + "\"assemblyTrace\":[{\"phase\":\"read_map\",\"status\":\"ok\",\"message\":\"读图\"}],"
                + "\"modelCalls\":[{\"model\":\"deepseek-chat\",\"inputTokens\":120,\"outputTokens\":80,\"latencyMs\":540}]}",
                MediaType.APPLICATION_JSON));

        SkillExecutionResult result = adapter.execute(cmd());

        assertThat(result.isOk()).isTrue();
        assertThat(result.status()).isEqualTo(SkillExecutionStatus.OK);
        assertThat(result.requestId()).isEqualTo("req-abc");
        assertThat(result.data()).containsEntry("reportId", "R-001");
        assertThat(result.trace()).hasSize(1);
        assertThat(result.trace().get(0).phase()).isEqualTo("read_map");
        assertThat(result.trace().get(0).status()).isEqualTo("ok");
        assertThat(result.modelCalls()).hasSize(1);
        assertThat(result.modelCalls().get(0).model()).isEqualTo("deepseek-chat");
        server.verify();
    }

    @Test
    void executeOkParsesOptionalKiId() {
        server.expect(requestTo("http://dsh.local:3080/api/skill/execute"))
            .andRespond(withSuccess(
                "{\"requestId\":\"req-abc\",\"status\":\"ok\",\"data\":{},\"errors\":[],"
                + "\"assemblyTrace\":["
                + "{\"phase\":\"evidence\",\"status\":\"ok\",\"kiId\":\"KI-009\","
                + "\"message\":\"读取知识条目 KI-009\"},"
                + "{\"phase\":\"model\",\"status\":\"ok\",\"message\":\"模型调用完成\"}"
                + "],\"modelCalls\":[]}",
                MediaType.APPLICATION_JSON));

        SkillExecutionResult result = adapter.execute(cmd());

        assertThat(result.trace().get(0).kiId()).isEqualTo("KI-009");
        assertThat(result.trace().get(1).kiId()).isNull();
        server.verify();
    }

    @Test
    void executeExitPolicyNoNewEvidence() {
        server.expect(requestTo("http://dsh.local:3080/api/skill/execute"))
            .andRespond(withSuccess(
                "{\"requestId\":\"req-abc\",\"status\":\"exit_policy_no_new_evidence\","
                + "\"data\":{},\"errors\":[],\"assemblyTrace\":[],\"modelCalls\":[]}",
                MediaType.APPLICATION_JSON));

        SkillExecutionResult result = adapter.execute(cmd());
        assertThat(result.status()).isEqualTo(SkillExecutionStatus.EXIT_POLICY_NO_NEW_EVIDENCE);
        assertThat(result.isOk()).isFalse();
        server.verify();
    }

    @Test
    void executeSkillErrorParsesErrors() {
        server.expect(requestTo("http://dsh.local:3080/api/skill/execute"))
            .andRespond(withSuccess(
                "{\"requestId\":\"req-abc\",\"status\":\"skill_error\",\"data\":{},"
                + "\"errors\":[{\"code\":\"MODEL_TIMEOUT\",\"message\":\"模型超时\"}],"
                + "\"assemblyTrace\":[],\"modelCalls\":[]}",
                MediaType.APPLICATION_JSON));

        SkillExecutionResult result = adapter.execute(cmd());
        assertThat(result.status()).isEqualTo(SkillExecutionStatus.SKILL_ERROR);
        assertThat(result.errors()).hasSize(1);
        assertThat(result.errors().get(0).code()).isEqualTo("MODEL_TIMEOUT");
        server.verify();
    }

    @Test
    void unknownSkillReturnsErrorAndIsMapped() {
        server.expect(requestTo("http://dsh.local:3080/api/skill/execute"))
            .andRespond(withStatus(
                org.springframework.http.HttpStatus.NOT_FOUND)
                .body("{\"requestId\":\"req-abc\",\"status\":\"skill_error\",\"data\":{},"
                    + "\"errors\":[{\"code\":\"UNKNOWN_SKILL\",\"message\":\"未知技能\"}],"
                    + "\"assemblyTrace\":[],\"modelCalls\":[]}")
                .contentType(MediaType.APPLICATION_JSON));

        // 契约 §1: 未知 skillId → 404; gits 侧 as异常，调用方回落 fallback。
        assertThatThrownBy(() -> adapter.execute(cmd()))
            .isInstanceOf(SkillExecutionException.class)
            .hasMessageContaining("SKILL HTTP 404");
        server.verify();
    }

    @Test
    void executeAsyncPollUntilCompleted() {
        server.expect(requestTo("http://dsh.local:3080/api/skill/execute"))
            .andRespond(withStatus(org.springframework.http.HttpStatus.ACCEPTED)
                .body("{\"jobId\":\"JOB-SKILL-20260824-001\",\"status\":\"PENDING\"}")
                .contentType(MediaType.APPLICATION_JSON));
        server.expect(requestTo("http://dsh.local:3080/v1/jobs/JOB-SKILL-20260824-001"))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-SKILL-20260824-001\",\"status\":\"ok\",\"data\":{\"status\":\"COMPLETED\","
                + "\"skill_result\":{\"requestId\":\"req-abc\",\"status\":\"ok\","
                + "\"data\":{\"reportId\":\"R-ASYNC\"},\"errors\":[],\"assemblyTrace\":[],\"modelCalls\":[]}}}",
                MediaType.APPLICATION_JSON));

        SkillExecutionCommand asyncCmd = new SkillExecutionCommand(
            "skill-customer-previsit-report", "req-abc", "CUST-CORP-0001",
            Map.of("visitObjective", "供应链金融"), true, Map.of());
        SkillExecutionResult result = adapter.execute(asyncCmd);

        assertThat(result.isOk()).isTrue();
        assertThat(result.data()).containsEntry("reportId", "R-ASYNC");
        server.verify();
    }

    @Test
    void executeAsyncJobFailedThrows() {
        server.expect(requestTo("http://dsh.local:3080/api/skill/execute"))
            .andRespond(withStatus(org.springframework.http.HttpStatus.ACCEPTED)
                .body("{\"jobId\":\"JOB-SKILL-20260824-002\",\"status\":\"PENDING\"}")
                .contentType(MediaType.APPLICATION_JSON));
        server.expect(requestTo("http://dsh.local:3080/v1/jobs/JOB-SKILL-20260824-002"))
            .andRespond(withSuccess(
                "{\"jobId\":\"JOB-SKILL-20260824-002\",\"status\":\"ok\","
                + "\"data\":{\"status\":\"FAILED\"}}",
                MediaType.APPLICATION_JSON));

        SkillExecutionCommand asyncCmd = new SkillExecutionCommand(
            "skill-customer-previsit-report", "req-abc", "CUST-CORP-0001",
            Map.of("visitObjective", "供应链金融"), true, Map.of());

        assertThatThrownBy(() -> adapter.execute(asyncCmd))
            .isInstanceOf(SkillExecutionException.class)
            .hasMessageContaining("job failed");
        server.verify();
    }

    @Test
    void contractPayloadIncludesAsyncAndMergesContext() {
        SkillExecutionCommand cmd = new SkillExecutionCommand(
            "skill-customer-previsit-report", "req-abc", "CUST-CORP-0001",
            Map.of("visitObjective", "供应链金融", "context", Map.of("requestCtx", "req-ctx")),
            true, Map.of("version", "1.4", "customerVersion", Map.of("label", "内部")));

        Map<String, Object> payload = DshHttpSkillExecutionAdapter.contractPayload(cmd);

        assertThat(payload.get("async")).isEqualTo(Boolean.TRUE);
        assertThat(payload.get("skillId")).isEqualTo("skill-customer-previsit-report");
        Map<?, ?> request = (Map<?, ?>) payload.get("request");
        assertThat(request.get("customerId")).isEqualTo("CUST-CORP-0001");
        Map<?, ?> merged = (Map<?, ?>) request.get("context");
        assertThat(merged.get("version")).isEqualTo("1.4");
        assertThat(merged.get("requestCtx")).isEqualTo("req-ctx"); // request.context 优先
    }
}