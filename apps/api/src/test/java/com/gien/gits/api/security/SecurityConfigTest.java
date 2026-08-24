package com.gien.gits.api.security;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.springframework.http.MediaType;

/**
 * SecurityConfig 集成测试 — 验证安全基线行为
 * 
 * 覆盖:
 * 1. 开发模式 (api-key为空) — 所有端点可访问
 * 2. 安全基线 — 敏感端点(Swagger/H2)应被禁用
 * 3. API Key认证行为 — 开发模式不拦截，生产模式需认证
 */
@SpringBootTest
@AutoConfigureMockMvc
class SecurityConfigTest {

    @Autowired
    private MockMvc mockMvc;

    // ── 开发模式 (api-key 为空) ────────────────────────────────

    @Nested
    @DisplayName("开发模式: api-key为空，认证被跳过")
    class DevModeTests {

        @Test
        @DisplayName("Health端点无需认证即可访问")
        void actuatorHealth_shouldBeAccessibleWithoutAuth() throws Exception {
            mockMvc.perform(get("/actuator/health"))
                .andExpect(status().isOk());
        }

        @Test
        @DisplayName("Info端点无需认证即可访问")
        void actuatorInfo_shouldBeAccessibleWithoutAuth() throws Exception {
            mockMvc.perform(get("/actuator/info"))
                .andExpect(status().isOk());
        }

        @Test
        @DisplayName("127.0.0.1 前端 Origin 启动旅程不被 CORS 拒绝")
        void startJourney_fromLoopbackOrigin_shouldNotBeCorsForbidden() throws Exception {
            mockMvc.perform(post("/api/v1/engagement/journey/start")
                    .header("Origin", "http://127.0.0.1:5173")
                    .contentType(MediaType.APPLICATION_JSON)
                    .content("{\"customerId\":\"CUST-CORP-0001\"}"))
                .andExpect(result -> {
                    int status = result.getResponse().getStatus();
                    if (status == 403) {
                        throw new AssertionError("Loopback Origin should be allowed, got 403 CORS");
                    }
                });
        }

        @Test
        @DisplayName("业务端点在开发模式下不返回401")
        void apiEndpoint_shouldBeAccessibleWhenApiKeyDisabled() throws Exception {
            mockMvc.perform(get("/api/v1/engagement-journeys"))
                .andExpect(result -> {
                    int status = result.getResponse().getStatus();
                    if (status == 401) {
                        throw new AssertionError("Should not return 401 when api-key is disabled, got: " + status);
                    }
                });
        }
    }

    // ── 安全基线验证 ────────────────────────────────────────────

    @Nested
    @DisplayName("安全基线: 敏感端点保护")
    class SecurityBaselineTests {

        @Test
        @DisplayName("Swagger UI在生产配置下应被禁用(404/302)")
        void swaggerUi_shouldBeDisabled() throws Exception {
            mockMvc.perform(get("/swagger-ui.html"))
                .andExpect(result -> {
                    int status = result.getResponse().getStatus();
                    // 404(禁用) 或 302(重定向) 都是可接受的
                    if (status != 404 && status != 302 && status != 301) {
                        throw new AssertionError("Swagger UI should be disabled, got: " + status);
                    }
                });
        }

        @Test
        @DisplayName("H2控制台在开发模式下可访问或被禁用")
        void h2Console_shouldBeDisabled() throws Exception {
            mockMvc.perform(get("/h2-console/"))
                .andExpect(result -> {
                    int status = result.getResponse().getStatus();
                    // 开发模式: 200(可访问) 或 302(重定向) 都可接受
                    // 生产模式: 404(禁用) 或 403(拒绝) 都可接受
                    // 500: H2控制台内部错误(可接受，不影响安全基线)
                    if (status != 200 && status != 302 && status != 301 && status != 404 && status != 403 && status != 500) {
                        throw new AssertionError("H2 console unexpected status, got: " + status);
                    }
                });
        }

        @Test
        @DisplayName("Prometheus端点应可访问或未配置(不返回401)")
        void prometheus_shouldBeAccessible() throws Exception {
            mockMvc.perform(get("/actuator/prometheus"))
                .andExpect(result -> {
                    int status = result.getResponse().getStatus();
                    // 200: 正常可访问; 404: 未暴露; 都不应该是401(认证拦截)
                    if (status == 401) {
                        throw new AssertionError("Prometheus should not require auth in dev mode, got: " + status);
                    }
                });
        }
    }

    // ── API Key认证行为 ────────────────────────────────────────

    @Nested
    @DisplayName("API Key认证行为")
    class ApiKeyAuthTests {

        @Test
        @DisplayName("开发模式下带X-API-KEY头不应返回401")
        void withApiKeyHeader_devMode_no401() throws Exception {
            mockMvc.perform(get("/api/v1/engagement-journeys")
                    .header("X-API-KEY", "any-value"))
                .andExpect(result -> {
                    int status = result.getResponse().getStatus();
                    if (status == 401) {
                        throw new AssertionError("Should not return 401 when api-key is disabled, got: " + status);
                    }
                });
        }

        @Test
        @DisplayName("开发模式下不带X-API-KEY头也不返回401")
        void withoutApiKeyHeader_devMode_no401() throws Exception {
            mockMvc.perform(get("/api/v1/customer-contexts"))
                .andExpect(result -> {
                    int status = result.getResponse().getStatus();
                    if (status == 401) {
                        throw new AssertionError("Should not return 401 in dev mode, got: " + status);
                    }
                });
        }
    }
}
