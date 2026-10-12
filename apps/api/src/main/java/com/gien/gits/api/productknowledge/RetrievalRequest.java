package com.gien.gits.api.productknowledge;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * LightRAG 派生检索请求（PC8 · CR-5 衍生）。
 *
 * <p>只承载查询意图，不携带任何 GITS 侧权威结论；{@code service} 由 GITS 用
 * {@code productId} 注入，使检索限定到该产品的 KERT workspace。</p>
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record RetrievalRequest(String query, String mode, Integer limit) {

    /** 解析检索模式，缺省 hybrid。 */
    public String resolveMode() {
        return (mode == null || mode.isBlank()) ? "hybrid" : mode;
    }

    /** 解析返回条数上限，缺省 10，夹在 [1,50]。 */
    public int resolveLimit() {
        int v = (limit == null || limit < 1) ? 10 : limit;
        return Math.min(v, 50);
    }
}
