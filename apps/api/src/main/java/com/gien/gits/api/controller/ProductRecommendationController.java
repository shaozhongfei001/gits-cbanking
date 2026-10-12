package com.gien.gits.api.controller;

import com.gien.gits.api.dto.ProductRecommendationCreateRequest;
import com.gien.gits.api.dto.ProductRecommendationProposalVersionDto;
import com.gien.gits.api.dto.ProductRecommendationRunDto;
import com.gien.gits.api.dto.ProductRecommendationStageResultDto;
import com.gien.gits.api.service.ProductRecommendationApplicationService;
import com.gien.gits.customerjourney.recommendation.port.ProductRecommendationRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.Objects;

/**
 * 产品推荐三段式决策 REST 控制器（CTR-PR-API-001，CANDIDATE）。
 *
 * <p>薄控制器：仅 HTTP 职责（鉴权头、参数校验、DTO 映射），业务逻辑与状态推进
 * 全部委托 {@link ProductRecommendationApplicationService} 与
 * {@link ProductRecommendationRepository}；错误经
 * {@link RecommendationExceptionHandler}（409/422/403）与
 * {@link GlobalExceptionHandler}（400/404/409）映射。</p>
 *
 * <p>端点：createRun（Idempotency-Key 幂等）、getRun、getStages（只读组合视图）、
 * getVersion、retry（仅 REQUESTED 可重试，新 attempt 不覆盖旧轨迹）。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
@RestController
@RequestMapping("/api/v1/product-recommendation-runs")
public class ProductRecommendationController {

    private static final Logger log = LoggerFactory.getLogger(ProductRecommendationController.class);

    private final ProductRecommendationApplicationService applicationService;
    private final ProductRecommendationRepository repository;

    public ProductRecommendationController(ProductRecommendationApplicationService applicationService,
                                           ProductRecommendationRepository repository) {
        this.applicationService = Objects.requireNonNull(applicationService, "applicationService");
        this.repository = Objects.requireNonNull(repository, "repository");
    }

    /** POST /api/v1/product-recommendation-runs —— 创建运行（Idempotency-Key 幂等）。 */
    @PostMapping
    public ResponseEntity<ProductRecommendationRunDto> createRun(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestHeader(value = "X-RM-ID", required = false) String rmId,
            @RequestBody ProductRecommendationCreateRequest request) {
        if (idempotencyKey == null || idempotencyKey.isBlank()) {
            throw new IllegalArgumentException("Idempotency-Key header is required");
        }
        log.info("[PR-CTRL] createRun customerId={} objective={} idem={}",
                 request.customerId(), request.recommendationObjective(), idempotencyKey);
        var run = applicationService.createRun(new ProductRecommendationApplicationService.CreateRunCommand(
                rmId, request.customerId(), request.journeyId(), request.operatingCaseId(),
                request.needVersionIds(), request.recommendationObjective(),
                request.requestedProductDomains(), request.asOf(), idempotencyKey,
                request.customerFactSnapshotId(), request.productKnowledgeSnapshotRef(),
                request.ruleBundleRef(), request.permissionDecisionId(), request.activationContract()));
        return ResponseEntity.ok(ProductRecommendationRunDto.from(run));
    }

    /** GET /api/v1/product-recommendation-runs/{runId} —— 查询总体状态与当前版本（只读）。 */
    @GetMapping("/{runId}")
    public ResponseEntity<ProductRecommendationRunDto> getRun(@PathVariable String runId) {
        return repository.findRunById(runId)
                .map(run -> ResponseEntity.ok(ProductRecommendationRunDto.from(run)))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    /** GET /api/v1/product-recommendation-runs/{runId}/stages —— 三段式阶段结果（只读组合视图）。 */
    @GetMapping("/{runId}/stages")
    public ResponseEntity<ProductRecommendationStageResultDto> getStages(@PathVariable String runId) {
        var run = repository.findRunById(runId).orElse(null);
        if (run == null) {
            return ResponseEntity.notFound().build();
        }
        Map<String, Object> payload = run.currentVersionId() == null
                ? Map.of()
                : repository.findVersionById(run.currentVersionId())
                        .map(v -> v.payload())
                        .orElse(Map.of());
        return ResponseEntity.ok(ProductRecommendationStageResultDto.from(run, payload));
    }

    /** GET /api/v1/product-recommendation-runs/{runId}/versions/{versionId} —— 不可变方案版本（只读）。 */
    @GetMapping("/{runId}/versions/{versionId}")
    public ResponseEntity<ProductRecommendationProposalVersionDto> getVersion(
            @PathVariable String runId,
            @PathVariable String versionId) {
        return repository.findVersionById(versionId)
                .filter(v -> v.runId().equals(runId))
                .map(v -> ResponseEntity.ok(ProductRecommendationProposalVersionDto.from(v)))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    /** POST /api/v1/product-recommendation-runs/{runId}/retry —— 对可重试失败发起新 attempt。 */
    @PostMapping("/{runId}/retry")
    public ResponseEntity<ProductRecommendationRunDto> retry(@PathVariable String runId) {
        if (repository.findRunById(runId).isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        var run = applicationService.retryRun(runId);
        return ResponseEntity.ok(ProductRecommendationRunDto.from(run));
    }
}
