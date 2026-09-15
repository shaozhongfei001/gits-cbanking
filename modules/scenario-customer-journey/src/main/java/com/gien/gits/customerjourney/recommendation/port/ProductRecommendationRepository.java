package com.gien.gits.customerjourney.recommendation.port;

import com.gien.gits.customerjourney.recommendation.ProductRecommendationRun;
import com.gien.gits.customerjourney.recommendation.RecommendationAttempt;
import com.gien.gits.customerjourney.recommendation.RecommendationFeedback;
import com.gien.gits.customerjourney.recommendation.RecommendationHumanDecision;
import com.gien.gits.customerjourney.recommendation.RecommendationProposalVersion;

import java.util.List;
import java.util.Optional;

/**
 * 产品推荐仓储端口（读写 V020 五张表：
 * {@code product_recommendation_run / product_recommendation_attempt /
 * recommendation_proposal_version / recommendation_human_decision /
 * recommendation_feedback}）。
 *
 * <p>FO-02 唯一归属合并：本端口随领域模型一并归属
 * {@code modules/scenario-customer-journey}（原 operational-ontology 版本已删除）。</p>
 *
 * <p>状态 CANDIDATE / FROZEN=NO / IMPLEMENTED=NO。</p>
 */
public interface ProductRecommendationRepository {

    // ── run ─────────────────────────────────────────────────────────────
    void saveRun(ProductRecommendationRun run);

    void updateRun(ProductRecommendationRun run);

    Optional<ProductRecommendationRun> findRunById(String runId);

    Optional<ProductRecommendationRun> findRunByIdempotencyKey(String idempotencyKey);

    // ── attempt ─────────────────────────────────────────────────────────
    void saveAttempt(RecommendationAttempt attempt);

    List<RecommendationAttempt> findAttemptsByRun(String runId);

    // ── proposal version ───────────────────────────────────────────────
    void saveVersion(RecommendationProposalVersion version);

    Optional<RecommendationProposalVersion> findVersionById(String versionId);

    List<RecommendationProposalVersion> findVersionsByRun(String runId);

    // ── human decision ─────────────────────────────────────────────────
    void saveDecision(RecommendationHumanDecision decision);

    Optional<RecommendationHumanDecision> findDecisionById(String decisionId);

    Optional<RecommendationHumanDecision> findDecisionByProposalVersion(String proposalVersionId);

    List<RecommendationHumanDecision> findDecisionsByRun(String runId);

    // ── feedback ───────────────────────────────────────────────────────
    void saveFeedback(RecommendationFeedback feedback);

    List<RecommendationFeedback> findFeedbackByRun(String runId);
}
