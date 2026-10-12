package com.gien.gits.adapter.filesystem;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.gien.gits.knowledge.repository.InMemoryKnowledgeStore;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * 集成测试：用真实权威数据 {@code specs/knowledge-architecture} 加载内存快照，
 * 验证 P22 E1 生产可用控制面的启动加载路径。
 */
class KnowledgeSnapshotLoaderIT {

    private static Path KNOWLEDGE_ROOT;

    @BeforeAll
    static void resolveRoot() {
        Path root = Path.of(".").toAbsolutePath().normalize();
        while (root != null && !root.resolve("specs/knowledge-architecture").toFile().isDirectory()) {
            root = root.getParent();
        }
        assertNotNull(root, "specs/knowledge-architecture not found");
        KNOWLEDGE_ROOT = root.resolve("specs/knowledge-architecture");
    }

    @Test
    void loadsCompleteNonEmptySnapshot() {
        InMemoryKnowledgeStore store = new KnowledgeSnapshotLoader(KNOWLEDGE_ROOT).load();

        // 根地图 + 至少一个域地图
        assertNotNull(store.rootMap());
        assertFalse(store.maps().isEmpty());

        // 四类资产非空
        assertFalse(store.assets().isEmpty());

        // 激活合同：AC-PREVISIT-001 + AC-FACT-RECONCILIATION-001 + AC-PRODUCT-RECOMMEND-001
        // 其中 AC-PRODUCT-RECOMMEND-001 为后续新增。此处按
        // specs/knowledge-architecture/activations/ 的实际条数断言；
        // 该目录是受控合同源（SSOT），新增合同属正常治理变更。
        assertEquals(3, store.contracts().size());

        // 路由策略：RP-CORP-RM-001
        assertFalse(store.policies().isEmpty());

        // 知识要素：39 个（权威规范 4.4）
        assertEquals(39, store.elements().size());
    }

    @Test
    void memoryReadersReadFromLoadedSnapshot() {
        InMemoryKnowledgeStore store = new KnowledgeSnapshotLoader(KNOWLEDGE_ROOT).load();

        // 路由策略可被评估器读取
        assertTrue(new InMemoryRoutePolicyReader(store).find("RP-CORP-RM-001").isPresent());
        // 激活合同可读
        assertTrue(new InMemoryActivationContractReader(store).find("AC-PREVISIT-001").isPresent());
        // 知识要素可按 KI 列出
        assertEquals(8, new InMemoryKnowledgeElementReader(store).listByKnowledgeItem("KI-009").size());
        // 资产按域过滤
        assertFalse(new InMemoryAssetCatalogReader(store).listAll().isEmpty());
    }

    @Test
    void rejectsEmptyOrMissingRoot() {
        Path missing = KNOWLEDGE_ROOT.resolve("does-not-exist-dir");
        assertThrows(java.lang.IllegalStateException.class,
                () -> new KnowledgeSnapshotLoader(missing).load());
    }
}
