package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record SupplyChainGraphEdge(
        String source,
        String target,
        String relation,
        String direction,
        Double annualAmount,
        Double share,
        String settlement) {
}
