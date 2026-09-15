package com.gien.gits.adapter.skill;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withException;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import com.gien.gits.engagement.port.LlmClient;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

/**
 * 产品推荐 Skill（SP-15）KERT HTTP 适配器契约测试。
 *
 * <p>对齐契约 {@code Leibniz-KERT docs/skill-execute-api-contract-vNext.md}（SP-15 执行契约细化）
 * 与 {@code docs/integration/DKWS_GITS_CONTRACT_DIFF.md}（错误码映射 §5）：</p>
 * <ul>
 *   <li>{@code POST /api/skill/execute} 同步 200 / 异步 202 + {@code GET /v1/jobs/{jobId}} 轮询；</li>
 *   <li>非 2xx（401/403/409/422/5xx）→ {@link SkillExecutionException}；</li>
 *   <li>超时 / 畸形响应 → {@link SkillExecutionException}（fail-closed，不吞异常）；</li>
 *   <li>产品推荐 GITS skillId {@code bank-front-product-recommendation}（DKWS 侧 SP-15）在
 *       DKWS 不可达时禁止本地补数：{@link FallbackSkillExecutionAdapter#NO_LOCAL_FILL} 包含该 skillId。</li>
 * </ul>
 *
 * <p>沿用 {@link DshHttpSkillExecutionAdapterTest} 的 {@code MockRestServiceServer.bindTo(builder)}
 * 桩模式，不启动 Spring 上下文。</p>
 *
 * <pre>{@code
 * DOC_STATUS=CANDIDATE
 * FROZEN=NO
 * IMPLEMENTED=NO
 * REAL_E2E_PASS=NO
 * }</pre>
 */
class ProductRecommendationSkillContractTest {

    /** GITS 侧产品推荐 skillId（DKWS 侧 skillId = SP-15）。 */
    private static final String SKILL_ID = "bank-front-product-recommendation";
    private static final String REQUEST_ID = "REC-20260831-0001";
    private static final String CUSTOMER_ID = "CUST-001";
    private static final String BASE_URL = "http://dsh.local:3080";
    private static final String EXECUTE_URL = BASE_URL + "/api/skill/execute";
    private static final String JOB_ID = "JOB-PR-20260831-001";
    private static final String JOB_URL = BASE_URL + "/v1/jobs/" + JOB_ID;

    private RestClient.Builder builder;
    private MockRestServiceServer server;
    private DshHttpSkillExecutionAdapter adapter;

    @BeforeEach
    void setUp() {
        builder = RestClient.builder();
        server = MockRestServiceServer.bindTo(builder).build();
        adapter = new DshHttpSkillExecutionAdapter(builder, BASE_URL);
    }

    /** 同步命令：request.context 携带 SP-15 上下文快照（契约 vNext §3.1）。 */
    private SkillExecutionCommand cmd() {
        return new SkillExecutionCommand(
                SKILL_ID, REQUEST_ID, CUSTOMER_ID,
                Map.of("context", recommendationContext()));
    }

    /** 异步命令：async=true（SP-15 长任务建议异步）。 */
    private SkillExecutionCommand asyncCmd() {
        return new SkillExecutionCommand(
                SKILL_ID, REQUEST_ID, CUSTOMER_ID,
                Map.of("context", recommendationContext()), true, Map.of());
    }

    /** SP-15 上下文快照（含 3 个必填快照引用，契约 vNext §3.1）。 */
    private static Map<String, Object> recommendationContext() {
        Map<String, Object> ctx = new LinkedHashMap<>();
        ctx.put("schemaVersion", "1.0.0");
        ctx.put("customerId", CUSTOMER_ID);
        ctx.put("needVersionIds", List.of("NEEDV-001"));
        ctx.put("recommendationObjective", "补充流动资金与跨境结算方案");
        ctx.put("requestedProductDomains", List.of("FINANCING", "SETTLEMENT"));
        ctx.put("asOf", "2026-08-31T09:00:00+08:00");
        ctx.put("customerFactSnapshotId", "CFS-20260831-0001");
        ctx.put("productKnowledgeSnapshotRef", "PKS-20260831-0001");
        ctx.put("ruleBundleRef", "RB-20260831-0001");
        ctx.put("permissionDecisionId", "PERM-20260831-0001");
        ctx.put("activationContract", "AC-PRODUCT-RECOMMEND-001");
        return ctx;
    }

