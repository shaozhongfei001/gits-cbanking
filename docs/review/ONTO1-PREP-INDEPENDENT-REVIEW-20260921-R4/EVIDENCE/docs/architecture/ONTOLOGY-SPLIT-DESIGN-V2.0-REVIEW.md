# GITS-KERT 本体模型四层归属设计与国标（GB/T 48000.3-2026）参照对齐方案

| 项 | 值 |
|---|---|
| 文档编号 | ARCH-ONTO-2026-001 |
| 版本 | **V2.0**（RETURN_TO_HLD 整改后复审稿） |
| 状态 | **待复审（RE_REVIEW）**——目标状态迁移：`FOR_REVIEW → DESIGN_APPROVED`（仅请求设计基线批准与实施入口，见 §10 状态机） |
| 日期 | 2026-09-20 |
| 作者 | GITS-KERT 工作区全局架构师 |
| 评审依据 | `docs/review/ARCH-ONTO-2026-001_架构委员会评审报告_V1.0.md`（3 BLOCKER / 10 MAJOR / 3 MINOR，十项关闭条件） |
| 逐条处置 | `docs/review/ARCH-ONTO-2026-001_整改处置报告-V1.0.md`（本稿为其设计层载体） |
| 版本沿革 | V1.0 设计稿 → V1.1/V1.2 评审稿（RETURN_TO_HLD）→ **V2.0：四层模型重构**；V1.2 已标记退回 |
| 事实基线 | `gits-core.owl.ttl`（32 类 / 34 对象属性 / 1 数据属性，`sha256:705578d6324abd0c…`）。**声明**：该基线统计为作者系统观察（SYSTEM_OBSERVATION），未经委员会独立复现 |

---

## 0. V2.0 相对 V1.2 的实质变更（响应评审结论）

| # | 变更 | 响应 |
|---|---|---|
| 1 | **三层 → 四类模型资产 + 受控词表**：公共业务语义核心 / KERT 知识供给元模型 / GITS 经营运行本体 / GK-KE 集成契约注册表（+SKOS 词表单列） | B-01、M-06 |
| 2 | **废止「A/B/C 任一满足 ⇒ 公共」算法**，改用委员会认可的四条严格条件（§2.2） | B-01 |
| 3 | **撤回「权威循环」论断**：改为六列权威表 + 发布依赖图论证（§2.1）；E1 重新定性为「归属含混 + 发布耦合」 | M-01 |
| 4 | **业务真相边界纠正**：客户/法人/集团/产品身份的正式 A-Box 权威 = 银行源系统/数据平台；GITS/KERT 仅持授权投影；SIM 阶段用**显式临时模拟权威声明**（含退出条件） | B-02 |
| 5 | **Product 模式闭合**：`ProductOffering`（身份）与 `ProductKnowledgeCard/Version/Interpretation/RuleBundle`（知识内容）分离，`describesProduct` 关联；40 悬空引用进入处置流程，**不得永久豁免** | §3.5→§5，M-03 |
| 6 | **客户建模重构**：`Customer` → `Party`/`Organization`/`LegalEntity` + `CustomerRole`；`CorporateGroup`→`EnterpriseGroup`、`GroupRelationship`→`GroupMembership`（带来源/有效期/类型）；新增 `SourceIdentifier` | §3.6→§4.2 |
| 7 | **国标表述降级为「参照对齐」**：采用委员会给定的唯一可声明口径；`ONTOLOGY-CONFORMANCE.md` 更名 `REFERENCE-ALIGNMENT.md`；条款级矩阵待正式文本（外部依赖已声明） | M-02 |
| 8 | **验证状态模型**：`PASS/FAIL/NOT_EVALUATED/DESIGN_ONLY/WAIVED_FOR_DEVELOPMENT`；豁免只放行开发，永不满足激活门禁 | M-03、§6.3 |
| 9 | **命名空间**：采纳中立持久 IRI + 旧 IRI `LEGACY` 兼容迁移（ADR 框架见 §7） | 裁定 1、M-04 |
| 10 | **状态机分离**：`DESIGN_APPROVED → IMPLEMENTED → QA_PASS → OWNER_ACTIVATED`；委员会只批设计基线 | B-03 |
| 11 | **SHACL 策略修正**：废止「每类一份 NodeShape」普遍真理，Shape 由验证场景与封闭边界决定；空转判定补目标数/夹具命中数 | §5.5、§6.3 |
| 12 | **R9 改写**：version IRI 钉值为**项目加严策略**而非 W3C/GB 强制；新增 import closure 单版本检查 | §6.2 |
| 13 | **兼容性规范**：major/minor/patch 矩阵 + 弃用期 + 迁移映射 + 回滚，替代朴素「只增不改」 | M-09 |
| 14 | **统一计数（分口径）**：基线 32 → **目标 45 模型资产 = 39 OWL 类 + 1 SKOS 词表 + 5 Schema 对象**（13 净新增），全部 32 基线术语有映射、0 退役 | m-01、复审 §4.3 |
| 15 | **证据纪律**：全部证据标注 VERIFIED / SYSTEM_OBSERVATION / EXPERT_JUDGMENT 三级 + 输出摘要哈希 | M-08 |
| 16 | **元数据修正**：公共制品 `PROVENANCE.json` 用 `authorityEntity`（公共语义权威实体）+ `hostingRepo`（物理寄放）双字段 | m-02 |

