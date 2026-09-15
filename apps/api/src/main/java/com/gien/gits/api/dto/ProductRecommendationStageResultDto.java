package com.gien.gits.api.dto;

import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 三段式阶段结果（对齐 specs/openapi/product-recommendation.openapi.json
 * → {@code ProductRecommendationStageResult}；CTR-PR-API-001）。
 *
 * <p>只读组合视图：阶段明细数组取自当前方案版本 {@code payload}（KERT
 * {@code ProductRecommendationResult}）中的对应键；不触发任何生成。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public record ProductRecommendationStageResultDto(
        String runId,
        ProductRecommendationRunStatus status,
        List<Map<String, Object>> eligibilityResults,
        List<Map<String, Object>> fitResults,
        List<Map<String, Object>> portfolioCandidates,
        List<Map<String, Object>> needProfile,
        List<String> unknowns,
        List<String> conflicts) {

    public static ProductRecommendationStageResultDto from(ProductRecommendationRun run, Map<String, Object> payload) {
        Map<String, Object> p = payload == null ? Map.of() : payload;
        return new ProductRecommendationStageResultDto(
                run.runId(), run.status(),
                listOfMaps(p.get("eligibilityResults")),
                listOfMaps(p.get("fitResults")),
                listOfMaps(p.get("portfolioCandidates")),
                listOfMaps(p.get("needProfile")),
                listOfStrings(p.get("unknowns")),
                listOfStrings(p.get("conflicts")));
    }

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> listOfMaps(Object raw) {
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

    private static List<String> listOfStrings(Object raw) {
        if (!(raw instanceof List<?> list)) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        for (Object item : list) {
            if (item != null) {
                out.add(String.valueOf(item));
            }
        }
        return out;
    }
}
