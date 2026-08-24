# 客户经理持续经营 Skill — 当前项目端需求详细设计

- 版本：V1.0
- 日期：2026-08-21
- 关联：dsh 端文档（`docs/dd/客户经理持续经营Skill-v2-deepseek-harness端需求详细设计.md`）
- 基线决策（Owner 确认）：
  1. 桥接方式 = **A**：当前项目用 **Spring RestClient** 调 dsh `POST /api/skill/execute`
  2. 运行平台 = **A**：**dsh 即运行平台**（SkillRegistry + Typert 承担服务激活 + 服务发布）；当前项目仅作**调用方**
  3. Skill 拆分 = **A**：外联脚本 / 会面脚本 / R1 拜访报告 = **三个独立 Skill**，各自可单独激活

---

## 1. 现状与本设计目标

### 1.1 现状（当前项目 gits）
- 外联脚本、会面脚本、R1 拜访报告目前**各自**在 gits 内用 `LlmClient.complete(systemPrompt, userPrompt)` **各发起一次 LLM 请求**（fail-closed，规则兜底）。
- `skills:["SP-02","SP-15"]` 仅存在于元数据（`KnowledgeMap.skillRefs`/`ActivationContract.skills`/`ActivationPlan.skills`），**无真实 Skill 执行器**，未接线进业务流。
- R2 快速作战卡为纯规则，非本设计范围（保持现状或演进到 skill 可另议）。

### 1.2 目标
把三份产物的生成能力**迁移到 dsh 平台**，当前项目改为**通过 HTTP 服务接口调用 dsh 激活对应 Skill**、接收结构化结果并回落（fail-closed）。当前项目中 `LlmClient` 对这三类产物的快速调用逐步退居为**fallback**；其余（R2、KYC gap、规则推理）短工期保留本地。

---

## 2. 架构变化（当前项目端）

```
                   当前项目 (gits)
┌───────────────────────────────────────────────┐
│  EngagementWorkflow                            │
│   ├ OutreachScriptService ──► SkillExecutionClient ─┐
│   ├ MeetingScriptService  ──► SkillExecutionClient  │──HTTP──► dsh POST /api/skill/execute
│   └ KnowledgeDrivenPrevisitReportGenerator ──► ...  │         (外联/会面/R1 三个skill)
│                                                  │
│  SkillExecutionClient (新 Port)                  │
│    ├ DshHttpSkillExecutionAdapter (新 Adapter)    │
│    └ DshFallbackLlmSkillExecutionAdapter (兜底)   │
└───────────────────────────────────────────────┘
```

- **调用方**：当前项目新增 `SkillExecutionPort`（Port），实现分两类：`DshHttpSkillExecutionAdapter`（走 HTTP）与 Fallback（退回归有 `LlmClient`）。
- **激活**：按 `skillRef` 调 `POST /api/skill/execute`（skillId 由映射：SP-02/SP-15 → `skill-customer-*`）。
- **发布**：由 dsh 完成（SkillRegistry + Typert）；当前项目只消费发布出的服务与契约。

---

## 3. 当前项目（gits）详细需求

### 3.1 新 Port：SkillExecutionPort
```java
public interface SkillExecutionPort {
    SkillExecutionResult execute(SkillExecutionCommand cmd);
}
record SkillExecutionCommand(String skillId, String requestId,
        Map<String,Object> request, List<String> assemblyTrailId);
record SkillExecutionResult(String status, Map<String,Object> data,
        List<AssemblyTraceStep> trace, List<ModelCallMeta> modelCalls);
```

### 3.2 Adapter1：DshHttpSkillExecutionAdapter
- 基于 `RestClient`（Spring）调用 dsh `POST /api/skill/execute`。
- 配置：`dsh.base-url`、`dsh.api-key`（**来自环境变量，不硬编码**）、超时/重试（N 次 / 熔断）。
- 错误处理：网络错误 → 回落 Fallback；业务错误（`skill_error`/`exit_policy_no_new_evidence`）→ 如实记录并回落。
- 请求封装：`requestId` 幂等；`knowledgeContext`/`structuredFacts`/`supplyChainMarkdown` 按 skill 所需。

### 3.3 Adapter2：FallbackSkillExecutionAdapter
- dsh 不可达 / 超时 / 无新证据策略时，退回归有 `LlmClient`（保系统可用）。
- 与现状行为一致（fail-closed，规则兜底）。

### 3.4 三个 Skill 接入点（替代原 LlmClient 调用）
| 当前 Service | 原调用 | 改为 |
|---|---|---|
| `OutreachScriptService` | `llmClient.complete(sys,user)` | `skillExecutionPort.execute(skill-customer-outreach-script)` |
| `MeetingScriptService` | `llmClient.complete(sys,user)` | `skillExecutionPort.execute(skill-customer-meeting-script)` |
| `KnowledgeDrivenPrevisitReportGenerator` | `llmClient.complete(...)` | `skillExecutionPort.execute(skill-customer-previsit-report)` |

每个接入点保持：**结构化事实由规则装配 → skill 增强 → 结果合并 → fail-closed**。`service.skillRef` 由激活合同/`KnowledgeMap.skillRefs` 驱动，实现"通过服务接口调用 SKILL 运行平台服务激活"。

