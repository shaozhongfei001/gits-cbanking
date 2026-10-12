package com.gien.gits.adapter.skill;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import com.gien.gits.engagement.port.GateAssets;
import com.gien.gits.engagement.port.SkillExecutionException;

import java.util.LinkedHashMap;
import java.util.Map;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

/**
 * {@link DshHttpSkillGateAdapter} 存量覆盖补测。
 *
 * <p>该类此前 0 行覆盖（jest 图：78 missed / 0 covered），是 apps/api 覆盖率门槛
 * （0.7827 &lt; 0.80）的主要缺口之一。本类按"契约 v1.4 §4"的两个端点逐一覆盖：
 * 资产读取（含 {@code data} 包装 / 顶层两种形态、{@code criteria} 与 {@code must} 两种字段、
 * {@code description} 与 {@code assetPath} 两种说明来源）与决策镜像（含字段改名、
 * 幂等缺省、失败可重试返回 false 而不影响 GITS 权威状态）。</p>
 *
 * <p>按类 Javadoc 的既定约定，用 {@code MockRestServiceServer.bindTo(builder)} 拦截，
 * 不发起真实网络请求。</p>
 */
class DshHttpSkillGateAdapterTest {

    private static final String BASE = "http://dsh.test";
    private static final String CUSTOMER = "CUST-CORP-0001";

    /** 测试夹具：适配器 + 与之绑定的 Mock 服务端。 */
    private record Harness(DshHttpSkillGateAdapter adapter, MockRestServiceServer server) {
    }

    private Harness harness(String baseUrl) {
        RestClient.Builder builder = RestClient.builder();
        MockRestServiceServer server = MockRestServiceServer.bindTo(builder).build();
        return new Harness(new DshHttpSkillGateAdapter(builder, baseUrl), server);
    }

    // ── 构造 ──────────────────────────────────────────────

    @Test
    void blankBaseUrlIsRejected() {
        assertThatThrownBy(() -> new DshHttpSkillGateAdapter(RestClient.builder(), "  "))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("dsh.base-url");
    }

    @Test
    void trailingSlashInBaseUrlIsNormalised() {
        Harness h = harness(BASE + "/");
        h.server().expect(requestTo(BASE + "/api/skill/gates/" + CUSTOMER))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("{\"gates\":[]}", MediaType.APPLICATION_JSON));

        h.adapter().fetchGateAssets(CUSTOMER);

