package com.gien.gits.adapter.skill;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

import com.gien.gits.engagement.port.LlmClient;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.Mockito;

/**
 * 验证 {@link FallbackSkillExecutionAdapter}：禁止本地补数的 skill 直接 SKILL_ERROR；
 * 其它 skill 可回落本地 {@link LlmClient}。
 */
class FallbackSkillExecutionAdapterTest {

    @Test
    void fallsBackToLlmAndMarksFallback() {
        LlmClient llmClient = Mockito.mock(LlmClient.class);
        when(llmClient.complete(anyString(), anyString()))
            .thenReturn("{\"content\":\"本地回落结果\"}");
        FallbackSkillExecutionAdapter adapter =
            new FallbackSkillExecutionAdapter(llmClient, "sys-prompt");

        SkillExecutionResult result = adapter.execute(
            new SkillExecutionCommand("skill-other-local-ok", "req-fb",
                "CUST-CORP-0001", Map.of("channel", "phone")));

        assertThat(result.isOk()).isTrue();
        assertThat(result.data()).containsEntry("fallback", true);
        assertThat(result.data()).containsEntry("skillId", "skill-other-local-ok");
        assertThat(result.trace()).isNotEmpty();
        assertThat(result.modelCalls().get(0).model()).isEqualTo("deterministic_fallback");
    }

    @Test
    void reportsSkillErrorWhenLocalLlmAlsoFails() {
        LlmClient llmClient = Mockito.mock(LlmClient.class);
        when(llmClient.complete(anyString(), anyString()))
            .thenThrow(new RuntimeException("本地 LLM 故障"));
        FallbackSkillExecutionAdapter adapter =
            new FallbackSkillExecutionAdapter(llmClient, "sys-prompt");

        SkillExecutionResult result = adapter.execute(
            new SkillExecutionCommand("skill-other-local-ok", "req-fail",
                "CUST-CORP-0001", Map.of()));

        assertThat(result.status()).isEqualTo(SkillExecutionStatus.SKILL_ERROR);
        assertThat(result.trace().get(0).status()).isEqualTo("failed");
    }

    @ParameterizedTest
    @ValueSource(strings = {
            "skill-customer-previsit-report",
            "skill-customer-outreach-script",
            "skill-customer-meeting-script",
            "bank-front-supply-chain-graph",
            "bank-front-product-recommendation"
    })
    void identitySkillsDoNotFillFromLocalLlm(String skillId) {
        LlmClient llmClient = Mockito.mock(LlmClient.class);
        FallbackSkillExecutionAdapter adapter =
            new FallbackSkillExecutionAdapter(llmClient, "sys-prompt");

        SkillExecutionResult result = adapter.execute(
            new SkillExecutionCommand(skillId, "req-nf",
                "CUST-CORP-0001", Map.of("customerId", "CUST-CORP-0001")));

        assertThat(result.status()).isEqualTo(SkillExecutionStatus.SKILL_ERROR);
        assertThat(result.data()).isEmpty();
        Mockito.verifyNoInteractions(llmClient);
    }
}
