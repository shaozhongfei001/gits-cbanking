package com.gien.gits.api.config;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.core.env.Environment;

/**
 * P21: Production profile fail-closed validator 单元测试。
 */
class ProdConfigValidatorTest {

    @Mock private Environment env;

    private ProdConfigValidator validator;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        validator = new ProdConfigValidator(env);
    }

    @Test
    void run_apiKeyBlank_throwsIllegalState() {
        when(env.getProperty(eq("engagement.security.api-key"), anyString())).thenReturn("   ");

        assertThatThrownBy(() -> validator.run(null))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("engagement.security.api-key is required in production");
    }

    @Test
    void run_llmRealMissingKey_throwsIllegalState() {
        when(env.getProperty(eq("engagement.security.api-key"), anyString())).thenReturn("test-api-key");
        when(env.getProperty(eq("engagement.llm.mode"), anyString())).thenReturn("real");
        when(env.getProperty(eq("engagement.llm.api-key"), anyString())).thenReturn("");

        assertThatThrownBy(() -> validator.run(null))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("engagement.llm.api-key is required when LLM_MODE=real");
    }

    @Test
    void run_llmRealWithKey_passes() {
        when(env.getProperty(eq("engagement.security.api-key"), anyString())).thenReturn("test-api-key");
        when(env.getProperty(eq("engagement.llm.mode"), anyString())).thenReturn("real");
        when(env.getProperty(eq("engagement.llm.api-key"), anyString())).thenReturn("sk-test");

        assertThatCode(() -> validator.run(null)).doesNotThrowAnyException();
    }

    @Test
    void run_crmHttpMissingUrl_throwsIllegalState() {
        when(env.getProperty(eq("engagement.security.api-key"), anyString())).thenReturn("test-api-key");
        when(env.getProperty(eq("engagement.crm.mode"), anyString())).thenReturn("http");
        when(env.getProperty(eq("engagement.crm.writeback-url"), anyString())).thenReturn("");

        assertThatThrownBy(() -> validator.run(null))
                .isInstanceOf(IllegalStateException.class)
                .hasMessageContaining("engagement.crm.writeback-url is required when CRM_MODE=http");
    }

    @Test
    void run_crmHttpWithUrl_passes() {
        when(env.getProperty(eq("engagement.security.api-key"), anyString())).thenReturn("test-api-key");
        when(env.getProperty(eq("engagement.crm.mode"), anyString())).thenReturn("http");
        when(env.getProperty(eq("engagement.crm.writeback-url"), anyString())).thenReturn("http://localhost:9090/crm/writeback");

        assertThatCode(() -> validator.run(null)).doesNotThrowAnyException();
    }

    @Test
    void run_defaultMockModes_passes() {
        when(env.getProperty(eq("engagement.security.api-key"), anyString())).thenReturn("test-api-key");

        assertThatCode(() -> validator.run(null)).doesNotThrowAnyException();
    }
}
