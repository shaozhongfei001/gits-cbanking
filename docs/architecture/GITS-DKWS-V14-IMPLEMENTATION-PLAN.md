# GITS 对接 DKWS v1.4 实现方案与任务拆解

> 版本：v1（2026-08-24）｜ 依据：`docs/architecture/codebuddy-techlead-prompt-v14.txt`
> 契约：`docs/dd/skill-execute-api-contract.md`（v1.3 基线）+ `docs/dd/skill-execute-api-contract-v1.4.md`（增量）
> 样例：`docs/architecture/DKWS-V1.4-GITS-INTEGRATION-SAMPLES.md`（真实样例包）
> 分支：`feature/v14-dkws-integration`（自当前 P24 分支提交完成后切出）

---

## 0. 基线现状（勘察结论）

| 项 | v1.3 现状 | v1.4 缺口 |
|---|---|---|
| 命令模型 | `SkillExecutionCommand(skillId, requestId, customerId, request)` | 无 `context`、无 `async` 标志 |
| HTTP 适配器 | `DshHttpSkillExecutionAdapter` 同步 POST，顶层 `{skillId,requestId,request}` | 无 202/jobId 处理、无轮询、无 context |
| 响应解析 | 顶层 `requestId/status/data/errors/assemblyTrace/modelCalls` 全支持 | `data.result` 保持泛型 Map，无强类型 |
| 端口 | `SkillExecutionPort.execute()` 同步阻塞 | 无 `ProposalPort`、无 `InteractionMemoryPort` |
| 闸门 | 无任何闸门基础设施 | G0-G5 权威状态机 + gates 资产 + audit 镜像全缺 |
| 前端 | `EngagementWorkspace.vue` 单页卡片式 | 无建议书 Tab / 闸门视图 / 对客版放行 |
| 记忆 | `InteractionExtraction`（claim 级）已有 | 无候选/强化/取代 3 类记忆 + 衰减规则 |

装配点：`apps/api/.../config/EngagementConfig.java`（bean `skillExecutionPort`，mode http/fallback）。
配置键：`engagement.skill.mode`、`dsh.base-url`、`dsh.connect-timeout-ms`、`dsh.read-timeout-ms`。

---

## 1. 分阶段 PR 与改动清单

### PR-1 契约 DTO + async 适配器（后端）

- `scenario/execute/.../port/SkillExecutionCommand.java`：
  新增 `boolean async`、`Map<String,Object> context`（均可缺省；既有调用点零改动，构造兼容）。
- `apps/api/.../adapter/skill/DshHttpSkillExecutionAdapter.java`：
  - `contractPayload`：`"async": true` 时输出；`context` 合并（`request.context` 优先于顶层）。
  - execute 流程：async 模式 202 → 解析 `{jobId,status}` → 轮询 `GET /v1/jobs/{jobId}` → COMPLETED 取 `data.skill_result` 复用现有 parse；FAILED → `SkillExecutionException`。
- 新增 `apps/api/.../adapter/skill/DshJobPoller.java`：循环轮询至终态，退避 + TTL（可配置）。
- 新增 `JobStatusRecord(jobId, status, skillResult)` 解析 DTO。
- 配置：`engagement.skill.async-timeout-ms`（默认 120000）、`engagement.skill.async-poll-interval-ms`（默认 2000）。
- 同步路径完全不变（回归保障）。

### PR-2 ProposalPort（SP-20 服务建议书）

- 新端口 `scenario/execute/.../port/ServiceProposalPort.java`：`ServiceProposal generate(ServiceProposalCommand)`；
  内部组合 `SkillExecutionPort` + 强类型映射，不重复 HTTP 细节。
- 强类型模型 `ServiceProposal`：schemaVersion/skillId/runId/status/timestamp/
  content(proposalDraft, internalVersion{factLabels}, customerVersion{filteringNotes,includes,excludes,releaseBlockedUntil}, customerVersionNote)/
  citations/unknowns/limitations/gateRecommendations{currentGate,passedGates,overallReadiness,checklist,nextGatePrerequisites}/ruleViolations。
- `ServiceProposalMapper`：`data.result` → 强类型；未知字段忽略（契约 §5）。
- 消费方 `ServiceProposalService`（装配进 `EngagementConfig`）。
- 放行权在 GITS：`customerVersion.releaseBlockedUntil` 为空（G1/G2/G3 passed）方可展示/导出对客版。

### PR-3 InteractionMemoryPort（SP-21 交互记忆）

- 新端口 `scenario/execute/.../port/InteractionMemoryPort.java`：`apply(InteractionMemoryExtraction)`。
- 强类型：`candidateMemories / memoryUpdates / memorySupersessions` + 3 规则违规。
- 存储：GITS H2 新表 `interaction_memory`（memoryId/category/content/confidence/decayRule/evidenceQuote/status/updatedAt）；
  衰减规则实现：NONE / LINEAR（按日线性衰减）/ STEP（事件触发阶梯）。
- 生命周期归属 GITS：确认/衰减/取代全在 GITS 侧；SP-21 只产出候选。
- SP-21 为同步快任务（≤60s），不走 async。

### PR-4 闸门协作（G0-G5）

- 权威状态机 `GateStateMachine`（GITS）：currentGate / passedGates / checklist 状态；`pass(gateId, evidence)` 推进。
- 新端点消费：`GET /api/skill/gates/{customerId}` 拉取 GATE-BIZ 清单资产（适配器新方法 `fetchGateAssets`）。
- `POST /api/skill/gates/audit` 决策**镜像**：GITS 决策 → DKWS 追加 `90_control/audit/gates.jsonl`；失败不影响权威状态，可重试。
- SP-20 `gateRecommendations` 接入：checklist 合并进 GITS 权威视图。
- 放行条件：G1/G2/G3 全部 passed → `releaseBlockedUntil=[]` → 前端可导出对客版。

### PR-5 前端

- `frontend/src/api/engagement.ts`：新增 `generateServiceProposal`、`fetchGateAssets`、`auditGate`。
- `EngagementWorkspace.vue`（或独立视图）新增"服务建议书"区块：
  内部版（含 factLabels）/ 对客版（含 filteringNotes）+ 闸门状态视图（G0-G5 checklist、currentGate、放行按钮）。
- 放行 UX：`releaseBlockedUntil` 非空 → 对客版只读、导出按钮禁用。

### PR-6 测试 + 联调记录

- unit：`DshJobPollerTest`（MockRestServiceServer：202→轮询→COMPLETED/FAILED/超时）、
  `contractPayload` async/context 合并、`ServiceProposalMapperTest`（样例包全量走通）。
- integration：SP-20 async 全链路（镜像场景）、SP-21 记忆落地、闸门镜像。
- 联调记录：`docs/architecture/` 下新增，附 8106 实测请求/响应（演示环境可用时）。

---

## 2. 约束与风险

- 认证无（演示环境网络层控制）；SP-20 一律 async，SP-21 同步 ≤60s。
- 数据所有权（v1.3 延续）：context 只用于生成，不落 DKWS 权威库；记忆/闸门决策不落 DKWS。
- 三条禁止：不越权（闸门决策在 GITS）、不写知识进 customer 权威库、不静默降级（async 失败必须显式报错）。
- 本地联调依赖 8106 演示环境；CI/单测一律 MockRestServiceServer。
