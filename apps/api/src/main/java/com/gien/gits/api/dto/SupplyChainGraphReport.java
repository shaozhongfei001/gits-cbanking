package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.List;

/**
 * SK-FRONT-002 供应链图谱报告（对齐 DKWS data.result + GITS 信封字段）。
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record SupplyChainGraphReport(
        String requestId,
        String customerId,
        String customerName,
        String generatedAt,
        String status,
        String reportUrl,
        SupplyChainGraphResult result) {
}
