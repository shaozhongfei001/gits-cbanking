package com.gien.gits.engagement.port;

/**
 * SKILL 执行结果状态（对齐跨端联调契约 dsh 侧 status 取值）。
 */
public enum SkillExecutionStatus {
    /** 执行成功，data 携带结构化结果。 */
    OK,
    /** Skill 执行出错（模型故障 / 契约错误 / 参数非法）。 */
    SKILL_ERROR,
    /** 策略终止：请求未携带新证据，拒绝伪生成新产出。 */
    EXIT_POLICY_NO_NEW_EVIDENCE;

    /** 由 dsh 返回的 snake_case 字符串解析（ok/skill_error/exit_policy_no_new_evidence）。 */
    public static SkillExecutionStatus fromWire(String value) {
        if (value == null) {
            return SKILL_ERROR;
        }
        return switch (value.strip().toLowerCase()) {
            case "ok" -> OK;
            case "exit_policy_no_new_evidence" -> EXIT_POLICY_NO_NEW_EVIDENCE;
            default -> SKILL_ERROR;
        };
    }
}