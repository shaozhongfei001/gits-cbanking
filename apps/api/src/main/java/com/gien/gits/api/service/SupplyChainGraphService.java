package com.gien.gits.api.service;

import com.gien.gits.api.dto.SupplyChainGraphEdge;
import com.gien.gits.api.dto.SupplyChainGraphExecuteRequest;
import com.gien.gits.api.dto.SupplyChainGraphInterpretation;
import com.gien.gits.api.dto.SupplyChainGraphNode;
import com.gien.gits.api.dto.SupplyChainGraphReport;
import com.gien.gits.api.dto.SupplyChainGraphResult;
import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.ontology.Customer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Clock;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.UUID;

/**
 * 调用 DKWS {@code bank-front-supply-chain-graph}，缓存结果 10 分钟，供 GITS 自研报告页读取。
 * 不解析 DKWS HTML；无 result 时不虚构节点。
 */
public class SupplyChainGraphService {

    public static final String SKILL_ID = "bank-front-supply-chain-graph";
    public static final String EXPIRED_MESSAGE = "报告已过期，请重新执行";

    private static final Logger log = LoggerFactory.getLogger(SupplyChainGraphService.class);

    private final SkillExecutionPort skillExecutionPort;
    private final CustomerContextService customerContextService;
    private final SupplyChainGraphReportCache cache;
    private final Clock clock;

    public SupplyChainGraphService(
            SkillExecutionPort skillExecutionPort,
            CustomerContextService customerContextService,
            SupplyChainGraphReportCache cache,
            Clock clock) {
        this.skillExecutionPort = Objects.requireNonNull(skillExecutionPort);
        this.customerContextService = Objects.requireNonNull(customerContextService);
        this.cache = Objects.requireNonNull(cache);
        this.clock = clock == null ? Clock.systemUTC() : clock;
    }

    public SupplyChainGraphReport execute(SupplyChainGraphExecuteRequest request) {
        if (request == null || request.customerId() == null || request.customerId().isBlank()) {
            throw new IllegalArgumentException("customerId is required");
        }
        Customer customer = customerContextService.findCustomer(request.customerId())
                .orElseThrow(() -> new IllegalArgumentException("Customer not found: " + request.customerId()));

        String requestId = (request.requestId() == null || request.requestId().isBlank())
                ? "SCG-" + UUID.randomUUID()
                : request.requestId();

        Map<String, Object> skillRequest = buildSkillRequest(customer);
        SkillExecutionResult exec;
        try {
            exec = skillExecutionPort.execute(new SkillExecutionCommand(
                    SKILL_ID, requestId, customer.customerId(), skillRequest));
        } catch (SkillExecutionException e) {
            log.warn("[SCG] DKWS 不可达，不虚构图谱: {}", e.getMessage());
            exec = null;
        }

        SupplyChainGraphResult result = parseResult(exec);
        String status = "skill_error";
        if (exec != null && exec.status() != null) {
            status = switch (exec.status()) {
                case OK -> "ok";
                case SKILL_ERROR -> "skill_error";
                case EXIT_POLICY_NO_NEW_EVIDENCE -> "exit_policy_no_new_evidence";
            };
        }

        SupplyChainGraphReport report = new SupplyChainGraphReport(
                requestId,
                customer.customerId(),
                customer.customerName(),
                Instant.now(clock).toString(),
                status,
                "/supply-chain-report/" + requestId,
                result);
        cache.put(report);
        return report;
    }

    public SupplyChainGraphReport getReport(String requestId) {
        return cache.get(requestId)
                .orElseThrow(() -> new NoSuchElementException(EXPIRED_MESSAGE));
    }

    private Map<String, Object> buildSkillRequest(Customer customer) {
        Map<String, Object> req = new LinkedHashMap<>();
        req.put("customerId", customer.customerId());
        return req;
    }

