# SIM 迁移演练｜断点清单（由 `sim-rehearsal-report.json` 派生）

> 边界：`https://rehearsal.sim.local/ns-l1#` 为**演练专用占位**，永不发布；仓内制品零改动。

## 1. 分类总览

- 迁移行 **67**：SAME_NAME 51 · RENAME 7 · NON_IRI_TARGET 8 · RETIRE 1
- 改名类消费者命中 **7049** 处；**盲替换会误伤** 4933 处

## 2. 必须人工逐条的断点（盲替换风险）

| 旧名 | 新名 | 本名命中 | 会被误伤的同形/包含命中 | 风险样例 |
|---|---|---|---|---|
| `Customer` | `CustomerRole` | 779 | 3872 | `customerId`, `gateOfCustomer`, `ofCustomer` |
| `Product` | `ProductOffering` | 332 | 598 | `ProductKnowledgeCard`, `ProductKnowledgeVersion`, `cardOfProduct` |
| `Skill` | `SkillDefinition` | 1467 | 21 | `referencesSkill` |
| `Asset` | `AssetDefinition` | 184 | 442 | `ASSET`, `referencesAsset` |

## 3. 迁移配方（四通道）

- **same_name**：仅做 IRI 级替换（旧命名空间→新命名空间），术语名不变 ⇒ 可机械化
- **rename**：**必须**逐条走显式迁移清单：词边界替换 + 前后不得邻接标识符字符；有盲替换风险的条目**不得**批处理
- **retire**：**不得**改名：须 deprecated + dcterms:isReplacedBy，且保留只读期
- **non_iri_target**：REGISTRY/SCHEMA-FIELD/SKOS 通道：非 OWL 术语，按各自登记机制处理

## 4. 沙箱演练结果

- 处理文件 13（真改写 12 · `generated/` 派生跳过 1）
- 演练后 TTL 全部可解析：**True**
- 退役项一处未换：**True**

## 5. 逐文件迁移计划（前 10，按命中数）

| 文件 | 命中 | IRI 级替换 | 受限改名 | 退役未换 | 备注 |
|---|---|---|---|---|---|
| `loops/ONTO1-ontology-split/evidence/consumer-scan-obligations.csv` | 1008 | 0 | 42 | 1 | REHEARSED |
| `loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv` | 591 | 0 | 33 | 1 | REHEARSED |
| `apps/api/src/main/java/com/gien/gits/api/service/ScenarioSeedDataService.java` | 196 | 0 | 5 | 1 | REHEARSED |
| `specs/semantic/gits-core.owl.ttl` | 195 | 1 | 17 | 1 | REHEARSED |
| `docs/dd/engagement-main-chain-flow-design.md` | 182 | 0 | 4 | 1 | REHEARSED |
| `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md` | 175 | 0 | 14 | 1 | REHEARSED |
| `docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md` | 175 | 0 | 14 | 1 | REHEARSED |
| `generated/openapi/gits-kno-api.normalized.json` | 174 | 0 | 0 | 0 | GENERATED_DERIVED |
| `specs/openapi/gits-kno-api.openapi.json` | 174 | 0 | 0 | 1 | REHEARSED |
| `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` | 166 | 0 | 16 | 1 | REHEARSED |

> **给 Wave 2/3 的硬性要求**：断点表（§2）内条目**不得**批处理；`generated/**` 一律随 `make generate` 重新生成；退役项走 `deprecated` + `dcterms:isReplacedBy`。