### 3.5 激活合同接线（打通元数据 → 执行）
- 使 `ActivationContract.skills`（SP-02/SP-15）**真正被消费**：`SkillExecutionRouter` 读激活合同的 `skills` → 映射到 dsh skillId → 触发执行。
- 之前休眠的 `ActivationPlannerPort` 决策：归档/彻底移除，或改为把 `ActivationPlan.skills` 交给执行器（避免误导性未接线设计）。

### 3.6 结果消费与落库
- 把 skill 返回的 `data` 反序列化为现有 DTO（`OutreachScript`/`MeetingScript`/`PrevisitReportContent`）——**不发明新响应契字段**。
- `assemblyTrace` → 存入 `PrevisitExecutionResponse.supplyChainMarkdown` 之外的既有轨迹字段或本地表（`assembly_trace`），供前端实时控制台读取。
- `modelCalls` → 记入审计/日志（脱敏）。

---

## 4. DTO / 契约影响（当前项目端）

| 影响面 | 处理 |
|---|---|
| `OutreachScript` / `MeetingScript` / `PrevisitReportContent` | 无结构变化（skill 返回映射到既有字段） |
| 新增 `SkillExecutionCommand` / `SkillExecutionResult` | 新 Port 类型，非合同，无需改 OpenAPI |
| `PrevisitExecutionResponse` | 保留 `supplyChainMarkdown`；如需轨迹复用现有某字段或本地表，不加合同字段 |
| 是否需要改 OpenAPI | ✅ 否（新增 Port/Adapter 是后端内部，不入 contract） |

---

## 5. 验收标准（当前项目端）

| # | 验收点 |
|---|---|
| G1 | 新增 `SkillExecutionPort` + 双 Adapter，Spring 装配正确 |
| G2 | dsh 可达时，外联/会面/R1 三产物由 dsh `POST /api/skill/execute` 产生（真实 HTTP 链路，调试日志证明请求打向 dsh） |
| G3 | dsh 不可达时自动回落 Fallback `LlmClient`，三产物仍生成（fail-closed） |
| G4 | 激活合同 `skills(SP-02/SP-15)` 被路由消费并映射到 dsh skillId |
| G5 | `requestId` 幂等；模型故障时 `skill_error` 记录且回落 |
| G6 | `assemblyTrace`/`modelCalls` 记录进库存档，前端实时控制台可显示启动轨迹 |
| G7 | `make check` PASS；新增代码有单测（`DshHttpSkillExecutionAdapterTest` / `SkillExecutionRouterTest`） |
| G8 | 无敏感数据泄露（key 不硬编码、日志脱敏） |

---

## 6. 里程碑

| M | 内容 |
|---|---|
| M1 | `SkillExecutionPort` + `DshHttpSkillExecutionAdapter` + Fallback Adapter + 配置装配 |
| M2 | 三接入点改造（Outreach/Meeting/PrevisitReport 改走 Port） |
| M3 | 激活合同 skills 接线 + `SkillExecutionRouter` |
| M4 | `assemblyTrace`/`modelCalls` 落库 + 前端控制台读取 |
| M5 | 单测 + `make check` + 与 dsh 端到端联调 |

---

## 7. 跨端联调契约（两文档共用）

### 7.1 `/api/skill/execute` 请求/响应（已在 dsh 端 4.2 定义）
- 请求：`{ skillId, requestId, request: { customerId, knowledgeContext, structuredFacts, supplyChainMarkdown? } }`
- 响应：`{ requestId, status(ok|skill_error|exit_policy_no_new_evidence), data, assemblyTrace[], modelCalls[] }`

### 7.2 Skill ID 映射表
| gits 侧 | dsh skillId |
|---|---|
| 外联脚本 | `skill-customer-outreach-script` |
| 会面脚本 | `skill-customer-meeting-script` |
| R1 拜访报告 | `skill-customer-previsit-report` |

### 7.3 环境
- `dsh.base-url`（环境变量 `DSH_BASE_URL`）、`dsh.api-key`（`DSH_API_KEY`，**不落盘**）。
- gits 与 dsh 同机/跨机均可，走 HTTP。

---

## 8. 已知风险与缓解

| 风险 | 缓解 |
|---|---|
| dsh 不可达导致三产物失败 | Fallback Adapter 回落 `LlmClient`，fail-closed |
| skill 无新证据策略误伤正常请求 | 仅对**非告警**产物启用；外联/会面多为即时，previsit 需显式传 evidence 时间戳 |
| Token/延迟上升 | `assemblyTrace`+`modelCalls` 度量；必要时合并请求 |
| 契约漂移（gits/dsh 字段不一致） | 以 `docs/dd/` 两份文档为 SSOT；联调后锁接口版本 |

---

## 9. 决策记录

- 本设计采纳 Owner 三个 A 决策：HTTP/REST（A）、dsh 即运行平台（A）、三独立 Skill（A）。
- 当前项目新增 1 个 Port（`SkillExecutionPort`）+ 2 Adapter，不改 OpenAPI，不动 R2。
- `skills` 元数据由休眠元数据 → 真实执行路由（见 3.5）。