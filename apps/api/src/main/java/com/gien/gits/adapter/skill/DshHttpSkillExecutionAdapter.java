package com.gien.gits.adapter.skill;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * DSH SKILL 运行平台 HTTP 适配器 — 调用 dsh {@code POST /api/skill/execute}。
 *
 * <p>对齐契约 {@code docs/dd/skill-execute-api-contract.md}：</p>
 * <ul>
 *   <li>请求 {@code {skillId, requestId, request:{...}}}（request 自由 map）</li>
 *   <li>响应 {@code {requestId, status, data, errors, assemblyTrace[], modelCalls[]}}</li>
 *   <li>{@code status ∈ ok | skill_error | exit_policy_no_new_evidence}（snake_case）</li>
 *   <li>未知 skillId → {@code 404}, {@code errors[0].code=UNKNOWN_SKILL}</li>
 *   <li>非 200 / 网络异常 → 抛 {@link SkillExecutionException}，调用方回落 Fallback</li>
 * </ul>
 *
 * <p>构造接收一个 <b>已用超时配置好的 {@link RestClient}</b>（由 {@code EngagementConfig}
 * 构建），本类不复刻 builder —— 这样测试可用 {@code MockRestServiceServer.bindTo(client)}
 * 精确拦截，也避免 builder 复制导致 mock 失效。</p>
 *
 * @param restClient 已配置超时的 RestClient（指向 dsh）
 * @param baseUrl    dsh 服务 base url（仅日志/拼接用）
 */
public class DshHttpSkillExecutionAdapter implements SkillExecutionPort {

    private static final Logger log = LoggerFactory.getLogger(DshHttpSkillExecutionAdapter.class);
    private static final String EXECUTE_PATH = "/api/skill/execute";
    private static final long DEFAULT_ASYNC_TIMEOUT_MS = 120_000L;
    private static final long DEFAULT_ASYNC_POLL_INTERVAL_MS = 2_000L;

    private final RestClient restClient;
    private final ObjectMapper objectMapper;
    private final String baseUrl;
    private final DshJobPoller jobPoller;

    /**
     * @param restClientBuilder 与外部共享的 builder（未克隆），由此直接 {@code build()}。
     *                          测试可用 {@code MockRestServiceServer.bindTo(builder)} 拦截。
     */
    public DshHttpSkillExecutionAdapter(RestClient.Builder restClientBuilder, String baseUrl) {
        this(restClientBuilder, baseUrl, DEFAULT_ASYNC_TIMEOUT_MS, DEFAULT_ASYNC_POLL_INTERVAL_MS);
    }

    /**
     * @param restClientBuilder 与外部共享的 builder（未克隆），由此直接 {@code build()}。
     * @param baseUrl           dsh 服务 base url（仅日志/拼接用）
     * @param asyncTimeoutMs    异步作业轮询总超时（毫秒，契约 v1.4 §2.2）
     * @param asyncPollIntervalMs 异步作业轮询间隔（毫秒）
     */
    public DshHttpSkillExecutionAdapter(RestClient.Builder restClientBuilder, String baseUrl,
                                        long asyncTimeoutMs, long asyncPollIntervalMs) {
        if (baseUrl == null || baseUrl.isBlank()) {
            throw new IllegalArgumentException(
                "dsh.base-url must be configured for HTTP mode");
        }
        this.restClient = restClientBuilder.build();
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.objectMapper = new ObjectMapper();
        this.jobPoller = new DshJobPoller(this.restClient, this.baseUrl, asyncTimeoutMs, asyncPollIntervalMs);
        log.info("DshHttpSkillExecutionAdapter configured: base-url={}", this.baseUrl);
    }

    @Override
    public SkillExecutionResult execute(SkillExecutionCommand command) {
        String url = this.baseUrl + EXECUTE_PATH;
        log.info("[SKILL-HTTP] execute skillId={} requestId={} customerId={} async={} url={}",
                 command.skillId(), command.requestId(), command.customerId(), command.async(), url);

        String response = post(command, url);

        if (command.async()) {
            return executeAsync(command, response);
        }
        return parse(response, command);
    }

    private SkillExecutionResult executeAsync(SkillExecutionCommand command, String response) {
        try {
            JsonNode root = objectMapper.readTree(response);
            if (root.hasNonNull("jobId")) {
                String jobId = root.path("jobId").asText("");
                log.info("[SKILL-HTTP] async skillId={} requestId={} jobId={}",
                         command.skillId(), command.requestId(), jobId);
                String skillResult = jobPoller.pollUntilCompleted(jobId);
                return parse(skillResult, command);
            }
            // 同步完成（200 + 完整 execute 响应，契约 v1.4 §2.2 允许）
            return parse(response, command);
        } catch (SkillExecutionException e) {
            throw e;
        } catch (Exception e) {
            log.error("[SKILL-HTTP] async 解析失败 skillId={} requestId={}",
                      command.skillId(), command.requestId(), e);
            throw new SkillExecutionException("dsh async 响应解析失败: " + e.getMessage(), e);
        }
    }

