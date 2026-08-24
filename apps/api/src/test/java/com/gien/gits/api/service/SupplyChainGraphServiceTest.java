package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.gien.gits.api.dto.SupplyChainGraphExecuteRequest;
import com.gien.gits.api.dto.SupplyChainGraphReport;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import com.gien.gits.ontology.Customer;
import com.gien.gits.ontology.CustomerTier;
import com.gien.gits.ontology.EnterpriseScale;
import com.gien.gits.ontology.Industry;
import com.gien.gits.ontology.ListedStatus;
import com.gien.gits.ontology.RiskLevel;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

class SupplyChainGraphServiceTest {

    private SkillExecutionPort skillPort;
    private CustomerContextService customerContextService;
    private SupplyChainGraphReportCache cache;
    private SupplyChainGraphService service;
    private Customer customer;

    @BeforeEach
    void setUp() {
        skillPort = mock(SkillExecutionPort.class);
        customerContextService = mock(CustomerContextService.class);
        cache = new SupplyChainGraphReportCache(Duration.ofMinutes(10), Clock.systemUTC());
        service = new SupplyChainGraphService(
                skillPort, customerContextService, cache, Clock.systemUTC());
        customer = new Customer(
                "CUST-001", "杭州智造", "杭州智造精密齿轮有限公司",
                "91330100MA27XXXXXX", LocalDate.of(2010, 1, 1), 50000000L,
                Industry.MANUFACTURING.name(), "浙江省",
                EnterpriseScale.LARGE.name(), CustomerTier.KEY.name(),
                LocalDate.of(2018, 1, 1), "RM-001", "张经理", "杭州分行",
                false, ListedStatus.UNLISTED.name(), RiskLevel.MEDIUM.name(),
                List.of("齿轮"), List.of(), "中游制造");
        when(customerContextService.findCustomer("CUST-001")).thenReturn(Optional.of(customer));
    }

    @Test
    void executeMapsDkwsResultWithoutInventingNodes() {
        when(skillPort.execute(any(SkillExecutionCommand.class))).thenReturn(okResult(completePayload()));

        SupplyChainGraphReport report = service.execute(
                new SupplyChainGraphExecuteRequest("CUST-001", "SCG-1"));

        assertEquals("SCG-1", report.requestId());
        assertEquals("ok", report.status());
        assertEquals("complete", report.result().buildStatus());
        assertEquals(7, report.result().nodes().size());
        assertEquals(6, report.result().edges().size());
        assertEquals("中游核心制造", report.result().interpretation().supplyChainPosition());
        assertEquals("/supply-chain-report/SCG-1", report.reportUrl());
        assertEquals("SCG-1", service.getReport("SCG-1").requestId());
        ArgumentCaptor<SkillExecutionCommand> captor = ArgumentCaptor.forClass(SkillExecutionCommand.class);
        verify(skillPort).execute(captor.capture());
        assertEquals("CUST-001", captor.getValue().request().get("customerId"));
        assertEquals(1, captor.getValue().request().size());
        assertTrue(!captor.getValue().request().containsKey("knowledgeContext"));
        assertTrue(!captor.getValue().request().containsKey("structuredFacts"));
    }

    @Test
    void executePartialKeepsEmptyNodes() {
        when(skillPort.execute(any(SkillExecutionCommand.class))).thenReturn(okResult(Map.of(
                "skillId", "bank-front-supply-chain-graph",
                "result", Map.of(
                        "schemaVersion", "1.0",
                        "buildStatus", "partial",
                        "nodes", List.of(),
                        "edges", List.of(),
                        "interpretation", Map.of(
                                "overallAssessment", "输入不足，仅部分降级",
                                "followUpQuestions", List.of("请补充上下游名单"))))));

        SupplyChainGraphReport report = service.execute(
                new SupplyChainGraphExecuteRequest("CUST-001", "SCG-P"));

        assertEquals("partial", report.result().buildStatus());
        assertTrue(report.result().nodes().isEmpty());
        assertTrue(report.result().edges().isEmpty());
        assertEquals("输入不足，仅部分降级", report.result().interpretation().overallAssessment());
    }

    @Test
    void executeWithoutResultDoesNotFabricateGraph() {
        when(skillPort.execute(any(SkillExecutionCommand.class))).thenReturn(new SkillExecutionResult(
                SkillExecutionStatus.OK, "SCG-F", Map.of("fallback", true, "content", "一段散文"),
                List.of(), List.of(), List.of()));

        SupplyChainGraphReport report = service.execute(
                new SupplyChainGraphExecuteRequest("CUST-001", "SCG-F"));

        assertEquals("partial", report.result().buildStatus());
        assertTrue(report.result().nodes().isEmpty());
        assertTrue(report.result().edges().isEmpty());
    }

