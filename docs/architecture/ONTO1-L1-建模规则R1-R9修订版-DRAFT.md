# ONTO1｜L1 建模规则 R1~R9 修订版（内部规则 / 参照对齐）— DRAFT

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT 草案**——候任公共语义 Owner 任职技术准备产出；**待 Owner 签署** |
| 名义 | **本项目内部工程规则 + 参照对齐（reference alignment）**。本文件**不是**符合性声明，**不**声称 R1~R9 即任何标准条款要求 |
| 状态 | `DRAFT / 待 Owner 签署`；**不得**标 `DESIGN_APPROVED` / `ACTIVE` / `FROZEN` |
| 目标载体 | 独立语义契约库 `MODELING-RULES.md`（本稿为其内容草案，见 `ONTO1-Wave1独立语义契约库五条件落地方案-DRAFT.md` §3） |
| 修订对象 | 设计 V1.2 §7.3（`docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md:291-303`）中的 R1~R9 |
| 修订依据 | 设计 V2.0 §5.5 / §6.2 / §6.3 / §6.4 / §6.5 / §8（M-02、M-09、M-07、委员会 §5.5/§6.2/§6.3）；复审包 `07-兼容性矩阵-major-minor-patch.md`、`06-验证状态模型与状态跃迁表.md` |
| 执行计划 | `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §4（WI-1-2 库骨架）、§7（Wave 4 门禁） |

---

## 0. 名义与禁用词（强制，先于规则正文）

### 0.1 唯一可声明口径（逐字采用设计 §8，不得改写、不得扩写）

> 本项目建立企业本体建模内部规范，并参照 GB/T 48000.3-2026 中经适用性评估确认的通用建模要求。

### 0.2 禁用清单（本文件及其派生产物一律适用）

| # | 禁用 | 说明 |
|---|---|---|
| D-1 | `CONFORMANCE` 字样（文件名、标题、报告名、变量名、CI job 名） | 目标文件名为 **`REFERENCE-ALIGNMENT.md`** / 报告名 **`REFERENCE-ALIGNMENT-REPORT.md`** |
| D-2 | 「符合性 / 合规性 / 达标 / 继承标准要求」等表述 | 一律改为「内部规则 / 参照对齐 / 参照适用评估」 |
| D-3 | 「R1~R9 = 国标要求」「R1~R9 即 GB/T 48000.3-2026 的继承」 | 见 D-2；条款级关系须待正式文本到手后由 T2~T4 单独门禁判定 |
| D-4 | 条款号引用（未获正式文本前） | 矩阵空表可预留栏位，**不得**填条款号与判定 |
| D-5 | 把 R1~R9 写入设计基线或合同 | 条款对齐（D1）不阻塞主链路 |

### 0.3 命令名与文件名的落差（待裁定，见 §6 Q-1）

执行计划 §7 使用命令名 `make conformance`，同时要求「输出文件一律用 REFERENCE-ALIGNMENT/内部规则名义」。本稿的处理：**命令名沿用计划不变**，但其产出一律为 `REFERENCE-ALIGNMENT-REPORT.md`；命令名是否改为 `make reference-alignment` 需 Owner 裁定（避免语义漂移），本稿不预判。

---

## 1. 修订后规则正文（R1~R9）

> 每条含：**规则文本（可执行）**｜**门禁判据**｜**失败具名码（fail-closed）**｜**适用层**｜**现状**｜**责任 Owner**｜**相对 V1.2 的修订**。
> 术语：`L1` 公共核心 / `L2` KERT 元模型 / `L3` GITS 运行本体 / `L4` 注册表与词表。

### R1｜命名空间与 IRI 唯一性（白名单）

- **规则文本**：所有 L1/L2/L3/L4 术语的 IRI 必须落在 `namespaces.json` 登记的前缀白名单内；同一短前缀不得指向两个命名空间；术语 IRI 唯一（集合内无重复）；IRI 不得含时间戳、构建号、会话 ID（禁动态 IRI）；保留段 `LEGACY/`、`_meta/` 不得用作术语短名。**D3 未签前，L1 IRI 一律为 `PENDING:{NS-L1}#<短名>` 形式，且 `namespaces.json` 的根域字段保持空值。**
- **门禁判据**：前缀白名单校验（0 违规）+ IRI 集合唯一性 + 前缀→命名空间 1:1 映射 + `PENDING:` 占位不得进入发布制品（发布门禁拦）。
- **失败具名码**：`ONTOLOGY_NS_VIOLATION`（白名单外）、`ONTOLOGY_PREFIX_COLLISION`（同前缀多命名空间，现成反例 `specs/knowledge-architecture/instances/product/products.ttl:1`）、`ONTOLOGY_PLACEHOLDER_IN_RELEASE`（占位根域进制品）、`ONTOLOGY_DYNAMIC_IRI`。
- **续任细节**：ADR-ONTO1 草案 §5.4 的 C-1（集合互斥）/C-2（前缀唯一）为本条子检查，脚本归属 Integration Contract Owner（待任命）。
- **适用层**：全层。
- **现状**：✗ 已知一处前缀错配（`products.ttl:1` 用 `gits:` 指向 `https://gits.bank.example/ontology/core#`，本体前缀为 `https://gientech.com/gits/kno/`）。
- **责任 Owner**：公共语义 Owner（L1）+ Integration Contract Owner（L2~L4）+ 域名 Owner（根域）。
- **相对 V1.2 修订**：**新增** `PENDING:` 占位纪律、前缀碰撞检查、动态 IRI 禁止（V1.2 仅「白名单 + 唯一 IRI 检查」）。

