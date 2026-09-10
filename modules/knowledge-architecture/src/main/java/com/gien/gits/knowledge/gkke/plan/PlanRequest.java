package com.gien.gits.knowledge.gkke.plan;

import com.gien.gits.knowledge.gkke.model.Budget;
import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.List;
import java.util.Objects;

/**
 * 计划装配的确定性内部请求（已剥离入口导航来源，CR-02 §4.4，验收 T05）。
 *
 * <p>Wiki 入口与对象入口都把各自特有的导航信息（wikiPage / businessObjectRef / entryAnchor）
 * 剥离，归一到同一个 {@code PlanRequest}。因此相同任务上下文 + 相同地图版本 + 相同发布快照
 * 必然得到相同计划载荷与 planHash，与从哪个入口发起无关。
 */
public record PlanRequest(
        String planId,
        String taskId,
        KnowledgeMapRecord map,
        String releaseId,
        String coreVersion,
        Integer catalogRevision,
        String routePolicyVersion,
        String purpose,
        Scope scope,
        Budget budget,
        String permissionDecisionRef,
        List<VersionRef> queryRefs) {

    public PlanRequest {
        Objects.requireNonNull(planId, "planId must not be null");
        Objects.requireNonNull(taskId, "taskId must not be null");
        Objects.requireNonNull(map, "map must not be null");
        Objects.requireNonNull(releaseId, "releaseId must not be null");
        Objects.requireNonNull(coreVersion, "coreVersion must not be null");
        Objects.requireNonNull(catalogRevision, "catalogRevision must not be null");
        Objects.requireNonNull(routePolicyVersion, "routePolicyVersion must not be null");
        Objects.requireNonNull(purpose, "purpose must not be null");
        Objects.requireNonNull(scope, "scope must not be null");
        Objects.requireNonNull(budget, "budget must not be null");
        queryRefs = queryRefs == null ? List.of() : List.copyOf(queryRefs);
    }
}
