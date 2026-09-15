package com.gien.gits.customerjourney.recommendation;

/**
 * 产品推荐业务运行（ProductRecommendationRun）的生命周期状态（GITS 权威）。
 *
 * <p>状态块：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO（WP4-1）。</p>
 *
 * <p>权威依据：</p>
 * <ul>
 *   <li>{@code specs/product-recommendation/product-recommendation-run.schema.json}（CTR-PR-RUN-001，12 值枚举）</li>
 *   <li>{@code docs/adr/ADR-PR-IDEMPOTENCY_CANDIDATE.md} §0.3（RecommendationRunStatus 12 值）</li>
 *   <li>{@code ~/dev/Leibniz-KERT/docs/integration/DKWS_GITS_STATE_MAPPING_CANDIDATE.md} §1.1 / §3.1</li>
 * </ul>
 *
 * <p>GITS 拥有业务状态权威；KERT 只维护 Skill 执行作业状态，不成为业务审批状态的第二权威源。</p>
 *
 * <p>终态：{@link #APPROVED} / {@link #MODIFIED} / {@link #REJECTED} / {@link #FAILED_CLOSED}；
 * 另 {@link #STALE_REQUIRES_RERUN} 对本运行无出边（旧版本保留、触发新 run）。</p>
 */
public enum ProductRecommendationRunStatus {
    /** 已请求，尚未提交 KERT。 */
    REQUESTED,
    /** 上下文装配中（请求并校验受控 ContextPackage + EvidenceBundle）。 */
    CONTEXT_ASSEMBLING,
    /** 第一段：硬过滤（Eligibility 四态硬规则）。 */
    HARD_FILTERING,
    /** 第二段：需求-能力匹配（分维度匹配/排序）。 */
    MATCHING,
    /** 方案就绪：已固化不可变方案版本，等待进入人工门禁。 */
    PROPOSAL_READY,
    /** 等待客户经理人工决定（HG-D01 / D01_PRODUCT_RECOMMEND）。 */
    AWAITING_HUMAN,
    /** 已批准（仅允许候选进入 G2 装配，不代表审批）。 */
    APPROVED,
    /** 已结构化修改后采纳（生成新方案版本 + 结构化差异）。 */
    MODIFIED,
    /** 已驳回（进入反馈/评测闭环）。 */
    REJECTED,
    /** 暂缓/事实不足（生成核实任务；可恢复继续，不当作成功）。 */
    HELD,
    /** 上游事实/产品/规则/权限/目标变化或超期导致过期，要求重跑（旧版本保留，不自动删除）。 */
    STALE_REQUIRES_RERUN,
    /** 失败关闭（终态，禁止本地生产推荐回退）。 */
    FAILED_CLOSED
}
