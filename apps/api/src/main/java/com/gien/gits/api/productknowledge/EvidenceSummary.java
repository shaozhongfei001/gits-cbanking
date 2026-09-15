package com.gien.gits.api.productknowledge;

/**
 * 证据回链摘要（CTR-PK-INT-001）。
 */
public record EvidenceSummary(
        String evidenceId,
        String sourceId,
        String sourceVersionId,
        String authorityLevel,
        String locatorHint,
        String quoteExcerpt) {
}
