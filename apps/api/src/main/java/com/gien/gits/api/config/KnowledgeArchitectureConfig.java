package com.gien.gits.api.config;

import com.gien.gits.adapter.filesystem.InMemoryActivationContractReader;
import com.gien.gits.adapter.filesystem.InMemoryAssetCatalogReader;
import com.gien.gits.adapter.filesystem.InMemoryKnowledgeElementReader;
import com.gien.gits.adapter.filesystem.InMemoryKnowledgeMapReader;
import com.gien.gits.adapter.filesystem.InMemoryRoutePolicyReader;
import com.gien.gits.adapter.filesystem.KnowledgeSnapshotLoader;
import com.gien.gits.adapter.filesystem.KnowledgeWikiFilesystemAdapter;
import com.gien.gits.adapter.jena.JenaOntologyAdapter;
import com.gien.gits.knowledge.plan.DefaultActivationPlanner;
import com.gien.gits.knowledge.port.ActivationContractPort;
import com.gien.gits.knowledge.port.ActivationPlannerPort;
import com.gien.gits.knowledge.port.AssetCatalogPort;
import com.gien.gits.knowledge.port.KnowledgeElementPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import com.gien.gits.knowledge.port.KnowledgeWikiPort;
import com.gien.gits.knowledge.port.RoutePolicyEvaluatorPort;
import com.gien.gits.knowledge.port.RoutePolicyPort;
import com.gien.gits.knowledge.repository.InMemoryKnowledgeStore;
import com.gien.gits.knowledge.route.DefaultRoutePolicyEvaluator;
import com.gien.gits.semantic.OntologyPort;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 知识架构控制面装配（P22 E1 生产可用控制面）。
 *
 * <p>启动时通过 {@link KnowledgeSnapshotLoader} 从 Git/文件系统权威源一次性加载
 * {@link InMemoryKnowledgeStore} 内存快照，运行时各 Port 高频读内存（消除 GAP-2 每请求扫盘）。
 * 快照加载失败（目录缺失/为空）按 fail-closed 拒绝启动，不产生半成品控制面。
 *
 * <p>数据根目录配置项：{@code gits.knowledge.root}（默认 {@code specs/knowledge-architecture}）。</p>
 */
@Configuration
@org.springframework.boot.autoconfigure.condition.ConditionalOnProperty(
        name = "gits.knowledge.enabled",
        havingValue = "true",
        matchIfMissing = true)
public class KnowledgeArchitectureConfig {

    private static final Logger log = LoggerFactory.getLogger(KnowledgeArchitectureConfig.class);

    /**
     * 本体合同引用（GK17 / WP2.2）：{@code specs/semantic/gits-core.owl.ttl} 的受控合同。
     *
     * <p>该值与黄金计划 {@code versions.ontology} 的前缀同源（{@code CTR-SEM-002@sha256:…}）——
     * 改这里必须同步改
     * {@code specs/knowledge-architecture/examples/AP-*-GOLDEN.json}（合同先行）。</p>
     */
    private static final String ONTOLOGY_CONTRACT_REF = "CTR-SEM-002";

    @Bean
    public InMemoryKnowledgeStore inMemoryKnowledgeStore(
            @Value("${gits.knowledge.root:specs/knowledge-architecture}") String knowledgeRoot) {

        Objects.requireNonNull(knowledgeRoot, "gits.knowledge.root");
        Path resolvedRoot = resolveKnowledgeRoot(knowledgeRoot);
        KnowledgeSnapshotLoader loader = new KnowledgeSnapshotLoader(resolvedRoot);
        InMemoryKnowledgeStore store = loader.load();
        log.info("[KnowledgeArchitecture] in-memory snapshot loaded from {}: {} maps, {} assets, "
                        + "{} contracts, {} policies, {} elements",
                resolvedRoot,
                store.maps().size(), store.assets().size(), store.contracts().size(),
                store.policies().size(), store.elements().size());
        return store;
    }

    /**
     * 解析知识根目录，使其不依赖启动工作目录（仓库根或模块目录均可）。
     *
     * <p>配置的根路径可为相对路径（如 {@code specs/knowledge-architecture}）。若当前工作目录
     * 下直接不可达，则沿目录树向上查找，兼容从 {@code apps/api} 等模块目录启动（与
     * {@code KnowledgeSnapshotLoaderIT} 一致）。</p>
     *
     * @param configuredRoot 配置的知识根路径
     * @return 已解析的绝对知识根路径
     */
    private static Path resolveKnowledgeRoot(String configuredRoot) {
        Path requested = Path.of(configuredRoot);
        if (requested.isAbsolute() && requested.toFile().isDirectory()) {
            return requested.normalize();
        }
        Path dir = Path.of("").toAbsolutePath().normalize();
        while (dir != null && !dir.resolve(configuredRoot).toFile().isDirectory()) {
            dir = dir.getParent();
        }
        if (dir == null) {
            // fail-closed：无法定位权威根目录时抛异常拒绝启动。
            throw new IllegalStateException("gits.knowledge.root not found from CWD: " + configuredRoot);
        }
        return dir.resolve(configuredRoot).normalize();
    }

