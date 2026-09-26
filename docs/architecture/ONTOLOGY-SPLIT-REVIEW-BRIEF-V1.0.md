# 本体三分拆设计 · 评审简报 V1.0（提交外部架构师审核）

| 项 | 内容 |
|---|---|
| **文档性质** | 评审简报（Review Brief）——用于提交其他智能体/架构师审核，**非最终决策** |
| **日期** | 2026-09-20 |
| **评审对象** | 「本体定义三分拆 + 公共本体模块 + 国标继承 + 改造波次」方案 |
| **前序状态** | ADR-018《公共本体独立化与三层治理》**已作废**（标注 SUPERSEDED），其 §决策（L1/L2/L3 三层 + 临时寄放）被否决 |
| **正式设计稿** | `Leibniz-KERT/docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.0.md`（237 行，本简报为其评审版） |
| **状态** | 待裁定 3 项（见 §6）→ 裁定后冻结并开工 |

> **给评审者的最短上下文**：现有一套共享本体 `gits-core.owl.ttl`（32 类/35 属性，物理放在 GITS 仓，KERT 持只读副本 + sha256 钉值）。该安排存在「宿主＝权威＝消费者三重混同」与「权威循环」两个结构性缺陷。本方案主张：**把 32 类按三条判据拆成三份**——GITS 自持（运营控制面）、KERT 自持（产品与知识供给域）、公共模块（KERT 上的独立目录，未来可剥离）。**请重点审：拆分是否穷尽且互斥、判据是否充分、物理寄放 KERT 的耦合风险、国标参照适用的边界。**

---

## 0. 事实基线（全部实测，非估计）

| 项 | 实测值 | 证据 |
|---|---|---|
| 本体现状 | `gits-core.owl.ttl`：**32 类 / 34 对象属性 / 1 数据属性**；17,273 B；`sha256:705578d6324a…` | `/home/szf/dev/gits-cbanking/specs/semantic/gits-core.owl.ttl`（rdflib 解析） |
| 本体自述范围 | IRI `https://gientech.com/gits/kno/CoreOntology`；comment：*"Operational control-plane classes **plus domain reference classes** declared in semantic contracts (ADR-0001, ADR-0010)"* | 同上（`owl:Ontology` 头） |
| GITS 运行期消费 | `gits.semantic.ontology=specs/semantic/gits-core.owl.ttl` → `JenaOntologyAdapter` → `DefaultActivationPlanner.versions.ontology` | `apps/api/.../KnowledgeArchitectureConfig.java:167-171` |
| KERT 侧消费 | 只读副本 + 钉值：`90_control/ontology/`（4 件 `.ttl` + `PROVENANCE.json`）+ `90_control/schema/ontology_reference.json` | `/home/szf/dev/Leibniz-KERT/...`（`ontology_assets.py` / `ontology_reference.py`） |
| **权威循环（缺陷）** | `gits:Product` 注释自述「产品身份（域引用类）。**权威物理源为 KERT 产品卡** `03_core/*/product-cards/PROD-*.md`」；而 KERT 的本体副本又钉 GITS 的本体 sha256 ⇒ **两仓互为权威** | `gits-core.owl.ttl:127-129`；`GK17-WP1.3-产品关系权威归属裁定-V1.0.md:27-29` |
| **命名空间不一致（缺陷）** | `products.ttl:1` 用 `https://gits.bank.example/ontology/core#`；本体用 `https://gientech.com/gits/kno/` ⇒ `targetedInstances=0`、`vacuous=true` | `FAILURES.md:567-570`（`NAMESPACE_MISMATCH_SILENTLY_GREEN`，状态：待裁定） |
| **权威错位（缺陷）** | GITS 侧 `ProductKnowledgeCard` 实据来自 V021 元数据表，而该表自述「**非产品卡权威源；产品卡权威源在 KERT workspace**」 | `loops/GK17-ontology-unified-map/memory/waves/W3-PLAN.md` |
| GITS「系统既有对象」真身 | `modules/operational-ontology` 是 **Java 领域模型**（约 104 个 record/enum + 53 个仓储接口），**不是 RDF/OWL 本体**；被投影进上述 32 类 | `modules/operational-ontology/`（只读侦察） |

