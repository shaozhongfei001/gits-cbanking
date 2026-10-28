# GK6-simulation-factory｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-10T15:35:20Z` |
| **holder** | `owner_review` |
| **packet** | `GK6-simulation-factory` |
| **wave** | `W0` |
| **QA verdict** | **QA_PASS**（独立 QA `gk6-qa`，session `qa-gk6-formal-001`，离线工厂范围） |
| **do_not_start** | REAL_E2E_PASS、BUSINESS_SIGNED、生产探针、真实人工审批（须后续独立 Loop） |

短提示词：独立 QA 已完成并记录 QA_PASS（`EVIDENCE.json.independent_qa.status=pass`，证据 `evidence/independent_qa.md`，sha256 `f14198312bd7c0f40354044dc7b29db6f3f253f32c2ba2974df35cd049855623`）。STATE.status=`qa_pass`。请 Tech Lead 复核并关闭/归档 Loop。

## QA 复核摘要

- 6 gate 全部由 QA 独立重跑 PASS：contract_check、vendor_factory（连跑两次 sha256 逐字节一致）、validate_dataset（117/117）、isolation_oracle（11 tests）、tooling_test（11 tests）、security-check。
- QA 自写只读真值复算 42/42 PASS：12/24/6/30/144/288/720/12/12/18 计数；C001 日均 2,983,333.33 CNY；每事件同币借贷相等反向；closing=opening+ΣsignedAmount；次日 opening=前日 closing；FK 闭包；授信边界。
- T31：manifest/语料哈希 0 失配；schema 14 正/28 负；图引用闭包；30M 提及≠持有；同名不同身份；0.9.0/1.0.0 版本族。
- T32：10 个 guard 负例独立变异全部被稳定错误码拒绝（生产写、探针、自批、真实审批标记、陈旧版本、预测当事实、币种未确认、客户端注入授权、缺 simulationOnly、非 SIM- ID）。
- T33：oracle 不进任何语料清单/图/文档；独立泄漏负例被拒；构建器无 random/网络/模型/DB；sqlite 仅 `:memory:` 校验 SQL 模板。
- 合同纪律：`git diff --stat c7017b1 HEAD -- specs generated` 为空；无真实客户/机构/凭据。

## 范围边界（不构成生产就绪）

验收矩阵 T30–T33 标注 PLANNED_NOT_EXECUTED 且要求服务验证/生产探针/真实审批；本 Loop 经 Owner 豁免为离线工厂范围。QA_PASS 仅覆盖离线证据；服务化 E2E、生产探针、真实人工审批、BUSINESS_SIGNED 须后续独立 Loop 承接。

## 待办（Tech Lead）

1. 复核 QA 证据与 `make check` / `python3 scripts/loop_guard.py --loop GK6-simulation-factory --memory-only`。
2. 关闭/归档 Loop；如需推进服务化，新建 Loop 并登记合同/基线变更。
