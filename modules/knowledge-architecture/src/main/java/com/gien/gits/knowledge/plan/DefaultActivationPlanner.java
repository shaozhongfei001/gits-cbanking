package com.gien.gits.knowledge.plan;

import com.gien.gits.knowledge.ActivationContract;
import com.gien.gits.knowledge.ActivationPlan;
import com.gien.gits.knowledge.AssetManifest;
import com.gien.gits.knowledge.KnowledgeMap;
import com.gien.gits.knowledge.port.ActivationContractPort;
import com.gien.gits.knowledge.port.ActivationPlannerPort;
import com.gien.gits.knowledge.port.AssetCatalogPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import com.gien.gits.knowledge.port.RoutePolicyEvaluatorPort;
import com.gien.gits.knowledge.route.RouteDecision;
import com.gien.gits.semantic.OntologyPort;
import com.gien.gits.semantic.OntologyPort.OntologyLoadResult;
import com.gien.gits.semantic.OntologyPort.OntologySnapshot;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.Comparator;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Supplier;

/**
 * 默认激活计划生成器（P20 shadow 基础设施，不迁移生产流程、不启用 fusion、不执行生产写回）。
 *
 * <p>由 Route Policy Evaluator 解析唯一合法 route，再经 Activation Contract → Asset Catalog
 * 汇合为可重放的 {@link ActivationPlan}。所有校验 fail-closed：任务未映射、合同不在 P20、
 * 权限未决、请求 production mode、请求生产写回、route/contract 不一致、资产未登记等一律返回
 * {@link PlanDecision.Deny}，绝不返回部分计划，绝无业务副作用。</p>
 *
 * <p><b>本体（GK17 / WP2.2）</b>：本类不再使用版本占位串 —— 每次规划都通过
 * {@link OntologyPort} **真实加载本体**，并把
 * ① 内容派生的本体版本写入 {@code versions.ontology}、
 * ② {@code snapshot().evidence()}（版本 + 四类实体计数 + 来源）写入 {@code trace.ontologyEvidence}、
 * ③ 本体版本纳入 {@code planHash}（改本体 ⇒ 计划必变，判据 V2）。
 * 本体不可达或不可解析 ⇒ 以端口的 {@code failureCode()} 直接拒绝，**不得**降级为"没有本体也能出计划"。</p>
 */
public final class DefaultActivationPlanner implements ActivationPlannerPort {

    /** 权限决策未决标记。 */
    private static final String PERMISSION_PENDING = "PENDING";

    /** Shadow 规划器版本，用于 trace.plannerVersion 与 golden 区分。 */
    public static final String PLANNER_VERSION = "p20-shadow-0.1.0";

    private final RoutePolicyEvaluatorPort routeEvaluator;
    private final ActivationContractPort activationContractPort;
    private final AssetCatalogPort assetCatalogPort;
    private final KnowledgeMapPort knowledgeMapPort;
    private final OntologyPort ontologyPort;
    private final Supplier<Instant> clock;

    public DefaultActivationPlanner(
            RoutePolicyEvaluatorPort routeEvaluator,
            ActivationContractPort activationContractPort,
            AssetCatalogPort assetCatalogPort,
            KnowledgeMapPort knowledgeMapPort,
            OntologyPort ontologyPort,
            Supplier<Instant> clock) {
        this.routeEvaluator = Objects.requireNonNull(routeEvaluator, "routeEvaluator");
        this.activationContractPort = Objects.requireNonNull(activationContractPort, "activationContractPort");
        this.assetCatalogPort = Objects.requireNonNull(assetCatalogPort, "assetCatalogPort");
        this.knowledgeMapPort = Objects.requireNonNull(knowledgeMapPort, "knowledgeMapPort");
        this.ontologyPort = Objects.requireNonNull(ontologyPort, "ontologyPort");
        this.clock = Objects.requireNonNull(clock, "clock");
    }