---

## 1. GITS 应该放哪些本体定义（+ 哪些该迁移）

**GITS 自持 = 运营控制面 19 类**（与本体头注释自述范围一致）：

`OperatingCase`、`Claim`、`Evidence`、`Evaluation`、`Action`、`Receipt`、`HumanConfirmation`、`HumanGate`、`Interaction`、`InteractionExtension`、`Opportunity`、`OpportunitySignal`、`Commitment`、`ExternalEvent`、`KycGapProfile`、`PolicyRule`、`AuditTraceEntry`、`RelationshipReport`、`Task`

**+ 19 条属性（随类留下）**：
`authorizedBy`、`belongsToCase`、`commitmentInCase`、`extensionOfInteraction`、`fromInteraction`、`gateInCase`、`gateOfCustomer`、`inCase`、`ofCustomer`、`opportunityForProduct`、`opportunityInCase`、`opportunityOfCustomer`、`producedReceipt`、`profileOfCustomer`、`refersToCustomer`、`reportInCase`、`signalInCase`、`subTaskOf`、`supportedBy`

**该从 GITS「迁出」（迁走不留副本）**：

| 迁出项 | 迁往 | 硬理由 |
|---|---|---|
| `Customer`、`LegalEntity`、`CorporateGroup`、`GroupRelationship` | 公共模块 | 两侧引用；`Customer` 实例权威在 EDWCRM（`CTR-DATA-002`） |
| `Product` | 公共模块 | 该类注释**自述实例权威在 KERT 产品卡**（域引用类模板） |
| `Capability`、`TaskType`、`KnowledgeMap`、`Asset`、`Skill`、`ActivationContract` | 公共模块 | 两侧引用 + SSOT 在 KERT workspace（地图 SSOT 在 KERT = D-2 裁定） |
| `ProductKnowledgeCard`、`ProductKnowledgeVersion` + `cardOfProduct`、`versionOfProduct`、`supersedesVersion`、`requiresProduct`、`complementsProduct`、`mutuallyExclusiveWith` | **KERT 本体** | **权威错位**：GITS 侧实据来自 V021 表，而该表自述权威源在 KERT workspace |
| `customerId`（数据属性） | 公共模块 | 随 `Customer` 走 |

> GITS 侧动作：移出后收敛为 `gits-operational.owl.ttl`（19 类 + 19 属性），并对公共模块 `owl:imports`（**本地副本 + 钉值**，不跨仓直读）。

---

## 2. KERT 应该放哪些本体定义

**KERT 自持 = 产品与知识供给域**

### 2.1 迁入（2 类 + 6 属性，来自 GITS）

| 类/属性 | 中文 | KERT 侧权威源 |
|---|---|---|
| `ProductKnowledgeCard` | 产品知识卡 | `03_core/*/product-cards/PROD-*.md`（13 张，W3.1 实测） |
| `ProductKnowledgeVersion` | 产品知识版本 | 产品卡 front matter `version` + `releases/` |
| `cardOfProduct`/`versionOfProduct`/`supersedesVersion` | 卡→产品 / 版本→产品 / 版本替代 | 同上 |
| `requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith` | 产品关系（**类型权威**） | 产品卡 front matter（实例权威=产品卡，WP1.3 裁定） |

### 2.2 新增（当前本体缺失，KERT 代码/产物已有真实实据）

