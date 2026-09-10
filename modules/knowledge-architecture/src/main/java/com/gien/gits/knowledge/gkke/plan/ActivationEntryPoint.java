package com.gien.gits.knowledge.gkke.plan;

import com.gien.gits.knowledge.gkke.model.ActivationPlanRecord;
import com.gien.gits.knowledge.gkke.model.Budget;
import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.List;
import java.util.Objects;

/**
 * 双入口装配门面（CR-02 §4.4，验收 T05）。
 *
 * <p>同一任务可从两个<b>真正独立</b>的入口发起，二者入参类型不同、导航来源不同：
 * <ul>
 *   <li><b>Wiki 入口</b> {@link #fromWiki(WikiEntry)}：用户在知识地图/Wiki 页面点击“执行”，
 *       携带页面坐标与浏览来源 {@code wikiPage}；</li>
 *   <li><b>对象入口</b> {@link #fromObject(ObjectEntry)}：用户在业务对象卡片（如客户/产品）
 *       上发起，携带业务对象坐标 {@code businessObjectRef} 与入口锚点 {@code entryAnchor}。</li>
 * </ul>
 *
 * <p>两入口各自把“入口特有导航信息”剥离，只归一为同一个确定性 {@link PlanRequest}：
 * 入口来源（wikiPage / businessObjectRef / entryAnchor）<b>不进入</b>计划载荷。因此在相同
 * {@link TaskContext} + 相同地图版本 + 相同发布快照下，两入口产出的
 * {@link ActivationPlanRecord#planHash()} 必须逐字节相等（两个独立入口对象分别装配，
 * 不是同一 Java 对象哈希两次）。
 */
public final class ActivationEntryPoint {

    private final ActivationPlanner planner;

    public ActivationEntryPoint(ActivationPlanner planner) {
        this.planner = Objects.requireNonNull(planner, "planner must not be null");
    }

    /** Wiki 入口：从知识地图页面发起。 */
    public ActivationPlanRecord fromWiki(WikiEntry entry) {
        Objects.requireNonNull(entry, "entry must not be null");
        return planner.plan(toRequest(entry.taskContext(), entry.map(), entry.releaseId(),
                entry.coreVersion(), entry.catalogRevision(), entry.routePolicyVersion(),
                entry.permissionDecisionRef(), entry.queryRefs()));
    }

    /** 对象入口：从业务对象卡片携带地图引用发起。 */
    public ActivationPlanRecord fromObject(ObjectEntry entry) {
        Objects.requireNonNull(entry, "entry must not be null");
        return planner.plan(toRequest(entry.taskContext(), entry.map(), entry.releaseId(),
                entry.coreVersion(), entry.catalogRevision(), entry.routePolicyVersion(),
                entry.permissionDecisionRef(), entry.queryRefs()));
    }

    private PlanRequest toRequest(TaskContext ctx, KnowledgeMapRecord map, String releaseId,
                                  String coreVersion, Integer catalogRevision,
                                  String routePolicyVersion, String permissionDecisionRef,
                                  List<VersionRef> queryRefs) {
        String deterministicPlanId =
                ctx.taskId() + ":" + map.mapId() + ":" + map.version() + ":" + releaseId;
        return new PlanRequest(deterministicPlanId, ctx.taskId(), map, releaseId, coreVersion,
                catalogRevision, routePolicyVersion, ctx.purpose(), ctx.scope(), ctx.budget(),
                permissionDecisionRef, queryRefs == null ? List.of() : queryRefs);
    }

    /** 两入口共享的确定性任务上下文（T05 对拍的同一输入）。 */
    public record TaskContext(
            String taskId,
            String purpose,
            Scope scope,
            Budget budget) {

        public TaskContext {
            Objects.requireNonNull(taskId, "taskId must not be null");
            Objects.requireNonNull(purpose, "purpose must not be null");
            Objects.requireNonNull(scope, "scope must not be null");
            Objects.requireNonNull(budget, "budget must not be null");
        }
    }

    /** Wiki 入口入参（知识地图页面坐标 + 浏览来源；来源不进入计划载荷）。 */
    public record WikiEntry(
            TaskContext taskContext,
            KnowledgeMapRecord map,
            String releaseId,
            String coreVersion,
            Integer catalogRevision,
            String routePolicyVersion,
            String permissionDecisionRef,
            List<VersionRef> queryRefs,
            String wikiPage) {
    }

    /** 对象入口入参（业务对象坐标 + 锚点；来源不进入计划载荷）。 */
    public record ObjectEntry(
            TaskContext taskContext,
            KnowledgeMapRecord map,
            String releaseId,
            String coreVersion,
            Integer catalogRevision,
            String routePolicyVersion,
            String permissionDecisionRef,
            List<VersionRef> queryRefs,
            String businessObjectRef,
            String entryAnchor) {
    }
}
