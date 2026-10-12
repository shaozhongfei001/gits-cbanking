package com.gien.gits.engagement.port;

/**
 * SKILL 运行平台执行端口（架构演进：客户经理持续经营 Skill）。
 *
 * <p>将"外联脚本 / 会面脚本 / R1 拜访报告"的生成从本地 {@link LlmClient} 迁移为
 * 调用 deepseek-harness（dsh）平台上的三个可激活 Skill。本端口是 gits 侧的调用方抽象：</p>
 *
 * <ul>
 *   <li>实现一：{@code DshHttpSkillExecutionAdapter} —— 走 HTTP 调 dsh {@code POST /api/skill/execute}；</li>
 *   <li>实现二：{@code FallbackSkillExecutionAdapter} —— dsh 不可达时回退本地 {@link LlmClient}（fail-closed）。</li>
 * </ul>
 *
 * <p>调用失败不得吞异常；由调用方决定 fallback 策略。</p>
 *
 * @see SkillExecutionCommand
 * @see SkillExecutionResult
 */
public interface SkillExecutionPort {

    /**
     * 激活并执行一次 SKILL。
     *
     * @param command 执行命令（skillId + requestId + 请求上下文）
     * @return 结构化执行结果（含 data / 装配轨迹 / 模型调用元数据）
     * @throws SkillExecutionException 执行失败（网络、契约、策略终止等）
     */
    SkillExecutionResult execute(SkillExecutionCommand command);
}