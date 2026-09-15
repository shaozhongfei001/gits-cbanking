package com.gien.gits.adapter.persistence.scenario;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;

import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.InsightClaim;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.PostvisitAnalysis;
import com.gien.gits.customerjourney.PrevisitReport;
import com.gien.gits.customerjourney.ProductCandidateClaim;
import com.gien.gits.customerjourney.port.WritableCustomerJourneyRepository;

/**
 * JDBC persistence adapter for CustomerJourney scenario entities.
 * Covers M17(CustomerJourney), M18(InsightClaim), M20(ProductCandidateClaim),
 * M21(PrevisitReport), M22(PostvisitAnalysis).
 *
 * <p>Placed in the API app's adapter package because persistence-relational
 * does not depend on scenario-customer-journey module.
 */
public class JdbcCustomerJourneyRepository implements WritableCustomerJourneyRepository {

    private final JdbcTemplate jdbc;

    public JdbcCustomerJourneyRepository(JdbcTemplate jdbc) {
        this.jdbc = Objects.requireNonNull(jdbc, "jdbc");
    }

    // ── M17: CustomerJourney ──

    public void saveJourney(CustomerJourney journey) {
        jdbc.update(
            "INSERT INTO customer_journey (journey_id, case_id, customer_id, customer_name, phase, started_at, updated_at) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            journey.journeyId().toString(),
            journey.operatingCaseId().toString(),
            journey.customerId(),
            journey.customerName(),
            journey.phase().name(),
            Timestamp.from(journey.startedAt()),
            journey.updatedAt() == null ? null : Timestamp.from(journey.updatedAt()));
    }

    public Optional<CustomerJourney> findJourneyById(UUID journeyId) {
        List<CustomerJourney> results = jdbc.query(
            "SELECT journey_id, case_id, customer_id, customer_name, phase, started_at, updated_at " +
            "FROM customer_journey WHERE journey_id = ?",
            new JourneyRowMapper(), journeyId.toString());
        return results.isEmpty() ? Optional.empty() : Optional.of(results.get(0));
    }

    public List<CustomerJourney> findJourneysByCaseId(UUID caseId) {
        return jdbc.query(
            "SELECT journey_id, case_id, customer_id, customer_name, phase, started_at, updated_at " +
            "FROM customer_journey WHERE case_id = ? ORDER BY started_at",
            new JourneyRowMapper(), caseId.toString());
    }

    @Override
    public List<CustomerJourney> findJourneysByCustomerId(String customerId) {
        return jdbc.query(
            "SELECT journey_id, case_id, customer_id, customer_name, phase, started_at, updated_at " +
            "FROM customer_journey WHERE customer_id = ? ORDER BY started_at DESC",
            new JourneyRowMapper(), customerId);
    }

    public void updateJourneyPhase(UUID journeyId, JourneyPhase phase) {
        jdbc.update(
            "UPDATE customer_journey SET phase = ?, updated_at = CURRENT_TIMESTAMP WHERE journey_id = ?",
            phase.name(), journeyId.toString());
    }

    // ── M18: InsightClaim ──

    public void saveInsight(InsightClaim insight) {
        jdbc.update(
            "INSERT INTO insight_claim (insight_id, claim_id, operating_case_id, insight_category, insight_summary, generated_at) " +
            "VALUES (?, ?, ?, ?, ?, ?)",
            insight.insightId().toString(),
            insight.claimId().toString(),
            insight.operatingCaseId().toString(),
            insight.insightCategory(),
            insight.insightSummary(),
            Timestamp.from(insight.generatedAt()));
    }

    public Optional<InsightClaim> findInsightById(UUID insightId) {
        List<InsightClaim> results = jdbc.query(
            "SELECT insight_id, claim_id, operating_case_id, insight_category, insight_summary, generated_at " +
            "FROM insight_claim WHERE insight_id = ?",
            new InsightRowMapper(), insightId.toString());
        return results.isEmpty() ? Optional.empty() : Optional.of(results.get(0));
    }

    public List<InsightClaim> findInsightsByCaseId(UUID caseId) {
        return jdbc.query(
            "SELECT insight_id, claim_id, operating_case_id, insight_category, insight_summary, generated_at " +
            "FROM insight_claim WHERE operating_case_id = ? ORDER BY generated_at",
            new InsightRowMapper(), caseId.toString());
    }

    // ── M20: ProductCandidateClaim ──

    public void saveProductCandidate(ProductCandidateClaim product) {
        jdbc.update(
            "INSERT INTO product_candidate_claim (product_id, claim_id, insight_claim_id, operating_case_id, " +
            " product_code, product_name, match_reason, proposed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            product.productId().toString(),
            product.claimId().toString(),
            product.insightClaimId().toString(),
            product.operatingCaseId().toString(),
            product.productCode(),
            product.productName(),
            product.matchReason(),
            Timestamp.from(product.proposedAt()));
    }

    public Optional<ProductCandidateClaim> findProductCandidateById(UUID productId) {
        List<ProductCandidateClaim> results = jdbc.query(
            "SELECT product_id, claim_id, insight_claim_id, operating_case_id, " +
            " product_code, product_name, match_reason, proposed_at " +
            "FROM product_candidate_claim WHERE product_id = ?",
            new ProductRowMapper(), productId.toString());
        return results.isEmpty() ? Optional.empty() : Optional.of(results.get(0));
    }

    // ── M21: PrevisitReport ──

    public void savePrevisitReport(PrevisitReport report) {
        jdbc.update(
            "INSERT INTO previsit_report (report_id, operating_case_id, journey_id, insight_ids, " +
            " product_candidate_ids, summary, generated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            report.reportId().toString(),
            report.operatingCaseId().toString(),
            report.journeyId().toString(),
            toJsonArray(report.insightIds()),
            toJsonArray(report.productCandidateIds()),
            report.summary(),
            Timestamp.from(report.generatedAt()));
    }

