# ONTO1｜L1 企业公共业务语义核心 八类术语定义稿（DRAFT）

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT 草案**——候任公共语义 Owner（Public Semantic Owner, 下称 PSO）任职技术准备产出；**待 Owner 签署后方可成为受控定义** |
| 编制角色 | 候任 PSO（`ROLE_BOARD.yaml` 中 `public_semantics_owner.status = UNASSIGNED_GAP`，**尚未任命**；本稿不代表任命生效） |
| 状态 | `DRAFT / 待 Owner 签署`；**不得**标 `DESIGN_APPROVED` / `ACTIVE` / `FROZEN` |
| 权威来源 | 设计 `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §4.2（L1 八类）｜矩阵 `docs/review/ARCH-ONTO-2026-001-rereview-package/03-逐术语权威矩阵-22字段.csv`｜映射 `…/04-基线32项映射表.md`｜机读底座 `loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv` |
| 执行依据 | `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §4（Wave 1） |
| 当前门禁 | `RETURN_TO_HLD` 有效；Wave 0 及以后未开工 |
| **IRI 纪律** | 全部权威 IRI **保持 `PENDING:{NS-L1}#<术语短名>`**。D3（语义架构 Owner + 域名 Owner）未签署前，**不得**填任何正式根域，不得写入 `bank.example` / `example.com` / `localhost` / `gientech.com` 等任何值（ADR-ONTO1 草案 §纪律声明、§3 U-1） |

---

## 1. 编制口径

### 1.1 字段集（22 字段，取自设计 V2.0 §9「术语合同字段」）

`termId`、`权威IRI`、`中文名`、`英文名`、`精确定义`、`概念类型`、`T-Box Owner`、`A-Box Owner`、`ID Owner`、`来源系统`、`生命周期`、`父概念`、`域/值域`、`基数`、`时间语义`、`来源/证据`、`隐私等级`、`兼容性等级`、`弃用映射`、`消费方`、`验证方式`、`示例与反例`。

### 1.2 取值规则

| 项 | 规则 |
|---|---|
| 取值优先级 | ① 已登记的机读矩阵（`attribution-45-v2.csv`，哈希钉值）→ ② 复审包 03/04/05 号 → ③ 基线本体回源（`文件:行`）→ ④ **本稿新增建议一律用 `[DRAFT 建议]` 显式标注**，不得与①~③混写 |
| 严禁 | 不发明字段、不改写已登记取值、不用占位根域、不声称任何标准符合性 |
| 计数口径 | L1 = **8 OWL 类**（设计 §4.2）；L1 另有 **4 条 OWL 对象属性**（`memberOfGroup`/`relatesToGroup`/`connectsFrom`/`connectsTo`，复审包 04-C）——属性见附录 A，**不计入「八类」** 以免口径混淆 |
| 证据等级 | 本稿所有「来源/证据」列沿用设计附录 C 三级标注：`VERIFIED`（逐字核验，附 `文件:行`）/ `SYSTEM_OBSERVATION`（工具统计）/ `EXPERT_JUDGMENT`（架构判断）。本稿新增判断一律 `EXPERT_JUDGMENT` + `[DRAFT 建议]` |

### 1.3 已回源核对的基线事实（本稿引用前逐条核验）

