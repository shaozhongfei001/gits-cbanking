# GK-KE L6 独立 QA 包

- **角色**：Independent QA（gate_review）
- **Session**：`qa-gkl6-001`
- **范围**：L0-2 → L6 全程序交付的最终验收复核
- **日期**：2026-09-12

## 1. 覆盖矩阵（12 个 Loop）

| Wave | Loop | Gate | 结果 | 变异测试 |
|---|---|---|---|---|
| A | GK1-l0-2-contract-activation | `gk_ke_openapi_lint` | PASS | ✅（负例空转 → 修复） |
| B1 | GK2-l1-1-public-semantics | `l1_1_semantics_tests` | PASS | ✅（TYPEID_UNIQUE） |
| B2 | GK3-l1-2-simulation-source | `l1_2_simulation_tests` | PASS | ✅（C001 公式） |
| B3 | GK4-l2-2-registry | `l2_2_registry_tests` | PASS | ✅（CAS 空转 → 修复） |
| C1 | GK5-l2-1-semantic-query | `l2_1_semantic_query_tests` | PASS | ✅（白名单冗余掩盖 → 修复） |
| C2 | GK6-l3-1-factory-candidate | `l3_1_factory_tests` | PASS | ✅（回链空转 → 修复） |
| D1 | GK7-l3-2-review-release | `l3_2_release_tests` | PASS | ✅（5 类拒绝空转 → 修复） |
| D2 | GK8-l4-1-map-activation | `l4_1_map_activation_tests` | PASS | ✅（排序 / 歧义） |
| C3 | GK9-l5-1-kuzu | `l5_1_kuzu_tests` | PASS | ✅ |
| C3 | GK10-l5-2-lightrag | `l5_2_lightrag_tests` | PASS | ✅（门槛口径错误 → 修复） |
| E | GK11-l4-2-gits-closed-loop | `l4_2_closed_loop_tests` | PASS | ✅（6 类拒绝空转 → 修复） |
| F | GK12-l6-runtime-acceptance | `l6_runtime_acceptance_tests` | PASS | ✅（统一真值函数） |

## 2. 方法论：变异测试为中心

本程序贯穿使用**变异测试**验证断言非空转：
故意破坏被测判定逻辑，要求测试**必须转为失败**。

**共捕获 6 个空转/口径缺陷**：
- `FAIL-2026-09-12-02` L0-2 负例断言空转（BLOCKER）
- `FAIL-2026-09-12-07` L2-2 CAS 断言空转
- `FAIL-2026-09-12-09` L2-1 白名单主防线被冗余路径掩盖
- `FAIL-2026-09-12-11` L3-1 回链断言无触发路径
- `FAIL-2026-09-12-12` L3-2 五类拒绝断言全部空转
- `FAIL-2026-09-12-13` L5-2 门槛口径错误（与 B 比较误写成与 A）
- `FAIL-2026-09-12-14` L4-2 六类拒绝断言全部空转
- `FAIL-2026-09-12-15` L6 五类验收主断言空转

> **共同模式**：全部夹具为合规正例 → 拒绝分支从不进入 → 断言恒真。
> **共同修复**：统一 `detect_*(doc)` 真值函数 + fail-closed（缺夹具即失败）+ 变异复验。

这是本程序**最有价值的发现**：若只跑一次"全绿"，会上报 12 个虚假 PASS。

## 3. 否定式要求清单（必须由违规夹具证明）

| 要求 | 来源 | 违规夹具 |
|---|---|---|
| 禁止任意 SPARQL/Cypher/rawSql | C04 §6 | ✅ |
| 禁止白名单外动作（转账/放款/授信审批） | OWNER-003 §6.1 | ✅ |
| 禁止审批后改字 | C08 L3-2 | ✅ |
| 禁止半发布 | C08 L3-2 | ✅ |
| 禁止撤销后仍可检索 | C08 L3-2 | ✅ |
| 禁止回滚到已撤销版本 | C03 §6.6 | ✅ |
| 禁止用途静默升级 | C03 §4 | ✅ |
| 禁止图不可用时返回 200 空结果 | C08 L5-1 | ✅ |
| 禁止把客户声明当事实 | C03 §8 | ✅ |
| 禁止用途未知却通过准入 | C03 §8 | ✅ |
| 禁止自审自批 | C06 §1 | ✅ |
| 禁止 KERT 计划含 GITS 写回 | C06 §2 | ✅ |
| 禁止删除后可重放 | C08 L6 | ✅ |
| 禁止未实测 RTO 提交目标 | C08 §6 | ✅ |

## 4. 关键数学真值

| 值 | 断言 | 独立复算 |
|---|---|---|
| C001 日均存款 | **2,983,333.33 CNY** | ✅ C07 §5 公式（按日跨账户汇总 ÷ 30 天） |

## 5. 红线核查

| 项 | 结果 |
|---|---|
| `generated/` 手工编辑 | 无（`make generate` 可重现） |
| 封版 `docs/dd/gk-ke-contract/` | 未改（tree `4c5f5373` 一致） |
| P20 / DKES / PI-0 合同 | 未改 |
| `CONTRACT_CANDIDATE` → `APPROVED` | 未改（21 CANDIDATE / 0 APPROVED） |
| `PLANNED_NOT_EXECUTED` → `PASS` | 未改（36 项） |
| `git add .` | 未使用（显式路径） |
| 隔离资产启用 | 无 |
| 生产写回 | 无（SIM only） |

## 6. QA 结论

**QA_PASS**（技术侧）。

**未覆盖（Owner 职责，不代签）**：
- L1-1 语义专家审、L1-2 数据专家核对、L2-1 指标 Owner 签署（OM-C1/C2）
- L3-2 知识 Owner 签署（OC-03）
- L4-1 知识/能力 Owner 签署（OC-04）
- L4-2 **业务专家验收（OB-C3）**（OC-05）
- **L6 试点范围裁定**（Owner 决定）
