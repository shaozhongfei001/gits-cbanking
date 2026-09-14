# W1 输入｜本体类清单 + ID 空间锚定清单

> 来源：两个**只读**侦察代理（`code-explorer`），2026-09-15；**未写盘**，由 TL 落盘。
> 用途：W1（扩本体）、W5.1（引用锚定门禁）的输入。
> **纪律**：以下均为**有实据**项；无实据者已标注，不得据以发明本体内容。

---

## A. 候选本体类（只列有 Java/注册表实据者）

### A.1 现有本体已覆盖（9 类）

`OperatingCase` / `Interaction` / `Claim` / `Evidence` / `HumanConfirmation` / `Action` / `Receipt` / `Evaluation` / `Customer`

### A.2 有系统实据、本体**未覆盖**（按设计 8 类归类）

| 建议 gits: 名 | 系统来源 | 标识字段（实测名） | 关键属性 | 候选关系 |
|---|---|---|---|---|
| `gits:LegalEntity` | `com.gien.gits.ontology.LegalEntity` | `entityId` | groupId, name, role, ownership, bankCustomerId, relationshipStatus, evidenceRef | memberOfGroup→Group；refersToCustomer→Customer |
| `gits:GroupRelationship` | `...ontology.GroupRelationship` | `id` | groupId, fromEntityId, toEntityId, relationshipType, ownershipRatio | connectsFrom→LegalEntity；connectsTo→LegalEntity |
| `gits:CreditFacility` | `...ontology.CreditFacility` | `facilityId` | customerId, borrowerEntity, approvalDate, maturityDate, creditTotalCny, usedCreditCny, availableCreditCny | grantedTo→Customer |
| `gits:BankRelationshipSnapshot` | `...ontology.BankRelationshipSnapshot` | `id` | customerId, snapshotMonth, avgDailyDepositCny, loanBalanceCny, creditTotalCny, productCount | snapshotOf→Customer |
| `gits:TransactionRecord` | `...ontology.TransactionRecord` | `id` | customerId, transactionDate, transactionType, counterparty, amountCny, evidenceRef | belongsToCustomer→Customer |
| `gits:ProductKnowledgeCard` | `...ontology.ProductKnowledgeCard` | `productId` | name, definition, keyConditions, requiredMaterials, riskPoints, trigger | cardOfProduct→Product（类未定） |
| `gits:ProductKnowledgeVersion` | `...ontology.domain.ProductKnowledgeVersion` | `versionId`（业务键 productId+versionNumber） | productId, versionNumber, productName, category, riskLevel, pricingBasis, previousVersionId | versionOf→Product（类未定） |
| `gits:Task` | `com.gien.gits.action.domain.Task`（**在 modules/human-action**） | `taskId` | interactionId, customerId, operatingCaseId, taskType, title, status, priority, assignedTo, parentTaskId | inCase→OperatingCase；ofCustomer→Customer；fromInteraction→Interaction；subTaskOf→Task |
| `gits:EvidenceVersionLink` | `...ontology.domain.EvidenceVersionLink` | `linkId` | evidenceId, previousVersionId, nextVersionId, versionNumber, changeType, changedBy | linksEvidence→Evidence |
| `gits:Capability` | **无 Java 类**；注册表 `specs/knowledge-architecture/registry/Capability.json` | `capabilityId` | version, inputSchemaRef, outputSchemaRef, executorRef, sideEffect, probeStatus, callable | invokedByTask→Task |
| `gits:Opportunity` / `gits:OpportunitySignal` / `gits:Commitment` / `gits:KycGapProfile` / `gits:HumanGate` / `gits:PolicyRule` / `gits:FactReconciliationCase` / `gits:ExternalEvent` / `gits:InteractionExtension` / `gits:ActionReceipt` / `gits:ControlledAction` / `gits:AuditTraceEntry` / `gits:RelationshipReport` / `gits:CustomerTier` / `gits:EnterpriseScale` / `gits:RiskLevel` / `gits:Industry` / `gits:ListedStatus` / `gits:Channel` / `gits:CaseType` / `gits:CaseStatus` / `gits:ClaimType` / `gits:ClaimStatus` / `gits:GateType` / `gits:HumanGateStatus` / `gits:ReconciliationStatus` / `gits:DomainEventType` | 均在 `modules/operational-ontology/src/main/java/`（100 文件） | 逐类见源码 record 组件名 | — | — |

