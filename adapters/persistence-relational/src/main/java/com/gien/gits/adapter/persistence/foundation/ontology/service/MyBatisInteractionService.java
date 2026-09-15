package com.gien.gits.adapter.persistence.foundation.ontology.service;

import com.gien.gits.adapter.persistence.foundation.ontology.dto.InteractionRow;
import com.gien.gits.adapter.persistence.foundation.ontology.dto.ParticipantRow;
import com.gien.gits.adapter.persistence.foundation.ontology.mapper.InteractionMapper;
import com.gien.gits.ontology.Interaction;
import com.gien.gits.ontology.port.WritableInteractionRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * MyBatis 实现 — 交互仓储
 */
public class MyBatisInteractionService implements WritableInteractionRepository {

    private final InteractionMapper mapper;

    public MyBatisInteractionService(InteractionMapper mapper) {
        this.mapper = mapper;
    }

    @Override
    public Optional<Interaction> findById(UUID interactionId) {
        return mapper.findRowById(interactionId).map(this::toInteraction);
    }

    @Override
    public List<Interaction> findByCaseId(UUID caseId) {
        return mapper.findRowsByCaseId(caseId).stream().map(this::toInteraction).toList();
    }

    @Override
    public List<Interaction> findByJourneyId(UUID journeyId) {
        return mapper.findRowsByJourneyId(journeyId).stream().map(this::toInteraction).toList();
    }

    @Override
    public List<Interaction> findAll() {
        return mapper.findRowsAll().stream().map(this::toInteraction).toList();
    }

    @Override
    public void save(Interaction interaction) {
        mapper.insert(interaction);
        if (interaction.participants() != null) {
            for (var participant : interaction.participants()) {
                mapper.insertParticipant(interaction.interactionId(), participant);
            }
        }
    }

    private Interaction toInteraction(InteractionRow row) {
        var initiator = new Interaction.Participant(
                row.initiatorId(), row.initiatorRole(), row.initiatorDisplayName());

        var participantRows = mapper.findParticipantsByInteractionId(row.interactionId());
        var participants = participantRows.stream()
                .map(pr -> new Interaction.Participant(pr.participantId(), pr.participantRole(), pr.displayName()))
                .toList();

        return new Interaction(
                row.interactionId(), row.caseId(), row.journeyId(),
                row.type(), row.direction(), row.channel(),
                initiator, participants,
                row.contentSummary(), row.producedClaimIds(), row.outcome(),
                row.occurredAt(), row.endedAt(), row.sourceHash(),
                row.sourceUri(), row.sourceVersion(), row.recordedAt());
    }
}
