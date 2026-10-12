# ONTO1｜`CTR-SEM-*` 拆条登记草案（DRAFT）

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT（草稿）**——**只出草案，不落地**。候任 Integration Contract Owner 任职技术准备产出 |
| 状态 | `DRAFT` / `NOT_LANDED`；**未写入** `specs/CONTRACT_INDEX.yaml` |
| 依据 | 执行计划 §5.1；设计 §4.1~§4.5；ADR §5.1/§5.2/§5.4；复审包 07 号（兼容性）、06 号（五态） |
| 当前门禁 | `RETURN_TO_HLD` 有效：`CONTRACT_INDEX` 变更属 Wave 2，**本轮禁止** |

> **红线声明**
> 1. 本轮**未改动** `specs/CONTRACT_INDEX.yaml`、**未改动** `generated/`、**未执行** `make generate`；
> 2. 本草案中所有 `authority_source` / `generated` 路径均为**候选**；标记 `⟨待定⟩` 者**不得**直接落地；
> 3. 不标 `ACTIVE`；不代签；不把候选登记当作已批准。

---

## 0. 为什么拆条不是"改个 ID"

`scripts/contract_pipeline.py` 的硬约束（回源，逐条带行号）决定了拆条的正确做法：

| # | 约束 | 回源 | 对拆条的后果 |
|---|---|---|---|
| P-1 | `kind` 必须属于受支持集合，否则构建报错 | `scripts/contract_pipeline.py:249` | 新登记**不能**自造 kind；SKOS **无对应 kind**（见 §4 风险 R-1） |
| P-2 | 每条合同必须有 `kind`/`authority_source`/`owner`/`compatibility`/`consumers`/`generated` 六键，且 `owner`、`consumers` 非空 | `:199-204` | 新登记必须写全；owner 须是**已任命**角色 |
| P-3 | `authority_source` 必须真实存在，且**拒绝占位值** | `:215-217` | L1 若指向独立契约库（跨仓/跨目录）需先确认路径可达 |
| P-4 | `json_schema` 等 kind **恰好 1 个** generated 目标 | `:253-255` | 新目标不得与既有目标同名 |
| P-5 | `linkml_subset` **恰好 2 个**（JSON Schema + SHACL） | `:263-269` | L1 若用此 kind，源必须是 LinkML 形态 |
| P-6 | `turtle` kind **只校验、不产出** generated 制品 | `:242-243`（校验）+ `:252-275`（无 turtle 分支） | ⚠️ `CTR-SEM-002` 的 `generated: []` 是**正确**的，不是遗漏；给 turtle 声明目标会造成 `make check` 漂移 |
| P-7 | `make check` 比对 missing/extra/changed 三态漂移；`generated/` 必须只读 | `:325-339` | **每个新 generated 目标必须唯一归属**（GK-KE 已有覆盖既有制品的踩坑） |

**结论**：拆条的真正难点不是 ID，而是 **kind 选择 + generated 目标唯一性 + 跨仓 authority_source 可达性**。以下草案逐条标注。

---

## 1. 现状登记（回源）

| ID | kind | authority_source | owner | compatibility | consumers | generated | 行号 |
|---|---|---|---|---|---|---|---|
| `CTR-SEM-001` | `linkml_subset` | `specs/semantic/gits-core.linkml.yaml` | `semantic_architecture_owner` | `explicit_migration` | operational_ontology, semantic_runtime, context_evidence | `generated/semantic/gits-core.schema.json`、`generated/semantic/gits-core.shacl.ttl` | `CONTRACT_INDEX.yaml:35` |
| `CTR-SEM-002` | `turtle` | `specs/semantic/gits-core.owl.ttl` | `semantic_architecture_owner` | `explicit_migration` | `semantic_runtime` | `[]` | `CONTRACT_INDEX.yaml:51` |

**既有产物现状**：`generated/semantic/` 下仅 `gits-core.schema.json` + `gits-core.shacl.ttl` 两个文件。

**契约库总规模**：62 条（`CONTRACT_INDEX.yaml`）。**新增 3 条 + 收窄 1 条**是本次拆条的全部动作；不得顺手改动其他条目。

---

## 2. `CTR-SEM-003`（L1 企业公共业务语义核心）草案

