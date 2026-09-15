package com.gien.gits.adapter.persistence;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.sql.Types;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;

import com.gien.gits.ontology.Channel;
import com.gien.gits.ontology.Claim;
import com.gien.gits.ontology.ClaimStatus;
import com.gien.gits.ontology.Interaction;
import com.gien.gits.ontology.port.WritableInteractionRepository;

/**
 * JDBC persistence adapter for {@link Interaction} against Flyway V002 enriched interaction schema.
 *
 * <p>Maps the 14-field Interaction record to the interaction + interaction_participant tables.
 * The initiator is stored inline (initiator_id/role/display_name columns);
 * participants are stored in the interaction_participant table.
 * producedClaimIds is stored as a JSON array column.
 */
public class JdbcInteractionRepository implements WritableInteractionRepository {

    private static final String INSERT_SQL =
            "INSERT INTO interaction " +
            "(interaction_id, case_id, journey_id, interaction_type, direction, channel, " +
            " content_summary, outcome, initiator_id, initiator_role, initiator_display_name, " +
            " produced_claim_ids, occurred_at, ended_at, source_uri, source_version, source_hash, recorded_at) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', ?, CURRENT_TIMESTAMP)";

    private static final String INSERT_PARTICIPANT_SQL =
            "INSERT INTO interaction_participant " +
            "(interaction_id, participant_id, participant_role, display_name) " +
            "VALUES (?, ?, ?, ?)";

    private static final String FIND_BY_ID_SQL =
            "SELECT i.interaction_id, i.case_id, i.journey_id, i.interaction_type, i.direction, " +
            " i.channel, i.content_summary, i.outcome, " +
            " i.initiator_id, i.initiator_role, i.initiator_display_name, " +
            " i.produced_claim_ids, i.occurred_at, i.ended_at, i.source_hash, " +
            " i.source_uri, i.source_version, i.recorded_at " +
            "FROM interaction i WHERE i.interaction_id = ?";

    private static final String FIND_PARTICIPANTS_SQL =
            "SELECT participant_id, participant_role, display_name " +
            "FROM interaction_participant WHERE interaction_id = ?";

    private static final String FIND_BY_CASE_SQL =
            "SELECT i.interaction_id, i.case_id, i.journey_id, i.interaction_type, i.direction, " +
            " i.channel, i.content_summary, i.outcome, " +
            " i.initiator_id, i.initiator_role, i.initiator_display_name, " +
            " i.produced_claim_ids, i.occurred_at, i.ended_at, i.source_hash, " +
            " i.source_uri, i.source_version, i.recorded_at " +
            "FROM interaction i WHERE i.case_id = ? ORDER BY i.occurred_at";

    private static final String FIND_BY_JOURNEY_SQL =
            "SELECT i.interaction_id, i.case_id, i.journey_id, i.interaction_type, i.direction, " +
            " i.channel, i.content_summary, i.outcome, " +
            " i.initiator_id, i.initiator_role, i.initiator_display_name, " +
            " i.produced_claim_ids, i.occurred_at, i.ended_at, i.source_hash, " +
            " i.source_uri, i.source_version, i.recorded_at " +
            "FROM interaction i WHERE i.journey_id = ? ORDER BY i.occurred_at";

    private static final String FIND_ALL_SQL =
            "SELECT i.interaction_id, i.case_id, i.journey_id, i.interaction_type, i.direction, " +
            " i.channel, i.content_summary, i.outcome, " +
            " i.initiator_id, i.initiator_role, i.initiator_display_name, " +
            " i.produced_claim_ids, i.occurred_at, i.ended_at, i.source_hash, " +
            " i.source_uri, i.source_version, i.recorded_at " +
            "FROM interaction i ORDER BY i.occurred_at DESC";

    private final JdbcTemplate jdbcTemplate;