| # | 事实 | 回源位置 | 等级 |
|---|---|---|---|
| E-1 | `gits:Customer` 为域引用类，映射自 `EDWCRM.A_ZHCX_CUST_BASE`，非运营控制面状态 | `specs/semantic/gits-core.owl.ttl:22-24` | VERIFIED |
| E-2 | `gits:customerId`（DatatypeProperty，domain `Customer`，range `xsd:string`，源自 `CUSTID`） | `specs/semantic/gits-core.owl.ttl:27-30` | VERIFIED |
| E-3 | `gits:CorporateGroup`（集团身份，由 `LegalEntity.groupId` 与 `GroupRelationship.groupId` 引用） | `specs/semantic/gits-core.owl.ttl:115-117` | VERIFIED |
| E-4 | `gits:LegalEntity`（法人/公司，实据 `LegalEntity(entityId)`） | `specs/semantic/gits-core.owl.ttl:119-121` | VERIFIED |
| E-5 | `gits:GroupRelationship`（`id, groupId, fromEntityId, toEntityId, relationshipType, ownershipRatio`） | `specs/semantic/gits-core.owl.ttl:123-125` | VERIFIED |
| E-6 | `gits:Product`（产品身份，权威物理源为 KERT 产品卡 `product_id`） | `specs/semantic/gits-core.owl.ttl:127-129` | VERIFIED |
| E-7 | `gits:memberOfGroup` domain `LegalEntity` → range `CorporateGroup`（对应 `groupId`） | `specs/semantic/gits-core.owl.ttl:151-155` | VERIFIED |
| E-8 | `gits:relatesToGroup` domain `GroupRelationship` → range `CorporateGroup` | `specs/semantic/gits-core.owl.ttl:157-161` | VERIFIED |
| E-9 | `gits:connectsFrom` / `gits:connectsTo` domain `GroupRelationship` → range **`LegalEntity`** | `specs/semantic/gits-core.owl.ttl:163-173` | VERIFIED |
| E-10 | `Customer` 的 8 个属性（`customer_id`/`cust_name`/`cust_code`/`cert_no`/`cust_type`/`cust_status`/`region`/`brid`） | `specs/semantic/gits-core.linkml.yaml:25-36` | VERIFIED |

> E-6 的一致性说明：基线 `Product` 注释把「权威物理源」写在 **KERT 产品卡**；设计 V2.0 §3.2/§5 已把产品**身份**权威纠正为产品主数据/数据产品（SIM 阶段临时模拟权威，D2），KERT 产品卡回退为 **L2 知识内容**。本稿按设计口径登记，并在 §3 标注该口径差异（属 B-02 类纠正的范围，**非术语定义 Owner 可单方改写**）。

---

## 2. 八类逐术语定义（22 字段齐全）

### 2.1 `Party` 主体

| 字段 | 值 |
|---|---|
| termId | `Party` |
| 权威 IRI | `PENDING:{NS-L1}#Party` |
| 中文名 | 主体 |
| 英文名 | Party |
| 精确定义 | 在法律或业务关系中可承担权利义务的参与方**顶层概念**。本类不含「客户」「成员」等带关系语义的称谓——那些由 `CustomerRole` / `GroupMembership` 承载。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | 银行源系统 / 数据平台 |
| ID Owner | 源系统 |
| 来源系统 | 源系统登记（多源） |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | 无（L1 主体层顶层）`[DRAFT 建议]` |
| 域/值域 | —（类；其作为域名见附录 A 属性） |
| 基数 | — |
| 时间语义 | 主体存续期 |
| 来源/证据 | 委员会报告 §3.6；矩阵 03 号第 2 行 |
| 隐私等级 | 内部 |
| 兼容性等级 | `minor`（新增） |
| 弃用映射 | — |
| 消费方 | GITS / KERT |
| 验证方式 | CQ1 + SHACL 场景 |
| 示例与反例 | 例：某法人主体；反：无主键主体（无任何 `SourceIdentifier` 可锚定的主体） |

### 2.2 `Organization` 组织

| 字段 | 值 |
|---|---|
| termId | `Organization` |
| 权威 IRI | `PENDING:{NS-L1}#Organization` |
| 中文名 | 组织 |
| 英文名 | Organization |
| 精确定义 | 具有内部结构的主体集合；是 `Party` 的分型之一，用于承载「机关/部门/分支机构」等有内部结构的主体。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | 银行源系统 / 数据平台 |
| ID Owner | 源系统 |
| 来源系统 | 源系统登记 |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | `Party` `[DRAFT 建议]`（矩阵已登记 `Organization → Party`） |
| 域/值域 | — |
| 基数 | — |
| 时间语义 | 存续期 |
| 来源/证据 | 委员会报告 §3.6；矩阵 03 号第 3 行 |
| 隐私等级 | 内部 |
| 兼容性等级 | `minor`（新增） |
| 弃用映射 | — |
| 消费方 | GITS / KERT |
| 验证方式 | CQ1 |
| 示例与反例 | 例：某企业；反：临时群组（无登记、无常设内部结构） |

### 2.3 `LegalEntity` 法人