| 字段 | 值 | 说明 |
|---|---|---|
| `id` | `CTR-SEM-003` | 由 TL 在 Wave 2 分配确认 |
| `kind` | **⟨待裁定 K-1⟩** `turtle` 或 `linkml_subset` | 见下方选项分析 |
| `authority_source` | **⟨待定⟩ `specs/semantic/gits-public-core.owl.ttl`**（候选） | 真实位置取决于裁定 3 独立语义契约库的仓与路径（Wave 1 产出）。**若独立库尚未设立，L1 源只能以"钉定副本"形态存在于 GITS 仓**，此时必须显式声明这是副本而非权威 |
| `owner` | `public_semantics_owner` | **该角色当前 `UNASSIGNED_GAP`**（`memory/ROLE_BOARD.yaml:30`）⇒ 登记前必须先任命，否则 `owner` 字段无合法取值 |
| `compatibility` | `explicit_migration` | 与 `CTR-SEM-001/002` 保持一致（本次为重构 + 改名 + 转制品，07 号矩阵定级 `major`） |
| `consumers` | `["operational_ontology", "semantic_runtime", "kert_knowledge_runtime"]`（候选） | KERT 是否作为消费者需 KERT 维护方确认（本环境 KERT 只读） |
| `generated` | 见 K-1 选项 | — |
| 覆盖范围 | L1 8 类：`Party`/`Organization`/`LegalEntity`/`CustomerRole`/`EnterpriseGroup`/`GroupMembership`/`ProductOffering`/`SourceIdentifier` + 4 属性（`memberOfGroup`/`relatesToGroup`/`connectsFrom`/`connectsTo`） | 设计 §4.2、§4.5 |
| 映射状态 | 新增 3、重构 4（`REMODELED`）、原名迁移 1（`RETAINED`） | ADR §5.1 三分法；**重构项禁止 `equivalentClass`** |

### 2.1 K-1 选项分析（kind 与 generated）

| 选项 | kind | generated 目标 | 优点 | 缺点 | 建议 |
|---|---|---|---|---|---|
| K-1a | `turtle` | `[]` | 与 `CTR-SEM-002` 同型、零漂移风险；OWL TTL 是 L1 的天然权威形态 | **不产出** SHACL/JSON Schema（P-6）⇒ L1 的验证制品无生成物 | 若 L1 只需 OWL + 外部 SHACL，选此项 |
| K-1b | `linkml_subset` | `generated/semantic/gits-public-core.schema.json` + `generated/semantic/gits-public-core.shacl.ttl` | 有 SHACL 生成物（设计 §4.1 要求 L1 出 OWL/SHACL） | 需要把 OWL 语义**重述为 LinkML 源**，存在"两个源描述同一语义"的漂移风险 | 若坚持 SHACL 由源模型生成（计划 §5.5"SHACL 由源模型生成，禁手改"），选此项 |
| K-1c | 新增 kind `owl_subset`（需改 `contract_pipeline.py`） | 待定 | 可从 OWL 直接生成 SHACL | **改动构建工具**，超出本 Loop scope（`scripts/onto1_*` 之外） | 不建议，除非 Owner 明确授权 |

**本草案倾向 K-1b**（理由：设计 §4.1 要求 L1 出 OWL/SHACL，且计划 §5.5 要求 SHACL 由源模型生成）；但**目标路径必须与 `CTR-SEM-001` 的既有目标不同名**（P-4/P-7）。

---

## 3. `CTR-SEM-004`（L2 KERT 知识供给元模型）草案

| 字段 | 值 | 说明 |
|---|---|---|
| `id` | `CTR-SEM-004` | — |
| `kind` | `turtle`（候选） | L2 制品为 OWL/SHACL |
| `authority_source` | **⟨阻塞⟩ KERT 仓路径**（本环境只读，无法在此确认） | ⚠️ 见风险 R-2 |
| `owner` | `knowledge_owner_kert`（`memory/ROLE_BOARD.yaml:45`，状态 `EXTERNAL`） | 需 KERT 维护方确认协作接口 |
| `compatibility` | `explicit_migration` | L2 有 3 类改名 + 6 属性改名/新增 |
| `consumers` | `["gits_operational_ontology"]`（候选，方向单向） | 设计 §2.1 ⑤ 消费依赖方向必须单向（KERT 钉 GITS 制品；反向不成立） |
| `generated` | `[]`（若 kind=`turtle`） | — |
| 覆盖范围 | L2 12 类 + 13 属性（含新增 `describesProduct`） | 设计 §4.3 |

