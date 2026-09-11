# 独立 QA 报告：GK1-l0-2-contract-activation（C08 L0-2 契约激活）

- **角色**：Independent QA（gate_review）
- **Session**：`qa-gk1-l02-001`
- **审计对象**：L0-2 契约激活候选（WI-01 OpenAPI / WI-03 正负例 / WI-04 消费者测试）
- **审计基线**：`597d6fac`（开工）→ `8777195`（作者交付）→ 本报告结论提交（含 QA 发现修复）
- **审计时间**：2026-09-12
- **结论**：**QA_PASS**（经 1 次 BLOCKER 退回修复后）

> 独立性声明：本审计**未采信**作者自述的"6 门禁全 PASS / 44 负例确实被拒"。
> 所有结论均为独立复现所得；关键项执行了**变异测试**（mutation testing）以验证断言非空转。

---

## 1. 逐项审计结论

| # | 审计项 | 结论 | 独立证据 |
|---|---|---|---|
| 1 | 合同源可解析且为 OpenAPI 3.1.1 | **PASS** | `python3 -c "..."` → `3.1.1` |
| 2 | C06 §1 的 15 个 operation 全覆盖 | **PASS** | 实测 count=15，逐项对齐权威源 C06 §1 |
| 3 | 闭集未静默扩展（20 schema） | **PASS** | 20/20 `simulationOnly={const:true}` 且 required，`additionalProperties=false` |
| 4 | 命名空间隔离 `/gk-ke/v1` vs `/api/v1` | **PASS** | `servers[].url=/gk-ke/v1`；`git diff` 显示 `specs/openapi/` 仅新增 1 文件，未改既有 2 个 |
| 5 | `simulationOnly` 未在 OpenAPI 层放宽 | **PASS** | `x-gk-ke-simulation-only=true`；无 `type:boolean` 放松 |
| 6 | **负例非 noop（变异测试）** | **PASS（修复后）** | 见 §2 —— 首次变异**未**触发 FAIL，退回修复后变异**正确 FAIL** |
| 7 | 6 个门禁证据哈希真实性 | **PASS** | 6/6 sha256 重算一致，`status=pass`、`exit_code=0` |
| 8 | FAILURES 自愈记录真实性 | **PASS** | `resolve_refs()` 与 `ExpectedVersion` 参数均实际存在 |
| 9 | 受测封版制品未改 | **PASS** | `git diff docs/dd/gk-ke-contract/` 为空 |
| 10 | 禁止项核查 | **PASS** | CANDIDATE=21 / APPROVED=0；PLANNED_NOT_EXECUTED=36 未改；`generated/` 仅 make generate 产出且**可重现**（重跑后 `git status` 为空） |

## 2. 变异测试（本次审计的核心反自证检查）

**目的**：验证断言 [5] "negative example was NOT rejected" 不是空转。

| 轮次 | 操作 | 期望 | 实测 | 判定 |
|---|---|---|---|---|
| 第 1 轮（修复前） | 把 `negative/createSimAction_1.json` 的 `actionType` 由 `TRANSFER_FUNDS`（白名单外）改为 `CREATE_FOLLOWUP_TASK`（白名单内），使其不再是负例 | 测试 FAIL | **PASS（假通过）** | ❌ **BLOCKER** |
| 第 2 轮（修复后） | 同一变异 | 测试 FAIL | **FAIL**（`[5] createSimAction_1.json: negative example was NOT rejected`） | ✅ |
| 恢复 | 还原原文件 | 测试 PASS | **PASS**（44 负例） | ✅ |

**根因（记录为 FAIL-2026-09-12-02）**：`_is_rejected()` 先用"生成期显式标志位"（含 `sameKeyDifferentPayload`）短路返回 `True`，
导致带标志位的负例**恒判为已拒绝**，根本未走到 `SIM_ACTION_NOT_WHITELISTED` 的语义判定。
即断言 [5] 对绝大多数负例是 **noop**——作者此前"44 负例确实被拒"的结论**不成立**。

**修复**：改为**规则驱动 + fail-closed**——每条 `rule` 必须映射到对被测数据求值的真值检查函数；
未知 rule 直接判为"未拒绝"使测试 FAIL，不得放过。

**修复后复验**：变异 → FAIL；恢复 → PASS。断言非空转，结论可信。

## 3. 冲突/漂移清单

| 编号 | 描述 | 级别 | 状态 |
|---|---|---|---|
| D-1 | **`_is_rejected()` 断言空转**（标志位短路）→ 负例"被拒"结论不可信 | BLOCKER | 已修复并复验（FAIL-2026-09-12-02） |
| D-2 | 文档措辞：`LOOP.yaml` 的 `objective[1]`/`workitems[L0-2-WI-01].name`/`gates[gk_ke_openapi_lint].pass_condition` 写 "14 endpoint rows"，而实际为 **15 operation**（C06 §1 表 14 行 + 配套 `GET /knowledge/jobs/{id}`） | MINOR（文档） | 已修正为 15 |

## 4. 独立性边界（明确未覆盖项）

本次 QA **未**执行、也不声称覆盖：

- 服务级 E2E（无运行中的 GK-KE 服务；L0-2 交付物为合同候选，不含服务实现）
- Kuzu / LightRAG 适配（属 L5）
- 真实银行系统联调、真实凭据、生产写回（明确不在 L0-2 scope）
- Owner 激活决定（**不由 QA 代签**）

## 5. QA 结论

**QA_PASS** —— 在 §3 的 D-1 修复并复验后：

- 15/15 operation 覆盖权威源 C06 §1；
- 20/20 schema 闭集与 `simulationOnly` 未放宽；
- 命名空间隔离有效，既有 OpenAPI 与封版制品未被修改；
- 44 个负例的"被拒"结论经**变异测试**证明非空转；
- 6 个门禁证据哈希真实、`generated/` 可重现；
- 禁止项（CANDIDATE 改 APPROVED、36 项改 PASS、手工改 generated、改封版）**全部未违反**。

**移交**：Owner 批准激活 + OC-01 收口（属 Owner 权限，QA/TL 不得代签）。