| 字段 | 值 |
|---|---|
| termId | `LegalEntity` |
| 权威 IRI | `PENDING:{NS-L1}#LegalEntity` |
| 中文名 | 法人 |
| 英文名 | LegalEntity |
| 精确定义 | 经法定登记具有法人资格的组织。此处的「资格」指登记事实，**不**表示 GITS/KERT 持有其实例权威。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | 银行源系统 / 数据平台 |
| ID Owner | 源系统 |
| 来源系统 | 工商登记 / 行内源系统 |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | `Organization` `[DRAFT 建议]`（矩阵已登记 `LegalEntity → Organization`） |
| 域/值域 | — |
| 基数 | — |
| 时间语义 | 存续期 |
| 来源/证据 | 基线原名迁移（E-4：`specs/semantic/gits-core.owl.ttl:119-121`）；矩阵 03 号第 4 行 |
| 隐私等级 | 内部 |
| 兼容性等级 | `major`（**迁移**：IRI 从 `gits:` 迁至 `PENDING:{NS-L1}`；术语语义不变） |
| 弃用映射 | `← gits:LegalEntity`（`LEGACY`，映射状态 `RETAINED`） |
| 消费方 | GITS / KERT |
| 验证方式 | CQ1 + SHACL 场景 |
| 示例与反例 | 例：某有限公司；反：无登记号（不能证明法人资格） |

### 2.4 `CustomerRole` 客户角色

| 字段 | 值 |
|---|---|
| termId | `CustomerRole` |
| 权威 IRI | `PENDING:{NS-L1}#CustomerRole` |
| 中文名 | 客户角色 |
| 英文名 | CustomerRole |
| 精确定义 | 主体在**特定机构关系与时间范围**内扮演的客户角色。客户是角色而非互斥实体；同一主体可在不同机构/时期持有多个客户角色。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | EDWCRM 等源系统（SIM 阶段：临时模拟权威，**D4** 未签） |
| ID Owner | 源系统（经 `SourceIdentifier`） |
| 来源系统 | `CTR-DATA-002` / `EDWCRM.A_ZHCX_CUST_BASE`（E-1） |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | 无（**不是** `Party` 的子类）；经关系 `playedBy → Party` 关联 —— 见 §3.2 **未登记项 O-2** |
| 域/值域 | — |
| 基数 | — |
| 时间语义 | **关系有效期**（`validFrom` / `validTo` 强制；客户角色必须可定位到时间区间） |
| 来源/证据 | 基线 `Customer` 重构（E-1/E-2/E-10：`gits-core.owl.ttl:22-24`、`linkml.yaml:25-36`）；设计 §3.6；矩阵 03 号第 5 行 |
| 隐私等级 | **敏感** |
| 兼容性等级 | `major`（**重构**：语义收窄 —— `Customer` 实体 → 角色） |
| 弃用映射 | `← gits:Customer`（`LEGACY`，映射状态 **`REMODELED`：禁止 `owl:equivalentClass`**，允许 SKOS `closeMatch`） |
| 消费方 | GITS / KERT |
| 验证方式 | CQ1 + SHACL 场景 |
| 示例与反例 | 例：`C001` 客户角色（来源 `EDWCRM`，有效期 2026-01-05 起）；反：无来源标识（缺 `SourceIdentifier` ⇒ 具名拒绝） |

### 2.5 `EnterpriseGroup` 集团

| 字段 | 值 |
|---|---|
| termId | `EnterpriseGroup` |
| 权威 IRI | `PENDING:{NS-L1}#EnterpriseGroup` |
| 中文名 | 集团 |
| 英文名 | EnterpriseGroup |
| 精确定义 | 由控制关系形成的企业集合或组织安排。成员关系与其属性**不在本类内**，由 `GroupMembership` 承载。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | 银行源系统 / 数据平台 |
| ID Owner | 源系统 |
| 来源系统 | 集团登记源系统 |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | 无 `[DRAFT 建议]` |
| 域/值域 | — |
| 基数 | — |
| 时间语义 | 存续期 |
| 来源/证据 | 基线改名（E-3：`specs/semantic/gits-core.owl.ttl:115-117`）；矩阵 03 号第 6 行 |
| 隐私等级 | 内部 |
| 兼容性等级 | `major`（**改名**：`CorporateGroup → EnterpriseGroup`） |
| 弃用映射 | `← gits:CorporateGroup`（`LEGACY`，映射状态 `REMODELED`，禁 `equivalentClass`） |
| 消费方 | GITS / KERT |
| 验证方式 | CQ2 |
| 示例与反例 | 例：某控股集团；反：松散名单（无控制关系依据） |

