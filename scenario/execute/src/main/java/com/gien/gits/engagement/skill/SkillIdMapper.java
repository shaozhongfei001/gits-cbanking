package com.gien.gits.engagement.skill;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * 知识条目 SP-ID → deepseek-harness skillId 映射器。
 *
 * <p>Phase2 架构演进：将 ActivationContract.skills(SP-*) 映射到 dsh 真实技能 id。
 * 默认映射以 OutboundScript / MeetingScript / PrevisitReport 三类为核心，
 * 可通过 {@link #override(String, String)} 在运行期覆盖（例如本地调试、A/B 实验）。
 *
 * <p>映射规则遵循 docs/dd/skill-execute-api-contract.md §5：
 * <ul>
 *   <li>SP-OUTREACH-* / Outbound  场景 → skill-customer-outreach-script</li>
 *   <li>SP-MEETING-*  / Meeting   场景 → skill-customer-meeting-script</li>
 *   <li>SP-PREVISIT-* / Previsit  场景 → skill-customer-previsit-report</li>
 *   <li>其他（SP-VISIT-* 等）      → skill-customer-visiting-record（可选）</li>
 * </ul>
 */
public final class SkillIdMapper {

    public static final String DEFAULT_OUTREACH = "skill-customer-outreach-script";
    public static final String DEFAULT_MEETING  = "skill-customer-meeting-script";
    public static final String DEFAULT_PREVISIT = "skill-customer-previsit-report";
    public static final String DEFAULT_VISIT    = "skill-customer-visiting-record";

    private final Map<String, String> overrides;

    public SkillIdMapper() {
        this(Map.of());
    }

    public SkillIdMapper(Map<String, String> overrides) {
        this.overrides = overrides == null ? new HashMap<>() : new HashMap<>(overrides);
    }

    /**
     * 将 ActivationContract.skills 中的 SP-ID 解析为 dsh skillId。
     * 解析优先级：override > 默认规则 > empty（未匹配）。
     *
     * @param spId 来自激活合同的 SP 标识（例 "SP-OUTREACH-001"），可空
     * @return 解析出的 skillId，可空（表示该 SP 无对应 dsh 技能）
     */
    public Optional<String> resolve(String spId) {
        if (spId == null || spId.isBlank()) {
            return Optional.empty();
        }
        // 1. override 优先
        String overridden = overrides.get(spId);
        if (overridden != null && !overridden.isBlank()) {
            return Optional.of(overridden);
        }
        // 2. 默认规则
        String upper = spId.toUpperCase();
        if (upper.contains("OUTREACH") || upper.contains("OUTBOUND")) {
            return Optional.of(DEFAULT_OUTREACH);
        }
        if (upper.contains("MEETING") || upper.contains("AGENDA")) {
            return Optional.of(DEFAULT_MEETING);
        }
        if (upper.contains("PREVISIT") || upper.contains("PRE-VISIT")) {
            return Optional.of(DEFAULT_PREVISIT);
        }
        if (upper.contains("VISIT") || upper.contains("POSTVISIT")) {
            return Optional.of(DEFAULT_VISIT);
        }
        return Optional.empty();
    }

    /**
     * 运行期覆盖单个 SP-ID 的解析。
     *
     * @param spId    源 SP 标识
     * @param skillId 目标 dsh skillId；若为 null 则清除覆盖
     */
    public void override(String spId, String skillId) {
        Objects.requireNonNull(spId, "spId");
        if (skillId == null) {
            overrides.remove(spId);
        } else {
            overrides.put(spId, skillId);
        }
    }

    /** 复制当前覆盖表，便于测试断言。 */
    public Map<String, String> snapshotOverrides() {
        return Map.copyOf(overrides);
    }
}