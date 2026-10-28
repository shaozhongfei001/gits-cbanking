package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 任务上下文（C06 §2：/v1/activation/plan 请求体）。
 *
 * <p>字段与 C06 合同 TaskContext 对齐；驱动地图选择、权限过滤与计划装配。
 *
 * @param tenantId            租户 ID
 * @param orgIds              授权机构 ID
 * @param customerIds         授权客户 ID
 * @param purpose             用途
 * @param channel             渠道（RM_WORKBENCH/API/SIMULATION）
 * @param conversationId      会话 ID
 * @param taskId              任务 ID
 * @param taskType            任务类型（PRODUCT_EXPLAIN/COMPARISON/RISK_EXPLAIN 等）
 * @param requiredAssetClasses 要求的资产大类
 * @param budget              执行预算
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record TaskContextRecord(
        String tenantId,
        List<String> orgIds,
        List<String> customerIds,
        String purpose,
        String channel,
        String conversationId,
        String taskId,
        String taskType,
        List<String> requiredAssetClasses,
        Budget budget) {
}
