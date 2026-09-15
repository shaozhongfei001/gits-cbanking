package com.gien.gits.engagement.port;

/**
 * SKILL 执行失败异常 — 由 {@link SkillExecutionPort} 实现抛出，调用方决定 fallback。
 *
 * <p>fail-closed：任何网络 / 契约 / 策略终止错误都应映射为此异常（或返回
 * {@link SkillExecutionStatus#SKILL_ERROR}），由调用方回落本地 {@link LlmClient}。</p>
 */
public class SkillExecutionException extends RuntimeException {

    private final SkillExecutionStatus status;

    public SkillExecutionException(String message) {
        this(SkillExecutionStatus.SKILL_ERROR, message, null);
    }

    public SkillExecutionException(SkillExecutionStatus status, String message) {
        this(status, message, null);
    }

    public SkillExecutionException(SkillExecutionStatus status, String message, Throwable cause) {
        super(message, cause);
        this.status = status == null ? SkillExecutionStatus.SKILL_ERROR : status;
    }

    /** 便捷构造：消息 + 根因，状态默认 SKILL_ERROR。 */
    public SkillExecutionException(String message, Throwable cause) {
        super(message, cause);
        this.status = SkillExecutionStatus.SKILL_ERROR;
    }

    /** 触发该异常的执行状态（默认 SKILL_ERROR）。 */
    public SkillExecutionStatus status() {
        return status;
    }
}