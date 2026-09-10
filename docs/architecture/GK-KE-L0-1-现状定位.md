# GK-KE 系统群 L0-1 现状定位

> 依据：`GK-KE-CONTRACT-V1.0/00_项目总契约.md` §10 与 `contracts/C08_实施验收与变更合同.md` L0-1。
> 角色：Tech Lead（只做现状定位与差异分析，不写 Feature 实现）。
> 日期：2026-09-10。状态：**L0-1 候选，待 Owner 确认变更范围**。

## 0. 结论摘要

- 随包离线验证器：**125 passed / 0 failed**（`OFFLINE_AUTHOR_SELF_CHECK`，非独立 QA、非服务 E2E）。
- 现行仓库已具备 **P20/DKES/PI-0 知识架构雏形**（7 个受控 schema、8 个 Port、`knowledge-architecture` 与 `semantic-runtime` 两个模块、111 个测试类），但与 GK-KE V1.0 的 8 份候选合同存在**结构性差异**，不是字段改名能弥合。
- 候选包状态为 `CONTRACT_CANDIDATE`、`simulationOnly=true`、`productionReady=false`。**不得覆盖** P20/DKES/PI-0，不得手改 `generated/`，不得把离线样例当能力 ready。
- 建议：按 C08 的 L0-2 起，以**新增候选命名空间 `gk-ke/v1` + 适配映射**方式激活，逐 Loop 小步推进；CR-01~08 中 **CR-03（审核发布）、CR-04（分析语义）、CR-05（RAG/图）、CR-07（模拟数据）为主要新增面**，CR-02/CR-06 为**增强面**，CR-01/CR-08 为**约束/治理面**。

## 1. 固定基线（HEAD / 版本 / 包）

| 项 | 值 |
|---|---|
| 仓库 | `/home/szf/dev/gits-cbanking` |
| 分支 | `feature/PI-ARCH-L10-L13` |
| HEAD | `46e1b00575a1bfe1e609462220c43abca414c3b2` |
| 工作区 | 215 个未提交改动（**未纳入本次结论，需 Owner 先决定是否提交/隔离**） |
| 契约包 | `gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/`（已解压） |
| 包自检 | `acceptance/package_self_check.json`，验证器 `passed=125 failed=0` |
| 候选命名空间 | `gk-ke/v1`，14 Schema / 14 正例 / 28 Schema 负例 / 36 验收项（T01–T36，全 `PLANNED_NOT_EXECUTED`） |
| 模拟能力 | `SIM-CAP-INTERPRET`：`productionProbePassed=false`、`status=SIMULATED_CONTRACT_ONLY` |

> 注意：总契约要求固定"三个仓库 HEAD"。当前工作区只挂载了 `gits-cbanking`；`GITS-KERT` 与公共核心仓库未在本机定位到独立工作树。**L0-2 前需 Owner 提供另两个仓库路径或确认其边界由本仓承载。**

## 2. 现行合同 / Schema / 接口基线

### 2.1 受控合同（`specs/CONTRACT_INDEX.yaml`，JSON 结构）

知识相关已注册条目：

| 合同 ID | 权威源 schema | 说明 |
|---|---|---|
| `CTR-KMAP-001` | `knowledge-map.schema.json` | 知识地图 |
| （同组） | `asset-manifest.schema.json` | 资产清单 |
| （同组） | `activation-contract.schema.json` | 激活契约 |
| （同组） | `route-policy.schema.json` | 路由策略 |
| （同组） | `activation-plan.schema.json` | 激活计划 |
| （同组） | `skill-descriptor.schema.json` | 技能描述符 |
| `CTR-KELEM-001` | `knowledge-element.schema.json` | 知识元素 |
| `CTR-PR-API-001` | （产品解读/推荐 API） | 含 L03 v1.1-candidate：knowledgeState/UNKNOWN 中和不变式 |

### 2.2 现行 7 Schema 顶层字段（对照基准）

