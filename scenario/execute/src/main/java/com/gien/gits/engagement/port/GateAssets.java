package com.gien.gits.engagement.port;

import java.util.List;
import java.util.Map;

/**
 * GATE-BIZ 清单资产（契约 v1.4 §4.1）— DKWS {@code GET /api/skill/gates/{customerId}} 的强类型投影。
 *
 * <p>仅作 GITS 权威状态机的输入清单；闸门状态（currentGate/passedGates/checklist 各 item state）
 * 由 GITS 权威维护，镜像回 DKWS audit。</p>
 *
 * @param schemaVersion 1.0.0
 * @param customerId    客户 ID
 * @param flowName      流程名（如 service-proposal）
 * @param gates         闸门定义清单（G0..G5 顺序）
 */
public record GateAssets(
        String schemaVersion,
        String customerId,
        String flowName,
        List<GateDefinition> gates) {

    public static final GateAssets EMPTY = new GateAssets("1.0.0", "", "", List.of());

    public GateAssets {
        gates = List.copyOf(gates != null ? gates : List.of());
    }

    /**
     * 闸门定义。
     *
     * @param gateId     G0 / G1 / G2 / G3 / G4 / G5
     * @param name       闸门名称
     * @param description 说明
     * @param criteria   通过条件（布尔式语义）
     */
    public record GateDefinition(
            String gateId,
            String name,
            String description,
            List<String> criteria) {

        public static final GateDefinition EMPTY = new GateDefinition("", "", "", List.of());

        public GateDefinition {
            gateId = gateId == null ? "" : gateId;
            name = name == null ? "" : name;
            description = description == null ? "" : description;
            criteria = List.copyOf(criteria != null ? criteria : List.of());
        }
    }

    /** 供测试：G0-G5 默认清单。 */
    public static GateAssets defaultServiceProposalFlow(String customerId) {
        return new GateAssets("1.0.0", customerId, "service-proposal",
            List.of(
                new GateDefinition("G0", "准备就绪", "ContextPackage 与客户主档就绪", List.of("customerMasterLoaded", "contextPackageComplete")),
                new GateDefinition("G1", "事实基础", "F/A 事实与引用齐备", List.of("factCoverage", "citationCoverage")),
                new GateDefinition("G2", "规则合规", "SP-20 规则零 BLOCKING 违规", List.of("noBlockingViolations")),
                new GateDefinition("G3", "对客版就绪", "内部版已审、对客版过滤完成", List.of("internalApproved", "customerVersionFiltered")),
                new GateDefinition("G4", "版本冻结", "对客版已放行、双版本已归档", List.of("customerReleased")),
                new GateDefinition("G5", "闭环", "联调/审计记录完备", List.of("auditTrailComplete"))));
    }
}
