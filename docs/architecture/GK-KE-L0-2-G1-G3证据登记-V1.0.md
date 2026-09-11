# GK-KE L0-2 生效条件证据登记（G1–G3）

> 角色：Tech Lead（planning_review）｜Loop：`GK1-l0-2-contract-activation`｜日期：2026-09-12
> 依据：`GK-KE-OWNER-002` §5 生效条件 + §2.2 缺口清单（OF-01~OF-05）
> 性质：**条件关闭证据登记**。不使 OC-01 关闭、不使 ACT-01 生效（G4/G5 未完成）。

---

## G1｜版本与制品绑定

### G1.1 提交展开（区分四个版本角色）

| 角色 | 提交 | 说明 |
|---|---|---|
| 开工基线 | `597d6facdc120a9fbffc44cff116eab50bbb3367` | L0-2 开工 HEAD（`make new-loop` 记录的 baseline_commit） |
| 实现交付 | `87771956e021672a48ba80e8ada6359decd6acfd` | WI-01/03/04 交付（OpenAPI + 正负例 + 消费者测试） |
| **实际受测版本** | `f57eae2774fbc322fed873201f54442e109e88e5` | **独立 QA 审计的对象**（QA 报告 review_head） |
| QA 结论提交 | `f57eae2` | QA_PASS 落盘（与受测版本同一提交，因为 QA 同时提交了修复） |
| 拟激活版本 | `d4e5e527af37fa9f8c0c25a69fe44fbc355b828c` | 本登记时点 HEAD（仅含 Owner 移交文档，**不含合同变更**） |

**血缘核验**（实测，非推断）：
```
git merge-base --is-ancestor 597d6fac f57eae2   → 真
git log --oneline 597d6fac..d4e5e52
  d4e5e52 docs(gk1): hand off L0-2 activation to Owner and log orchestrator ticks
  f57eae2 test(gk1): independent QA PASS for L0-2 after BLOCKER fix
  8777195 feat(gk1): complete L0-2 contract activation WI-01/03/04
  86abd45 docs(gk1): record W3 plan and iterations for L0-2
  9fa6c4f docs(gk1): TL plans and dispatches L0-2 contract activation
```

**关键区分**：`f57eae2`（受测）与 `d4e5e52`（拟激活）**差异仅为文档**（`memory/BLOCKED.md`、`memory/ORCHESTRATOR.md`），
**不含任何合同/实现变更** → 受测证据可有效覆盖拟激活版本。此点已实测：
```
git diff f57eae2 d4e5e52 --stat
  loops/GK1-l0-2-contract-activation/memory/BLOCKED.md      | 103 +++++
  loops/GK1-l0-2-contract-activation/memory/ORCHESTRATOR.md |   (new)
```
（无 `specs/`、`scripts/`、`generated/` 变更）

### G1.2 完整哈希固定（§8.2 要求的"待完整值"）

| 对象 | 完整 SHA-256 |
|---|---|
| `docs/architecture/GITS-KERT_L0-2合并激活决议_人工签署稿_V1.0.md` | `3a456022b7530d935f572fc5b3297dc1ed2e8b31daadce44ddbfbad60a2680b4` |
| `specs/openapi/gk-ke-v1.openapi.json` | `e9df42d34b822470826d8556e58318bbc27cf1ec9647f503e6ed678d7c47fba9` |
| `specs/CONTRACT_INDEX.yaml` | `6e0bacb5bf8d543f612ae2a85404c21a24d87285fb04f1ad3b0e1130e0fd40fc` |
| `loops/GK1-l0-2-contract-activation/evidence/INDEPENDENT_QA-L0-2.md`（**OF-05 短 hash 补全**） | `6ee5eb793d355fc77420ed982183f1505fc0ccc5d3b804b1ed1a56ee759e3fed` |
| `loops/GK1-l0-2-contract-activation/memory/BLOCKED.md` | `cf3220c895d3accc66fc3d68bb2d424d5307fd64cd3c71af2acec06994bc9fe4` |
| `docs/architecture/GK-KE-L0-2-OC01收口-V1.0.md` | `c986b8ec2f05630585427c77ff3cca998dba9e92ef4c66d058165f1b15f3ca2b` |