    /**
     * 生成激活计划（P20 双路径汇合为可重放 ActivationPlan 的核心入口）。
     *
     * <p>完整执行管线（全部 fail-closed）：
     * <ol>
     *   <li>前置护栏：拒绝空请求 / production 模式 / 生产写回 / 权限未决；</li>
     *   <li>本体前置条件：**真实加载本体**（GK17 / WP2.2）；不可达/不可解析 ⇒ 以端口
     *       {@code failureCode()} 为拒绝码直接拒绝，不降级、不给部分 credit；</li>
     *   <li>路由解析：由 {@link RoutePolicyEvaluatorPort} 从 Route Policy 解析唯一合法 route；</li>
     *   <li>合同校验：加载激活合同，并核对 route 与合同的 taskType/routeMode 一致性（引用完整性）；</li>
     *   <li>地图加载：加载根知识地图以获取版本信息；</li>
     *   <li>资产解析：将合同声明的激活资产逐一解析为已登记的 AssetManifest；</li>
     *   <li>计划组装：构造含版本、资产、查询、规则、技能、上下文与可重放 planHash 的 {@link ActivationPlan}。</li>
     * </ol>
     * 任何一步失败都返回 {@link PlanDecision.Deny}，绝不返回部分计划，绝无业务副作用。</p>
     */
    @Override
    public PlanDecision plan(ActivationPlanRequest request) {
        // ── 1. 前置护栏：fail-closed 拒绝非法/未授权请求 ──────────────────────
        // 请求为 null：无法解析任何 task，直接拒绝（未映射任务语义）。
        if (request == null) {
            return new PlanDecision.Deny("DENY_UNMAPPED_TASK", "request is null (fail-closed)");
        }
        // production 模式：P20 仅允许 shadow，任何 production 请求一律拒绝。
        if (request.executionMode() == ExecutionMode.PRODUCTION) {
            return new PlanDecision.Deny("DENY_PRODUCTION_MODE",
                    "production mode is not authorized for P20 shadow slice");
        }
        // 生产写回：P20 不授权写回生产系统，请求写回一律拒绝。
        if (request.writebackRequested()) {
            return new PlanDecision.Deny("DENY_WRITEBACK",
                    "production writeback is not authorized for P20 shadow slice");
        }
        // 权限未决：权限决策缺失或为 PENDING 时拒绝（SEC-001/002）。
        if (!isPermissionResolved(request.permissionDecisionId())) {
            return new PlanDecision.Deny("DENY_PERMISSION_PENDING",
                    "permission decision is missing or pending (fail-closed)");
        }

        // 本体前置条件（GK17 / WP2.2）：本体是**全部四条 routeMode 路径**的共同前置，
        // 故先于路由解析加载 —— 这样"本体不可达"不依赖 route/合同/地图是否恰好可用，
        // 不给任何部分 credit。fail-closed：端口不抛异常，失败以 failureCode() 直接成拒绝码，
        // 消息带 failureReason()；**不得**降级为"没有本体也能出计划"。
        OntologyLoadResult ontologyResult = ontologyPort.load();
        if (!ontologyResult.isLoaded()) {
            return new PlanDecision.Deny(ontologyResult.failureCode(), ontologyResult.failureReason());
        }
        OntologySnapshot ontology = ontologyResult.snapshot();

        // ── 2. 路由解析：从 Route Policy 取得唯一合法 route ───────────────────
        // 由独立的 Route Policy Evaluator 判定任务应走哪条路径（主路径由此决定）。
        RouteDecision routeDecision = routeEvaluator.evaluate(request.taskType(), request.executionMode());
        if (!routeDecision.isAllowed()) {
            // 路由评估返回拒绝（未映射/不在 P20/production 等），原样转成计划级拒绝。
            return toPlanDeny(routeDecision);
        }
        RouteDecision.AllowRoute route = routeDecision.allow().orElseThrow();

        // ── 3. 激活合同校验（含引用完整性）────────────────────────────────────
        // 依据 route 指向的激活合同引用加载合同对象。
        Optional<ActivationContract> contractOpt =
                activationContractPort.find(route.activationContractRef());
        if (contractOpt.isEmpty()) {
            // 合同不存在或不可解析 → 无法继续，拒绝（fail-closed）。
            return new PlanDecision.Deny("DENY_NOT_IN_P20",
                    "activation contract '" + route.activationContractRef() + "' not resolvable (fail-closed)");
        }
        ActivationContract contract = contractOpt.get();

        // 引用完整性：route 策略与激活合同对同一 task 的任务类型与主路径模式必须一致；
        // 不一致说明合同链存在漂移，禁止据此生成计划（fail-closed）。
        if (!request.taskType().equals(contract.taskType())
                || !route.mode().equals(contract.routeMode())) {
            return new PlanDecision.Deny("DENY_CONTRACT_MISMATCH",
                    "route policy and activation contract disagree for task '"
                            + request.taskType() + "' (routeMode=" + route.mode()
                            + ", contract=" + contract.routeMode() + ")");
        }

        // ── 4. 知识地图加载 ───────────────────────────────────────────────────
        // 加载根知识地图以取得版本信息（versions.knowledgeMap），供计划版本溯源。
        Optional<KnowledgeMap> mapOpt = knowledgeMapPort.loadRoot();
        if (mapOpt.isEmpty()) {
            return new PlanDecision.Deny("DENY_UNMAPPED_TASK", "knowledge map not resolvable (fail-closed)");
        }
        KnowledgeMap map = mapOpt.get();

        // ── 5. 资产解析：合同声明的激活资产必须全部已登记 ─────────────────────
        // 逐项把合同中的 activation.assetId 解析为 AssetManifest；任一未登记 → fail-closed 拒绝（SEC-003）。
        List<ActivationPlan.SelectedAsset> selectedAssets = resolveAssets(contract);
        if (selectedAssets == null) {
            return new PlanDecision.Deny("DENY",
                    "one or more activation assets are not registered in Asset Manifest (fail-closed)");
        }

        // ── 6. 计划组装：构造可重放的 ActivationPlan ──────────────────────────
        // 取当前业务时点用于 trace.createdAt。
        Instant now = clock.get();
        // 计划 ID 与任务 ID 由 taskType + customerId 确定性派生，便于追溯与去重。
        String planId = "AP-" + request.taskType() + "-" + safeToken(request.customerId()) + "-SHADOW";
        String taskId = "TASK-" + request.taskType() + "-" + safeToken(request.customerId()) + "-SHADOW";
        // planHash 仅基于确定性字段（routeMode/**本体版本**/资产/查询/规则/技能/上下文），
        // 保证相同输入可重放；本体版本由本体内容派生 ⇒ 本体一变，planHash 必变（判据 V2）。
        String planHash = sha256(deterministicContent(
                route.mode(), selectedAssets, contract, ontology.ontologyVersion()));

        ActivationPlan plan = new ActivationPlan(
                "1.0.0",                        // schema 版本
                planId,                         // 计划 ID
                taskId,                         // 任务 ID
                request.taskType(),             // 任务类型
                route.mode(),                   // 主路径模式（route 决定）
                new ActivationPlan.Versions(    // 各合同版本，供审计溯源
                        map.mapId() + "@" + map.version(),          // 知识地图版本
                        route.policyId() + "@" + route.policyVersion(), // 路由策略版本
                        contract.contractId() + "@" + contract.version(), // 激活合同版本
                        ontology.ontologyVersion()),                // 本体版本（真实加载，由内容派生）
                selectedAssets,                 // 已解析并排序的激活资产
                contract.semanticQueries(),     // 语义查询 ID 列表
                contract.ruleChecks(),          // 规则检查列表
                contract.skills(),              // 技能列表
                new ActivationPlan.Context(     // 上下文预算
                        contract.context().maxTokens(),
                        contract.context().trimPolicy()),
                request.permissionDecisionId(), // 权限决策 ID
                // 可重放追踪：planHash 可重放（不含环境字段）；ontologyEvidence 记本体依据
                // （版本 + 四类计数 + 来源），使"本体真的被读到"成为**可从计划复核**的事实。
                new ActivationPlan.Trace(
                        planHash, now.toString(), PLANNER_VERSION, ontology.evidence()));

        // 所有校验通过，返回允许计划。
        return new PlanDecision.AllowPlan(plan);
    }