### R2｜本体头元数据

- **规则文本**：每份本体文件的 `owl:Ontology` 头必须带 `owl:versionIRI`、`dcterms:hasVersion`、`rdfs:label`、`rdfs:comment`；`rdfs:comment` 须含中文定义 + ID 空间 + 权威源三要素。
- **门禁判据**：头三元组齐备率 100%；缺任一 ⇒ FAIL。
- **失败具名码**：`ONTOLOGY_HEADER_INCOMPLETE`、`ONTOLOGY_VERSIONIRI_MISSING`、`ONTOLOGY_COMMENT_MISSING_AUTHORITY`。
- **适用层**：各层本体文件（L1/L2/L3 为 OWL；L4 的 Schema 载体用等效字段，见 R2.1）。
- **R2.1（新增）**：L4 非 OWL 载体（JSON Schema / LinkML / SKOS）以**等效字段**满足本条：`$id` 或 `version`、`description`、`authorityEntity`、来源声明。判定等价性由 Integration Contract Owner 出具对照表。
- **现状**：部分已有（`versionIRI` 缺，设计 §6.4 已定）。
- **责任 Owner**：各层 T-Box Owner。
- **相对 V1.2 修订**：新增 R2.1（非 OWL 载体的等效要求）；「权威源」由注释升级为**必填要素**。

### R3｜序列化与导出

- **规则文本**：源制品以 Turtle 为权威序列化；JSON-LD 为**导出物**（`make export-jsonld`），导出物由源生成、禁手改；导出物与源内容哈希钉值并行记录。
- **门禁判据**：Turtle 可解析 + JSON-LD 导出成功 + 导出物哈希入 `PROVENANCE.json` + 导出物禁手工编辑（生成物纪律）。
- **失败具名码**：`ONTOLOGY_PARSE_FAIL`、`ONTOLOGY_EXPORT_MISSING`、`ONTOLOGY_GENERATED_FILE_TAMPERED`。
- **适用层**：L1/L2/L3（L4 按 R2.1 以 Schema 形式导出）。
- **现状**：Turtle ✓，JSON-LD 缺。
- **责任 Owner**：各层 T-Box Owner + 契约库发布流水线。
- **相对 V1.2 修订**：补「生成物禁手改 + 导出物哈希钉值」（与仓库既有生成物纪律对齐）。

### R4｜Shape 由验证场景决定（**废止「每类一 Shape」**）

- **规则文本**：
  1. **废止**「每类恰好一份 NodeShape」的普遍要求；Shape 由**验证场景与封闭边界**决定——一个类可有多份 Shape（发布/摄取/运行），不同类可复用同一 Shape；
  2. 必须提供**场景清单 + 覆盖矩阵**（说明每个场景的意图、目标类、约束来源），入 `REFERENCE-ALIGNMENT.md` 附录；
  3. **空转（vacuous）= 失败**：`实际目标数 = 0` 时不得给绿 —— 应为 `NOT_EVALUATED`（无生产实例）或 `DESIGN_ONLY`（无实现），**显式豁免除外**（豁免只放行开发，永不满足激活门禁）；
  4. Shape **由源模型经生成链产出，禁手改**；
  5. **Shape ↔ 源模型一致性门禁**：类增删必须伴随 Shape 同步；门禁比对的锚点是**源模型清单 ↔ Shape 目标类清单**（而非「类数 == Shape 数」）。
