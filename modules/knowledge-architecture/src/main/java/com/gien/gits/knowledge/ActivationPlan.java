package com.gien.gits.knowledge;

import java.util.List;

/**
 * 可重放激活计划（Replayable Activation Plan）领域模型，对应合同 CTR-PLAN-001
 * (specs/knowledge-architecture/schemas/activation-plan.schema.json)。
 *
 * <p>仅承载合同已定义的字段，不发明额外字段。</p>
 */
public record ActivationPlan(
        String schemaVersion,
        String planId,
        String taskId,
        String taskType,
        String routeMode,
        Versions versions,
        List<SelectedAsset> selectedAssets,
        List<String> semanticQueries,
        List<String> ruleChecks,
        List<String> skills,
        Context context,
        String permissionDecisionId,
        Trace trace) {

    public ActivationPlan {
        selectedAssets = orEmptyAssets(selectedAssets);
        semanticQueries = orEmpty(semanticQueries);
        ruleChecks = orEmpty(ruleChecks);
        skills = orEmpty(skills);
    }

    private static List<String> orEmpty(List<String> value) {
        return value == null ? List.of() : List.copyOf(value);
    }

    private static List<SelectedAsset> orEmptyAssets(List<SelectedAsset> value) {
        return value == null ? List.of() : List.copyOf(value);
    }

    public record Versions(
            String knowledgeMap,
            String routePolicy,
            String activationContract,
            String ontology) {}

    public record SelectedAsset(String assetId, String version, boolean required, Integer sequence) {}

    public record Context(Integer maxTokens, String trimPolicy) {}

    /**
     * 可重放追踪（CTR-PLAN-001 的 {@code trace}）。
     *
     * @param planHash          确定性计划哈希（可重放；**不含**环境相关字段）
     * @param createdAt         计划生成时刻
     * @param plannerVersion    规划器版本
     * @param ontologyEvidence  本体依据（版本 + 四类实体计数 + 来源），由规划器从
     *                          {@code OntologyPort} 快照填入；见
     *                          {@code specs/knowledge-architecture/schemas/activation-plan.schema.json}。
     *                          **不参与** {@code planHash} —— 其中含来源路径，属环境相关字段，
     *                          入哈希会破坏可重放性（本体版本已单独入哈希）。
     */
    public record Trace(
            String planHash,
            String createdAt,
            String plannerVersion,
            String ontologyEvidence) {

        /**
         * 兼容构造：仅用于**非运行时样本与既有测试替身**（黄金计划、下游 fabric 夹具）——
         * 它们不带本体依据。运行时计划一律由规划器填入，**不存在**缺依据的运行计划。
         */
        public Trace(String planHash, String createdAt, String plannerVersion) {
            this(planHash, createdAt, plannerVersion, null);
        }
    }
}