    private String post(SkillExecutionCommand command, String url) {
        try {
            return restClient.post()
                .uri(url)
                .contentType(MediaType.APPLICATION_JSON)
                .body(objectMapper.writeValueAsString(contractPayload(command)))
                .retrieve()
                .onStatus(HttpStatusCode::isError,
                    (req, resp) -> {
                        String msg = "SKILL HTTP " + resp.getStatusCode().value()
                            + " for skillId=" + command.skillId();
                        log.error("[SKILL-HTTP] {} requestId={}", msg, command.requestId());
                        throw new SkillExecutionException(msg);
                    })
                .body(String.class);
        } catch (SkillExecutionException e) {
            throw e;
        } catch (Exception e) {
            // 网络/超时/连接拒绝等：契约 §7 —— 服务端不会把不可达包装为 skill_error；
            // gits 应在调用方捕获后回落 Fallback。
            log.error("[SKILL-HTTP] 网络/超时异常 skillId={} requestId={}: {}",
                      command.skillId(), command.requestId(), e.getMessage());
            throw new SkillExecutionException("dsh 不可达: " + e.getMessage(), e);
        }
    }

    /**
     * 契约 v1.4 §2.1：顶层 skillId/requestId/request(+async,context 可选)；
     * customerId 放入 request；context 与 request.context 合并，request.context 优先。
     */
    static Map<String, Object> contractPayload(SkillExecutionCommand command) {
        Map<String, Object> request = new LinkedHashMap<>(command.request());
        if (command.customerId() != null && !command.customerId().isBlank()) {
            request.putIfAbsent("customerId", command.customerId());
        }
        if (command.context() != null && !command.context().isEmpty()) {
            Map<String, Object> merged = new LinkedHashMap<>(command.context());
            Object rc = request.get("context");
            if (rc instanceof Map<?, ?> rm) {
                for (Map.Entry<?, ?> e : rm.entrySet()) {
                    merged.put(String.valueOf(e.getKey()), e.getValue());
                }
            }
            request.put("context", merged);
        }
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("skillId", command.skillId());
        payload.put("requestId", command.requestId());
        payload.put("request", request);
        if (command.async()) {
            payload.put("async", true);
        }
        return payload;
    }

    private SkillExecutionResult parse(String response, SkillExecutionCommand command) {
        try {
            JsonNode root = objectMapper.readTree(response);
            SkillExecutionStatus status = parseStatus(root);
            String requestId = root.path("requestId").asText(null);
            Map<String, Object> data = parseData(root);
            List<SkillExecutionResult.ErrorItem> errors = parseErrors(root);
            List<SkillExecutionResult.TraceStep> trace = parseTrace(root);
            List<SkillExecutionResult.ModelCall> modelCalls = parseModelCalls(root);

            return new SkillExecutionResult(status, requestId, data, errors, trace, modelCalls);
        } catch (Exception e) {
            log.error("[SKILL-HTTP] 响应解析失败 skillId={} requestId={}", command.skillId(),
                      command.requestId(), e);
            throw new SkillExecutionException("dsh 响应解析失败: " + e.getMessage(), e);
        }
    }

    private SkillExecutionStatus parseStatus(JsonNode root) {
        String raw = root.path("status").asText("");
        return SkillExecutionStatus.fromWire(raw);
    }

    private Map<String, Object> parseData(JsonNode root) {
        if (!root.has("data") || root.get("data").isNull()) {
            return Map.of();
        }
        try {
            return objectMapper.convertValue(root.get("data"), new TypeReference<>() {
            });
        } catch (Exception e) {
            return Map.of();
        }
    }

    private List<SkillExecutionResult.ErrorItem> parseErrors(JsonNode root) {
        List<SkillExecutionResult.ErrorItem> out = new ArrayList<>();
        JsonNode arr = root.path("errors");
        if (arr.isArray()) {
            for (JsonNode n : arr) {
                out.add(new SkillExecutionResult.ErrorItem(
                    n.path("code").asText("UNKNOWN"), n.path("message").asText("")));
            }
        }
        return out;
    }

    private List<SkillExecutionResult.TraceStep> parseTrace(JsonNode root) {
        List<SkillExecutionResult.TraceStep> out = new ArrayList<>();
        JsonNode arr = root.path("assemblyTrace");
        if (arr.isArray()) {
            for (JsonNode n : arr) {
                out.add(new SkillExecutionResult.TraceStep(
                    n.path("phase").asText(""),
                    n.path("status").asText(""),
                    n.path("message").asText(""),
                    optionalKiId(n)));
            }
        }
        return out;
    }

    private List<SkillExecutionResult.ModelCall> parseModelCalls(JsonNode root) {
        List<SkillExecutionResult.ModelCall> out = new ArrayList<>();
        JsonNode arr = root.path("modelCalls");
        if (arr.isArray()) {
            for (JsonNode n : arr) {
                out.add(new SkillExecutionResult.ModelCall(
                    n.path("model").asText(""),
                    n.path("inputTokens").asInt(0),
                    n.path("outputTokens").asInt(0),
                    n.path("latencyMs").asLong(0)));
            }
        }
        return out;
    }

    private static String optionalKiId(JsonNode n) {
        if (!n.hasNonNull("kiId")) {
            return null;
        }
        String kiId = n.path("kiId").asText("");
        return kiId.isBlank() ? null : kiId;
    }
}