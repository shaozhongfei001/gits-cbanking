package com.gien.gits.engagement.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.gien.gits.engagement.port.GateAssets;
import com.gien.gits.engagement.port.ServiceProposal;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

/**
 * G0-G5 闸门权威状态机（契约 v1.4 §4.2）：推进/阻滞/吸收建议/放行条件。
 */
class GateStateMachineTest {

    private final GateAssets assets = GateAssets.defaultServiceProposalFlow("CUST-CORP-0001");

    @Test
    void initialStatePendingAndCurrentGateG0() {
        GateStateMachine machine = new GateStateMachine("CUST-CORP-0001", assets);
        assertThat(machine.currentGate()).isEqualTo("G0");
        assertThat(machine.passedGates()).isEmpty();
        assertThat(machine.isReleaseReady()).isFalse();
    }

    @Test
    void passAdvancesGates() {
        GateStateMachine machine = new GateStateMachine("CUST-CORP-0001", assets);
        machine.pass("G0", "RM-01", "主档就绪");
        machine.pass("G1", "RM-01", "事实齐备");
        machine.pass("G2", "RM-01", "无 BLOCKING");
        machine.pass("G3", "RM-01", "对客版已审");

        assertThat(machine.passedGates()).containsExactly("G0", "G1", "G2", "G3");
        assertThat(machine.currentGate()).isEqualTo("G4");
        assertThat(machine.isReleaseReady()).isTrue();
    }

    @Test
    void releaseRequiresG1G2G3() {
        GateStateMachine machine = new GateStateMachine("CUST-CORP-0001", assets);
        machine.pass("G0", "RM-01", "主档就绪");
        machine.pass("G1", "RM-01", "事实齐备");
        // G2 未过
        assertThat(machine.isReleaseReady()).isFalse();
        machine.pass("G2", "RM-01", "规则合规");
        machine.pass("G3", "RM-01", "对客版已审");
        assertThat(machine.isReleaseReady()).isTrue();
    }

    @Test
    void blockHaltsRelease() {
        GateStateMachine machine = new GateStateMachine("CUST-CORP-0001", assets);
        machine.pass("G0", "RM-01", "主档就绪");
        machine.pass("G1", "RM-01", "事实齐备");
        machine.block("G2", "RM-01", "发现 BLOCKING 违规");

        assertThat(machine.currentGate()).isEqualTo("G2");
        assertThat(machine.isReleaseReady()).isFalse();
        assertThat(machine.snapshot().get("checklist"))
            .asList()
            .anyMatch(item -> "G2".equals(((Map<?, ?>) item).get("gate"))
                && "BLOCKED".equals(((Map<?, ?>) item).get("state")));
    }

    @Test
    void absorbRecommendationsSeedsPendingStates() {
        GateStateMachine machine = new GateStateMachine("CUST-CORP-0001", assets);
        ServiceProposal.GateRecommendations recs = new ServiceProposal.GateRecommendations(
            "G2", List.of("G0", "G1"), "READY_FOR_REVIEW",
            List.of(
                new ServiceProposal.GateCheck("G1", "PASSED", "事实基础", Map.of()),
                new ServiceProposal.GateCheck("G2", "READY_FOR_REVIEW", "规则合规", Map.of())),
            List.of("noBlockingViolations"));

        machine.absorb(recs);

        // G1 为 PASSED（吸收成功），G0 保持 PENDING（无推荐状态）
        assertThat(machine.snapshot().get("checklist")).asList()
            .anyMatch(item -> "G1".equals(((Map<?, ?>) item).get("gate"))
                && "PASSED".equals(((Map<?, ?>) item).get("state")));
        assertThat(machine.passedGates()).isEmpty(); // 建议非权威，不进入 passed 集合
        assertThat(machine.isReleaseReady()).isFalse();
    }

    @Test
    void unknownGateThrows() {
        GateStateMachine machine = new GateStateMachine("CUST-CORP-0001", assets);
        assertThatThrownBy(() -> machine.pass("G99", "RM-01", "x"))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("未知闸门");
    }
}
