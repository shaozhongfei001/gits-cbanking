package com.gien.gits.api.dto;

import com.gien.gits.customerjourney.recommendation.RecommendationDecision;

import java.util.List;

/**
 * HG-D01 结构化人工决定请求 DTO。
 *
 * <p>字段对齐 {@code recommendation-human-decision.schema.json}（CTR-PR-DEC-001）：
 * {@code gateId} 来自 URL 路径；{@code decidedAt} 由服务端时间权威生成（不接收客户端时间）。
 * {@code proposalVersionId} 必填（INV-06）；{@code expectedVersion} 承载 If-Match/ETag 并发校验，
 * 过期提交由应用服务抛 {@code RecommendationVersionConflictException}（语义等价 409）。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 *
 * @param schemaVersion     契约版本（可选，如提供必须为 "1.0.0"）
 * @param runId             产品推荐运行 ID（必填）
 * @param proposalVersionId 被决定的方案版本 ID（必填，INV-06）
 * @param expectedVersion   If-Match/ETag 期望版本（可选）
 * @param decision          决定值（APPROVE / MODIFY / REJECT / HOLD）
 * @param modifications     结构化修改列表（仅 decision=MODIFY 必填）
 * @param reason            决定理由（REJECT / HOLD 必填）
 * @param actorId           操作者 ID（必填）
 * @param actorRole         操作者角色（可选）
 */
public record RecommendationHumanDecisionRequest(
        String schemaVersion,
        String runId,
        String proposalVersionId,
        String expectedVersion,
        RecommendationDecision decision,
        List<StructuredModification> modifications,
        String reason,
        String actorId,
        String actorRole) {
}