    @Test
    void getReportExpiredThrowsFriendlyMessage() {
        Instant start = Instant.parse("2026-08-22T02:00:00Z");
        java.util.concurrent.atomic.AtomicReference<Instant> now =
                new java.util.concurrent.atomic.AtomicReference<>(start);
        Clock clock = new Clock() {
            @Override public ZoneOffset getZone() { return ZoneOffset.UTC; }
            @Override public Clock withZone(java.time.ZoneId zone) { return this; }
            @Override public Instant instant() { return now.get(); }
        };
        cache = new SupplyChainGraphReportCache(Duration.ofMinutes(10), clock);
        service = new SupplyChainGraphService(
                skillPort, customerContextService, cache, clock);
        when(skillPort.execute(any(SkillExecutionCommand.class))).thenReturn(okResult(completePayload()));
        service.execute(new SupplyChainGraphExecuteRequest("CUST-001", "SCG-TTL"));
        assertEquals("SCG-TTL", service.getReport("SCG-TTL").requestId());

        now.set(start.plus(Duration.ofMinutes(11)));
        NoSuchElementException ex = assertThrows(NoSuchElementException.class,
                () -> service.getReport("SCG-TTL"));
        assertEquals(SupplyChainGraphService.EXPIRED_MESSAGE, ex.getMessage());
    }

    @Test
    void getMissingReportThrowsExpiredMessage() {
        NoSuchElementException ex = assertThrows(NoSuchElementException.class,
                () -> service.getReport("missing"));
        assertEquals("报告已过期，请重新执行", ex.getMessage());
    }

    @Test
    void executeSkillFailure_returnsSkillErrorStatus() {
        when(skillPort.execute(any(SkillExecutionCommand.class)))
                .thenThrow(new SkillExecutionException("DKWS 不可达"));

        SupplyChainGraphReport report = service.execute(
                new SupplyChainGraphExecuteRequest("CUST-001", "SCG-ERR"));

        assertEquals("skill_error", report.status());
        assertEquals("partial", report.result().buildStatus());
        assertTrue(report.result().nodes().isEmpty());
        assertTrue(report.result().edges().isEmpty());
    }

    @Test
    void executeBlankRequestId_generatesSkgUuid() {
        when(skillPort.execute(any(SkillExecutionCommand.class))).thenReturn(okResult(completePayload()));

        SupplyChainGraphReport report = service.execute(
                new SupplyChainGraphExecuteRequest("CUST-001", "   "));

        assertTrue(report.requestId().startsWith("SCG-"));
    }

    @Test
    void executeMissingBuildStatus_fallsBackToPartial() {
        when(skillPort.execute(any(SkillExecutionCommand.class))).thenReturn(okResult(Map.of(
                "skillId", "bank-front-supply-chain-graph",
                "result", Map.of(
                        "schemaVersion", "1.0",
                        "nodes", List.of(),
                        "edges", List.of(),
                        "interpretation", Map.of("overallAssessment", "无 buildStatus 字段")))));

        SupplyChainGraphReport report = service.execute(
                new SupplyChainGraphExecuteRequest("CUST-001", "SCG-NB"));

        assertEquals("partial", report.result().buildStatus());
    }

    private static SkillExecutionResult okResult(Map<String, Object> data) {
        return new SkillExecutionResult(SkillExecutionStatus.OK, "req", data, List.of(), List.of(), List.of());
    }

    private static Map<String, Object> completePayload() {
        return Map.of(
                "skillId", "bank-front-supply-chain-graph",
                "result", Map.of(
                        "schemaVersion", "1.0",
                        "buildStatus", "complete",
                        "nodes", List.of(
                                node("N-S1", "浙江轴承集团", "supplier", 12_000_000d, 0.35),
                                node("N-S2", "宁波特种钢公司", "supplier", 8_000_000d, 0.24),
                                node("N-S3", "杭州热处理厂", "supplier", 4_000_000d, 0.12),
                                node("N-E", "杭州智造精密齿轮有限公司", "enterprise", 50_000_000d, 1.0),
                                node("N-C1", "新能源汽车主机厂A", "customer", 25_000_000d, 0.50),
                                node("N-C2", "变速箱总成厂B", "customer", 18_000_000d, 0.36),
                                node("N-C3", "出口渠道C", "customer", 7_000_000d, 0.14)),
                        "edges", List.of(
                                edge("N-S1", "N-E", "purchase", 12_000_000d, 0.35, "月结 60 天"),
                                edge("N-S2", "N-E", "purchase", 8_000_000d, 0.24, "货到付款"),
                                edge("N-S3", "N-E", "purchase", 4_000_000d, 0.12, "月结 30 天"),
                                edge("N-E", "N-C1", "sale", 25_000_000d, 0.50, "账期 45 天"),
                                edge("N-E", "N-C2", "sale", 18_000_000d, 0.36, "账期 30 天"),
                                edge("N-E", "N-C3", "sale", 7_000_000d, 0.14, "信用证")),
                        "interpretation", Map.of(
                                "supplyChainPosition", "中游核心制造",
                                "bargainingPower", "对下游较强",
                                "concentrationRisk", List.of("主机厂A 占销售 50%"),
                                "keyChanges", "总成厂B 采购下降",
                                "overallAssessment", "链条清晰，关注集中度",
                                "followUpQuestions", List.of("核实总成厂B下降原因"),
                                "confidence", Map.of("position", "high"))));
    }

    private static Map<String, Object> node(String id, String name, String layer, double amount, double share) {
        return Map.of(
                "id", id, "name", name, "layer", layer, "type", layer,
                "annualAmount", amount, "share", share, "trend", "up",
                "dataSource", "T-CORE-001", "verifyStatus", "VERIFIED");
    }

    private static Map<String, Object> edge(
            String source, String target, String relation, double amount, double share, String settlement) {
        return Map.of(
                "source", source, "target", target, "relation", relation, "direction", "out",
                "annualAmount", amount, "share", share, "settlement", settlement);
    }
}