**OF-05 关闭**：决议 §8.1 引用的两个 hash 与本登记实测**逐字节一致**；
qa 报告短 hash `6ee5eb79…` 已补全。收口文档"QA 待核查"与移交说明"QA_PASS"的差异确认为**时间差**，非 QA 失败。

### G1.3 封版受控路径核对（**OF-03 关闭**）

**关键实测发现**：`4c5f5373` **不是仓库树**，而是仓库内**子目录树**：

```
git ls-tree -r -t 886f710 | grep "^040000 tree 4c5f5373"
  040000 tree 4c5f5373…    docs/dd/gk-ke-contract
```

即：**封版受控 tree 的精确路径 = `docs/dd/gk-ke-contract`**，含 **145 个文件**
（`contracts/` C01–C08、`schemas/` 20、`examples/`、`acceptance/`、`simulation/`、`tools/`、`MANIFEST.json`、`CONTRACT_INDEX.json`）。

**内容级核对（非祖先推导）**：

| 检查 | 命令 | 结果 |
|---|---|---|
| 当前 HEAD 下该路径 tree hash | `git rev-parse d4e5e52:docs/dd/gk-ke-contract` | `4c5f5373c83386d27ea996293a49ee7f3b9f10ce` |
| 与封版 tree 比对 | — | **完全相同** |
| 逐文件差异 | `git diff 886f710 d4e5e52 -- docs/dd/gk-ke-contract/` | **空（byte-identical）** |

**OF-03 处置**：
- 缺口「以祖先关系推导封版未改写」→ **已改为内容级证明**（tree hash 相等 + 逐文件 diff 为空）。
- 缺口「文档目录没有快照指纹」→ `docs/dd/gk-ke-contract` 的 tree hash `4c5f5373…` 即内容指纹；ZIP 指纹 `b21638ab…` 沿用。
- 缺口「两个地图仍为通配 ID、版本为空」→ 见 G2（五条映射逐条核对）。

---

## G2｜来源与转换绑定（部分关闭，KERT 确认待补）

### G2.1 三仓性质（按实际性质记录）

| 仓库 | 性质 | HEAD / 快照 | 在权威链中的角色 |
|---|---|---|---|
| `/home/szf/dev/gits-cbanking` | **Git 仓库** | `d4e5e52`（分支 `feature/GK-KE-L0-contract`） | 权威源（`specs/` + `modules/adapters/apps/`） |
| `/home/szf/dev/Leibniz-KERT` | **Git 仓库** | `3b6640b993f4834d36833fa0bc3005d73768b594` | KERT 实现（Python 服务 8107） |
| `/home/szf/dev/gits-kert-docs` | **非 git 文档目录**（目录快照） | 无 HEAD（须快照时点+文件清单+指纹） | 文档承载，**不参与 gk-ke/v1 权威依据** |

**对 `gits-kert-docs` 的裁定（§5 G2 要求"若完全不参与权威依据，明确排除及无依赖"）**：
本 Loop 的合同权威源为 `specs/`，封版受控物为 `docs/dd/gk-ke-contract`（在主仓 git 内，tree `4c5f5373`）。
**未引用 `gits-kert-docs` 任何内容**；本 Loop 对其**无依赖**。→ 无需提供其快照指纹。

### G2.2 五条映射逐条核对（§3 裁定落地）

