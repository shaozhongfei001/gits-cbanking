# W1｜ITER 记录

## ITER 1｜WP1.1 + WP1.3 + WP1.4（2026-09-15）

### 动作

改动**双权威源**（先源后制品）：

| 文件 | 改动 |
|---|---|
| `specs/semantic/gits-core.owl.ttl`（CTR-SEM-002） | +8 类 / +14 object property |
| `specs/semantic/gits-core.linkml.yaml`（CTR-SEM-001） | +8 类（属性取自实测 record 字段） |

**新增类**（全部标注实据来源，无实据者不补）：

| 类 | 标识字段 | 实据 |
|---|---|---|
| `gits:CorporateGroup` | `group_id` | 域引用类（`LegalEntity.groupId` / `GroupRelationship.groupId` 引用） |
| `gits:LegalEntity` | `entity_id` | `modules/operational-ontology/.../ontology/LegalEntity`（record） |
| `gits:GroupRelationship` | `id` (UUID) | `.../ontology/GroupRelationship`（record） |
| `gits:Product` | `product_id` | 域引用类；物理源 = KERT 产品卡 `product_id` |
| `gits:ProductKnowledgeCard` | `product_id` | `.../ontology/ProductKnowledgeCard`（record） |
| `gits:ProductKnowledgeVersion` | `version_id` | `.../ontology/domain/ProductKnowledgeVersion`（record） |
| `gits:Task` | `task_id` | `modules/human-action/.../action/domain/Task`（record） |
| `gits:Capability` | `capability_id` | 注册表 `specs/knowledge-architecture/registry/Capability.json` |

**新增关系**：`memberOfGroup` / `relatesToGroup` / `connectsFrom` / `connectsTo` / `refersToCustomer` /
`cardOfProduct` / `versionOfProduct` / `supersedesVersion` / `inCase` / `ofCustomer` / `fromInteraction` /
`subTaskOf` / `invokesCapability`，以及 WP1.3 的三个产品关系谓词
`requiresProduct` / `mutuallyExclusiveWith` / `complementsProduct`。

### 门禁结果（全部串行执行，经 `record_gate.py` 落证）

| Gate | 结果 |
|---|---|
| `contract_generate` | **pass**（exit 0） |
| `contract_check` | **pass**（exit 0；22/23，`INTEGRITY FAILURES` 为空） |
| `gk_ke_gates` | **pass**（exit 0） |
| `ontology_load` | **pass**（exit 0；`MechanismE2eIT` = 1 test / 0 failure） |
| `security_check` | **pass**（exit 0） |
| `backend_test` | **pass**（exit 0；BUILD SUCCESS） |
| `frontend_test` | **fail**（exit 2）⇒ 见 `FAILURES.md`，根因 = **环境 safe-delete 守卫阻断 `npm ci`**，**非产品缺陷**；**未弱化门禁** |

**制品核对**：8 个新类均出现在 `generated/semantic/gits-core.shacl.ttl` 与 `generated/semantic/gits-core.schema.json`。

### 独立产物

- `docs/architecture/GK17-WP1.3-产品关系权威归属裁定-V1.0.md`
  （关系类型权威=本体 / 关系实例权威=产品卡 / 投影单向；含 V2/V3/V4 后果）

### 未完成 / 下一 ITER

1. **WP1.2 系统既有对象**：`CreditFacility`(facilityId)、`BankRelationshipSnapshot`(id)、
   `TransactionRecord`(id)、`Opportunity`、`OpportunitySignal`、`Commitment`、`KycGapProfile`、
   `HumanGate`、`PolicyRule`、`ExternalEvent`、`InteractionExtension`、`ActionReceipt`、
   `ControlledAction`、`AuditTraceEntry`、`RelationshipReport` —— **标识字段已实测，待落盘**；
2. **`Account` / `Document` 不入本 ITER**：GITS 侧**无系统类**（已确认零命中），
   权威物理源需裁定 ⇒ 记入待裁定项，**不得发明字段**；
3. `KM-` / `KD-` / `SIM-CAP-` 的前缀契约缺口 ⇒ **W5.1 范围**。

### 非声明

- ITER 1 **不声称**"本体完整"；进度以 §未完成为准；
- `frontend_test` 的 fail **保持 fail**，未因"与 W1 无关"而改写状态；
- 本 ITER 未修改任何 ADR、未接受任何 ADR。
