package com.gien.gits.api.controller;

import com.gien.gits.api.dto.UpdateStageRequest;
import com.gien.gits.api.service.OpportunityService;
import com.gien.gits.ontology.domain.Opportunity;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

/**
 * 商机控制器 — 销售机会管理
 */
@RestController
@RequestMapping("/api/v1/opportunities")
public class OpportunityController {

    private final OpportunityService opportunityService;

    public OpportunityController(OpportunityService opportunityService) {
        this.opportunityService = Objects.requireNonNull(opportunityService);
    }

    @GetMapping("/{opportunityId}")
    public ResponseEntity<Opportunity> getById(@PathVariable String opportunityId) {
        return opportunityService.findById(opportunityId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping(params = "customerId")
    public ResponseEntity<List<Opportunity>> getByCustomerId(@RequestParam String customerId) {
        return ResponseEntity.ok(opportunityService.findByCustomerId(customerId));
    }

    @GetMapping(params = "status")
    public ResponseEntity<List<Opportunity>> getByStatus(@RequestParam String status) {
        return ResponseEntity.ok(opportunityService.findByStatus(status));
    }

    @GetMapping(params = "opportunityType")
    public ResponseEntity<List<Opportunity>> getByType(@RequestParam String opportunityType) {
        return ResponseEntity.ok(opportunityService.findByOpportunityType(opportunityType));
    }

    @GetMapping(params = "assignedTo")
    public ResponseEntity<List<Opportunity>> getByAssignedTo(@RequestParam String assignedTo) {
        return ResponseEntity.ok(opportunityService.findByAssignedTo(assignedTo));
    }

    @GetMapping("/{customerId}/active")
    public ResponseEntity<List<Opportunity>> getActiveByCustomerId(@PathVariable String customerId) {
        return ResponseEntity.ok(opportunityService.findActiveByCustomerId(customerId));
    }

    @GetMapping
    public ResponseEntity<List<Opportunity>> listAll() {
        return ResponseEntity.ok(opportunityService.findAll());
    }

    @PostMapping
    public ResponseEntity<Opportunity> create(@RequestBody Opportunity opportunity) {
        return ResponseEntity.status(HttpStatus.CREATED).body(opportunityService.create(opportunity));
    }

    @PutMapping("/{opportunityId}/stage")
    public ResponseEntity<Opportunity> updateStage(@PathVariable String opportunityId, @RequestBody UpdateStageRequest request) {
        return opportunityService.updateStatus(opportunityId, request.stage())
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