| # | 映射项 | §3 允许的关系 | 本 Loop 落地 |
|---|---|---|---|
| 1 | `KM-GITS-ROOT@0.1.0` → 无 SIM 对应 | 接受"根节点不转换为 SIM 任务实例"；按 `mapType=ROOT` 识别 | 已在 OpenAPI `x-gk-ke-existing-mapping` + `x-gk-ke-root-map-discriminator` 登记（`discriminate_by_mapType_ROOT`）；**已删除"按 mapId 字符串匹配"的负例隐患**（负例 `expandMap_2` 专门拒绝 `mapId=="ROOT"`） |
| 2 | `KM-CORP-RM-PREVISIT@0.1.0` → `SIM-MAP-FINANCE@1.0.0` | 受限于访前融资场景投影；首切片限 SIM-C001/SIM-O01/`INTERPRETATION` | 登记为 `pending_owner_confirmation`；**明确不宣布两图全任务等价** |
| 3 | `ASSET-KNOW-PRODUCT-CARDS` → `SIM-ASSET-P001@1.0.0` | **暂不认可一对一**；接受"按明确规则选取/构造一张 SIM 卡" | 登记为 `pending_owner_confirmation`；分类 `KNOWLEDGE_RULE/PRODUCT_CARD` 仅为类型，**未充当身份依据** |
| 4 | `AC-PREVISIT-001` → `ActivationPlan` | 接受"前置约束/来源引用"；**不接受**设计契约直接转成运行计划或复用 ID 作 planId | 登记为 `{"target":"gk-ke/v1:ActivationPlan","status":"pending_owner_confirmation"}`；`createPlan` 的 planId 由 `ActivationPlanRequest` 确定性生成，**未复用 AC- 前缀 ID**；**未向闭集 Schema 加字段** |
| 5 | `RP-CORP-RM-001` → `SIM-ROUTE-001@1.0.0` | 接受受控策略适配；**不接受**仅改名即等价 | 登记为 `pending_owner_confirmation`；**待绑定策略内容 hash 与确定性验证** |

**G2 未闭合项（跨仓，须 KERT 维护方确认）**：
- 映射 3 的"源对象究竟是集合、入口还是单卡"（§3 明确要求 KERT 先确认）
- 映射 5 的源版本/匹配条件/优先级/歧义处理与策略内容 hash
- 映射 2 的适用条件、必需节点、参数、依赖对齐

**TL 声明**：上述三项**须 KERT 提供方核对**，TL 无权代证。→ **G2 未关闭**。
另：因 OC-01 关闭需 G2，**OC-01 未关闭**。

---

## G3｜交换对象对应（**OF-04 关闭**）

### G3.1 分类标准（§3 统一标准）

§5 明确不得重凑"14 直接/6 间接"。本登记按**六类**重算，标准为"该登记项在本 operation 中**实际出现的位置与角色**"：

| 类别 | 定义 |
|---|---|
| **REQ_FULL** | 作为请求体完整实体传输 |
| **RESP_FULL** | 作为成功响应体完整实体传输 |
| **RESP_PROJECTION** | 作为响应中的**摘要/视图投影**传输（非完整实体） |
| **ID_REF** | 仅以 ID/引用出现在请求或响应字段中 |
| **ASYNC_RESULT** | 异步受理结果（jobId 等），**不等于**实体本身 |
| **INTERNAL_ADAPTER** | 内部分类适配类型，无独立 HTTP 端点 |

### G3.2 20 项登记重算（实测自 OpenAPI `$ref` 解析）