| 建议类名 | 中文 | 实据 |
|---|---|---|
| `KnowledgeItem` | KI 片段 | `application/customer_knowledge.py`（"KI 片段"） |
| `Segment` | 稳定切片 | `application/extract.py`（`segment_id`） |
| `KnowledgeSource` | 知识来源声明 | `domain/knowledge_source.py`（ID 空间 `KS-*`，已有一整套失败码） |
| `ProductInterpretation` | 产品解读 | `examples/product-recommendation-assets/04_serve/interpretation/PROD-CM-001.json` |
| `RuleBundle` | 规则包 | `application/product_recommendation/eligibility.py` |
| `EvidenceBundle` | 证据包 | `infrastructure/stage_store.py` |
| `Projection` | 供给面投影 | `04_serve/<service_id>/version=<v>/`（`PROJECTION.md` + `*.PROJECTION.json`） |

**建议属性**：`segmentOf`(KI→Segment)、`sourcedFrom`(KI→KnowledgeSource)、`interprets`(Interpretation→Product)、`rulesFor`(RuleBundle→Product)、`projectionOf`(Projection→Service)、`evidenceOf`(EvidenceBundle→…)

> KERT 不再持有 GITS 运营类；跨域引用一律经公共模块锚点。

---

## 3. 公共本地模块（KERT 上、未来可剥离）应该放哪些本体定义

**模块名（建议）**：`public-ontology/`（KERT 仓根，与 `src/` 平级）
**契约号（建议）**：`CTR-SEM-003`（公共本体契约）；`CTR-SEM-002` 收窄为「GITS 运营本体」

### 3.1 归属清单（11 类 + 9 属性 + 1 数据属性）

| # | 类 | 中文 | 判据 | 实例权威（在哪） |
|---|---|---|---|---|
| 1 | `Customer` | 客户 | A+B | EDWCRM `A_ZHCX_CUST_BASE` |
| 2 | `LegalEntity` | 法人/公司 | A | GITS 运营库（`legal_entity`） |
| 3 | `CorporateGroup` | 集团身份 | A | GITS 运营库 |
| 4 | `GroupRelationship` | 集团成员关系 | A | GITS 运营库 |
| 5 | `Product` | 产品身份（**域引用类模板**） | A+B | **KERT 产品卡** `PROD-*` |
| 6 | `TaskType` | 任务类型 | A+C | 地图/激活合同 `entrypoint` 取值 |
| 7 | `KnowledgeMap` | 知识地图（ROOT/DOMAIN/TASK） | A+C | **KERT workspace**（D-2） |
| 8 | `Asset` | 可激活资产 | A+C | `ASSET-*` 登记处 |
| 9 | `Skill` | 可调用技能 | A+C | `SP-*`（KERT `skills/`） |
| 10 | `ActivationContract` | 激活合同 | A+C | `AC-*`（KERT workspace，D-3） |
| 11 | `Capability` | 能力 | A+C | 能力/KM 登记 |

**属性（9）**：`connectsFrom`、`connectsTo`、`memberOfGroup`、`relatesToGroup`、`hasTaskType`、`governedByContract`、`invokesCapability`、`referencesAsset`、`referencesSkill`
**数据属性（1）**：`customerId`

**核算自检**：类 19+2+11 = **32** ✓ ｜ 对象属性 19+6+9 = **34** ✓ ｜ 数据属性 1 ✓（与实测逐项一致）

### 3.2 模块形态（剥离就绪）

```
public-ontology/
  README.md                 # 定位 + 角色声明（GB/T 42131：供应方/集成方/用户）
  MODELING-RULES.md         # 建模规范（GB/T 48000.3-2026 的可执行化，见 §4）
  ONTOLOGY-CONFORMANCE.md   # 国标符合性声明（逐条 + 证据）
  VERSION  CHANGELOG.md
  namespaces.json           # 命名空间与 ID 空间白名单
  src/public-kno.owl.ttl    # 11 类 + 9 属性 + 1 数据属性
  src/public-kno.shacl.ttl  # 对应 NodeShape（每类一份）
  build/export-jsonld.py  Makefile
  PROVENANCE.json           # authorityRepo=Leibniz-KERT + 每文件 sha256
```

