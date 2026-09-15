package com.gien.gits.api.controller;

import com.gien.gits.api.dto.SupplyChainGraphExecuteRequest;
import com.gien.gits.api.dto.SupplyChainGraphReport;
import com.gien.gits.api.service.SupplyChainGraphService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Objects;

@RestController
@RequestMapping("/api/v1/engagement")
public class SupplyChainGraphController {

    private final SupplyChainGraphService supplyChainGraphService;

    public SupplyChainGraphController(SupplyChainGraphService supplyChainGraphService) {
        this.supplyChainGraphService = Objects.requireNonNull(supplyChainGraphService);
    }

    @PostMapping("/supply-chain-graph")
    public ResponseEntity<SupplyChainGraphReport> executeSupplyChainGraph(
            @RequestBody SupplyChainGraphExecuteRequest request) {
        return ResponseEntity.ok(supplyChainGraphService.execute(request));
    }

    @GetMapping("/supply-chain-graph/reports/{requestId}")
    public ResponseEntity<SupplyChainGraphReport> getSupplyChainGraphReport(
            @PathVariable String requestId) {
        return ResponseEntity.ok(supplyChainGraphService.getReport(requestId));
    }
}
