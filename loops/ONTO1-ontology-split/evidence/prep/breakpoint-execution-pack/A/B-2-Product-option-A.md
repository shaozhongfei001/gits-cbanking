# 执行包｜B-2｜出口 A｜`Product` ⇒ `ProductOffering`

> **本包为待执行材料，不构成出口选择**：选择权在 Owner / PSO / 数据 Owner；选定后由实现者按本包逐条执行（**不得**批处理）。

## 1. 出口定义

**A 显式清单改名**：逐文件、逐处按受限配方改名，**排除**下列相邻名；**不得**批处理。

```python
pattern = r"(?<![A-Za-z0-9_])Product(?![A-Za-z0-9_])"
```

**必须排除的相邻名（完整）**：

- `ProductKnowledgeCard`
- `ProductKnowledgeVersion`
- `cardOfProduct`
- `complementsProduct`
- `opportunityForProduct`
- `requiresProduct`
- `versionOfProduct`

## 2. 待改文件清单（按命中数降序，前 40）

| # | 文件 | 命中 | 操作 |
|---|---|---|---|
| 1 | `scripts/graph/init_product_knowledge_graph.py` | 18 | 受限改名（逐处） |
| 2 | `specs/knowledge-architecture/instances/product/products.ttl` | 13 | 受限改名（逐处） |
| 3 | `specs/semantic/gits-core.owl.ttl` | 13 | 受限改名（逐处） |
| 4 | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | 13 | 受限改名（逐处） |
| 5 | `examples/bank-front-knowledge-maps/90_control/ontology/products.ttl` | 13 | 受限改名（逐处） |
| 6 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md` | 11 | 受限改名（逐处） |
| 7 | `docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md` | 11 | 受限改名（逐处） |
| 8 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` | 10 | 受限改名（逐处） |
| 9 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` | 8 | 受限改名（逐处） |
| 10 | `docs/review/ARCH-ONTO-2026-001-rereview-package/01-主设计-V2.0-复审快照.md` | 8 | 受限改名（逐处） |
| 11 | `docs/review/ARCH-ONTO-2026-001_架构委员会评审报告_V1.0.md` | 8 | 受限改名（逐处） |
| 12 | `docs/architecture/ONTOLOGY-SPLIT-REVIEW-BRIEF-V1.0.md` | 7 | 受限改名（逐处） |
| 13 | `generated/openapi/product-recommendation.normalized.json` | 7 | 随 make generate 重生成 |
| 14 | `specs/openapi/product-recommendation.openapi.json` | 7 | 受限改名（逐处） |
| 15 | `docs/dd/gk-ke-contract/simulation/graph/nodes.jsonl` | 6 | 受限改名（逐处） |
| 16 | `loops/GK17-ontology-unified-map/FAILURES.md` | 6 | 受限改名（逐处） |
| 17 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.0.md` | 6 | 受限改名（逐处） |
| 18 | `scripts/gk17_triple_consistency_check.py` | 5 | 受限改名（逐处） |
| 19 | `diagrams/ontology-model-design.html` | 4 | 受限改名（逐处） |
| 20 | `docs/V1.1_UPGRADE_AUDIT.md` | 4 | 受限改名（逐处） |
| 21 | `docs/dispatch/PI-ROUND1-需求准入与影响分析-V1.0.md` | 4 | 受限改名（逐处） |
| 22 | `docs/review/ARCH-ONTO-2026-001-rereview-package/02-整改处置报告-V2.0.md` | 3 | 受限改名（逐处） |
| 23 | `docs/review/ARCH-ONTO-2026-001_整改处置报告-V1.0.md` | 3 | 受限改名（逐处） |
| 24 | `loops/GK17-ontology-unified-map/evidence/W1-INPUTS.md` | 3 | 受限改名（逐处） |
| 25 | `loops/GK17-ontology-unified-map/memory/waves/W8-WP8.0d-PLAN.md` | 3 | 受限改名（逐处） |
| 26 | `examples/product-recommendation-assets/04_serve/projection.md` | 3 | 受限改名（逐处） |
| 27 | `diagrams/ontology-model-design.architecture.json` | 2 | 受限改名（逐处） |
| 28 | `docs/dd/gk-ke-contract/GITS-KERT_知识工程体系_项目总契约_V1.0.md` | 2 | 受限改名（逐处） |
| 29 | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md` | 2 | 受限改名（逐处） |
| 30 | `docs/review/ARCH-ONTO-2026-001-committee-package/00-送审函与阅读指南.md` | 2 | 受限改名（逐处） |
| 31 | `docs/review/ARCH-ONTO-2026-001-committee-package/05-现状问题与证据摘录.md` | 2 | 受限改名（逐处） |
| 32 | `generated/openapi/gits-kno-api.normalized.json` | 2 | 随 make generate 重生成 |
| 33 | `loops/GK17-ontology-unified-map/evidence/INDEPENDENT_QA-W2-W6-independent-qa.md` | 2 | 受限改名（逐处） |
| 34 | `loops/GK17-ontology-unified-map/memory/ORCHESTRATOR.md` | 2 | 受限改名（逐处） |
| 35 | `loops/GK17-ontology-unified-map/memory/waves/W3-ITER.md` | 2 | 受限改名（逐处） |
| 36 | `scenario/execute/src/test/java/com/gien/gits/hermes/MeetingScriptTest.java` | 2 | 受限改名（逐处） |
| 37 | `scenario/seed/07_pain_point_scenes/p0_scene_contracts.jsonl` | 2 | 受限改名（逐处） |
| 38 | `scenario_data_promopt.md` | 2 | 受限改名（逐处） |
| 39 | `scripts/_gen_gk_ke_l1_1_examples.py` | 2 | 受限改名（逐处） |
| 40 | `specs/openapi/gits-kno-api.openapi.json` | 2 | 受限改名（逐处） |

**全量清单**：`breakpoint-execution-pack/A/B-2-Product-option-A-FULL.csv`（100 个文件 / 288 处命中，含逐条签字位）

（批级清单另见 `migration-worklist.csv`；本包前 40 行属**摘要**，执行须以全量 CSV 为准）

## 3. 演练证据（沙箱真跑）

- 改写处数 **157**；**脏值 0**；相邻名保持 **True**

## 4. 权限与红线

- 一旦获批执行：**仍须**逐条确认，**不得**批处理（除出口 C 外）；
- **不得**发布新 IRI（D3 未签）；**不得**手改 `specs/**`、`generated/**`；
- KERT 侧涉及项须 KERT 维护方执行。