### 2.6 `GroupMembership` 集团成员关系

| 字段 | 值 |
|---|---|
| termId | `GroupMembership` |
| 权威 IRI | `PENDING:{NS-L1}#GroupMembership` |
| 中文名 | 集团成员关系 |
| 英文名 | GroupMembership |
| 精确定义 | 带**来源、有效期与关系类型**的集团成员关系**实体**（关系被实体化，以承载时间与来源，避免把时态信息塞进边属性）。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | 银行源系统 / 数据平台 |
| ID Owner | 源系统 |
| 来源系统 | 集团登记源系统 |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | 无 `[DRAFT 建议]` |
| 域/值域 | — |
| 基数 | — |
| 时间语义 | **`validFrom` / `validTo` 强制**（缺失 ⇒ 具名拒绝，见 `ONTO1-CQ1-CQ2履职准备-DRAFT.md`） |
| 来源/证据 | 基线 `GroupRelationship` 重构（E-5：`gits-core.owl.ttl:123-125`，原字段 `relationshipType`/`ownershipRatio`/`fromEntityId`/`toEntityId`）；矩阵 03 号第 7 行 |
| 隐私等级 | 内部 |
| 兼容性等级 | `major`（**重构**：新增来源/有效期约束） |
| 弃用映射 | `← gits:GroupRelationship`（`LEGACY`，映射状态 `REMODELED`，禁 `equivalentClass`） |
| 消费方 | GITS / KERT |
| 验证方式 | CQ2 + SHACL 场景 |
| 示例与反例 | 例：母公司-子公司（2025-06-01~2026-12-31，来源=集团登记系统）；反：无有效期（`MISSING_VALIDITY_WINDOW`） |

### 2.7 `ProductOffering` 产品身份

| 字段 | 值 |
|---|---|
| termId | `ProductOffering` |
| 权威 IRI | `PENDING:{NS-L1}#ProductOffering` |
| 中文名 | 产品身份 |
| 英文名 | ProductOffering |
| 精确定义 | 银行可售产品的**身份编码与生命周期**的公共引用对象。仅承载「产品是什么、是否在售」；产品的**知识内容**（卖点/准入/风险/解读）属 L2 `ProductKnowledgeCard` 族，经 `describesProduct` 指向本类。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | 产品主数据 / 数据产品（SIM 阶段：临时模拟权威，**D2** 未签） |
| ID Owner | 产品主数据 Owner |
| 来源系统 | 产品目录 / 产品工厂 |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | 无 `[DRAFT 建议]` |
| 域/值域 | — |
| 基数 | — |
| 时间语义 | 在售生命周期 |
| 来源/证据 | 基线 `Product` 重构（E-6：`gits-core.owl.ttl:127-129`，原文把权威物理源写作 KERT 产品卡 —— 口径差异见 §3.1）；设计 §5；矩阵 03 号第 8 行 |
| 隐私等级 | 内部 |
| 兼容性等级 | `major`（**重构**：身份/知识分离） |
| 弃用映射 | `← gits:Product`（`LEGACY`，映射状态 `REMODELED`，禁 `equivalentClass`） |
| 消费方 | GITS / KERT |
| 验证方式 | CQ3 + SHACL 场景（CQ3 责任 Owner 为 Knowledge Owner，非本角色） |
| 示例与反例 | 例：`PROD-CB-001`；反：无编码产品（不能作为公共引用对象）；反：以产品知识卡充当产品身份 |

### 2.8 `SourceIdentifier` 来源标识

