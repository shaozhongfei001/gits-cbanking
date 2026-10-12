package com.gien.gits.api.productknowledge;

/**
 * 解读端点的统一错误响应（CTR-PK-INT-001）。
 */
public record ProductKnowledgeErrorResponse(
        int status,
        String error,
        String code,
        String message,
        String path,
        String timestamp) {
}
