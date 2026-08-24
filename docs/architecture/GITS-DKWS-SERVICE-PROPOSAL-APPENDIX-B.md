# 附录 B：Port 接口完整 Java 定义

> 关联主文档：`GITS-DKWS-SERVICE-PROPOSAL-INTEGRATION-DESIGN.md` §5

---

## B.1 ProposalPort

```java
package com.gien.gits.engagement.port;

import java.util.List;
import java.util.Map;

/**
 * 服务建议书端口接口。
 * GITS 通过此端口调用 DKWS 的服务建议书生成能力。
 *
 * 合同ID: CTR-PROPOSAL-001
 * 实现类: DkwsProposalAdapter（HTTP 调用 DKWS /skills/execute）
 */
public interface ProposalPort {

    /**
     * 生成服务建议书草稿。
     * 调用 DKWS SP-20 Skill，返回草稿供人工审核。
     *
     * @param command 生成命令
     * @return 建议书草稿
     * @throws ProposalGenerationException 生成失败时抛出
     */
    ProposalDraft generateDraft(ProposalCommand command);

    /**
     * 获取客户已有建议书版本列表。
     *
     * @param customerId 客户ID
     * @return 版本列表，按时间倒序
     */
    List<ProposalVersion> listVersions(String customerId);

    /**
     * 获取指定版本的建议书。
     *
     * @param customerId 客户ID
     * @param versionId  版本ID
     * @return 建议书版本详情
     * @throws ProposalVersionNotFoundException 版本不存在时抛出
     */
    ProposalVersion getVersion(String customerId, String versionId);

    /**
     * 推进闸门。
     * 闸门只能顺序推进（G0→G1→G2→G3→G4→G5），禁止跳门。
     *
     * @param command 闸门推进命令
     * @return 推进后的建议书版本
     * @throws GateSequenceViolationException 跳门时抛出
     * @throws GatePrerequisiteNotMetException 前置条件未满足时抛出
     */
    ProposalVersion advanceGate(GateAdvancementCommand command);

    /**
     * 生成对客版。
     * 仅在 G1+G2+G3 完成后可调用。
     * 对客版由内部版经规则过滤（脱敏/合规）后生成。
     *
     * @param customerId 客户ID
     * @param versionId  内部版版本ID
     * @return 对客版建议书
     * @throws GatePrerequisiteNotMetException G1+G2+G3 未全部通过时抛出
     */
    ProposalVersion generateCustomerVersion(String customerId, String versionId);
}
```

## B.2 ProposalCommand

```java
package com.gien.gits.engagement.port;

import java.util.List;

/**
 * 服务建议书生成命令。
 */
public record ProposalCommand(
    /** 客户ID */
    String customerId,

    /** 旅程ID */
    String journeyId,

    /** 经营案例ID */
    String operatingCaseId,

    /** 客户经营阶段 */
    EngagementPhase phase,

    /** 已有证据ID列表 */
    List<String> evidenceIds,

    /** 交互记忆ID列表（阶段二才有，阶段一为空列表） */
    List<String> interactionMemoryIds,

    /** 建议书类型：INITIAL（首次）或 UPDATE（更新） */
    ProposalType proposalType,

    /** 已有建议书版本ID（更新时必填，首次为 null） */
    String existingVersionId
) {
    public ProposalCommand {
        if (evidenceIds == null) {
            evidenceIds = List.of();
        }
        if (interactionMemoryIds == null) {
            interactionMemoryIds = List.of();
        }
    }
}
```

## B.3 ProposalDraft

```java
package com.gien.gits.engagement.port;

import java.util.List;
import java.util.Map;

/**
 * 服务建议书草稿。
 * DKWS SP-20 返回的结构化结果。
 */
public record ProposalDraft(
    /** 草稿ID */
    String draftId,

    /** 客户ID */
    String customerId,

    /** 版本号（语义化版本，如 1.0.0-draft） */
    String version,

    /** 建议书正文（Markdown 格式） */
    String content,

    /** 内部版正文（含假设、风险红旗、内部判断） */
    String internalContent,

    /** 事实标签映射（断言文本 → 标签） */
    Map<String, FactLabel> factLabels,

    /** 引用索引 */
    List<Citation> citations,

    /** 未知项列表 */
    List<String> unknowns,

    /** 限制说明 */
    List<String> limitations,

    /** 闸门状态 */
    GateStatus gateStatus,

    /** DKWS 运行ID（用于追踪） */
    String dkwsRunId
) {}
```

## B.4 ProposalVersion

