package com.gien.gits.hermes.knowledge;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.gien.gits.ontology.port.ScenarioDataProvider;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.junit.jupiter.api.Test;

class SimulatedKnowledgeProviderTest {

    private static final String CONTRACT = """
            {"schemaVersion":"1.0.0","contractId":"AC-PREVISIT-DEMO-001","knowledgeItemIds":["KI-FRONT-001","KI-FRONT-002"]}
            """;

    private static final String KE_001 = """
            ---
            {"schemaVersion":"1.0.0","elementId":"KE-FRONT-001-01","name":"上游供应商列表","kind":"K-Type-F","knowledgeItemId":"KI-FRONT-001","content":"华东精工上游供应商清单。"}
            ---

            # 上游供应商列表
            """;

    private static final String KE_002 = """
            ---
            {"schemaVersion":"1.0.0","elementId":"KE-FRONT-002-01","name":"经营与财务概况","kind":"K-Type-F","knowledgeItemId":"KI-FRONT-002","content":"华东精工经营与财务概况。"}
            ---

            # 经营概况
            """;

    private static final String RULES = """
            rules:
              - ruleId: "RUL-FRONT-001"
                name: "客户表达不得直接写成事实"
                enforcement: "FAIL_CLOSED"
              - ruleId: "RUL-FRONT-002"
                name: "可用额度不等同融资需求"
                enforcement: "PARTY"
            """;

    private static final String NON_JSON_FRONTMATTER = """
            ---
            schemaVersion: "1.0.0"
            elementId: "KE-X-01"
            ---

            # fallback
            """;

    private static final String SUPPLY_CHAIN = """
            schema: supply_chain_graph/v1
            customer_id: CUST-CORP-0001
            focal:
              node_id: HDJG-GROUP
              name: 华东精工装备集团
              node_role: 核心企业
            upstream_suppliers:
              - supplier_id: SUP-001
                name: 华东精工智能制造有限公司
                category: 智能制造设备
                notes: 项目主体倾向为智能制造公司
                last12m_purchase_cny_wan: 3280
                pct_of_annual_purchase: 42
                price_trend: 上行
                payment_preference: 银行承兑汇票占比高，接受供应链融资
                relationship_since: "2019"
                evidence_refs: ["NOTE-002"]
              - supplier_id: SUP-002
                name: 杭州精工数控装备有限公司
                category: 数控/精密传动部件
                notes: 主力供应商之一
                last12m_purchase_cny_wan: 1950
                pct_of_annual_purchase: 25
                price_trend: 平稳
                payment_preference: 应收账款融资/供应链票据可接受
                relationship_since: "2020"
            midstream_integrators:
              - integrator_id: MID-01
                integrator_name: 浙江智造系统集成有限公司
                service: 段内系统集成与安装调试
                contract_value_cny_wan: 780
            downstream_customers:
              - customer_id: DST-01
                name: 中骏新能源科技
                industry: 新能源
                annual_contract_cny_wan: 5600
            gap_summary_in_review: false
            """;

