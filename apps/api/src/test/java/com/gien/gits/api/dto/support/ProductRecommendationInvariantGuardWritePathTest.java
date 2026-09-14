package com.gien.gits.api.dto.support;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * {@link ProductRecommendationInvariantGuard#detectViolations} 单元测试
 * （FAIL-2026-09-04-03 写路径 fail-closed）。
 *
 * <p>关键断言是 <b>payload 不被修改</b>——写路径只检测不改写，改写发生在读路径的
 * {@code enforce}。若 detectViolations 意外改写了 payload，落库数据会与 KERT 原始
 * 返回不一致，破坏可追溯性。</p>
 */
class ProductRecommendationInvariantGuardWritePathTest {

    private static final String RUN_ID = "run-write-001";

    @Test
    @DisplayName("合法 payload → 无违规")
    void detectsNoViolationOnValidPayload() {
        Map<String, Object> payload = payload(
                List.of(elig("PROD-A", "1.0", "ELIGIBLE")),
                List.of(fit("PROD-A", "1.0", 1, 0.9)));

        assertThat(ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload)).isEmpty();
    }

    @Test
    @DisplayName("INV-02 违规 → 返回违规明细")
    void detectsInv02Violation() {
        Map<String, Object> payload = payload(
                List.of(elig("PROD-B", "1.0", "INELIGIBLE")),
                List.of(fit("PROD-B", "1.0", 1, 0.8)));

        List<String> v = ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload);

        assertThat(v).hasSize(1);
        assertThat(v.get(0)).startsWith("INV-02:").contains("PROD-B");
    }

    @Test
    @DisplayName("INV-03 违规 → 返回违规明细")
    void detectsInv03Violation() {
        Map<String, Object> payload = payload(
                List.of(elig("PROD-C", "1.0", "UNKNOWN")),
                List.of(fit("PROD-C", "1.0", 2, 0.7)));

        List<String> v = ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload);

        assertThat(v).hasSize(1);
        assertThat(v.get(0)).startsWith("INV-03:");
    }

    @Test
    @DisplayName("核心：detectViolations 不得修改 payload（落库数据须与 KERT 原始返回一致）")
    void doesNotMutatePayload() {
        Map<String, Object> fitEntry = fit("PROD-D", "1.0", 3, 0.6);
        Map<String, Object> payload = payload(
                List.of(elig("PROD-D", "1.0", "INELIGIBLE")),
                List.of(fitEntry));

        List<String> v = ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload);

        assertThat(v).hasSize(1);
        // 原 payload 中的评分必须保持原值，未被置 null
        assertThat(fitEntry.get("fitScore")).isEqualTo(0.6);
        assertThat(fitEntry.get("rank")).isEqualTo(3);
    }

    @Test
    @DisplayName("对比读路径：enforce 会改写，detectViolations 不会")
    void contrastsWithEnforceMutation() {
        Map<String, Object> fitForEnforce = fit("PROD-E", "1.0", 1, 0.5);
        Map<String, Object> fitForDetect = fit("PROD-E", "1.0", 1, 0.5);
        List<Map<String, Object>> elig = List.of(elig("PROD-E", "1.0", "INELIGIBLE"));

        // 读路径：就地中和
        List<String> conflicts = new ArrayList<>();
        ProductRecommendationInvariantGuard.enforce(
                RUN_ID, elig, new ArrayList<>(List.of(fitForEnforce)), conflicts);
        assertThat(fitForEnforce.get("fitScore")).isNull();

        // 写路径：只检测
        ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload(elig, List.of(fitForDetect)));
        assertThat(fitForDetect.get("fitScore")).isEqualTo(0.5);
    }

    @Test
    @DisplayName("多条违规全部返回")
    void detectsMultipleViolations() {
        Map<String, Object> payload = payload(
                List.of(elig("P1", "1.0", "INELIGIBLE"),
                        elig("P2", "1.0", "UNKNOWN"),
                        elig("P3", "1.0", "ELIGIBLE")),
                List.of(fit("P1", "1.0", 1, 0.9),
                        fit("P2", "1.0", 2, 0.8),
                        fit("P3", "1.0", 3, 0.7)));

        List<String> v = ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload);

        assertThat(v).hasSize(2);
        assertThat(v.get(0)).startsWith("INV-02:");
        assertThat(v.get(1)).startsWith("INV-03:");
    }

    @Test
    @DisplayName("null / 空 payload → 无违规不抛异常")
    void toleratesNullAndEmptyPayload() {
        assertThat(ProductRecommendationInvariantGuard.detectViolations(RUN_ID, null)).isEmpty();
        assertThat(ProductRecommendationInvariantGuard.detectViolations(RUN_ID, Map.of())).isEmpty();
    }

    @Test
    @DisplayName("payload 缺 fitResults → 无违规")
    void toleratesMissingFitResults() {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("eligibilityResults", List.of(elig("P1", "1.0", "INELIGIBLE")));

        assertThat(ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload)).isEmpty();
    }

    @Test
    @DisplayName("payload 字段类型异常（非 List）→ 无违规不抛异常")
    void toleratesMalformedFieldTypes() {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("eligibilityResults", "not-a-list");
        payload.put("fitResults", 42);

        assertThat(ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload)).isEmpty();
    }

    @Test
    @DisplayName("返回列表不可变")
    void returnsImmutableList() {
        Map<String, Object> payload = payload(
                List.of(elig("P1", "1.0", "INELIGIBLE")),
                List.of(fit("P1", "1.0", 1, 0.9)));

        List<String> v = ProductRecommendationInvariantGuard.detectViolations(RUN_ID, payload);

        assertThat(v).hasSize(1);
        try {
            v.add("x");
            org.junit.jupiter.api.Assertions.fail("返回列表应不可变");
        } catch (UnsupportedOperationException expected) {
            // 预期
        }
    }

    private static Map<String, Object> payload(List<Map<String, Object>> elig,
                                               List<Map<String, Object>> fit) {
        Map<String, Object> p = new LinkedHashMap<>();
        p.put("eligibilityResults", elig);
        p.put("fitResults", fit);
        return p;
    }

    private static Map<String, Object> elig(String productId, String version, String eligibility) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("productId", productId);
        m.put("productVersion", version);
        m.put("eligibility", eligibility);
        return m;
    }

    private static Map<String, Object> fit(String productId, String version, Integer rank, Double fitScore) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("productId", productId);
        m.put("productVersion", version);
        m.put("rank", rank);
        m.put("fitScore", fitScore);
        return m;
    }
}
