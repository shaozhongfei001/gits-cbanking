package com.gien.gits.knowledge.gkke.map;

import java.util.Arrays;

/**
 * 知识地图边关系枚举（CR-02 §4.2，KnowledgeMap.schema.json#edges/properties/relation）。
 *
 * <p>合同固定 6 值，禁止发明（历史实现中的 ROUTES_TO 已删除）：</p>
 * <ul>
 *   <li>{@link #REQUIRES}：任务装配必需资产/能力，缺失则不可激活 —— 执行依赖；</li>
 *   <li>{@link #USES}：能力/任务执行时调用资产/能力 —— 执行依赖；</li>
 *   <li>{@link #DEPENDS_ON}：节点间执行先后依赖 —— 执行依赖；</li>
 *   <li>{@link #OPTIONAL}：可选增强，缺失不阻断激活 —— 非执行依赖；</li>
 *   <li>{@link #COVERS}：导航/溯源（领域→知识），允许成环 —— 非执行依赖；</li>
 *   <li>{@link #RELATED_TO}：松散语义关联，允许成环 —— 非执行依赖。</li>
 * </ul>
 *
 * <p><b>取舍依据：</b>C02 §4.2 明确“可执行依赖子图必须为 DAG”。requires/uses 表达
 * 激活/执行期必须满足的装配与调用依赖，与 dependsOn 同属执行语义，故一并纳入执行子图；
 * optional 不阻断激活，covers/relatedTo 仅服务导航与溯源，三者均不参与执行环检测。</p>
 */
public enum MapRelation {

    REQUIRES("requires", true),
    OPTIONAL("optional", false),
    USES("uses", true),
    DEPENDS_ON("dependsOn", true),
    COVERS("covers", false),
    RELATED_TO("relatedTo", false);

    private final String wireValue;
    private final boolean executableDependency;

    MapRelation(String wireValue, boolean executableDependency) {
        this.wireValue = wireValue;
        this.executableDependency = executableDependency;
    }

    /** 合同 JSON 字面值。 */
    public String wireValue() {
        return wireValue;
    }

    /** 是否构成可执行依赖子图的边（参与 DAG 环检测）。 */
    public boolean isExecutableDependency() {
        return executableDependency;
    }

    /**
     * 按合同字面值解析；null 或非 6 值枚举时抛 IllegalArgumentException。
     *
     * @param value 合同 relation 字面值
     * @return 对应枚举
     */
    public static MapRelation fromWire(String value) {
        return Arrays.stream(values())
                .filter(relation -> relation.wireValue.equals(value))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException(
                        "unsupported map edge relation: " + value));
    }
}
