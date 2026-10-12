package com.gien.gits.customerjourney.recommendation;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.junit.jupiter.api.Test;

/**
 * FO-02 唯一归属合并后：标识字段对齐 schema/V020 迁移为字符串（CHAR(36)），
 * 原 WP4-1 的 {@code UUID} 字面量机械替换为 {@code UUID.randomUUID().toString()}；
 * 状态机语义（19 条合法迁移 / 终态无出边 / 过期 / 决定并发）保持不变。
 */
class ProductRecommendationRunTest {

    // 全部 19 条合法迁移（忠实复刻状态映射文档 §3.1 状态机图 + 补充语义）。
    private static final ProductRecommendationRunStatus[][] LEGAL_TRANSITIONS = {
            {ProductRecommendationRunStatus.REQUESTED, ProductRecommendationRunStatus.CONTEXT_ASSEMBLING},
            {ProductRecommendationRunStatus.CONTEXT_ASSEMBLING, ProductRecommendationRunStatus.HARD_FILTERING},
            {ProductRecommendationRunStatus.CONTEXT_ASSEMBLING, ProductRecommendationRunStatus.HELD},
            {ProductRecommendationRunStatus.CONTEXT_ASSEMBLING, ProductRecommendationRunStatus.FAILED_CLOSED},
            {ProductRecommendationRunStatus.HARD_FILTERING, ProductRecommendationRunStatus.MATCHING},
            {ProductRecommendationRunStatus.HARD_FILTERING, ProductRecommendationRunStatus.HELD},
            {ProductRecommendationRunStatus.HARD_FILTERING, ProductRecommendationRunStatus.FAILED_CLOSED},
            {ProductRecommendationRunStatus.MATCHING, ProductRecommendationRunStatus.PROPOSAL_READY},
            {ProductRecommendationRunStatus.MATCHING, ProductRecommendationRunStatus.HELD},
            {ProductRecommendationRunStatus.MATCHING, ProductRecommendationRunStatus.FAILED_CLOSED},
            {ProductRecommendationRunStatus.PROPOSAL_READY, ProductRecommendationRunStatus.AWAITING_HUMAN},
            {ProductRecommendationRunStatus.PROPOSAL_READY, ProductRecommendationRunStatus.STALE_REQUIRES_RERUN},
            {ProductRecommendationRunStatus.AWAITING_HUMAN, ProductRecommendationRunStatus.APPROVED},
            {ProductRecommendationRunStatus.AWAITING_HUMAN, ProductRecommendationRunStatus.MODIFIED},
            {ProductRecommendationRunStatus.AWAITING_HUMAN, ProductRecommendationRunStatus.REJECTED},
            {ProductRecommendationRunStatus.AWAITING_HUMAN, ProductRecommendationRunStatus.HELD},
            {ProductRecommendationRunStatus.AWAITING_HUMAN, ProductRecommendationRunStatus.STALE_REQUIRES_RERUN},
            {ProductRecommendationRunStatus.HELD, ProductRecommendationRunStatus.CONTEXT_ASSEMBLING},
            {ProductRecommendationRunStatus.HELD, ProductRecommendationRunStatus.AWAITING_HUMAN},
    };

    private ProductRecommendationRun runAt(ProductRecommendationRunStatus status, String currentVersionId) {
        Instant now = Instant.now();
        return new ProductRecommendationRun(UUID.randomUUID().toString(), "CUST-001",
                UUID.randomUUID().toString(), UUID.randomUUID().toString(),
                List.of(), "推荐跨境结算与汇率避险方案", List.of(), now, "IDEM-001",
                status, currentVersionId, null, Map.of(), now, now);
    }

    // ── 枚举 ────────────────────────────────────────────────────

    @Test
    void runStatusHasExactlyTwelveValues() {
        assertEquals(12, ProductRecommendationRunStatus.values().length);
        for (String name : new String[]{"REQUESTED", "CONTEXT_ASSEMBLING", "HARD_FILTERING",
                "MATCHING", "PROPOSAL_READY", "AWAITING_HUMAN", "APPROVED", "MODIFIED",
                "REJECTED", "HELD", "STALE_REQUIRES_RERUN", "FAILED_CLOSED"}) {
            assertEquals(name, ProductRecommendationRunStatus.valueOf(name).name());
        }
    }