| 现行 schema | required 关键字段 |
|---|---|
| knowledge-map | schemaVersion, mapId, name, version, status, mapType, entrypoints, domains, defaultPolicy, routePolicyRef（+assetRefs/skillRefs/activationContractRefs/maxInitialTokens） |
| asset-manifest | schemaVersion, assetId, assetType, name, domain, version, status, source, governance, capabilities, activation, evidence |
| activation-contract | schemaVersion, contractId, version, taskType, routeMode, preconditions, activations, semanticQueries, ruleChecks, skills, context, humanGates, failurePolicy |
| activation-plan | schemaVersion, planId, taskId, taskType, routeMode, versions, selectedAssets, semanticQueries, ruleChecks, skills, context, permissionDecisionId, trace |
| route-policy | schemaVersion, policyId, version, defaultMode, defaultDecision, rules |
| skill-descriptor | schemaVersion, skillId, name, version, owner, status, implementationType, inputs, outputs, *Dependencies, humanGatePolicy, sideEffectPolicy |
| knowledge-element | schemaVersion, elementId, name, kind, knowledgeItemId, content, source, relatedRules, status |

### 2.3 模块与 Port（既有能力证据）

- `modules/knowledge-architecture`：领域对象 6（KnowledgeMap/AssetManifest/ActivationContract/ActivationPlan/RoutePolicy/KnowledgeElement）+ Port 8（KnowledgeMapPort、AssetCatalogPort、ActivationContractPort、ActivationPlannerPort、RoutePolicyPort、RoutePolicyEvaluatorPort、KnowledgeElementPort、KnowledgeWikiPort）+ 内存实现（InMemoryKnowledgeStore、DefaultActivationPlanner、DefaultRoutePolicyEvaluator）。
- `modules/semantic-runtime`：SemanticPackage、SemanticQueryPort、SemanticRepositoryPort、RegisteredSemanticQueryCatalog、**FailClosedSemanticQueryGuard**（已是 fail-closed 语义查询守卫）、InMemorySemanticRepository、SemanticQueryRequest/Result。
- `modules/human-action`：`ControlledAction`（operational-ontology）、ControlledActionService（受控动作 + 审计）。
- 相关 Controller：KnowledgeMapController、KnowledgeRuleController、ProductInterpretationController、ProductRecommendationController、ProductKnowledgeVersionController、V14KertIntegrationController、SupplyChainGraphController、EvidenceVersionController、HumanGateController、AuditTraceController 等。
- OpenAPI 已暴露的相关端点（节选）：`GET /engagement/customer/{id}/knowledge-map`、`POST /engagement/customer/{id}/product-matching`、`GET /api/v1/product-knowledge/{pid}/interpretation`、`POST /engagement/supply-chain-graph`、`GET /evidences/{id}/versions`、`/knowledge-rules`、`/products/versions`。
- 测试基线：全仓 111 个 `*Test/*IT`；知识/语义相关单测 6 个（KnowledgeMapTest、RoutePolicyTest、DefaultActivationPlannerTest、SemanticPackageTest、FailClosedSemanticQueryGuardTest、InMemorySemanticRepositoryTest）。

## 3. 候选 gk-ke/v1 14 Schema 字段（新画像）

