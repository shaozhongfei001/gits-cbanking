# 人读模块地图（两仓分工白话版）

```text
DOC_ID      = UA-HUMAN-MODULE-MAP-001
STATUS      = DERIVED / NOT_AUTHORITATIVE（派生视图，非权威）
SOURCE      = .ua/knowledge-graph.json（Understand-Anything 产物）+ 代码目录与类名实证
CREATED_AT  = 2026-09-15
AUTHOR      = tech_lead（会话侧车 ua_humanize.py 生成层名，本文为人工归纳）
GRAPH_AT    = gits-cbanking @a1e183bb（内容扫描 @6b30d23d） + Leibniz-KERT @c49ddb5f
REDLINE     本文件不得写入 evidence/、不得替代 specs/、不得作为 Gate/ADR 依据
```

> **为什么需要这份文件**：UA 原图是**文件级**的（3256 + 609 个文件节点），标签是社区检测硬编码的 `Cluster A/B/C`，描述是逐文件的技术摘要。**它对 LLM 有用，对人没用**。本文把图**升到模块级**、换成业务中文名、用白话讲清"谁负责什么"。
>
> **层级关系**：本文（人读，6 大类 → 模块） ＞ 图里的 `layers`（模块级，42 层） ＞ 图里的文件节点（机器读）。

---

## 一、30 秒看懂

| | gits-cbanking | Leibniz-KERT |
|---|---|---|
| 一句话 | **客户经理的作业系统**：把"见客户前后该做什么"变成有章法、有留痕、AI 只能提建议不能自己动手的流程 | **知识供应的底座**：把银行内部散落的资料（条款、话术、规则）整理成能按需取用的"知识件"，供上面的作业系统调用 |
| 规模 | 3256 个文件进入图谱 | 609 个文件进入图谱 |
| 技术栈 | Java（Spring）+ 网页前端（Vue） | Python |
| 关系 | 两仓在图上**没有任何连线**——这是工具的盲区（跨仓关系它看不见），不代表业务上没有关系 | 同左 |

---

## 二、五个能力点速查（知识地图 · SKILL 路由 · LightRAG · 本体建模 · 语义层）

> **先说结论**：这五块**大部分在 gits，不在 KERT**；其中 **LightRAG 两仓都没有代码实现**，**KERT 也没有任何 RDF/OWL/SHACL 本体文件**（KERT 的"图"是另一种东西）。上一版看不到它们，是因为我按目录归档，把 KERT 整个 `src/` 压成了一层。**现已拆开。**

### ① 知识地图 —— 在 gits，KERT 只消费

| 项 | 事实 |
|---|---|
| 实现在哪 | `gits-cbanking｜知识地图与激活编排`（37 文件）= `modules/knowledge-architecture/` |
| 核心类型 | `KnowledgeMap`(45 行) / `KnowledgeMapPort`(17 行) / `KnowledgeElementPort` / `KnowledgeWikiPort` / `DefaultActivationPlanner`(318 行) / `ActivationPlan` |
| 契约 | `generated/gk-ke/v1/KnowledgeMap.schema.json`；必填：`mapId / version / releaseId / taskTypes / entryNodes / **routePolicyRef** / nodes / edges / purpose / scope / simulationOnly` |
| 它是什么 | 一张"**什么任务该带哪些知识**"的导航图：节点是任务/知识域/资产/能力，边是带关系类型与设计决策引用的连接；另有**入口节点**（从哪进）与**路由策略引用**（怎么走） |
| 界面 | `frontend/src/views/KnowledgeMapView.vue` + `frontend/src/api/knowledge.ts` |
| 实例数据 | `scenario/seed/` 下的演示知识资产（如 `KM-CORP-RM-PREVISIT-DEMO`），层 = `演示客户数据包`(281) |
| KERT 侧 | **只消费、不建模**：`src/kert/application/skills.py` 的 `_load_ki` / `_ki_context` 把知识片段注入给 LLM |
| 图能答 / 不能答 | 能：地图有哪些节点与边、由哪些文件实现。**不能**：某次具体请求实际走了哪条路径（图里没有运行期数据） |

