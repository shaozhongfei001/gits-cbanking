# 32 类 × 目标层 × 45 制品口径 · 逐类核清（复核材料）

> **来源盘点 ≠ L1 候选**：`l1-term-inventory.json` 记录的是**现有本体 32 个 OWL 类**（基线全量，覆盖 L1/L2/L3 三层，见下表 target_layer），**不是** L1 候选模型；真正的 **L1 候选模型 = 8 类**（下表 `l1_candidate_model`），与设计 §4.2 逐项一致。

## 1. 计数单位（防混算）

| 数 | 口径 |
|---|---|
| **32** | 基线 OWL 类数（来源盘点口径） |
| **45** | 目标制品数 = 39 OWL 类 + 1 SKOS 概念体系 + 5 集成契约 Schema 对象（**不是 45 个本体类**） |
| **87** | attribution-45-v2.csv 数据行数（另含 36 对象属性 + 5 L4 Schema 字段 + 1 退役） |

**设计偏差声明**：无（未把 32 类放入 L1；本次为**登记口径分离**，非设计变更）

## 2. 基线 32 类逐项（现有 IRI / 目标层 / 权威责任 / 理由 / 对应 45 映射项）

| # | 基线类 | 现有 IRI | 目标术语 | 目标口径 | 目标层 | 去向 | 理由 | T-Box Owner | 对应 45 项 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `OperatingCase` | `https://gientech.com/gits/kno/OperatingCase` | `OperatingCase` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | OperatingCase / OWL 类 / 目标口径=OWL类 |
| 2 | `Claim` | `https://gientech.com/gits/kno/Claim` | `Claim` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Claim / OWL 类 / 目标口径=OWL类 |
| 3 | `Evidence` | `https://gientech.com/gits/kno/Evidence` | `Evidence` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Evidence / OWL 类 / 目标口径=OWL类 |
| 4 | `Evaluation` | `https://gientech.com/gits/kno/Evaluation` | `Evaluation` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Evaluation / OWL 类 / 目标口径=OWL类 |
| 5 | `Action` | `https://gientech.com/gits/kno/Action` | `Action` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Action / OWL 类 / 目标口径=OWL类 |
| 6 | `Receipt` | `https://gientech.com/gits/kno/Receipt` | `Receipt` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Receipt / OWL 类 / 目标口径=OWL类 |
| 7 | `HumanConfirmation` | `https://gientech.com/gits/kno/HumanConfirmation` | `HumanConfirmation` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | HumanConfirmation / OWL 类 / 目标口径=OWL类 |
| 8 | `HumanGate` | `https://gientech.com/gits/kno/HumanGate` | `HumanGate` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | HumanGate / OWL 类 / 目标口径=OWL类 |
| 9 | `Interaction` | `https://gientech.com/gits/kno/Interaction` | `Interaction` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Interaction / OWL 类 / 目标口径=OWL类 |
| 10 | `InteractionExtension` | `https://gientech.com/gits/kno/InteractionExtension` | `InteractionExtension` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | InteractionExtension / OWL 类 / 目标口径=OWL类 |
| 11 | `Opportunity` | `https://gientech.com/gits/kno/Opportunity` | `Opportunity` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Opportunity / OWL 类 / 目标口径=OWL类 |
| 12 | `OpportunitySignal` | `https://gientech.com/gits/kno/OpportunitySignal` | `OpportunitySignal` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | OpportunitySignal / OWL 类 / 目标口径=OWL类 |
| 13 | `Commitment` | `https://gientech.com/gits/kno/Commitment` | `Commitment` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Commitment / OWL 类 / 目标口径=OWL类 |
| 14 | `ExternalEvent` | `https://gientech.com/gits/kno/ExternalEvent` | `ExternalEvent` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | ExternalEvent / OWL 类 / 目标口径=OWL类 |
| 15 | `KycGapProfile` | `https://gientech.com/gits/kno/KycGapProfile` | `KycGapProfile` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | KycGapProfile / OWL 类 / 目标口径=OWL类 |
| 16 | `PolicyRule` | `https://gientech.com/gits/kno/PolicyRule` | `PolicyRule` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | PolicyRule / OWL 类 / 目标口径=OWL类 |
| 17 | `AuditTraceEntry` | `https://gientech.com/gits/kno/AuditTraceEntry` | `AuditTraceEntry` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | AuditTraceEntry / OWL 类 / 目标口径=OWL类 |
| 18 | `RelationshipReport` | `https://gientech.com/gits/kno/RelationshipReport` | `RelationshipReport` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | RelationshipReport / OWL 类 / 目标口径=OWL类 |
| 19 | `Task` | `https://gientech.com/gits/kno/Task` | `Task` | OWL 类 | L3 GITS | 保留原名 | 结构不变，仅归属声明变化 | GITS Owner | Task / OWL 类 / 目标口径=OWL类 |
| 20 | `LegalEntity` | `https://gientech.com/gits/kno/LegalEntity` | `LegalEntity` | OWL 类 | L1 公共 | 迁移（原名） | 迁移（原名） | 公共语义Owner | LegalEntity / OWL 类 / 目标口径=OWL类 |
| 21 | `Customer` | `https://gientech.com/gits/kno/Customer` | `CustomerRole` | OWL 类 | L1 公共 | 迁移重构 | 语义收窄/职责重划（详见设计 §4.2~§4.5） | 公共语义Owner | CustomerRole / OWL 类 / 目标口径=OWL类 |
| 22 | `CorporateGroup` | `https://gientech.com/gits/kno/CorporateGroup` | `EnterpriseGroup` | OWL 类 | L1 公共 | 迁移改名 | 迁移改名 | 公共语义Owner | EnterpriseGroup / OWL 类 / 目标口径=OWL类 |
| 23 | `GroupRelationship` | `https://gientech.com/gits/kno/GroupRelationship` | `GroupMembership` | OWL 类 | L1 公共 | 迁移重构 | 语义收窄/职责重划（详见设计 §4.2~§4.5） | 公共语义Owner | GroupMembership / OWL 类 / 目标口径=OWL类 |
| 24 | `Product` | `https://gientech.com/gits/kno/Product` | `ProductOffering` | OWL 类 | L1 公共 | 迁移重构 | 语义收窄/职责重划（详见设计 §4.2~§4.5） | 公共语义Owner | ProductOffering / OWL 类 / 目标口径=OWL类 |
| 25 | `ProductKnowledgeCard` | `https://gientech.com/gits/kno/ProductKnowledgeCard` | `ProductKnowledgeCard` | OWL 类 | L2 KERT | 迁移（原名） | 迁移（原名） | Knowledge Owner/KERT Owner | ProductKnowledgeCard / OWL 类 / 目标口径=OWL类 |
| 26 | `ProductKnowledgeVersion` | `https://gientech.com/gits/kno/ProductKnowledgeVersion` | `ProductKnowledgeVersion` | OWL 类 | L2 KERT | 迁移（原名） | 迁移（原名） | Knowledge Owner/KERT Owner | ProductKnowledgeVersion / OWL 类 / 目标口径=OWL类 |
| 27 | `KnowledgeMap` | `https://gientech.com/gits/kno/KnowledgeMap` | `KnowledgeMapDefinition` | OWL 类 | L2 KERT | 迁移改名 | 迁移改名 | Knowledge Owner/KERT Owner | KnowledgeMapDefinition / OWL 类 / 目标口径=OWL类 |
| 28 | `Asset` | `https://gientech.com/gits/kno/Asset` | `AssetDefinition` | OWL 类 | L2 KERT | 迁移改名 | 迁移改名 | Knowledge Owner/KERT Owner | AssetDefinition / OWL 类 / 目标口径=OWL类 |
| 29 | `Skill` | `https://gientech.com/gits/kno/Skill` | `SkillDefinition` | OWL 类 | L2 KERT | 迁移改名 | 迁移改名 | Knowledge Owner/KERT Owner | SkillDefinition / OWL 类 / 目标口径=OWL类 |
| 30 | `ActivationContract` | `https://gientech.com/gits/kno/ActivationContract` | `ActivationContract` | **JSON Schema 对象** | L4 注册表 | **转换制品类型** | **转换制品类型** | Integration Contract Owner | ActivationContract / **JSON Schema 对象** / 目标口径=集成契约Schema对象 |
| 31 | `Capability` | `https://gientech.com/gits/kno/Capability` | `CapabilityPublication` | **JSON Schema 对象** | L4 注册表 | **转换制品类型+重构** | **转换制品类型+重构** | Integration Contract Owner | CapabilityPublication / **JSON Schema 对象** / 目标口径=集成契约Schema对象 |
| 32 | `TaskType` | `https://gientech.com/gits/kno/TaskType` | `TaskTypeScheme` | **SKOS 概念体系** | L4 词表 | **转换制品类型** | **转换制品类型** | 词表Owner | TaskTypeScheme / **SKOS 概念体系** / 目标口径=SKOS概念体系 |

