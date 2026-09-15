package com.gien.gits.api.dto;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import com.gien.gits.engagement.port.SkillExecutionResult;
import org.junit.jupiter.api.Test;

/**
 * P24: AssemblyTraceStep record 单元测试（3 参便捷构造 + from 静态工厂）。
 */
class AssemblyTraceStepTest {

    @Test
    void threeArgConstructor_setsKiIdNull() {
        AssemblyTraceStep step = new AssemblyTraceStep("assemble", "OK", "装配完成");

        assertThat(step.phase()).isEqualTo("assemble");
        assertThat(step.status()).isEqualTo("OK");
        assertThat(step.message()).isEqualTo("装配完成");
        assertThat(step.kiId()).isNull();
    }

    @Test
    void from_null_returnsEmptyList() {
        assertThat(AssemblyTraceStep.from(null)).isEmpty();
    }

    @Test
    void from_empty_returnsEmptyList() {
        assertThat(AssemblyTraceStep.from(List.of())).isEmpty();
    }

    @Test
    void from_mapsAllSteps() {
        SkillExecutionResult.TraceStep init = new SkillExecutionResult.TraceStep(
                "init", "OK", "初始化", "KI-FRONT-001");
        SkillExecutionResult.TraceStep assemble = new SkillExecutionResult.TraceStep(
                "assemble", "WARN", "部分条目缺失");

        List<AssemblyTraceStep> steps = AssemblyTraceStep.from(List.of(init, assemble));

        assertThat(steps).hasSize(2);
        assertThat(steps.get(0).phase()).isEqualTo("init");
        assertThat(steps.get(0).status()).isEqualTo("OK");
        assertThat(steps.get(0).message()).isEqualTo("初始化");
        assertThat(steps.get(0).kiId()).isEqualTo("KI-FRONT-001");
        assertThat(steps.get(1).phase()).isEqualTo("assemble");
        assertThat(steps.get(1).status()).isEqualTo("WARN");
        assertThat(steps.get(1).kiId()).isNull();
    }
}