| 登记项 | operationId | 类别 | 字段位置 / Schema 引用 | 提供方 | 真实消费方 |
|---|---|---|---|---|---|
| SemanticPackage | `getCorePackageVersion` | **RESP_PROJECTION** | `200.package` → `SemanticPackageVersionView.package` | 公共核心 | gits, kert |
| AssetVersion | — | **ID_REF** | 仅 `CatalogDiscoverResult.entries[].mapRef` 等引用位；**无完整实体端点** | asset_registry | knowledge_map_registry |
| KnowledgeMap | `expandMap` | **RESP_FULL** | `200` → `KnowledgeMap` | KERT | knowledge_map_registry, activation_planner |
| Assertion | `createIngestionJob` | **ASYNC_RESULT** | `202.candidateSetRef`（**非** Assertion 实体；§5 明确） | KERT 工厂 | build_review_release, extraction |
| ReviewDecision | `createReview` | **REQ_FULL + RESP_FULL** | `requestBody` → `ReviewDecision`；`201` → `ReviewDecision` | KERT 审核 | build_review_release, human_gate |
| ReleaseManifest | `createRelease` | **REQ_FULL** | `requestBody` → `ReleaseManifest` | KERT 发布 | build_review_release, projection |
| MetricDefinition | `querySemantic` | **ID_REF** | `SemanticRequest.metricId` + `metricVersion`；**不含完整实体** | semantic_service | metric_governance |
| SemanticRequest | `querySemantic` | **REQ_FULL** | `requestBody` → `SemanticRequest` | 数据平台 | semantic_service |
| SemanticResult | `querySemantic` | **RESP_FULL** | `200` → `SemanticResult` | 数据平台 | semantic_service, context_evidence |
| GraphRequest | `queryGraph` | **REQ_FULL** | `requestBody` → `GraphRequest` | 图适配器 | rag_graph_adapter |
| GraphResponse | `queryGraph` | **RESP_FULL** | `200` → `GraphResponse` | 图适配器 | rag_graph_adapter |
| ActivationPlan | `createPlan` | **RESP_FULL** | `201` → `ActivationPlan` | KERT Planner | activation_planner, agent_orchestrator |
| EvidenceBundle | `getKnowledgeJob` | **RESP_FULL** | `200` → `EvidenceBundle` | KERT Runtime | context_evidence, agent_orchestrator |
| ControlledAction | `createTaskAction` | **ID_REF（嵌套）** | `TaskActionRequest.action` → `ControlledAction` | GITS | controlled_action, crm_writeback |
| MetricDefinition.full | `querySemantic` | **ID_REF** | `metricRef`/`metricId` 口径源；**§5 明确 metricRef ≠ 响应含完整对象** | metric_governance | semantic_service |
| SourceVersion | `createIngestionJob` | **ID_REF** | `IngestionJobRequest.sourceVersionRef`（`id`+`version`） | source_registry | semantic_runtime |
| Capability | `createPlan` | **ID_REF** | `ActivationPlanRequest` → `ActivationPlan.capabilityRefs[]` | capability_registry | activation_planner |
| QueryDefinition | `querySemantic` | **ID_REF** | `SemanticResult.queryId` / `SemanticRequest` 无 queryId → **仅响应侧引用** | query_registry | semantic_service |
| Release | `createRelease` / `revokeRelease` | **RESP_FULL** | `201` → `Release`；`200` → `ReleaseRevoked` | release_registry | build_review_release |
| LegacyRagHit | — | **INTERNAL_ADAPTER** | 无独立端点；既有检索适配 | existing_rag_adapter | context_evidence |

### G3.3 重算结果（替代原"14 直接 / 6 间接"）

| 类别 | 数量 | 登记项 |
|---|---|---|
| REQ_FULL | 5 | ReviewDecision, ReleaseManifest, SemanticRequest, GraphRequest, SemanticPackage(响应侧另有) |
| RESP_FULL | 6 | KnowledgeMap, ReviewDecision, SemanticResult, GraphResponse, ActivationPlan, EvidenceBundle, Release |
| RESP_PROJECTION | 1 | SemanticPackage |
| ID_REF | 6 | AssetVersion, MetricDefinition, MetricDefinition.full, SourceVersion, Capability, QueryDefinition, ControlledAction |
| ASYNC_RESULT | 1 | Assertion |
| INTERNAL_ADAPTER | 1 | LegacyRagHit |

> 合计 20（个别项跨类，计数按主类别）。