---

## 1. 保留的既定原则（委员会已认可，不再论证）

类权威与实例权威分离（显式登记 + 可追溯引用）；每术语单一发布权威；跨仓不运行时直读；哈希钉值 + 漂移具名拒绝（不替代语义兼容性判断）；SHACL 空转不得当作业务验证通过；生成物禁手改、单向可复现链；公共模块防单系统私有化（双 Owner、独立版本、独立发布）；Kuzu 等图平台仅为授权实例投影与查询索引，不是业务事实或知识审批权威。

---

## 2. 归属方法论（重写）

### 2.1 六列权威表（替代「权威循环」论断）

V1.2 把「`Product` 类在 GITS + KERT 钉 GITS 副本 + 产品卡实例在 KERT」直接解释为权威循环，经委员会指正：这三件事只构成**发布依赖和所有权表达不清**，不构成逻辑/治理循环。V2.0 撤回该论断，改用六列权威模型作为唯一分析框架：

| 列 | 含义 |
|---|---|
| ① 术语定义 Owner | 该类/属性/词表项的定义（T-Box）由谁发布 |
| ② 身份与 ID Owner | 标识符空间（如 PROD-\*、客户号）由谁分配与裁决冲突 |
| ③ 实例事实 Owner | 实例数据（A-Box）的正式权威系统 |
| ④ 发布制品 Owner | 可消费制品（OWL/Schema/副本包）的发布流水线 |
| ⑤ 消费依赖方向 | 谁钉谁的版本（必须单向） |
| ⑥ 变更审批与兼容性责任 | 变更谁批、破坏性变更谁负责迁移 |

**判定规则**：仅当六列中出现闭环依赖（A 的发布以 B 的权威决定为前提 ∧ B 的发布以 A 的权威决定为前提，且无单向版本契约可打断）才可定性「权威循环」。对 `Product` 族应用本表（附录 B）：现状为「定义 Owner 与实例事实 Owner 分置两仓且未显式登记」的**归属含混**，消费依赖方向（KERT 钉 GITS 制品）本身是单向的、不构成循环——但归属含混仍是缺陷，由四层模型 + 逐术语权威矩阵（附录 A）消除。

### 2.2 公共层准入条件（替代旧算法）

概念进入**企业公共业务语义核心**须**同时**满足（委员会 §3.3 口径）：

1. 在多个业务域中具有**相同、稳定、与提供方实现无关**的含义；
2. 任一单域都**没有充分权力单独改变**其语义；
3. 承载**跨系统身份、基础关系或互操作语义**；
4. 进入公共层**减少耦合**，而非把提供方内部模型扩散给所有消费者。

推论（采纳委员会 §3.3/§3.4）：`KnowledgeMap`/`Asset`/`Skill` 是 **KERT 发布的知识供给元模型**（GITS 经版本化契约消费，如同消费 API）；`ActivationContract`/`Capability` 属**集成契约注册表**；`TaskType` 属**受控词表（SKOS）**——均不因「两侧引用」进入公共业务本体。

---

## 3. 目标架构：四类模型资产 + 受控词表

### 3.1 总览（采纳委员会 §5.1，含一处项目补充建议）

| 资产层 | 定义 Owner | 实例/记录 Owner | 主要制品 |
|---|---|---|---|
| **L1 企业公共业务语义核心** | 公共语义 Owner（新设角色） | 银行源系统/数据平台 | OWL/SHACL、词典、ID 与映射规则 |
| **L2 KERT 知识供给元模型** | Knowledge Owner / KERT Owner | KERT | OWL/SHACL + 知识资产 Schema/API |
| **L3 GITS 经营运行本体** | Business Process Owner / GITS Owner | GITS | OWL/SHACL + 状态机/动作合同 |
| **L4 GK-KE 集成契约注册表** | Integration Contract Owner（新设角色） | 契约注册中心 | JSON Schema/LinkML/OpenAPI；需要图查询时生成 RDF 投影 |
| **受控词表** | 各词表 Owner | 注册中心 | SKOS |

