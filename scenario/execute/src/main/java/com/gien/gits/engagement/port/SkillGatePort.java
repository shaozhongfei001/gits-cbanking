package com.gien.gits.engagement.port;

import java.util.Map;

/**
 * SP-20 闸门协作端口（契约 v1.4 §4）。
 *
 * <p>职责边界：GATE-BIZ 清单资产由 DKWS 提供；闸门权威状态（推进/决策）在 GITS；
 * 决策通过 audit 镜像回 DKWS（追加 {@code 90_control/audit/gates.jsonl}），镜像失败不影响权威状态。</p>
 */
public interface SkillGatePort {

    /**
     * 拉取 GATE-BIZ 清单资产。
     *
     * @param customerId 客户 ID
     * @return 闸门定义清单（G0..G5）
     * @throws SkillExecutionException 拉取失败（网络/非 2xx）
     */
    GateAssets fetchGateAssets(String customerId);

    /**
     * 镜像闸门决策到 DKWS audit（GITS 权威 → DKWS 追加记录）。
     *
     * @param customerId 客户 ID
     * @param auditEntry 决策记录（gateId/decision/actorId/reason/timestamp 等）
     * @return 镜像是否成功；失败不影响 GITS 权威状态
     */
    boolean mirrorGateAudit(String customerId, Map<String, Object> auditEntry);
}