```java
package com.gien.gits.engagement.port;

import java.time.Instant;

/**
 * 服务建议书版本。
 */
public record ProposalVersion(
    /** 版本ID */
    String versionId,

    /** 客户ID */
    String customerId,

    /** 语义化版本号 */
    String semanticVersion,

    /** 版本类型：INTERNAL 或 CUSTOMER */
    ProposalVersionType versionType,

    /** 建议书正文（Markdown） */
    String content,

    /** 闸门状态 */
    GateStatus gateStatus,

    /** 创建时间 */
    Instant createdAt,

    /** 创建人 */
    String createdBy,

    /** 关联的内部版版本ID（仅对客版有） */
    String internalVersionId,

    /** 过滤报告（仅对客版有） */
    String filteringReport
) {}

public enum ProposalVersionType {
    INTERNAL,   // 内部版
    CUSTOMER    // 对客版
}
```

## B.5 GateAdvancementCommand

```java
package com.gien.gits.engagement.port;

/**
 * 闸门推进命令。
 */
public record GateAdvancementCommand(
    /** 客户ID */
    String customerId,

    /** 版本ID */
    String versionId,

    /** 闸门名称：G0, G1, G2, G3, G4, G5 */
    String gateName,

    /** 审核人ID */
    String reviewerId,

    /** 审核意见 */
    String reviewNote,

    /** 是否通过 */
    boolean approved
) {}
```

## B.6 枚举和值对象

```java
package com.gien.gits.engagement.port;

/**
 * 事实状态标签。
 * 对应交接文档中的 F/C/B/H/P/A 标签体系。
 */
public enum FactLabel {
    /** Fact - 经核验的确定事实，可写入对客版 */
    F,
    /** Candidate - 有来源但未经客户确认的候选事实，仅内部版 */
    C,
    /** Belief - 客户经理个人判断，仅内部版，需标注判断依据 */
    B,
    /** Hypothesis - 基于行业/产业数据的假设，仅内部版，需标注假设前提 */
    H,
    /** Pending - 待审批事项，仅内部版，需标注审批流程 */
    P,
    /** Approved - 已批准事项，可写入对客版 */
    A
}

/**
 * 客户经营阶段。
 */
public enum EngagementPhase {
    /** 潜客阶段：仅有公开数据，未接触 */
    PROSPECTING,
    /** 首次接触：已准备建议书，预约/拜访中 */
    FIRST_CONTACT,
    /** 深度经营：多次交互，有交互记忆积累 */
    ACTIVE_ENGAGEMENT,
    /** 方案交付：建议书已对客确认 */
    PROPOSAL_DELIVERED,
    /** 实施阶段：30/90/180天计划执行中 */
    IMPLEMENTATION,
    /** 存续经营：持续服务，定期复盘 */
    RETENTION
}

/**
 * 建议书类型。
 */
public enum ProposalType {
    /** 首次生成 */
    INITIAL,
    /** 基于新交互记忆更新 */
    UPDATE
}

/**
 * 闸门状态枚举。
 */
public enum GateState {
    /** 未开始 */
    PENDING,
    /** 待审核 */
    READY_FOR_REVIEW,
    /** 已通过 */
    PASSED,
    /** 被阻塞 */
    BLOCKED
}

/**
 * 闸门状态。
 */
public record GateStatus(
    GateState g0,
    GateState g1,
    GateState g2,
    GateState g3,
    GateState g4,
    GateState g5
) {}

/**
 * 引用。
 */
public record Citation(
    /** 引用ID */
    String id,
    /** 断言内容 */
    String claim,
    /** 来源 */
    String source,
    /** 来源日期 */
    String date,
    /** 事实标签 */
    FactLabel factLabel,
    /** 所在章节引用 */
    String chapterRef
) {}
```

## B.7 InteractionMemoryPort

```java
package com.gien.gits.engagement.port;

import java.util.List;

/**
 * 交互记忆端口接口。
 * 管理从客户交互中抽取的结构化洞察。
 *
 * 合同ID: CTR-INTERACTION-MEMORY-001
 */
public interface InteractionMemoryPort {

    /**
     * 从交互纪要中抽取候选记忆。
     * 调用 DKWS SP-21 Skill，返回候选记忆供人工确认。
     *
     * @param interactionId 交互ID
     * @return 候选记忆列表
     */
    List<CandidateMemory> extractCandidates(String interactionId);

    /**
     * 确认候选记忆。
     * 客户经理审核后确认，状态从 CANDIDATE 变为 CONFIRMED。
     *
     * @param memoryId        候选记忆ID
     * @param confirmed       是否确认
     * @param revisedContent  修正后的内容（确认时可修正，拒绝时可为 null）
     */
    void confirmCandidate(String memoryId, boolean confirmed, String revisedContent);

    /**
     * 获取客户的所有有效交互记忆。
     * 按置信度和时效性排序，用于驱动访前准备和建议书更新。
     *
     * @param customerId 客户ID
     * @return 有效记忆列表（仅 CONFIRMED 状态）
     */
    List<InteractionMemory> getEffectiveMemories(String customerId);

    /**
     * 获取指定类别的交互记忆。
     *
     * @param customerId 客户ID
     * @param category   记忆类别
     * @return 该类别的记忆列表
     */
    List<InteractionMemory> getMemoriesByCategory(String customerId, MemoryCategory category);
}
```

