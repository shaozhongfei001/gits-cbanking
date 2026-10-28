package com.gien.gits.knowledge.gkke.permission;

import java.util.List;
import java.util.Objects;

/**
 * GK-KE v1 运行时权限上下文（CR-02 §4.1 scope + C06 purpose，验收 T07）。
 *
 * <p>承载调用方身份与授权范围。目录/邻居/计数等出口的过滤结果按 {@link #cacheKey()} 缓存，
 * 缓存键由五要素构成，任一要素不同即得到不同键，从结构上杜绝跨上下文串缓存：
 * <ol>
 *   <li>{@code tenant}：租户；</li>
 *   <li>{@code principalScopeHash}：主体授权范围哈希（机构/客户范围的稳定摘要，非明文）；</li>
 *   <li>{@code purpose}：调用目的；</li>
 *   <li>{@code releaseId}：发布快照 ID；</li>
 *   <li>{@code catalogRevision}：目录修订号。</li>
 * </ol>
 *
 * @param tenantId           调用方租户 ID
 * @param orgIds             调用方被授权的机构 ID
 * @param customerIds        调用方被授权的客户 ID
 * @param purpose            调用目的（INTERPRETATION/RECOMMENDATION/RESEARCH 等）
 * @param principalScopeHash 主体授权范围哈希（org/customer 范围的稳定摘要，非明文）
 * @param releaseId          发布快照 ID
 * @param catalogRevision    目录修订号
 */
public record PermissionContext(
        String tenantId,
        List<String> orgIds,
        List<String> customerIds,
        String purpose,
        String principalScopeHash,
        String releaseId,
        int catalogRevision) {

    public PermissionContext {
        Objects.requireNonNull(tenantId, "tenantId must not be null");
        Objects.requireNonNull(purpose, "purpose must not be null");
        Objects.requireNonNull(principalScopeHash, "principalScopeHash must not be null");
        Objects.requireNonNull(releaseId, "releaseId must not be null");
        orgIds = orgIds == null ? List.of() : List.copyOf(orgIds);
        customerIds = customerIds == null ? List.of() : List.copyOf(customerIds);
    }

    /**
     * 兼容构造器：不绑定具体发布快照/目录修订的权限上下文（principalScopeHash 由授权范围
     * 确定性派生，releaseId/catalogRevision 取默认基线）。仅供不涉及缓存隔离的既有单资产
     * 决议测试使用；目录出口必须使用全参构造器。
     */
    public PermissionContext(String tenantId, List<String> orgIds, List<String> customerIds,
                             String purpose) {
        this(tenantId, orgIds, customerIds, purpose,
                scopeHash(tenantId, orgIds, customerIds), "UNBOUND", 0);
    }

    /**
     * 五要素缓存键：{@code tenant|principalScopeHash|purpose|releaseId|catalogRevision}。
     *
     * <p>不同租户/主体范围/目的/发布快照/目录修订之间键必然不同，过滤结果不会串缓存。
     */
    public String cacheKey() {
        return tenantId + "|" + principalScopeHash + "|" + purpose + "|"
                + releaseId + "|" + catalogRevision;
    }

    /** 由租户 + 授权机构/客户范围确定性派生主体范围哈希（稳定摘要，非明文范围）。 */
    public static String scopeHash(String tenantId, List<String> orgIds, List<String> customerIds) {
        String raw = String.valueOf(tenantId)
                + "|org=" + (orgIds == null ? "" : orgIds.stream().sorted().toList())
                + "|cus=" + (customerIds == null ? "" : customerIds.stream().sorted().toList());
        return Integer.toHexString(raw.hashCode());
    }
}
