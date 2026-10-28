package com.gien.gits.knowledge.gkke.registry;

import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.LinkedHashSet;
import java.util.Objects;
import java.util.Set;

/**
 * 能力注册表（CR-02 §4.1，验收 T06）。
 *
 * <p>L1 最小实现：登记已注册能力（ID+版本），激活前校验能力引用是否已登记；
 * 未登记抛 {@link CapabilityNotRegisteredException}（{@code CAPABILITY_NOT_REGISTERED}）。
 * 能力的资产化元数据在后续 Loop 接入资产目录后补全。</p>
 */
public final class CapabilityRegistry {

    private final Set<VersionRef> registered = new LinkedHashSet<>();

    /** 登记一个已发布能力版本。 */
    public void register(String capabilityId, String version) {
        Objects.requireNonNull(capabilityId, "capabilityId");
        Objects.requireNonNull(version, "version");
        registered.add(new VersionRef(capabilityId, version));
    }

    /** 能力已登记返回 true。 */
    public boolean isRegistered(String capabilityId, String version) {
        return registered.contains(new VersionRef(capabilityId, version));
    }

    /**
     * 要求能力已登记，否则抛 {@link CapabilityNotRegisteredException}。
     *
     * @param ref 能力引用
     */
    public void requireRegistered(VersionRef ref) {
        Objects.requireNonNull(ref, "capability ref");
        if (!registered.contains(ref)) {
            throw new CapabilityNotRegisteredException(ref.id(), ref.version());
        }
    }
}
