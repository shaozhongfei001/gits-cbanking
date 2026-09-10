package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * GK-KE v1 通用 ID/版本引用（CR-02 §4.2）。
 *
 * @param id      资产/能力/查询 ID
 * @param version 语义版本
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record VersionRef(String id, String version) {
}
