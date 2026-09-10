package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 激活计划（CTR-GKKE-005 / C06 §2）。
 *
 * @param contractVersion       合同版本
 * @param simulationOnly        是否仅模拟
 * @param planId                计划 ID
 * @param taskId                任务 ID
 * @param mapRef                地图引用
 * @param releaseId             发布 ID
 * @param coreVersion           公共核心版本
 * @param catalogRevision       目录版本号
 * @param routePolicyVersion    路由策略版本
 * @param assetRefs             资产引用
 * @param capabilityRefs        能力引用
 * @param queryRefs             查询引用
 * @param steps                 执行步骤
 * @param permissionDecisionRef 权限决议引用
 * @param purpose               用途
 * @param scope                 授权范围
 * @param budget                执行预算
 * @param planHash              计划规范化哈希
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record ActivationPlanRecord(
        String contractVersion,
        Boolean simulationOnly,
        String planId,
        String taskId,
        VersionRef mapRef,
        String releaseId,
        String coreVersion,
        Integer catalogRevision,
        String routePolicyVersion,
        List<VersionRef> assetRefs,
        List<VersionRef> capabilityRefs,
        List<VersionRef> queryRefs,
        List<PlanStep> steps,
        String permissionDecisionRef,
        String purpose,
        Scope scope,
        Budget budget,
        String planHash) {
}