### ② SKILL 路由 —— 分成两半，**而这两半没有连起来**

| 半 | 在哪 | 事实 |
|---|---|---|
| **策略半**（怎么算出一条合法路线） | **gits** | `RoutePolicyEvaluatorPort` + `DefaultActivationPlanner`，源码注释原文："由 Route Policy Evaluator 解析唯一合法 route，再经 Activation Contract → Asset Catalog"；权限未决 / 请求生产写回 / route 与合同不一致 / 资产未登记 → **一律拒** |
| **执行半**（按名字跑到脚本） | **KERT** | `src/kert/application/skills.py`（874 行）：`registry()` 只返回 **3 个内置技能**（外联脚本 / 会面脚本 / R1 拜访报告）；`_executor()` 用 **if/elif 硬编码分发**（`SP-20`/`SP-21`/`SP-15`/`bank-front-supply-chain-graph`/`skill-customer-*`）；另有 `_load_packages()` 从目录加载外部技能包 |
| ⚠ **缺口** | — | KERT 里 `bank-front-*`（文档命名）与 `skill-customer-*`（注册名）**两套命名并存**，靠 if/elif 分支桥接；gits 的 `routePolicyRef` 与 KERT 的 `_executor` **没有任何连线**（两仓 0 跨仓边）；也**没有独立的动态路由器代码** |

### ③ LightRAG —— **没有实现，也没有启用**

| 项 | 事实 |
|---|---|
| KERT | **零命中**（全仓 grep `lightrag` / `light_rag` 无结果） |
| gits 代码 | **零命中**（无 `.py` / `.java` 引用） |
| gits 文档与 Loop | `loops/GK10-l5-2-lightrag`，标题原文："LightRAG（Spike + A/B/C 对照 + 成本报告；**满足 C05 门槛才启用**）" |
| 最终状态 | `evidence/L6/DEPLOYMENT.lock.json` → **`"lightragEnabled": false`** |
| 结论 | 它是**被评估过、未启用的候选**。图上没有它是因为**它不在代码里**，不是漏扫。实际的检索路径是 KERT 的 **Kuzu 图谱**（见 ④）与内存检索 |

### ④ 本体建模 —— 在 gits 且链路完整；**KERT 用的是另一套"图"**

**gits（真正的 RDF 本体）**

| 环节 | 文件 | 说明 |
|---|---|---|
| 本体权威源 | `specs/semantic/gits-core.owl.ttl`（364 行） | OWL 本体，定义业务概念与关系 |
| 校验形状 | `generated/semantic/gits-core.shacl.ttl`（268 行） | 由本体派生：每个概念必须有哪些属性、什么类型、最少几个 |
| 结构定义 | `generated/semantic/gits-core.schema.json` | 由 LinkML 编译；领域对象（Action/Claim/Customer/Capability/Commitment）的字段与必填 |
| 产品实例 | `specs/knowledge-architecture/instances/product/products.ttl`（115 行） | 产品知识实例 |
| 数据映射 | `specs/data/customer-source-mapping.r2rml.ttl`（15 行） | **R2RML**：把老系统表结构映射成本体，让库里数据对得上 |
| 落地实现 | `adapters/semantic-jena/JenaOntologyAdapter.java` | 读 TTL → 统计类/对象属性/数据类型属性/个体数 → **按内容算 SHA-256 版本**；解析不了就 fail-closed 报 missing/malformed |

> 实测本体计数基线：**32 类 / 34 对象属性 / 1 数据类型属性 / 0 个体**（来自 `JenaOntologyAdapterTest`）。

**KERT（不是 RDF，是 Kuzu 属性图）**

