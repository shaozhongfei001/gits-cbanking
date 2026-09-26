package com.gien.gits.api.productknowledge;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * KERT 派生检索 HTTP 适配器（PC8 · CR-5 衍生）。
 *
 * <p>向 {@code DSH_BASE_URL + /v1/retrieval/query} 转发检索，复用 DSH 连接/读取超时配置
 * （与 skill gate 同源约束）。响应中实体/关系按 LightRAG 原始字段名防御性映射；
 * 出处直接取 KERT 已归一的 {@code chunkId}/{@code docId}。</p>
 *
 * <p>当 KERT DSH 不可用或返回空实体时，回退到直接调用 LightRAG
 * （{@code lightragUrl + /query}，naive 模式），从原始文本块中解析字段。</p>
 */
public class KertRetrievalAdapter implements ProductKnowledgeRetrievalPort {

    private static final Logger log = LoggerFactory.getLogger(KertRetrievalAdapter.class);
    private static final String RETRIEVAL_PATH = "/v1/retrieval/query";
    private static final Pattern SECTION_PATTERN_MD = Pattern.compile(
            "##\\s*[^\\n]*?(产品目的|使用方式|计息口径|适用主体)[^\\n]*\\s*\\n(.+?)(?=\\n#|$)", Pattern.DOTALL);
    private static final Pattern SECTION_PATTERN_BOLD = Pattern.compile(
            "\\*\\*[^\\n]*?(产品目的|使用方式|计息口径|适用主体)[^\\n]*?\\*\\*\\s*\\n(.+?)(?=\\n\\*\\*|\\n#|$)", Pattern.DOTALL);

    private final RestClient restClient;
    private final ObjectMapper objectMapper;
    private final String baseUrl;
    private final String lightragUrl;
    private final String lightragApiKey;

    public KertRetrievalAdapter(RestClient.Builder restClientBuilder, String baseUrl, String lightragUrl) {
        this(restClientBuilder, baseUrl, lightragUrl, null);
    }

    public KertRetrievalAdapter(RestClient.Builder restClientBuilder, String baseUrl, String lightragUrl, String lightragApiKey) {
        if (baseUrl == null || baseUrl.isBlank()) {
            throw new IllegalArgumentException("dsh.base-url must be configured for retrieval mode");
        }
        this.restClient = restClientBuilder.build();
        this.objectMapper = new ObjectMapper();
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.lightragUrl = (lightragUrl == null || lightragUrl.isBlank()) ? null
                : (lightragUrl.endsWith("/") ? lightragUrl.substring(0, lightragUrl.length() - 1) : lightragUrl);
        this.lightragApiKey = (lightragApiKey == null || lightragApiKey.isBlank()) ? null : lightragApiKey;
        log.info("KertRetrievalAdapter configured: base-url={}, lightrag-url={}, lightrag-auth={}",
                this.baseUrl, this.lightragUrl, this.lightragApiKey != null ? "yes" : "no");
    }

    @Override
    public RetrievalResponse retrieve(String productId, RetrievalRequest request) {
        // 先尝试 KERT DSH
        try {
            RetrievalResponse response = retrieveViaKert(productId, request);
            if (response != null && response.entities() != null && !response.entities().isEmpty()) {
                return response;
            }
            log.info("[PK-RETRIEVAL] KERT 返回空实体，尝试 LightRAG 直连回退 productId={}", productId);
        } catch (Exception e) {
            log.warn("[PK-RETRIEVAL] KERT 检索异常，尝试 LightRAG 直连回退 productId={}: {}",
                    productId, e.getMessage());
        }

        // 回退：直接调用 LightRAG
        if (lightragUrl != null) {
            return retrieveViaLightRag(productId, request);
        }
        throw new KnowledgeSourceUnavailableException(
                "KERT 检索不可用且 LightRAG 直连未配置 (productId=" + productId + ")");
    }

