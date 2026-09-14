package com.gien.gits.api.controller;

import com.gien.gits.api.dto.ClaimResponse;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.port.CustomerJourneyRepository;
import com.gien.gits.ontology.Claim;
import com.gien.gits.ontology.port.ClaimRepository;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * 主张(Claim)合同控制器 — 对齐 OpenAPI Claim tag。
 *
 * <p>实现合同端点 {@code listClaims}（GET /engagement/claims?customerId=）与
 * {@code getClaim}（GET /engagement/claims/{claimId}）。</p>
 *
 * <p>领域 Claim 为 statement 型（caseId + statement），无 customerId 列；
 * 本控制器通过 {@link CustomerJourneyRepository} 将 customerId 解析为 caseId，
 * 再查询 claim，并回填 customerId 以满足合同 {@code Claim.customerId} 必填约束。</p>
 */
@RestController
@RequestMapping("/api/v1/engagement/claims")
public class EngagementClaimController {

    private final ClaimRepository claimRepo;
    private final CustomerJourneyRepository journeyRepo;

    public EngagementClaimController(ClaimRepository claimRepo,
                                     CustomerJourneyRepository journeyRepo) {
        this.claimRepo = Objects.requireNonNull(claimRepo);
        this.journeyRepo = Objects.requireNonNull(journeyRepo);
    }

    /**
     * 按客户ID查询主张列表（合同 operationId=listClaims）。
     * customerId 缺省时返回空数组。
     */
    @GetMapping
    public ResponseEntity<List<ClaimResponse>> listClaims(
            @RequestParam(required = false) String customerId) {
        if (customerId == null || customerId.isBlank()) {
            return ResponseEntity.ok(List.of());
        }
        List<CustomerJourney> journeys = journeyRepo.findJourneysByCustomerId(customerId);
        if (journeys.isEmpty()) {
            return ResponseEntity.ok(List.of());
        }

        // caseId -> customerId 映射（一个 caseId 归属一个客户）
        Map<UUID, String> caseCustomer = journeys.stream()
                .collect(Collectors.toMap(
                        CustomerJourney::operatingCaseId,
                        CustomerJourney::customerId,
                        (a, b) -> a));

        List<ClaimResponse> responses = journeys.stream()
                .map(CustomerJourney::operatingCaseId)
                .distinct()
                .flatMap(caseId -> claimRepo.findByCaseId(caseId).stream())
                .map(claim -> toResponse(claim, caseCustomer.get(claim.caseId())))
                .toList();

        return ResponseEntity.ok(responses);
    }

    /**
     * 按主张ID查询（合同 operationId=getClaim）。
     */
    @GetMapping("/{claimId}")
    public ResponseEntity<ClaimResponse> getClaim(@PathVariable String claimId) {
        UUID uuid;
        try {
            uuid = UUID.fromString(claimId);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
        return claimRepo.findById(uuid)
                .map(claim -> ResponseEntity.ok(toResponse(claim, resolveCustomerId(claim.caseId()))))
                .orElse(ResponseEntity.notFound().build());
    }

    private String resolveCustomerId(UUID caseId) {
        return journeyRepo.findJourneysByCaseId(caseId).stream()
                .map(CustomerJourney::customerId)
                .findFirst()
                .orElse(null);
    }

    private ClaimResponse toResponse(Claim claim, String customerId) {
        String statement = claim.statement();
        return new ClaimResponse(
                claim.claimId().toString(),
                customerId,
                claim.caseId().toString(),
                claim.claimType() != null ? claim.claimType().name() : null,
                claim.status() != null ? claim.status().name() : null,
                statement,
                statement,
                null,
                null,
                claim.recordedAt(),
                claim.recordedAt(),
                claim.validTo());
    }
}
