package com.gien.gits.api.productknowledge;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

/**
 * {@link KertRetrievalAdapter} 存量覆盖补测。
 *
 * <p>该类此前 0 行覆盖（覆盖率门槛 0.7827 &lt; 0.80 的最大单点缺口），
 * 本类按「KERT 优先 → LightRAG 直连回退」的两级链路逐一覆盖：</p>
 * <ul>
 *   <li>KERT 命中 / 空实体 / 5xx / 4xx / 不可达 五条出口；</li>
 *   <li>LightRAG 直连 {@code /query/data}（结构化）→ {@code /query}（文本）回退链；</li>
 *   <li>防御性字段映射（{@code entity_name|entity|name|id} 等键回退）与
 *       {@code PRODUCT_ATTRIBUTE} 过滤；</li>
 *   <li>Markdown / 加粗 / 纯文本三种章节解析形态。</li>
 * </ul>
 *
 * <p>全部断言落在**外部可观察行为**（返回对象字段与最终异常类型）上，
 * 不依赖私有方法或实现细节。按适配器 Javadoc 约定用
 * {@code MockRestServiceServer.bindTo(builder)} 拦截，不发起真实网络请求。</p>
 */
class KertRetrievalAdapterTest {

    private static final String KERT_BASE = "http://kert.test";
    private static final String LIGHTRAG = "http://lightrag.test";
    private static final String PRODUCT = "PROD-CM-001";
    private static final String KERT_URL = KERT_BASE + "/v1/retrieval/query";
    private static final String LR_DATA_URL = LIGHTRAG + "/query/data";
    private static final String LR_TEXT_URL = LIGHTRAG + "/query";

    private static final String KERT_FULL = """
            {"data":{"entities":[{"entity_name":"产品目的","entity_type":"PRODUCT_ATTRIBUTE","description":"用于支付结算"}],
             "relations":[{"src_id":"产品目的","tgt_id":"使用方式","relation":"并列"}],
             "citations":[{"chunkId":"ck-1","docId":"doc/a.md","content":"原句","artifact":"art-1","planId":"plan-1","planHash":"hash-1"}],
             "evidenceClass":"DERIVED_RETRIEVAL","provenanceState":"DEMO","simulationOnly":true,
             "query":"产品目的","mode":"naive"}}
            """;

    private static final String KERT_EMPTY = "{\"data\":{\"entities\":[]}}";

    private record Harness(KertRetrievalAdapter adapter, MockRestServiceServer server) {
    }

    private Harness harness(String baseUrl, String lightragUrl, String apiKey) {
        RestClient.Builder builder = RestClient.builder();
        MockRestServiceServer server = MockRestServiceServer.bindTo(builder).build();
        return new Harness(new KertRetrievalAdapter(builder, baseUrl, lightragUrl, apiKey), server);
    }

    private Harness harness() {
        return harness(KERT_BASE, LIGHTRAG, null);
    }

    // ── 构造 ──────────────────────────────────────────────