| 字段 | 值 |
|---|---|
| termId | `SourceIdentifier` |
| 权威 IRI | `PENDING:{NS-L1}#SourceIdentifier` |
| 中文名 | 来源标识 |
| 英文名 | SourceIdentifier |
| 精确定义 | 由**来源系统 + 对象类型 + 原始 ID + 生效区间**构成的复合标识，用于把 L1 术语实例锚定到其权威来源，并承载 `customerId` 退役后的标识职责。 |
| 概念类型 | OWL 类 |
| T-Box Owner | 公共语义 Owner |
| A-Box Owner | 随各源系统 |
| ID Owner | 源系统 |
| 来源系统 | 各源系统 |
| 生命周期 | 候选 `CANDIDATE` |
| 父概念 | 无 `[DRAFT 建议]` |
| 域/值域 | 语义字段（`[DRAFT 建议]`，供 D4 决策包收敛）：`sourceSystem`、`objectType`、`originalId`、`validFrom`、`validTo`、`extractedAt`、`authorizationBasis` |
| 基数 | 每主体/产品实例 **≥1**（缺失 ⇒ 具名拒绝）；同一来源系统内 `(objectType, originalId)` 唯一 `[DRAFT 建议]` |
| 时间语义 | 生效区间（`validFrom`/`validTo`）；`extractedAt` 记录投影提取时点 |
| 来源/证据 | 委员会报告 §3.6；矩阵 03 号第 9 行；承接 `customerId` 退役（E-2：`gits-core.owl.ttl:27-30`）；字段建议参照 `docs/dispatch/ONTO1-D4-数据Owner请求函.md` |
| 隐私等级 | 内部（`originalId` 可能间接标识个人 ⇒ 投影侧按数据 Owner 分类处置） |
| 兼容性等级 | `minor`（新增） |
| 弃用映射 | 承接 `gits:customerId` 退役（`DEPRECATED`，弃用映射登记） |
| 消费方 | GITS / KERT |
| 验证方式 | CQ1 / CQ2 |
| 示例与反例 | 例：`EDWCRM:C001`；反：缺来源系统（`MISSING_SOURCE_IDENTIFIER`）；反：裸字符串 ID（无来源可追溯） |

---

## 3. 本稿发现的口径问题与待决项（**须 TL / 委员会裁定，PSO 不得单方决定**）

> 纪律：以下均为**登记**而非修改。PSO 无权改写已登记的矩阵/设计取值；任一处确定后须走「设计修订 → 矩阵更新 → 本稿修订」链路。

### 3.1 O-1：`ProductOffering` 的「权威物理源」两处口径不一致

| 出处 | 表述 |
|---|---|
| 基线本体原文 | 「产品身份（域引用类）。权威物理源为 KERT 产品卡 `product_id`」（E-6：`specs/semantic/gits-core.owl.ttl:127-129`） |
| 设计 V2.0 / 矩阵 | A-Box Owner = 产品主数据/数据产品（SIM 临时模拟权威，D2）；KERT 产品卡回退为 L2 知识内容 |

判定：属设计 B-02 类纠正（业务真相边界）**已覆盖**的差异，本稿按设计口径登记。但**本体注释文字尚未改写**，Wave 2 拆分时须同步处理，否则新制品会带着旧口径发布。**建议**：列入 Wave 2 的 `Product` 注释改写清单（与 `products.ttl:1` 前缀修复同批）。

### 3.2 O-2：`playedBy` 未登记为新属性（**计数影响**）

矩阵 03 号 `CustomerRole` 的「父概念」列写 `—(角色playedBy→Party)`，`attribution-45-v2.csv` 第 5 行同。但：

- `playedBy` **不在** 04-C 属性映射的 36 条 OWL 对象属性之内；
- 全仓检索 `playedBy` 仅命中两处矩阵文书（`03-逐术语权威矩阵-22字段.csv:5`、`attribution-45-v2.csv:5`），**无代码/本体实据**。

判定：若 `CustomerRole → Party` 的关联确需一个命名属性，则它是**第 37 条 OWL 对象属性**，与既有计数（36）不自洽。**建议**：Wave 2 前由设计 Owner 裁定三选一 —— ① 正式登记 `playedBy` 并更新计数（36→37）；② 用 `rdfs:subClassOf`/等价构造（如 `CustomerRole ⊑ ∃playedBy.Party` 用匿名限制，不新增命名属性）；③ 从矩阵中删除该括注（避免悬空标识符）。

### 3.3 O-3：L1 `connectsFrom` / `connectsTo` 的 range 放宽，级别判定与 07 号矩阵可能不自洽

