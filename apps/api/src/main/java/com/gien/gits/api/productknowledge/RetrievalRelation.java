package com.gien.gits.api.productknowledge;

/**
 * 检索召回的关系（防御性映射 LightRAG 原始字段）。
 */
public record RetrievalRelation(String source, String target, String type) {
}