    @Test
    void assembleReadsAssetBindingSupplyChainAndTrace() {
        Map<String, Object> files = new LinkedHashMap<>();
        files.put("05_knowledge/demo/activation-contract.json", CONTRACT);
        files.put("05_knowledge/demo/knowledge-map.yaml",
                "mapId: KM-CORP-RM-PREVISIT-DEMO\n"
                        + "knowledgeItemBindings:\n"
                        + "  - knowledgeItemId: \"KI-FRONT-001\"\n"
                        + "    dataAsset: \"ASSET-KNOW-SUPPLY-CHAIN-DEMO\"\n"
                        + "    dataPath: \"supply-chain/supply-chain.yaml\"\n"
                        + "    elementType: \"SUPPLY_CHAIN_GRAPH\"\n"
                        + "  - knowledgeItemId: \"KI-FRONT-002\"\n"
                        + "    dataAsset: \"ASSET-DATA-CUSTOMER-PROFILE-DEMO\"\n"
                        + "    dataPath: \"02_master_data/customer_master.json\"\n"
                        + "    elementType: \"CUSTOMER_PROFILE\"\n");
        files.put("05_knowledge/demo/supply-chain/supply-chain.yaml", SUPPLY_CHAIN);
        files.put("05_knowledge/demo/elements/KI-FRONT-001/KE-FRONT-001-01.md", KE_001);
        files.put("05_knowledge/demo/elements/KI-FRONT-002/KE-FRONT-002-01.md", KE_002);

        SimulatedKnowledgeProvider provider = new SimulatedKnowledgeProvider(
                new InMemoryScenarioDataProvider(files));

        KnowledgeAssemblyResult result = provider.assemble("KM-CORP-RM-PREVISIT-DEMO", "客户：华东精工");

        // 供应链真实数据装配进上下文
        String ctx = result.knowledgeContext();
        assertTrue(ctx.contains("华东精工智能制造有限公司"), "应装配上游供应商 SUP-001");
        assertTrue(ctx.contains("杭州精工数控装备有限公司"), "应装配上游供应商 SUP-002");
        assertTrue(ctx.contains("占比 42%"), "应带采购占比");
        assertTrue(ctx.contains("银行承兑汇票"), "应带付款偏好");

        // 轨迹应包含逐 KI 读图/取数/完成
        assertFalse(result.trace().isEmpty(), "应产生装配轨迹");
        boolean hasLoad = result.trace().stream()
                .anyMatch(s -> "LOAD_DATA".equals(s.phase()) && s.kiId().equals("KI-FRONT-001")
                        && s.dataPath() != null && s.dataPath().contains("supply-chain"));
        assertTrue(hasLoad, "KI-FRONT-001 应有 LOAD_DATA 供应链取数轨迹");
        boolean hasDone = result.trace().stream()
                .anyMatch(s -> "DONE".equals(s.phase()) && s.kiId().equals("KI-FRONT-001"));
        assertTrue(hasDone, "KI-FRONT-001 应有 DONE 完成轨迹");
    }

    @Test
    void assembleReadsContractAndElements() {
        Map<String, Object> files = new LinkedHashMap<>();
        files.put("05_knowledge/demo/activation-contract.json", CONTRACT);
        files.put("05_knowledge/demo/knowledge-map.yaml", "mapId: KM-CORP-RM-PREVISIT-DEMO");
        files.put("05_knowledge/demo/rules.yaml", RULES);
        files.put("05_knowledge/demo/elements/KI-FRONT-001/KE-FRONT-001-01.md", KE_001);
        files.put("05_knowledge/demo/elements/KI-FRONT-002/KE-FRONT-002-01.md", KE_002);

        SimulatedKnowledgeProvider provider = new SimulatedKnowledgeProvider(
                new InMemoryScenarioDataProvider(files));

        KnowledgeAssemblyResult result = provider.assemble("KM-CORP-RM-PREVISIT-DEMO", "客户：华东精工");

        assertEquals("KM-CORP-RM-PREVISIT-DEMO", result.scope());
        assertTrue(result.hasAssembledKi());
        assertEquals(List.of("KI-FRONT-001", "KI-FRONT-002"), result.assembledKiIds());
        assertTrue(result.knowledgeContext().contains("上游供应商列表"));
        assertTrue(result.knowledgeContext().contains("经营与财务概况"));
        assertTrue(result.knowledgeContext().contains("华东精工上游供应商清单。"));
        assertTrue(result.knowledgeContext().contains("可用额度不等同融资需求"));
        assertTrue(result.knowledgeContext().contains("客户：华东精工"));
        assertTrue(result.ruleRefs().contains("RUL-FRONT-001"));
        assertTrue(result.ruleRefs().contains("RUL-FRONT-002"));
        assertFalse(result.sourcePaths().isEmpty());
        assertTrue(result.sourcePaths().get(0).contains("KI-FRONT-001"));
    }