**剥离命令**：`git subtree split -P public-ontology -b public-ontology-export`
**剥离约束**：模块**零 KERT 内部依赖**（仅 W3C 栈 + Python 标准库/make）

---

## 4. 如何继承国标（以 GB/T 48000.3-2026 为主）

### 4.1 适用边界（必须先声明，避免过度声称合规）

`GB/T 48000.3-2026《标准数字化 第3部分：本体建模要求》`（2026-01-28 发布，归口 SWG29）面向**标准数字化**中的**标准本体**——其核心实体含 `Standard`、要素、层次、信息单元、制定程序等。
本项目是**企业域本体** ⇒ 采取 **参照适用**：继承 **① 本体建模通用要求 ② 形式化要求 ③ 本体公理与规则 ④ 扩展方式 ⑤ 元数据描述项**；**不继承**「标准实体/要素/层次/制定程序」等标准数字化专有实体。
该边界须**显式写入** `ONTOLOGY-CONFORMANCE.md`。

> ⚠️ **证据强度声明**：标准名称/编号/日期取自全国标准信息公共服务平台元数据与公开摘要；**该标准的条款级内容（IRI 唯一性、序列化格式、SHACL、版本替代等）来自二手来源的转述，待原文核对**后方可升级为条款级引用。

### 4.2 把"标准要求"变成模块内可执行规则

| 标准要求（方向） | 本模块规则 | 现状 |
|---|---|---|
| 唯一标识 / 命名空间 | **R1** `namespaces.json` 白名单 + 唯一 IRI 门禁 | ✗ 现混用两套前缀，须修 |
| 形式化（W3C 栈） | **R2** `owl:Ontology` 头必带 `versionIRI` + `dcterms:hasVersion` + 中文 `label/comment`（含 ID 空间、权威源） | 部分有 |
| 序列化 | **R3** Turtle 为主 + JSON-LD 导出（`make export-jsonld`） | Turtle ✓ / JSON-LD 缺 |
| 约束验证 | **R4** 每类一份 SHACL NodeShape，约束行不合并 | ✓ 32/32、169 条 |
| 本体公理 / 规则 | **R5** `owl:disjointWith`、唯一性、功能性、**版本替代** | 部分有 |
| 扩展方式 | **R6** **只增不改**：公共类不得就地改语义；域侧用 `owl:imports` + `rdfs:subClassOf`；破坏性 ⇒ 新 `versionIRI` | 新增 |
| 元数据描述项 | **R7** label/comment/定义来源/ID 空间/权威源/生命周期 必填 | 部分有 |
| 版本与追踪 | **R8** `VERSION` + `CHANGELOG` + `PROVENANCE.json`（sha256 逐件）+ 裁定留痕 | 新建 |

**门禁化**：`make conformance` 对 R1~R8 逐条给绿/红，产出 `CONFORMANCE-REPORT.md`（含命令与哈希），随模块钉值受漂移保护。

### 4.3 与其它国标的关系

| 标准 | 关系 | 落点 |
|---|---|---|
| GB/T 48000.1-2025《标准数字化 第1部分：通用指南》 | 顶层原则 | README |
| GB/T 42131-2022《人工智能 知识图谱技术框架》（2022-12-30 发布 / 2023-07-01 实施） | **角色划分**（供应方/集成方/用户） | 公共模块=供应方；GITS/KERT=集成方；业务=用户 |
| GB/T 45628-2025《人工智能 知识图谱 知识交换协议》（2025-04-25 发布） | 知识描述规则、**最小知识片段**、基于文件/消息交换 | 模块导出格式 + KI 片段契约 |
| GB/T 42777-2023《基于文本数据的金融风险防控 知识图谱构建技术框架指南》（2023-08-06 实施，人民银行归口） | 七层架构（数据源/抽取加工/知识管理/挖掘分析/服务交互） | 分层映射表 |
| GB/T 45288.1-2025《人工智能 大模型 第1部分：通用要求》（2025-02-28 发布） | 消费侧（非本体模块） | KERT 大模型侧合规面 |
| 在研：《人工智能 知识图谱与大规模预训练模型集成 第1部分：技术框架》（2026-08-07 登记） | 跟踪 | 影响 KERT 主线 |

