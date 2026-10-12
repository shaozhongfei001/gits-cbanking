package com.gien.gits.engagement.port;

/**
 * SP-20 服务建议书端口（契约 v1.4 §2）。
 *
 * <p>职责边界：生成动作委托 DKWS SP-20（经 {@link SkillExecutionPort}，async 202+轮询）；
 * 闸门推进（G1/G2/G3 人工审批）与对客版放行决策在 GITS，见 {@code GateStateMachine}。</p>
 *
 * <p>实现约定：失败必须抛异常（不静默降级）；未知字段忽略（契约 §5）；BLOCKING 规则违规
 * 时 {@link ServiceProposal#status()} 为 PARTIAL 且不入对客版。</p>
 */
public interface ServiceProposalPort {

    /**
     * 生成服务建议书。
     *
     * @param command SP-20 生成命令（含 ContextPackage）
     * @return 强类型服务建议书
     * @throws SkillExecutionException 生成失败（网络/超时/job 失败）
     */
    ServiceProposal generate(ServiceProposalCommand command);
}
