package com.gien.gits.api.service;

import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.ontology.port.CustomerRepository;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/**
 * 产品匹配：只调用 DKWS {@code bank-front-product-recommendation}，request 仅 customerId。
 * 不读 H2 交易流水 / KYC / 产品目录，也不用本地 LLM 补推荐。
 *
 * <p><b>⚠️ M1_RULE_PROTOTYPE — DEMO_ONLY</b>：本服务仅为规则原型演示，
 * 不构成正式银行产品推荐能力。所有推荐结果必须经人工审核后方可使用。
 * 正式产品推荐能力需按 HLD 建立完整链路（需求→知识卡→准入→评分→组合→证据→人工确认）。</p>
 */
public class ProductMatchingService {

    public static final String SKILL_ID = "bank-front-product-recommendation";

    private static final Logger log = LoggerFactory.getLogger(ProductMatchingService.class);

    private static final List<String> LIST_KEYS = List.of(
            "products", "recommendations", "candidates", "items");

    private final SkillExecutionPort skillExecutionPort;
    private final CustomerRepository customerRepo;

    public ProductMatchingService(SkillExecutionPort skillExecutionPort,
                                  CustomerRepository customerRepo) {
        this.skillExecutionPort = Objects.requireNonNull(skillExecutionPort);
        this.customerRepo = Objects.requireNonNull(customerRepo);
    }

    /**
     * 调用 DKWS Skill 匹配产品。客户不存在或 Skill 失败时返回空列表，不抛异常。
     *
     * @param customerId 客户ID
     * @return 匹配的产品推荐列表
     */
    public List<ProductMatch> matchProducts(String customerId) {
        log.info("Matching products via DKWS Skill for customer: {}", customerId);

        if (customerRepo.findById(customerId).isEmpty()) {
            log.warn("Customer not found: {}", customerId);
            return List.of();
        }

        try {
            SkillExecutionResult result = skillExecutionPort.execute(skillCommand(customerId));
            if (!result.isOk() || result.data().isEmpty()) {
                log.warn("[PRODUCT-SKILL] dsh status={} empty={}, 未使用 H2 流水种子规则",
                        result.status(), result.data().isEmpty());
                return List.of();
            }
            return mapFromSkill(result.data());
        } catch (SkillExecutionException ex) {
            log.warn("[PRODUCT-SKILL] DKWS 不可达，未使用 H2 流水种子规则: {}", ex.getMessage());
            return List.of();
        }
    }

    private SkillExecutionCommand skillCommand(String customerId) {
        Map<String, Object> request = new LinkedHashMap<>();
        request.put("customerId", customerId);
        return new SkillExecutionCommand(
                SKILL_ID, "REQ-PRODUCT-" + UUID.randomUUID(), customerId, request);
    }

    private static List<ProductMatch> mapFromSkill(Map<String, Object> data) {
        List<Map<String, Object>> items = firstProductList(data);
        if (!items.isEmpty()) {
            List<ProductMatch> matches = new ArrayList<>();
            for (int i = 0; i < items.size(); i++) {
                Map<String, Object> item = items.get(i);
                String productName = firstString(item, "productName", "name", "title");
                if (productName.isBlank()) {
                    continue;
                }
                String productId = firstString(item, "productId", "id", "code");
                if (productId.isBlank()) {
                    productId = "PROD-DKWS-" + (i + 1);
                }
                String reason = firstString(item, "reason", "matchReason", "rationale",
                        "description", "content");
                double confidence = asConfidence(firstValue(item, "confidence", "matchScore", "score"));
                String signal = firstString(item, "signal", "source");
                matches.add(new ProductMatch(productId, productName, reason, confidence, signal));
            }
            return matches;
        }
        return mapFromSections(data.get("sections"));
    }

    private static List<ProductMatch> mapFromSections(Object raw) {
        for (Map<String, Object> section : mapList(raw)) {
            String heading = stringValue(section.get("heading"));
            if (heading.contains("KI-FRONT-006")
                    || heading.contains("产品候选")
                    || heading.contains("产品组合")) {
                return List.of(new ProductMatch(
                        "KI-FRONT-006",
                        heading,
                        stringValue(section.get("content")),
                        0,
                        ""));
            }
        }
        return List.of();
    }

    private static List<Map<String, Object>> firstProductList(Map<String, Object> data) {
        for (String key : LIST_KEYS) {
            List<Map<String, Object>> list = mapList(data.get(key));
            if (!list.isEmpty()) {
                return list;
            }
        }
        return List.of();
    }

    private static List<Map<String, Object>> mapList(Object raw) {
        if (!(raw instanceof List<?> list)) {
            return List.of();
        }
        List<Map<String, Object>> out = new ArrayList<>();
        for (Object item : list) {
            if (item instanceof Map<?, ?> map) {
                Map<String, Object> converted = new LinkedHashMap<>();
                map.forEach((k, v) -> converted.put(String.valueOf(k), v));
                out.add(converted);
            }
        }
        return out;
    }

    private static String firstString(Map<String, Object> map, String... keys) {
        for (String key : keys) {
            Object value = map.get(key);
            if (value == null) {
                continue;
            }
            String text = stringValue(value);
            if (!text.isBlank()) {
                return text;
            }
        }
        return "";
    }

    private static Object firstValue(Map<String, Object> map, String... keys) {
        for (String key : keys) {
            Object value = map.get(key);
            if (value != null) {
                return value;
            }
        }
        return null;
    }

    private static String stringValue(Object value) {
        return value == null ? "" : String.valueOf(value).trim();
    }

    private static double asConfidence(Object raw) {
        if (raw == null) {
            return 0;
        }
        double value;
        if (raw instanceof Number number) {
            value = number.doubleValue();
        } else {
            try {
                value = Double.parseDouble(String.valueOf(raw).trim());
            } catch (NumberFormatException ex) {
                return 0;
            }
        }
        if (value > 1 && value <= 100) {
            return value / 100;
        }
        return value;
    }

    /**
     * 产品匹配结果
     *
     * @param productId   产品ID
     * @param productName 产品名称
     * @param reason      匹配原因
     * @param confidence  匹配置信度 (0-1)
     * @param signal      匹配信号
     */
    public record ProductMatch(
            String productId,
            String productName,
            String reason,
            double confidence,
            String signal) {}
}
