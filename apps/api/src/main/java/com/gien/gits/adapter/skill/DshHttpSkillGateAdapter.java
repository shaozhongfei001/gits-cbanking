package com.gien.gits.adapter.skill;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.engagement.port.GateAssets;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillGatePort;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;

/**
 * DKWS 闸门协作 HTTP 适配器（契约 v1.4 §4）。
 *
 * <ul>
 *   <li>{@code GET /api/skill/gates/{customerId}} → GATE-BIZ 清单资产（仅输入，非权威）</li>
 *   <li>{@code POST /api/skill/gates/audit} → 决策镜像追加 {@code 90_control/audit/gates.jsonl}，
 *       失败不影响 GITS 权威状态（可重试）</li>
 * </ul>
 */
public class DshHttpSkillGateAdapter implements SkillGatePort {

    private static final Logger log = LoggerFactory.getLogger(DshHttpSkillGateAdapter.class);
    private static final String GATES_PATH = "/api/skill/gates/";
    private static final String AUDIT_PATH = "/api/skill/gates/audit";

    private final RestClient restClient;
    private final ObjectMapper objectMapper;
    private final String baseUrl;

    /**
     * @param restClientBuilder 与 execute 适配器同源共享 builder（未克隆），测试可用
     *                          {@code MockRestServiceServer.bindTo(builder)} 拦截
     * @param baseUrl           dsh 服务 base url
     */
    public DshHttpSkillGateAdapter(RestClient.Builder restClientBuilder, String baseUrl) {
        if (baseUrl == null || baseUrl.isBlank()) {
            throw new IllegalArgumentException("dsh.base-url must be configured for HTTP mode");
        }
        this.restClient = restClientBuilder.build();
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.objectMapper = new ObjectMapper();
        log.info("DshHttpSkillGateAdapter configured: base-url={}", this.baseUrl);
    }

    @Override
    public GateAssets fetchGateAssets(String customerId) {
        String url = this.baseUrl + GATES_PATH + customerId;
        log.info("[SKILL-GATE] fetch assets customerId={} url={}", customerId, url);
        String response;
        try {
            response = restClient.get()
                .uri(url)
                .retrieve()
                .onStatus(HttpStatusCode::isError,
                    (req, resp) -> {
                        String msg = "SKILL GATE HTTP " + resp.getStatusCode().value()
                            + " for customerId=" + customerId;
                        log.error("[SKILL-GATE] {}", msg);
                        throw new SkillExecutionException(msg);
                    })
                .body(String.class);
        } catch (SkillExecutionException e) {
            throw e;
        } catch (Exception e) {
            log.error("[SKILL-GATE] 网络/超时异常 customerId={}: {}", customerId, e.getMessage());
            throw new SkillExecutionException("dsh 不可达: " + e.getMessage(), e);
        }
        try {
            JsonNode root = objectMapper.readTree(response);
            JsonNode data = root.path("data");
            if (!data.isObject() || data.isEmpty()) {
                // DKWS 真实响应为顶层 {customerId, gates:[...]}（无 data 包装）
                data = root;
            }
            List<GateAssets.GateDefinition> gates = new ArrayList<>();
            JsonNode gatesNode = data.path("gates");
            if (gatesNode.isArray()) {
                for (JsonNode g : gatesNode) {
                    List<String> criteria = new ArrayList<>();
                    JsonNode c = g.path("criteria");
                    if (c.isArray()) {
                        c.forEach(item -> criteria.add(item.asText()));
                    } else {
                        JsonNode must = g.path("must");
                        if (must.isArray()) {
                            must.forEach(item -> criteria.add(item.asText()));
                        }
                    }
                    String description = g.path("description").asText("");
                    if (description.isBlank()) {
                        description = g.path("assetPath").asText("");
                    }
                    gates.add(new GateAssets.GateDefinition(
                        g.path("gateId").asText(),
                        g.path("name").asText(),
                        description,
                        criteria));
                }
            }
            return new GateAssets(
                data.path("schemaVersion").asText("1.0.0"),
                data.path("customerId").asText(customerId),
                data.path("flowName").asText("service-proposal"),
                gates);
        } catch (Exception e) {
            log.error("[SKILL-GATE] 响应解析失败 customerId={}", customerId, e);
            throw new SkillExecutionException("dsh gate 响应解析失败: " + e.getMessage(), e);
        }
    }

    @Override
    public boolean mirrorGateAudit(String customerId, Map<String, Object> auditEntry) {
        String url = this.baseUrl + AUDIT_PATH;
        try {
            Map<String, Object> body = new java.util.LinkedHashMap<>(auditEntry);
            body.putIfAbsent("customerId", customerId);
            // DKWS 契约字段对齐：gateCode → gate；决策者缺省 GITS:SYSTEM
            if (body.containsKey("gateCode") && !body.containsKey("gate")) {
                body.put("gate", body.remove("gateCode"));
            }
            body.putIfAbsent("decidedBy", "GITS:SYSTEM");
            String response = restClient.post()
                .uri(url)
                .contentType(MediaType.APPLICATION_JSON)
                .body(objectMapper.writeValueAsString(body))
                .retrieve()
                .onStatus(HttpStatusCode::isError,
                    (req, resp) -> {
                        String msg = "SKILL GATE AUDIT HTTP " + resp.getStatusCode().value()
                            + " for customerId=" + customerId;
                        log.error("[SKILL-GATE] {}", msg);
                        throw new SkillExecutionException(msg);
                    })
                .body(String.class);
            JsonNode root = objectMapper.readTree(response);
            return root.path("recorded").asBoolean(false);
        } catch (SkillExecutionException e) {
            // 镜像失败不影响 GITS 权威状态（契约 v1.4 §4）：记录并返回 false 供重试
            log.warn("[SKILL-GATE] 镜像失败 customerId={}: {}", customerId, e.getMessage());
            return false;
        } catch (Exception e) {
            log.warn("[SKILL-GATE] 镜像网络异常 customerId={}: {}", customerId, e.getMessage());
            return false;
        }
    }
}
