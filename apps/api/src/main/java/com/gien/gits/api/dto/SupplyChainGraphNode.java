package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record SupplyChainGraphNode(
        String id,
        String name,
        String layer,
        String type,
        String industry,
        Double annualAmount,
        Double share,
        String trend,
        String dataSource,
        String verifyStatus) {
}
