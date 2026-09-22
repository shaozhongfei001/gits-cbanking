package com.gien.gits.api.productcenter;

import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import java.util.List;
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
 * 产品中心只读控制器（CTR-PKC-API-001 · REQ-PI-01 / Loop PC1）。
 *
 * <p><b>硬边界（需求 §三）</b>：产品为主语；不读取任何客户上下文；
 * 不输出适配度/推荐分/排名/赢单概率；不承诺额度、价格、担保、时效与审批结果。
 * 本控制器<b>只有</b>只读 GET，不提供任何写接口。</p>
 *
 * <p><b>PC1 范围</b>：{@code families} / {@code products} / {@code products/{productId}} 三个端点。
 * 其余 12 个端点（章节分片、搜索、版本、完整度、收藏、下载、提纲、助手、证据定位、反馈）
 * 由 PC2–PC5 按合同实现。</p>
 */
@RestController
@RequestMapping("/api/v1/product-center")
@ConditionalOnProperty(name = "gits.product-center.enabled", havingValue = "true", matchIfMissing = true)
public class ProductCenterController {

    private static final Logger log = LoggerFactory.getLogger(ProductCenterController.class);

    private final ProductCenterCatalogService catalogService;

    public ProductCenterController(ProductCenterCatalogService catalogService) {
        this.catalogService = catalogService;
    }

    /** 基础路径不承载资源：显式 404，避免 Spring 把前缀匹配失败抛成 500。 */
    @GetMapping
    public ResponseEntity<Void> index() {
        return ResponseEntity.notFound().build();
    }

    /** 产品族目录（PI-FR-009/010/014）。 */
    @GetMapping("/families")
    public List<ProductCenterFamily> families(@RequestParam(required = false) String keyword) {
        return catalogService.listFamilies();
    }

    /** 产品目录（按族/关键词；权限与有效版本过滤在 PC2 接入身份服务后生效）。 */
    @GetMapping("/products")
    public List<ProductCenterProductEntry> products(@RequestParam(required = false) String familyId,
                                                    @RequestParam(required = false) String keyword) {
        return catalogService.listProducts(familyId, keyword);
    }

    /** 产品详情（PC1 子集：首屏 + 版本 + 固定边界语句）。 */
    @GetMapping("/products/{productId}")
    public ProductCenterDetail detail(@PathVariable String productId) {
        return catalogService.loadDetail(productId);
    }

    // ── 受控失败矩阵（CTR-PKC-API-001） ─────────────────────────────────────

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ProductCenterErrorResponse> badRequest(IllegalArgumentException ex,
                                                                HttpServletRequest request) {
        return error(HttpStatus.BAD_REQUEST, "BAD_REQUEST", ex.getMessage(), request);
    }

    @ExceptionHandler(ProductNotFoundException.class)
    public ResponseEntity<ProductCenterErrorResponse> notFound(ProductNotFoundException ex,
                                                              HttpServletRequest request) {
        return error(HttpStatus.NOT_FOUND, "PRODUCT_NOT_FOUND", ex.getMessage(), request);
    }

    @ExceptionHandler(NoPublishedVersionException.class)
    public ResponseEntity<ProductCenterErrorResponse> noVersion(NoPublishedVersionException ex,
                                                                HttpServletRequest request) {
        return error(HttpStatus.NOT_FOUND, "NO_PUBLISHED_VERSION", ex.getMessage(), request);
    }

    @ExceptionHandler(ProductCenterSourceUnavailableException.class)
    public ResponseEntity<ProductCenterErrorResponse> sourcesUnavailable(
            ProductCenterSourceUnavailableException ex, HttpServletRequest request) {
        log.error("[PC-CATALOG] 知识源不可用（fail-closed，不本地兜底）: {}", ex.getMessage());
        return error(HttpStatus.SERVICE_UNAVAILABLE, "SOURCES_UNAVAILABLE", ex.getMessage(), request);
    }

    private ResponseEntity<ProductCenterErrorResponse> error(HttpStatus status, String code,
                                                            String message, HttpServletRequest request) {
        return ResponseEntity.status(status).body(new ProductCenterErrorResponse(
                status.value(),
                status.getReasonPhrase(),
                code,
                message,
                request.getRequestURI(),
                Instant.now().toString()));
    }
}
