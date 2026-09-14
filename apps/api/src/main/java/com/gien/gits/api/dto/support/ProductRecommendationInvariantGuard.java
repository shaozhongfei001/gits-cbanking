package com.gien.gits.api.dto.support;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

/**
 * 产品推荐阶段结果不变量守卫（GAP-2 / GAP-3）。
 *
 * <p>强制 CTR-PR-ELIG-001 与 CTR-PR-FIT-001 的两条不变量，一处覆盖两项：</p>
 * <ul>
 *   <li><b>INV-02</b>：{@code eligibility=INELIGIBLE} 的产品不得携带 {@code fitScore}/{@code rank}。
 *       此前后端不校验，KERT 返回违规值会直接透传给前端。</li>
 *   <li><b>INV-03</b>：{@code eligibility=UNKNOWN} 不得按 {@code ELIGIBLE} 处理，因而同样不得携带评分。</li>
 * </ul>
 *
 * <h2>处置策略：中和 + 标记 + 告警，不抛异常</h2>
 *
 * <p>违规项的 {@code fitScore} 与 {@code rank} 就地置 null，违规明细以
 * {@code INV-02:} / {@code INV-03:} 前缀追加进 {@code conflicts}，并打 WARN 日志。
 * HTTP 仍返回 200。</p>
 *
 * <p>选择不抛 422 的三条依据：</p>
 * <ol>
 *   <li><b>合同不允许</b>：{@code specs/openapi/product-recommendation.openapi.json} 中
 *       {@code getProductRecommendationStages} 只登记 200 与 404。抛 422 属未登记响应码，
 *       等于用一处 API First 违规去修另一处（F-3 批评的正是同类问题）。</li>
 *   <li><b>fail-closed 的作用点不在只读路径</b>：INV-07 约束的是「不得生产出假推荐」，
 *       针对写路径。{@code getStages} 是纯只读投影，整体 422 掉不会阻止任何错误决策，
 *       只会让客户经理连「这轮为什么被排除」都看不到，反而促使其走旁路渠道。</li>
 *   <li><b>中和已实质达成防护目的</b>：前端 {@code ProductCandidateCompare.vue} 按
 *       {@code rank != null && fitScore != null} 过滤候选，置 null 后违规产品自动从
 *       候选对比表消失。这是外科手术式 fail-closed——污染项被摘除，其余视图仍可用。</li>
 * </ol>
 *
 * <p><b>剩余缺口（不掩盖）</b>：</p>
 * <ul>
 *   <li>违规明细混入 {@code conflicts} 会与 INV-10「权威证据冲突」语义共用同一数组，
 *       前端以「权威证据冲突」标题渲染。已加 {@code INV-0x:} 前缀便于分流，但这是技术债，
 *       与 GAP-7 相关。彻底解法是新增 {@code invariantViolations} 字段，需改 OpenAPI，
 *       本 Loop 红线禁止碰产品推荐合同冻结，故延后。</li>
 *   <li>写路径（{@code executeKert} 结果落库前）的同源校验未做。那才是 INV-07 的正确落点：
 *       契约违规应走 {@code KERT_CONTRACT_MISMATCH} → run {@code FAILED_CLOSED}。需另立 Loop。</li>
 * </ul>
 *
 * <p>状态 CANDIDATE / FROZEN=NO。</p>
 */
public final class ProductRecommendationInvariantGuard {

    private static final Logger log =
            LoggerFactory.getLogger(ProductRecommendationInvariantGuard.class);

    /** 唯一允许携带评分的资格态。其余一切取值（含未来新增枚举）均禁止评分，fail-safe 取向。 */
    private static final String ELIGIBLE = "ELIGIBLE";

    /** 明确的禁分态，用于区分应记 INV-02 还是 INV-03。 */
    private static final Set<String> KNOWN_INELIGIBLE = Set.of("INELIGIBLE");

