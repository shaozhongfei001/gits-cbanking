package com.gien.gits.engagement.skill;

import com.gien.gits.engagement.port.SkillExecutionCommand;
import com.gien.gits.engagement.port.SkillExecutionException;
import com.gien.gits.engagement.port.SkillExecutionPort;
import com.gien.gits.engagement.port.SkillExecutionResult;
import com.gien.gits.engagement.port.SkillExecutionStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * 客户经理持续经营 Skill 调度器。
 *
 * <p>消费激活合同中的 SP-* 列表（由调用方传入 {@code contract.skills()}），
 * 经 {@link SkillIdMapper} 映射到 dsh skillId，由 {@link SkillExecutionPort}
 * 串行执行，返回统一 {@link RouteResult}。
 *
 * <p>scenario/execute 不依赖 knowledge-architecture 的 {@code ActivationContract}
 * 类型，避免本模块为编排 WIP 引入额外合同层依赖。
 */
public final class SkillExecutionRouter {

    private static final Logger log = LoggerFactory.getLogger(SkillExecutionRouter.class);

    private final SkillExecutionPort port;
    private final SkillIdMapper mapper;

    public SkillExecutionRouter(SkillExecutionPort port, SkillIdMapper mapper) {
        this.port = Objects.requireNonNull(port, "port");
        this.mapper = Objects.requireNonNull(mapper, "mapper");
    }

    /**
     * 按 SP 列表调度执行。空列表返回空 {@link RouteResult}（status=OK）。
     *
     * @param spIds     激活合同 skills（SP-*），可空
     * @param request   透传给 dsh 的业务请求上下文
     * @param requestId 幂等键；null/blank 自动生成 UUID
     */
    public RouteResult route(List<String> spIds, Map<String, Object> request, String requestId) {
        Objects.requireNonNull(request, "request");
        String rid = requestId == null || requestId.isBlank()
            ? "ROUTE-" + UUID.randomUUID() : requestId;
        List<String> ids = spIds == null ? List.of() : List.copyOf(spIds);
        if (ids.isEmpty()) {
            log.debug("route: empty skills, no-op (requestId={})", rid);
            return RouteResult.empty(rid);
        }

        RouteAccumulator acc = new RouteAccumulator();
        for (String spId : ids) {
            dispatchOne(spId, request, rid, acc);
        }
        return new RouteResult(rid, acc.aggregate(), acc.trace, acc.modelCalls,
            acc.perSkill, acc.errors);
    }

    private void dispatchOne(String spId, Map<String, Object> request, String rid,
                             RouteAccumulator acc) {
        Optional<String> skillIdOpt = mapper.resolve(spId);
        if (skillIdOpt.isEmpty()) {
            log.warn("route: SP[{}] 未映射到 dsh skillId，跳过", spId);
            acc.trace.add(new TraceEntry(spId, "RESOLVE", "SKIPPED",
                "SP 未映射到任何 dsh skillId"));
            acc.errors.add(new ErrorEntry(spId, "unmapped_sp",
                "SP[" + spId + "] 未映射到 dsh skillId"));
            return;
        }
        String skillId = skillIdOpt.get();
        Map<String, Object> spRequest = new LinkedHashMap<>(request);
        spRequest.put("spId", spId);
        spRequest.put("skillId", skillId);
        acc.trace.add(new TraceEntry(spId, "RESOLVE", "OK", "mapped → " + skillId));
        executeOne(spId, skillId, rid, customerIdFrom(request), spRequest, acc);
    }

    private void executeOne(String spId, String skillId, String rid, String customerId,
                            Map<String, Object> spRequest, RouteAccumulator acc) {
        SkillExecutionCommand cmd = new SkillExecutionCommand(
            skillId, rid + ":" + spId, customerId, spRequest);
        try {
            SkillExecutionResult result = port.execute(cmd);
            acc.perSkill.put(spId, result);
            recordResult(spId, result, acc);
        } catch (SkillExecutionException ex) {
            acc.anyFailed = true;
            String status = ex.status() == null ? "skill_error" : ex.status().name().toLowerCase();
            String msg = ex.getMessage() == null ? "" : ex.getMessage();
            acc.errors.add(new ErrorEntry(spId, status, msg));
            acc.trace.add(new TraceEntry(spId, "EXECUTE", status, msg));
            log.warn("route: SP[{}] execute failed: {}", spId, ex.getMessage());
        } catch (RuntimeException ex) {
            acc.anyFailed = true;
            String msg = ex.getMessage() == null ? "" : ex.getMessage();
            acc.errors.add(new ErrorEntry(spId, "RUNTIME_ERROR", msg));
            acc.trace.add(new TraceEntry(spId, "EXECUTE", "RUNTIME_ERROR", msg));
            log.error("route: SP[{}] runtime error", spId, ex);
        }
    }

    private static void recordResult(String spId, SkillExecutionResult result,
                                     RouteAccumulator acc) {
        if (result.status() != SkillExecutionStatus.OK) {
            acc.anyFailed = true;
            if (result.status() == SkillExecutionStatus.EXIT_POLICY_NO_NEW_EVIDENCE) {
                acc.anyExitPolicy = true;
            }
            String msg = result.errors().isEmpty()
                ? result.status().name().toLowerCase()
                : result.errors().get(0).message();
            acc.errors.add(new ErrorEntry(spId, result.status().name().toLowerCase(), msg));
            acc.trace.add(new TraceEntry(spId, "EXECUTE", result.status().name().toLowerCase(), msg));
        } else {
            acc.trace.add(new TraceEntry(spId, "EXECUTE", "OK",
                "data keys=" + result.data().keySet()));
        }
        acc.modelCalls.addAll(result.modelCalls());
    }

    private static String customerIdFrom(Map<String, Object> request) {
        Object raw = request.get("customerId");
        if (raw instanceof String s && !s.isBlank()) {
            return s;
        }
        return "UNSET";
    }

    private static final class RouteAccumulator {
        private final List<TraceEntry> trace = new ArrayList<>();
        private final List<SkillExecutionResult.ModelCall> modelCalls = new ArrayList<>();
        private final List<ErrorEntry> errors = new ArrayList<>();
        private final Map<String, SkillExecutionResult> perSkill = new LinkedHashMap<>();
        private boolean anyFailed;
        private boolean anyExitPolicy;

        private SkillExecutionStatus aggregate() {
            if (anyExitPolicy) {
                return SkillExecutionStatus.EXIT_POLICY_NO_NEW_EVIDENCE;
            }
            return anyFailed ? SkillExecutionStatus.SKILL_ERROR : SkillExecutionStatus.OK;
        }
    }

    public record TraceEntry(String spId, String phase, String status, String message) {}

    public record ErrorEntry(String spId, String code, String message) {}

    public record RouteResult(String requestId,
                              SkillExecutionStatus status,
                              List<TraceEntry> trace,
                              List<SkillExecutionResult.ModelCall> modelCalls,
                              Map<String, SkillExecutionResult> perSkill,
                              List<ErrorEntry> errors) {

        public boolean ok() { return status == SkillExecutionStatus.OK; }

        public boolean exitPolicy() {
            return status == SkillExecutionStatus.EXIT_POLICY_NO_NEW_EVIDENCE;
        }

        public static RouteResult empty(String requestId) {
            return new RouteResult(requestId, SkillExecutionStatus.OK,
                Collections.emptyList(), Collections.emptyList(),
                Collections.emptyMap(), Collections.emptyList());
        }
    }
}
