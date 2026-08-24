package com.gien.gits.adapter.skill;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.engagement.port.SkillExecutionException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatusCode;
import org.springframework.web.client.RestClient;

/**
 * DKWS 异步作业轮询器 — 轮询 {@code GET /v1/jobs/{jobId}} 直至终态。
 *
 * <p>契约 v1.4 §2.2：轮询响应 {@code data.status ∈ {PENDING,RUNNING,COMPLETED,FAILED}}；
 * COMPLETED 时 {@code data.skill_result} 为完整 execute 响应（与同步响应同构）。</p>
 *
 * <p>与 {@link DshHttpSkillExecutionAdapter} 共享同一 {@link RestClient}，
 * 便于测试用 {@code MockRestServiceServer.bindTo(client)} 拦截。</p>
 *
 * <p>网络异常 / 非 2xx / job FAILED / 超时 → 抛 {@link SkillExecutionException}，
 * 调用方回落 Fallback（不静默降级，契约 §2.2 幂等 TTL 内复用同一 job）。</p>
 */
public class DshJobPoller {

    private static final Logger log = LoggerFactory.getLogger(DshJobPoller.class);
    private static final String JOBS_PATH = "/v1/jobs/";

    private final RestClient restClient;
    private final ObjectMapper objectMapper;
    private final String baseUrl;
    private final long timeoutMs;
    private final long pollIntervalMs;

    /**
     * @param restClient    与适配器共享的 RestClient（已配置超时）
     * @param baseUrl       dsh 服务 base url（仅拼接用）
     * @param timeoutMs     轮询总超时（毫秒）
     * @param pollIntervalMs 轮询间隔（毫秒）
     */
    public DshJobPoller(RestClient restClient, String baseUrl, long timeoutMs, long pollIntervalMs) {
        if (timeoutMs <= 0 || pollIntervalMs <= 0) {
            throw new IllegalArgumentException("async timeout/poll-interval must be positive");
        }
        this.restClient = restClient;
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.timeoutMs = timeoutMs;
        this.pollIntervalMs = pollIntervalMs;
        this.objectMapper = new ObjectMapper();
    }

    /**
     * 轮询直到终态。
     *
     * @param jobId 202 响应返回的 jobId
     * @return COMPLETED 时返回 {@code data.skill_result} 的 JSON 文本
     * @throws SkillExecutionException job FAILED / 超时 / 网络异常 / 响应解析失败 / 未知状态
     */
    public String pollUntilCompleted(String jobId) {
        long deadline = System.currentTimeMillis() + timeoutMs;
        while (true) {
            JobStatusRecord record = fetch(jobId);
            switch (record.status()) {
                case "COMPLETED" -> {
                    log.info("[SKILL-JOB] job={} COMPLETED", jobId);
                    return record.skillResult();
                }
                case "FAILED" -> {
                    log.error("[SKILL-JOB] job={} FAILED", jobId);
                    throw new SkillExecutionException("dsh job failed: " + jobId);
                }
                case "PENDING", "RUNNING" ->
                    log.info("[SKILL-JOB] job={} status={}, polling...", jobId, record.status());
                default -> throw new SkillExecutionException(
                    "dsh job unknown status '" + record.status() + "' for jobId=" + jobId);
            }
            if (System.currentTimeMillis() + pollIntervalMs > deadline) {
                log.error("[SKILL-JOB] job={} poll timeout after {}ms", jobId, timeoutMs);
                throw new SkillExecutionException("dsh job poll timeout: " + jobId);
            }
            sleep(pollIntervalMs);
        }
    }

    private JobStatusRecord fetch(String jobId) {
        String url = this.baseUrl + JOBS_PATH + jobId;
        String body;
        try {
            body = restClient.get()
                .uri(url)
                .retrieve()
                .onStatus(HttpStatusCode::isError,
                    (req, resp) -> {
                        String msg = "SKILL JOB HTTP " + resp.getStatusCode().value() + " for jobId=" + jobId;
                        log.error("[SKILL-JOB] {}", msg);
                        throw new SkillExecutionException(msg);
                    })
                .body(String.class);
        } catch (SkillExecutionException e) {
            throw e;
        } catch (Exception e) {
            log.error("[SKILL-JOB] 网络/超时异常 jobId={}: {}", jobId, e.getMessage());
            throw new SkillExecutionException("dsh 不可达: " + e.getMessage(), e);
        }
        try {
            JsonNode root = objectMapper.readTree(body);
            JsonNode data = root.path("data");
            String status = data.path("status").asText("");
            String skillResult = data.hasNonNull("skill_result")
                ? data.path("skill_result").toString()
                : null;
            if (status.isBlank()) {
                throw new SkillExecutionException("dsh job 响应缺 data.status: " + jobId);
            }
            return new JobStatusRecord(status, skillResult);
        } catch (SkillExecutionException e) {
            throw e;
        } catch (Exception e) {
            log.error("[SKILL-JOB] 响应解析失败 jobId={}", jobId, e);
            throw new SkillExecutionException("dsh job 响应解析失败: " + e.getMessage(), e);
        }
    }

    private static void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new SkillExecutionException("dsh job poll interrupted", e);
        }
    }
}
