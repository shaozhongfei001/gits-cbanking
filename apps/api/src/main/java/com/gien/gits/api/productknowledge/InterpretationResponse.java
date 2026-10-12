package com.gien.gits.api.productknowledge;

import java.util.List;

/**
 * 产品解读响应（CTR-PK-INT-001）。
 *
 * <p>{@code fields} 为空数组表示无可呈现字段，绝不返回 {@code null}；
 * {@code displayValue} 在 UNKNOWN / CONFLICT / STALE 时恒为 {@code null}，
 * 前端须显式标注状态而非留白。</p>
 */
public record InterpretationResponse(
        String productId,
        String releaseId,
        String bundleHash,
        String view,
        String purpose,
        boolean isStale,
        List<InterpretedField> fields,
        String generatedAt) {
}