    @Test
    void blankBaseUrlIsRejected() {
        assertThatThrownBy(() -> new KertRetrievalAdapter(RestClient.builder(), "  ", LIGHTRAG, "key"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("dsh.base-url");
    }

    @Test
    void trailingSlashInBaseUrlIsNormalised() {
        Harness h = harness(KERT_BASE + "/", null, null);
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_FULL, MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("产品目的", "naive", null));

        assertThat(response.entities()).hasSize(1);
        h.server().verify();
    }

    // ── KERT 命中 ─────────────────────────────────────────

    @Test
    void kertResponseIsMappedAndApiKeyTravelsAsBearerHeader() {
        Harness h = harness(KERT_BASE, null, "secret-key");
        h.server().expect(requestTo(KERT_URL))
                .andExpect(method(HttpMethod.POST))
                .andExpect(header("Authorization", "Bearer secret-key"))
                .andRespond(withSuccess(KERT_FULL, MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("产品目的", "naive", null));

        assertThat(response.productId()).isEqualTo(PRODUCT);
        assertThat(response.query()).isEqualTo("产品目的");
        assertThat(response.mode()).isEqualTo("naive");
        assertThat(response.simulationOnly()).isTrue();
        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("产品目的");
        assertThat(response.entities().get(0).type()).isEqualTo("PRODUCT_ATTRIBUTE");
        assertThat(response.entities().get(0).description()).isEqualTo("用于支付结算");
        assertThat(response.relations()).hasSize(1);
        assertThat(response.relations().get(0).source()).isEqualTo("产品目的");
        assertThat(response.relations().get(0).target()).isEqualTo("使用方式");
        assertThat(response.relations().get(0).type()).isEqualTo("并列");
        assertThat(response.citations()).hasSize(1);
        assertThat(response.citations().get(0).chunkId()).isEqualTo("ck-1");
        assertThat(response.citations().get(0).docId()).isEqualTo("doc/a.md");
        assertThat(response.citations().get(0).artifact()).isEqualTo("art-1");
        assertThat(response.citations().get(0).planId()).isEqualTo("plan-1");
        assertThat(response.citations().get(0).planHash()).isEqualTo("hash-1");
        h.server().verify();
    }

    @Test
    void kertPayloadWithoutDataWrapperAndWithFallbackKeysIsMapped() {
        Harness h = harness(KERT_BASE, null, null);
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess("""
                        {"entities":[{"name":"产品目的","type":"PRODUCT_ATTRIBUTE","description":"d"}],
                         "references":[{"reference_id":"ck-9","file_path":"b.md","content":"c"}]}
                        """, MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("产品目的");
        // 未声明 mode ⇒ 回落到请求侧解析出的缺省 hybrid
        assertThat(response.mode()).isEqualTo("hybrid");
        assertThat(response.citations()).hasSize(1);
        assertThat(response.citations().get(0).chunkId()).isEqualTo("ck-9");
        assertThat(response.citations().get(0).docId()).isEqualTo("b.md");
        h.server().verify();
    }

    @Test
    void requestCarriesResolvedModeAndProductScopedService() {
        Harness h = harness(KERT_BASE, null, null);
        h.server().expect(requestTo(KERT_URL))
                .andExpect(content().json("""
                        {"query":"产品目的","mode":"hybrid","service":"PROD-CM-001"}
                        """, false))
                .andRespond(withSuccess(KERT_FULL, MediaType.APPLICATION_JSON));

        h.adapter().retrieve(PRODUCT, new RetrievalRequest("产品目的", "   ", null));

        h.server().verify();
    }

    // ── KERT → LightRAG 回退 ──────────────────────────────

    @Test
    void emptyKertEntitiesFallBackToLightRagStructuredData() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess("""
                        {"status":"success","data":{
                          "entities":[{"entity_name":"产品目的","entity_type":"PRODUCT_ATTRIBUTE","description":"desc"}],
                          "relationships":[{"src_id":"x","tgt_id":"y","relation":"r"}],
                          "chunks":[{"chunkId":"ck-2","docId":"c.md","content":"cc"}]}}
                        """, MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.provenanceState()).isEqualTo("LIGHTRAG_DIRECT");
        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("产品目的");
        assertThat(response.relations()).hasSize(1);
        assertThat(response.citations()).hasSize(1);
        assertThat(response.citations().get(0).chunkId()).isEqualTo("ck-2");
        h.server().verify();
    }

    @Test
    void kertServerErrorFallsBackToLightRag() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withStatus(HttpStatus.INTERNAL_SERVER_ERROR));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("""
                        {"data":{"entities":[{"entity_name":"产品目的","entity_type":"PRODUCT_ATTRIBUTE","description":"d"}]}}
                        """, MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.provenanceState()).isEqualTo("LIGHTRAG_DIRECT");
        assertThat(response.entities()).hasSize(1);
        h.server().verify();
    }

    @Test
    void lightRagDataFiltersNonProductAttributeEntitiesAndSkipsNonObjects() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("""
                        {"data":{
                          "entities":[{"entity_name":"噪音","entity_type":"OTHER","description":"d"},
                                      "not-an-object",
                                      {"entity_name":"无描述","entity_type":"PRODUCT_ATTRIBUTE"},
                                      {"entity_name":"产品目的","entity_type":"PRODUCT_ATTRIBUTE","description":"desc"}],
                          "relations":[{"head":"a","tail":"b","type":"r"}],
                          "references":[{"chunk_id":"ck-3","file_path":"e.md"}]}}
                        """, MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        // 仅 PRODUCT_ATTRIBUTE 且 name/description 齐备的实体被保留
        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("产品目的");
        assertThat(response.relations()).hasSize(1);
        assertThat(response.relations().get(0).source()).isEqualTo("a");
        assertThat(response.relations().get(0).type()).isEqualTo("r");
        assertThat(response.citations()).hasSize(1);
        assertThat(response.citations().get(0).chunkId()).isEqualTo("ck-3");
        h.server().verify();
    }