    private RetrievalResponse retrieveViaKert(String productId, RetrievalRequest request) {
        String url = this.baseUrl + RETRIEVAL_PATH;
        String requestId = UUID.randomUUID().toString();
        String mode = request.resolveMode();
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("request_id", requestId);
        body.put("query", request.query());
        body.put("mode", mode);
        body.put("service", productId);
        String payload;
        try {
            payload = objectMapper.writeValueAsString(body);
        } catch (Exception e) {
            throw new KnowledgeSourceUnavailableException("检索请求序列化失败: " + e.getMessage());
        }
        log.info("[PK-RETRIEVAL] productId={} mode={} url={}", productId, mode, url);
        try {
            var reqSpec = restClient.post()
                    .uri(url)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(payload);
            if (lightragApiKey != null) {
                reqSpec = reqSpec.header("Authorization", "Bearer " + lightragApiKey);
            }
            String response = reqSpec.retrieve().body(String.class);
            return parse(response, productId, request.query(), mode, response);
        } catch (RestClientResponseException e) {
            throw mapError(e.getStatusCode(), e.getResponseBodyAsString());
        } catch (KnowledgeSourceUnavailableException e) {
            throw e;
        } catch (Exception e) {
            log.error("[PK-RETRIEVAL] 网络/超时异常 productId={}: {}", productId, e.getMessage());
            throw new KnowledgeSourceUnavailableException("KERT 检索不可达: " + e.getMessage());
        }
    }