    /** 最小 ProductRecommendationResult（8 个必填字段，契约 vNext §4.1）。 */
    private static String productResultJson() {
        return "{\"schemaVersion\":\"1.0.0\",\"runId\":\"" + REQUEST_ID + "\","
                + "\"skillId\":\"SP-15\",\"skillVersion\":\"2.0.0-candidate\","
                + "\"productKnowledgeSnapshotRef\":\"PKS-20260831-0001\","
                + "\"ruleExecutionRef\":\"RULE-RUN-20260831-0001\","
                + "\"evidenceBundleId\":\"EVB-20260831-0001\","
                + "\"contentHash\":\"sha256:abc\",\"traceId\":\"TRACE-20260831-0001\","
                + "\"eligibilityResults\":[],\"fitResults\":[],\"portfolioCandidates\":[],"
                + "\"needProfile\":[],\"unknowns\":[],\"conflicts\":[],"
                + "\"generatedAt\":\"2026-08-31T09:00:00+08:00\"}";
    }

    @Test
    void execute200OkReturnsProductRecommendationResult() {
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withSuccess(
                        "{\"requestId\":\"" + REQUEST_ID + "\",\"status\":\"ok\","
                        + "\"data\":{\"skillId\":\"SP-15\","
                        + "\"reportUrl\":\"/api/skill/report/" + REQUEST_ID + "\","
                        + "\"result\":" + productResultJson() + "},"
                        + "\"errors\":[],\"assemblyTrace\":[],\"modelCalls\":[]}",
                        MediaType.APPLICATION_JSON));

        SkillExecutionResult result = adapter.execute(cmd());

