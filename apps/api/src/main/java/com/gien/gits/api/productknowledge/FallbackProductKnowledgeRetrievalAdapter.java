package com.gien.gits.api.productknowledge;

/**
 * 检索端口 fail-closed 回退：{@code dsh.base-url} 未配置时，绝不本地补数，直接受控失败。
 */
public class FallbackProductKnowledgeRetrievalAdapter implements ProductKnowledgeRetrievalPort {

    @Override
    public RetrievalResponse retrieve(String productId, RetrievalRequest request) {
        throw new KnowledgeSourceUnavailableException(
                "dsh.base-url 未配置，LightRAG 检索端点 fail-closed（不本地补数）");
    }
}