### 3.1 R-2（阻塞）：**跨仓 `authority_source` 没有登记格式**

`CONTRACT_INDEX.yaml` 的 `authority_source` 目前**全部是 GITS 仓内相对路径**（回源：62 条逐条检查，无例外）。L2 的权威源在 `Leibniz-KERT` 仓，因此：

| 选项 | 做法 | 后果 |
|---|---|---|
| R-2a | GITS 仓内放**钉定副本**（versionIRI + 内容哈希），`authority_source` 指向副本 | 与设计 §1"跨仓不运行时直读"一致；但**副本 ≠ 权威**，须显式声明 `hostingRepo` vs `authorityEntity`（设计 m-02 双字段） |
| R-2b | 扩展 `authority_source` 支持跨仓引用（如 `kert:src/kert/...`） | 需改 `contract_pipeline.py`（P-3 路径校验逻辑）+ 改登记 Schema ⇒ **超出 scope** |
| R-2c | **不登记** L2（L2 由 KERT 侧自行登记其制品） | 最诚实，但 L4 的 `ContractVersion` 会失去 L2 的版本锚点 |

**建议**：R-2a（钉定副本 + 双字段声明），并**明确副本的更新责任与刷新门禁**；R-2b 作为独立议题提交 Owner（需改构建工具）。

---

## 4. `CTR-SEM-005`（L4 集成契约注册表 Schema / SKOS）草案

| 字段 | 值 | 说明 |
|---|---|---|
| `id` | `CTR-SEM-005` | — |
| `kind` | **⟨阻塞 R-1⟩** 需拆成多条 | 5 个 JSON Schema + 1 个 SKOS，**无法用一条合同承载**（P-4：`json_schema` 恰好 1 个 generated 目标） |
| `authority_source` | **⟨待裁定 K-6⟩** 见 §4.2 | 与既有 `CTR-ACTIVATION-001` / `CTR-GKKE-017` 重叠 |
| `owner` | `integration_contract_owner` | **当前 `UNASSIGNED_GAP`**（`memory/ROLE_BOARD.yaml:35`） |
| `compatibility` | 待逐条判定 | 见 §4.3 |
| `consumers` | 双向：GITS 侧 + KERT 侧 + 数据平台 | 三方评审规则 §4 |

### 4.1 R-1（结构性问题）：一条 `CTR-SEM-005` 装不下 6 个不同 kind 的制品

设计 §4.4 把 L4 定为"6 项（非 OWL）"。但 `json_schema` kind **只允许 1 个 generated 目标**（`:253-255`），SKOS **没有 kind**（`:249` 受支持集合不含 `skos`）。因此"一条 `CTR-SEM-005`"在**当前构建工具下不可实现**。

**候选方案**：

| 方案 | 拆法 | 优点 | 缺点 |
|---|---|---|---|
| S-1（推荐） | 每条 Schema 一个合同（如 `CTR-SEM-005`~`CTR-SEM-009`），SKOS 单列 | 符合 P-4；逐条可独立版本化与兼容判定 | 合同数量 +5；须一次申请号段 |
| S-2 | 一条合同 + 多目标 | 合同少 | **违反 P-4**，构建直接报错 |
| S-3 | 复用既有 `CTR-GKKE-0xx` 号段扩字段 | 不新增号段 | 混淆 L4 治理面与 gk-ke 交换面（见 §4.2） |

**建议 S-1**，并把号段申请作为 Owner 决定项（因涉及合同编号分配权）。

### 4.2 K-6（重叠）：`CTR-SEM-005` 与既有登记的归并（回源见 L4 设计 §8）

| L4 对象 | 既有登记 | 候选处置 |
|---|---|---|
| `ActivationContract` | `CTR-ACTIVATION-001`（`CONTRACT_INDEX.yaml:307`） | **不新建**（扩既有） |
| `CapabilityPublication` | `CTR-GKKE-017`（`CONTRACT_INDEX.yaml:943`） | 扩既有 **或** 新登记 + 旧条标 `superseded`（须 Owner 裁定） |
| `EndpointBinding` | 无 | 新建（真缺口） |
| `ConsumerBinding` | 无（仅有未登记的 `ConsumerObligations.json`） | 新建 |
| `ContractVersion` | 无（仅各条 `compatibility` 单值） | 新建 |
| `TaskTypeScheme` | 无 | 新建（SKOS） |

