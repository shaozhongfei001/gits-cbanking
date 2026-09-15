package com.gien.gits.api.config;

import com.gien.gits.adapter.crm.LoggingCrmWritebackChannel;
import com.gien.gits.adapter.llm.*;
import com.gien.gits.api.metrics.BusinessMetrics;
import org.junit.jupiter.api.Test;
import org.springframework.core.env.Environment;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

class EngagementConfigTest {
    private final EngagementConfig cfg = new EngagementConfig();
    private final BusinessMetrics m = mock(BusinessMetrics.class);
    private final Environment env = mock(Environment.class);

    @Test void mockLlmByDefault() {
        assertThat(cfg.llmClient("mock", env, m)).isInstanceOf(MockLlmClient.class);
    }

    @Test void realLlmWhenModeReal() {
        when(env.getProperty(anyString(), anyString())).thenAnswer(inv -> inv.getArgument(1));
        assertThat(cfg.llmClient("real", env, m)).isInstanceOf(RealLlmClient.class);
    }

    @Test void fallbackClaimAndLoggingChannel() {
        assertThat(cfg.claimReconciliationPort(m)).isNotNull();
        assertThat(cfg.loggingCrmWritebackChannel(m)).isInstanceOf(LoggingCrmWritebackChannel.class);
    }

    @Test void semanticStrategyWired() {
        assertThat(cfg.semanticPatternExtractionStrategy(mock(com.gien.gits.engagement.port.LlmClient.class))).isNotNull();
    }

    @Test void httpCrmChannelWired() {
        when(env.getProperty(anyString(), anyString())).thenAnswer(i -> i.getArgument(1));
        assertThat(cfg.httpCrmWritebackChannel(
            org.springframework.web.client.RestClient.builder(), "http://x", "tok", env, m)).isNotNull();
    }
}