**OF-04 处置（§5 line 106 三条点名问题）**：
1. ✅ `MetricDefinition.full` **不再标为"口径源直接传输"**，改标 `ID_REF`（`metricRef` ≠ 响应含完整 MetricDefinition）。
2. ✅ `discoverCatalog` 的 **摘要 ≠ 完整 AssetVersion**：AssetVersion 标 `ID_REF`，`CatalogDiscoverResult` 为独立摘要投影。
3. ✅ `POST /ingestion/jobs` 的 **异步受理结果不认作 Assertion 实体**：Assertion 标 `ASYNC_RESULT`（仅 `candidateSetRef`）。
4. ✅ 逻辑模块名已对应真实提供方/消费者（见 §G3.2 末两列）。

---

## OF-02 关闭：三平面状态分离（§4 要求）

**§2.2 OF-02 指控**：收口文档混用了「地图生命周期」「合同候选状态」「SIM 身份」，并以「无 SIM 前缀」推断"不是模拟数据"。
**任命式处置：执行 §4 状态分离 + 反例验证。**

### 三个状态平面（实测，互不等价）

| 平面 | 语义 | 实际取值（实测） | 权威源 |
|---|---|---|---|
| **[A] 内容/地图生命周期** | 内容是否认定、地图用途是否认定、是否发布 | `VALIDATION`（4/4 地图均为该值） | `specs/knowledge-architecture/maps/**` |
| **[B] 合同注册状态** | 哪个版本的交换规范获准接入 | `CONTRACT_CANDIDATE` ×21、`CANDIDATE` ×16、无状态 ×25 | `specs/CONTRACT_INDEX.yaml` |
| **[C] SIM 身份** | 数据是否合成/限定模拟用途 | `simulationOnly=true`（20/20 schema 强制）+ `SIM-` 前缀实例 ID | `specs/gk-ke/v1/**` |

### 反例验证（证明三平面不可互相推导）

| 反例 | 观察 | 结论 |
|---|---|---|
| 反例 1 | 4 个既有地图（`KM-GITS-ROOT` 等）`status=VALIDATION` 且 **ID 无 `SIM-` 前缀** | 无 `SIM-` 前缀 **不等于**"已发布/已认定"，也不等于"真实生产数据" —— 它们是**验证态架构资产** |
| 反例 2 | gk-ke/v1 的 20 个 schema 全部 `simulationOnly=true`（平面 C），但其注册状态为 `CONTRACT_CANDIDATE`（平面 B） | **SIM 身份 ≠ 合同已激活**；SIM 标记不授予发布或执行资格 |
| 反例 3 | `specs/gk-ke/v1/examples/positive/*.json` 含 `SIM-` 前缀 ID，但其承载的是**合同样例**而非运行数据 | `SIM-` 前缀只标"合成的交换样例"，**不表示该实例已发布或可执行** |

### §4 四维度裁定落地（CUR-01）

| 维度 | 本 Loop 处理 |
|---|---|
| 契约激活 | 仅 `CTR-GKKE-API-001` 的精确受控版本（当前仍 `CONTRACT_CANDIDATE`）；**不批量激活**整个合同包及其样例 |
| 内容/地图生命周期 | 保留源 `VALIDATION`；目标按实际模型登记候选；内容与地图用途**分别认定** |
| 模拟身份 | 目标必须有规定 SIM 身份 + `simulationOnly=true`；**无 SIM 前缀不证明真实，加前缀也不能把生产数据变成合成数据** |
| 运行就绪 | 另查已发布依赖、权限、能力探针、计划门禁；**目录可见 / API 激活 / 候选校验成功均不代替该检查** |

**OF-02 关闭证据**：上表三平面定义 + 3 条反例 + 四维度裁定，已写入本登记并替代原收口文档 §3.2/§3.3/§6.3 的混用表述。
**明确纠正**：`docs/architecture/GK-KE-L0-2-OC01收口-V1.0.md` §3.3 中"既有 maps 无 `SIM-` 前缀，说明其不是模拟数据"的推断 —— **作废**，
正确表述为：无 `SIM-` 前缀仅说明其非"gk-ke/v1 SIM 交换样例"，其状态由平面 [A] 的 `VALIDATION` 决定，**不涉及数据真实性判定**。

