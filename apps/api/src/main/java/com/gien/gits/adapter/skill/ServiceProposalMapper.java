package com.gien.gits.adapter.skill;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.engagement.port.KertContractMismatchException;
import com.gien.gits.engagement.port.ServiceProposal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 将 KERT SP-20 {@code data.result}（JsonNode）映射为强类型 {@link ServiceProposal}。
 *
 * <p>对齐样例 {@code docs/architecture/KERT-V1.4-GITS-INTEGRATION-SAMPLES.md} §2.4；
 * 未知字段忽略（契约 §5）；字段缺失回退空实例而非失败。</p>
 */
public class ServiceProposalMapper {

    private static final Logger log = LoggerFactory.getLogger(ServiceProposalMapper.class);

    private final ObjectMapper objectMapper;

    public ServiceProposalMapper(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    /**
     * @param result KERT {@code data.result} JsonNode（完整 execute 响应的 data.result）
     * @return 强类型建议书
     * @throws KertContractMismatchException {@code result} 缺失/为空，或无法映射为强类型
     *     —— <b>绝不</b>降级为空结果（PI · P1：不得把失败伪装成成功）
     */
    public ServiceProposal fromResult(JsonNode result) {
        if (result == null || result.isMissingNode() || result.isNull()) {
            throw new KertContractMismatchException(
                    "KERT 契约不符：execute 成功但响应缺少 data.result 节点");
        }
        try {
            // 契约 §5：未知字段忽略，不因未来新增字段而失败。
            // copy() 避免污染共享 ObjectMapper 实例的全局配置。
            return objectMapper.copy()
                .configure(com.fasterxml.jackson.databind.DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
                .convertValue(result, ServiceProposal.class);
        } catch (Exception e) {
            throw new KertContractMismatchException(
                    "KERT 契约不符：data.result 无法映射为 ServiceProposal（" + e.getMessage() + "）", e);
        }
    }

    /**
     * 从完整 execute 响应 JsonNode 提取 data.result 并映射。
     *
     * @param responseRoot 完整 execute 响应（顶层含 data）
     * @return 强类型建议书
     */
    public ServiceProposal fromExecuteResponse(JsonNode responseRoot) {
        JsonNode data = responseRoot == null ? null : responseRoot.path("data");
        JsonNode result = data == null ? null : data.path("result");
        return fromResult(result);
    }

    /** 供测试/日志：从 result 提取未知字段名集合。 */
    static List<String> unknownFields(JsonNode result, ObjectMapper om) {
        List<String> unknown = new ArrayList<>();
        if (result == null || !result.isObject()) {
            return unknown;
        }
        var fields = result.fieldNames();
        while (fields.hasNext()) {
            String f = fields.next();
            try {
                om.readTree("{}");
                // ServiceProposal 已知字段
                if (!List.of(
                    "schemaVersion", "skillId", "runId", "status", "timestamp",
                    "content", "citations", "unknowns", "limitations",
                    "gateRecommendations", "ruleViolations").contains(f)) {
                    unknown.add(f);
                }
            } catch (Exception ignore) {
                // 不可能
            }
        }
        return unknown;
    }
}
