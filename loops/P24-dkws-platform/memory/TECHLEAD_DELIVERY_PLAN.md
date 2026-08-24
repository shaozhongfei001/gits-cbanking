# P24-DKWS 架构演进 · Tech Lead 门禁计划（多阶段无人值守）

- 作者角色：Tech Lead
- 日期：2026-08-21
- 分支：`feature/P24-dkws-supplychain`
- 关联设计：`docs/dd/改造-客户经理持续经营Skill-v2-当前项目端需求详细设计.md`
- 契约：`docs/dd/skill-execute-api-contract.md`

## 目标
把"外联脚本 / 会面脚本 / R1 拜访报告"生成迁移为调用 dsh `POST /api/skill/execute`，
当前项目新增 `SkillExecutionPort` + 双 Adapter（HTTP / Fallback），激活合同 `skills` 真实接线，
`assemblyTrace` 经新查询端点暴露给前端。

## 门禁（Gate）拆分 —— 每 Gate 有独立退出条件

| Gate | 内容 | 退出条件（机器事实，非叙述） |
|---|---|---|
| G1 | 端口层 + 双 Adapter + 装配 | ✅ 已完成（19 测试 BUILD SUCCESS） |
| G2 | 三接入点改造（Outreach/Meeting/Previsit → skillExecutionPort） + 结果映射既有 DTO + 单测 | 3 接入点改完；`git diff` 确认三处 `llmClient.complete` 迁移；新增映射测试绿 |
| G3 | SkillExecutionRouter 消费 `ActivationContract.skills`(SP-02/SP-15) → dsh skillId + 接线 + 单测 | Router 单测绿；`skills` 不再休眠 |
| G4 | 合同变更：OpenAPI 新增 `GET /api/v1/assembly/trace` → `make generate` → `make check`（API-First 正式流程） | `make check` PASS；合同 hash 一致 |
| G5 | assemblyTrace 查询端点实现 + 前端控制台由模拟改消费后端轨迹 | 后端端点 200 返回轨迹；前端 test/build 过 |
| G6 | 全量验证：单测 + `make check` + backend/frontend + 与 dsh 端到端（若 dsh 可用） + 证据/FAILURES | 全绿；证据落盘 |

## 工单（Ticket）与角色
- **T2**：Feature Pilot —— 三接入点改造 + 映射（Gate G2）
- **T3**：Feature Pilot —— SkillExecutionRouter（Gate G3）
- **T4**：Tech Lead 审合同 / Feature Pilot —— OpenAPI 变更 + generate + check（Gate G4）
- **T5**：Feature Pilot —— assemblyTrace 端点 + 前端（Gate G5）
- **T6**：E2E Owner —— 全量验证 + 证据（Gate G6）

## 红线（Tech Lead 命令）
- 禁止手工改 `generated/`；specs 变更走 `make generate` / `make check`。
- 本地未配 `dsh.base-url` 时必须走 Fallback（不联网）。
- 每 Gate 完成 = 代码 + 测试 + 证据；不凭叙述自签。
- 角色职责隔离：Feature Pilot 不批自己 QA；独立 QA/E2E 才记 QA。

## 进度
- G1 ✅（已由我完成）
- G2 ⬜ → T2