package com.gien.gits.knowledge.gkke.registry;

/**
 * 引用的能力未在能力注册表登记（验收 T06）。
 *
 * <p>Q3：映射稳定错误码 {@link GkErrorCode#CAPABILITY_NOT_REGISTERED}（CR-02 §6.1）。
 * 与 {@link AssetNotFoundException} 区分：能力（Capability）是可执行技能/服务，
 * 未登记时激活计划不得放行。</p>
 */
public class CapabilityNotRegisteredException extends GkDomainException {

    public CapabilityNotRegisteredException(String capabilityId, String version) {
        super(GkErrorCode.CAPABILITY_NOT_REGISTERED,
                "capability not registered: capabilityId=" + capabilityId
                        + ", version=" + version);
    }
}
