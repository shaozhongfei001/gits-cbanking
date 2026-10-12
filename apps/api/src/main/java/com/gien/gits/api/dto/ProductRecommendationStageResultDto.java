package com.gien.gits.api.dto;

import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;
import com.gien.gits.api.dto.support.ProductRecommendationInvariantGuard;

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
 * <p>GAP-2/GAP-3（2026-09-04）：{@code from()} 内经
 * {@link com.gien.gits.api.dto.support.ProductRecommendationInvariantGuard} 强制
 * INV-02 与 INV-03——非 {@code ELIGIBLE} 产品携带的 {@code fitScore}/{@code rank}
 * 被中和为 null，违规明细以 {@code INV-0x:} 前缀记入 {@code conflicts}。
 * 处置策略与不抛 422 的依据见该守卫类注释。</p>
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
        List<Map<String, Object>> eligibilityResults = listOfMaps(p.get("eligibilityResults"));
        List<Map<String, Object>> fitResults = listOfMaps(p.get("fitResults"));
        // listOfStrings 在非 List 输入时返回不可变 List.of()，守卫需追加违规明细，故包为可变副本
        List<String> conflicts = new ArrayList<>(listOfStrings(p.get("conflicts")));

        ProductRecommendationInvariantGuard.enforce(run.runId(), eligibilityResults, fitResults, conflicts);

        return new ProductRecommendationStageResultDto(
                run.runId(), run.status(),
                eligibilityResults,
                fitResults,
                listOfMaps(p.get("portfolioCandidates")),
                listOfMaps(p.get("needProfile")),
                listOfStrings(p.get("unknowns")),
                List.copyOf(conflicts));
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
