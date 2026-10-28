package com.gien.gits.knowledge.gkke.plan;

import com.gien.gits.knowledge.gkke.model.ActivationPlanRecord;
import com.gien.gits.knowledge.gkke.model.AssetVersionRecord;
import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.MapNode;
import com.gien.gits.knowledge.gkke.model.PlanStep;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import com.gien.gits.knowledge.gkke.registry.AssetNotAvailableException;
import com.gien.gits.knowledge.gkke.registry.AssetNotFoundException;
import com.gien.gits.knowledge.gkke.registry.AssetRegistryPort;
import com.gien.gits.knowledge.gkke.registry.CapabilityRegistry;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 激活计划装配器（CR-02 §4.4，验收 T05/T06）。
 *
 * <p>基于知识地图与发布快照，把入口任务节点展开为确定性的 {@link ActivationPlanRecord}。
 * <b>硬拒绝语义（T06）</b>：装配期任何引用无法解析都直接抛出携带稳定 code 的领域异常，
 * 不跳过步骤、不静默降级：
 * <ul>
 *   <li>资产版本缺失 → {@code DEPENDENCY_UNRESOLVED}（{@link AssetNotFoundException}）；</li>
 *   <li>资产未发布 → {@code ASSET_NOT_AVAILABLE}（{@link AssetNotAvailableException}）；</li>
 *   <li>能力未注册 → {@code CAPABILITY_NOT_REGISTERED}（由 {@link CapabilityRegistry} 抛出）。</li>
 * </ul>
 */
public final class ActivationPlanner {

    private static final Logger LOG = LoggerFactory.getLogger(ActivationPlanner.class);
    private static final String CONTRACT_VERSION = "gk-ke/v1";

    private final AssetRegistryPort assets;
    private final CapabilityRegistry capabilities;
    private final PlanCanonicalHasher hasher;

    public ActivationPlanner(AssetRegistryPort assets) {
        this(assets, new CapabilityRegistry(), new PlanCanonicalHasher());
    }

    public ActivationPlanner(AssetRegistryPort assets, CapabilityRegistry capabilities,
                             PlanCanonicalHasher hasher) {
        this.assets = Objects.requireNonNull(assets, "assets must not be null");
        this.capabilities = Objects.requireNonNull(capabilities, "capabilities must not be null");
        this.hasher = Objects.requireNonNull(hasher, "hasher must not be null");
    }

    /** 装配激活计划；引用无法解析时硬失败（T06），成功则附 canonical planHash（T05）。 */
    public ActivationPlanRecord plan(PlanRequest req) {
        Objects.requireNonNull(req, "req must not be null");
        Set<VersionRef> assetRefs = new LinkedHashSet<>();
        Set<VersionRef> capabilityRefs = new LinkedHashSet<>();
        List<PlanStep> steps = resolveSteps(req.map(), assetRefs, capabilityRefs);
        ActivationPlanRecord plan = buildPlan(req, assetRefs, capabilityRefs, steps);
        LOG.info("Activation plan assembled: planId={}, steps={}", req.planId(), steps.size());
        return hasher.withComputedHash(plan);
    }

    private List<PlanStep> resolveSteps(KnowledgeMapRecord map, Set<VersionRef> assetRefs,
                                        Set<VersionRef> capabilityRefs) {
        List<PlanStep> steps = new ArrayList<>();
        for (MapNode node : map.nodes()) {
            resolveNode(node, assetRefs, capabilityRefs);
            steps.add(new PlanStep(node.nodeId(), executorRef(node),
                    incomingDependencies(map, node.nodeId()), null));
        }
        return List.copyOf(steps);
    }

    private void resolveNode(MapNode node, Set<VersionRef> assetRefs,
                             Set<VersionRef> capabilityRefs) {
        if (node.referencesCapability()) {
            capabilities.requireRegistered(node.ref());
            capabilityRefs.add(node.ref());
        }
        if (node.referencesAsset()) {
            assetRefs.add(resolvePublishedAsset(node.ref()));
        }
    }

    private VersionRef resolvePublishedAsset(VersionRef ref) {
        AssetVersionRecord asset = assets.resolve(ref.id(), ref.version())
                .orElseThrow(() -> new AssetNotFoundException(ref.id(), ref.version()));
        if (!asset.isPublished()) {
            throw new AssetNotAvailableException(ref.id(), ref.version());
        }
        return new VersionRef(asset.assetId(), asset.version());
    }

    private List<String> incomingDependencies(KnowledgeMapRecord map, String nodeId) {
        return map.edges().stream()
                .filter(e -> e.to().equals(nodeId) && e.isExecutableDependency())
                .map(e -> e.from())
                .toList();
    }

    private String executorRef(MapNode node) {
        if (node.ref() == null) {
            return node.nodeId();
        }
        String version = node.ref().version() == null ? "" : ":" + node.ref().version();
        return node.ref().id() + version;
    }

    private ActivationPlanRecord buildPlan(PlanRequest req, Set<VersionRef> assetRefs,
                                           Set<VersionRef> capabilityRefs,
                                           List<PlanStep> steps) {
        VersionRef mapRef = new VersionRef(req.map().mapId(), req.map().version());
        return new ActivationPlanRecord(CONTRACT_VERSION, Boolean.FALSE, req.planId(),
                req.taskId(), mapRef, req.releaseId(), req.coreVersion(), req.catalogRevision(),
                req.routePolicyVersion(), List.copyOf(assetRefs), List.copyOf(capabilityRefs),
                List.copyOf(req.queryRefs()), steps, req.permissionDecisionRef(),
                req.purpose(), req.scope(), req.budget(), null);
    }
}
