package com.gien.gits.adapter.jena;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.gien.gits.semantic.OntologyPort;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * {@link JenaOntologyAdapter} 的单元测试（GK17 / WP2.1）。
 *
 * <p>覆盖三类事实：① **成功态**的读数正确；② **两种失败态**（不可达 / 不可解析）都被显式返回
 * 而非静默降级；③ **版本由内容派生** —— 内容变则版本变（判据 V2 依赖此性质）。</p>
 *
 * <p>另有一条对**真实本体**的断言：读数必须等于实测值 32/34/1/0。
 * 这是**防空转**的关键 —— 若解析器悄悄失效，此断言会当场失败，而不是因为夹具缺失而"通过"。</p>
 */
class JenaOntologyAdapterTest {

    private static final String SMALL_ONTOLOGY = """
            @prefix owl: <http://www.w3.org/2002/07/owl#> .
            @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix gits: <https://gientech.com/gits/kno/> .

            gits:CoreOntology a owl:Ontology .

            gits:Thing a owl:Class .
            gits:Other a owl:Class .
            gits:relatesTo a owl:ObjectProperty .
            gits:label a owl:DatatypeProperty .

            gits:individual_one a gits:Thing .
            """;

    private static Path write(Path dir, String name, String content) throws IOException {
        Path path = dir.resolve(name);
        Files.writeString(path, content, StandardCharsets.UTF_8);
        return path;
    }

    @Test
    void loadsRealOntologyWithMeasuredCounts() {
        // 仓库根下的真实本体：读数必须是实测值，不得"读到 0 也算通过"。
        Path ontology = Path.of("..", "..", "specs", "semantic", "gits-core.owl.ttl");
        assertTrue(Files.isRegularFile(ontology), "真实本体不在预期路径：" + ontology.toAbsolutePath());

        OntologyPort.OntologyLoadResult result = new JenaOntologyAdapter(ontology, "CTR-SEM-002").load();

        assertTrue(result.isLoaded(), "真实本体应加载成功：" + result.failureReason());
        OntologyPort.OntologySnapshot snapshot = result.snapshot();
        // 实测基线（2026-09-15，GK17 W1 产出）：32 类 / 34 对象属性 / 1 数据类型属性 / 0 个体。
        assertEquals(32, snapshot.classCount(), "本体类数");
        assertEquals(34, snapshot.objectPropertyCount(), "本体对象属性数");
        assertEquals(1, snapshot.datatypePropertyCount(), "本体数据类型属性数");
        assertEquals(0, snapshot.individualCount(), "本体个体数（本体只承载 T-Box）");
        assertTrue(snapshot.ontologyVersion().startsWith("CTR-SEM-002@sha256:"), snapshot.ontologyVersion());
        assertTrue(snapshot.evidence().contains("classes=32"), snapshot.evidence());
    }

    @Test
    void loadsSmallOntologyAndCountsEntities(@TempDir Path dir) throws IOException {
        Path ontology = write(dir, "small.ttl", SMALL_ONTOLOGY);

        OntologyPort.OntologyLoadResult result = new JenaOntologyAdapter(ontology, "CTR-SEM-002").load();

        assertTrue(result.isLoaded(), result.failureReason());
        OntologyPort.OntologySnapshot snapshot = result.snapshot();
        assertEquals(2, snapshot.classCount(), "owl:Class 数（Thing/Other）");
        assertEquals(1, snapshot.objectPropertyCount(), "owl:ObjectProperty 数");
        assertEquals(1, snapshot.datatypePropertyCount(), "owl:DatatypeProperty 数");
        // 个体 = 被非 schema 类实例化的主语；`a owl:Ontology` 等 schema 声明不算个体。
        assertEquals(1, snapshot.individualCount(), "个体数（individual_one）");
    }

    @Test
    void missingFileIsFailClosedNotSilent(@TempDir Path dir) {
        OntologyPort.OntologyLoadResult result =
                new JenaOntologyAdapter(dir.resolve("does-not-exist.ttl"), "CTR-SEM-002").load();

        assertFalse(result.isLoaded());
        assertEquals(OntologyPort.OntologyLoadResult.CODE_MISSING, result.failureCode());
        assertTrue(result.failureReason().contains("does-not-exist.ttl"), result.failureReason());
    }

    @Test
    void nullPathIsFailClosed() {
        OntologyPort.OntologyLoadResult result = new JenaOntologyAdapter(null, "CTR-SEM-002").load();

        assertFalse(result.isLoaded());
        assertEquals(OntologyPort.OntologyLoadResult.CODE_MISSING, result.failureCode());
    }

    @Test
    void emptyFileIsMalformedNotMissingAndNotLoaded(@TempDir Path dir) throws IOException {
        Path ontology = write(dir, "empty.ttl", "");

        OntologyPort.OntologyLoadResult result = new JenaOntologyAdapter(ontology, "CTR-SEM-002").load();

        assertFalse(result.isLoaded(), "空文件不得被判为加载成功");
        assertEquals(OntologyPort.OntologyLoadResult.CODE_MALFORMED, result.failureCode());
    }

    @Test
    void unparseableTurtleIsFailClosedNotCrash(@TempDir Path dir) throws IOException {
        // 语法错：必须返回 malformed，不得抛栈（抛栈只证明无输入防御，不证明有判定）。
        Path ontology = write(dir, "broken.ttl", "@prefix gits: <https://x/> .\ngits:a a owl:Class ;\n");

        OntologyPort.OntologyLoadResult result = new JenaOntologyAdapter(ontology, "CTR-SEM-002").load();

        assertFalse(result.isLoaded());
        assertEquals(OntologyPort.OntologyLoadResult.CODE_MALFORMED, result.failureCode());
    }

    @Test
    void versionIsDeterministicForSameContentAndChangesWithContent(@TempDir Path dir) throws IOException {
        Path first = write(dir, "a.ttl", SMALL_ONTOLOGY);
        Path same = write(dir, "same.ttl", SMALL_ONTOLOGY);
        Path changed = write(dir, "changed.ttl", SMALL_ONTOLOGY + "\ngits:Third a owl:Class .\n");

        String versionA = new JenaOntologyAdapter(first, "CTR-SEM-002").load().snapshot().ontologyVersion();
        String versionSame = new JenaOntologyAdapter(same, "CTR-SEM-002").load().snapshot().ontologyVersion();
        OntologyPort.OntologyLoadResult changedResult = new JenaOntologyAdapter(changed, "CTR-SEM-002").load();

        // 同内容 ⇒ 同版本（可重放）
        assertEquals(versionA, versionSame);
        // 内容变 ⇒ 版本必须变（判据 V2「改本体 ⇒ 计划必变」依赖此性质）
        assertNotEquals(versionA, changedResult.snapshot().ontologyVersion());
        assertEquals(3, changedResult.snapshot().classCount(), "内容变更后类数应增加");
    }
}