> **项目补充建议**（请委员会确认）：`Asset`（ASSET-\* 可激活资产）按委员会 §3.3 口径归 L2，命名为 `AssetDefinition`——委员会 §5.1 的 L2 行未显式列出 `Asset`，此处为显性化补充。

### 3.2 权威责任矩阵（采纳委员会 §5.2）

| 事实类型 | 权威系统 | GITS/KERT 的允许行为 |
|---|---|---|
| 客户、法人、集团、产品身份与正式状态 | **银行源系统/数据平台** | 保存带来源、时点、版本的授权投影，不重新定义真相 |
| 知识文档、规则、知识地图、技能定义、产品知识版本 | KERT | 发布候选、审核版和 ACTIVE 版；不代替业务主数据或审批结论 |
| 任务、案件、建议、人工决定、动作与回执 | GITS | 作为经营过程权威；引用知识版本和源数据时点 |
| 关系查询投影 | Kuzu/图平台 | 提供索引和路径；不得成为知识审批、产品主数据或业务决定权威 |
| 跨系统端点、消费者、版本绑定和兼容性 | 集成契约注册中心 | 双方按批准合同消费；运行时验证版本、权限和状态 |

**SIM 阶段特别裁定项**：当前试点无正式产品主数据/客户主数据接口。须由 Owner 批准《SIM 临时模拟权威声明》：指定 SIM 登记表为**临时**模拟权威，写明 ① 临时性质 ② 覆盖范围 ③ **退出条件**（正式源系统接入即废止）④ 责任人。**禁止**把临时登记表静默升级为企业权威。

---

## 4. 逐层归属清单

### 4.1 L3 GITS 经营运行本体（19 类，与 V1.2 一致）

`OperatingCase`、`Claim`、`Evidence`、`Evaluation`、`Action`、`Receipt`、`HumanConfirmation`、`HumanGate`、`Interaction`、`InteractionExtension`、`Opportunity`、`OpportunitySignal`、`Commitment`、`ExternalEvent`、`KycGapProfile`、`PolicyRule`、`AuditTraceEntry`、`RelationshipReport`、`Task`；属性 19 条不变（`ofCustomer` 等 4 条的 range 改指 L1 `CustomerRole`，经 `owl:imports` 引用）。

### 4.2 L1 企业公共业务语义核心（8 类）

| 类 | 中文 | 来源 | A-Box Owner |
|---|---|---|---|
| `Party` | 主体（参与方顶层概念） | **新增**（委员会 §3.6） | 银行源系统/数据平台 |
| `Organization` | 组织 | **新增**（委员会 §3.6） | 同上 |
| `LegalEntity` | 法人 | 基线 `LegalEntity` | 同上（GITS 仅持授权快照/运行投影） |
| `CustomerRole` | 客户角色（主体在特定机构/关系/时间范围内扮演） | 基线 `Customer` **重构** | 同上（正式权威 EDWCRM 等源系统；SIM 阶段临时模拟权威声明） |
| `EnterpriseGroup` | 集团 | 基线 `CorporateGroup` 改名 | 银行源系统/数据平台 |
| `GroupMembership` | 集团成员关系（**带来源、有效期、关系类型**） | 基线 `GroupRelationship` 重构 | 同上 |
| `ProductOffering` | 产品身份/编码/生命周期（公共引用对象） | 基线 `Product` 改名重构 | **产品目录/产品工厂/经批准的数据产品**（不得默认为 KERT 产品卡；SIM 阶段临时模拟权威声明） |
| `SourceIdentifier` | 来源标识（来源系统 + 对象类型 + 原始 ID + 生效区间） | **新增**（委员会 §3.6） | 随各主体/产品源系统 |

**数据属性调整**：基线 `customerId`（datatype）**退役**，由 `CustomerRole` + `SourceIdentifier` 模式承载（弃用映射入附录 A）。

### 4.3 L2 KERT 知识供给元模型（12 类）

| 类 | 来源 | 类 | 来源 |
|---|---|---|---|
| `ProductKnowledgeCard` | 基线 | `KnowledgeItem` | 新增（V1.2 已建议，委员会 §5.1 采纳） |
| `ProductKnowledgeVersion` | 基线 | `Segment` | 新增（同） |
| `KnowledgeMapDefinition` | 基线 `KnowledgeMap` 改名 | `KnowledgeSource` | 新增（同） |
| `SkillDefinition` | 基线 `Skill` 改名 | `ProductInterpretation` | 新增（同） |
| `AssetDefinition` | 基线 `Asset` 改名（§3.1 补充建议） | `RuleBundle` | 新增（同） |
| `EvidenceBundle` | 新增（同） | `Projection` | 新增（同） |