**若不先裁定 K-6 就登记，将出现"同一语义两处登记"**，这本身就是合同漂移，且与 `AGENTS.md`"`specs/CONTRACT_INDEX.yaml` 是唯一合同登记处"的原则冲突。

### 4.3 R-3：SKOS 无 kind（需 Owner 决策）

| 选项 | 做法 | 代价 |
|---|---|---|
| R-3a | 用 `turtle` kind 承载 SKOS（TTL 可行） | 有校验、**无 generated**（P-6），词表无规范化产物 |
| R-3b | 新增 kind `skos`（改 `contract_pipeline.py` + 校验器） | 改构建工具，需独立派工与门禁；超出本 Loop scope |
| R-3c | 词表不由 `CONTRACT_INDEX` 承载，改由契约库自管 | 破坏"唯一登记处"原则 |

**建议 R-3b**，但**列为独立工作包**（不塞进 Wave 2 的拆条动作），先裁定再派工。

---

## 5. 收窄 `CTR-SEM-002`（L3 GITS 经营运行本体）草案

| 字段 | 现状 | 收窄后（草案） | 变化说明 |
|---|---|---|---|
| `id` | `CTR-SEM-002` | `CTR-SEM-002`（**不变**） | 收窄 ≠ 换号 |
| `kind` | `turtle` | `turtle`（不变） | — |
| `authority_source` | `specs/semantic/gits-core.owl.ttl` | **`specs/semantic/gits-operational.owl.ttl`**（候选，随 Wave 3 改名） | 计划 §6：GITS 侧 `gits-core.owl.ttl` → `gits-operational.owl.ttl` + `owl:imports` L1 |
| `owner` | `semantic_architecture_owner` | **⟨待裁定 K-2⟩** 是否改为 `gits_owner` | 设计 §3.1 规定 L3 定义 Owner = Business Process Owner / GITS Owner；但合同登记 owner 与本体 Owner 是否同一角色，须裁定 |
| `compatibility` | `explicit_migration` | `explicit_migration`（不变） | 改名 + range 改指 = `major`（07 号矩阵） |
| `consumers` | `["semantic_runtime"]` | `["semantic_runtime", "operational_ontology"]`（候选） | ⚠️ 扩 consumers 是**声明性变更**，须逐条回源确认（见消费者扫描义务表） |
| `generated` | `[]` | `[]`（**保持为空**） | P-6：turtle 不产出制品。**不得**因"想加 SHACL"而误加目标 |
| 覆盖范围 | 基线 32 类全集 | **L3 19 类 + 19 属性**（4 条 range 改指 L1 `CustomerRole`） | 设计 §4.1、§4.5 |

### 5.1 收窄的**连带必要动作**（不得漏）

收窄 `CTR-SEM-002` 只覆盖 OWL TTL；但基线本体在**两处**同时存在，且都是跨层混合：

| 制品 | 现状类数 | 层分布（回源） | 是否也需要拆条 |
|---|---|---|---|
| `specs/semantic/gits-core.owl.ttl`（`CTR-SEM-002`） | 32 类 | L1+L2+L3+L4 **混合**（`gits:TaskType` 在 `:65`、`gits:hasTaskType` 在 `:81`） | ✅ 本文 §5 |
| `specs/semantic/gits-core.linkml.yaml`（`CTR-SEM-001`） | **32 类**（回源：文件 `classes` 块 `:11`，含 `OperatingCase`(L3) `:12` 与 `Customer`(L1) `:25`） | L1+L2+L3+L4 **混合** | ⚠️ **同等需要**，但**不在本轮派工范围** |

`specs/semantic/gits-core.linkml.yaml` 的 32 类清单（回源实测）：
`Action, ActivationContract, Asset, AuditTraceEntry, Capability, Claim, Commitment, CorporateGroup, Customer, Evaluation, Evidence, ExternalEvent, GroupRelationship, HumanConfirmation, HumanGate, Interaction, InteractionExtension, KnowledgeMap, KycGapProfile, LegalEntity, OperatingCase, Opportunity, OpportunitySignal, PolicyRule, Product, ProductKnowledgeCard, ProductKnowledgeVersion, Receipt, RelationshipReport, Skill, Task, TaskType`

其中 `ActivationContract` / `Capability` / `TaskType`（L4）、`Asset` / `KnowledgeMap` / `Skill` / `ProductKnowledgeCard` / `ProductKnowledgeVersion`（L2）、`Customer` / `CorporateGroup` / `GroupRelationship` / `LegalEntity` / `Product`（L1）**均混在 `CTR-SEM-001` 内**。

