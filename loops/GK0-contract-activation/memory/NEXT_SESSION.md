# GK0-contract-activation｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-11` |
| **holder** | `owner`（各领域 Owner 并行） |
| **packet** | `GK0-contract-activation` |
| **wave** | `W2（Owner 决议）` |
| **do_not_start** | 无（QA_PASS 已达成，进入 Owner 决议） |
| **review_result** | `RETURN_TO_HLD_RESOLVED`（qa-gk0-formal-001 QA_PASS） |

## 短提示词

你是 GK-KE 各领域 Owner。独立 QA 已对 WP-R4-1 合同源整改记录 QA_PASS（qa-gk0-formal-001，HEAD 91d5fed），RETURN_TO_HLD 已解除。

待你做的 Owner 决议（并行，各司其职）：

1. **指标 Owner**：认定 `SIM.METRIC.CUSTOMER_AVG_DEPOSIT` 的指标口径（30 自然日/CNY/日均公式）。
2. **知识 Owner**：认定知识地图/规则/断言的内容正确性。
3. **业务 Owner**：认定地图任务/能力映射的业务价值 + 试点范围。

红线：这是 Owner 权限内的决定，不得由开发/QA 代签；只在你职权范围内签字。

## 交接历史

- W0：tech_lead 规划 → 机构委员会评审 RETURN_TO_HLD
- W1：feature_pilot 执行 WP-R4-1（6 合同源变更）→ independent_qa QA_PASS
- W2：owner 决议（当前）
