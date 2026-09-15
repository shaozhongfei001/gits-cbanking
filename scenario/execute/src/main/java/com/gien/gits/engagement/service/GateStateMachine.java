package com.gien.gits.engagement.service;

import com.gien.gits.engagement.port.GateAssets;
import com.gien.gits.engagement.port.ServiceProposal;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * G0-G5 闸门权威状态机（GITS 侧，契约 v1.4 §4.2）。
 *
 * <p>职责：闸门推进/决策权威在 GITS；SP-20 的 {@code gateRecommendations} 仅作输入建议；
 * 当前闸门 + passed 集合 + checklist 状态全由本状态机维护，镜像回 DKWS 供审计。</p>
 *
 * <p>放行条件：G1/G2/G3 全部 passed → 对客版可放行（对应 {@code releaseBlockedUntil} 清空）。</p>
 */
public class GateStateMachine {

    /** 对客版放行所需闸门（G1 事实基础、G2 规则合规、G3 对客版就绪）。 */
    public static final List<String> RELEASE_GATES = List.of("G1", "G2", "G3");

    private final String customerId;
    private final List<String> gateOrder;
    private final Map<String, String> stateByGate;   // gateId -> PASSED | BLOCKED | PENDING
    private final Map<String, List<String>> evidenceByGate;
    private final Set<String> passedGates;

    public GateStateMachine(String customerId, GateAssets assets) {
        this.customerId = customerId;
        this.gateOrder = assets != null && !assets.gates().isEmpty()
            ? assets.gates().stream().map(GateAssets.GateDefinition::gateId).toList()
            : List.of("G0", "G1", "G2", "G3", "G4", "G5");
        this.stateByGate = new LinkedHashMap<>();
        this.evidenceByGate = new LinkedHashMap<>();
        this.passedGates = new LinkedHashSet<>();
        for (String g : gateOrder) {
            stateByGate.put(g, "PENDING");
            evidenceByGate.put(g, List.of());
        }
    }

    public String customerId() {
        return customerId;
    }

    /** 当前闸门：第一个非 PASSED 的闸门。 */
    public String currentGate() {
        return gateOrder.stream()
            .filter(g -> !"PASSED".equals(stateByGate.get(g)))
            .findFirst()
            .orElse("G5");
    }

    public List<String> passedGates() {
        return List.copyOf(passedGates);
    }

    /** 推进闸门（人工审批通过）。 */
    public GateStateMachine pass(String gateId, String actorId, String evidence) {
        if (!stateByGate.containsKey(gateId)) {
            throw new IllegalArgumentException("未知闸门: " + gateId);
        }
        stateByGate.put(gateId, "PASSED");
        passedGates.add(gateId);
        evidenceByGate.put(gateId, List.of(actorId, evidence));
        return this;
    }

    /** 阻滞闸门（人工驳回/阻塞）。 */
    public GateStateMachine block(String gateId, String actorId, String reason) {
        if (!stateByGate.containsKey(gateId)) {
            throw new IllegalArgumentException("未知闸门: " + gateId);
        }
        stateByGate.put(gateId, "BLOCKED");
        evidenceByGate.put(gateId, List.of(actorId, reason));
        return this;
    }

    /** 吸收 SP-20 gateRecommendations 输入（仅当闸门尚未被人工推进时生效）。 */
    public GateStateMachine absorb(ServiceProposal.GateRecommendations recommendations) {
        if (recommendations == null) {
            return this;
        }
        for (ServiceProposal.GateCheck check : recommendations.checklist()) {
            String gate = check.gate();
            if (stateByGate.containsKey(gate) && !"PASSED".equals(stateByGate.get(gate))) {
                String st = check.state() == null ? "PENDING" : check.state();
                if ("PASSED".equals(st) || "READY_FOR_REVIEW".equals(st)) {
                    stateByGate.put(gate, st);
                } else if ("BLOCKED".equals(st)) {
                    stateByGate.put(gate, "BLOCKED");
                }
            }
        }
        return this;
    }

    /** 对客版是否已满足放行条件（G1/G2/G3 全 passed）。 */
    public boolean isReleaseReady() {
        return RELEASE_GATES.stream().allMatch(g -> "PASSED".equals(stateByGate.get(g)));
    }

    /** 闸门权威视图（供前端/镜像）。 */
    public Map<String, Object> snapshot() {
        Map<String, Object> view = new LinkedHashMap<>();
        view.put("customerId", customerId);
        view.put("currentGate", currentGate());
        view.put("passedGates", passedGates());
        view.put("releaseReady", isReleaseReady());
        List<Map<String, Object>> checklist = new ArrayList<>();
        for (String g : gateOrder) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("gate", g);
            item.put("state", stateByGate.get(g));
            item.put("evidence", evidenceByGate.get(g));
            checklist.add(item);
        }
        view.put("checklist", checklist);
        return view;
    }
}