    @Test
    void stageHasExactlyThreeValues() {
        assertEquals(3, RecommendationStage.values().length);
        assertEquals(RecommendationStage.HARD_FILTERING, RecommendationStage.valueOf("HARD_FILTERING"));
        assertEquals(RecommendationStage.MATCHING, RecommendationStage.valueOf("MATCHING"));
        assertEquals(RecommendationStage.HUMAN_DECISION, RecommendationStage.valueOf("HUMAN_DECISION"));
    }

    // ── 全部合法迁移 ─────────────────────────────────────────────

    @Test
    void allLegalTransitionsAreAccepted() {
        for (ProductRecommendationRunStatus[] edge : LEGAL_TRANSITIONS) {
            ProductRecommendationRun from = runAt(edge[0], null);
            assertTrue(from.canTransitionTo(edge[1]),
                    "expected legal: " + edge[0] + " -> " + edge[1]);
            ProductRecommendationRun to = from.transitionTo(edge[1]);
            assertEquals(edge[1], to.status(), "expected status after " + edge[0] + " -> " + edge[1]);
        }
    }

    // ── 非法迁移拒绝 ─────────────────────────────────────────────

    @Test
    void illegalTransitionsAreRejected() {
        // 跳过中间阶段（跨段）
        assertThrows(IllegalStateException.class, () ->
                runAt(ProductRecommendationRunStatus.REQUESTED, null)
                        .transitionTo(ProductRecommendationRunStatus.MATCHING));
        // 回退
        assertThrows(IllegalStateException.class, () ->
                runAt(ProductRecommendationRunStatus.AWAITING_HUMAN, null)
                        .transitionTo(ProductRecommendationRunStatus.REQUESTED));
        // 未就绪不可直接决定
        assertThrows(IllegalStateException.class, () ->
                runAt(ProductRecommendationRunStatus.PROPOSAL_READY, null)
                        .transitionTo(ProductRecommendationRunStatus.APPROVED));
        // 终态无出边
        for (ProductRecommendationRunStatus terminal : new ProductRecommendationRunStatus[]{
                ProductRecommendationRunStatus.APPROVED,
                ProductRecommendationRunStatus.MODIFIED,
                ProductRecommendationRunStatus.REJECTED,
                ProductRecommendationRunStatus.STALE_REQUIRES_RERUN,
                ProductRecommendationRunStatus.FAILED_CLOSED}) {
            for (ProductRecommendationRunStatus target : ProductRecommendationRunStatus.values()) {
                assertFalse(ProductRecommendationRun.canTransition(terminal, target),
                        "terminal " + terminal + " must not allow -> " + target);
            }
        }
    }

    @Test
    void failedClosedIsTerminal() {
        ProductRecommendationRun failed = runAt(ProductRecommendationRunStatus.FAILED_CLOSED, null);
        for (ProductRecommendationRunStatus target : ProductRecommendationRunStatus.values()) {
            assertThrows(IllegalStateException.class, () -> failed.transitionTo(target),
                    "FAILED_CLOSED must reject -> " + target);
        }
    }

    // ── 过期 → STALE ────────────────────────────────────────────

    @Test
    void proposalReadyBecomesStaleAfterValidityExpires() {
        Instant createdAt = Instant.now().minus(Duration.ofHours(10));
        Instant proposalReadyAt = Instant.now().minus(Duration.ofHours(5));
        ProductRecommendationRun run = new ProductRecommendationRun(UUID.randomUUID().toString(), "CUST-001",
                UUID.randomUUID().toString(), UUID.randomUUID().toString(),
                List.of(), "推荐跨境结算与汇率避险方案", List.of(),
                Instant.now().minus(Duration.ofHours(10)), "IDEM-001",
                ProductRecommendationRunStatus.PROPOSAL_READY, "v1", null, Map.of(), createdAt, proposalReadyAt);

        ProductRecommendationRun stale = run.markStaleIfExpired(Instant.now(), Duration.ofHours(1));

        assertEquals(ProductRecommendationRunStatus.STALE_REQUIRES_RERUN, stale.status());
        assertEquals("v1", stale.currentVersionId());
    }