| 候选 schema | 合同 | required 要点 |
|---|---|---|
| SemanticPackage | C01 | contractVersion, simulationOnly, packageId, version, ownerSystem, types, imports |
| AssetVersion | C02 | …, assetId, version, **assetClass(4类)**, kind, title, ownerSystem, ownerRole, contentRef, contentHash, coreVersion, scope, purposeFlags, lifecycle, dependencyRefs |
| KnowledgeMap | C02 | …, mapId, version, releaseId, taskTypes, entryNodes, routePolicyRef, nodes, edges, purpose, scope |
| Assertion | C03 | …, assertionId, subjectRef, predicate, value, modality, **knowledgeState**, validTime, scope, evidence, extractionRunId |
| ReviewDecision | C03 | …, decisionId, targetId, targetVersion, targetHash, reviewerPrincipal, authorPrincipal, reviewerRole, decision, purpose, reason |
| ReleaseManifest | C03 | …, payload, payloadHash, approvalRefs, projectionStates, status |
| MetricDefinition | C04 | …, metricId, version, ownerSystem/Role, approvalRef, baseGrain, aggregationGrain, calendarPolicy, timezone, currencyPolicy, unit, nullPolicy, rounding, queryId, mappingVersion, formula |
| SemanticRequest | C04 | …, metricId, metricVersion, customerId, period, snapshotId, currency, purpose |
| SemanticResult | C04 | …, value, currency, unit, period, asOf, snapshotId, mappingVersion, queryId, queryRunId, permissionDecisionRef, completeness, calculationDetailRef, warnings |
| GraphRequest | C05 | …, queryId, queryVersion, entityId, releaseId, maxHops, maxNodes, scope |
| GraphResponse | C05 | …, queryId, projectionVersion, paths, truncated, warnings |
| ActivationPlan | C06 | …, planId, taskId, mapRef, releaseId, coreVersion, catalogRevision, routePolicyVersion, assetRefs, capabilityRefs, queryRefs, steps, permissionDecisionRef, purpose, scope, budget, **planHash** |
| EvidenceBundle | C06 | …, bundleId, planId, releaseId, permissionDecisionRef, facts, claims, evidence, ruleResults, unknowns, conflicts, scope |
| ControlledAction | C06 | …, actionId, taskId, actionType, customerId, parametersHash, confirmationRef, targetVersion, idempotencyKey, mode, purpose |

**横切字段（每个候选对象都有）**：`contractVersion="gk-ke/v1"`、`simulationOnly=true`（当前剖面）。

## 4. CR-01 ~ CR-08 差异分析

> 评级：✅已具备（可映射）／🟡部分具备（需增强）／🔴缺失（需新增）／⛔治理约束（非代码）。

### CR-01 系统边界与理论（C01）— 🟡 + ⛔
- 现状：模块分层（modules/adapters/apps）与"公共核心独立"方向一致；已有 `semantic-runtime` 公共语义包雏形。
- 差异：
  - 候选 `SemanticPackage` 用 `ownerSystem + types + imports` 显式声明跨系统语义包归属与依赖；现行 `SemanticPackage` 字段更偏注册表，**缺 ownerSystem/imports 的强约束与公共包破坏性变更门禁**（T03）。
  - 缺"源权威字段 KERT 拒绝写入"的系统级强制（T01）、同名不并户（T02）、声明≠事实（FORECAST 不转额度，T04）的**统一边界策略**——这些散落在各 Service，未在合同层声明。
- 建议：L0-2 补 C01 映射，定义 GITS/KERT/公共核心/银行源四系统的写权威矩阵；不急于改代码。

### CR-02 注册中心与知识地图（C02）— 🟡
- 现状：`CTR-KMAP-001` 七 schema 与候选高度同源（map/asset/activation/route/skill 都在）。
- 差异（字段级，需适配而非覆盖）：
  - 版本信封：现行 `schemaVersion` ↔ 候选 `contractVersion + simulationOnly`。
  - 资产：现行单字段 `assetType` ↔ 候选 **`assetClass`（四类闭集：RULE/KNOWLEDGE/SKILL/SEMANTIC_PACKAGE）+ `kind`**。总契约红线：**保留四类 assetClass，不得用 subjectCategory 替代资产枚举**。现行 assetType 值域需映射到四类。
  - 资产治理：候选新增 `ownerSystem/ownerRole/contentRef/contentHash/coreVersion/purposeFlags/lifecycle/dependencyRefs`；现行用 `governance/capabilities/activation/evidence` 嵌套，结构不同。
  - 地图：现行 `mapType/domains/entrypoints/defaultPolicy` ↔ 候选 `releaseId/taskTypes/entryNodes/nodes/edges/purpose/scope`。候选把地图建模为"绑定 release 的节点-边图"，现行为"域+入口"模型。
  - 激活计划：候选要求 `planHash`（规范化哈希，双入口同计划 hash 一致，T05）、`catalogRevision/routePolicyVersion/coreVersion` 版本三元组、`capabilityRefs`（未注册 skill → DEPENDENCY_UNRESOLVED，T06）；现行 plan 无 planHash，用 `versions/selectedAssets/trace`。
  - 目录越权（T07，标题/关系/计数不泄漏）：现行有 defaultPolicy=DENY，但缺"计数不泄漏"级别的测试。
