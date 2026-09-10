package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 知识地图节点（CTR-GKKE-002 / CR-02 §4.2）。
 *
 * @param nodeId        节点 ID
 * @param label         节点显示名
 * @param assetRef      资产版本引用
 * @param capabilityRef 能力版本引用
 * @param assetClass    资产大类
 * @param assetKind     资产类型
 * @param required      是否必需
 * @param minTokens     最少 token 预算
 * @param maxTokens     最大 token 预算
 * @param preconditions 前置条件
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record MapNode(
        String nodeId,
        String label,
        VersionRef assetRef,
        VersionRef capabilityRef,
        String assetClass,
        String assetKind,
        Boolean required,
        Integer minTokens,
        Integer maxTokens,
        List<String> preconditions) {
}
