package com.gien.gits.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.gien.gits.ontology.Channel;
import com.gien.gits.ontology.Interaction;

import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

/**
 * OpenAPI Interaction 列表/详情读模型（operationId=listInteractions / getInteraction）。
 *
 * <p>只映射既有本体字段到已登记合同形状，不发明 transcript / 日历写回。</p>
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public record ListedInteractionDto(
        String interactionId,
        String customerId,
        String channel,
        String transcript,
        String summary,
        String recordingConsentId,
        Integer durationSeconds,
        List<String> participants,
        String interactionDate,
        String createdAt,
        String updatedAt
) {
    public static ListedInteractionDto from(Interaction interaction, String customerId) {
        List<String> names = new ArrayList<>();
        LinkedHashSet<String> seen = new LinkedHashSet<>();
        addName(names, seen, interaction.initiator().displayName());
        for (Interaction.Participant participant : interaction.participants()) {
            addName(names, seen, participant.displayName());
        }
        Integer duration = null;
        if (interaction.endedAt() != null) {
            long seconds = Duration.between(interaction.occurredAt(), interaction.endedAt()).getSeconds();
            if (seconds >= 0 && seconds <= Integer.MAX_VALUE) {
                duration = (int) seconds;
            }
        }
        String recorded = interaction.recordedAt() == null ? null : interaction.recordedAt().toString();
        return new ListedInteractionDto(
                interaction.interactionId().toString(),
                customerId,
                toContractChannel(interaction.channel()),
                null,
                interaction.contentSummary(),
                null,
                duration,
                List.copyOf(names),
                interaction.occurredAt().toString(),
                recorded,
                recorded);
    }

    static String toContractChannel(Channel channel) {
        if (channel == null) {
            return "OTHER";
        }
        return switch (channel) {
            case PHONE, PHONE_CALL -> "PHONE";
            case IN_PERSON, FACE_TO_FACE -> "IN_PERSON";
            case EMAIL -> "EMAIL";
            case INSTANT_MESSAGE -> "WECHAT";
            case VIDEO_CONFERENCE -> "VIDEO";
            default -> "OTHER";
        };
    }

    private static void addName(List<String> names, LinkedHashSet<String> seen, String name) {
        if (name == null || name.isBlank() || !seen.add(name)) {
            return;
        }
        names.add(name);
    }
}
