# GK0-contract-activation｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-11` |
| **holder** | `independent_qa` |
| **packet** | `GK0-contract-activation` |
| **wave** | `W1（评审退回整改·已完成）` |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |
| **review_result** | `RETURN_TO_HLD`（GK-KE-AR-20260911-01） |

## 短提示词

你是 `independent_qa`。WP-R4-1 的 6 个合同源变更已由 feature_pilot 完成并记录 `DEV_SELF_CHECK_PASS`，现进行独立 QA 复核。

**已交付（feature_pilot 完成）**：
1. `MetricDefinition.full.schema.json`（C04 §2 七组字段，CTR-GKKE-015）
2. `simulation/oracles/negative_cases.json`（T15/T14/T14b/T12/T13/T02 负例）
3. `tools/verify_simulation.py`（独立复算，C001=2983333.33 已 PASS）
4. `SourceVersion/Capability/QueryDefinition/Release` 四 Schema（CTR-GKKE-016~019）
5. `LegacyRagHit.schema.json`（C05 §3，CTR-GKKE-020）
6. `SemanticPackage` 补 writeOwner/writeEntry/authorityScope（仅新增可选字段，向后兼容）

**验证结果**：`make generate` PASS；`make check` PASS（正例 20/20，负例 40）；`verify_simulation.py` PASS。

**QA 重点**：
- 变更 1/4/5 是否逐字段对齐 C02/C04/C05 合同正文，未发明合同外字段。
- 变更 6 是否保持向后兼容（仅新增可选字段，required 未变）。
- 负例是否隔离（未污染 simulation/tables/）。
- 登记 CTR-GKKE-015~020 是否与 authority_source/generated 路径一致。

**禁止**：dev 角色已记 DEV_SELF_CHECK_PASS，只有你（独立 QA）可记录 QA_PASS。

完成 QA 后：更新 STATE.json（qa_actor/独立 QA 证据）+ EVIDENCE.json.independent_qa + 本文件（Baton → tech_lead 待 Owner 决议）。