        assertThat(result.isOk()).isTrue();
        assertThat(result.status()).isEqualTo(SkillExecutionStatus.OK);
        assertThat(result.requestId()).isEqualTo(REQUEST_ID);
        assertThat(result.data()).containsKey("result");
        @SuppressWarnings("unchecked")
        Map<String, Object> productResult = (Map<String, Object>) result.data().get("result");
        // 契约 vNext §4.1：8 个必填字段
        assertThat(productResult).containsKeys(
                "schemaVersion", "runId", "productKnowledgeSnapshotRef", "ruleExecutionRef",
                "evidenceBundleId", "contentHash", "traceId", "generatedAt");
        server.verify();
    }

    @Test
    void execute202AsyncPollsJobToCompleted() {
        DshHttpSkillExecutionAdapter asyncAdapter =
                new DshHttpSkillExecutionAdapter(builder, BASE_URL, 60_000L, 10L);
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withStatus(HttpStatus.ACCEPTED)
                        .body("{\"jobId\":\"" + JOB_ID + "\",\"status\":\"PENDING\"}")
                        .contentType(MediaType.APPLICATION_JSON));
        server.expect(requestTo(JOB_URL))
                .andRespond(withSuccess(
                        "{\"jobId\":\"" + JOB_ID + "\",\"status\":\"ok\",\"data\":{\"status\":\"PENDING\"}}",
                        MediaType.APPLICATION_JSON));
        server.expect(requestTo(JOB_URL))
                .andRespond(withSuccess(
                        "{\"jobId\":\"" + JOB_ID + "\",\"status\":\"ok\",\"data\":{\"status\":\"COMPLETED\","
                        + "\"skill_result\":{\"requestId\":\"" + REQUEST_ID + "\",\"status\":\"ok\","
                        + "\"data\":{\"skillId\":\"SP-15\",\"result\":" + productResultJson() + "},"
                        + "\"errors\":[],\"assemblyTrace\":[],\"modelCalls\":[]}}}",
                        MediaType.APPLICATION_JSON));

        SkillExecutionResult result = asyncAdapter.execute(asyncCmd());

        assertThat(result.isOk()).isTrue();
        assertThat(result.requestId()).isEqualTo(REQUEST_ID);
        assertThat(result.data()).containsKey("result");
        server.verify();
    }

    @Test
    void execute401UnauthorizedThrows() {
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withStatus(HttpStatus.UNAUTHORIZED)
                        .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("SKILL HTTP 401");
        server.verify();
    }

    @Test
    void execute403ForbiddenThrows() {
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withStatus(HttpStatus.FORBIDDEN)
                        .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("SKILL HTTP 403");
        server.verify();
    }

    @Test
    void execute409ConflictThrows() {
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withStatus(HttpStatus.CONFLICT)
                        .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("SKILL HTTP 409");
        server.verify();
    }

    @Test
    void execute422GateCheckFailedThrows() {
        // DKWS_GITS_CONTRACT_DIFF §5：GATE_CHECK_FAILED → HTTP 422
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withStatus(HttpStatus.UNPROCESSABLE_ENTITY)
                        .body("{\"requestId\":\"" + REQUEST_ID + "\",\"status\":\"skill_error\",\"data\":{},"
                        + "\"errors\":[{\"code\":\"GATE_CHECK_FAILED\",\"message\":\"闸门检查失败\"}],"
                        + "\"assemblyTrace\":[],\"modelCalls\":[]}")
                        .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("SKILL HTTP 422");
        server.verify();
    }

    @Test
    void execute500InternalErrorThrows() {
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withStatus(HttpStatus.INTERNAL_SERVER_ERROR)
                        .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("SKILL HTTP 500");
        server.verify();
    }

    @Test
    void executeTimeoutThrows() {
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withException(new IOException("Read timed out")));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("dsh 不可达");
        server.verify();
    }

    @Test
    void executeMalformedResponseThrows() {
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withSuccess("this is not valid json", MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("dsh 响应解析失败");
        server.verify();
    }

    @Test
    void contractPayloadUsesProductRecommendationSkillIdAndContext() {
        SkillExecutionCommand cmd = new SkillExecutionCommand(
                SKILL_ID, REQUEST_ID, CUSTOMER_ID,
                Map.of("context", recommendationContext()), true, Map.of());

        Map<String, Object> payload = DshHttpSkillExecutionAdapter.contractPayload(cmd);

        assertThat(payload.get("skillId")).isEqualTo(SKILL_ID);
        assertThat(payload.get("requestId")).isEqualTo(REQUEST_ID);
        assertThat(payload.get("async")).isEqualTo(Boolean.TRUE);
        @SuppressWarnings("unchecked")
        Map<String, Object> request = (Map<String, Object>) payload.get("request");
        assertThat(request.get("customerId")).isEqualTo(CUSTOMER_ID);
        @SuppressWarnings("unchecked")
        Map<String, Object> context = (Map<String, Object>) request.get("context");
        // 3 个必填快照引用 + 权限决策 + 激活合同（契约 vNext §3.1）
        assertThat(context).containsKeys(
                "schemaVersion", "customerFactSnapshotId", "productKnowledgeSnapshotRef",
                "ruleBundleRef", "permissionDecisionId", "activationContract");
    }

    @Test
    void fallbackNoLocalFillSetContainsProductRecommendation() throws Exception {
        java.lang.reflect.Field field =
                FallbackSkillExecutionAdapter.class.getDeclaredField("NO_LOCAL_FILL");
        field.setAccessible(true);
        @SuppressWarnings("unchecked")
        Set<String> noLocalFill = (Set<String>) field.get(null);

        assertThat(noLocalFill).contains(SKILL_ID);
    }

    @Test
    void fallbackProductRecommendationDoesNotLocalFill() {
        LlmClient llmClient = Mockito.mock(LlmClient.class);
        FallbackSkillExecutionAdapter fallback =
                new FallbackSkillExecutionAdapter(llmClient, "sys-prompt");

        SkillExecutionResult result = fallback.execute(cmd());

        assertThat(result.status()).isEqualTo(SkillExecutionStatus.SKILL_ERROR);
        assertThat(result.isOk()).isFalse();
        assertThat(result.data()).isEmpty();
        assertThat(result.errors())
                .extracting(SkillExecutionResult.ErrorItem::code)
                .contains("DKWS_REQUIRED");
        Mockito.verifyNoInteractions(llmClient);
    }

    @Test
    void dshUnreachableFailsClosedNoLocalFill() {
        // DKWS 不可达：DshHttp 抛 SkillExecutionException（不吞异常）
        server.expect(requestTo(EXECUTE_URL))
                .andRespond(withException(new IOException("Connection refused")));

        assertThatThrownBy(() -> adapter.execute(cmd()))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("dsh 不可达");
        server.verify();

        // 回落 Fallback：产品推荐禁止本地补数 → SKILL_ERROR 且不调用 LlmClient
        LlmClient llmClient = Mockito.mock(LlmClient.class);
        FallbackSkillExecutionAdapter fallback =
                new FallbackSkillExecutionAdapter(llmClient, "sys-prompt");
        SkillExecutionResult result = fallback.execute(cmd());

        assertThat(result.status()).isEqualTo(SkillExecutionStatus.SKILL_ERROR);
        assertThat(result.data()).isEmpty();
        Mockito.verifyNoInteractions(llmClient);
    }
}
