package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 知识地图版本（CTR-GKKE-002 / CR-02 §4.2）。
 *
 * @param mapId           地图 ID
 * @param version         语义版本
 * @param title           标题
 * @param status          状态（DRAFT/PUBLISHED/DEPRECATED）
 * @param entryNodeIds    入口节点 ID 列表
 * @param nodes           节点列表
 * @param edges           有向边列表
 * @param maxInitialTokens 初始 token 预算上限
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record KnowledgeMapRecord(
        String mapId,
        String version,
        String title,
        String status,
        List<String> entryNodeIds,
        List<MapNode> nodes,
        List<MapEdge> edges,
        Integer maxInitialTokens) {
}