> **结论（本草案最重要的越界提示）**：执行计划 §5.1 只写了"新增 003/004/005 + 收窄 002"，**未提 `CTR-SEM-001`**。若只按字面执行，会出现"OWL 侧已分层、LinkML 侧仍混层"的**半拆分状态**，而 `CTR-SEM-001` 正是 `CTR-SEM-003/004/005` 的**同源制品**（同一批 32 类）。
> **建议**：把 `CTR-SEM-001` 的拆条**登记为 Wave 2 的追加条目**（`CTR-SEM-010`~? 或与 003/004/005 同批），并请 TL/Owner 裁定；**不得**在未裁定前只改 002。

---

## 6. 拆条后的登记全景（草案，**未落地**）

| ID | 层 | kind（候选） | authority_source（候选） | owner（候选） | generated（候选） | 状态 |
|---|---|---|---|---|---|---|
| `CTR-SEM-001` | **跨层（应拆）** | `linkml_subset` | `specs/semantic/gits-core.linkml.yaml` | `semantic_architecture_owner` | `generated/semantic/gits-core.{schema.json,shacl.ttl}` | ⚠️ 追加待裁定 |
| `CTR-SEM-002` | L3 | `turtle` | `specs/semantic/gits-operational.owl.ttl` ⟨待定⟩ | ⟨K-2⟩ | `[]` | 收窄草案 |
| `CTR-SEM-003` | L1 | ⟨K-1⟩ | ⟨独立契约库 或 钉定副本⟩ | `public_semantics_owner` ⟨未任命⟩ | ⟨K-1⟩ | 草案 |
| `CTR-SEM-004` | L2 | `turtle` | ⟨KERT 仓 / 钉定副本 R-2a⟩ | `knowledge_owner_kert` | `[]` | 草案 |
| `CTR-SEM-005…009` | L4 | `json_schema` × 5 | `specs/…/schemas/*.schema.json` ⟨K-6 归并⟩ | `integration_contract_owner` ⟨未任命⟩ | 各 1 个独立目标 | 草案（S-1） |
| `CTR-SEM-0??` | L4 词表 | ⟨R-3⟩ | SKOS 源 | 词表 Owner ⟨T-4⟩ | ⟨R-3⟩ | 草案 |

**登记顺序（强制）**：`DESIGN_APPROVED` → 角色任命（Owner 合法取值）→ K-1/K-2/K-6/R-2/R-3 裁定 → 写 `CONTRACT_INDEX` → **一次** `make generate` → `make check` 绿 → 记证据。
**禁止**：先写实现再补登记（API First / 合同先行）；分批 `make generate` 造成中间态漂移。

---

## 7. 裁清单（提交 Owner / TL）

| # | 待裁定 | 影响 | 选项 |
|---|---|---|---|
| K-1 | L1 的 kind 与 generated | 决定 L1 是否有 SHACL 生成物 | K-1a / **K-1b（倾向）** / K-1c |
| K-2 | 收窄后 `CTR-SEM-002.owner` 是否改 `gits_owner` | 责任归属 | 保持 / 改 |
| K-3 | 是否新增 `CTR-SEM-010+` 处理 `CTR-SEM-001` 拆条 | **防半拆分**（§5.1） | 追加 / 延后（须具名） |
| K-4 | `consumers` 扩容是否需逐条回源 | 声明性变更的证明责任 | 需（与 WI-A2 口径一致） |
| K-5 | L4 号段与拆分数（S-1 需 5~6 个号） | 编号分配权 | Owner |
| K-6 | L4 与 `CTR-ACTIVATION-001`/`CTR-GKKE-017` 的归并 | 防双处登记 | 扩既有 / 新建+superseded / 分工 |
| R-2 | 跨仓 `authority_source` 形态 | L2 是否可登记 | R-2a（倾向）/ R-2b / R-2c |
| R-3 | SKOS 是否有 `kind` | 词表可否进登记 | R-3a / **R-3b（倾向）** / R-3c |

---

## 8. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|---|---|---|---|
| DRAFT-v0.1 | 2026-09-20 | 初稿（仅草案，未落地） | 候任 Integration Contract Owner（AI 起草） |

> 草稿，签字权在人类 Owner。
