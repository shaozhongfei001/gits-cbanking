# 执行包｜B-3｜出口 A｜`Skill` ⇒ `SkillDefinition`

> **本包为待执行材料，不构成出口选择**：选择权在 Owner / PSO / 数据 Owner；选定后由实现者按本包逐条执行（**不得**批处理）。

## 1. 出口定义

**A 显式清单改名**：逐文件、逐处按受限配方改名，**排除**下列相邻名；**不得**批处理。

```python
pattern = r"(?<![A-Za-z0-9_])Skill(?![A-Za-z0-9_])"
```

**必须排除的相邻名（完整）**：

- `referencesSkill`

## 2. 待改文件清单（按命中数降序，前 40）

| # | 文件 | 命中 | 操作 |
|---|---|---|---|
| 1 | `docs/analysis/PREVISIT_WORKFLOW_ANALYSIS_V3.2.md` | 52 | 受限改名（逐处） |
| 2 | `docs/dd/KERT_生产级混合架构独立评审报告_2026-08-26_V1.0.md` | 41 | 受限改名（逐处） |
| 3 | `docs/architecture/KERT_SPRING_AI_ALIBABA_VS_PYTHON_NATIVE_COMPARISON_V1.0.md` | 39 | 受限改名（逐处） |
| 4 | `docs/dd/KERT_independent_architecture_review_2026-08-26_V1.0.md` | 36 | 受限改名（逐处） |
| 5 | `evidence/kert-e2e-ci/evidence-runs/ci_kert-down.log` | 29 | 受限改名（逐处） |
| 6 | `evidence/kert-e2e-ci/evidence-runs/g4_kert_down_require_kert.log` | 29 | 受限改名（逐处） |
| 7 | `evidence/kert-e2e-ci/evidence-runs/g6_no_service_require_all.log` | 29 | 受限改名（逐处） |
| 8 | `specs/kert-openapi-v1.yaml` | 28 | 受限改名（逐处） |
| 9 | `scenario/seed/15_tests/acceptance_tests.jsonl` | 27 | 受限改名（逐处） |
| 10 | `evidence/kert-e2e-ci/evidence-runs/g1_no_service-ledger.json` | 26 | 受限改名（逐处） |
| 11 | `evidence/kert-e2e-ci/evidence-runs/g1_no_service.log` | 26 | 受限改名（逐处） |
| 12 | `evidence/kert-e2e-ci/evidence-runs/g1b_no_service-ledger.json` | 26 | 受限改名（逐处） |
| 13 | `evidence/kert-e2e-ci/evidence-runs/g1b_no_service.log` | 26 | 受限改名（逐处） |
| 14 | `evidence/m7-3/e2e-stack-up-05-pytest-fail-no-apikey.log` | 26 | 受限改名（逐处） |
| 15 | `docs/architecture/KERT_SPRING_AI_ALIBABA_SKILL_RUNTIME_POC_V1.0.md` | 21 | 受限改名（逐处） |
| 16 | `docs/production-evolution-plan.md` | 17 | 受限改名（逐处） |
| 17 | `docs/architecture/KERT_OPEN_SOURCE_TECH_STACK_V1.0.md` | 15 | 受限改名（逐处） |
| 18 | `docs/handover-review-2026-08-26.md` | 14 | 受限改名（逐处） |
| 19 | `src/kert/application/skills.py` | 14 | 受限改名（逐处） |
| 20 | `examples/gits_adapter/python/kert_client.py` | 13 | 受限改名（逐处） |
| 21 | `docs/V1.1_IMPLEMENTATION_PLAN.md` | 11 | 受限改名（逐处） |
| 22 | `docs/architecture/KERT_ADAPTER_FIRST_TECH_STACK_V1.1.md` | 11 | 受限改名（逐处） |
| 23 | `docs/architecture/KERT_INDEPENDENT_SERVER_BOUNDARY_V1.0.md` | 11 | 受限改名（逐处） |
| 24 | `docs/governance/KERT_GATE0_EVIDENCE_PACK_CANDIDATE.md` | 11 | 受限改名（逐处） |
| 25 | `evidence/m2-p6/nfr_baseline.md` | 11 | 受限改名（逐处） |
| 26 | `scripts/nfr_benchmark.py` | 11 | 受限改名（逐处） |
| 27 | `README.md` | 10 | 受限改名（逐处） |
| 28 | `docs/architecture/KERT_HYBRID_DEPLOYMENT_AND_OPERATIONS_V1.0_CANDIDATE.md` | 10 | 受限改名（逐处） |
| 29 | `src/kert/api/server.py` | 10 | 受限改名（逐处） |
| 30 | `docs/dd/GITS_Bank_信号与互动_互动记录访前路径_UX改造方案_V1.0_20260829.md` | 9 | 受限改名（逐处） |
| 31 | `evidence/m2-p6/nfr_baseline_report.md` | 9 | 受限改名（逐处） |
| 32 | `apps/api/src/test/java/com/gien/gits/api/e2e/EngagementScenarioE2eIT.java` | 8 | 受限改名（逐处） |
| 33 | `docs/adr/ADR-PR-CANDIDATES.md` | 8 | 受限改名（逐处） |
| 34 | `docs/dd/gk-ke-contract/GITS-KERT_知识工程体系_项目总契约_V1.0.md` | 8 | 受限改名（逐处） |
| 35 | `scenario/seed/07_pain_point_scenes/extension/PP-G02_客户经理经常修改AI内容，但修改没有持续反哺Skill评测和版本.md` | 8 | 受限改名（逐处） |
| 36 | `docs/skill-execute-api-contract.md` | 8 | 受限改名（逐处） |
| 37 | `examples/gits_adapter/README.md` | 8 | 受限改名（逐处） |
| 38 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` | 7 | 受限改名（逐处） |
| 39 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md` | 7 | 受限改名（逐处） |
| 40 | `docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md` | 7 | 受限改名（逐处） |

**全量清单**：`breakpoint-execution-pack/A/B-3-Skill-option-A-FULL.csv`（355 个文件 / 1398 处命中，含逐条签字位）

（批级清单另见 `migration-worklist.csv`；本包前 40 行属**摘要**，执行须以全量 CSV 为准）

## 3. 演练证据（沙箱真跑）

- 改写处数 **93**；**脏值 0**；相邻名保持 **True**

## 4. 权限与红线

- 一旦获批执行：**仍须**逐条确认，**不得**批处理（除出口 C 外）；
- **不得**发布新 IRI（D3 未签）；**不得**手改 `specs/**`、`generated/**`；
- KERT 侧涉及项须 KERT 维护方执行。

