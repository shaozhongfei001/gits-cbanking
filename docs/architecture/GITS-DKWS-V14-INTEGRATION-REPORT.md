# GITS ↔ DKWS v1.4 集成联调记录

> 版本：v1（2026-08-24）｜ 分支：`feature/v14-dkws-integration`（规划，自 P24 分支提交后切出）
> 契约：`docs/dd/skill-execute-api-contract-v1.4.md` ｜ 实现方案：`GITS-DKWS-V14-IMPLEMENTATION-PLAN.md`
> 真实样例：`docs/architecture/DKWS-V1.4-GITS-INTEGRATION-SAMPLES.md`

---

## 1. 交付物清单（本轮已完成代码）

| PR | 改动 | 文件 | 测试 |
|---|---|---|---|
| PR-1 契约 DTO + async | `SkillExecutionCommand` 加 `async`/`context`（4 参重载兼容） | scenario/execute/.../port/SkillExecutionCommand.java | ✅ 8 |
| | async 202+轮询适配器 | apps/api/.../adapter/skill/DshHttpSkillExecutionAdapter.java | 同上 |
| | 轮询器 | apps/api/.../adapter/skill/DshJobPoller.java | ✅ 5 |
| | job 快照 DTO | apps/api/.../adapter/skill/JobStatusRecord.java | — |
| PR-2 SP-20 | 强类型模型/命令/端口 | scenario/execute/.../port/ServiceProposal{,.java,Command.java,Port.java} | — |
| | 映射器 | apps/api/.../adapter/skill/ServiceProposalMapper.java | ✅ 4 |
| | 消费服务 | apps/api/.../api/service/ServiceProposalService.java | — |
| PR-3 SP-21 | 强类型模型/端口 | scenario/execute/.../port/InteractionMemory{Extraction.java,Port.java} | — |
| | 映射器/服务 | apps/api/.../adapter/skill/InteractionMemoryMapper.java + api/service/InteractionMemoryService.java | ✅ 4 |
| PR-4 闸门 | 端口/资产模型 | scenario/execute/.../port/SkillGatePort.java + GateAssets.java | — |
| | 权威状态机 | scenario/execute/.../service/GateStateMachine.java | ✅ 6 |
| | HTTP 适配器 | apps/api/.../adapter/skill/DshHttpSkillGateAdapter.java | — |
| | 本地回退 | apps/api/.../adapter/skill/FallbackSkillGateAdapter.java | — |
| PR-5 前端 | API 客户端 | frontend/src/api/v14.ts | — |
| | 建议书视图（内部/对客/引用/闸门/记忆） | frontend/src/views/ServiceProposalView.vue | — |
| | 路由 + 工作台入口 | frontend/src/router/index.ts、EngagementWorkspace.vue | — |
| PR-6 测试 | 上述单测合计 | — | ✅ 27/27 |

后端装配：`apps/api/.../api/config/EngagementConfig.java`（`serviceProposalPort` / `interactionMemoryPort` / `skillGatePort` / 两个 mapper）。
Controller：`apps/api/.../api/controller/V14DkwsIntegrationController.java`（`/api/v14/proposals`、`/memories/extract`、`/gates/*`）。

---

## 2. 联调请求/响应映射（对齐 8106 真实样例）

### 2.1 SP-20 生成（async）

请求（GITS → DKWS `POST /api/skill/execute`）：
```json
{
  "skillId": "SP-20",
  "requestId": "V14-20260824-001",
  "async": true,
  "request": {
    "customerId": "CUST-CORP-0001",
    "context": {
      "enterpriseData": { "customerId": "CUST-CORP-0001" },
      "interactionMemories": [],
      "previousReports": []
    }
  }
}
```

202 响应：`{ "jobId": "JOB-SKILL-20260824-001", "status": "PENDING" }`

轮询（GITS → DKWS `GET /v1/jobs/JOB-SKILL-20260824-001`）：
```json
{ "jobId": "JOB-SKILL-20260824-001", "status": "ok",
  "data": { "status": "COMPLETED",
    "skill_result": {
      "requestId": "V14-20260824-001", "status": "ok",
      "data": { "result": { "schemaVersion": "1.0.0", "skillId": "SP-20",
        "runId": "RUN-SP20-20260824-001", "status": "SUCCESS",
        "content": { "proposalDraft": "## 1. 客户经营现状与核心诉求",
          "internalVersion": { "content": "...", "factLabels": { "F-001": "F" } },
          "customerVersion": { "content": "...", "filteringNotes": ["仅保留 F/A 事实"],
            "includes": ["F-001"], "excludes": [], "releaseBlockedUntil": [] },
          "customerVersionNote": "对客版已按规则过滤" },
        "citations": [{ "id": "C-001", "claim": "...", "source": "CRM",
          "date": "2026-08-01", "factLabel": "F", "chapterRef": "CH1" }],
        "unknowns": [], "limitations": [],
        "gateRecommendations": { "currentGate": "G2", "passedGates": ["G0","G1"],
          "overallReadiness": "READY_FOR_REVIEW", "checklist": [], "nextGatePrerequisites": [] },
        "ruleViolations": [] } } } } }
```

GITS 侧处理：`DshJobPoller` COMPLETED 取 `data.skill_result` → 复用同步 parse → `ServiceProposalMapper` 强类型化（未知字段忽略，契约 §5）。**同步路径不变（回归保障）。**

### 2.2 SP-21 记忆抽取（同步 ≤60s）

请求：`skillId: "SP-21"`，`request.context = { interactionContent, existingMemories }`。
结果：`data.result.candidateMemories / memoryUpdates / memorySupersessions / ruleViolations`，
GITS 侧 `InteractionMemoryMapper` 强类型化；生命周期（确认/衰减/取代）归属 GITS。

### 2.3 闸门协作

- `GET /api/skill/gates/{customerId}` → GATE-BIZ 清单资产（仅输入，非权威）。
- GITS `GateStateMachine` 为权威（currentGate/passedGates/checklist/releaseReady）。
- `POST /api/skill/gates/audit` 镜像决策追加 `90_control/audit/gates.jsonl`；**失败不影响权威状态**（可重试，返回 `recorded:false`）。

---

## 3. 测试结果

| 测试 | 覆盖 | 结果 |
|---|---|---|
| `DshHttpSkillExecutionAdapterTest` | 同步/404/async COMPLETED/async FAILED/context 合并 | 8/8 |
| `DshJobPollerTest` | COMPLETED/RUNNING→COMPLETED/FAILED/500/超时 | 5/5 |
| `ServiceProposalMapperTest` | 样例包 §2.4 全量映射/违规 PARTIAL/缺失回退/未知字段 | 4/4 |
| `InteractionMemoryMapperTest` | 样例包 §3 全量映射/BLOCKING/缺失/未知字段 | 4/4 |
| `GateStateMachineTest` | 初态/推进/放行条件/阻滞/吸收建议/未知闸门 | 6/6 |
| **合计** | — | **27/27** |

前端：`vue-tsc --noEmit` 通过；新增 `v14.ts` API 客户端 + `ServiceProposalView.vue`（内部版/对客版/引用/闸门/记忆 Tab）。

---

## 4. 待办（依赖 8106 演示环境可用时）

1. 真机联调：SP-20 async 全链路、SP-21 抽取、闸门资产/镜像（附实测请求/响应回填 §2）。
2. 上下文生命周期确认：`context` 由 GITS 生命周期管理（不落 DKWS 权威库）。
3. PR-3 记忆落库（H2 `interaction_memory` 表 + 衰减规则 NONE/LINEAR/STEP 实现）在 P24 分支提交后并入。
