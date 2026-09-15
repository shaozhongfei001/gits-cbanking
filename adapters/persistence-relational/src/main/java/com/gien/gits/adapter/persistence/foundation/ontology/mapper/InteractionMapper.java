package com.gien.gits.adapter.persistence.foundation.ontology.mapper;

import com.gien.gits.adapter.persistence.foundation.ontology.dto.InteractionRow;
import com.gien.gits.adapter.persistence.foundation.ontology.dto.ParticipantRow;
import com.gien.gits.ontology.Interaction;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * 交互 Mapper — foundation/ontology 层
 */
@Mapper
public interface InteractionMapper {

    void insert(Interaction interaction);

    void insertParticipant(@Param("interactionId") UUID interactionId,
                           @Param("participant") Interaction.Participant participant);

    Optional<InteractionRow> findRowById(@Param("interactionId") UUID interactionId);

    List<InteractionRow> findRowsByCaseId(@Param("caseId") UUID caseId);

    List<InteractionRow> findRowsByJourneyId(@Param("journeyId") UUID journeyId);

    List<InteractionRow> findRowsAll();

    List<ParticipantRow> findParticipantsByInteractionId(@Param("interactionId") UUID interactionId);
}
