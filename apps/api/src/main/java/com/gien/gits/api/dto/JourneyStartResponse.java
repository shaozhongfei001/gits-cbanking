package com.gien.gits.api.dto;

/**
 * 旅程启动响应 — 返回新创建的客户旅程信息
 *
 * @param journeyId        旅程唯一标识
 * @param customerId       客户唯一标识
 * @param operatingCaseId  经营案例唯一标识（后续访前/访后/迭代操作必需）
 * @param phase            旅程当前阶段
 * @param startedAt        旅程启动时间（ISO格式）
 * @param kycGapSummary    KYC缺口摘要（可能为null）
 * @param journeyName      经营旅程名称（人工填写或服务端派生，非空）
 */
public record JourneyStartResponse(
        String journeyId,
        String customerId,
        String operatingCaseId,
        String phase,
        String startedAt,
        String kycGapSummary,
        String journeyName) {
    public JourneyStartResponse(String journeyId, String customerId, String operatingCaseId,
                                String phase, String startedAt) {
        this(journeyId, customerId, operatingCaseId, phase, startedAt, null, null);
    }

    public JourneyStartResponse(String journeyId, String customerId, String operatingCaseId,
                                String phase, String startedAt, String kycGapSummary) {
        this(journeyId, customerId, operatingCaseId, phase, startedAt, kycGapSummary, null);
    }
}