## B.8 交互记忆相关类型

```java
package com.gien.gits.engagement.port;

import java.util.List;

/**
 * 记忆类别。
 */
public enum MemoryCategory {
    /** 客户偏好（沟通方式、决策风格、关注重点） */
    PREFERENCE,
    /** 决策模式（决策链、审批流程、时间窗口） */
    DECISION_PATTERN,
    /** 关系网络（关键影响人、内部政治、利益关系） */
    RELATIONSHIP,
    /** 业务信号（预算周期、采购计划、战略方向） */
    BUSINESS_SIGNAL,
    /** 情感状态（信任程度、满意度、风险预警） */
    EMOTIONAL_STATE
}

/**
 * 置信度衰减规则。
 */
public enum DecayRule {
    /** 不衰减（事实性记忆，如决策人身份） */
    NONE,
    /** 线性衰减（业务信号，如采购计划） */
    LINEAR,
    /** 阶梯衰减（情感状态，在关键事件后骤变） */
    STEP
}

/**
 * 记忆状态。
 */
public enum MemoryStatus {
    /** 候选，待人工确认 */
    CANDIDATE,
    /** 已确认，可驱动决策 */
    CONFIRMED,
    /** 已过期 */
    EXPIRED,
    /** 已被新记忆取代 */
    SUPERSEDED
}

/**
 * 交互记忆。
 */
public record InteractionMemory(
    /** 记忆ID，格式 MEM-NNN */
    String memoryId,
    /** 客户ID */
    String customerId,
    /** 记忆类别 */
    MemoryCategory category,
    /** 结构化描述 */
    String content,
    /** 来源交互ID列表 */
    List<String> sourceInteractionIds,
    /** 置信度 0-1 */
    double confidence,
    /** 生效日期 */
    String validFrom,
    /** 失效日期（可选） */
    String validUntil,
    /** 衰减规则 */
    DecayRule decayRule,
    /** 记忆状态 */
    MemoryStatus status
) {}

/**
 * 候选记忆。
 */
public record CandidateMemory(
    /** 候选ID */
    String candidateId,
    /** 来源交互ID */
    String interactionId,
    /** 记忆类别 */
    MemoryCategory category,
    /** 结构化描述 */
    String content,
    /** 置信度 0-1 */
    double confidence,
    /** LLM 抽取理由 */
    String rationale
) {}
```

## B.9 异常类

```java
package com.gien.gits.engagement.port;

/**
 * 建议书生成异常。
 */
public class ProposalGenerationException extends RuntimeException {
    private final String customerId;
    private final String dkwsRunId;

    public ProposalGenerationException(String customerId, String dkwsRunId, String message, Throwable cause) {
        super(message, cause);
        this.customerId = customerId;
        this.dkwsRunId = dkwsRunId;
    }

    public String getCustomerId() { return customerId; }
    public String getDkwsRunId() { return dkwsRunId; }
}

/**
 * 闸门顺序违规异常。
 * 当尝试跳门推进时抛出。
 */
public class GateSequenceViolationException extends RuntimeException {
    private final String attemptedGate;
    private final String currentGate;

    public GateSequenceViolationException(String attemptedGate, String currentGate) {
        super("Cannot advance to " + attemptedGate + ": current gate is " + currentGate + ", sequential advancement required");
        this.attemptedGate = attemptedGate;
        this.currentGate = currentGate;
    }

    public String getAttemptedGate() { return attemptedGate; }
    public String getCurrentGate() { return currentGate; }
}

/**
 * 闸门前置条件未满足异常。
 */
public class GatePrerequisiteNotMetException extends RuntimeException {
    private final String gateName;
    private final String prerequisite;

    public GatePrerequisiteNotMetException(String gateName, String prerequisite) {
        super("Prerequisite not met for " + gateName + ": " + prerequisite);
        this.gateName = gateName;
        this.prerequisite = prerequisite;
    }

    public String getGateName() { return gateName; }
    public String getPrerequisite() { return prerequisite; }
}

/**
 * 建议书版本不存在异常。
 */
public class ProposalVersionNotFoundException extends RuntimeException {
    private final String customerId;
    private final String versionId;

    public ProposalVersionNotFoundException(String customerId, String versionId) {
        super("Proposal version not found: customer=" + customerId + ", version=" + versionId);
        this.customerId = customerId;
        this.versionId = versionId;
    }

    public String getCustomerId() { return customerId; }
    public String getVersionId() { return versionId; }
}
```