- **门禁判据**：场景覆盖矩阵齐备 + 每个场景记录「期望目标数 vs 实际目标数 + 正/负/变异夹具命中数」+ Shape 源一致性 + 无手改生成物。
- **失败具名码**：`ONTOLOGY_VACUOUS_SHACL`（目标数 0 却给绿）、`ONTOLOGY_SHAPE_SCENARIO_MISSING`、`ONTOLOGY_SHAPE_DRIFT`（Shape 与源不一致）、`ONTOLOGY_GENERATED_FILE_TAMPERED`。
- **适用层**：L1/L2/L3。
- **现状**：32/32 类、169 条约束，但 `vacuous` 静默绿 —— 纪律须改。
- **责任 Owner**：各层 T-Box Owner；Q1/Q2 场景的验证数据由数据 Owner（D4）提供。
- **相对 V1.2 修订**：**重大修订** —— V1.2 的「每类一份 NodeShape」普遍真理被设计 §5.5/§6.3 推翻；一致性门禁判据从「计数相等」改为「清单同步」；空转判定补目标数与夹具命中数（设计 §6.2）。

### R5｜公理与约束

- **规则文本**：必须显式建模：不相交（`owl:disjointWith`，仅在有真实业务互斥时声明）、功能性/基数约束、版本替代关系（如 `supersedesVersion`）、以及**时态语义约束**（有效期字段必填/区间合法）。
- **门禁判据**：公理清单可枚举；每条公理有场景归属；**新增公理须过 R6 兼容性判定**（新增互斥/新增必填属 major 候选）。
- **失败具名码**：`ONTOLOGY_AXIOM_UNJUSTIFIED`（无场景归属的公理）、`ONTOLOGY_TEMPORAL_CONSTRAINT_MISSING`。
- **适用层**：L1/L2/L3。
- **现状**：部分有。
- **责任 Owner**：各层 T-Box Owner。
- **相对 V1.2 修订**：新增「无场景归属的公理不得声明」与「时态语义约束」两项（回应 `GroupMembership`/`CustomerRole` 要求的有效期强制）。

### R6｜变更兼容性（**替代「只增不改」**）

- **规则文本**：每次变更先按 `patch / minor / major` 判定（判据见复审包 07 号矩阵），并按级别执行动作：

| 级别 | 判据（摘要） | 必须动作 |
|---|---|---|
| `patch` | 注释/标签/示例完善，不动语义 | CHANGELOG；旧钉值有效 |
| `minor` | 只增式扩展（新类/新属性）**且不改既有约束**；放宽约束 | CHANGELOG + 版本号 minor 递增；旧钉值有效 |
| `major` | 删项/改名/收窄 domain·range·值域/**新增可能推翻既有结论的约束**/转制品类型/IRI 变更 | 新 `versionIRI` + 弃用期（≥1 发布周期双发布）+ `oldIRI → newIRI` 迁移映射 + 回滚预案 + **双侧 Owner 批准** |

  附加：**「只增」不自动等于 minor**；**复合变更取最高级别**（见 §6 Q-2）；词表变更单列（SKOS 新增概念 = minor，退役概念 = major）；Schema 变更单列（新增可选字段 = minor，新增必填/删字段/改类型 = major）。
- **门禁判据**：每次变更附**变更预测表** + 旧夹具回归（该通过仍通过、该失败仍失败）+ 影响面分析 + 回滚可执行性验证。
- **失败具名码**：`ONTOLOGY_BREAKING_CHANGE`（未按 major 流程）、`ONTOLOGY_COMPAT_TEST_MISSING`、`ONTOLOGY_NO_MIGRATION_MAP`、`ONTOLOGY_NO_ROLLBACK_PLAN`。
- **适用层**：全层。
- **现状**：新增（V1.2 为「只增不改」朴素规则）。
- **责任 Owner**：各层 T-Box Owner + 双侧 Owner 共签（major）。
- **相对 V1.2 修订**：**重大修订** —— 采纳 M-09，以兼容性矩阵替代「只增不改」，并吸收委员会指正「新增约束也可能破坏兼容」。

### R7｜元数据完备性

