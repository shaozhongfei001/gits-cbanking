package com.gien.gits.engagement.port;

/**
 * KERT 返回**契约不符**：执行成功但响应缺少必需节点（如 {@code data.result}）或无法映射为强类型结果。
 *
 * <p><b>为什么单独一个类型</b>（PI · P1）：它与「KERT 不可达」是**不同**的失败面，处置也不同 ——</p>
 * <ul>
 *   <li>调用方必须能区分 {@code 503 KERT_UNAVAILABLE}（暂时不可用，可重试）与
 *       {@code 502 KERT_CONTRACT_MISMATCH}（对方契约变了，重试无用）；</li>
 *   <li>本异常的存在，正是为了**消灭「静默降级为空结果 + HTTP 200」**这种把失败伪装成成功的做法
 *       （违反 {@link ServiceProposalPort} 的「失败必须抛异常」契约）。</li>
 * </ul>
 */
public class KertContractMismatchException extends SkillExecutionException {

    public KertContractMismatchException(String message) {
        super(SkillExecutionStatus.SKILL_ERROR, message);
    }

    public KertContractMismatchException(String message, Throwable cause) {
        super(SkillExecutionStatus.SKILL_ERROR, message, cause);
    }
}