    @SuppressWarnings("unchecked")
    private SupplyChainGraphResult parseResult(SkillExecutionResult exec) {
        if (exec == null || exec.data() == null || exec.data().isEmpty()) {
            return emptyPartial();
        }
        Object raw = exec.data().get("result");
        if (!(raw instanceof Map<?, ?> rawMap) || rawMap.isEmpty()) {
            return emptyPartial();
        }
        Map<String, Object> map = (Map<String, Object>) rawMap;
        String schemaVersion = asString(map.get("schemaVersion"));
        String buildStatus = asString(map.get("buildStatus"));
        if (buildStatus == null || buildStatus.isBlank()) {
            buildStatus = "partial";
        }
        List<SupplyChainGraphNode> nodes = parseNodes(map.get("nodes"));
        List<SupplyChainGraphEdge> edges = parseEdges(map.get("edges"));
        SupplyChainGraphInterpretation interpretation = parseInterpretation(map.get("interpretation"));
        return new SupplyChainGraphResult(schemaVersion, buildStatus, nodes, edges, interpretation);
    }

    private static SupplyChainGraphResult emptyPartial() {
        return new SupplyChainGraphResult(
                "1.0",
                "partial",
                List.of(),
                List.of(),
                new SupplyChainGraphInterpretation(null, null, List.of(), null, null, List.of(), null));
    }

    @SuppressWarnings("unchecked")
    private List<SupplyChainGraphNode> parseNodes(Object raw) {
        if (!(raw instanceof List<?> list)) {
            return List.of();
        }
        List<SupplyChainGraphNode> out = new ArrayList<>();
        for (Object item : list) {
            if (!(item instanceof Map<?, ?> m)) {
                continue;
            }
            Map<String, Object> n = (Map<String, Object>) m;
            out.add(new SupplyChainGraphNode(
                    asString(n.get("id")),
                    asString(n.get("name")),
                    asString(n.get("layer")),
                    asString(n.get("type")),
                    asString(n.get("industry")),
                    asDouble(n.get("annualAmount")),
                    asDouble(n.get("share")),
                    asString(n.get("trend")),
                    asString(n.get("dataSource")),
                    asString(n.get("verifyStatus"))));
        }
        return out;
    }

    @SuppressWarnings("unchecked")
    private List<SupplyChainGraphEdge> parseEdges(Object raw) {
        if (!(raw instanceof List<?> list)) {
            return List.of();
        }
        List<SupplyChainGraphEdge> out = new ArrayList<>();
        for (Object item : list) {
            if (!(item instanceof Map<?, ?> m)) {
                continue;
            }
            Map<String, Object> e = (Map<String, Object>) m;
            out.add(new SupplyChainGraphEdge(
                    asString(e.get("source")),
                    asString(e.get("target")),
                    asString(e.get("relation")),
                    asString(e.get("direction")),
                    asDouble(e.get("annualAmount")),
                    asDouble(e.get("share")),
                    asString(e.get("settlement"))));
        }
        return out;
    }

    @SuppressWarnings("unchecked")
    private SupplyChainGraphInterpretation parseInterpretation(Object raw) {
        if (!(raw instanceof Map<?, ?> m)) {
            return new SupplyChainGraphInterpretation(null, null, List.of(), null, null, List.of(), null);
        }
        Map<String, Object> i = (Map<String, Object>) m;
        return new SupplyChainGraphInterpretation(
                asString(i.get("supplyChainPosition")),
                asString(i.get("bargainingPower")),
                asStringList(i.get("concentrationRisk")),
                asString(i.get("keyChanges")),
                asString(i.get("overallAssessment")),
                asStringList(i.get("followUpQuestions")),
                i.get("confidence"));
    }

    private static String asString(Object v) {
        return v == null ? null : String.valueOf(v);
    }

    private static Double asDouble(Object v) {
        if (v instanceof Number n) {
            return n.doubleValue();
        }
        if (v instanceof String s && !s.isBlank()) {
            try {
                return Double.parseDouble(s);
            } catch (NumberFormatException ignored) {
                return null;
            }
        }
        return null;
    }

    private static List<String> asStringList(Object v) {
        if (!(v instanceof List<?> list)) {
            return List.of();
        }
        List<String> out = new ArrayList<>();
        for (Object item : list) {
            if (item != null) {
                out.add(String.valueOf(item));
            }
        }
        return out;
    }
}
