package com.gien.gits.api.config;

import org.junit.jupiter.api.Test;
import org.springframework.boot.ApplicationArguments;
import org.springframework.core.env.Environment;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

class ProdConfigValidatorTest {
    private final Environment env = mock(Environment.class);
    private final ProdConfigValidator v = new ProdConfigValidator(env);
    private final ApplicationArguments args = mock(ApplicationArguments.class);

    private void prop(String k, String val) { when(env.getProperty(eq(k), anyString())).thenReturn(val); }

    @Test void blankApiKeyFailsClosed() {
        prop("gits.security.api-key", "");
        assertThatThrownBy(() -> v.run(args)).isInstanceOf(IllegalStateException.class);
    }

    @Test void realLlmWithoutKeyFails() {
        prop("gits.security.api-key", "k");
        prop("engagement.llm.mode", "real");
        prop("engagement.llm.api-key", "");
        assertThatThrownBy(() -> v.run(args)).isInstanceOf(IllegalStateException.class);
    }

    @Test void httpCrmWithoutUrlFails() {
        prop("gits.security.api-key", "k");
        prop("engagement.llm.mode", "mock");
        prop("engagement.crm.mode", "http");
        prop("engagement.crm.writeback-url", "");
        assertThatThrownBy(() -> v.run(args)).isInstanceOf(IllegalStateException.class);
    }

    @Test void allCredentialsPresentPasses() {
        prop("gits.security.api-key", "k");
        prop("engagement.llm.mode", "real");
        prop("engagement.llm.api-key", "lk");
        prop("engagement.crm.mode", "http");
        prop("engagement.crm.writeback-url", "http://x");
        assertThatCode(() -> v.run(args)).doesNotThrowAnyException();
    }
}
