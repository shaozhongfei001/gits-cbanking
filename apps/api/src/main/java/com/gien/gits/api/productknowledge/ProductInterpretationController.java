package com.gien.gits.api.productknowledge;

import java.time.Instant;
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
import org.springframework.web.bind.annotation.RestController;

/**
 * 产品卡只读控制器（原 CTR-PK-INT-001 解读控制器，2026-10-28 收缩为卡片链路）。
 *
 * <p>「产品知识」二菜单（{@code /product-knowledge/interpretation}，P38 老解读页）随 Owner 指令下线，
 * 其独占的三视图解读端点 {@code GET /{productId}/interpretation} 与 LightRAG 派生检索端点
 * {@code POST /{productId}/retrieval} 一并删除；解读投影快照端口
 * （{@code ProductKnowledgeInterpretationPort} / {@code KertReleaseSnapshotAdapter}）同步移除。</p>
 *
 * <p>本控制器只保留产品中心仍在使用的只读能力：卡片目录与卡片详情。
 * GITS 不得拥有产品卡写接口，也不得本地兜底生成产品结论。</p>
 */
@RestController
@RequestMapping("/api/v1/product-knowledge")
@ConditionalOnProperty(name = "gits.product-knowledge.enabled", havingValue = "true", matchIfMissing = true)
public class ProductInterpretationController {

    private static final Logger log = LoggerFactory.getLogger(ProductInterpretationController.class);
    private static final Pattern PRODUCT_ID = Pattern.compile("^PROD-[A-Z]+-[0-9]{3}$");
    private static final String PATH_TEMPLATE = "/api/v1/product-knowledge/%s";

    private final ProductCardCatalogService cardCatalog;

    public ProductInterpretationController(ProductCardCatalogService cardCatalog) {
        this.cardCatalog = cardCatalog;
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
     * 产品卡目录列表（产品全景）。来源为 KERT 产品卡文件，只读呈现。
     */
    @GetMapping("/cards")
    public ResponseEntity<java.util.List<ProductCardSummary>> listCards() {
        return ResponseEntity.ok(cardCatalog.listSummaries());
    }

    /**
     * 单个产品卡详情（含原始产品文档全文，供「深度解读」与「原始材料」展示）。
     */
    @GetMapping("/cards/{productId}")
    public ResponseEntity<ProductCardDetail> getCard(@PathVariable String productId) {
        // productId 格式错误 → 400，未知产品 → 404。两者均经
        // {@link InterpretationRejectedException} 统一成
        // ProductKnowledgeErrorResponse（仓库规则 §2：所有 API 错误返回统一结构）。
        if (productId == null || !PRODUCT_ID.matcher(productId).matches()) {
            throw new InterpretationRejectedException(HttpStatus.BAD_REQUEST, "BAD_REQUEST",
                    "productId 不符合 PROD-XX-NNN 格式: " + productId);
        }
        return cardCatalog.loadDetail(productId)
                .map(ResponseEntity::ok)
                .orElseThrow(() -> new InterpretationRejectedException(
                        HttpStatus.NOT_FOUND, "NOT_FOUND",
                        "产品卡不存在: " + productId));
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
        log.error("[PK-CATALOG] 受控失败: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(new ProductKnowledgeErrorResponse(
                        503, "Service Unavailable", "FAILED_CLOSED", ex.getMessage(),
                        request == null ? String.format(PATH_TEMPLATE, "{productId}")
                                : request.getRequestURI(),
                        Instant.now().toString()));
    }
}
