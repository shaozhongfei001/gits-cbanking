package com.gien.gits.adapter.persistence;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.RecommendationAttempt;
import com.gien.gits.customerjourney.recommendation.RecommendationAttemptStatus;
import com.gien.gits.customerjourney.recommendation.RecommendationDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationFeedback;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;
import com.gien.gits.customerjourney.recommendation.ProductRecommendationRunStatus;

import org.flywaydb.core.Flyway;
import org.h2.Driver;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.SimpleDriverDataSource;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import javax.sql.DataSource;

/**
 * JdbcProductRecommendationRepository 集成测试（H2 MySQL 兼容模式 + Flyway V020）。
 *
 * <p>验证对 V020 五张表的读写：{@code product_recommendation_run /
 * product_recommendation_attempt / recommendation_proposal_version /
 * recommendation_human_decision / recommendation_feedback}，列名与迁移 SQL 一致。</p>
 */
class JdbcProductRecommendationRepositoryIT {

    private JdbcTemplate jdbc;
    private JdbcProductRecommendationRepository repository;

    @BeforeEach
    void setUp() {
        String dbName = "pr_repo_it_" + System.nanoTime();
        String jdbcUrl = "jdbc:h2:mem:" + dbName + ";MODE=MySQL;DB_CLOSE_DELAY=-1";
        DataSource dataSource = new SimpleDriverDataSource(new Driver(), jdbcUrl, "sa", "");
        jdbc = new JdbcTemplate(dataSource);
        Flyway.configure()
            .dataSource(dataSource)
            .locations("classpath:db/migration/h2")
            .load()
            .migrate();
        repository = new JdbcProductRecommendationRepository(jdbc, new ObjectMapper());
    }

    @Test
    void saveAndFindRunRoundTrips() {
        Instant asOf = Instant.parse("2026-08-31T09:00:00Z");
        ProductRecommendationRun run = new ProductRecommendationRun(
            "run-1", "CUST-1", "JNY-1", null,
            List.of("NEEDV-1", "NEEDV-2"), "补充流动资金与跨境结算方案",
            List.of("FINANCING", "SETTLEMENT"), asOf, "idem-1",
            ProductRecommendationRunStatus.AWAITING_HUMAN, "V1", "KERT-JOB-1",
            Map.of("evidenceBundleId", "EVB-1", "productKnowledgeSnapshotRef", "PKS-1"),
            Instant.parse("2026-08-31T08:00:00Z"), Instant.parse("2026-08-31T09:30:00Z"));

        repository.saveRun(run);

        Optional<ProductRecommendationRun> found = repository.findRunById("run-1");
        assertThat(found).isPresent();
        assertThat(found.get().runId()).isEqualTo("run-1");
        assertThat(found.get().customerId()).isEqualTo("CUST-1");
        assertThat(found.get().needVersionIds()).containsExactly("NEEDV-1", "NEEDV-2");
        assertThat(found.get().requestedProductDomains()).containsExactly("FINANCING", "SETTLEMENT");
        assertThat(found.get().asOf()).isEqualTo(asOf);
        assertThat(found.get().status()).isEqualTo(ProductRecommendationRunStatus.AWAITING_HUMAN);
        assertThat(found.get().currentVersionId()).isEqualTo("V1");
        assertThat(found.get().snapshotRefs()).containsEntry("evidenceBundleId", "EVB-1");
        assertThat(repository.findRunByIdempotencyKey("idem-1")).isPresent();
    }

    @Test
    void updateRunPersistsStateAndProposal() {
        repository.saveRun(new ProductRecommendationRun(
            "run-2", "CUST-2", "JNY-2", null, List.of(), "objective", List.of(),
            Instant.parse("2026-08-31T09:00:00Z"), "idem-2"));

        ProductRecommendationRun updated = repository.findRunById("run-2").orElseThrow()
            .transitionTo(ProductRecommendationRunStatus.CONTEXT_ASSEMBLING)
            .transitionTo(ProductRecommendationRunStatus.HARD_FILTERING)
            .transitionTo(ProductRecommendationRunStatus.MATCHING)
            .transitionTo(ProductRecommendationRunStatus.PROPOSAL_READY)
            .withProposal("V2", "KERT-JOB-2", Map.of("evidenceBundleId", "EVB-2"));

        repository.updateRun(updated);

        ProductRecommendationRun found = repository.findRunById("run-2").orElseThrow();
        assertThat(found.status()).isEqualTo(ProductRecommendationRunStatus.PROPOSAL_READY);
        assertThat(found.currentVersionId()).isEqualTo("V2");
        assertThat(found.kertJobRef()).isEqualTo("KERT-JOB-2");
    }

