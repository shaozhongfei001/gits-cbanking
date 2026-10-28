package com.gien.gits.knowledge.gkke.model;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.knowledge.gkke.map.KnowledgeMapDagValidator;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import java.io.InputStream;
import java.util.Set;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * Q2 合同字段对齐测试（CR-02 §4.2，KnowledgeMap.schema.json，additionalProperties=false）。
 *
 * <p>用合同正例 {@code gk-ke-registry/maps/SIM-MAP-FINANCE.json}（复制自
 * specs/gk-ke/v1/examples/positive/KnowledgeMap.json）验证：</p>
 * <ol>
 *   <li>正例通过 JSON Schema 校验（含 additionalProperties=false）；</li>
 *   <li>正例能被 gkke 地图模型无损反序列化，字段名/枚举与合同一致；</li>
 *   <li>反序列化结果通过 DAG 结构校验。</li>
 * </ol>
 */
class KnowledgeMapContractAlignmentTest {

    private static final String EXAMPLE = "/gk-ke-registry/maps/SIM-MAP-FINANCE.json";
    private static final String SCHEMA = "/gk-ke-v1-schema/KnowledgeMap.schema.json";

    private final ObjectMapper mapper = new ObjectMapper()
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    private final KnowledgeMapDagValidator validator = new KnowledgeMapDagValidator();

    @Test
    @DisplayName("合同正例通过 KnowledgeMap.schema.json 校验（additionalProperties=false）")
    void contractExamplePassesSchemaValidation() throws Exception {
        JsonSchema schema = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7)
                .getSchema(readResource(SCHEMA));

        Set<ValidationMessage> messages =
                schema.validate(mapper.readTree(readResource(EXAMPLE)));

        assertThat(messages).as("schema violations: %s", messages).isEmpty();
    }

    @Test
    @DisplayName("合同正例可反序列化为 KnowledgeMapRecord，字段名/枚举与合同一致")
    void contractExampleDeserializesToRecord() throws Exception {
        KnowledgeMapRecord map = mapper.readValue(readResource(EXAMPLE), KnowledgeMapRecord.class);

        assertThat(map.contractVersion()).isEqualTo("gk-ke/v1");
        assertThat(map.simulationOnly()).isTrue();
        assertThat(map.mapId()).isEqualTo("SIM-MAP-FINANCE");
        assertThat(map.version()).isEqualTo("1.0.0");
        assertThat(map.releaseId()).isEqualTo("SIM-REL-001");
        assertThat(map.taskTypes()).containsExactly("FINANCE_VISIT_PREP");
        assertThat(map.entryNodes()).containsExactly("N-TASK");
        assertThat(map.purpose()).isEqualTo("INTERPRETATION");
        assertThat(map.routePolicyRef().id()).isEqualTo("SIM-ROUTE-001");
        assertThat(map.routePolicyRef().version()).isEqualTo("1.0.0");
        assertThat(map.scope().tenantId()).isEqualTo("SIM-BANK");
        assertThat(map.scope().orgIds()).containsExactly("SIM-O01");
        assertThat(map.scope().customerIds()).containsExactly("SIM-C001");
        assertThat(map.scope().purpose()).isEqualTo("INTERPRETATION");

        assertThat(map.nodes()).hasSize(4);
        MapNode entry = map.nodes().get(0);
        assertThat(entry.nodeId()).isEqualTo("N-TASK");
        assertThat(entry.nodeType()).isEqualTo("Task");
        assertThat(entry.label()).isEqualTo("访前融资讨论");
        assertThat(entry.ref().id()).isEqualTo("SIM-TASK-TEMPLATE");
        assertThat(entry.ref().version()).isEqualTo("1.0.0");
        assertThat(map.nodes())
                .extracting(MapNode::nodeType)
                .containsExactly("Task", "Asset", "Asset", "Capability");

        assertThat(map.edges()).hasSize(4);
        MapEdge firstEdge = map.edges().get(0);
        assertThat(firstEdge.edgeId()).isEqualTo("SIM-ME-1");
        assertThat(firstEdge.from()).isEqualTo("N-TASK");
        assertThat(firstEdge.to()).isEqualTo("N-PRODUCT");
        assertThat(firstEdge.relation()).isEqualTo("requires");
        assertThat(firstEdge.reason()).isEqualTo("解读产品须引用受控条款");
        assertThat(firstEdge.designDecisionRef()).isEqualTo("SIM-MAP-DESIGN-001");
        assertThat(map.edges())
                .extracting(MapEdge::relation)
                .containsExactly("requires", "requires", "requires", "uses");
    }

    @Test
    @DisplayName("反序列化的合同正例通过 DAG 结构校验，入口可达全部 4 节点")
    void deserializedMapPassesDagValidation() throws Exception {
        KnowledgeMapRecord map = mapper.readValue(readResource(EXAMPLE), KnowledgeMapRecord.class);

        assertThatCode(() -> validator.validate(map)).doesNotThrowAnyException();
        assertThat(validator.reachableSubgraph(map, map.entryNodes()))
                .containsExactly("N-TASK", "N-PRODUCT", "N-METRIC", "N-SKILL");
    }

    private InputStream readResource(String name) {
        InputStream stream = getClass().getResourceAsStream(name);
        assertThat(stream).as("test resource on classpath: %s", name).isNotNull();
        return stream;
    }
}