    @Test
    void resolveKnowledgeItemIdsReadsContract() {
        Map<String, Object> files = new LinkedHashMap<>();
        files.put(SimulatedKnowledgeProvider.ACTIVATION_CONTRACT, CONTRACT);

        SimulatedKnowledgeProvider provider = new SimulatedKnowledgeProvider(
                new InMemoryScenarioDataProvider(files));

        assertEquals(List.of("KI-FRONT-001", "KI-FRONT-002"),
                provider.resolveKnowledgeItemIds());
    }

    @Test
    void missingContractYieldsEmptyKi() {
        SimulatedKnowledgeProvider provider = new SimulatedKnowledgeProvider(
                new InMemoryScenarioDataProvider(Map.of()));

        assertTrue(provider.resolveKnowledgeItemIds().isEmpty());
        KnowledgeAssemblyResult result = provider.assemble("KM-X", "");
        assertFalse(result.hasAssembledKi());
        assertTrue(result.knowledgeContext().contains("KM-X"));
    }

    @Test
    void nonJsonFrontmatterFallsBackToFileName() {
        Map<String, Object> files = new LinkedHashMap<>();
        files.put("05_knowledge/demo/activation-contract.json", CONTRACT);
        files.put("05_knowledge/demo/elements/KI-FRONT-001/KE-FRONT-001-01.md", NON_JSON_FRONTMATTER);

        SimulatedKnowledgeProvider provider = new SimulatedKnowledgeProvider(
                new InMemoryScenarioDataProvider(files));

        KnowledgeAssemblyResult result = provider.assemble("KM-CORP-RM-PREVISIT-DEMO", "");
        assertTrue(result.knowledgeContext().contains("KE-FRONT-001-01"));
    }

    @Test
    void nullScopeRejected() {
        SimulatedKnowledgeProvider provider = new SimulatedKnowledgeProvider(
                new InMemoryScenarioDataProvider(Map.of()));
        assertThrows(NullPointerException.class, () -> provider.assemble(null, ""));
    }

    @Test
    void nullBusinessContextTreatedAsEmpty() {
        Map<String, Object> files = new LinkedHashMap<>();
        files.put("05_knowledge/demo/activation-contract.json", CONTRACT);
        SimulatedKnowledgeProvider provider = new SimulatedKnowledgeProvider(
                new InMemoryScenarioDataProvider(files));
        KnowledgeAssemblyResult result = provider.assemble("KM-X", null);
        assertFalse(result.knowledgeContext().contains("null"));
    }

    private static final class InMemoryScenarioDataProvider implements ScenarioDataProvider {
        private final Map<String, Object> files;

        private InMemoryScenarioDataProvider(Map<String, Object> files) {
            this.files = files;
        }

        @Override
        public String getProviderType() {
            return "in-memory";
        }

        @Override
        public boolean exists(String relativePath) {
            return files.containsKey(relativePath);
        }

        @Override
        public Optional<InputStream> openStream(String relativePath) {
            return readText(relativePath).map(text -> new ByteArrayInputStream(text.getBytes()));
        }

        @Override
        public Optional<String> readText(String relativePath) {
            return Optional.ofNullable(files.get(relativePath)).map(String::valueOf);
        }

        @Override
        public List<String> readLines(String relativePath) {
            return new ArrayList<>(readText(relativePath).map(t -> t.lines().toList()).orElse(List.of()));
        }

        @Override
        public List<String> listFiles(String relativeDir) {
            List<String> out = new ArrayList<>();
            String prefix = relativeDir + "/";
            for (String key : files.keySet()) {
                if (key.startsWith(prefix)) {
                    out.add(key.substring(prefix.length()));
                }
            }
            return out;
        }

        @Override
        public String getRootDescription() {
            return "in-memory-demo";
        }
    }
}