# 执行包｜B-4｜出口 A｜`Asset` ⇒ `AssetDefinition`

> **本包为待执行材料，不构成出口选择**：选择权在 Owner / PSO / 数据 Owner；选定后由实现者按本包逐条执行（**不得**批处理）。

## 1. 出口定义

**A 显式清单改名**：逐文件、逐处按受限配方改名，**排除**下列相邻名；**不得**批处理。

```python
pattern = r"(?<![A-Za-z0-9_])Asset(?![A-Za-z0-9_])"
```

**必须排除的相邻名（完整）**：

- `ASSET`
- `referencesAsset`

## 2. 待改文件清单（按命中数降序，前 40）

| # | 文件 | 命中 | 操作 |
|---|---|---|---|
| 1 | `specs/knowledge-architecture/activation/map_spec.json` | 9 | 受限改名（逐处） |
| 2 | `docs/dd/gk-ke-contract/GITS-KERT_知识工程体系_项目总契约_V1.0.md` | 8 | 受限改名（逐处） |
| 3 | `docs/dd/gk-ke-contract/contracts/C02_注册中心与知识地图合同.md` | 7 | 受限改名（逐处） |
| 4 | `scripts/gk_ke_l2_2_registry_tests.py` | 7 | 受限改名（逐处） |
| 5 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md` | 5 | 受限改名（逐处） |
| 6 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` | 5 | 受限改名（逐处） |
| 7 | `docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md` | 5 | 受限改名（逐处） |
| 8 | `docs/review/ARCH-ONTO-2026-001-rereview-package/01-主设计-V2.0-复审快照.md` | 5 | 受限改名（逐处） |
| 9 | `scripts/_gen_gk_ke_l2_2_registry.py` | 5 | 受限改名（逐处） |
| 10 | `specs/knowledge-architecture/registry/MapVersion.json` | 5 | 受限改名（逐处） |
| 11 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` | 4 | 受限改名（逐处） |
| 12 | `docs/architecture/ONTOLOGY-SPLIT-REVIEW-BRIEF-V1.0.md` | 3 | 受限改名（逐处） |
| 13 | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java` | 3 | 受限改名（逐处） |
| 14 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.0.md` | 3 | 受限改名（逐处） |
| 15 | `docs/dd/gk-ke-contract/examples/negative/KnowledgeMap_1.json` | 2 | 受限改名（逐处） |
| 16 | `docs/dd/gk-ke-contract/examples/negative/KnowledgeMap_2.json` | 2 | 受限改名（逐处） |
| 17 | `docs/dd/gk-ke-contract/examples/positive/KnowledgeMap.json` | 2 | 受限改名（逐处） |
| 18 | `docs/dd/gk-ke-contract/tools/build_contract_examples.py` | 2 | 受限改名（逐处） |
| 19 | `docs/dd/gk-ke-contract/tools/validate_package.py` | 2 | 受限改名（逐处） |
| 20 | `docs/dd/必须理解的业务主链_任务骨架.md` | 2 | 受限改名（逐处） |
| 21 | `docs/dispatch/GK-KE-OC030405-人工审阅包-V1.0.md` | 2 | 受限改名（逐处） |
| 22 | `docs/review/ARCH-ONTO-2026-001_架构委员会评审报告_V1.0.md` | 2 | 受限改名（逐处） |
| 23 | `loops/GK17-ontology-unified-map/memory/ORCHESTRATOR.md` | 2 | 受限改名（逐处） |
| 24 | `loops/GK17-ontology-unified-map/memory/waves/W5-ITER.md` | 2 | 受限改名（逐处） |
| 25 | `loops/P20-wiki-ontology-fusion/REVIEW_PENDING.md` | 2 | 受限改名（逐处） |
| 26 | `scripts/_gen_gk_ke_l5_1_kuzu.py` | 2 | 受限改名（逐处） |
| 27 | `scripts/run_p20_shadow_e2e.py` | 2 | 受限改名（逐处） |
| 28 | `scripts/run_p22_shadow_e2e.py` | 2 | 受限改名（逐处） |
| 29 | `specs/gk-ke/v1/definitions/SIM-MAP-FINANCE.json` | 2 | 受限改名（逐处） |
| 30 | `specs/gk-ke/v1/examples/negative/KnowledgeMap_1.json` | 2 | 受限改名（逐处） |
| 31 | `specs/gk-ke/v1/examples/negative/KnowledgeMap_2.json` | 2 | 受限改名（逐处） |
| 32 | `specs/gk-ke/v1/examples/positive/KnowledgeMap.json` | 2 | 受限改名（逐处） |
| 33 | `specs/knowledge-architecture/graph/graph_manifest.json` | 2 | 受限改名（逐处） |
| 34 | `specs/semantic/gits-core.owl.ttl` | 2 | 受限改名（逐处） |
| 35 | `docs/adr/ADR-018-public-ontology-independence-and-governance.md` | 2 | 受限改名（逐处） |
| 36 | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | 2 | 受限改名（逐处） |
| 37 | `docs/architecture/GK-KE-L0-2-OC01收口-V1.0.md` | 1 | 受限改名（逐处） |
| 38 | `docs/architecture/GK-KE-L0-2-兼容与生成策略-V1.0.md` | 1 | 受限改名（逐处） |
| 39 | `docs/architecture/GK-KE-统一地图承担者论证-V1.0.md` | 1 | 受限改名（逐处） |
| 40 | `docs/architecture/OPENWIKI_PROJECTION_ASSESSMENT.md` | 1 | 受限改名（逐处） |

**全量清单**：`breakpoint-execution-pack/A/B-4-Asset-option-A-FULL.csv`（66 个文件 / 148 处命中，含逐条签字位）

（批级清单另见 `migration-worklist.csv`；本包前 40 行属**摘要**，执行须以全量 CSV 为准）

## 3. 演练证据（沙箱真跑）

- 改写处数 **112**；**脏值 0**；相邻名保持 **True**

## 4. 权限与红线

- 一旦获批执行：**仍须**逐条确认，**不得**批处理（除出口 C 外）；
- **不得**发布新 IRI（D3 未签）；**不得**手改 `specs/**`、`generated/**`；
- KERT 侧涉及项须 KERT 维护方执行。