- 建议：写双向字段映射表 + 适配器；保留现行 schema，新增 gk-ke/v1 候选，不替换。

### CR-03 自动构建审核发布（C03）— 🔴 主要新增
- 现状：有 KnowledgeElement、ProductKnowledgeVersion、EvidenceVersion、HumanGate、AuditTrace，但**没有**"抽取断言→人工/规则审核→发布清单→投影"的完整合同对象。
- 差异（候选三对象基本全新）：
  - `Assertion`：subjectRef/predicate/value/modality/**knowledgeState**/validTime/evidence/extractionRunId。支撑 T08（无原文→QUOTE_NOT_LOCATED）、T10（实体化冲突保留两来源+适用期）。
  - `ReviewDecision`：reviewer/author 双主体 + reviewerRole + targetHash，职责分离。支撑 T09（审批后篡改 hash 失配）。
  - `ReleaseManifest`：payload/payloadHash/approvalRefs/**projectionStates**/status。支撑 T18（半发布 active 指针不切换）、T19（撤销传播）、T20（执行环检测，relatedTo 导航环不误判）。
  - T21（来源文档夹带"调用转账工具"指令→只当数据）需要在抽取/装配层加 prompt-injection 数据隔离。
- 建议：这是工作量最大、风险最高的一块，单独立 Loop（建议 L2），先合同+负例，不接真实发布。

### CR-04 分析语义服务（C04）— 🔴 主要新增（指标治理）
- 现状：`semantic-runtime` 有 SemanticQuery 注册表 + fail-closed 守卫 + Request/Result，但**没有指标定义治理**（MetricDefinition）。
- 差异：
  - `MetricDefinition` 把口径固化为受控对象：baseGrain/aggregationGrain/calendarPolicy/timezone/currencyPolicy/unit/nullPolicy/rounding/queryId/mappingVersion/formula + approvalRef。
  - `SemanticResult` 强制 snapshotId/asOf/completeness/calculationDetailRef（历史时态，T16）、permissionDecisionRef。
  - 验收 T11–T16 全是硬指标：日均复算 2983333.33、关联放大不重复求和、双账户 200≠100、缺日 GRAIN_VIOLATION、多币种 CURRENCY_POLICY_REQUIRED、越权/历史快照拒绝。
- 建议：新模块或在 semantic-runtime 内新增 metric 子域；这些验收必须服务级 + 固定数据，离线样例不算数。

### CR-05 RAG 与图适配（C05）— 🔴 新增（且与本机 LightRAG 直接相关）
- 现状：**无任何 Kuzu/LightRAG/图存储 adapter**（`adapters/` 下无 graph/rag/kuzu/lightrag 目录）；有 SupplyChainGraphController 但是业务侧图，非知识检索适配。
- 候选：`GraphRequest/GraphResponse`（entityId/releaseId/maxHops/maxNodes → projectionVersion/paths/truncated/warnings）。
- 验收红线：
  - T22：旧 RAG 只返回答案无出处 → 不得编造证据，降级/拒绝。
  - T23：Kuzu **候选图/发布图隔离**，停服时必需图失败要明确拒绝；Kuzu 0.11.3 仅模拟候选、**未安装**。
  - T24：LightRAG **独立增益 A/B/C 固定题集**，报告 B→C 增益/成本/失败，不得拿 A→C 冒充图收益。
  - T25：跨权摘要泄漏 → 隔离/重建/关闭摘要，不能只滤引用。
- 与现状关系：本机已装 LightRAG 1.5.7 并导入了建行产品/规章，但那是**独立试验环境**，未经适配器接入 gits-cbanking，且当前语料不含 releaseId/scope 投影隔离。**接入必须走 Port+Adapter，且先满足 C03 发布投影与 C05 隔离，不能直连。**