    @Test
    void duplicateIdempotencyKeyViolatesUniqueConstraint() {
        Instant asOf = Instant.parse("2026-08-31T09:00:00Z");
        repository.saveRun(new ProductRecommendationRun(
            "run-dup-1", "CUST-1", "JNY-1", null, List.of(), "objective", List.of(),
            asOf, "idem-dup"));

        ProductRecommendationRun duplicate = new ProductRecommendationRun(
            "run-dup-2", "CUST-1", "JNY-1", null, List.of(), "objective", List.of(),
            asOf, "idem-dup");

        // H2 V020 的 uk_prr_idem 唯一约束：并发同键第二次 saveRun 必须抛 DuplicateKeyException，
        // 供 ProductRecommendationApplicationService.createRun 的 catch 分支回读既有 run。
        assertThatThrownBy(() -> repository.saveRun(duplicate))
            .isInstanceOf(DuplicateKeyException.class);
    }

    @Test
    void saveAndFindAttempt() {
        repository.saveRun(new ProductRecommendationRun(
            "run-3", "CUST-3", "JNY-3", null, List.of(), "objective", List.of(),
            Instant.parse("2026-08-31T09:00:00Z"), "idem-3"));

        repository.saveAttempt(new RecommendationAttempt(
            "att-1", "run-3", "KERT-REQ-1",
            Instant.parse("2026-08-31T09:00:00Z"), Instant.parse("2026-08-31T09:00:30Z"),
            RecommendationAttemptStatus.SUCCEEDED, null, false));

        List<RecommendationAttempt> attempts = repository.findAttemptsByRun("run-3");
        assertThat(attempts).hasSize(1);
        assertThat(attempts.get(0).attemptId()).isEqualTo("att-1");
        assertThat(attempts.get(0).status()).isEqualTo(RecommendationAttemptStatus.SUCCEEDED);
        assertThat(attempts.get(0).kertRequestId()).isEqualTo("KERT-REQ-1");
    }

    @Test
    void saveAndFindVersionWithPayloadRoundTrip() {
        repository.saveRun(new ProductRecommendationRun(
            "run-4", "CUST-4", "JNY-4", null, List.of(), "objective", List.of(),
            Instant.parse("2026-08-31T09:00:00Z"), "idem-4"));

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("eligibilityResults", List.of(Map.of("productId", "P1", "eligibility", "ELIGIBLE")));
        payload.put("contentHash", "sha256:abc");

        repository.saveVersion(new RecommendationProposalVersion(
            "V4", "run-4", "TRACE-4", "EVB-4", "sha256:abc", payload, null));

        Optional<RecommendationProposalVersion> found = repository.findVersionById("V4");
        assertThat(found).isPresent();
        assertThat(found.get().contentHash()).isEqualTo("sha256:abc");
        assertThat(found.get().evidenceBundleId()).isEqualTo("EVB-4");
        assertThat(found.get().payload()).containsKey("eligibilityResults");
        assertThat(repository.findVersionsByRun("run-4")).hasSize(1);
    }

    @Test
    void saveAndFindDecisionWithModifications() {
        repository.saveRun(new ProductRecommendationRun(
            "run-5", "CUST-5", "JNY-5", null, List.of(), "objective", List.of(),
            Instant.parse("2026-08-31T09:00:00Z"), "idem-5",
            ProductRecommendationRunStatus.AWAITING_HUMAN, "V5", "KERT-JOB-5", Map.of(),
            Instant.now(), Instant.now()));

        List<Map<String, Object>> modifications = List.of(
            Map.of("kind", "REORDER_CANDIDATE", "targetPortfolioId", "PORT-1", "fromPosition", 0, "toPosition", 1));

        repository.saveDecision(new RecommendationHumanDecision(
            "dec-1", "HG-D01", "run-5", "V5", RecommendationDecision.MODIFY,
            modifications, "调整顺序", "RM-1", "RELATIONSHIP_MANAGER",
            Instant.parse("2026-08-31T10:00:00Z")));

        Optional<RecommendationHumanDecision> byId = repository.findDecisionById("dec-1");
        assertThat(byId).isPresent();
        assertThat(byId.get().decision()).isEqualTo(RecommendationDecision.MODIFY);
        assertThat(byId.get().modifications()).hasSize(1);
        assertThat(byId.get().modifications().get(0)).containsEntry("kind", "REORDER_CANDIDATE");

        assertThat(repository.findDecisionByProposalVersion("V5")).isPresent();
        assertThat(repository.findDecisionsByRun("run-5")).hasSize(1);
    }

    @Test
    void saveAndFindFeedbackWithNullableAdopted() {
        repository.saveRun(new ProductRecommendationRun(
            "run-6", "CUST-6", "JNY-6", null, List.of(), "objective", List.of(),
            Instant.parse("2026-08-31T09:00:00Z"), "idem-6"));

        repository.saveFeedback(new RecommendationFeedback(
            "fb-1", "run-6", null, "非目标客群", List.of("fitScore"), "OUTCOME-1",
            Instant.parse("2026-08-31T11:00:00Z")));

        List<RecommendationFeedback> feedback = repository.findFeedbackByRun("run-6");
        assertThat(feedback).hasSize(1);
        assertThat(feedback.get(0).feedbackId()).isEqualTo("fb-1");
        assertThat(feedback.get(0).adopted()).isNull();
        assertThat(feedback.get(0).modifiedFields()).containsExactly("fitScore");
    }
}