    @Test
    void proposalReadyNotStaleBeforeValidityExpires() {
        Instant proposalReadyAt = Instant.now();
        ProductRecommendationRun run = new ProductRecommendationRun(UUID.randomUUID().toString(), "CUST-001",
                UUID.randomUUID().toString(), UUID.randomUUID().toString(),
                List.of(), "推荐跨境结算与汇率避险方案", List.of(),
                Instant.now(), "IDEM-001",
                ProductRecommendationRunStatus.PROPOSAL_READY, "v1", null, Map.of(),
                proposalReadyAt, proposalReadyAt);

        ProductRecommendationRun unchanged = run.markStaleIfExpired(Instant.now(), Duration.ofHours(1));

        assertSame(run, unchanged);
        assertEquals(ProductRecommendationRunStatus.PROPOSAL_READY, unchanged.status());
    }

    @Test
    void markStaleRejectsNonProposalReadyState() {
        assertThrows(IllegalStateException.class, () ->
                runAt(ProductRecommendationRunStatus.AWAITING_HUMAN, "v1")
                        .markStaleIfExpired(Instant.now(), Duration.ofHours(1)));
    }

    // ── 决策并发版本字段（INV-06）───────────────────────────────

    @Test
    void decisionWithCurrentVersionSucceeds() {
        ProductRecommendationRun awaiting = runAt(ProductRecommendationRunStatus.AWAITING_HUMAN, "v1");
        ProductRecommendationRun approved = awaiting.decide("v1", ProductRecommendationRunStatus.APPROVED);
        assertEquals(ProductRecommendationRunStatus.APPROVED, approved.status());
    }

    @Test
    void decisionWithStaleVersionIsRejected() {
        ProductRecommendationRun awaiting = runAt(ProductRecommendationRunStatus.AWAITING_HUMAN, "v2");
        assertThrows(ProductRecommendationRun.StaleProposalVersionException.class,
                () -> awaiting.decide("v1", ProductRecommendationRunStatus.APPROVED));
    }

    @Test
    void decisionWithoutAnyVersionIsRejected() {
        ProductRecommendationRun awaiting = runAt(ProductRecommendationRunStatus.AWAITING_HUMAN, null);
        assertThrows(ProductRecommendationRun.StaleProposalVersionException.class,
                () -> awaiting.decide("v1", ProductRecommendationRunStatus.APPROVED));
    }

    @Test
    void decisionRejectsNonDecisionStatus() {
        ProductRecommendationRun awaiting = runAt(ProductRecommendationRunStatus.AWAITING_HUMAN, "v1");
        assertThrows(IllegalArgumentException.class,
                () -> awaiting.decide("v1", ProductRecommendationRunStatus.MATCHING));
    }

    // ── 幂等键 / currentVersionId / 工厂 ─────────────────────────

    @Test
    void createFactoryProducesRequestedRunWithIdempotencyKey() {
        String runId = UUID.randomUUID().toString();
        String journeyId = UUID.randomUUID().toString();
        String caseId = UUID.randomUUID().toString();
        Instant asOf = Instant.now();

        ProductRecommendationRun run = ProductRecommendationRun.create(runId, "CUST-001", journeyId,
                caseId, "推荐跨境结算与汇率避险方案", asOf, "IDEM-001");

        assertEquals(runId, run.runId());
        assertEquals("CUST-001", run.customerId());
        assertEquals(journeyId, run.journeyId());
        assertEquals(caseId, run.operatingCaseId());
        assertEquals(asOf, run.asOf());
        assertEquals("IDEM-001", run.idempotencyKey());
        assertEquals(ProductRecommendationRunStatus.REQUESTED, run.status());
        assertNull(run.currentVersionId());
        assertNotNull(run.createdAt());
    }

    @Test
    void runRejectsMissingJourneyAndOperatingCase() {
        Instant now = Instant.now();
        assertThrows(IllegalArgumentException.class, () -> new ProductRecommendationRun(
                UUID.randomUUID().toString(), "CUST-001", null, null,
                List.of(), "推荐跨境结算与汇率避险方案", List.of(),
                now, "IDEM-001", ProductRecommendationRunStatus.REQUESTED, null, null, Map.of(), now, now));
    }

