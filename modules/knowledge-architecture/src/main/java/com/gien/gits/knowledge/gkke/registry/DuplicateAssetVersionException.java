package com.gien.gits.knowledge.gkke.registry;

/**
 * 同一资产 ID+版本重复登记。
 *
 * <p>Q3：映射稳定错误码 {@link GkErrorCode#DUPLICATE_ASSET_VERSION}（CR-02 §6.1）。</p>
 */
public class DuplicateAssetVersionException extends GkDomainException {

    public DuplicateAssetVersionException(String assetId, String version) {
        super(GkErrorCode.DUPLICATE_ASSET_VERSION,
                "asset version already registered: assetId=" + assetId + ", version=" + version);
    }
}