    private static PlanDecision toPlanDeny(RouteDecision decision) {
        return new PlanDecision.Deny(decision instanceof RouteDecision.Deny deny ? deny.decisionCode() : "DENY",
                decision instanceof RouteDecision.Deny deny ? deny.reason() : "route evaluation denied (fail-closed)");
    }

    private boolean isPermissionResolved(String permissionDecisionId) {
        return permissionDecisionId != null
                && !permissionDecisionId.isBlank()
                && !PERMISSION_PENDING.equalsIgnoreCase(permissionDecisionId);
    }

    /**
     * 解析合同声明的激活资产。
     *
     * <p>流程：先把合同中的 activations 按 {@code sequence} 升序排序（保证输出顺序确定），
     * 再逐项通过 {@link AssetCatalogPort} 把每个 {@code assetId} 解析为已登记的 AssetManifest。
     * 任一资产未登记则返回 {@code null}，由调用方以 fail-closed 拒绝（SEC-003：所有资产必须登记）。</p>
     *
     * @param contract 激活合同，含待激活的资产列表
     * @return 已解析并按 sequence 排序的激活资产列表；任一资产未登记返回 {@code null}
     */
    private List<ActivationPlan.SelectedAsset> resolveAssets(ActivationContract contract) {
        // 存放最终解析结果（保持 sequence 顺序）。
        List<ActivationPlan.SelectedAsset> result = new java.util.ArrayList<>();
        // 复制一份 activations 列表以排序，避免修改合同对象（不可变语义）。
        List<ActivationContract.Activation> activations = new java.util.ArrayList<>(contract.activations());
        // 按 sequence 升序排序；缺失 sequence 的视为最后（Integer.MAX_VALUE）。
        activations.sort(Comparator.comparing(a -> a.sequence() == null ? Integer.MAX_VALUE : a.sequence()));

        // 逐项解析：每个合同声明的激活资产都必须能在 Asset Manifest 中找到。
        for (ActivationContract.Activation activation : activations) {
            Optional<AssetManifest> assetOpt = assetCatalogPort.find(activation.assetId());
            if (assetOpt.isEmpty()) {
                // 资产未登记 → fail-closed，返回 null 让调用方整体拒绝。
                return null;
            }
            AssetManifest asset = assetOpt.get();
            // 记录资产 ID、版本、是否必需与执行顺序（供 ActivationPlan 输出）。
            result.add(new ActivationPlan.SelectedAsset(
                    asset.assetId(),
                    asset.version(),
                    activation.required(),
                    activation.sequence()));
        }
        // 返回不可变副本，保证调用方无法篡改。
        return List.copyOf(result);
    }

