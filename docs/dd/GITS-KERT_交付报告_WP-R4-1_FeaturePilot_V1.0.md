# WP-R4-1 交付报告（Feature Pilot）

> Loop: `GK0-contract-activation` · 角色: `feature_pilot` · 日期: 2026-09-11
> 状态: `DEV_SELF_CHECK_PASS`（待独立 QA，禁止 dev 自签 QA_PASS）

## 执行结果总览

| # | 任务 | 落点 | 登记 | 状态 |
|---|---|---|---|---|
| 1 | MetricDefinition.full（F06 G1） | `schemas/MetricDefinition.full.schema.json` | CTR-GKKE-015 | done |
| 2 | negative_cases.json（F06 G2/G3 + F08 H2） | `simulation/oracles/negative_cases.json` | — | done |
| 3 | verify_simulation.py（F08 H1） | `tools/verify_simulation.py` | — | done |
| 4 | 四注册对象 Schema（F04） | `SourceVersion/Capability/QueryDefinition/Release.schema.json` | CTR-GKKE-016~019 | done |
| 5 | LegacyRagHit（F07） | `schemas/LegacyRagHit.schema.json` | CTR-GKKE-020 | done |
| 6 | SemanticPackage 补写入口（F03） | `schemas/SemanticPackage.schema.json`（CTR-GKKE-001） | 不变 | done |

## 验证结果

| 门禁 | 结果 |
|---|---|
| `make generate` | PASS |
| `make check` | PASS |
| gk-ke 合同样例 | 正例 20/20，负例被拒 40 |
| `tools/verify_simulation.py` | PASS（exit=0） |
| `make memory-check` | PASS |
| `make evidence-check` | PASS |

## 关键决策记录（Feature Pilot 裁决，非 Owner 决议）

1. **任务 2 落点**：派工单给了两个候选（`examples/negative_cases.json` 或 `simulation/oracles/negative_cases.json`）。采用后者，理由：
   - 负例本质是 oracle 断言（供 `verify_simulation.py` 读取），非 schema 对拍样例；
   - 与 `expected.json` 同级，语义一致；
   - 天然隔离，不污染 `simulation/tables/` 正常快照。
   - 若 Owner 要求改落点，为低风险纯移动操作。

2. **任务 6 字段名**：C01 §2 要求"唯一变更责任"，落地为 `writeOwner`（唯一变更责任方）+ `writeEntry`（唯一写入口）+ 可选 `authorityScope`，均为新增可选字段，`required` 未含，向后兼容。

## 交付物清单

- 变更 diff：`specs/gk-ke/v1/schemas/`（+6 schema，1 修改）、`specs/gk-ke/v1/examples/`（+6 正例 +12 负例）、`specs/CONTRACT_INDEX.yaml`（+6 登记）
- 生成制品：`generated/gk-ke/v1/` 新增 6 个（只读，`make generate` 产出）
- 复算脚本：`tools/verify_simulation.py`
- 负例清单：`docs/dd/gk-ke-contract/simulation/oracles/negative_cases.json`
- Loop 状态：`STATE.json`（6 任务 done，`ready_for_independent_qa`）、`EVIDENCE.json`（remediation_wp_r4_1）、`NEXT_SESSION.md`（Baton → 独立 QA）、`ROLE_BOARD.yaml`（feature_pilot done_dev_self_check）

## 残留项（如实列出）

- 无未完成项；无虚构 PASS。
- 独立 QA 尚未记录（`independent_qa.status = pending`），需 TL 发起独立 QA 会话。
- Owner 最终决议待定。

## Baton 交接

```
[收工] Loop: GK0-contract-activation, Gate: remediation_complete, Baton → independent_qa
```
