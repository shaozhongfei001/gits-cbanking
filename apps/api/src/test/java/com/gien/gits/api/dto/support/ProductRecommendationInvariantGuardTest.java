package com.gien.gits.api.dto.support;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * {@link ProductRecommendationInvariantGuard} 单元测试（GAP-2 / GAP-3）。
 *
 * <p>覆盖 INV-02（INELIGIBLE 禁分）与 INV-03（UNKNOWN 不得按 ELIGIBLE 处理），
 * 并显式防守卫过度杀伤——合法的 ELIGIBLE + 评分必须原样透传。</p>
 */
class ProductRecommendationInvariantGuardTest {

    private static final String RUN_ID = "run-001";

    @Test
    @DisplayName("INV-02：INELIGIBLE 携带 fitScore/rank → 中和为 null 并记 conflicts")
    void neutralizesIneligibleWithScore() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-CM-001", "1.0", "INELIGIBLE"));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-CM-001", "1.0", 1, 0.85)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("fitScore")).isNull();
        assertThat(fit.get(0).get("rank")).isNull();
        assertThat(conflicts).hasSize(1);
        assertThat(conflicts.get(0)).startsWith("INV-02:").contains("PROD-CM-001@1.0").contains("INELIGIBLE");
    }

    @Test
    @DisplayName("INV-03：UNKNOWN 携带 fitScore → 中和并记 INV-03")
    void neutralizesUnknownWithScore() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-TF-001", "2.1", "UNKNOWN"));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-TF-001", "2.1", 2, 0.7)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("fitScore")).isNull();
        assertThat(fit.get(0).get("rank")).isNull();
        assertThat(conflicts.get(0)).startsWith("INV-03:").contains("UNKNOWN");
    }

    @ParameterizedTest
    @ValueSource(strings = {"REVIEW_REQUIRED", "SOME_FUTURE_STATUS", "ineligible"})
    @DisplayName("fail-safe：非 ELIGIBLE 的一切取值（含未来枚举、小写）均禁止评分")
    void neutralizesAnyNonEligibleStatus(String status) {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-X", "1.0", status));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-X", "1.0", 1, 0.5)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("fitScore")).isNull();
        assertThat(conflicts).hasSize(1);
    }

    @Test
    @DisplayName("防过度杀伤：ELIGIBLE + 评分 → 原样透传，不记 conflicts")
    void passesThroughEligibleWithScore() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-CM-003", "1.0", "ELIGIBLE"));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-CM-003", "1.0", 1, 0.9)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("fitScore")).isEqualTo(0.9);
        assertThat(fit.get(0).get("rank")).isEqualTo(1);
        assertThat(conflicts).isEmpty();
    }

    @Test
    @DisplayName("大小写与空白不敏感：eligible 视同 ELIGIBLE，评分透传")
    void normalizesEligibleCasing() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-A", "1.0", " eligible "));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-A", "1.0", 1, 0.8)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("fitScore")).isEqualTo(0.8);
        assertThat(conflicts).isEmpty();
    }

    @Test
    @DisplayName("INV-03 保守：fitResults 出现 eligibilityResults 中不存在的产品 → 视同 UNKNOWN 中和")
    void treatsMissingEligibilityAsUnknown() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-A", "1.0", "ELIGIBLE"));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-GHOST", "9.9", 1, 0.95)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("fitScore")).isNull();
        assertThat(conflicts.get(0)).startsWith("INV-03:").contains("PROD-GHOST");
    }

    @Test
    @DisplayName("版本退化匹配：productVersion 不一致时退化按 productId 匹配")
    void fallsBackToProductIdWhenVersionMismatched() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-B", "1.0", "INELIGIBLE"));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-B", "2.0", 1, 0.6)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("fitScore")).isNull();
        assertThat(conflicts.get(0)).startsWith("INV-02:");
    }

    @Test
    @DisplayName("非 ELIGIBLE 但本就无评分 → 不记 conflicts（无违规）")
    void ignoresNonEligibleWithoutScore() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-C", "1.0", "INELIGIBLE"));
        Map<String, Object> noScore = new LinkedHashMap<>();
        noScore.put("productId", "PROD-C");
        noScore.put("productVersion", "1.0");
        noScore.put("fitScore", null);
        noScore.put("rank", null);
        List<Map<String, Object>> fit = new ArrayList<>(List.of(noScore));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(conflicts).isEmpty();
    }

    @Test
    @DisplayName("仅 rank 无 fitScore 也算违规：不留孤儿排名")
    void neutralizesOrphanRank() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-D", "1.0", "INELIGIBLE"));
        Map<String, Object> orphan = new LinkedHashMap<>();
        orphan.put("productId", "PROD-D");
        orphan.put("productVersion", "1.0");
        orphan.put("rank", 3);
        List<Map<String, Object>> fit = new ArrayList<>(List.of(orphan));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(fit.get(0).get("rank")).isNull();
        assertThat(conflicts).hasSize(1);
    }

    @Test
    @DisplayName("空 fitResults / null 入参 → 直接放行不抛异常")
    void toleratesEmptyInputs() {
        List<String> conflicts = new ArrayList<>();
        ProductRecommendationInvariantGuard.enforce(RUN_ID, List.of(), new ArrayList<>(), conflicts);
        ProductRecommendationInvariantGuard.enforce(RUN_ID, null, null, conflicts);
        ProductRecommendationInvariantGuard.enforce(RUN_ID, List.of(), null, conflicts);
        assertThat(conflicts).isEmpty();
    }

    @Test
    @DisplayName("保留既有 conflicts：违规明细追加而非覆盖")
    void appendsToExistingConflicts() {
        List<Map<String, Object>> eligibility = List.of(elig("PROD-E", "1.0", "INELIGIBLE"));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(fit("PROD-E", "1.0", 1, 0.4)));
        List<String> conflicts = new ArrayList<>(List.of("必备材料缺失，需客户经理补齐并复核"));

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(conflicts).hasSize(2);
        assertThat(conflicts.get(0)).isEqualTo("必备材料缺失，需客户经理补齐并复核");
        assertThat(conflicts.get(1)).startsWith("INV-02:");
    }

    @Test
    @DisplayName("多条违规逐项记录")
    void recordsMultipleViolations() {
        List<Map<String, Object>> eligibility = List.of(
                elig("PROD-1", "1.0", "INELIGIBLE"),
                elig("PROD-2", "1.0", "UNKNOWN"),
                elig("PROD-3", "1.0", "ELIGIBLE"));
        List<Map<String, Object>> fit = new ArrayList<>(List.of(
                fit("PROD-1", "1.0", 1, 0.9),
                fit("PROD-2", "1.0", 2, 0.8),
                fit("PROD-3", "1.0", 3, 0.7)));
        List<String> conflicts = new ArrayList<>();

        ProductRecommendationInvariantGuard.enforce(RUN_ID, eligibility, fit, conflicts);

        assertThat(conflicts).hasSize(2);
        assertThat(conflicts.get(0)).startsWith("INV-02:");
        assertThat(conflicts.get(1)).startsWith("INV-03:");
        assertThat(fit.get(2).get("fitScore")).isEqualTo(0.7);
    }

    private static Map<String, Object> elig(String productId, String version, String eligibility) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("schemaVersion", "1.0.0");
        m.put("productId", productId);
        m.put("productVersion", version);
        m.put("eligibility", eligibility);
        return m;
    }

    private static Map<String, Object> fit(String productId, String version, Integer rank, Double fitScore) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("schemaVersion", "1.0.0");
        m.put("productId", productId);
        m.put("productVersion", version);
        m.put("rank", rank);
        m.put("fitScore", fitScore);
        return m;
    }
}
