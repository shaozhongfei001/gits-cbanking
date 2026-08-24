package com.gien.gits.adapter.skill;

import com.gien.gits.engagement.port.GateAssets;
import com.gien.gits.engagement.port.SkillGatePort;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 本地回退闸门适配器 — 未配置 {@code dsh.base-url} 时使用。
 *
 * <p>拉取资产返回 G0-G5 默认清单（仅 GITS 本地权威状态机输入，无 DKWS 交互）；
 * 镜像决策仅记日志（audit 权威仍在 GITS 本地）。</p>
 */
public class FallbackSkillGateAdapter implements SkillGatePort {

    private static final Logger log = LoggerFactory.getLogger(FallbackSkillGateAdapter.class);

    @Override
    public GateAssets fetchGateAssets(String customerId) {
        log.info("[SKILL-GATE][fallback] 返回默认 G0-G5 清单 customerId={}", customerId);
        return GateAssets.defaultServiceProposalFlow(customerId);
    }

    @Override
    public boolean mirrorGateAudit(String customerId, Map<String, Object> auditEntry) {
        log.info("[SKILL-GATE][fallback] 镜像记录(仅本地日志) customerId={} entry={}", customerId, auditEntry);
        return true;
    }
}
