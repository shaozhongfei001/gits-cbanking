package com.gien.gits.api.controller;

import com.gien.gits.api.dto.ErrorResponse;
import com.gien.gits.customerjourney.recommendation.RecommendationGatePreconditionException;
import com.gien.gits.customerjourney.recommendation.RecommendationVersionConflictException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.Instant;

/**
 * 产品推荐 HumanGate（HG-D01）异常 → HTTP 语义映射（WP5-2，CANDIDATE）。
 *
 * <ul>
 *   <li>{@link RecommendationVersionConflictException} → 409 Conflict（If-Match/ETag 过期或并发版本过期，
 *       不得覆盖先提交者的决定，见 ADR-PR-010）。</li>
 *   <li>{@link RecommendationGatePreconditionException} → PERMISSION_DENIED 语义 403，其余前置失败 422。</li>
 * </ul>
 *
 * <p>与 {@link GlobalExceptionHandler} 并存：本 advice 只处理上述特定异常，其余异常仍由全局处理器兜底。
 * 以 {@code HIGHEST_PRECEDENCE} 注册，避免被全局 {@code @ExceptionHandler(Exception.class)} 的
 * 兜底处理器先匹配（Spring 对多个 {@code @ControllerAdvice} 采用“首个可解析者胜”的迭代顺序）。</p>
 */
@RestControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE)
public class RecommendationExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(RecommendationExceptionHandler.class);

    @ExceptionHandler(RecommendationVersionConflictException.class)
    public ResponseEntity<ErrorResponse> handleVersionConflict(RecommendationVersionConflictException ex) {
        log.warn("Recommendation version conflict: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(new ErrorResponse(
            "VERSION_CONFLICT",
            ex.getMessage() != null ? ex.getMessage() : "Proposal version conflict",
            Instant.now().toString()));
    }

    @ExceptionHandler(RecommendationGatePreconditionException.class)
    public ResponseEntity<ErrorResponse> handlePrecondition(RecommendationGatePreconditionException ex) {
        HttpStatus status = "PERMISSION_DENIED".equals(ex.code())
            ? HttpStatus.FORBIDDEN
            : HttpStatus.UNPROCESSABLE_ENTITY;
        log.warn("Recommendation gate precondition failed: code={} message={}", ex.code(), ex.getMessage());
        return ResponseEntity.status(status).body(new ErrorResponse(
            ex.code(),
            ex.getMessage() != null ? ex.getMessage() : "Gate precondition failed",
            Instant.now().toString()));
    }
}
