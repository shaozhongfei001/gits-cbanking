package com.gien.gits.knowledge.gkke.registry;

/**
 * 请求的资产版本在注册中心不存在（CR-02 §6：404 语义）。
 */
public class AssetNotFoundException extends RuntimeException {

    private final String assetId;
    private final String version;

    public AssetNotFoundException(String assetId, String version) {
        super("asset not found: assetId=" + assetId + ", version=" + version);
        this.assetId = assetId;
        this.version = version;
    }

    public String assetId() {
        return assetId;
    }

    public String version() {
        return version;
    }
}