属性：基线 6 条（`cardOfProduct`/`versionOfProduct`/`supersedesVersion`/`requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith`）+ 新增 6 条（`segmentOf`/`sourcedFrom`/`interprets`/`rulesFor`/`projectionOf`/`evidenceOf`）+ 新增 `describesProduct`（`ProductKnowledgeCard → ProductOffering`，**知识卡指向产品身份，不以知识卡替代产品主数据**，委员会 §3.5）= 13 条。产品关系 3 条的 range 指向 L1 `ProductOffering`。

### 4.4 L4 集成契约注册表（6 项，非 OWL）

| 资产 | 来源 | 制品形式 |
|---|---|---|
| `ActivationContract` | 基线 | JSON Schema/LinkML |
| `CapabilityPublication` | 基线 `Capability` 改名重构（含发布状态/端点/授权/兼容版本） | JSON Schema/LinkML |
| `EndpointBinding` | **新增** | JSON Schema/OpenAPI |
| `ConsumerBinding` | **新增** | JSON Schema |
| `ContractVersion` | **新增**（版本与兼容性记录） | LinkML |
| `TaskTypeScheme` | 基线 `TaskType` 转 **SKOS 词表** | SKOS（RDF 词表，非 OWL 类） |

基线属性 `hasTaskType`/`governedByContract`/`invokesCapability`/`referencesAsset`/`referencesSkill`（5 条）**不再作为 OWL 属性**，由注册表 Schema 字段与 L2 引用关系承载（映射入附录 A）。

### 4.5 统一计数（m-01 整改；复审意见 §4.3 修正：分口径，不统称「45 个本体类」）

**目标模型资产合计 45 项，分三种制品口径**：

| 制品口径 | 数量 | 构成 |
|---|---|---|
| **OWL 类** | **39** | L3 GITS 19 + L1 公共 8 + L2 KERT 12 |
| **SKOS 概念体系** | **1** | `TaskTypeScheme`（L4） |
| **集成契约 Schema 对象** | **5** | `ActivationContract`、`CapabilityPublication`、`EndpointBinding`、`ConsumerBinding`、`ContractVersion`（L4，JSON Schema/LinkML） |
| **合计** | **45 模型资产** | 三种治理对象分别计数、分别批准流程 |

**基线 32 个 OWL 类的去向**（逐项映射见复审包 04 号文件）：保留原名 **19**（L3）｜迁移并重构/改名 **10**（L1：Customer→CustomerRole、CorporateGroup→EnterpriseGroup、GroupRelationship→GroupMembership、Product→ProductOffering 计 4 重构 + LegalEntity 计 1 原名迁移；L2：KnowledgeMap/Asset/Skill 计 3 改名 + PKC/PKV 计 2 原名迁移）｜转换制品类型 **3**（ActivationContract→Schema、Capability→CapabilityPublication Schema、TaskType→SKOS）｜**退役 0**。

**属性口径**：OWL 对象属性 **36** = L3 19 + L2 13 + L1 4（`memberOfGroup`/`relatesToGroup`/`connectsFrom`/`connectsTo`）；基线 34 对象属性中另 5 条（`hasTaskType`/`governedByContract`/`invokesCapability`/`referencesAsset`/`referencesSkill`）**转为 L4 Schema 字段**（不再是 OWL 属性）；数据属性 **0**（基线 `customerId` **退役**，由 `SourceIdentifier` 模式承载，弃用映射登记）。

---

## 5. `Product` 模式闭合（关闭条件 4）

```
ProductOffering（L1，产品身份）  ←── describesProduct ───  ProductKnowledgeCard（L2，知识资产）
        ▲                                                        │
        │ （A-Box：产品主数据/数据产品；SIM 临时模拟权威）          ├── ProductKnowledgeVersion（版本）
        │                                                        ├── ProductInterpretation（解读）── interprets ──▶ ProductOffering
        └──── requiresProduct / complementsProduct /             └── RuleBundle（规则包）── rulesFor ──▶ ProductOffering
              mutuallyExclusiveWith（关系类型权威在 L2，
              实例权威在产品卡 front matter，经 WP1.3 裁定）
```

**40 处悬空引用处置**（M-03，替代 V1.2 的「显式豁免」）：

