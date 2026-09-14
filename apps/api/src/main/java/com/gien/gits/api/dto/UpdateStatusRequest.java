package com.gien.gits.api.dto;

import java.util.Objects;

/**
 * 状态更新请求体（OpenAPI schema=UpdateStatusRequest）。
 *
 * <p>用于承诺/任务等资源的状态更新 PUT 端点，字段与 OpenAPI 合同一致。</p>
 *
 * @param status 目标状态
 */
public record UpdateStatusRequest(String status) {

    public UpdateStatusRequest {
        Objects.requireNonNull(status, "status must not be null");
    }
}