---

## 5. 现在该如何改造（5 波）

| Wave | 动作 | 时长 |
|---|---|---|
| **0 冻结** | 记基线 `sha256:705578d6324a…`；导出三分表；**不删任何文件** | 0.5d |
| **1 建模块** | KERT 建 `public-ontology/` 骨架；写 `MODELING-RULES.md` / `ONTOLOGY-CONFORMANCE.md` / `namespaces.json` / `VERSION` / `PROVENANCE.json` | 1d |
| **2 拆分** | 从 `gits-core.owl.ttl` 拆出 11 / 2 / 19 类 → 三份 TTL；SHACL 同步三分（32 → 11/2/19）；**IRI 保持不变** | 2d |
| **3 换消费 + 修命名空间** | KERT：`90_control/ontology/` 改放「公共模块副本 + KERT 本体」，`ontology_reference.json` 改 `authorityRepo: Leibniz-KERT`；GITS：`gits-core.owl.ttl` → `gits-operational.owl.ttl` + `owl:imports` 公共模块（本地副本 + 钉值），`KnowledgeArchitectureConfig:167` 改指向，`CONTRACT_INDEX` 拆条（`CTR-SEM-002` 收窄 + 新增 `CTR-SEM-003`）；**`products.ttl` 前缀对齐** ⇒ 解 `vacuous`；收口 KERT 三处「依据 D3-A」表述（`ontology_reference.py:1`、`knowledge_map.py:30`、`knowledge_source.py:64`） | 2d |
| **4 门禁** | G1~G8 脚本化 + CI；跨域引用白名单（GITS 只能引用公共模块类）；`vacuous=true` 由"静默绿"改「需显式标注」 | 1.5d |
| **5 剥离预案** | `git subtree split` 命令 + 零依赖校验 | 0.5d |

**验收（每波）**：① 模块齐备且 `make conformance` 可跑；② 三份 TTL 计数=11+2+19 / 9+6+19，**无 IRI 变更**（集合比对相等）；③ 双侧启动成功 + 漂移用例绿 + `vacuous` 消失；④ G1~G8 全绿 + 符合性报告钉值；⑤ 模块可独立打包（无 KERT import）。

### ⚠️ 必须预期的代价（对上一版的诚实修正）

**拆分必然改变文件内容 ⇒ 哈希必变 ⇒ 两侧钉值都要重钉**。这不是"内容不变"的搬迁。**因此建议把「命名空间修复」并入本次重钉一并完成**，避免二次重钉与二次门禁变更。

---

## 6. 待裁定（决定后冻结本设计）

| # | 待裁定 | 本方案主张 |
|---|---|---|
| 1 | **命名空间**：沿用 `https://gientech.com/gits/kno/` 还是中立前缀 | 建议**先沿用**（零 IRI 改动，把中立化留作独立第二波） |
| 2 | **`Product` 类归属**：公共模块 还是 KERT 本体 | **公共模块**（判据 A 两侧引用 + 判据 B 实例权威在 KERT） |
| 3 | **公共模块交付形态**：repo 内目录 还是 直接独立仓 | **repo 内目录**（跨仓引用与钉值成本更低，且保留 `subtree split` 出口） |

---

## 7. 给评审者的明确问题清单

