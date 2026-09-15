package com.gien.gits.api.config;

import com.gien.gits.adapter.filesystem.*;
import com.gien.gits.knowledge.port.*;
import com.gien.gits.knowledge.repository.InMemoryKnowledgeStore;
import com.gien.gits.semantic.OntologyPort;
import org.junit.jupiter.api.Test;
import java.lang.reflect.Method;
import java.nio.file.Path;
import static org.assertj.core.api.Assertions.*;

class KnowledgeArchitectureConfigTest {
    private final KnowledgeArchitectureConfig cfg = new KnowledgeArchitectureConfig();
    private final InMemoryKnowledgeStore store =
            cfg.inMemoryKnowledgeStore("specs/knowledge-architecture");

    @Test void snapshotLoaded() { assertThat(store).isNotNull(); }

    @Test void allPortsWired() {
        assertThat(cfg.knowledgeMapPort(store)).isNotNull();
        assertThat(cfg.assetCatalogPort(store)).isNotNull();
        assertThat(cfg.activationContractPort(store)).isNotNull();
        assertThat(cfg.routePolicyPort(store)).isNotNull();
        assertThat(cfg.knowledgeElementPort(store)).isNotNull();
        assertThat(cfg.knowledgeWikiPort(store)).isNotNull();
    }

    @Test void plannerWired() {
        RoutePolicyPort rp = cfg.routePolicyPort(store);
        RoutePolicyEvaluatorPort ev = cfg.routePolicyEvaluator(rp, "RP-CORP-RM-001");
        ActivationPlannerPort p = cfg.activationPlanner(ev,
            cfg.activationContractPort(store), cfg.assetCatalogPort(store), cfg.knowledgeMapPort(store),
            cfg.ontologyPort("specs/semantic/gits-core.owl.ttl"));
        assertThat(p).isNotNull();
    }

    @Test void ontologyPortLoadsRealOntology() {
        // GK17 / WP2.2：装配点必须**真能读本体**。
        // 原 `plannerWired` 只断言 isNotNull（装配成功即可过），属弱断言 ——
        // "装配了但读不出本体" 会被它放过，故在此补上读数断言。
        OntologyPort ontology = cfg.ontologyPort("specs/semantic/gits-core.owl.ttl");
        var result = ontology.load();

        assertThat(result.isLoaded())
            .as("ontology must load, failureReason=%s", result.failureReason())
            .isTrue();
        assertThat(result.snapshot().ontologyVersion()).startsWith("CTR-SEM-002@sha256:");
        assertThat(result.snapshot().classCount()).isGreaterThan(0);
        assertThat(result.snapshot().objectPropertyCount()).isGreaterThan(0);
        assertThat(result.snapshot().sourceRef()).endsWith("gits-core.owl.ttl");
    }

    @Test void missingRootFailsClosed() throws Exception {
        Method m = KnowledgeArchitectureConfig.class.getDeclaredMethod("resolveKnowledgeRoot", String.class);
        m.setAccessible(true);
        assertThatThrownBy(() -> m.invoke(null, "definitely-missing-root-xyz"))
            .hasCauseInstanceOf(IllegalStateException.class);
    }
}
