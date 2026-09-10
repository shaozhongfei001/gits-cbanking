package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * GK-KE v1 知识地图有向边（CTR-GKKE-002 / CR-02 §4.2）。
 *
 * @param from 源节点 ID
 * @param to   目标节点 ID
 * @param type 边类型（DEPENDS_ON/ROUTES_TO）
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record MapEdge(String from, String to, String type) {
}