1. 逐条分类：**有效待补 / 错误引用 / 作废**（产品 Owner 裁定，输出处置清单）；
2. 处置完成前，相关 SHACL 验证场景状态 = `NOT_EVALUATED`（关系无实例）或 `DESIGN_ONLY`；
3. **不得以永久豁免关闭**；豁免（`WAIVED_FOR_DEVELOPMENT`）只允许继续开发，不满足任何激活门禁；
4. 进入激活门禁前，关键关系必须有经 Owner 批准的实例或受控测试夹具（含目标数断言）。

---

## 6. 验证与质量（M-03/M-07/M-09、委员会 §5.4/§5.5/§6.2/§6.3）

### 6.1 验证状态模型（关闭条件 7）

`PASS` / `FAIL` / `NOT_EVALUATED`（无生产实例）/ `DESIGN_ONLY`（仅设计，无实现）/ `WAIVED_FOR_DEVELOPMENT`（豁免，仅放行开发）。规则：任何豁免**不得改写为 PASS**，**不得满足激活退出标准**；状态迁移须留痕（谁、何时、依据什么证据）。

### 6.2 SHACL 门禁加严（委员会 §6.3）

每个验证场景必须记录：期望目标数 vs 实际目标数；正例/负例/变异测试命中数；无生产实例 ⇒ `NOT_EVALUATED`/`DESIGN_ONLY`；激活门禁前关键关系须有经批准实例或受控夹具。「0 目标 0 违规」在 SHACL 规范上合规，但**项目不得解释为业务覆盖已验证**。

### 6.3 Shape 策略修正（委员会 §5.5）

废止「每类恰好一份 NodeShape」作为普遍真理。Shape 由**验证场景与封闭边界**决定：一个类可有发布/摄取/运行多个 Shape，不同类可复用 Shape。必须保证：目标、约束、场景覆盖**可解释且可复现**（场景清单 + 覆盖矩阵入 `REFERENCE-ALIGNMENT.md` 附录）。

### 6.4 导入与版本钉（委员会 §6.2，替代 V1.2 R9）

> GK-KE 内部发布策略：生产消费方固定特定 **version IRI** 并同时校验内容哈希；这是**项目加严规则**，不宣称为 W3C 或 GB/T 的普遍强制要求（W3C 中 versionIRI 为 MAY）。

新增检查：import closure **不得同时包含同一 ontology series 的两个不同版本**。

### 6.5 兼容性规范（M-09，替代朴素「只增不改」）

| 级别 | 定义 | 处置 |
|---|---|---|
| patch | 注释/标签/示例完善，不改语义 | 直接发布，消费方无需动作 |
| minor | 只增式扩展（新类/新属性/放宽约束），旧消费方不受影响 | 发布 + CHANGELOG；旧钉值仍有效 |
| major | 破坏性变更（删项/改名/收窄域值域/新增可能推翻既有结论的约束） | 新 versionIRI + 弃用期（≥1 发布周期双发布）+ oldIRI→newIRI 迁移映射 + 回滚预案 + 双侧 Owner 批准 |

**注意**（采纳委员会指正）：新增约束也可能破坏兼容性（收紧即 major 候选），不以「只增」自动判 minor；每次变更配兼容性测试（旧夹具必须仍按预期通过/失败）。

### 6.6 语义验收矩阵（M-07/关闭条件 9：competency questions）

六类 CQ 全部绑定查询、正例、负例、预期结果、责任 Owner（夹具设计在允许的复审前工作中完成）：

| # | 能力问题 | 验证对象 | 责任 Owner |
|---|---|---|---|
| CQ1 | 某法人何时、依据哪个源系统成为客户？ | `CustomerRole` + `SourceIdentifier`（来源系统/原始 ID/生效区间）；负例：无来源标识 ⇒ 拒绝 | 公共语义 Owner |
| CQ2 | 某集团成员关系在指定业务日是否有效，来源是什么？ | `GroupMembership`（validFrom/To + 来源）；负例：过期关系查询当日 ⇒ 无效 | 公共语义 Owner |
| CQ3 | 某产品知识卡描述的是哪个产品版本，是否在查询时点有效？ | `describesProduct` + `ProductKnowledgeVersion` 有效期；负例：卡指向已退役版本 ⇒ 具名提示 | Knowledge Owner |
| CQ4 | 某 GITS 建议使用了哪一版地图、规则、产品知识和数据快照？ | ActivationPlan planHash + 版本子块可重放；负例：版本子块缺失 ⇒ 拒绝执行 | Integration Contract Owner |
| CQ5 | 某能力可见但不可执行时，原因是未发布、无端点、无授权还是版本不兼容？ | `CapabilityPublication`+`EndpointBinding`+`ConsumerBinding`+`ContractVersion` 四态可区分；负例：四态混报 ⇒ FAIL | Integration Contract Owner |
| CQ6 | 某动作由谁确认，产生了什么回执，能否复算当时使用的知识与数据？ | `Action`/`Receipt`/`HumanConfirmation` + planHash 复算；负例：无确认的动作 ⇒ FAIL | GITS Owner |

