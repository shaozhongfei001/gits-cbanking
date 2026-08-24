package com.gien.gits.api.dto;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;

import org.junit.jupiter.api.Test;

/**
 * P24: PreparedPrevisitResponse record 单元测试（紧凑构造 null 归一化 + 6 参便捷构造）。
 */
class PreparedPrevisitResponseTest {

    @Test
    void compactConstructor_normalizesNullLists() {
        PreparedPrevisitResponse r = new PreparedPrevisitResponse(
                null, null, null, null, null, null, null, null, null);

        assertThat(r.assemblyTrace()).isEmpty();
        assertThat(r.skillSections()).isEmpty();
    }

    @Test
    void compactConstructor_preservesAndCopiesLists() {
        List<AssemblyTraceStep> trace = List.of(
                new AssemblyTraceStep("init", "OK", "初始化", "KI-001"));
        List<SkillReportSection> sections = List.of(
                new SkillReportSection("行业定位", "上游以制造业为主"));

        PreparedPrevisitResponse r = new PreparedPrevisitResponse(
                null, null, null, null, "supply-chain-markdown", trace,
                "R1 访前报告", "摘要", sections);

        assertThat(r.assemblyTrace()).containsExactly(new AssemblyTraceStep("init", "OK", "初始化", "KI-001"));
        assertThat(r.skillSections()).containsExactly(new SkillReportSection("行业定位", "上游以制造业为主"));
        assertThat(r.skillReportTitle()).isEqualTo("R1 访前报告");
        assertThat(r.skillExecutiveSummary()).isEqualTo("摘要");
        assertThatThrownBy(() -> r.assemblyTrace().add(null))
                .isInstanceOf(UnsupportedOperationException.class);
    }

    @Test
    void sixArgConstructor_fillsSkillDefaults() {
        List<AssemblyTraceStep> trace = List.of(
                new AssemblyTraceStep("init", "OK", "初始化"));

        PreparedPrevisitResponse r = new PreparedPrevisitResponse(
                null, null, null, null, "md", trace);

        assertThat(r.assemblyTrace()).containsExactly(new AssemblyTraceStep("init", "OK", "初始化"));
        assertThat(r.skillReportTitle()).isNull();
        assertThat(r.skillExecutiveSummary()).isNull();
        assertThat(r.skillSections()).isEmpty();
    }
}