    private RetrievalResponse retrieveViaLightRag(String productId, RetrievalRequest request) {
        // 优先使用 /query/data 获取结构化实体，回退到 /query 获取文本
        String dataUrl = this.lightragUrl + "/query/data";
        String textUrl = this.lightragUrl + "/query";
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("query", request.query());
        body.put("mode", request.mode() != null ? request.mode() : "hybrid");
        body.put("only_need_context", true);
        String payload;
        try {
            payload = objectMapper.writeValueAsString(body);
        } catch (Exception e) {
            throw new KnowledgeSourceUnavailableException("LightRAG 请求序列化失败: " + e.getMessage());
        }

        // 尝试 /query/data（结构化实体）
        log.info("[PK-RETRIEVAL] LightRAG 直连回退 productId={} url={}", productId, dataUrl);
        try {
            var reqSpec = restClient.post()
                    .uri(dataUrl)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(payload);
            if (lightragApiKey != null) {
                reqSpec = reqSpec.header("Authorization", "Bearer " + lightragApiKey);
            }
            String response = reqSpec.retrieve().body(String.class);
            RetrievalResponse result = parseLightRagDataResponse(response, productId, request.query());
            if (result != null && result.entities() != null && !result.entities().isEmpty()) {
                return result;
            }
        } catch (Exception e) {
            log.warn("[PK-RETRIEVAL] LightRAG /query/data 失败，回退到 /query: {}", e.getMessage());
        }

        // 回退到 /query（文本响应）
        log.info("[PK-RETRIEVAL] LightRAG 回退到 /query productId={} url={}", productId, textUrl);
        try {
            var reqSpec = restClient.post()
                    .uri(textUrl)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(payload);
            if (lightragApiKey != null) {
                reqSpec = reqSpec.header("Authorization", "Bearer " + lightragApiKey);
            }
            String response = reqSpec.retrieve().body(String.class);
            return parseLightRagDirect(response, productId, request.query());
        } catch (RestClientResponseException e) {
            throw new KnowledgeSourceUnavailableException(
                    "LightRAG 直连失败: HTTP " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
        } catch (KnowledgeSourceUnavailableException e) {
            throw e;
        } catch (Exception e) {
            throw new KnowledgeSourceUnavailableException("LightRAG 直连不可达: " + e.getMessage());
        }
    }

    /** 解析 LightRAG /query/data 响应（结构化实体列表）。 */
    private RetrievalResponse parseLightRagDataResponse(String json, String productId, String reqQuery) {
        try {
            JsonNode root = objectMapper.readTree(json);
            // /query/data 返回结构: {"status":..., "data":{"entities":[...], "relationships":[...], ...}}
            JsonNode entitiesNode = root.path("data").path("entities");
            if (!entitiesNode.isArray() || entitiesNode.isEmpty()) {
                // 回退：顶层 entities
                entitiesNode = root.path("entities");
            }
            if (!entitiesNode.isArray() || entitiesNode.isEmpty()) {
                log.debug("[PK-RETRIEVAL] LightRAG /query/data 无实体返回 productId={}", productId);
                return null;
            }

            List<RetrievalEntity> entities = new ArrayList<>();
            for (JsonNode e : entitiesNode) {
                if (!e.isObject()) {
                    continue;
                }
                String name = strOrNull(e, "entity_name", "name");
                String type = strOrNull(e, "entity_type", "type");
                String desc = strOrNull(e, "description");
                // 只保留 PRODUCT_ATTRIBUTE 类型的实体（产品知识属性）
                if ("PRODUCT_ATTRIBUTE".equals(type) && name != null && desc != null) {
                    entities.add(new RetrievalEntity(name, type, desc));
                }
            }

            // 解析关系
            List<RetrievalRelation> relations = new ArrayList<>();
            JsonNode relationsNode = root.path("data").path("relationships");
            if (!relationsNode.isArray()) {
                relationsNode = root.path("data").path("relations");
            }
            if (!relationsNode.isArray()) {
                relationsNode = root.path("relationships");
            }
            if (!relationsNode.isArray()) {
                relationsNode = root.path("relations");
            }
            if (relationsNode.isArray()) {
                for (JsonNode r : relationsNode) {
                    if (!r.isObject()) {
                        continue;
                    }
                    relations.add(new RetrievalRelation(
                            strOrNull(r, "src_id", "source", "head"),
                            strOrNull(r, "tgt_id", "target", "tail"),
                            strOrNull(r, "relation", "description", "type")));
                }
            }

            // 解析引用
            List<RetrievalCitation> citations = new ArrayList<>();
            JsonNode citationsNode = root.path("data").path("chunks");
            if (!citationsNode.isArray()) {
                citationsNode = root.path("data").path("citations");
            }
            if (!citationsNode.isArray()) {
                citationsNode = root.path("data").path("references");
            }
            if (!citationsNode.isArray()) {
                citationsNode = root.path("chunks");
            }
            if (!citationsNode.isArray()) {
                citationsNode = root.path("citations");
            }
            if (!citationsNode.isArray()) {
                citationsNode = root.path("references");
            }
            if (citationsNode.isArray()) {
                for (JsonNode c : citationsNode) {
                    if (!c.isObject()) {
                        continue;
                    }
                    citations.add(new RetrievalCitation(
                            strOrNull(c, "chunkId", "chunk_id"),
                            strOrNull(c, "docId", "file_path"),
                            strOrNull(c, "content"),
                            null, null, null));
                }
            }

            return RetrievalResponse.ofWithRaw(productId,
                    reqQuery, "hybrid",
                    entities, relations, citations,
                    "DERIVED_RETRIEVAL", "LIGHTRAG_DIRECT", true,
                    json);
        } catch (Exception e) {
            log.error("[PK-RETRIEVAL] LightRAG /query/data 响应解析失败 productId={}: {}", productId, e.getMessage());
            return null;
        }
    }

    /** 解析 LightRAG 直连响应（naive 模式），从原始文本中提取实体。 */
    private RetrievalResponse parseLightRagDirect(String json, String productId, String reqQuery) {
        try {
            JsonNode root = objectMapper.readTree(json);
            String responseText = root.path("response").asText("");

            // 从响应文本中按标题解析四类字段（支持 ## 标题 和 **加粗标题** 两种格式）
            List<RetrievalEntity> entities = new ArrayList<>();
            Matcher mdMatcher = SECTION_PATTERN_MD.matcher(responseText);
            while (mdMatcher.find()) {
                String heading = mdMatcher.group(1);
                String content = mdMatcher.group(2).trim();
                if (!content.isBlank()) {
                    entities.add(new RetrievalEntity(
                            heading, "PRODUCT_ATTRIBUTE", content));
                }
            }
            if (entities.isEmpty()) {
                Matcher boldMatcher = SECTION_PATTERN_BOLD.matcher(responseText);
                while (boldMatcher.find()) {
                    String heading = boldMatcher.group(1);
                    String content = boldMatcher.group(2).trim();
                    if (!content.isBlank()) {
                        entities.add(new RetrievalEntity(
                                heading, "PRODUCT_ATTRIBUTE", content));
                    }
                }
            }

            // 如果标题解析失败，把整个响应作为单个实体
            if (entities.isEmpty() && !responseText.isBlank()) {
                entities.add(new RetrievalEntity(
                        "LightRAG_RESPONSE", "RAW_TEXT", responseText));
            }

            return RetrievalResponse.ofWithRaw(productId,
                    reqQuery, "hybrid",
                    entities, List.of(), List.of(),
                    "DERIVED_RETRIEVAL", "LIGHTRAG_DIRECT", true,
                    json);
        } catch (Exception e) {
            log.error("[PK-RETRIEVAL] LightRAG 响应解析失败 productId={}: {}", productId, e.getMessage());
            throw new KnowledgeSourceUnavailableException("LightRAG 响应解析失败: " + e.getMessage());
        }
    }

    private RuntimeException mapError(HttpStatusCode status, String bodyStr) {
        String code = "LIGHTRAG_UNAVAILABLE";
        String message = (bodyStr == null) ? status.toString() : bodyStr;
        try {
            JsonNode err = objectMapper.readTree(bodyStr == null ? "{}" : bodyStr).path("error");
            if (!err.isMissingNode()) {
                code = err.path("code").asText(code);
                message = err.path("message").asText(bodyStr);
            }
        } catch (Exception ignored) {
        }
        if (status.is5xxServerError()) {
            return new RetrievalUpstreamException(HttpStatus.valueOf(status.value()), code, message);
        }
        return new InterpretationRejectedException(HttpStatus.valueOf(status.value()), code, message);
    }

    private RetrievalResponse parse(String json, String productId, String reqQuery, String reqMode, String rawJson) {
        try {
            JsonNode root = objectMapper.readTree(json);
            JsonNode data = root.path("data");
            if (data.isMissingNode() || !data.isObject()) {
                data = root;
            }
            List<RetrievalEntity> entities = new ArrayList<>();
            for (JsonNode e : data.path("entities")) {
                if (!e.isObject()) {
                    continue;
                }
                entities.add(new RetrievalEntity(
                        strOrNull(e, "entity_name", "entity", "name", "id"),
                        strOrNull(e, "entity_type", "type"),
                        strOrNull(e, "description")));
            }
            List<RetrievalRelation> relations = new ArrayList<>();
            for (JsonNode r : data.path("relations")) {
                if (!r.isObject()) {
                    continue;
                }
                relations.add(new RetrievalRelation(
                        strOrNull(r, "src_id", "source", "head"),
                        strOrNull(r, "tgt_id", "target", "tail"),
                        strOrNull(r, "relation", "description", "type")));
            }
            List<RetrievalCitation> citations = new ArrayList<>();
            JsonNode citationsNode = data.path("citations");
            if (!citationsNode.isArray() || citationsNode.isEmpty()) {
                citationsNode = data.path("references");
            }
            for (JsonNode c : citationsNode) {
                if (!c.isObject()) {
                    continue;
                }
                citations.add(new RetrievalCitation(
                        strOrNull(c, "chunkId", "reference_id", "chunk_id"),
                        strOrNull(c, "docId", "file_path"),
                        strOrNull(c, "content"),
                        strOrNull(c, "artifact"),
                        strOrNull(c, "planId"),
                        strOrNull(c, "planHash")));
            }
            String evidenceClass = strOrNull(data, "evidenceClass");
            String provenanceState = strOrNull(data, "provenanceState");
            Boolean simulationOnly = data.path("simulationOnly").isBoolean()
                    ? data.path("simulationOnly").asBoolean() : null;
            String query = strOrNull(data, "query");
            String mode = strOrNull(data, "mode");
            return RetrievalResponse.ofWithRaw(productId,
                    query != null ? query : reqQuery,
                    mode != null ? mode : reqMode,
                    entities, relations, citations, evidenceClass, provenanceState, simulationOnly,
                    rawJson);
        } catch (Exception e) {
            log.error("[PK-RETRIEVAL] 响应解析失败 productId={}: {}", productId, e.getMessage());
            throw new RetrievalUpstreamException(HttpStatus.INTERNAL_SERVER_ERROR,
                    "LIGHTRAG_RESPONSE_INVALID", "检索响应解析失败: " + e.getMessage());
        }
    }

    private static String strOrNull(JsonNode node, String... keys) {
        for (String k : keys) {
            JsonNode v = node.path(k);
            if (v.isTextual() && !v.asText().isEmpty()) {
                return v.asText();
            }
        }
        return null;
    }
}