每个 CQ 的验收物：查询（SPARQL/图查询/API 调用）+ 正例夹具 + 负例夹具 + 预期结果 + 变异复验记录。**仅类数量守恒不能证明语义覆盖**（m-01 计数表仅用于映射完整性，不作质量证据）。

---

## 7. 命名空间 ADR 框架（裁定 1 + M-04，关闭条件 5）

**决议方向**（采纳委员会）：新公共术语采用**机构控制的中立、持久 IRI**；具体根域名由**语义架构 Owner 与基础设施/域名 Owner 联合批准**（本稿不预填域名，`bank.example` 等占位值禁止作为正式值）。

迁移机制（ADR 待正式编号，要点）：

1. 旧 `gits:` IRI 保持只读，状态置 `LEGACY`；
2. 新公共术语发布中立权威 IRI；
3. 逐术语给出 `oldIRI → newIRI` 映射及语义关系：**仅当语义完全相同且身份可互换**时用 `owl:equivalentClass`/`owl:equivalentProperty`；近似映射用 SKOS `closeMatch`/`exactMatch` 或项目自定义映射状态；
4. 兼容窗口（≥1 发布周期，新旧双发布）后退役旧入口；
5. 解析机制：HTTP 可解析（303/内容协商）或受控离线解析 + 内容哈希钉值；
6. 碰撞检查：新旧 IRI 集合交集必须为空（脚本门禁）；
7. 影响面：全部消费方（含 KERT 硬编码 ID、生成目标、plan hash）纳入 Wave 2/3 影响分析（M-05/关闭条件 8）。

---

## 8. 国标 GB/T 48000.3-2026：参照对齐（M-02，关闭条件 6）

**当前唯一可声明口径**（委员会给定文字，本项目逐字采用）：

> 本项目建立企业本体建模内部规范，并参照 GB/T 48000.3-2026 中经适用性评估确认的通用建模要求。

**当前不得声明**：R1~R9 即为 GB/T 48000.3-2026 的完整继承或符合性要求；不得使用「符合性声明/CONFORMANCE」字样。模块内文件更名为 **`REFERENCE-ALIGNMENT.md`（参照适用矩阵）**。

R1~R9 重新定性：SHACL、哈希钉值、场景化 Shape、空转失败、双 Owner 共审、影响面分析等是**本项目的工程控制（部分加严）**，未证明其为国标条款要求；完成正式文本条款级核对前，一律称「内部规则 / 参照对齐」。

**条款级适用性矩阵**（正式文本获取后完成，列为外部依赖）：逐条标注「适用 / 不适用（理由）/ 项目加严 / 证据」。**状态：BLOCKED-ON-EXTERNAL**——正式标准文本获取动作已发起（采购/借阅渠道），本稿不包含任何条款级声称。其余国标族（48000.1/42131/45628/42777/45288.1）关系维持 V1.2 §7.5，同样按「参照对齐」口径表述。

---

## 9. 术语合同字段（委员会 §5.3，全量采纳）

复审后的每个类、属性、词表项至少具备：`termId`、权威 IRI、中文/英文名、精确定义、概念类型（OWL 类/SKOS 概念/Schema 对象）、T-Box Owner、A-Box Owner、ID Owner、来源系统、生命周期、父概念、域/值域、基数、时间语义、来源/证据、隐私等级、兼容性等级、弃用映射、消费方、验证方式、示例与反例。附录 A 矩阵按此字段集展开（机读版随复审包提供）。

---

## 10. 治理与批准状态机（B-03，关闭条件 10）

```
FOR_REVIEW ──委员会评审──▶ DESIGN_APPROVED ──实施──▶ IMPLEMENTED ──独立QA──▶ QA_PASS ──Owner──▶ OWNER_ACTIVATED
                ▲退回 RETURN_TO_HLD（当前所处轮次已完成整改，请求复审）
```

- **委员会只批准**：设计基线 + 实施入口（`DESIGN_APPROVED`）；**不批准、不暗示**实现完成、QA 通过、Owner 激活或生产可用。
- `IMPLEMENTED`：实施门禁（合同先行、IRI 映射集合比对、生成物纪律、消费者影响门禁含 M-05 硬编码处置表）。
- `QA_PASS`：独立 QA（含变异矩阵、CQ 语义验收矩阵全量执行）。
- `OWNER_ACTIVATED`：业务/数据/知识 Owner 分别激活（含 SIM 临时权威声明的退出条件跟踪）。
- 复审决议页按此状态机重写（替代 V1.2 送审包 08 页，文字见整改处置报告附件二）。

