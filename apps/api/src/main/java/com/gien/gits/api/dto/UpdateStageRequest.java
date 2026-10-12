package com.gien.gits.api.dto;

import java.util.Objects;

/**
 * 阶段更新请求体（OpenAPI schema=UpdateStageRequest）。
 *
 * <p>用于商机阶段推进 PUT 端点，字段与 OpenAPI 合同一致。</p>
 *
 * @param stage 目标阶段
 */
public record UpdateStageRequest(String stage) {

    public UpdateStageRequest {
        Objects.requireNonNull(stage, "stage must not be null");
    }
}
