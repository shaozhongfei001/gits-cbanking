package com.gien.gits.knowledge.gkke.permission;

import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import com.gien.gits.knowledge.gkke.registry.AssetRegistryPort;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * GK-KE v1 注册中心权限过滤器（CR-02 §4.1/§7，验收 T07）。
 *
 * <p>按运行时 {@link PermissionContext} 对候选资产做 scope 匹配，只放行已发布、
 * 租户/机构/客户/用途全部匹配的资产，并投影为不含内部存储位置的 {@link AssetView}。
 * 拒绝原因通过 {@link PermissionDecision} 可追溯（供 C06 权限决议引用）。
 */
public final class RegistryPermissionFilter {

    private static final Logger LOG = LoggerFactory.getLogger(RegistryPermissionFilter.class);
    private static final String LIFECYCLE_PUBLISHED = "PUBLISHED";

    private final AssetRegistryPort registry;

    public RegistryPermissionFilter(AssetRegistryPort registry) {
        this.registry = Objects.requireNonNull(registry, "registry must not be null");
    }

    /** 对候选资产列表做权限过滤，返回允许访问的安全投影（保持候选顺序）。 */
    public List<AssetView> filter(List<AssetVersionRecord> candidates, PermissionContext context) {
        Objects.requireNonNull(context, "context must not be null");
        return candidates.stream()
                .filter(asset -> decide(asset, context).allowed())
                .map(RegistryPermissionFilter::project)
                .toList();
    }

    /** 解析一组版本引用并过滤；引用缺失视为拒绝（不抛异常，跳过并记录）。 */
    public List<AssetView> filterRefs(List<VersionRef> refs, PermissionContext context) {
        return refs.stream()
                .map(ref -> registry.resolve(ref.id(), ref.version()).orElse(null))
                .filter(Objects::nonNull)
                .filter(asset -> decide(asset, context).allowed())
                .map(RegistryPermissionFilter::project)
                .toList();
    }

    /** 单资产访问决议：生命周期 → 租户 → 机构 → 客户 → 用途，短路返回首个拒绝原因。 */
    public PermissionDecision decide(AssetVersionRecord asset, PermissionContext context) {
        if (!LIFECYCLE_PUBLISHED.equals(asset.lifecycle())) {
            return deny(asset, PermissionDecision.NOT_PUBLISHED);
        }
        Scope scope = asset.scope();
        if (scope == null || !Objects.equals(scope.tenantId(), context.tenantId())) {
            return deny(asset, PermissionDecision.TENANT_MISMATCH);
        }
        if (!matchesRestriction(scope.orgIds(), context.orgIds())) {
            return deny(asset, PermissionDecision.ORG_NOT_AUTHORIZED);
        }
        if (!matchesRestriction(scope.customerIds(), context.customerIds())) {
            return deny(asset, PermissionDecision.CUSTOMER_NOT_AUTHORIZED);
        }
        if (asset.purposeFlags() == null || !asset.purposeFlags().contains(context.purpose())) {
            return deny(asset, PermissionDecision.PURPOSE_NOT_DECLARED);
        }
        return PermissionDecision.allow();
    }

    /**
     * 限制集合匹配：资产未声明限制（空）表示不约束；否则调用方授权集合必须与之有交集。
     */
    private boolean matchesRestriction(List<String> required, List<String> granted) {
        if (required == null || required.isEmpty()) {
            return true;
        }
        return granted != null && granted.stream().anyMatch(Set.copyOf(required)::contains);
    }

    private PermissionDecision deny(AssetVersionRecord asset, String reason) {
        LOG.info("Asset access denied: assetId={}, version={}, reason={}",
                asset.assetId(), asset.version(), reason);
        return PermissionDecision.deny(reason);
    }

    private static AssetView project(AssetVersionRecord asset) {
        return new AssetView(asset.assetId(), asset.version(), asset.assetClass(), asset.kind(),
                asset.title(), asset.lifecycle(), asset.purposeFlags(), asset.coreVersion());
    }
}