| 项 | 事实 |
|---|---|
| 有没有 OWL/RDF | **没有**。全仓无 `.ttl` / `.owl` / `.shacl` 文件；`ontology` 仅 1 处提及（`service_proposal.py`） |
| 它的"图"是什么 | `data/product_knowledge_graph.kuzu`（**32 MB**，2026-09-02）——嵌入式图数据库 |
| 怎么建的 | `src/kert/infrastructure/graph/kuzu_builder.py`（152 行）：从活动投影 `entities/relations.parquet` 构建，保留 `relation_id` / `statement_id` 溯源，输出带内容指纹的 `PROJECTION.json`，支持**删掉后仅凭投影重建且指纹一致** |
| 依据 | **IMP-ADR-011**（受控豁免引入 Kuzu 作为"可重建的查询加速投影"）；`scripts/kuzu_prototype.py` 是选型原型 |

> **所以项目里有两种"图"**：gits 的 **RDF 语义图**（本体 + SHACL，管"对不对"）与 KERT 的 **Kuzu 属性图**（管"查得快不快"）。性质、责任人、治理路径都不同，**目前图上无连线**。

### ⑤ 语义层实现 —— 在 gits；KERT 的 "semantic" 是另一个意思

**gits**

| 组件 | 位置 | 白话 |
|---|---|---|
| 对外能力定义 | `modules/semantic-runtime/`（层 `语义层运行时`，14 文件） | `SemanticRepositoryPort` / `OntologyPort` / `InMemorySemanticRepository` / `FailClosedSemanticQueryGuard` —— 语义层能提供什么 |
| 查询守卫 | `FailClosedSemanticQueryGuard`（SEC-005） | **只放行登记过的查询 ID**；原始 SPARQL、缺失或未登记 ID 一律拒；shadow 阶段返回确定性占位行数且无副作用 |
| 真实实现 | `adapters/semantic-jena/`（层 `语义层实现（Jena）`，6 文件） | 用 Jena 跑起来：事务型内存 Dataset + 加载本体与 SHACL + 对候选 Turtle 做一致性校验 |

**KERT**：**没有 RDF 语义层**。它的 `semantic` 命中在 `domain/hashing.py`、`application/publish.py`、`application/gates.py`——含义是**内容指纹与版本语义**（同一内容得到同一指纹、可重建、可比较），**不是 RDF 推理**。

### 为什么上一版报告里看不到这五块

| 原因 | 说明 |
|---|---|
| 我的分层太粗 | KERT 整个 `src/` 被打包成"知识服务运行时"一层。**已拆成 6 层**：对外接口与加固 / 业务应用层（含技能分发）/ 领域模型与契约 / 基础设施与图谱投影 / 命令行工具 / 知识服务看板 |
| 它们大多不在 KERT | 知识地图、本体、语义层在 **gits**；Skill 路由**横跨两仓**。你点开的是 KERT，自然看不到 |
| gits 侧也埋着 | 原来 `specs/` 是一整层（412 文件）、知识地图混在"知识资产与装配"里。**已拆出 9 个新层**：知识地图与激活编排 / 语义层运行时 / 语义层实现（Jena）/ 本体权威源（OWL）/ 数据到本体的映射（R2RML）/ 知识架构契约与实例 / 知识引擎交换契约 / 生成的语义制品（SHACL/Schema）/ 生成的知识引擎契约制品 |
| **两个真实盲区** | `bank_front_ws/`（187 文件）与 `data/`（32 MB Kuzu 库）被 **`.gitignore` 挡住**，工具**连枚举都枚举不到** → 完全没进图。而它们恰是"知识落地 / 工作区"的地方。**这条只有改 `.gitignore` 或换采集方式才能补，改 `.understandignore` 无效** |

---

## 三、gits-cbanking：模块分工总览

### 第 1 类 · 业务能力（真正干活的 7 个）

