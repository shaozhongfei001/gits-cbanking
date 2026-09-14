package com.gien.gits.api.controller;

import com.gien.gits.api.dto.UpdateStatusRequest;
import com.gien.gits.api.service.RecordingConsentService;
import com.gien.gits.action.domain.RecordingConsent;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

/**
 * 录音录像同意控制器 — 交互记录合规授权管理
 */
@RestController
@RequestMapping("/api/v1/recording-consents")
public class RecordingConsentController {

    private final RecordingConsentService consentService;

    public RecordingConsentController(RecordingConsentService consentService) {
        this.consentService = Objects.requireNonNull(consentService);
    }

    @GetMapping("/{consentId}")
    public ResponseEntity<RecordingConsent> getById(@PathVariable String consentId) {
        return consentService.findByConsentId(consentId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping(params = "interactionId")
    public ResponseEntity<List<RecordingConsent>> getByInteractionId(@RequestParam String interactionId) {
        return ResponseEntity.ok(consentService.findByInteractionId(interactionId));
    }

    @GetMapping("/latest/{interactionId}")
    public ResponseEntity<RecordingConsent> getLatestByInteractionId(@PathVariable String interactionId) {
        return consentService.findLatestByInteractionId(interactionId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping(params = "customerId")
    public ResponseEntity<List<RecordingConsent>> getByCustomerId(@RequestParam String customerId) {
        return ResponseEntity.ok(consentService.findByCustomerId(customerId));
    }

    @GetMapping(params = "status")
    public ResponseEntity<List<RecordingConsent>> getByStatus(@RequestParam String status) {
        return ResponseEntity.ok(consentService.findByStatus(status));
    }

    @PostMapping
    public ResponseEntity<RecordingConsent> create(@RequestBody RecordingConsent consent) {
        return ResponseEntity.status(HttpStatus.CREATED).body(consentService.create(consent));
    }

    @PutMapping("/{consentId}/status")
    public ResponseEntity<RecordingConsent> updateStatus(@PathVariable String consentId,
                                                          @RequestBody UpdateStatusRequest request) {
        return consentService.updateStatus(consentId, request.status(), null)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
