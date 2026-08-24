# 客户经理持续经营 Skill — deepseek-harness 端需求详细设计

- 版本：V1.0
- 日期：2026-08-21
- 关联：当前项目端文档（`docs/dd/客户经理持续经营Skill-v2-当前项目端需求详细设计.md`）
- 基线决策（Owner 确认）：
  1. 桥接方式 = **A**：dsh 做 HTTP/REST 服务（Typert 暴露 `POST /api/skill/execute`），当前项目用 Spring RestClient 调
  2. 运行平台 = **A**：**dsh 即运行平台**（`SkillRegistry` + Typert 激活并发布 skill 服务）
  3. Skill 拆分 = **A**：外联脚本 / 会面脚本 / R1 拜访报告 = **三个独立 Skill**，各自可单独激活

---

## 1. 现状与目标

### 1.1 现状（deepseek-harness 端）
- dsh 具备 **Skill** 概念：Skill 目录 + `SKILL.md` 定义 + `ctx.skills` 注册表 + Skill 内可调大模型（DeepSeek/OpenAI 兼容）。
- 已具备 **Typert GATEWAY**：可将函数/工具暴露为 HTTP 服务。
- 但：**无"客户端经理持续经营"相关 Skill**；Skill 为"文件内执行"，未以**常驻 HTTP 服务**向外提供。

### 1.2 目标
把"外联脚本、会面脚本、R1 拜访报告"的生成能力，从当前项目（gits 侧 `LlmClient` 快速内）**迁移为 dsh 平台上的三个可激活、可发布的服务 Skill**。当前项目通过 HTTP 调用激活；dsh（SkillRegistry + Typert）承担**运行平台**职责（服务激活 + 服务发布）。

---

## 2. 架构定位

```
                当前项目(gits)                     deepseek-harness (dsh) = 运行平台
┌──────────────────────────┐           ┌──────────────────────────────────────────┐
│  EngagementWorkflow      │  HTTP     │  Typert GATEWAY                          │
│  └ SkillExecutionClient  │─────────► │  POST /api/skill/execute                 │
│     (Spring RestClient)  │           │      │ 激活                              │
│                          │◄─────────│  SkillRegistry ──► 三个服务的 Skill       │
│  消费结构化结果          │  服务发布 │      └ outreach / meeting / previsit     │
└──────────────────────────┘           │  Gaerer+DpSeek                           │
                                       └──────────────────────────────────────────┘
```

- **服务激活**：当前项目调 `POST /api/skill/execute`（带 skillId + 请求题），dsh 查 `SkillRegistry` 定位 skill 并执行。
- **服务发布**：dsh 把三个 Skill 注册进 `SkillRegistry` 并提供 Typert 路由；对外发布 `POST /api/skill/execute` + 业务结果结构契约。

---

## 3. 三个 Skill 定义

| Skill id | 产物 | 输入 | 输出（结构化） |
|---|---|---|---|
| `skill-customer-outreach-script` | 外联脚本 | 客户画像 / KYC 摘要 / 访前目标 | `OutreachScriptResult` |
| `skill-customer-meeting-script` | 会面脚本 | 客户画像 / 产品候选 / 敏感点 | `MeetingScriptResult` |
| `skill-customer-previsit-report` | R1 拜访报告 | 知识上下文(KI) / 结构化事实 / 供应链图谱 | `PrevisitReportResult` |

> 三个 skill 均服务 `客户经理持续经营` 复合意图，但**各自可独立激活**（基线决策 A）。

---

## 4. 详细需求

### 4.1 Skill 目录结构（dsh 侧落地）
```
deepseek-harness/
  skills/
    customer-engagement/                     # 客户经理持续经营 skill 族
      SKILL.md                               # 族定义：name/version/description/intents
      outreach-script/SKILL.md               # 子 skill：外联脚本
      meeting-script/SKILL.md                # 子 skill：会面脚本
      previsit-report/SKILL.md               # 子 skill：R1 拜访报告
      main.py                                # 入口：暴露注册各子 skill 逻辑
  gateway/                                   # Typert 服务网关
    skill_api.py                             # @Remote 暴露 skill 执行路由
```

### 4.2 Skill 执行契约（HTTP）
`POST /api/skill/execute`
```json
{
  "skillId": "skill-customer-previsit-report",
  "requestId": "req-<uuid>",
  "request": {
    "customerId": "CUST-CORP-0001",
    "knowledgeContext": "...",      // gits 组好的知识上下文/KI
    "structuredFacts": { },          // 客户画像/KYC/产品候选（若需要）
    "supplyChainMarkdown": "..."     // 供应链图谱（previsit 用）
  }
}
```
响应（统一）：
```json
{
  "requestId": "req-...",
  "status": "ok" | "skill_error" | "exit_policy_no_new_evidence",
  "data": { }                       // skill-specific result
  "assemblyTrace": [ { "kiId","phase","status","message" } ],
  "modelCalls": [ { "model","inputTokens","outputTokens","latencyMs" } ]
}
```

### 4.3 服务发布（dsh 职责）
- **注册**：dsh 启动时 `SkillRegistry.register(...)` 三个 skill（读 `SKILL.md` + `main.py`）。
- **暴露**：Typert `@Remote` 生成 `POST /api/skill/execute` 路由，绑定 SkillRegistry。
- **健康**：`GET /api/skill/health` → 返回已注册 skill id + version。
- **发布结果**：每个 skill 执行返回统一 `assemblyTrace`（轨迹）+ 模型调用元数据，供 gits 记录与前端控制台。

### 4.4 模型调用（dsh 职责）
- 每个 skill 内部经 dsh 已有 DeepSeek/OpenAI 兼容客户端调用模型。
- 遵循 **fail-closed**：模型不可用/超时 → 返回 `status=skill_error` + 可纺；不返回残缺半成品。
- **机器事实优先**：skill 输出结构化字段不得臆造客户事实（证据驱动，§治理）。

### 4.5 治理与纪律（dsh 侧硬边界）
- `UNATTENDED_24X7_AUTHORIZED`：服务默认不可无人值守生成需人工批准的内容；正式外联/会面/拜访报告是非告警 or `humanGate` 产物。
- **无新证据不闭合**：若请求仅提供旧证据，skill 返回 `status=exit_policy_no_new_evidence`，不生成"新报告"冒充进展。
- 敏感数据：skill 输入/输出不落盘 key；日志脱敏。

---

## 5. 验收标准（dsh 端）

| # | 验收点 |
|---|---|
| D1 | 三个 skill 注册成功，`GET /api/skill/health` 列出且版本正确 |
| D2 | `POST /api/skill/execute` 对 outreach/meeting/previsit 各返回结构化结果 + `assemblyTrace` + `modelCalls` |
| D3 | 每个 skill 支持 `requestId` 幂等与 `fail-closed`（模型故障返回 skill_error） |
| D4 | 无新证据时 previsit skill 返回 `exit_policy_no_new_evidence`（不伪生成） |
| D5 | 模型调用元数据（token/延迟）正确记录，无敏感数据泄露 |
| D6 | 服务可通过 gits 侧 `POST /api/skill/execute` 被真实调用（端到端） |

---

## 6. 里程碑

| M | 内容 |
|---|---|
| M1 | Skill 族骨架 + 三个 SKILL.md 定义 + main.py 注册 |
| M2 | Typert skill_api 暴露 `/api/skill/execute` + health |
| M3 | 三个 skill 内联生成逻辑（接 DeepSeek） |
| M4 | assemblyTrace + modelCalls 元数据 + fail-closed + 无新证据策略 |
| M5 | 端到端联调（gits 调 EXEC） |
