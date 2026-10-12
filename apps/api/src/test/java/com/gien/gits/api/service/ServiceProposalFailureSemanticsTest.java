package com.gien.gits.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.adapter.skill.ServiceProposalMapper;
import com.gien.gits.engagement.port.KertContractMismatchException;
import com.gien.gits.engagement.port.ServiceProposalCommand;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

/**
 * PI · P1：SP-20 失败语义 —— <b>失败必须抛异常</b>，绝不以「HTTP 200 + SUCCESS 空壳」冒充成功。
 *
 * <p>背景（实测）：此前 {@code mapResult} 在 {@code result==null / !isOk / data==null} 与映射异常时
 * 一律 {@code return ServiceProposal.empty()}，而 {@code empty()} 把 {@code status} 写死为
 * {@code "SUCCESS"} ⇒ 前端只能显示「KERT 未返回建议书草稿」，**无法区分失败与真空结果**，
 * 且违反 {@code ServiceProposalPort} 的「失败必须抛异常（不静默降级）」。本类为该修复的机械证明。</p>
 */
@ExtendWith(MockitoExtension.class)
class ServiceProposalFailureSemanticsTest {

    private static final Map<String, Object> COMPLETE_CONTEXT = Map.of(
            "customerId", "CUST-X",
            "customerName", "客户X",
            "industry", "制造业",
            "enterpriseData", Map.of("basicInfo", Map.of()));

    @Mock
    private SkillExecutionPort skillExecutionPort;
    @Mock
    private ServiceProposalMapper mapper;
    @Mock
    private CustomerContextService customerContextService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    private ServiceProposalService service() {
        return new ServiceProposalService(skillExecutionPort, mapper, objectMapper, customerContextService);
    }

    private static SkillExecutionResult result(SkillExecutionStatus status,
                                              List<SkillExecutionResult.ErrorItem> errors) {
        return new SkillExecutionResult(status, "rid", Map.of("reportUrl", "/x"),
                errors, List.of(), List.of());
    }

    @Test
    @DisplayName("skill_error ⇒ 抛具名异常（不再返回 SUCCESS 空壳），并保留 KERT 错误码")
    void skillErrorThrowsInsteadOfEmptyShell() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class))).thenReturn(
                result(SkillExecutionStatus.SKILL_ERROR,
                        List.of(new SkillExecutionResult.ErrorItem("KERT_PERMISSION_DENIED", "路由未放行"))));

        assertThatThrownBy(() -> service().generate(new ServiceProposalCommand("r1", "CUST-X", COMPLETE_CONTEXT)))
                .isInstanceOf(SkillExecutionException.class)
                .hasMessageContaining("KERT_PERMISSION_DENIED")
                .hasMessageContaining("SKILL_ERROR");
    }

    @Test
    @DisplayName("策略退出 exit_policy_no_new_evidence ⇒ 具名异常且**状态可区分**（控制器据此回 409）")
    void policyExitIsDistinguishable() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class))).thenReturn(
                result(SkillExecutionStatus.EXIT_POLICY_NO_NEW_EVIDENCE, List.of()));

        SkillExecutionException ex = org.junit.jupiter.api.Assertions.assertThrows(
                SkillExecutionException.class,
                () -> service().generate(new ServiceProposalCommand("r1", "CUST-X", COMPLETE_CONTEXT)));

        assertThat(ex.status()).isEqualTo(SkillExecutionStatus.EXIT_POLICY_NO_NEW_EVIDENCE);
    }

    @Test
    @DisplayName("契约不符（data.result 映射失败）⇒ KertContractMismatchException 原样透出（控制器 502）")
    void contractMismatchPropagates() {
        when(skillExecutionPort.execute(any(SkillExecutionCommand.class))).thenReturn(
                result(SkillExecutionStatus.OK, List.of()));
        when(mapper.fromResult(any())).thenThrow(
                new KertContractMismatchException("KERT 契约不符：execute 成功但响应缺少 data.result 节点"));

        assertThatThrownBy(() -> service().generate(new ServiceProposalCommand("r1", "CUST-X", COMPLETE_CONTEXT)))
                .isInstanceOf(KertContractMismatchException.class)
                .hasMessageContaining("data.result");
    }
}
