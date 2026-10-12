package com.gien.gits.customerjourney.recommendation.port;

/**
 * 产品推荐 HumanGate（HG-D01）操作者权限判定端口。
 *
 * <p>应用服务在创建 HG-D01 决定前据此做"权限"前置校验；返回 {@code false} 时
 * 应用服务应拒绝（语义等价 403），不得落决定。</p>
 *
 * <p>FO-02 唯一归属合并：本端口随领域模型一并归属
 * {@code modules/scenario-customer-journey}（原 operational-ontology 版本已删除）。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
@FunctionalInterface
public interface RecommendationAuthorizationPort {

    /**
     * @param actorId   操作者 ID
     * @param actorRole 操作者角色（可空）
     * @param gateId    门禁 ID（HG-D01 的 gateId）
     * @return true 表示允许对给定 gate 作决定
     */
    boolean isAuthorized(String actorId, String actorRole, String gateId);
}
