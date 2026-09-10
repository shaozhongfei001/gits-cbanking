package com.gien.gits.knowledge.gkke.registry;

/**
 * 资产版本不存在（引用断裂）。
 *
 * <p>Q3：映射稳定错误码 {@link GkErrorCode#DEPENDENCY_UNRESOLVED}（CR-02 §6.1）。
 * 引用的资产 ID+版本在注册中心不存在，属依赖引用断裂。</p>
 */
public class AssetNotFoundException extends GkDomainException {

    public AssetNotFoundException(String assetId, String version) {
        super(GkErrorCode.DEPENDENCY_UNRESOLVED,
                "asset not found: assetId=" + assetId + ", version=" + version);
    }
}