    @Test
    void runRejectsBlankIdempotencyKey() {
        Instant now = Instant.now();
        assertThrows(IllegalArgumentException.class, () -> new ProductRecommendationRun(
                UUID.randomUUID().toString(), "CUST-001", UUID.randomUUID().toString(),
                UUID.randomUUID().toString(), List.of(), "推荐跨境结算与汇率避险方案", List.of(),
                now, "  ", ProductRecommendationRunStatus.REQUESTED, null, null, Map.of(), now, now));
    }

    @Test
    void withCurrentVersionIdReturnsNewInstancePreservingIdentity() {
        ProductRecommendationRun ready = runAt(ProductRecommendationRunStatus.PROPOSAL_READY, null);
        ProductRecommendationRun versioned = ready.withCurrentVersionId("v1");

        assertEquals("v1", versioned.currentVersionId());
        assertEquals(ProductRecommendationRunStatus.PROPOSAL_READY, versioned.status());
        assertEquals(ready.runId(), versioned.runId());
        assertEquals(ready.idempotencyKey(), versioned.idempotencyKey());
        assertNull(ready.currentVersionId());
    }

    // ── 完整快乐路径 ─────────────────────────────────────────────

    @Test
    void fullHappyPathFromRequestedToApproved() {
        String runId = UUID.randomUUID().toString();
        Instant asOf = Instant.now();
        ProductRecommendationRun run = ProductRecommendationRun.create(runId, "CUST-001",
                UUID.randomUUID().toString(), UUID.randomUUID().toString(),
                "推荐跨境结算与汇率避险方案", asOf, "IDEM-001");

        run = run.transitionTo(ProductRecommendationRunStatus.CONTEXT_ASSEMBLING);
        run = run.transitionTo(ProductRecommendationRunStatus.HARD_FILTERING);
        run = run.transitionTo(ProductRecommendationRunStatus.MATCHING);
        run = run.transitionTo(ProductRecommendationRunStatus.PROPOSAL_READY);
        run = run.withCurrentVersionId("v1");
        run = run.transitionTo(ProductRecommendationRunStatus.AWAITING_HUMAN);
        run = run.decide("v1", ProductRecommendationRunStatus.APPROVED);

        assertEquals(runId, run.runId());
        assertEquals(ProductRecommendationRunStatus.APPROVED, run.status());
        assertEquals("v1", run.currentVersionId());
    }

    // ── 方案版本（不可变 + contentHash + supersededBy）───────────

    @Test
    void proposalVersionIsImmutableAndSupersedesCorrectly() {
        String runId = UUID.randomUUID().toString();
        Instant createdAt = Instant.now();
        RecommendationProposalVersion v1 = RecommendationProposalVersion.create(
                "v1", runId, "result-1", "evidence-1", "hash-1", createdAt);

        assertEquals("v1", v1.versionId());
        assertEquals(runId, v1.runId());
        assertEquals("hash-1", v1.contentHash());
        assertNull(v1.supersededBy());
        assertFalse(v1.isSuperseded());

        RecommendationProposalVersion superseded = v1.withSupersededBy("v2");
        // 原实例不可变
        assertNull(v1.supersededBy());
        assertFalse(v1.isSuperseded());
        // 新实例携带 supersededBy 指针
        assertEquals("v2", superseded.supersededBy());
        assertTrue(superseded.isSuperseded());
        assertEquals("hash-1", superseded.contentHash());
        assertEquals(createdAt, superseded.createdAt());
    }

    @Test
    void proposalVersionRejectsSelfSupersede() {
        RecommendationProposalVersion v1 = RecommendationProposalVersion.create(
                "v1", UUID.randomUUID().toString(), "result-1", "evidence-1", "hash-1", Instant.now());
        assertThrows(IllegalArgumentException.class, () -> v1.withSupersededBy("v1"));
    }

    @Test
    void proposalVersionRejectsBlankContentHash() {
        assertThrows(IllegalArgumentException.class, () -> RecommendationProposalVersion.create(
                "v1", UUID.randomUUID().toString(), "result-1", "evidence-1", "  ", Instant.now()));
    }
}