        h.server().verify();
    }

    // ── fetchGateAssets ───────────────────────────────────

    @Test
    void fetchGateAssetsReadsDataWrapperWithCriteriaAndDescription() {
        Harness h = harness(BASE);
        h.server().expect(requestTo(BASE + "/api/skill/gates/" + CUSTOMER))
                .andRespond(withSuccess("""
                        {"data":{"schemaVersion":"1.0.0","customerId":"CUST-CORP-0001",
                         "flowName":"service-proposal",
                         "gates":[{"gateId":"G0","name":"准备就绪","description":"ContextPackage 就绪",
                                   "criteria":["customerMasterLoaded","contextPackageComplete"]}]}}
                        """, MediaType.APPLICATION_JSON));

        GateAssets assets = h.adapter().fetchGateAssets(CUSTOMER);

        assertThat(assets.schemaVersion()).isEqualTo("1.0.0");
        assertThat(assets.customerId()).isEqualTo(CUSTOMER);
        assertThat(assets.flowName()).isEqualTo("service-proposal");
        assertThat(assets.gates()).hasSize(1);
        assertThat(assets.gates().get(0).gateId()).isEqualTo("G0");
        assertThat(assets.gates().get(0).name()).isEqualTo("准备就绪");
        assertThat(assets.gates().get(0).description()).isEqualTo("ContextPackage 就绪");
        assertThat(assets.gates().get(0).criteria())
                .containsExactly("customerMasterLoaded", "contextPackageComplete");
        h.server().verify();
    }

    @Test
    void fetchGateAssetsReadsTopLevelPayloadWithMustAndAssetPathFallbacks() {
        Harness h = harness(BASE);
        // KERT 真实响应为顶层 {customerId, gates:[...]}（无 data 包装）；
        // 说明缺省时取 assetPath，条件缺省时取 must。
        h.server().expect(requestTo(BASE + "/api/skill/gates/" + CUSTOMER))
                .andRespond(withSuccess("""
                        {"customerId":"CUST-CORP-0001",
                         "gates":[{"gateId":"G1","name":"事实基础",
                                   "assetPath":"90_control/gates/G1.md","must":["factCoverage"]}]}
                        """, MediaType.APPLICATION_JSON));

        GateAssets assets = h.adapter().fetchGateAssets(CUSTOMER);

        assertThat(assets.customerId()).isEqualTo(CUSTOMER);
        assertThat(assets.flowName()).isEqualTo("service-proposal");
        assertThat(assets.gates()).hasSize(1);
        assertThat(assets.gates().get(0).description()).isEqualTo("90_control/gates/G1.md");
        assertThat(assets.gates().get(0).criteria()).containsExactly("factCoverage");
        h.server().verify();
    }

    @Test
    void fetchGateAssetsFallsBackToTopLevelWhenDataIsEmptyObject() {
        Harness h = harness(BASE);
        h.server().expect(requestTo(BASE + "/api/skill/gates/" + CUSTOMER))
                .andRespond(withSuccess("""
                        {"data":{},"customerId":"CUST-CORP-0001","gates":[]}
                        """, MediaType.APPLICATION_JSON));

        GateAssets assets = h.adapter().fetchGateAssets(CUSTOMER);

        assertThat(assets.gates()).isEmpty();
        assertThat(assets.customerId()).isEqualTo(CUSTOMER);
        h.server().verify();
    }

    @Test
    void fetchGateAssetsDefaultsCustomerIdAndSchemaWhenAbsent() {
        Harness h = harness(BASE);
        h.server().expect(requestTo(BASE + "/api/skill/gates/" + CUSTOMER))
                .andRespond(withSuccess("{\"gates\":[]}", MediaType.APPLICATION_JSON));

        GateAssets assets = h.adapter().fetchGateAssets(CUSTOMER);

        assertThat(assets.schemaVersion()).isEqualTo("1.0.0");
        assertThat(assets.customerId()).isEqualTo(CUSTOMER);
        h.server().verify();
    }

    @Test
    void fetchGateAssetsMapsHttpErrorToSkillExecutionException() {
        Harness h = harness(BASE);
        h.server().expect(requestTo(BASE + "/api/skill/gates/" + CUSTOMER))
                .andRespond(withStatus(HttpStatus.INTERNAL_SERVER_ERROR));

        assertThatThrownBy(() -> h.adapter().fetchGateAssets(CUSTOMER))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("SKILL GATE HTTP 500");
        h.server().verify();
    }

    @Test
    void fetchGateAssetsMapsUnparsableBodyToSkillExecutionException() {
        Harness h = harness(BASE);
        h.server().expect(requestTo(BASE + "/api/skill/gates/" + CUSTOMER))
                .andRespond(withSuccess("not-json", MediaType.APPLICATION_JSON));

        assertThatThrownBy(() -> h.adapter().fetchGateAssets(CUSTOMER))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("解析失败");
        h.server().verify();
    }

    @Test
    void fetchGateAssetsMapsUnreachableHostToSkillExecutionException() {
        // 端口 1 必然 ECONNREFUSED：覆盖「dsh 不可达」分支（不经过 Mock 服务端）
        DshHttpSkillGateAdapter adapter =
                new DshHttpSkillGateAdapter(RestClient.builder(), "http://127.0.0.1:1");

        assertThatThrownBy(() -> adapter.fetchGateAssets(CUSTOMER))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("dsh 不可达");
    }

    // ── mirrorGateAudit ───────────────────────────────────

    @Test
    void mirrorGateAuditReturnsRecordedFlagAndAlignsContractFields() {
        Harness h = harness(BASE);
        Map<String, Object> entry = new LinkedHashMap<>();
        entry.put("gateCode", "G2");   // 契约字段对齐：gateCode → gate
        entry.put("decision", "APPROVE");

        h.server().expect(requestTo(BASE + "/api/skill/gates/audit"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(header("Content-Type", MediaType.APPLICATION_JSON_VALUE))
                .andExpect(content().json("""
                        {"gate":"G2","customerId":"CUST-CORP-0001","decidedBy":"GITS:SYSTEM","decision":"APPROVE"}
                        """, false))
                .andRespond(withSuccess("{\"recorded\":true}", MediaType.APPLICATION_JSON));

        assertThat(h.adapter().mirrorGateAudit(CUSTOMER, entry)).isTrue();
        h.server().verify();
        // 不修改调用方 Map（复制后改名）
        assertThat(entry).containsKey("gateCode").doesNotContainKey("gate");
    }

    @Test
    void mirrorGateAuditDoesNotOverrideCallerProvidedGateAndDecider() {
        Harness h = harness(BASE);
        Map<String, Object> entry = new LinkedHashMap<>();
        entry.put("gate", "G3");
        entry.put("customerId", "CUST-OTHER");
        entry.put("decidedBy", "RM-ZW-001");

        h.server().expect(requestTo(BASE + "/api/skill/gates/audit"))
                .andExpect(content().json("""
                        {"gate":"G3","customerId":"CUST-OTHER","decidedBy":"RM-ZW-001"}
                        """, false))
                .andRespond(withSuccess("{\"recorded\":true}", MediaType.APPLICATION_JSON));

        assertThat(h.adapter().mirrorGateAudit(CUSTOMER, entry)).isTrue();
        h.server().verify();
    }

    @Test
    void mirrorGateAuditReturnsFalseWhenRecordedFlagIsNotBoolean() {
        Harness h = harness(BASE);
        h.server().expect(requestTo(BASE + "/api/skill/gates/audit"))
                .andRespond(withSuccess("{\"recorded\":\"yes\"}", MediaType.APPLICATION_JSON));

        assertThat(h.adapter().mirrorGateAudit(CUSTOMER, Map.of("gate", "G2"))).isFalse();
        h.server().verify();
    }

    @Test
    void mirrorGateAuditReturnsFalseOnHttpErrorSoCallerCanRetry() {
        Harness h = harness(BASE);
        h.server().expect(requestTo(BASE + "/api/skill/gates/audit"))
                .andRespond(withStatus(HttpStatus.BAD_GATEWAY));

        // 镜像失败不得抛出（不影响 GITS 权威状态），返回 false 供重试
        assertThat(h.adapter().mirrorGateAudit(CUSTOMER, Map.of("gate", "G2"))).isFalse();
        h.server().verify();
    }

    @Test
    void mirrorGateAuditReturnsFalseOnNetworkError() {
        DshHttpSkillGateAdapter adapter =
                new DshHttpSkillGateAdapter(RestClient.builder(), "http://127.0.0.1:1");

        assertThat(adapter.mirrorGateAudit(CUSTOMER, Map.of("gate", "G2"))).isFalse();
    }
}