1. **判据是否充分**：A（跨域共享）/B（域引用类）/C（SSOT 在 KERT）三条判据能否覆盖全部 32 类？是否存在"两边都不认"或"两边都要"的类别？
2. **拆分是否穷尽且互斥**：19 + 2 + 11 = 32 的划分是否有错判？（尤其 `Task` 留 GITS、而 `TaskType` 进公共，是否自洽？）
3. **`Product` 的归属**：公共模块 vs KERT 本体，哪个更能避免第二次「权威循环」？
4. **任务/规格/知识族**（`TaskType`/`KnowledgeMap`/`Asset`/`Skill`/`ActivationContract`/`Capability`）进公共模块是否恰当？是否存在"公共模块事实上变成 KERT 私有扩展"的风险？
5. **物理寄放 KERT 的耦合风险**：如何保证公共模块不被 KERT 私有约定污染（命名空间、ID 空间、生命周期）？
6. **国标参照适用的边界声明**是否恰当？"不继承标准本体专有实体"是否会被判定为规避？
7. **改造波次顺序**：Wave 2 拆分与 Wave 3 重钉是否应合并为一次变更？重钉对 GITS `JenaOntologyAdapter` 与 KERT 钉值校验的冲击面有多大？
8. **遗漏项**：是否还应包含 `PREFIX`/`owl:imports` 的版本约束、SHACL 与本体的一致性门禁、以及「公共本体变更的影响面自动分析」？
9. **W3 数据缺陷**：产品关系实例当前 **0 条**（40 处悬空引用待产品 Owner 裁定），是否会影响 KERT 本体的 `requiresProduct` 等属性落地验证？

---

## 附 A｜证据索引（可复核路径）

| 用途 | 路径 |
|---|---|
| 本体权威源 | `/home/szf/dev/gits-cbanking/specs/semantic/gits-core.owl.ttl`（+ `gits-core.linkml.yaml`） |
| 契约登记 | `specs/CONTRACT_INDEX.yaml`（CTR-SEM-001/002；`:646-650` `public_semantic_core` 消费者） |
| 生成物（禁手编） | `generated/semantic/gits-core.shacl.ttl`（由 `scripts/contract_pipeline.py` 生成） |
| GITS 运行期消费 | `apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java:167-171` |
| GITS 领域模型（非本体） | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/` |
| KERT 资产副本 + 溯源 | `Leibniz-KERT/examples/bank-front-knowledge-maps/90_control/ontology/`（4 `.ttl` + `PROVENANCE.json`） |
| KERT 消费侧声明 | 同上 `90_control/schema/ontology_reference.json` |
| 权威循环裁定 | `loops/GK17-ontology-unified-map/...` + `docs/architecture/GK17-WP1.3-产品关系权威归属裁定-V1.0.md` |
| 命名空间缺陷 | `scripts/gk17_triple_consistency_check.py:557-562`；`loops/GK17-.../FAILURES.md:567-570` |
| W3 投影与权威源 | `loops/GK17-ontology-unified-map/memory/waves/W3-PLAN.md`、`W3-ITER.md` |
| 总契约（公共语义核心） | `docs/dd/gk-ke-contract/GITS-KERT_知识工程体系_项目总契约_V1.0.md`（`:5`、`:23`、`:113-119`） |
| 设计稿（正式） | `Leibniz-KERT/docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.0.md` |
| 已作废 ADR | `Leibniz-KERT/docs/adr/ADR-018-public-ontology-independence-and-governance.md`（SUPERSEDED） |

## 附 B｜不确定项与声明

1. **国标条款细节**：本文所列"IRI 唯一 / 序列化 / SHACL / 版本替代"等为公开摘要与二手转述，**待 GB/T 48000.3-2026 原文核对**；标准编号与发布/实施日期来自全国标准信息公共服务平台。
2. **`gits:Product` 的注释**为 GITS 本体原文，代表**声明层面的自我定位**；其与 KERT 产品卡的实例级一致性**未在本简报中做代码级验证**。
3. **KERT 侧新增类名**（`KnowledgeItem`/`Segment`/…）为**建议命名**，实据已在 KERT 代码中定位，但命名需与 KERT 既有 ID 空间约定复核。
4. 本简报的"该迁移"判定基于**权威源归属**，未包含工作量与工期承诺（时长仅为量级估算）。