    @Test
    void lightRagDataFailureFallsThroughToTextEndpoint() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withStatus(HttpStatus.BAD_GATEWAY));
        h.server().expect(requestTo(LR_TEXT_URL))
                .andRespond(withSuccess("{\"response\":\"## 产品目的\\n用于支付结算。\"}",
                        MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("产品目的");
        assertThat(response.entities().get(0).type()).isEqualTo("PRODUCT_ATTRIBUTE");
        h.server().verify();
    }

    @Test
    void lightRagTextEndpointParsesMultipleMarkdownSections() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("{\"data\":{\"entities\":[]}}", MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_TEXT_URL))
                .andRespond(withSuccess(
                        "{\"response\":\"## 产品目的\\n用于支付结算。\\n## 使用方式\\n额度内提款。\"}",
                        MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.entities()).extracting(RetrievalEntity::name)
                .containsExactly("产品目的", "使用方式");
        h.server().verify();
    }

    @Test
    void lightRagTextEndpointParsesBoldSections() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("{\"data\":{\"entities\":[]}}", MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_TEXT_URL))
                .andRespond(withSuccess("{\"response\":\"**计息口径**\\n按日计息。\"}",
                        MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("计息口径");
        assertThat(response.entities().get(0).description()).isEqualTo("按日计息。");
        h.server().verify();
    }

    @Test
    void lightRagTextWithoutSectionsIsKeptAsRawTextEntity() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("{\"data\":{\"entities\":[]}}", MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_TEXT_URL))
                .andRespond(withSuccess("{\"response\":\"没有标题的说明文字\"}", MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("LightRAG_RESPONSE");
        assertThat(response.entities().get(0).type()).isEqualTo("RAW_TEXT");
        h.server().verify();
    }

    @Test
    void emptyLightRagDataPayloadReturnsNullAndFallsThroughToText() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        // data.entities 缺失 ⇒ 顶层 entities 也缺失 ⇒ 无实体 ⇒ 走文本端点
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("{\"status\":\"success\"}", MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_TEXT_URL))
                .andRespond(withSuccess("{\"response\":\"## 适用主体\\n对公客户。\"}",
                        MediaType.APPLICATION_JSON));

        RetrievalResponse response = h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null));

        assertThat(response.entities()).hasSize(1);
        assertThat(response.entities().get(0).name()).isEqualTo("适用主体");
        h.server().verify();
    }

    // ── fail-closed 出口 ──────────────────────────────────

    @Test
    void kertServerErrorWithoutLightRagIsFailedClosed() {
        Harness h = harness(KERT_BASE, "   ", null);
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withStatus(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body("{\"error\":{\"code\":\"KERT_DOWN\",\"message\":\"boom\"}}")
                        .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null)))
                .isInstanceOf(KnowledgeSourceUnavailableException.class)
                .hasMessageContaining("不可用");
        h.server().verify();
    }

    @Test
    void kertClientErrorWithoutLightRagIsFailedClosed() {
        Harness h = harness(KERT_BASE, null, null);
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withStatus(HttpStatus.BAD_REQUEST)
                        .body("{\"error\":{\"code\":\"BAD_QUERY\",\"message\":\"invalid\"}}")
                        .contentType(MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null)))
                .isInstanceOf(KnowledgeSourceUnavailableException.class);
        h.server().verify();
    }

    @Test
    void kertErrorBodyWithoutJsonErrorNodeIsTolerated() {
        Harness h = harness(KERT_BASE, null, null);
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withStatus(HttpStatus.BAD_GATEWAY)
                        .body("plain-text-error")
                        .contentType(MediaType.TEXT_PLAIN));

        assertThatThrownBy(() -> h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null)))
                .isInstanceOf(KnowledgeSourceUnavailableException.class);
        h.server().verify();
    }

    @Test
    void kertUnreachableWithoutLightRagIsFailedClosed() {
        KertRetrievalAdapter adapter =
                new KertRetrievalAdapter(RestClient.builder(), "http://127.0.0.1:1", null, null);

        assertThatThrownBy(() -> adapter.retrieve(PRODUCT, new RetrievalRequest("q", null, null)))
                .isInstanceOf(KnowledgeSourceUnavailableException.class)
                .hasMessageContaining("不可用");
    }

    @Test
    void lightRagTextEndpointHttpErrorIsFailedClosed() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("{\"data\":{\"entities\":[]}}", MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_TEXT_URL))
                .andRespond(withStatus(HttpStatus.BAD_GATEWAY));

        assertThatThrownBy(() -> h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null)))
                .isInstanceOf(KnowledgeSourceUnavailableException.class)
                .hasMessageContaining("LightRAG 直连失败");
        h.server().verify();
    }

    @Test
    void lightRagApiKeyTravelsAsBearerHeaderOnBothEndpoints() {
        Harness h = harness(KERT_BASE, LIGHTRAG, "lr-key");
        h.server().expect(requestTo(KERT_URL))
                .andExpect(header("Authorization", "Bearer lr-key"))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andExpect(header("Authorization", "Bearer lr-key"))
                .andRespond(withSuccess("""
                        {"data":{"entities":[{"entity_name":"产品目的","entity_type":"PRODUCT_ATTRIBUTE","description":"d"}]}}
                        """, MediaType.APPLICATION_JSON));

        assertThat(h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null)).entities()).hasSize(1);
        h.server().verify();
    }

    @Test
    void lightRagUnparsableTextPayloadIsFailedClosed() {
        Harness h = harness();
        h.server().expect(requestTo(KERT_URL))
                .andRespond(withSuccess(KERT_EMPTY, MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_DATA_URL))
                .andRespond(withSuccess("{\"data\":{\"entities\":[]}}", MediaType.APPLICATION_JSON));
        h.server().expect(requestTo(LR_TEXT_URL))
                .andRespond(withSuccess("not-json", MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> h.adapter().retrieve(PRODUCT, new RetrievalRequest("q", null, null)))
                .isInstanceOf(KnowledgeSourceUnavailableException.class)
                .hasMessageContaining("解析失败");
        h.server().verify();
    }
}
