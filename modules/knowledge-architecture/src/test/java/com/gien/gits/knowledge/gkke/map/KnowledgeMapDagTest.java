package com.gien.gits.knowledge.gkke.map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.MapEdge;
import com.gien.gits.knowledge.gkke.model.MapNode;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import com.gien.gits.knowledge.gkke.registry.GkErrorCode;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G2 知识地图 DAG 校验测试（CR-02 §4.2，验收 T20）。
 *
 * <p>Q1 回归重点：只有执行依赖边（dependsOn/requires/uses）参与环检测；
 * 导航边 covers/relatedTo 与可选边 optional 成环不拒绝。</p>
 */
class KnowledgeMapDagTest {

    private final KnowledgeMapDagValidator validator = new KnowledgeMapDagValidator();

    @Test
    @DisplayName("合法 DAG（多入口、分叉、汇合）校验通过")
    void validDagPasses() {
        KnowledgeMapRecord map = map(
                List.of("N1", "N2"),
                List.of(node("N1"), node("N2"), node("N3"), node("N4")),
                List.of(edge("N1", "N3", "dependsOn"), edge("N2", "N3", "dependsOn"),
                        edge("N3", "N4", "dependsOn")));

        assertThatCode(() -> validator.validate(map)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("无入口节点被拒绝")
    void missingEntryRejected() {
        KnowledgeMapRecord map = map(List.of(), List.of(node("N1")), List.of());

        assertThatThrownBy(() -> validator.validate(map))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("entry");
    }

    @Test
    @DisplayName("入口节点不存在被拒绝")
    void unknownEntryRejected() {
        KnowledgeMapRecord map = map(List.of("N-GHOST"), List.of(node("N1")), List.of());

        assertThatThrownBy(() -> validator.validate(map))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("entry node not found");
    }

    @Test
    @DisplayName("边端点不存在被拒绝（from/to 分别校验）")
    void danglingEdgeRejected() {
        KnowledgeMapRecord badFrom = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N-GHOST", "N2", "dependsOn")));
        KnowledgeMapRecord badTo = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N-GHOST", "dependsOn")));

        assertThatThrownBy(() -> validator.validate(badFrom))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("from-node not found");
        assertThatThrownBy(() -> validator.validate(badTo))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("to-node not found");
    }

    @Test
    @DisplayName("dependsOn 成环被拒绝（直接环与菱形回边），错误码 MAP_CYCLE_DETECTED")
    void dependsOnCycleRejected() {
        KnowledgeMapRecord directCycle = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N2", "dependsOn"), edge("N2", "N1", "dependsOn")));
        KnowledgeMapRecord diamondBackEdge = map(List.of("N1"),
                List.of(node("N1"), node("N2"), node("N3"), node("N4")),
                List.of(edge("N1", "N2", "dependsOn"), edge("N1", "N3", "dependsOn"),
                        edge("N2", "N4", "dependsOn"), edge("N3", "N4", "dependsOn"),
                        edge("N4", "N2", "dependsOn")));

        assertThatThrownBy(() -> validator.validate(directCycle))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("cycle")
                .extracting(ex -> ((MapValidationException) ex).errorCode())
                .isEqualTo(GkErrorCode.MAP_CYCLE_DETECTED.wireValue());
        assertThatThrownBy(() -> validator.validate(diamondBackEdge))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("cycle");
    }

    @Test
    @DisplayName("Q1：仅 relatedTo 成环不参与执行环检测，校验通过")
    void relatedToCyclePasses() {
        KnowledgeMapRecord map = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N2", "relatedTo"), edge("N2", "N1", "relatedTo")));

        assertThatCode(() -> validator.validate(map)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("Q1：仅 covers 成环不参与执行环检测，校验通过")
    void coversCyclePasses() {
        KnowledgeMapRecord map = map(List.of("N1"),
                List.of(node("N1"), node("N2"), node("N3")),
                List.of(edge("N1", "N2", "covers"), edge("N2", "N3", "covers"),
                        edge("N3", "N1", "covers")));

        assertThatCode(() -> validator.validate(map)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("Q1：optional 成环不阻断执行，校验通过")
    void optionalCyclePasses() {
        KnowledgeMapRecord map = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N2", "optional"), edge("N2", "N1", "optional")));

        assertThatCode(() -> validator.validate(map)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("Q1：requires/uses 属执行依赖，成环被拒绝")
    void requiresUsesCycleRejected() {
        KnowledgeMapRecord requiresCycle = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N2", "requires"), edge("N2", "N1", "requires")));
        KnowledgeMapRecord usesCycle = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N2", "uses"), edge("N2", "N1", "uses")));

        assertThatThrownBy(() -> validator.validate(requiresCycle))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("cycle");
        assertThatThrownBy(() -> validator.validate(usesCycle))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("cycle");
    }

    @Test
    @DisplayName("Q1：导航环与执行环并存时，执行环仍被检出")
    void mixedRelationsExecutableCycleStillRejected() {
        // 执行依赖子图 N1 -dependsOn-> N2 -dependsOn-> N1 成环；
        // N3 仅通过 covers/relatedTo 导航边挂接，不参与执行环判定。
        KnowledgeMapRecord map = map(List.of("N1"),
                List.of(node("N1"), node("N2"), node("N3")),
                List.of(edge("N1", "N2", "dependsOn"), edge("N2", "N1", "dependsOn"),
                        edge("N1", "N3", "covers"), edge("N3", "N2", "relatedTo")));

        assertThatThrownBy(() -> validator.validate(map))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("cycle");
    }

    @Test
    @DisplayName("Q2：relation 非合同枚举（如 ROUTES_TO）被拒绝")
    void unknownRelationRejected() {
        KnowledgeMapRecord map = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N2", "ROUTES_TO")));

        assertThatThrownBy(() -> validator.validate(map))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("relation not in contract enum");
    }

    @Test
    @DisplayName("重复 nodeId 被拒绝")
    void duplicateNodeRejected() {
        KnowledgeMapRecord map = map(List.of("N1"), List.of(node("N1"), node("N1")), List.of());

        assertThatThrownBy(() -> validator.validate(map))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("duplicate nodeId");
    }

    @Test
    @DisplayName("按入口提取可达子图：菱形依赖闭包正确且去重")
    void reachableSubgraphClosure() {
        KnowledgeMapRecord map = map(
                List.of("N1"),
                List.of(node("N1"), node("N2"), node("N3"), node("N4"), node("N5")),
                List.of(edge("N1", "N2", "dependsOn"), edge("N1", "N3", "dependsOn"),
                        edge("N2", "N4", "dependsOn"), edge("N3", "N4", "dependsOn"),
                        edge("N4", "N5", "dependsOn")));

        List<String> reachable = validator.reachableSubgraph(map, List.of("N1"));

        assertThat(reachable).containsExactly("N1", "N2", "N3", "N4", "N5");
    }

    @Test
    @DisplayName("不可达分支不进入子图")
    void unreachableBranchExcluded() {
        KnowledgeMapRecord map = map(
                List.of("N1"),
                List.of(node("N1"), node("N2"), node("N3")),
                List.of(edge("N1", "N2", "dependsOn"), edge("N3", "N2", "dependsOn")));

        List<String> reachable = validator.reachableSubgraph(map, List.of("N1"));

        assertThat(reachable).containsExactly("N1", "N2");
    }

    private static MapNode node(String nodeId) {
        return new MapNode(nodeId, "Task", "label-" + nodeId,
                new VersionRef("KE-" + nodeId, "1.0.0"));
    }

    private static MapEdge edge(String from, String to, String relation) {
        return new MapEdge("E-" + from + "-" + to, from, to, relation,
                "test relation", "DD-TEST-001");
    }

    private static KnowledgeMapRecord map(List<String> entries, List<MapNode> nodes,
                                          List<MapEdge> edges) {
        return new KnowledgeMapRecord("gk-ke/v1", Boolean.FALSE, "KM-1", "1.0.0", "REL-TEST-1",
                List.of("PRE_VISIT"), entries, new VersionRef("RP-DEFAULT", "1.0.0"),
                nodes, edges, "RECOMMENDATION",
                new Scope("RETAIL_BANK", List.of("ORG-1"), List.of(), "INTERPRETATION"));
    }
}