| 项 | 事实 |
|---|---|
| 基线 | domain `GroupRelationship` → range **`LegalEntity`**（E-9：`gits-core.owl.ttl:163-173`） |
| 目标 | domain `GroupMembership` → range **`Party`**（矩阵 03 号第 68/69 行） |
| 矩阵登记级别 | `major迁移` |
| 07 号矩阵口径 | 「**放宽约束**（扩大值域）= `minor`」（`07-兼容性矩阵-major-minor-patch.md` §1） |

判定：range 由 `LegalEntity` 放宽到 `Party` 属**扩大值域**；但同时发生 domain 改名（`GroupRelationship → GroupMembership`）与 IRI 迁移。**建议**：明确按「**复合变更取最高级别**」原则表述（IRI 迁移 + domain 改名已构成 major），并在 07 号矩阵补一行说明「放宽与迁移并发时取 major」，避免实施时两级判定打架。

### 3.4 O-4：`range 改指 CustomerRole` 的条数 —— 设计 §4.1「4 条」vs 矩阵「5 条」

- 设计 V2.0 §4.1：「属性 19 条不变（`ofCustomer` 等 **4 条**的 range 改指 L1 `CustomerRole`）」
- 复审包 04-C 与 `attribution-45-v2.csv` 实测：**5 条** —— `gateOfCustomer`、`ofCustomer`、`opportunityOfCustomer`、`profileOfCustomer`、`refersToCustomer`（复核命令：`grep -c "改指" loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv` → `5`）
- 另有 `opportunityForProduct` 1 条 range 指向 `ProductOffering`（合计 6 条 range 变更）

判定：**设计文字与机读矩阵不一致**。**建议**：以机读矩阵（有哈希钉值、可复现）为准，设计 §4.1 文字列为待修订项，Wave 2 的 `onto_split_check.py` 按 **5 + 1 = 6 条 range 变更** 断言。

### 3.5 O-5：`memberOfGroup` 的 domain 由 `LegalEntity` 放宽为 `Party`

基线 domain = `LegalEntity`（E-7），目标 domain = `Party`（矩阵 03 号第 66 行）。同为扩大值域，处置同 O-3。附带影响：`connectsFrom/To` 的 range 改为 `Party` 后，原来「集团关系只连接法人」的隐式约束**消失**，须由 SHACL 显式补回还是接受放宽 —— **需数据 Owner（D4）表态**（候选补齐放在 D4 决策包）。

---

## 4. 对八类的自检清单（提交 Owner 签署前须逐条可核）

| # | 检查 | 结论 |
|---|---|---|
| C-1 | 8 类逐条 22 字段齐全、无空字段（允许「—」但须有意义） | ☑ 本稿已满足 |
| C-2 | 全部权威 IRI 为 `PENDING:{NS-L1}#X`，无任何正式根域 | ☑ |
| C-3 | 无 `CONFORMANCE` / 国标符合性表述 | ☑ |
| C-4 | 未标 `ACTIVE` / `FROZEN` / `DESIGN_APPROVED`；生命周期列一律 `候选CANDIDATE` | ☑ |
| C-5 | 每条「来源/证据」带 `文件:行` 或矩阵行号 | ☑（E-1~E-10 + 03 号行号） |
| C-6 | 重构项（`CustomerRole`/`EnterpriseGroup`/`GroupMembership`/`ProductOffering`）弃用映射标注 `REMODELED` 且显式禁 `equivalentClass` | ☑ |
| C-7 | 新增项（`Party`/`Organization`/`SourceIdentifier`）标 `minor新增` | ☑ |
| C-8 | 未修改 `specs/semantic/`、`generated/`、`CONTRACT_INDEX.yaml` | ☑ |
| C-9 | 与矩阵 03 号/`attribution-45-v2.csv` 逐字段一致（除已登记的 `[DRAFT 建议]` 与 §3 待决项） | ☑ |
| C-10 | 待决项已登记而非静默决定 | ☑ §3 O-1~O-5 |

---

## 附录 A：L1 资产机读表（22 字段 + 3 归属列，12 行 = 8 类 + 4 属性）

> 用途：供 Wave 2 拆分与 `onto_split_check.py` 比对。**本附录不是受控制品**（受控制品在 `specs/`）；正式落库须走合同先行链路。
> 内容与 `loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv` 的 L1 行一致（该文件哈希 `sha256 05ec849e57a163a5…`）。

