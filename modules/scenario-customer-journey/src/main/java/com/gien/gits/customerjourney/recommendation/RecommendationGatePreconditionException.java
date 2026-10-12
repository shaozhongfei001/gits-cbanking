package com.gien.gits.customerjourney.recommendation;

/**
 * 产品推荐 HumanGate 前置校验失败异常（证据/权限等非并发类前置条件）。
 *
 * <p>常用 {@code code}：{@code PERMISSION_DENIED}（语义等价 403）、
 * {@code EVIDENCE_INCOMPLETE}、{@code NO_CURRENT_VERSION}（语义等价 422）。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public class RecommendationGatePreconditionException extends RuntimeException {

    private final String code;

    public RecommendationGatePreconditionException(String code, String message) {
        super(message);
        this.code = code;
    }

    /** 前置条件失败的业务码。 */
    public String code() {
        return code;
    }
}