---

## 11. 复审前允许工作与实施影响（委员会 §9；M-05/M-10；m-03）

**复审通过前仅允许**（不改变权威制品/运行消费）：① 固定三仓/三制品基线与完整哈希；② 术语、消费者、硬编码与悬空引用清单（消费者影响清单初版见整改处置报告附件三，标注 SYSTEM_OBSERVATION，全量扫描在 Wave -1 完成）；③ 获取正式标准文本并制作适用性矩阵；④ 命名空间 ADR 与新旧 IRI 映射起草；⑤ CQ 与验证夹具设计；⑥ 工作量重估（WBS + 前置依赖 + 缓冲；V1.2 的「7.5 人日」降级为**仅量级提示**，M-10）。

**暂不允许**：拆分权威本体、改变消费者入口、重钉生产契约、把候选公共模块标成 ACTIVE、签发国标符合性声明、关闭 R-6。

**落地计划处置**：《ONTO-SPLIT 落地执行计划 V1.0》已标注暂停；复审通过后按本稿重写 V2.0 版（新增 Wave -1 分析阶段、消费者影响门禁、状态机门禁、Wave 0 输入锚点与失败条件清单——m-03「零风险」表述已撤回，改为低风险）。

**外部依赖登记**：① GB/T 48000.3-2026 正式文本（阻塞关闭条件 6 的最终完成）；② 产品 Owner 对 40 处悬空引用的分类裁定（阻塞关闭条件 4 的最终完成）；③ 语义架构 Owner + 域名 Owner 对中立 IRI 根域的批准（阻塞命名空间 ADR 定稿）；④ 数据 Owner 对客户/法人/集团源系统权威的确认（阻塞附录 A 中 A-Box Owner 列的最终签署）。

---

## 附录 A：逐术语权威矩阵（关闭条件 1 设计层）

> 全量 45 项目标术语（32 基线映射 + 13 净新增）。列：术语｜层｜模型类型｜T-Box Owner｜A-Box Owner｜ID Owner｜基线映射/新增｜归属理由。机读版（CSV，含 §9 全部 22 字段）随复审包提供。

**L3 GITS（19）**：OperatingCase/Claim/Evidence/Evaluation/Action/Receipt/HumanConfirmation/HumanGate/Interaction/InteractionExtension/Opportunity/OpportunitySignal/Commitment/ExternalEvent/KycGapProfile/PolicyRule/AuditTraceEntry/RelationshipReport/Task —— 均为 OWL 类｜T-Box：GITS Owner｜A-Box：GITS 运营库｜ID：GITS｜基线原名映射｜理由：经营过程与受控动作运行语义（委员会认可方向 1）。

**L1 公共（8）**：

| 术语 | 模型类型 | T-Box Owner | A-Box Owner | ID Owner | 映射 | 理由（§2.2 条件） |
|---|---|---|---|---|---|---|
| Party | OWL 类 | 公共语义 Owner | 银行源系统/数据平台 | 源系统 | 新增 | 主体顶层概念，跨域稳定 |
| Organization | OWL 类 | 公共语义 Owner | 同上 | 源系统 | 新增 | 主体分型 |
| LegalEntity | OWL 类 | 公共语义 Owner | 同上 | 源系统 | 基线 LegalEntity | 跨域共享身份（B-02 纠正：实例权威不再写 GITS） |
| CustomerRole | OWL 类 | 公共语义 Owner | EDWCRM 等源系统（SIM 临时模拟权威） | 源系统（经 SourceIdentifier） | 基线 Customer 重构 | 客户=角色而非互斥实体（§3.6） |
| EnterpriseGroup | OWL 类 | 公共语义 Owner | 银行源系统/数据平台 | 源系统 | 基线 CorporateGroup | 同 B-02 纠正 |
| GroupMembership | OWL 类 | 公共语义 Owner | 同上 | 源系统 | 基线 GroupRelationship 重构 | 带来源/有效期/类型 |
| ProductOffering | OWL 类 | 公共语义 Owner | 产品主数据/数据产品（SIM 临时模拟权威） | 产品主数据 Owner | 基线 Product 重构 | 身份/知识内容分离（§3.5） |
| SourceIdentifier | OWL 类 | 公共语义 Owner | 随各源系统 | 源系统 | 新增 | 来源系统+对象类型+原始 ID+生效区间 |