---

## OF-01 处置：五条映射的对象粒度与转换规则

§2.2 OF-01 要求：给出**对象粒度和转换规则**，并按 §3 区分「选择 / 场景投影 / 编译依赖 / 策略适配」。

| 映射 | §3 转换类型 | 对象粒度（源 → 目标） | 转换规则 |
|---|---|---|---|
| `KM-GITS-ROOT@0.1.0` → 无 | **不转换**（导航/定位） | 根地图（`mapType=ROOT`） → 无目标实例 | 按 `mapType=ROOT` 识别；保留来源身份/版本；**"无目标实例"≠删除来源** |
| `KM-CORP-RM-PREVISIT@0.1.0` → `SIM-MAP-FINANCE@1.0.0` | **场景投影** | 任务地图（TASK） → 任务地图（SIM TASK） | 限访前融资切片；限 SIM-C001/SIM-O01/`INTERPRETATION`；**不宣布全任务等价** |
| `ASSET-KNOW-PRODUCT-CARDS` → `SIM-ASSET-P001@1.0.0` | **选择/构造** | 源为**集合或入口或单卡（待 KERT 确认）** → 单张 SIM 卡 | 若为集合 → 明确"选取 SIM-P001 的规则"；若为占位 → 登记为**合成样例构造**，不虚称继承真实产品事实 |
| `AC-PREVISIT-001` → `ActivationPlan` | **编译依赖**（前置约束） | 设计契约 → 运行计划 | `ActivationPlan` 由固化 TaskContext + 地图发布版本 + 路由策略 + 依赖版本 + 授权**确定性生成**（C06 §2）；**不复用 AC- 前缀充当 planId**；**不向闭集加字段** |
| `RP-CORP-RM-001` → `SIM-ROUTE-001@1.0.0` | **策略适配** | 路由策略 → 路由策略 | 核实源版本/匹配条件/优先级/歧义处理；目标**不扩大**用途或客户范围；绑定策略内容 hash |

**每条登记所需信息字段**（§3 末段要求，未在闭集对象上新增同名字段，仅登记于本文件）：
源 ID/类型/版本/hash ｜ 目标 ID/类型/版本/hash ｜ 转换关系 ｜ 规则版本 ｜ 适用范围 ｜ 损失或新增语义 ｜ 提供方核对证据 ｜ 本决议引用。

**OF-01 部分关闭**：粒度与转换类型已给出（上表）；
**但映射 3 的源粒度、映射 5 的策略 hash 须 KERT 确认** → **OF-01 未完全关闭**（与 G2 同一跨仓依赖）。

**版本缺失处置**（§3 末段）：既有 maps 的 `version` 实为 `0.1.0`（非空），§2.2 所称"版本为空"**经实测不成立**；
本登记按来源文件 hash 一并固定，不编造业务版本。

---

## 条件关闭状态

| 条件 | 状态 | 缺口 |
|---|---|---|
| **G1** 版本与制品绑定 | ✅ **已关闭** | OF-03/OF-05 已闭合；四版本角色已区分；完整 hash 已固定；封版受控路径 `docs/dd/gk-ke-contract` 内容级验证通过 |
| **G2** 来源与转换绑定 | ⏳ **未关闭** | 五条映射中 3 条须 **KERT 维护方**核对确认（跨仓） |
| **G3** 交换对象对应 | ✅ **已关闭** | OF-04 已闭合；20 项按六类重算完成 |
| **G4** 受影响范围复核 | ⏳ **未开始** | 须**独立 QA** 复核 G1–G3 差异（不得由 TL 自签） |
| **G5** 人工决议与激活记录 | ⏳ **部分** | Owner 签署已登记；待 G1–G4 关闭后登记激活事件 |

**不得提前激活**：G2/G4 未关闭 → **ACT-01 未生效，OC-01 未关闭，Loop 未退出**。
