package com.gien.gits.api.productknowledge;

/**
 * 产品知识 LightRAG 派生检索端口（PC8 · CR-5 衍生）。
 *
 * <p>GITS 不得拥有第二套检索系统：本端口只把查询转发给 KERT 的
 * {@code /v1/retrieval/query}（派生检索层），不本地生成或缓存结论。
 * KERT / LightRAG 不可达或响应异常时实现必须抛出
 * {@link KnowledgeSourceUnavailableException} / {@link RetrievalUpstreamException}，
 * 由上层转为 503 / 502 / 504 受控失败（fail-closed）。</p>
 */
public interface ProductKnowledgeRetrievalPort {

    /**
     * 对指定产品做 LightRAG 派生检索。
     *
     * @param productId 产品 ID（PROD-XX-NNN），注入为 KERT 检索的 service 维度
     * @param request   检索请求（query / mode / limit）
     * @return 召回结果
     */
    RetrievalResponse retrieve(String productId, RetrievalRequest request);
}