    public Optional<PrevisitReport> findPrevisitReportById(UUID reportId) {
        List<PrevisitReport> results = jdbc.query(
            "SELECT report_id, operating_case_id, journey_id, insight_ids, " +
            " product_candidate_ids, summary, generated_at " +
            "FROM previsit_report WHERE report_id = ?",
            new PrevisitRowMapper(), reportId.toString());
        return results.isEmpty() ? Optional.empty() : Optional.of(results.get(0));
    }

    // ── M22: PostvisitAnalysis ──

    public void savePostvisitAnalysis(PostvisitAnalysis analysis) {
        jdbc.update(
            "INSERT INTO postvisit_analysis (analysis_id, operating_case_id, journey_id, " +
            " previsit_report_id, outcome, follow_up_action, analyzed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            analysis.analysisId().toString(),
            analysis.operatingCaseId().toString(),
            analysis.journeyId().toString(),
            analysis.previsitReportId().toString(),
            analysis.outcome(),
            analysis.followUpAction(),
            Timestamp.from(analysis.analyzedAt()));
    }

    public Optional<PostvisitAnalysis> findPostvisitAnalysisById(UUID analysisId) {
        List<PostvisitAnalysis> results = jdbc.query(
            "SELECT analysis_id, operating_case_id, journey_id, previsit_report_id, " +
            " outcome, follow_up_action, analyzed_at " +
            "FROM postvisit_analysis WHERE analysis_id = ?",
            new PostvisitRowMapper(), analysisId.toString());
        return results.isEmpty() ? Optional.empty() : Optional.of(results.get(0));
    }

    // ── RowMappers ──

    private static final class JourneyRowMapper implements RowMapper<CustomerJourney> {
        @Override
        public CustomerJourney mapRow(ResultSet rs, int rowNum) throws SQLException {
            Timestamp updatedAtTs = rs.getTimestamp("updated_at");
            return new CustomerJourney(
                    UUID.fromString(rs.getString("journey_id")),
                    UUID.fromString(rs.getString("case_id")),
                    rs.getString("customer_id"),
                    rs.getString("customer_name"),
                    JourneyPhase.valueOf(rs.getString("phase")),
                    rs.getTimestamp("started_at").toInstant(),
                    updatedAtTs == null ? null : updatedAtTs.toInstant());
        }
    }

    private static final class InsightRowMapper implements RowMapper<InsightClaim> {
        @Override
        public InsightClaim mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new InsightClaim(
                    UUID.fromString(rs.getString("insight_id")),
                    UUID.fromString(rs.getString("claim_id")),
                    UUID.fromString(rs.getString("operating_case_id")),
                    rs.getString("insight_category"),
                    rs.getString("insight_summary"),
                    rs.getTimestamp("generated_at").toInstant());
        }
    }

    private static final class ProductRowMapper implements RowMapper<ProductCandidateClaim> {
        @Override
        public ProductCandidateClaim mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new ProductCandidateClaim(
                    UUID.fromString(rs.getString("product_id")),
                    UUID.fromString(rs.getString("claim_id")),
                    UUID.fromString(rs.getString("insight_claim_id")),
                    UUID.fromString(rs.getString("operating_case_id")),
                    rs.getString("product_code"),
                    rs.getString("product_name"),
                    rs.getString("match_reason"),
                    rs.getTimestamp("proposed_at").toInstant());
        }
    }

    private static final class PrevisitRowMapper implements RowMapper<PrevisitReport> {
        @Override
        public PrevisitReport mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new PrevisitReport(
                    UUID.fromString(rs.getString("report_id")),
                    UUID.fromString(rs.getString("operating_case_id")),
                    UUID.fromString(rs.getString("journey_id")),
                    parseUuidList(rs.getString("insight_ids")),
                    parseUuidList(rs.getString("product_candidate_ids")),
                    rs.getString("summary"),
                    rs.getTimestamp("generated_at").toInstant());
        }
    }

    private static final class PostvisitRowMapper implements RowMapper<PostvisitAnalysis> {
        @Override
        public PostvisitAnalysis mapRow(ResultSet rs, int rowNum) throws SQLException {
            return new PostvisitAnalysis(
                    UUID.fromString(rs.getString("analysis_id")),
                    UUID.fromString(rs.getString("operating_case_id")),
                    UUID.fromString(rs.getString("journey_id")),
                    UUID.fromString(rs.getString("previsit_report_id")),
                    rs.getString("outcome"),
                    rs.getString("follow_up_action"),
                    rs.getTimestamp("analyzed_at").toInstant());
        }
    }

    // ── JSON helpers ──

    static List<UUID> parseUuidList(String json) {
        if (json == null || json.isBlank() || "null".equals(json)) {
            return List.of();
        }
        String trimmed = json.trim();
        if (trimmed.startsWith("[")) trimmed = trimmed.substring(1);
        if (trimmed.endsWith("]")) trimmed = trimmed.substring(0, trimmed.length() - 1);
        if (trimmed.isBlank()) return List.of();
        return java.util.Arrays.stream(trimmed.split(","))
                .map(s -> s.trim().replace("\"", ""))
                .filter(s -> !s.isBlank())
                .map(UUID::fromString)
                .toList();
    }

    static String toJsonArray(List<UUID> uuids) {
        if (uuids == null || uuids.isEmpty()) return "[]";
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < uuids.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append("\"").append(uuids.get(i)).append("\"");
        }
        sb.append("]");
        return sb.toString();
    }
}
