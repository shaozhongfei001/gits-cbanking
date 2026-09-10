package com.gien.gits.knowledge.gkke.registry;

/**
 * 资产依赖图存在环（CR-02 §4.1：dependencyRefs 必须可闭包，禁止循环依赖）。
 */
public class DependencyCycleException extends RuntimeException {

    public DependencyCycleException(String assetId, String version) {
        super("dependency cycle detected at: assetId=" + assetId + ", version=" + version);
    }
}
