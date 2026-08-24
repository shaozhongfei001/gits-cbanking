package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record SupplyChainGraphExecuteRequest(
        String customerId,
        String requestId) {
}