- **规则文本**：每个类/属性/词表项必填六项：`rdfs:label`、`rdfs:comment`（定义）、**定义来源**、**ID 空间**、**权威源**、**生命周期状态**。L1 术语另须满足 22 字段术语合同（设计 §9）。
- **门禁判据**：六项齐备率 100%（逐项，不接受「整文件齐备」的抽样口径）；L1 术语 22 字段齐备率 100%。
- **失败具名码**：`ONTOLOGY_METADATA_INCOMPLETE`（附缺失字段名与 termId）。
- **适用层**：全层。
- **现状**：部分有。
- **责任 Owner**：各层 T-Box Owner。L1 的部分字段（A-Box Owner / ID Owner / 来源系统）依赖 D2/D4 签署，未签期间保持 `PENDING(D2|D4)` 具名值。
- **相对 V1.2 修订**：明确「逐项齐备、不抽样」，并把设计 §9 的 22 字段挂到 L1 术语上。

### R8｜版本、可追溯与变更影响面

- **规则文本**：库根须有 `VERSION`、`CHANGELOG`、`PROVENANCE.json`（逐件 sha256 + `authorityEntity` + `hostingRepo` 双字段）；每次本体变更必须产出**影响面分析报告**：受影响钉值方、`planHash` 失效范围、重钉清单、消费方清单。
- **门禁判据**：三件齐备 + `PROVENANCE.json` 哈希与制品一致 + 影响面分析非空（变更时）+ `authorityEntity`/`hostingRepo` **分列且非同一值**（防「权威=寄放」混同）。
- **失败具名码**：`ONTOLOGY_PROVENANCE_MISSING`、`ONTOLOGY_HASH_MISMATCH`（具名漂移拒绝）、`ONTOLOGY_IMPACT_ANALYSIS_MISSING`、`ONTOLOGY_PROVENANCE_FIELD_CONFLATED`（`authorityEntity` 与 `hostingRepo` 未分离）。
- **适用层**：全层（库级）。
- **现状**：需建。
- **责任 Owner**：公共语义 Owner（L1 库）+ 各层发布流水线 Owner。
- **相对 V1.2 修订**：新增 `authorityEntity`/`hostingRepo` 双字段要求（设计 V2.0 变更 #16）与「不得混同」判定。

### R9｜引用完整性与 import closure

- **规则文本**：
  1. `owl:imports` **必须**钉 `owl:versionIRI`（禁裸 ontology IRI 引用）；
  2. 生产消费方**同时**校验内容哈希 —— 明确为**项目加严规则**，**不**宣称为 W3C 或任何标准的普遍强制要求（W3C 中 `versionIRI` 为 MAY）；
  3. **import closure 不得同时包含同一 ontology series 的两个不同版本**；
  4. import 目标变更必须触发消费侧重钉检查。
- **门禁判据**：全部 import 为 pinned `versionIRI` + 闭包单版本 + 钉值哈希与实际内容一致 + 跨层引用在白名单内（L2/L3 仅经 `owl:imports` 引用 L1）。
- **失败具名码**：`ONTOLOGY_UNPINNED_IMPORT`、`ONTOLOGY_IMPORT_CLOSURE_MULTI_VERSION`、`ONTOLOGY_ASSET_DRIFT`（既有码，续用）、`ONTOLOGY_CROSS_LAYER_REF_VIOLATION`。
- **适用层**：L1（被引）+ L2/L3（引用方）。
- **现状**：新增（V1.2 补缺）。
- **责任 Owner**：各层 T-Box Owner + Integration Contract Owner。
- **相对 V1.2 修订**：**定性修订** —— 把「钉 versionIRI」明确写为**项目加严**而非标准要求（设计 §6.4）；新增 C-3（闭包单版本）与跨层引用白名单。

---

## 2. 相对 V1.2 的差异汇总（供复审与签署）

| 规则 | 修订性质 | 关键变化 |
|---|---|---|
| R1 | 加严 | `PENDING:` 占位纪律、前缀碰撞禁入发布、禁动态 IRI |
| R2 | 加严+扩展 | 新增 R2.1（L4 非 OWL 载体等效要求）；「权威源」为必填要素 |
| R3 | 加严 | 导出物禁手改 + 导出物哈希钉值 |
| **R4** | **重大** | **废止「每类一 Shape」**；一致性判据改「清单同步」；空转须记目标数与夹具命中数 |
| R5 | 加严 | 无场景归属的公理不得声明；时态语义约束必填 |
| **R6** | **重大** | **「只增不改」→ 兼容性矩阵（patch/minor/major）**；「只增」不自动 minor |
| R7 | 加严 | 逐项齐备（不抽样）；L1 挂 22 字段；D2/D4 未签用 `PENDING(Dx)` 具名值 |
| R8 | 加严 | `authorityEntity`/`hostingRepo` 双字段且不得混同 |
| R9 | 定性修订 | 明确为**项目加严**，不声称标准强制；新增闭包单版本与跨层白名单 |

