package com.gien.gits.api.config;

import com.gien.gits.knowledge.plan.DefaultActivationPlanner;
import com.gien.gits.knowledge.port.ActivationContractPort;
import com.gien.gits.knowledge.port.ActivationPlannerPort;
import com.gien.gits.knowledge.port.AssetCatalogPort;
import com.gien.gits.knowledge.port.KnowledgeElementPort;
import com.gien.gits.knowledge.port.KnowledgeMapPort;
import com.gien.gits.knowledge.port.KnowledgeWikiPort;
import com.gien.gits.knowledge.port.RoutePolicyEvaluatorPort;
import com.gien.gits.knowledge.port.RoutePolicyPort;
import com.gien.gits.knowledge.route.DefaultRoutePolicyEvaluator;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 知识架构控制面装配。
 *
 * <p>DKWS 替代 knowledge-filesystem / InMemoryKnowledgeStore 后，各 Port 暂用
 * fail-closed 空实现（返回 Optional.empty() / 空列表 / 空字符串），
 * 待 DKWS Skill API 集成后替换为真实适配器。</p>
 */
@Configuration
public class KnowledgeArchitectureConfig {

    private static final Logger log = LoggerFactory.getLogger(KnowledgeArchitectureConfig.class);

    @Bean
    public KnowledgeMapPort knowledgeMapPort() {
        log.info("[KnowledgeArchitecture] KnowledgeMapPort: fail-closed stub (DKWS pending)");
        return new KnowledgeMapPort() {
            @Override
            public Optional<com.gien.gits.knowledge.KnowledgeMap> loadRoot() {
                return Optional.empty();
            }

            @Override
            public Optional<com.gien.gits.knowledge.KnowledgeMap> load(String mapId) {
                return Optional.empty();
            }
        };
    }

    @Bean
    public AssetCatalogPort assetCatalogPort() {
        log.info("[KnowledgeArchitecture] AssetCatalogPort: fail-closed stub (DKWS pending)");
        return new AssetCatalogPort() {
            @Override
            public Optional<com.gien.gits.knowledge.AssetManifest> find(String assetId) {
                return Optional.empty();
            }

            @Override
            public List<com.gien.gits.knowledge.AssetManifest> listByDomain(String domain) {
                return List.of();
            }

            @Override
            public List<com.gien.gits.knowledge.AssetManifest> listAll() {
                return List.of();
            }
        };
    }

    @Bean
    public ActivationContractPort activationContractPort() {
        log.info("[KnowledgeArchitecture] ActivationContractPort: fail-closed stub (DKWS pending)");
        return contractId -> Optional.empty();
    }

    @Bean
    public RoutePolicyPort routePolicyPort() {
        log.info("[KnowledgeArchitecture] RoutePolicyPort: fail-closed stub (DKWS pending)");
        return policyId -> Optional.empty();
    }

    @Bean
    public KnowledgeElementPort knowledgeElementPort() {
        log.info("[KnowledgeArchitecture] KnowledgeElementPort: fail-closed stub (DKWS pending)");
        return new KnowledgeElementPort() {
            @Override
            public Optional<com.gien.gits.knowledge.KnowledgeElement> find(String elementId) {
                return Optional.empty();
            }

            @Override
            public List<com.gien.gits.knowledge.KnowledgeElement> listByKnowledgeItem(
                    String knowledgeItemId) {
                return List.of();
            }

            @Override
            public List<com.gien.gits.knowledge.KnowledgeElement> listAll() {
                return List.of();
            }
        };
    }

    @Bean
    public KnowledgeWikiPort knowledgeWikiPort() {
        log.info("[KnowledgeArchitecture] KnowledgeWikiPort: fail-closed stub (DKWS pending)");
        return new KnowledgeWikiPort() {
            @Override
            public String renderMap(String scope) {
                return "";
            }

            @Override
            public String renderKnowledgeItem(String kiId) {
                return "";
            }

            @Override
            public String renderElement(String elementId) {
                return "";
            }
        };
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
            KnowledgeMapPort knowledgeMapPort) {
        return new DefaultActivationPlanner(
                routePolicyEvaluator,
                activationContractPort,
                assetCatalogPort,
                knowledgeMapPort,
                Instant::now);
    }
}
