package com.gien.gits.customerjourney.recommendation;

import java.time.Duration;
import java.time.Instant;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * 产品推荐业务运行（ProductRecommendationRun）—— 三段式决策的生命周期容器与权威业务状态机。
 *
 * <p>状态块：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO（WP4-1 权威 + FO-02 唯一归属合并）。</p>
 *
 * <p>权威依据：</p>
 * <ul>
 *   <li>{@code specs/product-recommendation/product-recommendation-run.schema.json}（CTR-PR-RUN-001）</li>
 *   <li>{@code docs/adr/ADR-PR-IDEMPOTENCY_CANDIDATE.md}（ADR-PR-008~011：幂等/重试/并发/过期）</li>
 *   <li>{@code ~/dev/Leibniz-KERT/docs/integration/DKWS_GITS_STATE_MAPPING_CANDIDATE.md} §3.1（权威状态机）</li>
 *   <li>{@code adapters/persistence-relational/.../V020__product_recommendation.sql}（五张表列）</li>
 * </ul>
 *
 * <p>FO-02 唯一归属合并：本类是产品推荐业务运行的唯一权威定义。原
 * {@code modules/operational-ontology/.../domain/ProductRecommendationRun.java}（WP4-2 重复定义）已删除，
 * 其被 service/repository 实际消费的持久化字段（{@code needVersionIds / requestedProductDomains /
 * kertJobRef / snapshotRefs}）合并入本类；业务状态机以 WP4-1 的 §3.1 权威迁移表为准（19 条合法迁移）。</p>
 *
 * <p>设计要点：</p>
 * <ul>
 *   <li>不可变（record）：每次迁移返回新实例，不原地改写。</li>
 *   <li>标识字段为字符串（对齐 schema 与 V020 迁移的 {@code CHAR(36)}），非 {@code UUID} 强类型。</li>
 *   <li>状态机由 GITS Domain 权威裁决：合法迁移放行，非法迁移抛 {@link IllegalStateException}。</li>
 *   <li>{@link ProductRecommendationRunStatus#FAILED_CLOSED} 为终态（无出边）；KERT 不可达时禁止本地回退。</li>
 *   <li>幂等键 {@code idempotencyKey} 与幂等范围成分（customerId / journeyId·operatingCaseId / recommendationObjective / asOf）落为本域字段。</li>
 *   <li>{@code currentVersionId} 指向当前不可变方案版本（{@link RecommendationProposalVersion#versionId()}），用于人工决定乐观并发校验（INV-06）。</li>
 * </ul>
 */
public record ProductRecommendationRun(
        String runId,
        String customerId,
        String journeyId,
        String operatingCaseId,
        List<String> needVersionIds,
        String recommendationObjective,
        List<String> requestedProductDomains,
        Instant asOf,
        String idempotencyKey,
        ProductRecommendationRunStatus status,
        String currentVersionId,
        String kertJobRef,
        Map<String, String> snapshotRefs,
        Instant createdAt,
        Instant updatedAt) {

    /**
     * 合法迁移表（GITS 权威，忠实复刻状态映射文档 §3.1 状态机图 + 补充语义）。
     *
     * <p>终态（APPROVED/MODIFIED/REJECTED/FAILED_CLOSED）与 STALE_REQUIRES_RERUN 均无出边；
     * 其中 STALE_REQUIRES_RERUN 不是“关闭”终态，而是“旧版本保留、要求新建 run”。
     * {@code REQUESTED} 的唯一后继是 {@code CONTEXT_ASSEMBLING}；失败/暂缓必须先从
     * {@code REQUESTED} 进入 {@code CONTEXT_ASSEMBLING}，再从该态转入 {@code HELD / FAILED_CLOSED}。</p>
     */
    private static final Map<ProductRecommendationRunStatus, Set<ProductRecommendationRunStatus>> ALLOWED_TRANSITIONS =
            new EnumMap<>(ProductRecommendationRunStatus.class);

    static {
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.REQUESTED,
                EnumSet.of(ProductRecommendationRunStatus.CONTEXT_ASSEMBLING));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.CONTEXT_ASSEMBLING,
                EnumSet.of(ProductRecommendationRunStatus.HARD_FILTERING,
                        ProductRecommendationRunStatus.HELD,
                        ProductRecommendationRunStatus.FAILED_CLOSED));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.HARD_FILTERING,
                EnumSet.of(ProductRecommendationRunStatus.MATCHING,
                        ProductRecommendationRunStatus.HELD,
                        ProductRecommendationRunStatus.FAILED_CLOSED));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.MATCHING,
                EnumSet.of(ProductRecommendationRunStatus.PROPOSAL_READY,
                        ProductRecommendationRunStatus.HELD,
                        ProductRecommendationRunStatus.FAILED_CLOSED));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.PROPOSAL_READY,
                EnumSet.of(ProductRecommendationRunStatus.AWAITING_HUMAN,
                        ProductRecommendationRunStatus.STALE_REQUIRES_RERUN));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.AWAITING_HUMAN,
                EnumSet.of(ProductRecommendationRunStatus.APPROVED,
                        ProductRecommendationRunStatus.MODIFIED,
                        ProductRecommendationRunStatus.REJECTED,
                        ProductRecommendationRunStatus.HELD,
                        ProductRecommendationRunStatus.STALE_REQUIRES_RERUN));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.APPROVED,
                EnumSet.noneOf(ProductRecommendationRunStatus.class));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.MODIFIED,
                EnumSet.noneOf(ProductRecommendationRunStatus.class));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.REJECTED,
                EnumSet.noneOf(ProductRecommendationRunStatus.class));
        // HELD 可恢复：补数据后回到 CONTEXT_ASSEMBLING 重跑管线；人工暂缓后回到 AWAITING_HUMAN 重开闸门。
        // 两条恢复路径的合流与否为 CANDIDATE 边界（状态映射文档 §5.5 已登记为 Owner 待确认）。
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.HELD,
                EnumSet.of(ProductRecommendationRunStatus.CONTEXT_ASSEMBLING,
                        ProductRecommendationRunStatus.AWAITING_HUMAN));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.STALE_REQUIRES_RERUN,
                EnumSet.noneOf(ProductRecommendationRunStatus.class));
        ALLOWED_TRANSITIONS.put(ProductRecommendationRunStatus.FAILED_CLOSED,
                EnumSet.noneOf(ProductRecommendationRunStatus.class));
    }

    public ProductRecommendationRun {
        Objects.requireNonNull(runId, "runId");
        customerId = requireText(customerId, "customerId");
        if (isNullOrBlank(journeyId) && isNullOrBlank(operatingCaseId)) {
            throw new IllegalArgumentException("journeyId or operatingCaseId must be present");
        }
        recommendationObjective = requireText(recommendationObjective, "recommendationObjective");
        Objects.requireNonNull(asOf, "asOf");
        idempotencyKey = requireText(idempotencyKey, "idempotencyKey");
        Objects.requireNonNull(status, "status");
        needVersionIds = List.copyOf(needVersionIds != null ? needVersionIds : List.of());
        requestedProductDomains = List.copyOf(requestedProductDomains != null ? requestedProductDomains : List.of());
        snapshotRefs = snapshotRefs == null ? Map.of() : Map.copyOf(snapshotRefs);
        Objects.requireNonNull(createdAt, "createdAt");
        // currentVersionId、kertJobRef、updatedAt 允许为空（尚无版本 / 尚未提交 KERT / 未更新）。
    }

    /**
     * 新建 run 的便捷构造：{@code status} = {@link ProductRecommendationRunStatus#REQUESTED}，
     * {@code createdAt} = {@code updatedAt} = now，无当前版本、无 KERT 引用、无快照。
     */
    public ProductRecommendationRun(
            String runId,
            String customerId,
            String journeyId,
            String operatingCaseId,
            List<String> needVersionIds,
            String recommendationObjective,
            List<String> requestedProductDomains,
            Instant asOf,
            String idempotencyKey) {
        this(runId, customerId, journeyId, operatingCaseId, needVersionIds, recommendationObjective,
                requestedProductDomains, asOf, idempotencyKey, ProductRecommendationRunStatus.REQUESTED,
                null, null, Map.of(), Instant.now(), Instant.now());
    }

    /**
     * 便捷工厂：以 {@link ProductRecommendationRunStatus#REQUESTED} 初始状态创建运行（无 need/domain 维度）。
     */
    public static ProductRecommendationRun create(String runId, String customerId, String journeyId,
                                                  String operatingCaseId, String recommendationObjective,
                                                  Instant asOf, String idempotencyKey) {
        Instant now = Instant.now();
        return new ProductRecommendationRun(runId, customerId, journeyId, operatingCaseId,
                List.of(), recommendationObjective, List.of(), asOf, idempotencyKey,
                ProductRecommendationRunStatus.REQUESTED, null, null, Map.of(), now, now);
    }

    /**
     * 判断 {@code from → target} 是否合法。
     */
    public static boolean canTransition(ProductRecommendationRunStatus from, ProductRecommendationRunStatus target) {
        Objects.requireNonNull(from, "from");
        Objects.requireNonNull(target, "target");
        Set<ProductRecommendationRunStatus> allowed = ALLOWED_TRANSITIONS.get(from);
        return allowed != null && allowed.contains(target);
    }

    /**
     * 实例级迁移判断：当前状态到 {@code target} 是否合法。
     */
    public boolean canTransitionTo(ProductRecommendationRunStatus target) {
        return canTransition(status, target);
    }

    /**
     * 执行一次状态迁移：合法迁移返回新实例（updatedAt 刷新为 now），非法迁移抛 {@link IllegalStateException}。
     */
    public ProductRecommendationRun transitionTo(ProductRecommendationRunStatus target) {
        Objects.requireNonNull(target, "target");
        if (!canTransitionTo(target)) {
            throw new IllegalStateException(
                    "Invalid transition from " + status + " to " + target + " for run " + runId);
        }
        return withStatus(target, Instant.now());
    }

    /**
     * 挂接当前不可变方案版本（含 KERT 作业引用与快照引用），状态保持不变（{@code updatedAt} = now）。
     */
    public ProductRecommendationRun withProposal(String versionId, String kertJobRef,
                                                  Map<String, String> snapshotRefs) {
        String normalized = requireText(versionId, "versionId");
        return new ProductRecommendationRun(
                runId, customerId, journeyId, operatingCaseId, needVersionIds,
                recommendationObjective, requestedProductDomains, asOf, idempotencyKey,
                status, normalized, kertJobRef,
                snapshotRefs == null ? Map.of() : Map.copyOf(snapshotRefs),
                createdAt, Instant.now());
    }

    /**
     * 经领域对象落人工决定：{@code APPROVE -> APPROVED}、{@code MODIFY -> MODIFIED}、
     * {@code REJECT -> REJECTED}、{@code HOLD -> HELD}。
     */
    public ProductRecommendationRun applyDecision(RecommendationDecision decision) {
        Objects.requireNonNull(decision, "decision");
        ProductRecommendationRunStatus target = switch (decision) {
            case APPROVE -> ProductRecommendationRunStatus.APPROVED;
            case MODIFY -> ProductRecommendationRunStatus.MODIFIED;
            case REJECT -> ProductRecommendationRunStatus.REJECTED;
            case HOLD -> ProductRecommendationRunStatus.HELD;
        };
        return transitionTo(target);
    }

    /**
     * 过期判断（ADR-PR-011）：仅 {@link ProductRecommendationRunStatus#PROPOSAL_READY} 可被判定过期；
     * 当“方案就绪时点 + 有效期”不晚于 now 时迁至 {@link ProductRecommendationRunStatus#STALE_REQUIRES_RERUN}，
     * 否则原样返回（未过期）。
     *
     * <p>方案就绪时点取 {@code updatedAt}（缺失时回退 {@code createdAt}）。STALE 不自动删除旧版本。</p>
     */
    public ProductRecommendationRun markStaleIfExpired(Instant now, Duration validityPeriod) {
        Objects.requireNonNull(now, "now");
        Objects.requireNonNull(validityPeriod, "validityPeriod");
        if (validityPeriod.isZero() || validityPeriod.isNegative()) {
            throw new IllegalArgumentException("validityPeriod must be positive");
        }
        if (status != ProductRecommendationRunStatus.PROPOSAL_READY) {
            throw new IllegalStateException(
                    "Only PROPOSAL_READY runs can be marked stale, but was: " + status);
        }
        Instant proposalAt = updatedAt != null ? updatedAt : createdAt;
        if (!now.isBefore(proposalAt.plus(validityPeriod))) {
            return transitionTo(ProductRecommendationRunStatus.STALE_REQUIRES_RERUN);
        }
        return this;
    }

    /**
     * 人工决定（乐观并发校验，INV-06 / ADR-PR-010）。
     *
     * <p>决策值 {@code decision} 必须是四个决定结果状态之一
     * （APPROVED / MODIFIED / REJECTED / HELD），对应契约 {@code RecommendationDecision} 的
     * APPROVE / MODIFY / REJECT / HOLD（CANDIDATE 边界：本域以运行状态承载决定结果，
     * 独立的 {@code RecommendationDecision} 值对象与 {@link #applyDecision} 并存，
     * 映射口径见契约 README §1）。</p>
     *
     * <p>并发校验：{@code proposalVersionId} 必须等于 {@link #currentVersionId()}；不相等即视为过期提交，
     * 抛 {@link StaleProposalVersionException}（适配层映射 HTTP 409 Conflict），不得覆盖先提交者的决定。</p>
     *
     * @param proposalVersionId 决定所指向的方案版本（等价 If-Match/ETag 乐观锁）
     * @param decision          决定结果状态（APPROVED / MODIFIED / REJECTED / HELD）
     */
    public ProductRecommendationRun decide(String proposalVersionId, ProductRecommendationRunStatus decision) {
        Objects.requireNonNull(proposalVersionId, "proposalVersionId");
        Objects.requireNonNull(decision, "decision");
        if (!isDecisionOutcome(decision)) {
            throw new IllegalArgumentException(
                    "decision must be one of APPROVED/MODIFIED/REJECTED/HELD, but was: " + decision);
        }
        if (currentVersionId == null || !currentVersionId.equals(proposalVersionId)) {
            throw new StaleProposalVersionException(
                    "Stale proposal version for run " + runId + ": expected " + currentVersionId
                            + " but decision referenced " + proposalVersionId);
        }
        return transitionTo(decision);
    }

    /**
     * 固化当前不可变方案版本引用（不可变更新，返回新实例，{@code updatedAt} 保持不变）。
     */
    public ProductRecommendationRun withCurrentVersionId(String versionId) {
        String normalized = requireText(versionId, "versionId");
        return new ProductRecommendationRun(runId, customerId, journeyId, operatingCaseId,
                needVersionIds, recommendationObjective, requestedProductDomains, asOf, idempotencyKey,
                status, normalized, kertJobRef, snapshotRefs, createdAt, updatedAt);
    }

    private ProductRecommendationRun withStatus(ProductRecommendationRunStatus newStatus, Instant newUpdatedAt) {
        return new ProductRecommendationRun(runId, customerId, journeyId, operatingCaseId,
                needVersionIds, recommendationObjective, requestedProductDomains, asOf, idempotencyKey,
                newStatus, currentVersionId, kertJobRef, snapshotRefs, createdAt, newUpdatedAt);
    }

    private static boolean isDecisionOutcome(ProductRecommendationRunStatus value) {
        return value == ProductRecommendationRunStatus.APPROVED
                || value == ProductRecommendationRunStatus.MODIFIED
                || value == ProductRecommendationRunStatus.REJECTED
                || value == ProductRecommendationRunStatus.HELD;
    }

    private static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(field + " must not be blank");
        }
        return value;
    }

    private static boolean isNullOrBlank(String value) {
        return value == null || value.isBlank();
    }

    /**
     * 过期提交（并发冲突）异常：决定所引用的方案版本已非当前版本，等价 HTTP 409 Conflict。
     * 继承 {@link IllegalStateException} 便于统一按“非法状态操作”兜底，但语义可独立区分。
     */
    public static final class StaleProposalVersionException extends IllegalStateException {
        public StaleProposalVersionException(String message) {
            super(message);
        }
    }
}
