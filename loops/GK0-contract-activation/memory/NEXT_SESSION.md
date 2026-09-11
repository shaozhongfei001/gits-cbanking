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

你是 `feature_pilot`。读本 Loop 共享记忆与精确派工单 `docs/dd/GITS-KERT_派工单_WP-R4-1_FeaturePilot_V1.0.md`，执行 WP-R4-1 的 6 个合同源变更。

**权威落点（必读）**：改 `specs/gk-ke/v1/schemas/` + `specs/CONTRACT_INDEX.yaml`，禁止手改 `generated/`。

6 个任务：
1. `MetricDefinition.full.schema.json`（C04 §2 七组字段，登记 CTR-GKKE-015）
2. `negative_cases.json`（C002 跨币种 + T12–T16 负例）
3. `tools/verify_simulation.py`（独立复算，期望 C001=2983333.33）
4. `SourceVersion/Capability/QueryDefinition/Release` 四 Schema（登记 CTR-GKKE-016~019）
5. `LegacyRagHit.schema.json`（C05 §3 七字段，登记 CTR-GKKE-020）
6. `SemanticPackage` 补 writeOwner/writeEntry（仅新增可选字段，向后兼容）

红线：走 `specs/` → `make generate` → `make check`，禁改 `generated/`，禁发明合同外字段，只记 `DEV_SELF_CHECK_PASS`，禁自签 QA_PASS。

完成后：更新 STATE.json（6 任务 done）+ EVIDENCE.json + 本文件（Baton → 独立 QA）。TL 已备好独立 QA 复核提示词 `docs/dd/GITS-KERT_独立QA复核提示词_V1.0.md`，你完成后由 TL 发起 QA 会话。
