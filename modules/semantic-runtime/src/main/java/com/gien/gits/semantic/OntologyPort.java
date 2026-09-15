package com.gien.gits.semantic;

import java.util.Objects;
import java.util.Optional;

/**
 * 本体读取端口（GK17 / WP2.1）—— 读 **T-Box + A-Box**，**fail-closed**。
 *
 * <p>动因（实测缺口）：{@code DefaultActivationPlanner} 的 {@code versions.ontology} 此前是
 * 硬编码占位串 {@code "CTR-SEM-001/002@CURRENT_BASE"}，本体**从未被加载**，
 * 计划中也没有任何字段依赖本体内容 ⇒ 判据 V2（改本体 ⇒ 计划必变）在构造上不成立。
 * 本端口把"本体是否真的被读到"变成可判定的事实。</p>
 *
 * <p><b>fail-closed 语义（重要）</b>：本端口**不抛异常**，而是把失败**显式返回**，
 * 由调用方据此拒绝（不得静默降级为"没有本体也能出计划"）：</p>
 * <ul>
 *   <li>本体文件不可达 → {@link OntologyLoadResult#missing(String)}；</li>
 *   <li>本体存在但不可解析 → {@link OntologyLoadResult#malformed(String, String)}；</li>
 *   <li>仅当成功读出**非空**本体时 → {@link OntologyLoadResult#loaded(OntologySnapshot)}。</li>
 * </ul>
 *
 * <p><b>版本口径</b>：{@link OntologySnapshot#ontologyVersion()} 由
 * **本体内容的 SHA-256** 派生（{@code <contractRef>@sha256:<16hex>}），
 * 因此本体内容一变，版本即变 —— 这正是判据 V2 需要被机械保障的性质。</p>
 */
public interface OntologyPort {

    /**
     * 加载本体快照。
     *
     * @return 加载结果；**永不返回 null**。失败以 {@link OntologyLoadResult} 的失败态表达。
     */
    OntologyLoadResult load();

    /**
     * 本体加载结果（成功态 / 两种失败态）。
     *
     * @param snapshot      成功时的快照；失败时为 {@code null}
     * @param failureCode   失败码（{@code ONTOLOGY_MISSING} / {@code ONTOLOGY_MALFORMED}）；成功时为 {@code null}
     * @param failureReason 失败原因（用于计划拒绝消息）；成功时为 {@code null}
     */
    record OntologyLoadResult(OntologySnapshot snapshot, String failureCode, String failureReason) {

        /** 本体文件不可达。 */
        public static final String CODE_MISSING = "ONTOLOGY_MISSING";

        /** 本体存在但不可解析（语法错 / 读出为空）。 */
        public static final String CODE_MALFORMED = "ONTOLOGY_MALFORMED";

        public OntologyLoadResult {
            if (snapshot == null && (failureCode == null || failureCode.isBlank())) {
                throw new IllegalArgumentException("失败态必须给出 failureCode");
            }
            if (snapshot != null && failureCode != null) {
                throw new IllegalArgumentException("成功态不得携带 failureCode");
            }
        }

        public static OntologyLoadResult loaded(OntologySnapshot snapshot) {
            return new OntologyLoadResult(Objects.requireNonNull(snapshot, "snapshot"), null, null);
        }

        public static OntologyLoadResult missing(String sourceRef) {
            return new OntologyLoadResult(null, CODE_MISSING,
                    "ontology not reachable: " + (sourceRef == null ? "(unspecified)" : sourceRef));
        }

        public static OntologyLoadResult malformed(String sourceRef, String reason) {
            return new OntologyLoadResult(null, CODE_MALFORMED,
                    "ontology present but unusable at " + (sourceRef == null ? "(unspecified)" : sourceRef)
                            + ": " + reason);
        }

        public boolean isLoaded() {
            return snapshot != null;
        }

        public Optional<OntologySnapshot> optional() {
            return Optional.ofNullable(snapshot);
        }
    }

    /**
     * 本体快照。
     *
     * @param ontologyVersion       版本串，由本体内容 SHA-256 派生（{@code <contractRef>@sha256:<16hex>}）
     * @param sourceRef             本体来源引用（供计划溯源）
     * @param classCount            T-Box：{@code owl:Class} 数
     * @param objectPropertyCount   T-Box：{@code owl:ObjectProperty} 数
     * @param datatypePropertyCount T-Box：{@code owl:DatatypeProperty} 数
     * @param individualCount       A-Box：被非 schema 类实例化的个体数
     */
    record OntologySnapshot(
            String ontologyVersion,
            String sourceRef,
            int classCount,
            int objectPropertyCount,
            int datatypePropertyCount,
            int individualCount) {

        public OntologySnapshot {
            if (ontologyVersion == null || ontologyVersion.isBlank()) {
                throw new IllegalArgumentException("ontologyVersion is required");
            }
            if (classCount < 0 || objectPropertyCount < 0 || datatypePropertyCount < 0 || individualCount < 0) {
                throw new IllegalArgumentException("counts must be non-negative");
            }
        }

        /** 供计划 trace 的一行式摘要（**依据可复核**，不是"已加载"这种空话）。 */
        public String evidence() {
            return ontologyVersion + " [classes=" + classCount
                    + ",objectProperties=" + objectPropertyCount
                    + ",datatypeProperties=" + datatypePropertyCount
                    + ",individuals=" + individualCount
                    + ",source=" + sourceRef + "]";
        }
    }
}
