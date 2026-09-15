package com.gien.gits.adapter.persistence;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.RecommendationAttempt;
import com.gien.gits.customerjourney.recommendation.RecommendationAttemptStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationFeedback;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;
import com.gien.gits.customerjourney.recommendation.port.ProductRecommendationRepository;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * JDBC persistence adapter for the product recommendation run (三段式产品推荐),
 * against Flyway {@code V020__product_recommendation.sql} 五张表：
 * {@code product_recommendation_run / product_recommendation_attempt /
 * recommendation_proposal_version / recommendation_human_decision /
 * recommendation_feedback}。列名与迁移 SQL 保持一致。
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public class JdbcProductRecommendationRepository implements ProductRecommendationRepository {

    private static final String INSERT_RUN =
        "INSERT INTO product_recommendation_run (" +
        "run_id, customer_id, journey_id, operating_case_id, need_version_ids, " +
        "recommendation_objective, requested_product_domains, as_of, idempotency_key, " +
        "`status`, current_version_id, kert_job_ref, snapshot_refs, created_at, updated_at) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    private static final String UPDATE_RUN =
        "UPDATE product_recommendation_run SET customer_id = ?, journey_id = ?, operating_case_id = ?, " +
        "need_version_ids = ?, recommendation_objective = ?, requested_product_domains = ?, " +
        "as_of = ?, idempotency_key = ?, `status` = ?, current_version_id = ?, kert_job_ref = ?, " +
        "snapshot_refs = ?, updated_at = ? WHERE run_id = ?";

    private static final String FIND_RUN_BY_ID =
        "SELECT * FROM product_recommendation_run WHERE run_id = ?";

    private static final String FIND_RUN_BY_IDEMPOTENCY =
        "SELECT * FROM product_recommendation_run WHERE idempotency_key = ?";

    private static final String INSERT_ATTEMPT =
        "INSERT INTO product_recommendation_attempt (" +
        "attempt_id, run_id, kert_request_id, started_at, finished_at, `status`, error_code, retryable) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)";

    private static final String FIND_ATTEMPTS_BY_RUN =
        "SELECT * FROM product_recommendation_attempt WHERE run_id = ? ORDER BY started_at";

    private static final String INSERT_VERSION =
        "INSERT INTO recommendation_proposal_version (" +
        "version_id, run_id, result_ref, evidence_bundle_id, content_hash, payload, superseded_by, created_at) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)";

    private static final String FIND_VERSION_BY_ID =
        "SELECT * FROM recommendation_proposal_version WHERE version_id = ?";

    private static final String FIND_VERSIONS_BY_RUN =
        "SELECT * FROM recommendation_proposal_version WHERE run_id = ? ORDER BY created_at";

    private static final String INSERT_DECISION =
        "INSERT INTO recommendation_human_decision (" +
        "decision_id, gate_id, run_id, proposal_version_id, `decision`, modifications, reason, " +
        "actor_id, actor_role, decided_at) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    private static final String FIND_DECISION_BY_ID =
        "SELECT * FROM recommendation_human_decision WHERE decision_id = ?";

    private static final String FIND_DECISION_BY_VERSION =
        "SELECT * FROM recommendation_human_decision WHERE proposal_version_id = ?";

    private static final String FIND_DECISIONS_BY_RUN =
        "SELECT * FROM recommendation_human_decision WHERE run_id = ? ORDER BY decided_at";

    private static final String INSERT_FEEDBACK =
        "INSERT INTO recommendation_feedback (" +
        "feedback_id, run_id, adopted, rejection_reason, modified_fields, outcome_ref, created_at) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?)";

    private static final String FIND_FEEDBACK_BY_RUN =
        "SELECT * FROM recommendation_feedback WHERE run_id = ? ORDER BY created_at";

    private final JdbcTemplate jdbc;
    private final ObjectMapper objectMapper;

    public JdbcProductRecommendationRepository(JdbcTemplate jdbc, ObjectMapper objectMapper) {
        this.jdbc = Objects.requireNonNull(jdbc, "jdbc");
        this.objectMapper = Objects.requireNonNull(objectMapper, "objectMapper");
    }

    // ── run ─────────────────────────────────────────────────────────────

    @Override
    public void saveRun(ProductRecommendationRun run) {
        jdbc.update(INSERT_RUN,
            run.runId(), run.customerId(), run.journeyId(), run.operatingCaseId(),
            toJson(run.needVersionIds()), run.recommendationObjective(),
            toJson(run.requestedProductDomains()), Timestamp.from(run.asOf()),
            run.idempotencyKey(), run.status().name(), run.currentVersionId(),
            run.kertJobRef(), toJson(run.snapshotRefs()),
            Timestamp.from(run.createdAt()), Timestamp.from(run.updatedAt()));
    }

    @Override
    public void updateRun(ProductRecommendationRun run) {
        jdbc.update(UPDATE_RUN,
            run.customerId(), run.journeyId(), run.operatingCaseId(),
            toJson(run.needVersionIds()), run.recommendationObjective(),
            toJson(run.requestedProductDomains()), Timestamp.from(run.asOf()),
            run.idempotencyKey(), run.status().name(), run.currentVersionId(),
            run.kertJobRef(), toJson(run.snapshotRefs()), Timestamp.from(run.updatedAt()),
            run.runId());
    }

    @Override
    public Optional<ProductRecommendationRun> findRunById(String runId) {
        List<ProductRecommendationRun> rows = jdbc.query(FIND_RUN_BY_ID, new RunRowMapper(objectMapper), runId);
        return rows.isEmpty() ? Optional.empty() : Optional.of(rows.get(0));
    }

    @Override
    public Optional<ProductRecommendationRun> findRunByIdempotencyKey(String idempotencyKey) {
        List<ProductRecommendationRun> rows =
            jdbc.query(FIND_RUN_BY_IDEMPOTENCY, new RunRowMapper(objectMapper), idempotencyKey);
        return rows.isEmpty() ? Optional.empty() : Optional.of(rows.get(0));
    }

    // ── attempt ─────────────────────────────────────────────────────────

    @Override
    public void saveAttempt(RecommendationAttempt attempt) {
        jdbc.update(INSERT_ATTEMPT,
            attempt.attemptId(), attempt.runId(), attempt.kertRequestId(),
            Timestamp.from(attempt.startedAt()),
            attempt.finishedAt() == null ? null : Timestamp.from(attempt.finishedAt()),
            attempt.status().name(), attempt.errorCode(), attempt.retryable());
    }

    @Override
    public List<RecommendationAttempt> findAttemptsByRun(String runId) {
        return jdbc.query(FIND_ATTEMPTS_BY_RUN, new AttemptRowMapper(), runId);
    }

    // ── proposal version ───────────────────────────────────────────────

    @Override
    public void saveVersion(RecommendationProposalVersion version) {
        jdbc.update(INSERT_VERSION,
            version.versionId(), version.runId(), version.resultRef(), version.evidenceBundleId(),
            version.contentHash(), toJson(version.payload()), version.supersededBy(),
            Timestamp.from(version.createdAt()));
    }

    @Override
    public Optional<RecommendationProposalVersion> findVersionById(String versionId) {
        List<RecommendationProposalVersion> rows =
            jdbc.query(FIND_VERSION_BY_ID, new VersionRowMapper(objectMapper), versionId);
        return rows.isEmpty() ? Optional.empty() : Optional.of(rows.get(0));
    }

    @Override
    public List<RecommendationProposalVersion> findVersionsByRun(String runId) {
        return jdbc.query(FIND_VERSIONS_BY_RUN, new VersionRowMapper(objectMapper), runId);
    }

    // ── human decision ─────────────────────────────────────────────────

    @Override
    public void saveDecision(RecommendationHumanDecision decision) {
        jdbc.update(INSERT_DECISION,
            decision.decisionId(), decision.gateId(), decision.runId(), decision.proposalVersionId(),
            decision.decision().name(), toJson(decision.modifications()), decision.reason(),
            decision.actorId(), decision.actorRole(), Timestamp.from(decision.decidedAt()));
    }

    @Override
    public Optional<RecommendationHumanDecision> findDecisionById(String decisionId) {
        List<RecommendationHumanDecision> rows =
            jdbc.query(FIND_DECISION_BY_ID, new DecisionRowMapper(objectMapper), decisionId);
        return rows.isEmpty() ? Optional.empty() : Optional.of(rows.get(0));
    }

    @Override
    public Optional<RecommendationHumanDecision> findDecisionByProposalVersion(String proposalVersionId) {
        List<RecommendationHumanDecision> rows =
            jdbc.query(FIND_DECISION_BY_VERSION, new DecisionRowMapper(objectMapper), proposalVersionId);
        return rows.isEmpty() ? Optional.empty() : Optional.of(rows.get(0));
    }

    @Override
    public List<RecommendationHumanDecision> findDecisionsByRun(String runId) {
        return jdbc.query(FIND_DECISIONS_BY_RUN, new DecisionRowMapper(objectMapper), runId);
    }

    // ── feedback ───────────────────────────────────────────────────────

    @Override
    public void saveFeedback(RecommendationFeedback feedback) {
        jdbc.update(INSERT_FEEDBACK,
            feedback.feedbackId(), feedback.runId(), feedback.adopted(), feedback.rejectionReason(),
            toJson(feedback.modifiedFields()), feedback.outcomeRef(), Timestamp.from(feedback.createdAt()));
    }

    @Override
    public List<RecommendationFeedback> findFeedbackByRun(String runId) {
        return jdbc.query(FIND_FEEDBACK_BY_RUN, new FeedbackRowMapper(objectMapper), runId);
    }

    // ── JSON helpers ───────────────────────────────────────────────────

    private String toJson(Object value) {
        try {
            return value == null ? null : objectMapper.writeValueAsString(value);
        } catch (Exception e) {
            throw new RuntimeException("Failed to serialize product-recommendation JSON", e);
        }
    }

    private static List<String> readStringList(ObjectMapper om, String json) {
        List<String> value = readJson(om, json, new TypeReference<List<String>>() {});
        return value == null ? List.of() : value;
    }

    private static Map<String, String> readStringMap(ObjectMapper om, String json) {
        Map<String, String> value = readJson(om, json, new TypeReference<Map<String, String>>() {});
        return value == null ? Map.of() : value;
    }

    private static Map<String, Object> readObjectMap(ObjectMapper om, String json) {
        Map<String, Object> value = readJson(om, json, new TypeReference<Map<String, Object>>() {});
        return value == null ? Map.of() : value;
    }

    private static List<Map<String, Object>> readMapList(ObjectMapper om, String json) {
        List<Map<String, Object>> value =
            readJson(om, json, new TypeReference<List<Map<String, Object>>>() {});
        return value == null ? List.of() : value;
    }

    /**
     * 读取 JSON 列。H2 的 JSON 类型把 {@code setString} 的 JSON 文档当 JSON 字符串存储，
     * {@code getString} 会返回二次转义的字符串字面量；MySQL 则直接返回 JSON 文档文本。
     * 先尝试直接反序列化，失败（或为带引号字符串字面量）时剥一层引号后再反序列化，
     * 两种后端均能正确还原。
     */
    private static <T> T readJson(ObjectMapper om, String json, TypeReference<T> ref) {
        if (json == null || json.isBlank()) {
            return null;
        }
        try {
            return om.readValue(json, ref);
        } catch (Exception first) {
            String trimmed = json.trim();
            if (trimmed.startsWith("\"") && trimmed.endsWith("\"")) {
                try {
                    String unquoted = om.readValue(trimmed, String.class);
                    return om.readValue(unquoted, ref);
                } catch (Exception ignored) {
                    // fall through → null
                }
            }
            return null;
        }
    }

    // ── row mappers ────────────────────────────────────────────────────

    private static final class RunRowMapper implements RowMapper<ProductRecommendationRun> {
        private final ObjectMapper om;

        RunRowMapper(ObjectMapper om) {
            this.om = om;
        }

        @Override
        public ProductRecommendationRun mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new ProductRecommendationRun(
                rs.getString("run_id"),
                rs.getString("customer_id"),
                rs.getString("journey_id"),
                rs.getString("operating_case_id"),
                readStringList(om, rs.getString("need_version_ids")),
                rs.getString("recommendation_objective"),
                readStringList(om, rs.getString("requested_product_domains")),
                rs.getTimestamp("as_of").toInstant(),
                rs.getString("idempotency_key"),
                ProductRecommendationRunStatus.valueOf(rs.getString("status")),
                rs.getString("current_version_id"),
                rs.getString("kert_job_ref"),
                readStringMap(om, rs.getString("snapshot_refs")),
                rs.getTimestamp("created_at").toInstant(),
                rs.getTimestamp("updated_at").toInstant());
        }
    }

    private static final class AttemptRowMapper implements RowMapper<RecommendationAttempt> {
        @Override
        public RecommendationAttempt mapRow(ResultSet rs, int rowNum) throws SQLException {
            Timestamp finished = rs.getTimestamp("finished_at");
            return new RecommendationAttempt(
                rs.getString("attempt_id"),
                rs.getString("run_id"),
                rs.getString("kert_request_id"),
                rs.getTimestamp("started_at").toInstant(),
                finished == null ? null : finished.toInstant(),
                RecommendationAttemptStatus.valueOf(rs.getString("status")),
                rs.getString("error_code"),
                rs.getBoolean("retryable"));
        }
    }

    private static final class VersionRowMapper implements RowMapper<RecommendationProposalVersion> {
        private final ObjectMapper om;

        VersionRowMapper(ObjectMapper om) {
            this.om = om;
        }

        @Override
        public RecommendationProposalVersion mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new RecommendationProposalVersion(
                rs.getString("version_id"),
                rs.getString("run_id"),
                rs.getString("result_ref"),
                rs.getString("evidence_bundle_id"),
                rs.getString("content_hash"),
                readObjectMap(om, rs.getString("payload")),
                rs.getString("superseded_by"),
                rs.getTimestamp("created_at").toInstant());
        }
    }

    private static final class DecisionRowMapper implements RowMapper<RecommendationHumanDecision> {
        private final ObjectMapper om;

        DecisionRowMapper(ObjectMapper om) {
            this.om = om;
        }

        @Override
        public RecommendationHumanDecision mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new RecommendationHumanDecision(
                rs.getString("decision_id"),
                rs.getString("gate_id"),
                rs.getString("run_id"),
                rs.getString("proposal_version_id"),
                RecommendationDecision.valueOf(rs.getString("decision")),
                readMapList(om, rs.getString("modifications")),
                rs.getString("reason"),
                rs.getString("actor_id"),
                rs.getString("actor_role"),
                rs.getTimestamp("decided_at").toInstant());
        }
    }

    private static final class FeedbackRowMapper implements RowMapper<RecommendationFeedback> {
        private final ObjectMapper om;

        FeedbackRowMapper(ObjectMapper om) {
            this.om = om;
        }

        @Override
        public RecommendationFeedback mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new RecommendationFeedback(
                rs.getString("feedback_id"),
                rs.getString("run_id"),
                rs.getObject("adopted", Boolean.class),
                rs.getString("rejection_reason"),
                readStringList(om, rs.getString("modified_fields")),
                rs.getString("outcome_ref"),
                rs.getTimestamp("created_at").toInstant());
        }
    }
}
