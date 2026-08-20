package com.gien.gits.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.gien.gits.knowledge.KnowledgeElement;
import com.gien.gits.knowledge.KnowledgeElement.Source;
import com.gien.gits.knowledge.port.KnowledgeElementPort;
import com.gien.gits.knowledge.port.KnowledgeWikiPort;
import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * 验证 {@link KnowledgeAssembler#supplyChainMarkdown(List)} 从 KI-FRONT-001 KE 解析供应链图谱。
 */
class KnowledgeAssemblerSupplyChainTest {

    private static final String UPSTREAM_JSON =
            "[{\"supplierId\":\"SUP-001\",\"name\":\"华东精工智能制造有限公司\","
            + "\"category\":\"智能制造设备\",\"last12mPurchaseCnyWan\":3280,"
            + "\"pctOfAnnualPurchase\":42,\"priceTrend\":\"上行\","
            + "\"paymentPreference\":\"银行承兑汇票为主，接受供应链融资\"},"
            + "{\"supplierId\":\"SUP-002\",\"name\":\"杭州精工数控装备有限公司\","
            + "\"category\":\"数控部件\",\"last12mPurchaseCnyWan\":1950,"
            + "\"pctOfAnnualPurchase\":25,\"priceTrend\":\"平稳\","
            + "\"paymentPreference\":\"应收账款融资可接受\"}]";

    private static final String DOWNSTREAM_JSON =
            "[{\"customerId\":\"DST-01\",\"name\":\"中骏新能源科技\","
            + "\"industry\":\"新能源\",\"last12mSalesCnyWan\":5600,"
            + "\"pctOfAnnualSales\":34}]";

    private static final String INTERPRETATION =
            "角色定位：中游核心制造环节；议价能力评估：强；供应链稳定性判断：低风险";

    private KnowledgeElement el(String id, String name, String content) {
        return new KnowledgeElement("1.0.0", id, name, "K-Type-F", "KI-FRONT-001",
                content, new Source("graph(演示)", "AUTHORITATIVE"), List.of(), "DRAFT");
    }

    @Test
    void supplyChainParsesUpstreamAndDownstream() {
        KnowledgeElementPort elementPort = mock(KnowledgeElementPort.class);
        KnowledgeWikiPort wikiPort = mock(KnowledgeWikiPort.class);
        when(elementPort.listByKnowledgeItem("KI-FRONT-001")).thenReturn(List.of(
                el("KE-FRONT-001-01", "上游供应商列表", UPSTREAM_JSON),
                el("KE-FRONT-001-02", "下游客户列表", DOWNSTREAM_JSON),
                el("KE-FRONT-001-03", "供应链位置解读", INTERPRETATION)));
        KnowledgeAssembler assembler = new KnowledgeAssembler(elementPort, wikiPort);

        String markdown = assembler.supplyChainMarkdown(List.of("KI-FRONT-001"));

        assertThat(markdown).as("应含上游供应商 SUP-001")
                .contains("华东精工智能制造有限公司").contains("智能制造设备")
                .contains("采购(万) 3280").contains("采购占比% 42");
        assertThat(markdown).as("应含上游供应商 SUP-002")
                .contains("杭州精工数控装备有限公司").contains("数控部件");
        assertThat(markdown).as("应含下游客户")
                .contains("中骏新能源科技").contains("销售占比% 34");
        assertThat(markdown).as("应含位置解读（纯文本 KE 走解读分支）")
                .contains("议价能力评估");
    }

    @Test
    void supplyChainReturnsEmptyWhenNoElements() {
        KnowledgeElementPort elementPort = mock(KnowledgeElementPort.class);
        KnowledgeWikiPort wikiPort = mock(KnowledgeWikiPort.class);
        when(elementPort.listByKnowledgeItem("KI-FRONT-001")).thenReturn(List.of());
        KnowledgeAssembler assembler = new KnowledgeAssembler(elementPort, wikiPort);

        String markdown = assembler.supplyChainMarkdown(List.of("KI-FRONT-001"));
        assertThat(markdown).isBlank();
    }
}