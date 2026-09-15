package com.gien.gits.api.productknowledge;

import java.util.List;

/**
 * 解读字段（CTR-PK-INT-001）。
 */
public record InterpretedField(
        String fieldPath,
        String displayValue,
        String knowledgeState,
        List<EvidenceSummary> evidenceSummaries,
        String conflictId) {
}
