package com.gien.gits.api.productknowledge;

import java.time.Instant;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 产品解读只读控制器（L13 · CTR-PK-INT-001）。
 *
 * <p>只呈现 KERT 已发布 Release 的投影结论，并可回链证据。
 * 全部为只读 GET：GITS 不得拥有产品卡写接口，也不得本地兜底生成结论。
 * 未发布 / 用途不允许 / stale / 源不可达分别返回 404 / 422 / 409 / 503。</p>
 */
@RestController
@RequestMapping("/api/v1/product-knowledge")
@ConditionalOnProperty(name = "gits.product-knowledge.enabled", havingValue = "true", matchIfMissing = true)
public class ProductInterpretationController {

    private static final Logger log = LoggerFactory.getLogger(ProductInterpretationController.class);
    private static final Pattern PRODUCT_ID = Pattern.compile("^PROD-[A-Z]+-[0-9]{3}$");
    private static final java.util.Set<String> ALLOWED_VIEWS =
            java.util.Set.of("OVERVIEW", "ELIGIBILITY", "PRICING");
    private static final java.util.Set<String> ALLOWED_PURPOSES =
            java.util.Set.of("INTERPRETATION", "RECOMMENDATION");
    private static final String PATH_TEMPLATE = "/api/v1/product-knowledge/%s/interpretation";

    private final ProductKnowledgeInterpretationPort port;

    public ProductInterpretationController(ProductKnowledgeInterpretationPort port) {
        this.port = port;
    }

    /**
     * 基础路径不承载资源：此前无 handler，Spring 会把「前缀匹配但参数不满足」
     * 抛成 500 INTERNAL_ERROR，污染告警且误导调用方（F-L13-07）。
     * 显式返回 404，语义为「资源不存在」。
     */
    @GetMapping
    public ResponseEntity<Void> index() {
        return ResponseEntity.notFound().build();
    }

    /**
     * 获取产品解读三视图。
     */
    @GetMapping("/{productId}/interpretation")
    public InterpretationResponse getInterpretation(
            @PathVariable String productId,
            @RequestParam String view,
            @RequestParam String purpose,
            @RequestParam(required = false) String asOf) {
        if (productId == null || !PRODUCT_ID.matcher(productId).matches()) {
            throw new InterpretationRejectedException(HttpStatus.BAD_REQUEST, "BAD_REQUEST",
                    "productId 不符合 PROD-XX-NNN 格式: " + productId);
        }
        String normalizedView = normalizeEnum(view, "view", ALLOWED_VIEWS);
        String normalizedPurpose = normalizeEnum(purpose, "purpose", ALLOWED_PURPOSES);

        Optional<InterpretationProjection> loaded = port.load(productId);
        if (loaded.isEmpty()) {
            throw new InterpretationRejectedException(HttpStatus.NOT_FOUND,
                    "PRODUCT_KNOWLEDGE_NOT_PUBLISHED",
                    productId + " 无已发布 Release（legacy sample 卡不可消费）");
        }
        InterpretationProjection projection = loaded.get();
        if (!"PUBLISHED".equalsIgnoreCase(projection.getLifecycleState())) {
            throw new InterpretationRejectedException(HttpStatus.NOT_FOUND,
                    "PRODUCT_KNOWLEDGE_NOT_PUBLISHED",
                    productId + " 的 Release " + projection.getReleaseId() + " 尚未发布（"
                            + projection.getLifecycleState() + "）");
        }
        if (Boolean.TRUE.equals(projection.getIsStale())) {
            throw new InterpretationRejectedException(HttpStatus.CONFLICT, "RELEASE_STALE",
                    "Release " + projection.getReleaseId() + " 已 stale，需重新发布后方可使用");
        }
        Boolean allowed = projection.getPurposeAllowed().get(normalizedPurpose);
        if (!Boolean.TRUE.equals(allowed)) {
            throw new InterpretationRejectedException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "PURPOSE_NOT_ALLOWED",
                    "Release " + projection.getReleaseId() + " 不允许用于 " + normalizedPurpose + " 用途");
        }

        List<InterpretedField> fields = projection.getViews()
                .getOrDefault(normalizedView, List.of())
                .stream()
                .map(this::toField)
                .toList();

