# GK0-contract-activation｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-11` |
| **holder** | `feature_pilot` |
| **packet** | `GK0-contract-activation` |
| **wave** | `W1（评审退回整改）` |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |
| **review_result** | `RETURN_TO_HLD`（GK-KE-AR-20260911-01） |

## 短提示词

你是 `feature_pilot`。读本 Loop 共享记忆与 TL 派工单 `docs/dd/GITS-KERT_TL_派工单_AR-R4_R5_V1.0.md`，执行 WP-R4-1 的 6 个合同源变更：

1. `MetricDefinition.full.schema.json`（C04 §2 七组字段）
2. `simulation/oracles/negative_cases.json`（C002 跨币种 + T12–T16 负例）
3. `tools/verify_simulation.py`（独立复算）
4. `SourceVersion/Capability/QueryDefinition/Release` 四 Schema
5. `ExistingRagAdapter` Schema
6. `SemanticPackage` 补 writeOwner/writeEntry

红线：走 `specs/` → `make generate` → `make check`，禁改 `generated/`，禁发明合同外字段，只记 `DEV_SELF_CHECK_PASS`。
