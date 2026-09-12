# GK14-l4-0-capability-closure｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-12T13:22:15.597172+00:00` |
| **holder** | `independent_qa` |
| **packet** | `GK14-l4-0-capability-closure` |
| **wave** | `W1` |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |

## 待核验交付物（R-1/R-2/R-3 + WP02）

| 交付物 | 路径 |
|---|---|
| R-1 能力注册闭合 | `specs/knowledge-architecture/registry/Capability.json` |
| R-2 ID 全链映射 | `specs/knowledge-architecture/registry/CapabilityIdMapping.json` |
| WP02 行业方案包 | `specs/knowledge-architecture/industry/SIM-IND-MANUFACTURING.json` |
| 修复报告 | `docs/architecture/GK-KE-GK14-R1R2R3修复报告-V1.0.md` |

## 核验重点

1. `Capability.json` 中 **9 项 IMPLEMENTED*/DESIGN_ONLY 的 `callable` 是否全部为 false**，
   是否仅 `SIM-CAP-INTERPRET` 为 `true`（防止把"有代码"误读为"可运行"）。
2. `CapabilityIdMapping.json` 的 `summary.provenCompatible` 是否为 **0**，
   且 `forbiddenAssumptions` 10 条是否完整。
3. R-3 定性：是否已按"文档与代码不一致"（非僵尸注册）登记，
   证据行号（169 / 218 / 542 / 635）是否与 KERT 实际一致。
4. WP02 的 `comparisonToExisting` 是否覆盖全部 8 维，
   且结论是否明确写出"**不得认定两者等价**"。
5. `make check` 是否 PASS；`generated/` 与 `_registry.json` 是否**未被手改**。

短提示词：你是 `independent_qa`。读本 Loop 共享记忆与上述交付物，逐项独立核验并留证；
**不得复用 TL 的自检结论**；发现问题记入 `FAILURES.md` 后再判定。