| 业务名 | 代码在哪 | 白话职责 | 图内规模 |
|---|---|---|---|
| **经营事实与承诺账本** | `modules/operational-ontology/` | 全项目最核心的一本账。客户说了什么、我们答应了什么、发现了什么机会、经营数字是多少，全记在这里；谁改的、什么时候改的都有留痕。**"AI 说的只是候选，要人点头才能算数"这条规矩也在这里兜着。** | 105 文件 / 104 类 |
| **客户经营旅程** | `modules/scenario-customer-journey/` | 把"客户经理见客户"串成一条链：访前准备 → 会中记录 → 访后对账 → 下一步建议。每一步推进都会生成一条记录，AI 产出一律先标成"候选"。 | 29 / 28 |
| **人工确认与对外动作** | `modules/human-action/` | AI 不许自己动手。凡是真要对外做一件事（写回 CRM、发通知、外呼），必须先变成待办、拿到客户授权、做完留回执。 | 14 / 13 |
| **知识资产与装配** | `modules/knowledge-architecture/` | 把银行的资料切成一条条**有编号**的知识件，按当前任务把该用的装配给 AI。解决的是"这次见客户到底该带哪几份材料"。 | 37 / 27 |
| **语义校验底座** | `modules/semantic-runtime/` | 给知识做体检：符合规则的放行，不符合的直接拒收，**不悄悄放过**。 | 14 / 13 |
| **证据与上下文** | `modules/context-evidence/` | 每个结论都要能回答"凭什么"：把支撑它的原始材料一起存下来。 | 8 / 7 |
| **效果评测** | `modules/evaluation/` | 衡量 AI 给的建议到底好不好用。 | 9 / 8 |

### 第 2 类 · 支撑设施（让上面能跑起来）

| 业务名 | 代码在哪 | 白话职责 | 规模 |
|---|---|---|---|
| **对外服务入口** | `apps/api/` | 网页和其它系统访问后端的**唯一大门**。它自己不含业务道理，只负责把请求翻译成业务操作、再把结果按约定格式送回去。 | 268 / 257 |
| **后台作业** | `apps/worker/` | 没人盯着也要跑的活：定时批处理、异步补偿、事件消费。 | 11 / 9 |
| **数据落库** | `adapters/persistence-relational/` | 把上面那本账真正写进数据库（本地开发用内存库、线上用 MySQL）。 | 208 / 130 |
| **知识文件读取** | `adapters/knowledge-filesystem/` | 从文件目录读知识件；**读不到、读坏了就当作没有，绝不交半成品**。 | 29 / 28 |
| **本体校验引擎** | `adapters/semantic-jena/` | "语义校验底座"的具体实现（用 Jena + SHACL 跑规则）。 | 6 / 5 |
| **Oracle 只读取数** | `adapters/oracle-source/` | 只从老系统把数据搬过来，**明确不往回写**。 | 7 / 6 |
| **场景执行引擎** | `scenario/execute/` | 把一遍完整业务流程在演示环境里跑给你看。 | 44 / 43 |
| **演示客户数据包** | `scenario/seed/` | 一套造好的假客户数据，用来演示和自测。 | 281 / 1 |
| **客户经理工作台** | `frontend/` | 客户经理实际点的那套网页：访前包、会中助手、访后对账、审批、知识地图等 50+ 个页面。 | 225 / 1 ⚠ |

> ⚠ **前端这一行要特别提醒**：225 个文件里只有 1 个"类"节点。因为 UA 的结构抽取**不支持 `.vue` 文件**（101 个页面组件全部只拿到文本摘要，没有组件/方法结构）。所以"工作台有几个功能、谁调用谁"**在图上是看不出来的**。

### 第 3 类 · 权威源（不是"功能模块"，是规矩本身）

| 业务名 | 代码在哪 | 白话职责 | 规模 |
|---|---|---|---|
| **合同与基线** | `specs/`（⚠ **权威源**） | 全项目的规矩都写在这里；**代码不能绕过它自作主张**。 | 412 |
| **自动生成制品** | `generated/` | 按上面的规矩自动生成出来的文件，只读，不许手改。 | 59 |
| **封版受控资料** | `docs/dd/` | 评审通过、冻结在案的正式材料。 | 169 |

### 第 4 类 · 交付过程（记录，不是代码）

