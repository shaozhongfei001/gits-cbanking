package com.gien.gits.api.controller;

import com.gien.gits.api.dto.UpdateStatusRequest;
import com.gien.gits.api.service.CommitmentService;
import com.gien.gits.ontology.Commitment;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

/**
 * 承诺控制器 — 承诺跟踪与状态管理
 */
@RestController
@RequestMapping("/api/v1/commitments")
public class CommitmentController {

    private final CommitmentService commitmentService;

    public CommitmentController(CommitmentService commitmentService) {
        this.commitmentService = Objects.requireNonNull(commitmentService);
    }

    @GetMapping("/{commitmentId}")
    public ResponseEntity<Commitment> getById(@PathVariable String commitmentId) {
        return commitmentService.findById(commitmentId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping
    public ResponseEntity<List<Commitment>> list(@RequestParam(required = false) String interactionId,
                                                  @RequestParam(required = false) String customerId,
                                                  @RequestParam(required = false) String status) {
        if (interactionId != null) {
            return ResponseEntity.ok(commitmentService.findByInteractionId(interactionId));
        }
        if (customerId != null) {
            return ResponseEntity.ok(commitmentService.findByCustomerId(customerId));
        }
        if (status != null) {
            return ResponseEntity.ok(commitmentService.findByStatus(status));
        }
        return ResponseEntity.ok(commitmentService.findAll());
    }

    @GetMapping("/overdue")
    public ResponseEntity<List<Commitment>> getOverdue() {
        return ResponseEntity.ok(commitmentService.findOverdue());
    }

    @PostMapping
    public ResponseEntity<Commitment> create(@RequestBody Commitment commitment) {
        return ResponseEntity.status(HttpStatus.CREATED).body(commitmentService.create(commitment));
    }

    @PutMapping("/{commitmentId}/status")
    public ResponseEntity<Commitment> updateStatus(@PathVariable String commitmentId,
                                                    @RequestBody UpdateStatusRequest request) {
        return commitmentService.updateStatus(commitmentId, request.status(), null)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
