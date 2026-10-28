package com.gien.gits.knowledge.gkke.registry;

/**
 * 资产存在但当前不可用（未发布/已撤销）。
 *
 * <p>Q3：映射稳定错误码 {@link GkErrorCode#ASSET_NOT_AVAILABLE}（CR-02 §6.1）。
 * 与 {@link AssetNotFoundException}（引用断裂）区分：资产可解析但生命周期不满足发布要求。</p>
 */
public class AssetNotAvailableException extends GkDomainException {

    public AssetNotAvailableException(String assetId, String version) {
        super(GkErrorCode.ASSET_NOT_AVAILABLE,
                "asset not available: assetId=" + assetId + ", version=" + version);
    }
}