    /**
     * 只检测不改写，用于写路径 fail-closed（FAIL-2026-09-04-03）。
     *
     * <p>与 {@link #enforce} 的区别：{@code enforce} 用于只读投影，就地中和违规评分并放行；
     * 本方法用于 KERT 结果落库前，只返回违规明细，由调用方决定拒收。payload 不被修改。</p>
     *
     * <p>处置差异是刻意的：读路径已落库的脏数据摘除污染项仍可用（否则客户经理连排除原因
     * 都看不到）；写路径尚未落库，此时拒收成本最低，且能防止脏数据扩散到 worker、导出等
     * 其它消费方。后者才是 INV-07 的正确落点。</p>
     *
     * @param runId   仅用于日志归因
     * @param payload KERT 返回的原始结果，不会被修改
     * @return 违规明细列表；空列表表示通过
     */
    @SuppressWarnings("unchecked")
    public static List<String> detectViolations(String runId, Map<String, Object> payload) {
        if (payload == null || payload.isEmpty()) {
            return List.of();
        }
        List<Map<String, Object>> eligibilityResults = asListOfMaps(payload.get("eligibilityResults"));
        List<Map<String, Object>> fitResults = asListOfMaps(payload.get("fitResults"));
        if (fitResults.isEmpty()) {
            return List.of();
        }
        // 深拷贝待检字段，确保 enforce 的就地改写不触及原 payload
        List<Map<String, Object>> fitCopy = new ArrayList<>(fitResults.size());
        for (Map<String, Object> fit : fitResults) {
            fitCopy.add(new LinkedHashMap<>(fit));
        }
        List<String> violations = new ArrayList<>();
        enforce(runId, eligibilityResults, fitCopy, violations);
        return List.copyOf(violations);
    }

    @SuppressWarnings("unchecked")
    private static List<Map<String, Object>> asListOfMaps(Object value) {
        if (!(value instanceof List<?> list)) {
            return List.of();
        }
        List<Map<String, Object>> out = new ArrayList<>(list.size());
        for (Object item : list) {
            if (item instanceof Map<?, ?> map) {
                out.add((Map<String, Object>) map);
            }
        }
        return out;
    }

    private ProductRecommendationInvariantGuard() {
    }

    /**
     * 就地校验并中和违规评分。
     *
     * @param runId              仅用于日志归因
     * @param eligibilityResults 第一段硬约束结果，提供 {@code eligibility} 事实来源
     * @param fitResults         第二段需求匹配结果，评分所在处；违规项将被就地改写
     * @param conflicts          可变列表，违规明细追加至此
     */
    public static void enforce(String runId,
                               List<Map<String, Object>> eligibilityResults,
                               List<Map<String, Object>> fitResults,
                               List<String> conflicts) {
        if (fitResults == null || fitResults.isEmpty()) {
            return;
        }
        Map<String, String> byKey = new LinkedHashMap<>();
        Map<String, String> byProductId = new LinkedHashMap<>();
        if (eligibilityResults != null) {
            for (Map<String, Object> entry : eligibilityResults) {
                String productId = text(entry.get("productId"));
                String eligibility = upper(text(entry.get("eligibility")));
                if (productId.isEmpty() || eligibility.isEmpty()) {
                    continue;
                }
                byKey.put(compositeKey(productId, text(entry.get("productVersion"))), eligibility);
                byProductId.putIfAbsent(productId, eligibility);
            }
        }

        for (Map<String, Object> fit : fitResults) {
            String productId = text(fit.get("productId"));
            String productVersion = text(fit.get("productVersion"));
            String eligibility = resolveEligibility(byKey, byProductId, productId, productVersion);

            if (ELIGIBLE.equals(eligibility)) {
                continue;
            }
            Object fitScore = fit.get("fitScore");
            Object rank = fit.get("rank");
            if (fitScore == null && rank == null) {
                continue;
            }
            String invariant = KNOWN_INELIGIBLE.contains(eligibility) ? "INV-02" : "INV-03";
            fit.put("fitScore", null);
            fit.put("rank", null);
            conflicts.add(String.format(
                    "%s: productId=%s@%s eligibility=%s 但携带 fitScore=%s rank=%s，已按契约中和为 null",
                    invariant, productId, productVersion, eligibility, fitScore, rank));
            log.warn("[PR-INV] {} violated: runId={} productId={}@{} eligibility={} fitScore={} rank={}",
                    invariant, runId, productId, productVersion, eligibility, fitScore, rank);
        }
    }

    /**
     * 解析产品的资格态。
     *
     * <p>先按 productId+productVersion 精确匹配，退化到仅 productId。两者皆无命中时返回
     * {@code UNKNOWN}——fitResults 出现了 eligibilityResults 中不存在的产品，其资格未经硬约束
     * 过滤，按 INV-03 保守处理，不得视同合格。</p>
     */
    private static String resolveEligibility(Map<String, String> byKey,
                                             Map<String, String> byProductId,
                                             String productId,
                                             String productVersion) {
        String exact = byKey.get(compositeKey(productId, productVersion));
        if (exact != null) {
            return exact;
        }
        String fallback = byProductId.get(productId);
        return fallback != null ? fallback : "UNKNOWN";
    }

    private static String compositeKey(String productId, String productVersion) {
        return productId + "@" + productVersion;
    }

    private static String text(Object value) {
        return value == null ? "" : String.valueOf(value).trim();
    }

    private static String upper(String value) {
        return value.toUpperCase(Locale.ROOT);
    }
}