**未变**：R1~R9 的九条骨架、编号与顺序保持不变（便于与 V1.2 逐条比对与历史追溯）。

---

## 3. 门禁产出物与命名（禁 CONFORMANCE 字样）

| 产出物 | 路径（建议） | 名义 |
|---|---|---|
| 规则说明 | 契约库根 `MODELING-RULES.md`（本稿为其内容草案） | 内部规则 |
| 参照对齐矩阵 | 契约库根 `REFERENCE-ALIGNMENT.md`（条款版待 D1） | 参照对齐 |
| 门禁报告 | 契约库 `REFERENCE-ALIGNMENT-REPORT.md` | 内部规则逐条绿/红 |
| 豁免登记表 | `REFERENCE-ALIGNMENT-REPORT.md` 附录（原因/责任人/解除条件/到期日） | — |
| 命令 | `make conformance`（**沿用计划 §7**） | 见 §6 Q-1 |

**报告必备内容**：逐条 R1~R9 绿/红 + 执行命令 + 制品哈希 + 豁免登记 + 变异复验记录（注入一处违规 ⇒ FAIL；恢复 ⇒ PASS）。

---

## 4. 与 D1（标准文本）的关系

1. 本稿 R1~R9 的**定性不依赖**正式文本：它们是本项目内部工程控制（部分加严），不声称标准符合性；
2. 正式文本到手后，`REFERENCE-ALIGNMENT.md` 的**条款适用性矩阵**（栏位：条款号 / 适用性（适用·不适用+理由）/ 项目加严 / 证据 / 结论）单独走 **T2~T4 门禁**，不并入主设计基线（执行计划 §2 WI-A3）；
3. 若矩阵结论要求调整 R1~R9 文本，走本文件 §5 的修订流程，**不得**在实现里绕开。

## 5. 修订流程（本文件自身的变更）

| 变更类型 | 审批 |
|---|---|
| 措辞、示例、措辞一致性（不动判据） | 公共语义 Owner 单签 + CHANGELOG |
| 判据/失败码/级别变更 | 公共语义 Owner + 受影响层 T-Box Owner 共签 |
| 增删规则或其名义定性 | 公共语义 Owner + 委员会/复审 + Owner 批准 |

---

## 6. 待决项（PSO 不单方决定）

| # | 待决 | 决策 Owner | 影响 |
|---|---|---|---|
| **Q-1** | 命令名 `make conformance` 是否改为 `make reference-alignment` | Owner / TL | 命令名与「禁 CONFORMANCE 字样」的一致性；若保留，须在 README 显式声明「命令名为历史命名，输出文件不含该字样」 |
| **Q-2** | 「放宽约束（minor）」与「IRI 迁移/改名（major）」并发时的级别判定 | 设计 Owner + 委员会 | 直接决定 L1 四条属性（`connectsFrom/To` range 放宽、`memberOfGroup` domain 放宽）的级别与流程（见 `ONTO1-L1-八类术语定义稿-DRAFT.md` §3.3/§3.5） |
| **Q-3** | 豁免（`WAIVED_FOR_DEVELOPMENT`）的到期检查脚本归属与触发点 | TL + 契约库 Owner | R4/R6 的「豁免不得满足激活门禁」需要脚本化（设计 §7） |
| **Q-4** | 目标数断言的记录载体（报告内嵌 vs 机读 JSON） | 公共语义 Owner + 独立 QA | 决定 CQ/Shape 执行记录能否被独立 QA 复算 |
| **Q-5** | R7 的 `PENDING(D2\|D4)` 具名值是否被允许出现在发布制品 | 公共语义 Owner + Owner | 影响 Wave 1 库骨架的可构建性与发布门禁严格度 |

---

## 7. 非声明

- 本稿**不是**符合性声明，**不含**任何标准条款级判定，**不**声称 R1~R9 来源于任何标准；
- 本稿不构成 `DESIGN_APPROVED`、不构成 L1 发布、不代表公共语义 Owner 已任命；
- 与设计 V2.0 / 复审包冲突时，以设计 V2.0 / 复审包为准；
- 本稿未运行任何门禁、未产出 `REFERENCE-ALIGNMENT-REPORT.md`（该报告属 Wave 1 库骨架 / Wave 4，且需要 Owner 任命与 Wave 1 开工前置）。
