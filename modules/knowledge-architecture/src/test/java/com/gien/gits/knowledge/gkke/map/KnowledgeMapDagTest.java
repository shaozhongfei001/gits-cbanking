package com.gien.gits.knowledge.gkke.map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.gien.gits.knowledge.gkke.model.KnowledgeMapRecord;
import com.gien.gits.knowledge.gkke.model.MapEdge;
import com.gien.gits.knowledge.gkke.model.MapNode;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G2 知识地图 DAG 校验测试（CR-02 §4.2，验收 T06/T20）。
 */
class KnowledgeMapDagTest {

    private final KnowledgeMapDagValidator validator = new KnowledgeMapDagValidator();

    @Test
    @DisplayName("合法 DAG（多入口、分叉、汇合）校验通过")
    void validDagPasses() {
        KnowledgeMapRecord map = map(
                List.of("N1", "N2"),
                List.of(node("N1"), node("N2"), node("N3"), node("N4")),
                List.of(edge("N1", "N3"), edge("N2", "N3"), edge("N3", "N4")));

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
                List.of(edge("N-GHOST", "N2")));
        KnowledgeMapRecord badTo = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N-GHOST")));

        assertThatThrownBy(() -> validator.validate(badFrom))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("from-node not found");
        assertThatThrownBy(() -> validator.validate(badTo))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("to-node not found");
    }

    @Test
    @DisplayName("有环地图被拒绝（直接环与菱形回边）")
    void cycleRejected() {
        KnowledgeMapRecord directCycle = map(List.of("N1"), List.of(node("N1"), node("N2")),
                List.of(edge("N1", "N2"), edge("N2", "N1")));
        KnowledgeMapRecord diamondBackEdge = map(List.of("N1"),
                List.of(node("N1"), node("N2"), node("N3"), node("N4")),
                List.of(edge("N1", "N2"), edge("N1", "N3"), edge("N2", "N4"),
                        edge("N3", "N4"), edge("N4", "N2")));

        assertThatThrownBy(() -> validator.validate(directCycle))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("cycle");
        assertThatThrownBy(() -> validator.validate(diamondBackEdge))
                .isInstanceOf(MapValidationException.class)
                .hasMessageContaining("cycle");
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
                List.of(edge("N1", "N2"), edge("N1", "N3"), edge("N2", "N4"),
                        edge("N3", "N4"), edge("N4", "N5")));

        List<String> reachable = validator.reachableSubgraph(map, List.of("N1"));

        assertThat(reachable).containsExactly("N1", "N2", "N3", "N4", "N5");
        assertThat(reachable).doesNotContain("N6");
    }

    @Test
    @DisplayName("不可达分支不进入子图")
    void unreachableBranchExcluded() {
        KnowledgeMapRecord map = map(
                List.of("N1"),
                List.of(node("N1"), node("N2"), node("N3")),
                List.of(edge("N1", "N2"), edge("N3", "N2")));

        List<String> reachable = validator.reachableSubgraph(map, List.of("N1"));

        assertThat(reachable).containsExactly("N1", "N2");
    }

    private static MapNode node(String nodeId) {
        return new MapNode(nodeId, "label-" + nodeId,
                new VersionRef("KE-" + nodeId, "1.0.0"), null,
                "FOUNDATIONAL_DATA", "PRODUCT_CARD", true, 0, 1000, List.of());
    }

    private static MapEdge edge(String from, String to) {
        return new MapEdge(from, to, "DEPENDS_ON");
    }

    private static KnowledgeMapRecord map(List<String> entries, List<MapNode> nodes, List<MapEdge> edges) {
        return new KnowledgeMapRecord("KM-1", "1.0.0", "测试地图", "PUBLISHED",
                entries, nodes, edges, 8000);
    }
}