## 3. L1 候选模型（**8 类**，与设计 §4.2 逐项一致）

| L1 类 | 设计来源 | 基线前身 | 映射类型 | T-Box Owner | IRI（候选中） |
|---|---|---|---|---|---|
| `Party` | 新增（委员会 §3.6） | （新增） | 新增 | 公共语义Owner | `PENDING:{NS-L1}#Party` |
| `Organization` | 新增（委员会 §3.6） | （新增） | 新增 | 公共语义Owner | `PENDING:{NS-L1}#Organization` |
| `LegalEntity` | 基线 LegalEntity | LegalEntity | 基线映射 | 公共语义Owner | `PENDING:{NS-L1}#LegalEntity` |
| `CustomerRole` | 基线 Customer 重构 | Customer | 基线映射 | 公共语义Owner | `PENDING:{NS-L1}#CustomerRole` |
| `EnterpriseGroup` | 基线 CorporateGroup 改名 | CorporateGroup | 基线映射 | 公共语义Owner | `PENDING:{NS-L1}#EnterpriseGroup` |
| `GroupMembership` | 基线 GroupRelationship 重构 | GroupRelationship | 基线映射 | 公共语义Owner | `PENDING:{NS-L1}#GroupMembership` |
| `ProductOffering` | 基线 Product 改名重构 | Product | 基线映射 | 公共语义Owner | `PENDING:{NS-L1}#ProductOffering` |
| `SourceIdentifier` | 新增（委员会 §3.6） | （新增） | 新增 | 公共语义Owner | `PENDING:{NS-L1}#SourceIdentifier` |

## 4. 统计

- 解析到基线类：**32**；按目标层：{'L3 GITS': 19, 'L1 公共': 5, 'L2 KERT': 5, 'L4 注册表': 2, 'L4 词表': 1}
- 按去向：{'保留原名': 19, '迁移（原名）': 3, '迁移重构': 3, '迁移改名': 4, '**转换制品类型**': 2, '**转换制品类型+重构**': 1}
- **L1 候选 = 8 类**（基线映射 5 + 新增 3）
- 来源盘点件标注 `artifact_role` = SOURCE_INVENTORY（现有本体 32 类的**来源盘点**；**不是 L1 候选模型**）

状态：CANDIDATE_NOT_EFFECTIVE（复核材料；不改变任何制品）
