package com.gien.gits.knowledge.gkke.registry;

/**
 * GK-KE 领域异常基类（CR-02 §6.1）。
 *
 * <p>所有注册中心/地图领域异常携带稳定合同错误码 {@link GkErrorCode}，
 * 错误信息面向人可读且可变，错误码面向机器且跨版本稳定。</p>
 */
public class GkDomainException extends RuntimeException {

    private final GkErrorCode code;

    protected GkDomainException(GkErrorCode code, String message) {
        super(message);
        this.code = code;
    }

    protected GkDomainException(GkErrorCode code, String message, Throwable cause) {
        super(message, cause);
        this.code = code;
    }

    /** 稳定合同错误码。 */
    public GkErrorCode code() {
        return code;
    }

    /** 错误码合同字符串，如 {@code DEPENDENCY_UNRESOLVED}。 */
    public String errorCode() {
        return code.wireValue();
    }
}
