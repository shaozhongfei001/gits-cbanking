package com.gien.gits.api.productknowledge;

import java.time.Instant;
import java.util.List;

/**
 * LightRAG 派生检索响应（PC8 · CR-5 衍生）。
 *
 * <p>本响应是派生检索层产物，{@code evidenceClass} 恒为 {@code DERIVED_RETRIEVAL}；
 * 字段值不得取自检索（见 KERT 合同边界 5），仅承载召回的实体/关系/出处。</p>
 */
public record RetrievalResponse(String productId, String query, String mode,
                               List<RetrievalEntity> entities, List<RetrievalRelation> relations,
                               List<RetrievalCitation> citations, String evidenceClass,
                               String provenanceState, Boolean simulationOnly, String generatedAt,
                               String rawResponse) {

    public static RetrievalResponse of(String productId, String query, String mode,
                                      List<RetrievalEntity> entities, List<RetrievalRelation> relations,
                                      List<RetrievalCitation> citations, String evidenceClass,
                                      String provenanceState, Boolean simulationOnly) {
        return new RetrievalResponse(productId, query, mode, entities, relations, citations,
                evidenceClass, provenanceState, simulationOnly, Instant.now().toString(), null);
    }

    /** 包含原始响应文本的工厂方法（用于章节提取）。 */
    public static RetrievalResponse ofWithRaw(String productId, String query, String mode,
                                      List<RetrievalEntity> entities, List<RetrievalRelation> relations,
                                      List<RetrievalCitation> citations, String evidenceClass,
                                      String provenanceState, Boolean simulationOnly,
                                      String rawResponse) {
        return new RetrievalResponse(productId, query, mode, entities, relations, citations,
                evidenceClass, provenanceState, simulationOnly, Instant.now().toString(), rawResponse);
    }
}