### CR-06 运行与接口（C06）— 🟡
- 现状：有 ActivationPlanner、ControlledActionService、HumanGate、AuditTrace、CrmWriteback，方向一致。
- 差异：
  - `ActivationPlan` 候选要求 planHash + steps + budget + capabilityRefs/queryRefs（见 CR-02）。
  - `EvidenceBundle` 强制 facts/claims/evidence/ruleResults/**unknowns/conflicts** 分层——支撑 T26 三段式 UNKNOWN（用途或期限未知→UNKNOWN+补证清单，不直接推荐通过）。现行产品推荐 v1.1 已有 knowledgeState 中和（RC-PI-011），但 unknowns/conflicts 结构未合同化。
  - `ControlledAction` 候选要求 parametersHash/confirmationRef/targetVersion/idempotencyKey/mode——支撑 T27（未确认拒绝写回+审计）、T28（超时重复提交幂等对账）、T29（确认后撤权/撤销→执行前重校验）。现行 ControlledAction 字段需对照补齐。
- 建议：增强现有 human-action / planner，做字段映射与幂等键、执行前重校验。

### CR-07 模拟数据（C07）— 🔴 新增（工具与隔离）
- 现状：仓库**无 simulationOnly/SIM- 前缀**体系（grep 无命中）；有 scenario/seed 种子数据，但不是合同化的固定模拟数据包。
- 候选包自带：`simulation/`（seed_scenarios、documents、oracles、manifest）+ `tools/build_simulation.py`（标准库造数：主外键、借贷分录、每日余额、图关系、hash）。
- 验收：T30 主外键/借贷平衡/日终滚动；T31 文档-数据-图一致（提及≠持有）；T32 移除 simulationOnly 必须被拒；**T33 oracles 真值目录禁止进入检索语料**。
- 建议：把 C07 模拟数据作为独立 test fixture 源引入（SIM 前缀 + simulationOnly），与生产 seed 物理隔离；oracles 加管线拒绝规则。

### CR-08 实施验收与变更（C08）— ⛔ 治理
- 现状：有 Makefile（generate/check/backend-test）、CONTRACT_INDEX、generated 只读、独立 QA 角色规则，基础治理在。
- 差异：
  - T34：新闭集枚举/字段需消费者驱动测试 + 迁移批准，不覆盖旧索引。
  - T35：**跨语言 hash 一致**（Python 造数 / Java 服务）——需保存黄金规范化字节（sorted keys、ensure_ascii=false、紧凑分隔、NFC、金额字符串），做同值测试。
  - T36：最终服务验收 = 固定 HEAD 全链路 + 负例 + 恢复 + 独立签署 + Owner 决定。
- 建议：L0 阶段建立 hash 黄金字节夹具与 Java 侧规范化实现的对拍测试。

## 5. 风险与阻塞（需 Owner 决定）

1. **工作区 215 个未提交改动**：L0-1 基线固定在 `46e1b00`，但这些改动可能包含未完成的 PI-ARCH 工作。需 Owner 决定先提交、stash 还是另开分支，避免 L0-2 建在脏工作区上。
2. **三仓库只见到一个**：GITS-KERT 与公共核心仓库路径缺失，跨系统 ownerSystem 边界（CR-01）无法完全落地。
3. **候选合同尚未激活**：8 份合同都是 CONTRACT_CANDIDATE，L0-2 需要相应 Owner 逐一审批 CR 并补完整 OpenAPI，才能写实现。
4. **Kuzu 未安装、LightRAG 未适配**：CR-05 的 T23/T24 不能用现有 LightRAG 试验环境顶替。
5. **模拟数据不得进生产**：C07 数据入仓需明确 fixture 目录与隔离规则，避免误入 seed/迁移。
6. **hash 跨语言一致性**是隐性高风险点，建议最早做一个探针测试验证 Java/Python 规范化字节是否真能对齐。

## 6. 建议的 Loop 切分（供 Tech Lead 建 Loop，待 Owner 批准）

| Loop | 范围（合同） | 主要验收 | 依赖 |
|---|---|---|---|
| L0 | L0-1 现状定位（本文）+ L0-2 契约激活：引入 gk-ke/v1 候选 schema/正负例、CR 审批、字段映射、OpenAPI 骨架、hash 黄金字节探针 | T34、T35 探针 | Owner 清脏工作区、给三仓库边界 |
| L1 | CR-02 注册中心/地图适配（assetClass 四类、planHash、版本三元组、目录越权计数） | T05、T06、T07、T20 | L0 |
| L2 | CR-03 断言/审核/发布/投影（含 prompt 注入隔离、撤销传播） | T08、T09、T10、T18、T19、T21 | L1 |
| L3 | CR-04 指标语义（MetricDefinition + 固定数据复算） | T11–T16 | L0、C07 fixture |
| L4 | CR-06 运行接口（EvidenceBundle unknowns/conflicts、受控动作幂等/重校验） | T26–T29 | L1、L2 |
| L5 | CR-05 RAG/图适配（Kuzu 模拟图隔离、LightRAG 适配器 + A/B/C 增益、跨权摘要） | T22–T25 | L2 |
| L6 | CR-07 模拟数据入 fixture + 隔离（SIM/simulationOnly/oracles 拒绝） | T30–T33 | L0 |
| L7 | CR-01 边界强制（源权威写保护、同名不并户、声明≠事实） | T01–T04 | L1 |
| L8 | C08 全链路服务验收 + 独立 QA + Owner 签署 | T36 | 全部 |

> 每个 Loop 都遵守：合同先行 → `make generate` → `make check` → 负例 → 服务级测试 → 证据落盘；dev 只记 DEV_SELF_CHECK_PASS，独立 QA 才记 QA_PASS。

## 6.5 T35 跨语言 hash 一致性探针（已实测，排除风险）

在进入 L0-2 前，先用事实验证最高隐性风险 T35（Python 造数 / Java 服务的规范化 hash 必须一致）。

- 规范化算法（来自包 `tools/validate_package.py:17`）：`json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',',':'))` + SHA-256；字符串先 NFC。
- 黄金对象：候选正例 `examples/positive/AssetVersion.json`（含中文，588 规范化字节）。
- Python 侧 hash：`3e4a2d54815f5e499d28c0300c25e642bab51e80e23cee16f44c53c0e4bc1bcd`。
- Java 侧（JDK21 + Jackson 2.15.2 解析，自写规范化器：键按码点排序、紧凑分隔、中文不转义、NFC）：**字节逐字节一致（588=588），SHA-256 完全相同**。
- 结论：**T35 技术可行**。落地要点（供 L0 实现）：
  1. Java 不能直接用 Jackson 默认 `writeValueAsString`（含空格/转义差异），需自定义 `CanonicalJson`（排序 + `separators=(',',':')` + 不转义非 ASCII + 仅转义 JSON 必需控制符）。
  2. 排序须按 Unicode 码点（与 Python `sort_keys` 一致），不要用本地化 Collator。
  3. 金额一律字符串、禁止 NaN/Infinity；planHash 排除 planId/planHash 自身。
  4. 探针代码暂存 `/tmp/hashprobe/HashProbe.java`，L0 Loop 应把它固化为仓库内的黄金字节对拍测试（`*Test`，黄金字节入 test resources）。

## 7. L0-1 自检

- [x] 固定 HEAD/分支/包版本（§1）
- [x] 现行合同/schema/接口/测试基线（§2）
- [x] 候选 schema 字段画像（§3）
- [x] CR-01~08 字段级差异与既有能力证据（§4），未凭 PPT/文档宣称实现
- [x] 随包离线验证先跑（125/0），且明确其非服务 E2E、非独立 QA
- [x] 未覆盖 P20/DKES/PI-0、未手改 generated、未写 Feature 实现
- [ ] **待 Owner 确认变更范围（§5 阻塞项）后方可进入 L0-2**
