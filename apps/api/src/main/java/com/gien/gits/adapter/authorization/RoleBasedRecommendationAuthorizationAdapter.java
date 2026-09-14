package com.gien.gits.adapter.authorization;

import com.gien.gits.customerjourney.recommendation.port.RecommendationAuthorizationPort;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Set;

/**
 * 基于角色白名单的产品推荐门禁鉴权适配器（F-4）。
 *
 * <p>替换此前 {@code ProductRecommendationConfig} 中「任意非空 actorId 即放行」的
 * CANDIDATE 占位 lambda。占位实现使任何调用方只要带上一个非空字符串就能对
 * HG-D01 作决定，构成越权风险。</p>
 *
 * <p>判定顺序（任一不满足即拒绝）：</p>
 * <ol>
 *   <li>actorId 非空 —— 无法归因的操作一律拒绝，审计要求；</li>
 *   <li>gateId 非空 —— 不允许无目标的决定；</li>
 *   <li>actorRole 非空且在允许角色白名单内 —— fail-closed：角色缺失即拒绝，
 *       不再像占位实现那样忽略角色。</li>
 * </ol>
 *
 * <p><b>fail-closed 设计</b>：白名单为空时拒绝一切请求，而非放行一切。这与
 * INV-07（KERT 不可达时禁止本地回退）保持同一取向——不确定时选择拒绝。</p>
 *
 * <p><b>本适配器的边界</b>：仅做「角色是否被允许对该类门禁作决定」的粗粒度判定。
 * 尚未实现的细粒度判定：</p>
 * <ul>
 *   <li>RM 归属校验（该 actorId 是否为该客户的归属客户经理）—— 需 HumanGate 或 Run
 *       携带 rmId，当前领域模型 {@code HumanGate} 无此字段，需合同变更后补；</li>
 *   <li>与企业 IAM / SSO 的对接 —— 需 Owner 指定身份源。</li>
 * </ul>
 * 上述两项已记入 FAILURES.md，作为 F-4 的剩余部分。本次交付把「默认放行」
 * 改为「白名单准入」，消除无条件越权。
 *
 * <p>状态 CANDIDATE / FROZEN=NO。</p>
 */
public class RoleBasedRecommendationAuthorizationAdapter implements RecommendationAuthorizationPort {

    private static final Logger log =
            LoggerFactory.getLogger(RoleBasedRecommendationAuthorizationAdapter.class);

    private final Set<String> allowedRoles;

    /**
     * @param allowedRoles 允许对产品推荐门禁作决定的角色集合。传入空集合时拒绝一切请求（fail-closed）。
     */
    public RoleBasedRecommendationAuthorizationAdapter(Set<String> allowedRoles) {
        this.allowedRoles = allowedRoles == null ? Set.of() : Set.copyOf(allowedRoles);
        if (this.allowedRoles.isEmpty()) {
            log.warn("Recommendation authorization configured with empty role whitelist; all decisions will be denied (fail-closed)");
        }
    }

    @Override
    public boolean isAuthorized(String actorId, String actorRole, String gateId) {
        if (isBlank(actorId)) {
            log.warn("Authorization denied: blank actorId, gateId={}", gateId);
            return false;
        }
        if (isBlank(gateId)) {
            log.warn("Authorization denied: blank gateId, actorId={}", actorId);
            return false;
        }
        if (isBlank(actorRole)) {
            log.warn("Authorization denied: blank actorRole (fail-closed), actorId={}, gateId={}",
                    actorId, gateId);
            return false;
        }
        String normalized = actorRole.trim().toUpperCase();
        boolean allowed = allowedRoles.contains(normalized);
        if (!allowed) {
            log.warn("Authorization denied: role not in whitelist, actorId={}, actorRole={}, gateId={}",
                    actorId, normalized, gateId);
        }
        return allowed;
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }
}
