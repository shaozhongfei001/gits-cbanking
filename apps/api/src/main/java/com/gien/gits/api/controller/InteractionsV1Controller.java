package com.gien.gits.api.controller;

import com.gien.gits.api.dto.ListedInteractionDto;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.port.CustomerJourneyRepository;
import com.gien.gits.ontology.Interaction;
import com.gien.gits.ontology.port.InteractionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * OpenAPI {@code /interactions} 只读查询（listInteractions / getInteraction）。
 *
 * <p>不实现 recordInteraction 写入口。customerId 从既有旅程或 CUSTOMER 参与者解析，
 * 无法映射的行跳过，空结果返回 {@code []}，不返回 500。</p>
 */
@RestController
@RequestMapping("/api/v1/interactions")
public class InteractionsV1Controller {

    private static final Logger log = LoggerFactory.getLogger(InteractionsV1Controller.class);

    private final InteractionRepository interactionRepository;
    private final CustomerJourneyRepository journeyRepository;

    public InteractionsV1Controller(
            InteractionRepository interactionRepository,
            CustomerJourneyRepository journeyRepository) {
        this.interactionRepository = interactionRepository;
        this.journeyRepository = journeyRepository;
    }

    @GetMapping
    public ResponseEntity<List<ListedInteractionDto>> listInteractions(
            @RequestParam(required = false) String customerId) {
        log.info("Listing interactions: customerId={}", customerId);
        List<ListedInteractionDto> result = new ArrayList<>();
        for (Interaction interaction : interactionRepository.findAll()) {
            String resolvedCustomerId = resolveCustomerId(interaction);
            if (resolvedCustomerId == null || resolvedCustomerId.isBlank()) {
                continue;
            }
            if (customerId != null && !customerId.isBlank() && !customerId.equals(resolvedCustomerId)) {
                continue;
            }
            result.add(ListedInteractionDto.from(interaction, resolvedCustomerId));
        }
        return ResponseEntity.ok(result);
    }

    @GetMapping("/{interactionId}")
    public ResponseEntity<ListedInteractionDto> getInteraction(@PathVariable String interactionId) {
        UUID id;
        try {
            id = UUID.fromString(interactionId);
        } catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("interactionId must be a UUID");
        }
        Interaction interaction = interactionRepository.findById(id).orElse(null);
        if (interaction == null) {
            return ResponseEntity.notFound().build();
        }
        String resolvedCustomerId = resolveCustomerId(interaction);
        if (resolvedCustomerId == null || resolvedCustomerId.isBlank()) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(ListedInteractionDto.from(interaction, resolvedCustomerId));
    }

    private String resolveCustomerId(Interaction interaction) {
        if (interaction.journeyId() != null) {
            String fromJourney = journeyRepository.findJourneyById(interaction.journeyId())
                    .map(CustomerJourney::customerId)
                    .orElse(null);
            if (fromJourney != null && !fromJourney.isBlank()) {
                return fromJourney;
            }
        }
        if (interaction.initiator().role() == Interaction.Participant.Role.CUSTOMER) {
            return interaction.initiator().participantId();
        }
        return interaction.participants().stream()
                .filter(participant -> participant.role() == Interaction.Participant.Role.CUSTOMER)
                .map(Interaction.Participant::participantId)
                .filter(id -> id != null && !id.isBlank())
                .findFirst()
                .orElse(null);
    }
}