| 业务名 | 代码在哪 | 白话职责 | 规模 |
|---|---|---|---|
| **交付过程记录** | `loops/` | 每一轮活儿的留痕：谁在做、做到哪一步、证据是什么。**文件数最多的一块（934）**。 | 934 |
| **设计与治理文档** | `docs/`（除 `dd/`） | 设计说明、决策记录、派工单、操作手册。 | 191 |
| **证据归档** | `evidence/` | 给验收和审计看的成品证据。 | 18 |

### 第 5 类 · 工程配套（跑得起来的杂项）

运维与验收脚本 `scripts/`(111) · 架构图与流程图 `diagrams/`(7) · 内部工具与隔离资产 `tools/`(9) · 跨模块测试 `tests/`(14) · 自动检查流水线 `.github/`(1) · AI 协作规则 `.codebuddy/`(12) · 根级说明与配置(22)

### 谁依赖谁（图上实测的连线方向）

```
对外服务入口 ──┬─→ 经营事实与承诺账本 (294 条)
              ├─→ 场景执行引擎        (249)
              ├─→ 客户经营旅程        (113)
              ├─→ 数据落库            ( 48)
              └─→ 人工确认与对外动作   ( 44)

数据落库     ──→ 经营事实与承诺账本 (168)
客户经营旅程  ──→ 经营事实与承诺账本 ( 31)
人工确认     ──→ 经营事实与承诺账本 ( 11)
知识文件读取  ──→ 知识资产与装配     ( 60)
本体校验引擎  ──→ 语义校验底座       (  7)
Oracle 取数  ──→ 经营事实与承诺账本  (  7)
```

**读法**：箭头指向"被使用的一方"。**几乎所有线都指向「经营事实与承诺账本」**——这就是为什么它是核心：其它模块都在围着它转。
**按这张图推断的风险**（推断，非权威结论）：这本账如果定义错了，全系统一起错；它也几乎没有上游可依赖，改动它等于牵一发动全身。

---

## 四、Leibniz-KERT：模块分工

> `src/kert/` 已按**真实分层**拆开（原先是一整块"知识服务运行时"）：

| 业务名 | 代码在哪 | 白话职责 | 规模 |
|---|---|---|---|
| **对外接口与加固** | `src/kert/api/` | 所有外来请求的唯一入口：鉴权、限流、请求大小限制；外部技能目录解析失败就拒绝，不静默降级。 | 3 |
| **业务应用层（含技能分发）** | `src/kert/application/` | 真正干活的逻辑：**技能注册与分发（`skills.py`，874 行）**、知识抽取与发布、客户知识与交互记忆、产品推荐、评审与回滚。 | 27 |
| **领域模型与契约** | `src/kert/domain/` | 业务对象与契约的定义：文档/实体/关系/声明/规则/发布 等规格，以及资产与规则模型。 | 15 |
| **基础设施与图谱投影** | `src/kert/infrastructure/` | 文档解析（PDF/DOCX/文本）、LLM 适配、以及把知识投影成 **Kuzu 图库**（`kuzu_builder.py`）。 | 24 |
| **命令行工具** | `src/kert/cli/` | 给运维用的命令行：init / inspect / validate / ingest。 | 2 |
| **知识服务看板** | `src/kert/dsh/` | 自带小网页：看统计、搜技能、跑技能、浏览知识资产与任务监控。 | 5 |
| **技能知识包** | `skills/` | 每个技能一份说明书：输入什么、输出什么、按什么规则判断。 | 49 |
| **技能样例与契约样例** | `examples/` | 给开发参考的样例（含 7 个银行访前技能），不参与实际运行。 | 140 |
| **自动化测试** | `tests/` | 保证改动不弄坏已有功能。 | 80 |
| **自检与压测脚本** | `scripts/` | 上线前先自己体检一遍。 | 39 |
| **设计与运维文档** | `docs/` | 怎么设计、怎么部署、怎么排障。 | 92 |
| **评审与验收留痕** | `evidence/` | 评审和验收留下的记录。 | 59 |
| **技术预研** | `poc/` | 试过但还没定用的技术方案。 | 41 |
| **部署与网关** | `deploy/` | 打包、起服务、配网关。 | 10 |
| **接口规格** | `specs/` | 对外接口的书面约定。 | 1 |

