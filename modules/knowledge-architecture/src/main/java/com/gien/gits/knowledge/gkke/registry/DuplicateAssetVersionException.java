package com.gien.gits.knowledge.gkke.registry;

/**
 * 同一资产 ID + 版本重复登记（CR-02 §4.1：版本不可变）。
 */
public class DuplicateAssetVersionException extends RuntimeException {

    public DuplicateAssetVersionException(String assetId, String version) {
        super("duplicate asset version: assetId=" + assetId + ", version=" + version);
    }
}
