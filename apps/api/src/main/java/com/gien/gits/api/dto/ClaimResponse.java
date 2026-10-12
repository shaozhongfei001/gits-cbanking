package com.gien.gits.api.dto;

import java.time.Instant;

/**
 * Claim 合同响应 DTO（OpenAPI operationId=listClaims / getClaim）。
 *
 * <p>领域 {@code com.gien.gits.ontology.Claim} 为 statement 型（caseId + statement），
 * 而 OpenAPI {@code Claim} 为 content 型（customerId + content）。
 * 本 DTO 同时携带两种语义字段，前端 {@code Claim} 接口按需消费。</p>
 *
 * @param claimId               主张唯一标识
 * @param customerId            关联客户（经 journey.caseId 解析）
 * @param caseId                运营案例标识（领域语义）
 * @param claimType             主张类型（领域枚举名）
 * @param status                主张状态（领域枚举名）
 * @param content               主张内容（映射自领域 statement）
 * @param statement             原始陈述（领域语义，与 content 同值）
 * @param evidenceRef           证据引用（领域暂无，预留）
 * @param sourceInteractionId   来源交互（领域暂无，预留）
 * @param recordedAt            记录时间
 * @param createdAt             创建时间
 * @param updatedAt             更新时间
 */
public record ClaimResponse(
        String claimId,
        String customerId,
        String caseId,
        String claimType,
        String status,
        String content,
        String statement,
        String evidenceRef,
        String sourceInteractionId,
        Instant recordedAt,
        Instant createdAt,
        Instant updatedAt) {
}
