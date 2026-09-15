package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record SupplyChainGraphResult(
        String schemaVersion,
        String buildStatus,
        List<SupplyChainGraphNode> nodes,
        List<SupplyChainGraphEdge> edges,
        SupplyChainGraphInterpretation interpretation) {

    public SupplyChainGraphResult {
        nodes = nodes == null ? List.of() : List.copyOf(nodes);
        edges = edges == null ? List.of() : List.copyOf(edges);
    }
}
