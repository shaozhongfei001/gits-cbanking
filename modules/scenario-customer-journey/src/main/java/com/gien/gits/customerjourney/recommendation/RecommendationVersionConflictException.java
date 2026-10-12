package com.gien.gits.customerjourney.recommendation;

/**
 * 产品推荐并发/过期提交异常：HumanGate 决策基于过期方案版本
 * （INV-06 违例：{@code proposalVersionId != run.currentVersionId}，或 If-Match/ETag 的
 * {@code expectedVersion} 不匹配）。语义等价 HTTP {@code 409 Conflict}。
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public class RecommendationVersionConflictException extends RuntimeException {

    public RecommendationVersionConflictException(String message) {
        super(message);
    }
}
