# 执行包｜B-1｜出口 A｜`Customer` ⇒ `CustomerRole`

> **本包为待执行材料，不构成出口选择**：选择权在 Owner / PSO / 数据 Owner；选定后由实现者按本包逐条执行（**不得**批处理）。

## 1. 出口定义

**A 显式清单改名**：逐文件、逐处按受限配方改名，**排除**下列相邻名；**不得**批处理。

```python
pattern = r"(?<![A-Za-z0-9_])Customer(?![A-Za-z0-9_])"
```

**必须排除的相邻名（完整）**：

- `customerId`
- `gateOfCustomer`
- `ofCustomer`
- `opportunityOfCustomer`
- `profileOfCustomer`
- `refersToCustomer`

## 2. 待改文件清单（按命中数降序，前 40）

| # | 文件 | 命中 | 操作 |
|---|---|---|---|
| 1 | `docs/dd/ontology-model-detailed-design.md` | 15 | 受限改名（逐处） |
| 2 | `docs/dd/gk-ke-contract/simulation/graph/nodes.jsonl` | 12 | 受限改名（逐处） |
| 3 | `generated/openapi/gits-kno-api.normalized.json` | 12 | 随 make generate 重生成 |
| 4 | `specs/openapi/gits-kno-api.openapi.json` | 12 | 受限改名（逐处） |
| 5 | `docs/dd/mybatis-integration-spec.md` | 11 | 受限改名（逐处） |
| 6 | `adapters/persistence-relational/src/main/java/com/gien/gits/adapter/persistence/JdbcCustomerRepository.java` | 10 | 受限改名（逐处） |
| 7 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` | 10 | 受限改名（逐处） |
| 8 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md` | 9 | 受限改名（逐处） |
| 9 | `docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md` | 9 | 受限改名（逐处） |
| 10 | `specs/semantic/gits-core.owl.ttl` | 9 | 受限改名（逐处） |
| 11 | `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.owl.ttl` | 9 | 受限改名（逐处） |
| 12 | `apps/api/src/main/java/com/gien/gits/api/service/V11ScenarioDataLoader.java` | 8 | 受限改名（逐处） |
| 13 | `scripts/graph/init_product_knowledge_graph.py` | 8 | 受限改名（逐处） |
| 14 | `adapters/oracle-source/src/test/java/com/gien/gits/adapter/oracle/OracleCustomerMappingTest.java` | 7 | 受限改名（逐处） |
| 15 | `apps/api/src/main/java/com/gien/gits/api/service/CustomerContextService.java` | 7 | 受限改名（逐处） |
| 16 | `apps/api/src/main/java/com/gien/gits/api/service/ScenarioSeedDataService.java` | 7 | 受限改名（逐处） |
| 17 | `loops/GK17-ontology-unified-map/evidence/W1-INPUTS.md` | 7 | 受限改名（逐处） |
| 18 | `scripts/_gen_gk_ke_l1_1_examples.py` | 7 | 受限改名（逐处） |
| 19 | `docs/architecture/ADR-0010-customer-semantic-and-source-contract.md` | 6 | 受限改名（逐处） |
| 20 | `docs/dd/engagement-main-chain-flow-design.md` | 6 | 受限改名（逐处） |
| 21 | `frontend/src/api/engagement.ts` | 6 | 受限改名（逐处） |
| 22 | `adapters/persistence-relational/src/main/java/com/gien/gits/adapter/persistence/foundation/ontology/dto/CustomerRow.java` | 5 | 受限改名（逐处） |
| 23 | `adapters/persistence-relational/src/main/java/com/gien/gits/adapter/persistence/foundation/ontology/service/MyBatisCustomerService.java` | 5 | 受限改名（逐处） |
| 24 | `apps/api/src/main/java/com/gien/gits/api/service/PrevisitWorkflowService.java` | 5 | 受限改名（逐处） |
| 25 | `apps/api/src/test/java/com/gien/gits/api/controller/CustomerContextControllerTest.java` | 5 | 受限改名（逐处） |
| 26 | `docs/dd/访前报告生成的系统设计详解.md` | 5 | 受限改名（逐处） |
| 27 | `frontend/src/views/EngagementWorkspace.vue` | 5 | 受限改名（逐处） |
| 28 | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/CustomerRepository.java` | 5 | 受限改名（逐处） |
| 29 | `specs/data/hermes-seed-data.v0.1.json` | 5 | 受限改名（逐处） |
| 30 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.0.md` | 5 | 受限改名（逐处） |
| 31 | `apps/api/src/main/java/com/gien/gits/api/service/EngagementOrchestrator.java` | 4 | 受限改名（逐处） |
| 32 | `apps/api/src/main/java/com/gien/gits/api/service/ServiceProposalService.java` | 4 | 受限改名（逐处） |
| 33 | `apps/api/src/main/java/com/gien/gits/api/service/SupplyChainGraphService.java` | 4 | 受限改名（逐处） |
| 34 | `diagrams/FLOW.md` | 4 | 受限改名（逐处） |
| 35 | `docs/architecture/ADR-0009-customer-source-selection.md` | 4 | 受限改名（逐处） |
| 36 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` | 4 | 受限改名（逐处） |
| 37 | `docs/review/ARCH-ONTO-2026-001-rereview-package/01-主设计-V2.0-复审快照.md` | 4 | 受限改名（逐处） |
| 38 | `frontend/src/views/WorkbenchView.vue` | 4 | 受限改名（逐处） |
| 39 | `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T002338Z.log` | 4 | 受限改名（逐处） |
| 40 | `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T002736Z.log` | 4 | 受限改名（逐处） |

**全量清单**：`breakpoint-execution-pack/A/B-1-Customer-option-A-FULL.csv`（281 个文件 / 675 处命中，含逐条签字位）

（批级清单另见 `migration-worklist.csv`；本包前 40 行属**摘要**，执行须以全量 CSV 为准）

## 3. 演练证据（沙箱真跑）

- 改写处数 **187**；**脏值 0**；相邻名保持 **True**

## 4. 权限与红线

- 一旦获批执行：**仍须**逐条确认，**不得**批处理（除出口 C 外）；
- **不得**发布新 IRI（D3 未签）；**不得**手改 `specs/**`、`generated/**`；
- KERT 侧涉及项须 KERT 维护方执行。