    /**
     * 解析本体文件路径（**不抛异常**）。
     *
     * <p>与 {@link #resolveKnowledgeRoot(String)} 的关键区别：本体**刻意不在装配期 fail-closed**。
     * 若在这里抛异常，应用根本起不来，就永远走不到要求的那条行为 ——
     * "本体不可达 ⇒ {@code PlanDecision.Deny}（fail-closed）"。
     * 故本方法在找不到时仍返回一个绝对化路径，由 {@link JenaOntologyAdapter#load()} 报
     * {@code ONTOLOGY_MISSING}，在**规划期**拒绝，并把原因写进拒绝消息。</p>
     *
     * @param configuredPath 配置的本体路径（可为相对仓根的路径）
     * @return 解析后的绝对路径（可能不存在 → 由端口报 CODE_MISSING）
     */
    private static Path resolveOntologyPath(String configuredPath) {
        Path requested = Path.of(configuredPath);
        if (requested.isAbsolute()) {
            return requested.normalize();
        }
        Path dir = Path.of("").toAbsolutePath().normalize();
        while (dir != null && !dir.resolve(configuredPath).toFile().exists()) {
            dir = dir.getParent();
        }
        return dir == null
                ? requested.toAbsolutePath().normalize()
                : dir.resolve(configuredPath).normalize();
    }

    @Bean
    public KnowledgeMapPort knowledgeMapPort(InMemoryKnowledgeStore store) {
        return new InMemoryKnowledgeMapReader(store);
    }

    @Bean
    public AssetCatalogPort assetCatalogPort(InMemoryKnowledgeStore store) {
        return new InMemoryAssetCatalogReader(store);
    }

    @Bean
    public ActivationContractPort activationContractPort(InMemoryKnowledgeStore store) {
        return new InMemoryActivationContractReader(store);
    }

    @Bean
    public RoutePolicyPort routePolicyPort(InMemoryKnowledgeStore store) {
        return new InMemoryRoutePolicyReader(store);
    }

    @Bean
    public KnowledgeElementPort knowledgeElementPort(InMemoryKnowledgeStore store) {
        return new InMemoryKnowledgeElementReader(store);
    }

    @Bean
    public KnowledgeWikiPort knowledgeWikiPort(InMemoryKnowledgeStore store) {
        return new KnowledgeWikiFilesystemAdapter(store);
    }

    /**
     * 本体读取端口（GK17 / WP2.2）—— 装配 {@link JenaOntologyAdapter} 读真实 T-Box + A-Box。
     *
     * <p>数据根配置项：{@code gits.semantic.ontology}
     * （默认 {@code specs/semantic/gits-core.owl.ttl}，与 {@code gits.knowledge.root} 同源的相对仓根口径）。</p>
     *
     * <p>版本由**本体内容 SHA-256** 派生 ⇒ 本体一变，{@code versions.ontology} 与 {@code planHash}
     * 必变（判据 V2）。不可达/不可解析**不在装配期失败**，而由规划器在决策点 fail-closed
     * （理由见 {@link #resolveOntologyPath(String)}）。</p>
     */
    @Bean
    public OntologyPort ontologyPort(
            @Value("${gits.semantic.ontology:specs/semantic/gits-core.owl.ttl}") String ontologyPath) {
        Path resolved = resolveOntologyPath(ontologyPath);
        log.info("[KnowledgeArchitecture] ontology port bound to {} (contract {})",
                resolved, ONTOLOGY_CONTRACT_REF);
        return new JenaOntologyAdapter(resolved, ONTOLOGY_CONTRACT_REF);
    }

    @Bean
    public RoutePolicyEvaluatorPort routePolicyEvaluator(
            RoutePolicyPort routePolicyPort,
            @Value("${gits.knowledge.route-policy-id:RP-CORP-RM-001}") String policyId) {
        return new DefaultRoutePolicyEvaluator(routePolicyPort, policyId);
    }

    @Bean
    public ActivationPlannerPort activationPlanner(
            RoutePolicyEvaluatorPort routePolicyEvaluator,
            ActivationContractPort activationContractPort,
            AssetCatalogPort assetCatalogPort,
            KnowledgeMapPort knowledgeMapPort,
            OntologyPort ontologyPort) {
        return new DefaultActivationPlanner(
                routePolicyEvaluator,
                activationContractPort,
                assetCatalogPort,
                knowledgeMapPort,
                ontologyPort,
                Instant::now);
    }
}