---

## 五、图上怎么看到这些东西

| 你想看的 | 在 Dashboard 怎么看 |
|---|---|
| **模块分工（推荐）** | 总览层级**按 `layers` 聚合**，现在的层名就是业务模块名，例如 `gits-cbanking｜经营事实与承诺账本` |
| 目录归属 | 侧栏目录分组（现为 24 个目录桶，最大 `loops` 18.9%） |
| 单个文件/类 | 放大到文件层级看；摘要来自 LLM 逐文件归纳 |
| 机器视图 | 图里保留了 `layersStructural`（原结构层：迭代治理/接口契约/…），只适合机器看 |

### 关于你看到的 `Cluster A/B/C`

**它现在已经被修掉了**，原因和处理如下：

1. `Cluster A/B/C` 不是业务名，是 UA Dashboard 社区检测的**硬编码占位符**：
   `packages/dashboard/src/utils/containers.ts:120` → `Cluster ${String.fromCharCode(65+i)}`
2. 触发条件是**目录分组"塌陷"**：分组逻辑按 `filePath` 首段分桶，若单桶占比 > 70% 就放弃目录、改用社区检测。
3. 上一版合并图我给 `filePath` 加了 `gits-cbanking/` 前缀，导致只剩 2 个桶（gits 占 80%）→ **触发兜底 → 显示 Cluster A/B**。这是**我引入的**。
4. 修法：`filePath` 保持**仓内相对路径**（仓别改由节点 `repo` 字段和层名前缀承载）。实测复刻分组判定：桶数 24、最大桶 18.9%、根级 0.8% → **不再触发兜底**。

---

## 六、术语对照（你看文档时会遇到的词）

| 文档/代码里的词 | 白话 |
|---|---|
| Port / 端口接口 | 一个"插槽"，规定能力长什么样，具体谁来干由外面插进来 |
| Adapter / 适配器 | 插到插槽上的具体实现，负责跟外界（数据库、文件、外部系统）打交道 |
| 聚合根 | 一批数据里"说了算"的那个主体，比如一本账的"账本"本身 |
| fail-closed | 出问题时**默认拒绝**，而不是默认放行 |
| Claim / 声明 | 还没有被确认的说法（可能来自 AI，也可能来自口头） |
| 幂等 | 同一件事做两遍，结果跟做一遍一样 |
| 变异测试 | 故意把代码改坏，看测试能不能抓住 |
| Gate / 门禁 | 必须通过的检查关卡 |
| SSOT | 唯一权威来源（本项目的唯一权威是 `specs/`） |

---

## 七、边界与非声明

- 本文是 **DERIVED 派生视图**：模块名与白话说明由**代码目录 + 类名 + 已生成的逐文件中文摘要**归纳，**不是**权威职责定义。权威划分请看 `specs/`、`docs/` 与各 Loop 的 `LOOP.yaml`。
- **"图生成成功" ≠ "项目已验证"**：本文不构成 QA_PASS，不代表 PRODUCTION_READY，不作为 Gate/ADR 依据。
- 已知图侧缺口（详见同批交付报告）：
  1. `.vue` 前端结构完全未抽取（101 文件）；
  2. 没有函数级节点、没有调用边（"谁调用谁"除 import 外不可回答）；
  3. 两仓之间 0 条连线，跨仓关系不可回答；
  4. `specs/` 等权威源只被"摘要"，**未做任何字段级/合同级解析**——问合同细节仍需回查权威源；
  5. `scenario/kert-platform/` **零节点**。实测该目录（20 MB）里**没有任何源码文件**——只有 59 个 `.pyc` 字节码缓存（`src/kert/__pycache__/`）和一个 1339 文件、约 20 MB 的 `.venv/`；这两类都在内置排除规则内（`*.pyc` / `__pycache__/` / `.venv/`），git 也不跟踪。**结论：不是"工具漏了"，而是该目录确实没有可分析内容**（疑为残留的构建/虚拟环境目录，建议由仓库所有者确认是否清理）。