    public JdbcInteractionRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = Objects.requireNonNull(jdbcTemplate, "jdbcTemplate");
    }

    public void save(Interaction interaction) {
        if (interaction == null) {
            throw new IllegalArgumentException("interaction must not be null");
        }
        // Insert main interaction row
        jdbcTemplate.update(INSERT_SQL,
                interaction.interactionId().toString(),
                interaction.caseId().toString(),
                interaction.journeyId() == null ? null : interaction.journeyId().toString(),
                interaction.type().name(),
                interaction.direction().name(),
                interaction.channel().name(),
                interaction.contentSummary(),
                interaction.outcome().name(),
                interaction.initiator().participantId(),
                interaction.initiator().role().name(),
                interaction.initiator().displayName(),
                toJsonArray(interaction.producedClaimIds()),
                Timestamp.from(interaction.occurredAt()),
                interaction.endedAt() == null ? null : Timestamp.from(interaction.endedAt()),
                interaction.sourceHash());

        // Insert participants
        for (Interaction.Participant p : interaction.participants()) {
            jdbcTemplate.update(INSERT_PARTICIPANT_SQL,
                    interaction.interactionId().toString(),
                    p.participantId(),
                    p.role().name(),
                    p.displayName());
        }
    }

    public Optional<Interaction> findById(UUID interactionId) {
        if (interactionId == null) {
            throw new IllegalArgumentException("interactionId must not be null");
        }
        List<Interaction> results = jdbcTemplate.query(
                FIND_BY_ID_SQL,
                new InteractionRowMapper(),
                interactionId.toString());
        return results.isEmpty() ? Optional.empty() : Optional.of(results.get(0));
    }

    public List<Interaction> findByCaseId(UUID caseId) {
        if (caseId == null) {
            throw new IllegalArgumentException("caseId must not be null");
        }
        return jdbcTemplate.query(FIND_BY_CASE_SQL, new InteractionRowMapper(), caseId.toString());
    }

    public List<Interaction> findByJourneyId(UUID journeyId) {
        if (journeyId == null) {
            throw new IllegalArgumentException("journeyId must not be null");
        }
        return jdbcTemplate.query(FIND_BY_JOURNEY_SQL, new InteractionRowMapper(), journeyId.toString());
    }

    @Override
    public List<Interaction> findAll() {
        return jdbcTemplate.query(FIND_ALL_SQL, new InteractionRowMapper());
    }

    // --- Internal helpers ---

    private Interaction mapRowWithParticipants(ResultSet rs) throws SQLException {
        UUID id = UUID.fromString(rs.getString("interaction_id"));
        List<Interaction.Participant> participants = loadParticipants(id);
        return toInteraction(rs, participants);
    }

    private List<Interaction.Participant> loadParticipants(UUID interactionId) {
        return jdbcTemplate.query(FIND_PARTICIPANTS_SQL,
                (rs, rowNum) -> new Interaction.Participant(
                        rs.getString("participant_id"),
                        Interaction.Participant.Role.valueOf(rs.getString("participant_role")),
                        rs.getString("display_name")),
                interactionId.toString());
    }

    private static Interaction toInteraction(ResultSet rs, List<Interaction.Participant> participants) throws SQLException {
        String journeyIdStr = rs.getString("journey_id");
        Timestamp recordedAtTs = rs.getTimestamp("recorded_at");
        return new Interaction(
                UUID.fromString(rs.getString("interaction_id")),
                UUID.fromString(rs.getString("case_id")),
                journeyIdStr == null ? null : UUID.fromString(journeyIdStr),
                Interaction.InteractionType.valueOf(rs.getString("interaction_type")),
                Interaction.Direction.valueOf(rs.getString("direction")),
                Channel.valueOf(rs.getString("channel")),
                new Interaction.Participant(
                        rs.getString("initiator_id"),
                        Interaction.Participant.Role.valueOf(rs.getString("initiator_role")),
                        rs.getString("initiator_display_name")),
                participants,
                rs.getString("content_summary"),
                parseUuidList(rs.getString("produced_claim_ids")),
                Interaction.InteractionOutcome.valueOf(rs.getString("outcome")),
                rs.getTimestamp("occurred_at").toInstant(),
                rs.getTimestamp("ended_at") == null ? null : rs.getTimestamp("ended_at").toInstant(),
                rs.getString("source_hash"),
                rs.getString("source_uri"),
                rs.getString("source_version"),
                recordedAtTs == null ? null : recordedAtTs.toInstant());
    }

    private static List<UUID> parseUuidList(String json) {
        if (json == null || json.isBlank() || "null".equals(json)) {
            return List.of();
        }
        // Simple JSON array parsing: ["uuid1","uuid2"]
        String trimmed = json.trim();
        if (trimmed.startsWith("[")) {
            trimmed = trimmed.substring(1);
        }
        if (trimmed.endsWith("]")) {
            trimmed = trimmed.substring(0, trimmed.length() - 1);
        }
        if (trimmed.isBlank()) {
            return List.of();
        }
        return java.util.Arrays.stream(trimmed.split(","))
                .map(s -> s.trim().replace("\"", ""))
                .filter(s -> !s.isBlank())
                .map(UUID::fromString)
                .toList();
    }

    private static String toJsonArray(List<UUID> uuids) {
        if (uuids == null || uuids.isEmpty()) {
            return "[]";
        }
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < uuids.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append("\"").append(uuids.get(i)).append("\"");
        }
        sb.append("]");
        return sb.toString();
    }

    private final class InteractionRowMapper implements RowMapper<Interaction> {
        @Override
        public Interaction mapRow(ResultSet rs, int rowNum) throws SQLException {
            return mapRowWithParticipants(rs);
        }
    }
}
