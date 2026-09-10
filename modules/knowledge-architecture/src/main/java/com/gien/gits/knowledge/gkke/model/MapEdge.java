package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.Objects;
import java.util.Set;

/**
 * 知识地图有向边（严格对齐 {@code specs/gk-ke/v1/schemas/KnowledgeMap.schema.json} 的 edges[]，
 * additionalProperties=false）。
 *
 * <p>relation 严格取合同 6 值枚举：{@code requires|optional|uses|dependsOn|covers|relatedTo}。
 * 历史实现自创的 {@code ROUTES_TO} 已删除。执行依赖子图（必须 DAG）的边分类（C02 §4.2）：
 * <ul>
 *   <li>{@code requires/uses/dependsOn}：执行硬依赖，纳入执行子图判环；</li>
 *   <li>{@code optional}：可选装配依赖，不阻断激活，不参与执行环检测；</li>
 *   <li>{@code covers/relatedTo}：仅导航/溯源关系，绝不参与执行环检测（允许成环）。</li>
 * </ul>
 *
 * <p><b>requires/uses 取舍：</b>C02 §4.2 规定“可执行依赖子图必须为 DAG”。requires/uses
 * 表达激活/执行期必须满足的装配与调用依赖，与 dependsOn 同属执行语义，故一并纳入执行子图。
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record MapEdge(
        String edgeId,
        String from,
        String to,
        String relation,
        String reason,
        String designDecisionRef) {

    /** 合同 relation 枚举（线格式）。 */
    public static final String REL_REQUIRES = "requires";
    public static final String REL_OPTIONAL = "optional";
    public static final String REL_USES = "uses";
    public static final String REL_DEPENDS_ON = "dependsOn";
    public static final String REL_COVERS = "covers";
    public static final String REL_RELATED_TO = "relatedTo";

    /** 纳入执行依赖子图（参与判环）的关系：requires/uses/dependsOn。 */
    private static final Set<String> EXECUTION_DEPENDENCIES =
            Set.of(REL_REQUIRES, REL_USES, REL_DEPENDS_ON);

    public MapEdge {
        Objects.requireNonNull(edgeId, "edgeId must not be null");
        Objects.requireNonNull(from, "from must not be null");
        Objects.requireNonNull(to, "to must not be null");
        Objects.requireNonNull(relation, "relation must not be null");
    }

    /** 是否为执行依赖（纳入执行子图判环）：requires/uses/dependsOn。 */
    public boolean isExecutableDependency() {
        return EXECUTION_DEPENDENCIES.contains(relation);
    }

    /** 是否为导航/溯源关系（covers/relatedTo），绝不参与执行环检测。 */
    public boolean isNavigation() {
        return REL_COVERS.equals(relation) || REL_RELATED_TO.equals(relation);
    }
}