        log.info("[PK-INTERPRETATION] productId={} releaseId={} view={} purpose={} fields={}",
                productId, projection.getReleaseId(), normalizedView, normalizedPurpose, fields.size());

        return new InterpretationResponse(
                projection.getProductId(),
                projection.getReleaseId(),
                projection.getBundleHash(),
                normalizedView,
                normalizedPurpose,
                Boolean.TRUE.equals(projection.getIsStale()),
                fields,
                Instant.now().toString());
    }

    private InterpretedField toField(InterpretationProjection.ProjectionField f) {
        List<EvidenceSummary> summaries = f.getEvidenceSummaries().stream()
                .map(e -> new EvidenceSummary(e.getEvidenceId(), e.getSourceId(),
                        e.getSourceVersionId(), e.getAuthorityLevel(),
                        e.getLocatorHint(), e.getQuoteExcerpt()))
                .toList();
        // CTR-PK-INT-001 的呈现枚举只有 5 态；CANDIDATE 未经 Owner 复核，
        // 防御性归一为 UNKNOWN（fail-closed），并清空证据回链。
        String state = f.getKnowledgeState() == null ? "UNKNOWN" : f.getKnowledgeState();
        if ("CANDIDATE".equalsIgnoreCase(state)) {
            state = "UNKNOWN";
        }
        String value = "SUPPORTED".equals(state) ? f.getDisplayValue() : null;
        // UNKNOWN（无证据）不回链；CONFLICT 保留回链 —— 冲突场景恰恰需要让人看到
        // 两个来源的原文，只是不呈现确定值（displayValue 恒 null）。
        List<EvidenceSummary> visible = "UNKNOWN".equals(state) ? List.of() : summaries;
        return new InterpretedField(f.getFieldPath(), value, state, visible, f.getConflictId());
    }

    private static String normalizeEnum(String raw, String name, java.util.Set<String> allowed) {
        if (raw == null) {
            throw new InterpretationRejectedException(HttpStatus.BAD_REQUEST, "BAD_REQUEST",
                    name + " 为必填参数");
        }
        String normalized = raw.toUpperCase(Locale.ROOT);
        if (!allowed.contains(normalized)) {
            throw new InterpretationRejectedException(HttpStatus.BAD_REQUEST, "BAD_REQUEST",
                    name + " 取值非法: " + raw + "（允许 " + String.join("/", allowed) + "）");
        }
        return normalized;
    }

    @ExceptionHandler(org.springframework.web.bind.MissingServletRequestParameterException.class)
    public ResponseEntity<ProductKnowledgeErrorResponse> handleMissingParam(
            org.springframework.web.bind.MissingServletRequestParameterException ex,
            jakarta.servlet.http.HttpServletRequest request) {
        return ResponseEntity.badRequest().body(new ProductKnowledgeErrorResponse(
                400, "Bad Request", "BAD_REQUEST",
                "缺少必填参数 " + ex.getParameterName(),
                request == null ? String.format(PATH_TEMPLATE, "{productId}")
                        : request.getRequestURI(),
                Instant.now().toString()));
    }

    @ExceptionHandler(InterpretationRejectedException.class)
    public ResponseEntity<ProductKnowledgeErrorResponse> handleRejected(
            InterpretationRejectedException ex, jakarta.servlet.http.HttpServletRequest request) {
        return ResponseEntity.status(ex.status()).body(new ProductKnowledgeErrorResponse(
                ex.status().value(),
                ex.status().getReasonPhrase(),
                ex.code(),
                ex.getMessage(),
                request == null ? String.format(PATH_TEMPLATE, "{productId}") : request.getRequestURI(),
                Instant.now().toString()));
    }

    @ExceptionHandler(KnowledgeSourceUnavailableException.class)
    public ResponseEntity<ProductKnowledgeErrorResponse> handleUnavailable(
            KnowledgeSourceUnavailableException ex, jakarta.servlet.http.HttpServletRequest request) {
        log.error("[PK-INTERPRETATION] 受控失败: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new ProductKnowledgeErrorResponse(
                        503, "Service Unavailable", "FAILED_CLOSED", ex.getMessage(),
                        request == null ? String.format(PATH_TEMPLATE, "{productId}")
                                : request.getRequestURI(),
                        Instant.now().toString()));
    }
}
