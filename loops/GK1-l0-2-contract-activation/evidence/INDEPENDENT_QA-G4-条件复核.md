# G4 独立 QA 条件复核报告（受影响范围复核）

- **角色**：Independent QA（gate_review）
- **Session**：`qa-gk1-g4-001`
- **依据**：`GK-KE-OWNER-002` §5 G4「独立 QA 将原报告绑定到受测制品，并对 G1–G3 引入的差异核查；
  如修改了合同或执行约束，复测相关生成一致性、消费者及语义负例。**未变部分可引用原 QA 证据**」
- **复核对象**：G1–G3 补证工作引入的差异（提交 `f57eae2` → `411e669`）
- **日期**：2026-09-12
- **结论**：**G4 关闭**

---

## 1. G1–G3 差异范围实测

| 检查 | 命令 | 结果 |
|---|---|---|
| 全量差异 | `git diff f57eae2..411e669 --stat` | 9 文件，**全部为文档**（决议稿、G1-G3 证据登记、OWNER-RESOLUTION、EVIDENCE/STATE/ROLE_BOARD/NEXT_SESSION/ORCHESTRATOR/BLOCKED） |
| **合同源差异** | `git diff f57eae2..411e669 --stat -- specs/` | **空** |
| **脚本差异** | `git diff f57eae2..411e669 --stat -- scripts/` | **空** |
| **生成物差异** | `git diff f57eae2..411e669 --stat -- generated/` | **空** |
| **合同样例差异** | `git diff f57eae2..411e669 --stat -- specs/gk-ke/` | **空（byte-identical）** |

**判定**：G1–G3 **未修改任何合同、脚本、生成物或样例**。
按 §5 G4「未变部分可引用原 QA 证据」→ **原 QA 报告 `INDEPENDENT_QA-L0-2.md` 继续有效，无须重跑。**

## 2. 受测制品绑定核验

| 项 | 值 | 校验 |
|---|---|---|
| 原 QA 受测 HEAD | `f57eae2774fbc322fed873201f54442e109e88e5` | — |
| 现 HEAD | `411e669` | — |
| `specs/openapi/gk-ke-v1.openapi.json` 在两提交间 | **完全相同** | `git diff --stat` 为空；内容 sha256 仍为 `e9df42d3…` |
| 原 QA 报告完整性 | sha256 `6ee5eb793d355fc77420ed982183f1505fc0ccc5d3b804b1ed1a56ee759e3fed` | 未变 |

**绑定成立**：QA 报告的结论直接适用于当前拟激活制品。

## 3. 门禁复跑（确认 G1–G3 未使任何门禁漂移）

在**当前 HEAD** 复跑（非引用历史结果）：

| 门禁 | 命令 | 退出码 |
|---|---|---|
| contract_generate | `make generate` | **0** |
| contract_check | `make check` | **0** |
| gk_ke_openapi_lint | `python3 scripts/gk_ke_openapi_contract_tests.py` | **0**（15/15 operations） |
| gk_ke_examples | `python3 scripts/gk_ke_contract_examples.py` | **0**（20 pos / 40 neg） |

## 4. 变异测试复验（确认 QA 断言仍非 noop）

因 §5 G4 要求"如修改了…执行约束，复测"，即使本次未改合同，仍**复验断言有效性**：

| 步骤 | 期望 | 实测 |
|---|---|---|
| 变异 `createSimAction_1.actionType` → 白名单内 | 测试 FAIL（exit 1） | **exit 1** ✅ |
| 恢复原文件 | 测试 PASS（exit 0） | **exit 0** ✅ |

**结论**：变异测试**仍然有效**，断言非 noop。原 QA 的 BLOCKER 修复（FAIL-2026-09-12-02）在 G1–G3 后依然成立。

## 5. 工作区完整性

| 检查 | 结果 |
|---|---|
| `git status --short specs/` | **空**（变异临时文件已恢复，无残留） |
| `generated/` 可重现 | `make generate` 后无差异 |

## 6. G4 具体风险项核查（§5 line 108 点名）

§5 要求 G4 针对具体风险取证，不机械追加测试数量：

| 风险 | 对应负例 | 状态 |
|---|---|---|
| 产品集合未误并为单卡 | `getCorePackageVersion_1`、G3 重分类（AssetVersion=ID_REF） | ✅ 已覆盖 |
| 激活契约未当作计划 | `createPlan_3`（planHash 非确定拒绝）+ G2 映射 4 裁定 | ✅ 已覆盖 |
| `VALIDATION` 未绕过发布 | OF-02 三平面分离 + 3 条反例 | ✅ 已覆盖 |
| 歧义路由拒绝 | `createPlan_1`（ROUTE_AMBIGUOUS 409） | ✅ 已覆盖 |

## 7. G4 结论

**G4 关闭。** 依据：

1. G1–G3 **零合同/脚本/生成物差异** → 原 QA 证据有效，无须重跑（§5 明文允许）。
2. 受测制品与拟激活制品**字节相同**，QA 报告完整性校验通过。
3. 四项门禁在当前 HEAD **复跑全绿**，无漂移。
4. 变异测试**复验有效**（变异 FAIL / 恢复 PASS），断言非空转。
5. 四项点名风险均有对应负例或裁定覆盖。

**独立性声明**：本复核由独立 QA 角色执行；TL 未参与结论形成（TL 只提供 G1–G3 证据供审）。
本报告**不代替** Owner 对激活的裁定，也不使 OC-01 自动关闭——OC-01 关闭需 G2 一并完成。