### A.3 设计点名但**GITS 侧无系统类**（须按"域引用类"模式处理，同 `Customer`→`EDWCRM.A_ZHCX_CUST_BASE` 的先例）

| 设计对象 | 状态 | 处理建议 |
|---|---|---|
| **账户** `gits:Account` | 仅 `Transaction.accountId` 间接出现 | 作为**域引用类**声明身份；**不得**凭空造字段 |
| **产品** `gits:Product` | 系统只有 `ProductKnowledgeCard` / `ProductKnowledgeVersion` | 同上；产品身份可锚定 `productId`（KERT 产品卡） |
| **文档** `gits:Document` | 无 Document record；`Evidence.sourceUri` 间接承担 | 同上；或显式裁定"文档身份由 Evidence.sourceUri 承担" |
| **能力** `gits:Capability` | 无 Java 类，有注册表 | 以注册表为权威源，标识字段 `capabilityId` |

### A.4 关系缺口（现有 9 类未表达，但系统显然需要）

`memberOfGroup` / `customerOfGroup` / `holdsAccount` / `hasCreditFacility` / `snapshotOf` / `versionOfProduct` / `inCase` / `ofCustomer` / `fromInteraction` / `subTaskOf` / `invokedByTask`

---

## B. ID 空间锚定清单（W5.1 输入）

| 前缀 | 含义 | 权威定义源 | 标识字段 | 现有注册/校验 | 缺口 |
|---|---|---|---|---|---|
| `ASSET-` | 知识资产 | `schemas/asset-manifest.schema.json` + `assets/**/*.md` front matter | `assetId` | `scripts/validate_knowledge_architecture.py`（强制 21 项） | — |
| `SP-` | 治理化 Skill | `schemas/skill-descriptor.schema.json` + `skills/*.json` | `skillId` | 校验器强制 `{SP-02,05,07,10,15}` | — |
| `AC-` | 激活合同 | `schemas/activation-contract.schema.json` + `activations/*.json` | `contractId` | 校验器强制 3 项 | — |
| `RP-` | 路由策略 | `schemas/route-policy.schema.json` + `routes/RP-CORP-RM-001.json` | `policyId` | 校验器强制恰好 1 项 | — |
| `KM-` | 知识地图 | `schemas/knowledge-map.schema.json` + `maps/**/*.md` | `mapId` | **无独立 registry；校验器不核对地图间引用** | ⚠️ **W5.1 主目标** |
| `KD-` | 知识域 | **无前缀契约**（`domains[].domainId` 仅 string） | `domainId` | **无注册、无校验** | ⚠️ 缺口 |
| `KI-` | 知识条目 | `schemas/knowledge-element.schema.json` + `elements/knowledge-items-index.json` | `knowledgeItemId` | 索引 7 条 | — |
| `KE-` | 知识要素 | `knowledge-element.schema.json`（pattern `^KE-[A-Z0-9-]+-\d{2}$`） | `elementId` | 实例即源，无汇总 registry | — |
| `SIM-CAP-` | 模拟能力 | **GK-KE 侧无前缀契约**；`registry/Capability.json`（12 项） | `capabilityId` | `specs/gk-ke/v1/schemas/Capability.schema.json` 仅 `minLength:1` | ⚠️ 缺口 |

**B.1 地图实际引用的 ID**（`maps/**` 的 `assetRefs`/`skillRefs`/`activationContractRefs`/`entrypoints.tasks`/`routePolicyRef`）
—— 去重后逐条"能否在权威源找到定义"的完整清单，**侦察代理输出被截断，须在 W5.1 重跑并落盘为证据**。
已知抽样：`ASSET-DATA-*`（5）、`ASSET-KNOW-*`（5）、`SP-02/05/10/15`、`AC-PREVISIT-001`、`RP-CORP-RM-001`、任务 `PRE_VISIT_PREPARATION` 等。

**B.2 既有可复用组件**：`scripts/validate_knowledge_architecture.py`（assets/skills/activations/route-policy 索引与强制集合）
⇒ **W5.1 应复用它、而非另起一套**（避免"两份可独立修改的定义"，违反约束①）。

---

## C. 本文件的性质

- 侦察为**只读**，未修改任何文件；
- 本清单为 **W1/W5 的输入草案**，**不是合同**、**不构成 Owner 决议**；
- 标注「无对应系统类」「缺口」处**不得据以发明字段**，须走 W1.3 裁定（关系类型权威=本体 / 关系实例权威=产品卡）。