    /**
     * 计算用于 planHash 的确定性内容。
     *
     * <p>仅拼接黄金可比对的确定性字段（routeMode、资产、查询、规则、技能、上下文），
     * 使相同输入总能产生相同 planHash（可重放）。字段间用分隔符避免拼接歧义。</p>
     *
     * @return 确定性内容字符串
     */
    private String deterministicContent(
            String routeMode,
            List<ActivationPlan.SelectedAsset> selectedAssets,
            ActivationContract contract,
            String ontologyVersion) {
        StringBuilder sb = new StringBuilder();
        // 追加主路径模式，作为哈希内容的第一段。
        sb.append(routeMode).append('|');
        // 追加本体版本（GK17 / WP2.3）：本体内容一变，版本即变 ⇒ planHash 必变（判据 V2）。
        // 这里刻意只用**版本**（内容派生），不用整个 evidence() —— evidence 含来源路径，
        // 属环境相关字段，入哈希会破坏 planHash 的可重放性。
        sb.append(ontologyVersion).append('|');
        // 追加每个已排序资产：assetId@version:required:sequence，分号分隔。
        for (ActivationPlan.SelectedAsset asset : selectedAssets) {
            sb.append(asset.assetId()).append('@').append(asset.version())
                    .append(':').append(asset.required()).append(':').append(asset.sequence()).append(';');
        }
        // 追加合同声明的查询、规则、技能与上下文预算（列表按契约顺序）。
        sb.append(contract.semanticQueries()).append('|');
        sb.append(contract.ruleChecks()).append('|');
        sb.append(contract.skills()).append('|');
        sb.append(contract.context().maxTokens()).append('|').append(contract.context().trimPolicy());
        return sb.toString();
    }

    /**
     * 计算内容的 SHA-256 并取前 16 位十六进制作为 planHash（截断以缩短，碰撞概率可接受）。
     *
     * @param content 待哈希的确定性内容
     * @return 16 位十六进制哈希串
     */
    private static String sha256(String content) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(content.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(hash).substring(0, 16);
        } catch (NoSuchAlgorithmException error) {
            // SHA-256 是 JDK 强制实现的算法，理论上不会缺失；若缺失则抛出不可恢复异常。
            throw new IllegalStateException("SHA-256 unavailable", error);
        }
    }

    /**
     * 把用户输入的标识安全化为可嵌入 ID 的令牌。
     *
     * <p>空值/空白 → "UNKNOWN"；其余将非字母数字连字符替换为下划线，防止 ID 注入。</p>
     *
     * @param value 原始标识（如 customerId）
     * @return 安全化的令牌
     */
    private static String safeToken(String value) {
        if (value == null || value.isBlank()) {
            return "UNKNOWN";
        }
        return value.replaceAll("[^A-Za-z0-9-]", "_");
    }
}