```csv
termId,权威IRI,中文名,英文名,精确定义,概念类型,T-Box Owner,A-Box Owner,ID Owner,来源系统,生命周期,父概念,域/值域,基数,时间语义,来源证据,隐私等级,兼容性等级,弃用映射,消费方,验证方式,示例与反例,四层归属,目标制品口径,基线映射类型
Party,PENDING:{NS-L1}#Party,主体,Party,在法律或业务关系中可承担权利义务的参与方顶层概念,OWL类,公共语义Owner,银行源系统/数据平台,源系统,源系统登记,候选CANDIDATE,无[建议],—,—,主体存续期,委员会报告§3.6,内部,minor新增,—,GITS/KERT,CQ1+SHACL场景,例:某法人主体;反:无主键主体,L1 公共业务语义核心,OWL类,新增
Organization,PENDING:{NS-L1}#Organization,组织,Organization,具有内部结构的主体集合,OWL类,公共语义Owner,银行源系统/数据平台,源系统,源系统登记,候选CANDIDATE,Party,—,—,存续期,委员会报告§3.6,内部,minor新增,—,GITS/KERT,CQ1,例:某企业;反:临时群组,L1 公共业务语义核心,OWL类,新增
LegalEntity,PENDING:{NS-L1}#LegalEntity,法人,LegalEntity,经登记具有法人资格的组织,OWL类,公共语义Owner,银行源系统/数据平台,源系统,工商/行内源系统,候选CANDIDATE,Organization,—,—,存续期,基线LegalEntity(gits-core.owl.ttl:119-121),内部,major迁移,←gits:LegalEntity(LEGACY),GITS/KERT,CQ1+SHACL场景,例:某有限公司;反:无登记号,L1 公共业务语义核心,OWL类,基线映射
CustomerRole,PENDING:{NS-L1}#CustomerRole,客户角色,CustomerRole,主体在特定机构关系与时间范围内扮演的客户角色,OWL类,公共语义Owner,EDWCRM等源系统(SIM临时模拟权威D4),源系统经SourceIdentifier,CTR-DATA-002 EDWCRM,候选CANDIDATE,无(非Party子类;关联playedBy→Party见O-2),—,—,关系有效期,基线Customer重构(gits-core.owl.ttl:22-24;linkml.yaml:25-36),敏感,major重构,←gits:Customer(LEGACY;REMODELED禁equivalentClass),GITS/KERT,CQ1+SHACL场景,例:C001客户角色;反:无来源标识,L1 公共业务语义核心,OWL类,基线映射
EnterpriseGroup,PENDING:{NS-L1}#EnterpriseGroup,集团,EnterpriseGroup,由控制关系形成的企业集合或组织安排,OWL类,公共语义Owner,银行源系统/数据平台,源系统,集团登记源系统,候选CANDIDATE,无,—,—,存续期,基线CorporateGroup改名(gits-core.owl.ttl:115-117),内部,major改名,←gits:CorporateGroup(LEGACY;REMODELED),GITS/KERT,CQ2,例:某控股集团;反:松散名单,L1 公共业务语义核心,OWL类,基线映射
GroupMembership,PENDING:{NS-L1}#GroupMembership,集团成员关系,GroupMembership,带来源有效期与关系类型的集团成员关系实体,OWL类,公共语义Owner,银行源系统/数据平台,源系统,集团登记源系统,候选CANDIDATE,无,—,—,validFrom/validTo强制,基线GroupRelationship重构(gits-core.owl.ttl:123-125),内部,major重构,←gits:GroupRelationship(LEGACY;REMODELED),GITS/KERT,CQ2+SHACL场景,例:母公司-子公司;反:无有效期,L1 公共业务语义核心,OWL类,基线映射
ProductOffering,PENDING:{NS-L1}#ProductOffering,产品身份,ProductOffering,银行可售产品的身份编码与生命周期公共引用对象,OWL类,公共语义Owner,产品主数据/数据产品(SIM临时模拟权威D2),产品主数据Owner,产品目录/产品工厂,候选CANDIDATE,无,—,—,在售生命周期,基线Product重构(gits-core.owl.ttl:127-129;注释口径差见O-1),内部,major重构,←gits:Product(LEGACY;REMODELED),GITS/KERT,CQ3+SHACL场景,例:PROD-CB-001;反:无编码产品,L1 公共业务语义核心,OWL类,基线映射
SourceIdentifier,PENDING:{NS-L1}#SourceIdentifier,来源标识,SourceIdentifier,来源系统+对象类型+原始ID+生效区间的复合标识,OWL类,公共语义Owner,随各源系统,源系统,各源系统,候选CANDIDATE,无,—,每实例≥1,生效区间+extractedAt,委员会报告§3.6;承接customerId退役(gits-core.owl.ttl:27-30),内部,minor新增,承接customerId退役,GITS/KERT,CQ1/CQ2,例:EDWCRM:C001;反:缺来源系统,L1 公共业务语义核心,OWL类,新增
memberOfGroup,PENDING:{NS-L1}#memberOfGroup,集团成员于,memberOfGroup,主体与集团的成员关系(细节由GroupMembership承载),OWL对象属性,公共语义Owner,—,—,—,候选CANDIDATE,—,Party→EnterpriseGroup(基线为LegalEntity→CorporateGroup,见O-5),0..n,有效期随GroupMembership,基线OWL(domain/range适配;gits-core.owl.ttl:151-155),内部,major迁移,←gits:memberOfGroup(LEGACY),GITS/KERT,CQ2,—,L1 公共业务语义核心,OWL对象属性,基线映射
relatesToGroup,PENDING:{NS-L1}#relatesToGroup,关联集团,relatesToGroup,集团成员关系与集团的关联,OWL对象属性,公共语义Owner,—,—,—,候选CANDIDATE,—,GroupMembership→EnterpriseGroup,1..1,—,基线OWL(适配;gits-core.owl.ttl:157-161),内部,major迁移,←gits:relatesToGroup(LEGACY),GITS/KERT,CQ2,—,L1 公共业务语义核心,OWL对象属性,基线映射
connectsFrom,PENDING:{NS-L1}#connectsFrom,连接自,connectsFrom,集团关系的有向起点,OWL对象属性,公共语义Owner,—,—,—,候选CANDIDATE,—,GroupMembership→Party(基线range=LegalEntity,见O-3),1..1,—,基线OWL(适配;gits-core.owl.ttl:163-167),内部,major迁移,←gits:connectsFrom(LEGACY),GITS/KERT,CQ2,—,L1 公共业务语义核心,OWL对象属性,基线映射
connectsTo,PENDING:{NS-L1}#connectsTo,连接至,connectsTo,集团关系的有向终点,OWL对象属性,公共语义Owner,—,—,—,候选CANDIDATE,—,GroupMembership→Party(基线range=LegalEntity,见O-3),1..1,—,基线OWL(适配;gits-core.owl.ttl:169-173),内部,major迁移,←gits:connectsTo(LEGACY),GITS/KERT,CQ2,—,L1 公共业务语义核心,OWL对象属性,基线映射
```

---

## 附录 B：引用与回源命令（可复现）

```bash
# E-1~E-10 基线回源
sed -n '22,30p;115,129p;151,173p' specs/semantic/gits-core.owl.ttl
sed -n '25,36p'                     specs/semantic/gits-core.linkml.yaml
# 矩阵一致性（L1 行数应为 12 = 8 类 + 4 属性）
grep -c "L1 公共业务语义核心" loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv
# 本稿 §3.4 的 5 条 range 改指
grep -c "改指" loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv
# 本稿 §3.2 的 playedBy 全仓命中
rg -n "playedBy" --glob '!.git'
```

## 附录 C：非声明

- 本稿是**候任角色的技术准备草稿**，不构成受控定义、不构成 `DESIGN_APPROVED`、不构成 L1 发布、不代表公共语义 Owner 已任命；
- 与 `specs/` 冲突时以 `specs/` 为准；与设计 V2.0 / 复审包冲突时以设计 V2.0 / 复审包为准；
- 本稿不引入任何国标条款级声称；`R1~R9` 见 `ONTO1-L1-建模规则R1-R9修订版-DRAFT.md`（内部规则 / 参照对齐名义）。