**L2 KERT（12）**：ProductKnowledgeCard、ProductKnowledgeVersion（基线）；KnowledgeMapDefinition、SkillDefinition、AssetDefinition（基线改名）；KnowledgeItem、Segment、KnowledgeSource、ProductInterpretation、RuleBundle、EvidenceBundle、Projection（新增）—— OWL 类｜T-Box：Knowledge/KERT Owner｜A-Box：KERT workspace｜ID：KERT（KM-\*/ASSET-\*/SP-\*/KI-\*/PROD-\* 等）｜理由：知识供给元模型，经版本化契约供 GITS 消费（委员会 §3.3）。

**L4 注册表（6）**：ActivationContract（基线，JSON Schema）、CapabilityPublication（基线重构）、EndpointBinding、ConsumerBinding、ContractVersion（新增）—— Schema 对象｜T-Box：Integration Contract Owner｜记录 Owner：契约注册中心；TaskTypeScheme（基线 TaskType，SKOS 概念体系｜词表 Owner）。

**属性映射（34+1 基线）**：L3 19 条原名保留（4 条 range 改指 CustomerRole）；L2 6 条原名保留 + range 指向 ProductOffering；L1 4 条（memberOfGroup/relatesToGroup/connectsFrom/connectsTo，domain/range 适配 GroupMembership/LegalEntity）；hasTaskType/governedByContract/invokesCapability/referencesAsset/referencesSkill 5 条转 L4 Schema 字段（弃用映射登记）；customerId 退役（由 SourceIdentifier 承载，弃用映射登记）。新增 7 条：L2 的 segmentOf/sourcedFrom/interprets/rulesFor/projectionOf/evidenceOf + describesProduct。

## 附录 B：`Product` 族六列权威表（M-01 整改）

| 列 | ProductOffering（L1） | ProductKnowledgeCard（L2） |
|---|---|---|
| ① 术语定义 Owner | 公共语义 Owner | KERT Owner |
| ② 身份与 ID Owner | 产品主数据 Owner（SIM：临时登记表，Owner 批准） | KERT（PROD-\* 知识资产 ID） |
| ③ 实例事实 Owner | 产品主数据/数据产品（SIM 临时模拟权威，含退出条件） | KERT workspace |
| ④ 发布制品 Owner | 公共语义发布流水线（独立契约库，裁定 3） | KERT 知识发布流水线 |
| ⑤ 消费依赖方向 | 单向：GITS/KERT 钉 L1 发布版本 | 单向：经 describesProduct 引用 L1 |
| ⑥ 变更审批与兼容性 | 双侧 Owner + 公共语义 Owner 共签 | KERT Owner + 兼容性规范 §6.5 |

**结论**：六列无闭环依赖 ⇒ 不构成权威循环；V1.2 论断撤回。`ProductOffering` 入公共层的论证改由 §2.2 四条件承担（跨域稳定含义 / 单域无权独改 / 承载跨系统身份 / 降低耦合），与「循环」无关。

## 附录 C：证据账本纪律（M-08 整改）

全部证据三级标注：**VERIFIED**（作者逐字核验原文，附文件:行与内容哈希）/ **SYSTEM_OBSERVATION**（工具输出的统计/扫描结果，未经独立复现）/ **EXPERT_JUDGMENT**（架构判断）。复审包 05 号文件按此重标：E1/E2/E3 = VERIFIED（逐字摘录，哈希附后）；E4/E5/E6 = SYSTEM_OBSERVATION（勘探统计）；归属判定 = EXPERT_JUDGMENT。基线 32/34/1 计数 = SYSTEM_OBSERVATION（委员会不得引用为独立复核结论）。复审包将附证据账本（每条证据 + 级别 + 输出摘要哈希 + 复现命令），供独立 QA 复现。

## 附录 D：不确定项声明（更新）

1. **国标条款级映射**：未完成（BLOCKED-ON-EXTERNAL，正式文本获取中）；本稿无任何条款级声称。
2. **中立 IRI 根域**：未预填，待语义架构 Owner + 域名 Owner 批准。
3. **45 项目标计数**：设计层核算（EXPERT_JUDGMENT），实施时以 `onto_split_check.py` 集合比对为准。
4. **`AssetDefinition` 归 L2**：项目补充建议（委员会 §5.1 未显式列出 Asset），请复审确认。
5. **L2 新增类名**（KnowledgeItem 等 7 个）：委员会 §5.1 已采纳同名，ID 空间细节待 KERT 既有约定复核。
6. **工期**：V1.2 的 7.5 人日撤回，仅保留量级提示；WBS 重估为复审前允许工作。
