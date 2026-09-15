package com.gien.gits.adapter.jena;

import com.gien.gits.semantic.OntologyPort;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.Objects;
import java.util.Set;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.ResIterator;
import org.apache.jena.rdf.model.Resource;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RiotException;
import org.apache.jena.vocabulary.OWL;
import org.apache.jena.vocabulary.RDF;

/**
 * Jena 实现的本体读取适配器（GK17 / WP2.1）。
 *
 * <p>读**真实文件**、按内容算版本、按实体计数给依据。**fail-closed**：
 * 文件不可达 → {@link OntologyPort.OntologyLoadResult#missing}；
 * 不可解析或读出为空 → {@link OntologyPort.OntologyLoadResult#malformed}。
 * 二者**都不抛异常**，由调用方（规划器）据此拒绝出计划。</p>
 *
 * <p><b>本类不定义第二套本体语义</b>：T-Box/A-Box 的判定复用 Jena 的
 * {@code owl:Class} / {@code owl:ObjectProperty} / {@code owl:DatatypeProperty}
 * 词汇表，与 {@code specs/semantic/gits-core.owl.ttl} 的写法一致；
 * SHACL 校验仍由既有的 {@link JenaSemanticRepositoryAdapter} 承担，本类不重复实现。</p>
 */
public final class JenaOntologyAdapter implements OntologyPort {

    /** schema 层类型：被这些类型实例化的主语**不算个体**。 */
    private static final Set<Resource> SCHEMA_TYPES = Set.of(
            OWL.Class,
            OWL.ObjectProperty,
            OWL.DatatypeProperty,
            OWL.AnnotationProperty,
            OWL.Ontology);

    private final Path ontologyPath;
    private final String contractRef;

    public JenaOntologyAdapter(Path ontologyPath, String contractRef) {
        this.ontologyPath = ontologyPath;
        this.contractRef = (contractRef == null || contractRef.isBlank()) ? "CTR-SEM-002" : contractRef;
    }

    @Override
    public OntologyLoadResult load() {
        String sourceRef = ontologyPath == null ? "(null)" : ontologyPath.toString();
        if (ontologyPath == null || !Files.isRegularFile(ontologyPath)) {
            return OntologyLoadResult.missing(sourceRef);
        }

        byte[] bytes;
        try {
            bytes = Files.readAllBytes(ontologyPath);
        } catch (IOException error) {
            // 读不到内容的文件，对规划器而言与不可达等价 —— 仍走 fail-closed。
            return OntologyLoadResult.missing(sourceRef + " (" + error.getClass().getSimpleName() + ")");
        }
        if (bytes.length == 0) {
            return OntologyLoadResult.malformed(sourceRef, "file is empty (0 bytes)");
        }

        Model model = ModelFactory.createDefaultModel();
        try {
            RDFDataMgr.read(model, new java.io.ByteArrayInputStream(bytes),
                    org.apache.jena.riot.Lang.TURTLE);
        } catch (RiotException error) {
            // 语法错不得静默降级；如实报 malformed，由调用方拒绝。
            return OntologyLoadResult.malformed(sourceRef, error.getMessage());
        }

        // 读得出模型但**一条语句都没有** ⇒ 不是"空本体也可接受"，而是解析/输入有问题。
        if (model.isEmpty()) {
            return OntologyLoadResult.malformed(sourceRef, "parsed successfully but model is empty");
        }

        int classes = countTyped(model, OWL.Class);
        int objectProperties = countTyped(model, OWL.ObjectProperty);
        int datatypeProperties = countTyped(model, OWL.DatatypeProperty);
        int individuals = countIndividuals(model);

        return OntologyLoadResult.loaded(new OntologySnapshot(
                contractRef + "@sha256:" + sha256Hex16(bytes),
                sourceRef,
                classes,
                objectProperties,
                datatypeProperties,
                individuals));
    }

    private static int countTyped(Model model, Resource type) {
        Set<Resource> seen = new HashSet<>();
        ResIterator it = model.listSubjectsWithProperty(RDF.type, type);
        while (it.hasNext()) {
            seen.add(it.nextResource());
        }
        return seen.size();
    }

    /** 个体 = 被**非 schema 类**实例化的主语（schema 声明本身不算个体）。 */
    private static int countIndividuals(Model model) {
        Set<Resource> seen = new HashSet<>();
        ResIterator it = model.listSubjectsWithProperty(RDF.type);
        while (it.hasNext()) {
            Resource subject = it.nextResource();
            var types = subject.listProperties(RDF.type);
            while (types.hasNext()) {
                Resource type = types.nextStatement().getObject().asResource();
                if (!SCHEMA_TYPES.contains(type)) {
                    seen.add(subject);
                    break;
                }
            }
        }
        return seen.size();
    }

    /** 内容哈希取前 16 位十六进制 —— 与 {@code DefaultActivationPlanner.sha256} 同一截断口径。 */
    private static String sha256Hex16(byte[] content) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(digest.digest(content)).substring(0, 16);
        } catch (NoSuchAlgorithmException error) {
            throw new IllegalStateException("SHA-256 unavailable", error);
        }
    }

    @Override
    public String toString() {
        return "JenaOntologyAdapter(" + Objects.toString(ontologyPath) + ", " + contractRef + ")";
    }
}
