package com.gien.gits.api.config;

import com.gien.gits.adapter.filesystem.*;
import com.gien.gits.knowledge.port.*;
import com.gien.gits.knowledge.repository.InMemoryKnowledgeStore;
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
            cfg.activationContractPort(store), cfg.assetCatalogPort(store), cfg.knowledgeMapPort(store));
        assertThat(p).isNotNull();
    }

    @Test void missingRootFailsClosed() throws Exception {
        Method m = KnowledgeArchitectureConfig.class.getDeclaredMethod("resolveKnowledgeRoot", String.class);
        m.setAccessible(true);
        assertThatThrownBy(() -> m.invoke(null, "definitely-missing-root-xyz"))
            .hasCauseInstanceOf(IllegalStateException.class);
    }
}
