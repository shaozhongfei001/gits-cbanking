# GKB-baseline-hardening｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-10T16:40:00+00:00` |
| **holder** | `owner_review` |
| **packet** | `GKB-baseline-hardening` |
| **wave** | `W0`（implementation 完成，待 Owner 裁决 + 独立 QA） |
| **do_not_start** | QA_PASS（仅独立 QA 可记录）、REAL_E2E_PASS、BUSINESS_SIGNED；未经 Owner 授权不得改 `dependency-check-suppressions.xml` 或 pom spring 版本 |

## 上一波完成情况（baseline-pilot）

- 5 个 gate 全部执行完毕（EVIDENCE.json 为准）：repro_baseline 按预期复现 4 errors；fix_test_slice / apps_api_regression(450 tests) / spring_cve_decision_package / security_check 均 pass。
- 唯一代码变更：`apps/api/.../EngagementJourneyControllerTest.java` 补 `CustomerJourneyRepository`、`RelationshipReportRepository` 两个 `@MockitoBean`，可直接合入。
- spring-core 6.2.19 的 17 个 CVE 未落地任何豁免/升级，决策包在 `evidence/SPRING_CORE_CVE_DECISION.md`。

## 下一 holder 待办

1. **Owner**：在决策包 §7 签署区对方案 A（窄抑制 until 2026-12-31，编制者推荐）/ B（等企业版 6.2.20，需 Enterprise 合同）/ C（Boot4 迁移专项）书面裁决。
2. Owner 批准 A 后：由实施角色把决策包 §6 的 XML 草案（OWNER_DECISION 标识替换为正式批准标识）写入 `dependency-check-suppressions.xml`，重跑全量 verify 确认 17 项消失且无新增阻断。
3. **独立 QA**：非 implementation actor 复核测试修复与证据，记录 QA_PASS 到 `EVIDENCE.json.independent_qa`。

短提示词：你是 Owner/独立 QA。先读 `memory/handoffs/baseline-pilot.md` 与 `evidence/SPRING_CORE_CVE_DECISION.md`；测试修复可直接合入，spring CVE 必须 Owner 在 A/B/C 裁决后方可动作。
