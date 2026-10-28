package com.gien.gits.knowledge.gkke.registry;

/**
 * 依赖闭包存在环。
 *
 * <p>Q3：映射稳定错误码 {@link GkErrorCode#DEPENDENCY_CYCLE}（CR-02 §6.1）。</p>
 */
public class DependencyCycleException extends GkDomainException {

    public DependencyCycleException(String message) {
        super(GkErrorCode.DEPENDENCY_CYCLE, message);
    }

    public DependencyCycleException(String assetId, String version) {
        super(GkErrorCode.DEPENDENCY_CYCLE,
                "dependency cycle detected at: assetId=" + assetId + ", version=" + version);
    }
}
