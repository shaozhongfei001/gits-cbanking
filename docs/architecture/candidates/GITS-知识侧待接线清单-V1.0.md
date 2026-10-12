# GITS 知识侧「待接线」清单（按能力分工判据）

```
STATUS       = DERIVED / NOT_AUTHORITATIVE（派生核对，非权威）
AUTHORITY    = Owner 口径（2026-09-16）：只有需要知识 / skill 的功能才切到 KERT；其余留在 GITS 本地库
OWNER_DECISION = 2026-09-16 三条裁决：①路由＝任务→地图映射（KERT 口径）②地图 SSOT 在 KERT ③激活合同引入 KERT
REVISION     = 同日按上述裁决更新 §五；追加 N-1 / ④ / N-3 / N-4 / N-5 五条补充裁决，并回填 §二（K-01~K-10）处置方向；N-2 经 Owner 确认后**关闭**（证据三层收口，§5.3）；§5.5 ① 补入**对账基准表**（3 份 AC-*.json 文件字节 sha256，口径=KERT `sha256_file`）；§5.5 ①② **已施工**（① 落 2 份副本 + 出处文件；② `domain/activation_contract.py` 完成），权威缺口已开 **CR-2026-001**；供给缺口已修（`_plan_items` + `validate_source` 纳入 `schema/activations/`，含纪律 8 / `contractCount` / CLI 输出）
BASELINE     = gits-cbanking HEAD 7116904（只读核对，未修改任何文件）
SCOPE        = GITS 侧属于「知识 / skill 能力」但当前无入口的组件
NOT TOUCHED  = evidence/ · specs/ · generated/（本次核对未写入、未修改）
```

> **为什么需要这份文件**
>
> 一次"无生产调用方"的排查里，我犯过一个口径错误：**把「前端页面不调」当成了「没人用」**。
> 结果把一批 **GITS 本地库功能服务**（claim / case / journey / interaction / evaluation）误判为"待清理"。
> 按 Owner 口径修正后：**本地库功能留在 GITS，不因无前端调用而废弃**；真正需要处理的只有**知识侧那几项**。
> 本文只列后者。

---

## 一、判据（先立规矩）

| 能力类型 | 归属 | 例子 |
|---|---|---|
| **本地库功能**（不涉及知识 / skill） | **留在 GITS** | 客户列表、经营旅程、主张（claim）、案件（case）、交互记录、评估 |
| **知识 / skill 能力** | **切到 KERT** | 访前准备、外联脚本、会面脚本、产品匹配、供应链图谱、交互记忆、产品解读、产品推荐 |

**实测吻合证据**（`SkillExecutionPort` 的全部生产消费者，无一例外都是知识 / 技能类）：

| 消费者 | 位置 |
|---|---|
| `SupplyChainGraphService` | `apps/api/…/service/SupplyChainGraphService.java:38/44` |
| `OutreachScriptService` | `apps/api/…/service/OutreachScriptService.java:35/40` |
| `MeetingScriptService` | `apps/api/…/service/MeetingScriptService.java:41` |
| `InteractionMemoryService` | `apps/api/…/service/InteractionMemoryService.java:29/33` |
| `ProductMatchingService` | `apps/api/…/service/ProductMatchingService.java:36` |
| `ServiceProposalService` | `apps/api/…/service/ServiceProposalService.java:51` |
| `KnowledgeDrivenPrevisitReportGenerator` | `apps/api/…/service/KnowledgeDrivenPrevisitReportGenerator.java` |
| `ProductRecommendationApplicationService` | `apps/api/…/service/ProductRecommendationApplicationService.java:67` |

反之，纯本地库的那批 Controller **没有一个是 `SkillExecutionPort` 的消费者** → 判据可执行、可判别。

---

## 二、待接线清单（核心）

判定口径：**生产调用方** = 非 `src/test`、非 `/target`、非类型定义文件、非 `@Bean` 工厂内部；仅出现在 import 或 Javadoc 不算。

| 编号 | 组件 | 定义位置 | 装配状态 | 生产调用方 | 判定 |
|---|---|---|---|---|---|
| **K-01** | `ActivationPlannerPort` / `DefaultActivationPlanner` | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/port/ActivationPlannerPort.java:13`；实现 `…/plan/DefaultActivationPlanner.java:42`（318 行） | ✅ 已装配 `apps/api/…/config/KnowledgeArchitectureConfig.java:183-197` | ❌ **无任何注入点**（全仓非 test 仅出现于 config 与自身定义） | **待接线** |
| **K-02** | `KnowledgeAssembler` | `apps/api/…/service/KnowledgeAssembler.java:19` | ✅ 已装配 `EngagementConfig.java:271-277` | ❌ 仅命中定义 + `@Bean` 工厂（已抽验） | **待接线** |
| **K-03** | `KnowledgeMapController`（`/api/v1/knowledge`） | `apps/api/…/controller/KnowledgeMapController.java`；端点 `/elements:42`、`/items/{knowledgeItemId}:50`、`/map:58`、`/items:75` | ✅ 默认注册（`:25-28` `gits.knowledge.enabled`，`matchIfMissing=true`） | ❌ 无生产前端消费者：`frontend/src/api/knowledge.ts` 唯一引用者是 `views/__tests__/KnowledgeMapView.spec.ts`；P38 真实页走 `engagement.ts:649 fetchAssembledKnowledgeMap`（`KnowledgeMapView.vue:76`） | **暴露但无消费者** |
| **K-04** | `SemanticQueryPort` | `modules/semantic-runtime/…/SemanticQueryPort.java:9` | ❌ **未装配**（无任何 `@Bean`） | ❌ 无（`apps/api/src/main`、`apps/worker` 零命中） | **未装配 · 移 KERT**（N-3） |
| **K-05** | `SemanticRepositoryPort` / `InMemorySemanticRepository` | `…/SemanticRepositoryPort.java:3`；`…/InMemorySemanticRepository.java:17` | ❌ 未装配 | ❌ 仅测试 | **未装配 · 移 KERT**（N-3） |
| **K-06** | `FailClosedSemanticQueryGuard` / `RegisteredSemanticQueryCatalog` | `…/FailClosedSemanticQueryGuard.java:17`；`…/RegisteredSemanticQueryCatalog.java:11` | ❌ 未装配 | ❌ 仅同簇内部引用 + 测试 | **未装配 · 移 KERT**（N-3） |
| **K-07** | `JenaSemanticRepositoryAdapter` | `adapters/semantic-jena/…/JenaSemanticRepositoryAdapter.java:19` | ❌ 未装配 | ❌ 仅测试 | **未装配 · 移 KERT**（N-3） |
| **K-08** | `CanonicalHash` / `CanonicalJson` | `modules/knowledge-architecture/…/hash/CanonicalHash.java:14`、`…/CanonicalJson.java:20` | ❌ 未装配 | ❌ 仅 `CanonicalHashGoldenTest.java:39/44` | **未装配（低优先）** |
| **K-09** | `PrevisitWorkflowService` | `apps/api/…/service/PrevisitWorkflowService.java:17`（类注释：访前报告 R1 + 60秒作战卡 R2 + 外联脚本 R3） | ✅ 已装配 `EngagementConfig.java:262-270` | ❌ 仅测试 `EngagementScenarioE2eIT.java:41` 的 `@Autowired`；未注入 `SkillExecutionPort` | **登记退役**（N-4 已裁） |
| **K-10** | `KnowledgeRuleController`（`/product`、`/policy-rule`、`/external-event`） | `apps/api/…/controller/KnowledgeRuleController.java`（类注释：产品目录 / 政策规则 / 外部事件管理） | ✅ 默认注册（`@RestController`） | ❌ 6 端点前端零引用、`specs/openapi` 未收录 | **知识侧**（N-5 已裁）；前置：先定本地 `product_catalog` vs KERT 产品卡谁权威 |
| **K-11** | `KnowledgeWikiService`（消费 `KnowledgeWikiPort` + `LlmClient`，`renderMap` 渲染"LLM 可读受控知识地图"） | `apps/api/…/service/KnowledgeWikiService.java:21`（类）、`:30`（端口字段）、`:33`（构造器） | ✅ 端口已装配 `KnowledgeArchitectureConfig.java:153` | ❌ **无注入者**：生产代码零引用；全仓仅自身定义 + `KnowledgeWikiServiceTest.java:26/40/52/79` | **登记待裁**：与 K-02/K-03 同批（退役 / 改消费 KERT）（2026-09-16 复核新增，见 §5.6） |

> **2026-09-16 裁决后的重定性**：K-01 / K-02 / K-03 属 GITS 知识架构模块；按 §五 裁决（地图 SSOT 在 KERT），其处置方向由「待接线」改为 **「非权威侧：改为消费 KERT 或登记退役」**。K-04~K-07（语义运行时）按 **N-3** 裁决**移 KERT**；K-09 按 **N-4** **登记退役**；K-10 按 **N-5** 新增为**知识侧**；**K-11 为 2026-09-16 复核新增**（画图取证时发现，归入 K-02/K-03 同批处置）。
>
> **一条修正**：本文档此前在个别表述中把 GITS 知识层模块说成"零应用消费者"——**不准确**。实测它有两个消费出口（`KnowledgeMapController` 的 `/api/v1/knowledge`、`KnowledgeAssembler`），但**两者本身都无调用方**（K-02/K-03/K-11）。准确定性是 **「有出口、出口不可达」**，即 §三 的「表面在用、实际不可达」。

**对照组 —— 同簇里"确实在用"的**（避免把整块误判为死代码）：

| 组件 | 调用方 |
|---|---|
| `OntologyPort`（→ `JenaOntologyAdapter`） | `DefaultActivationPlanner.java:62`（用 `:115`） |
| `RoutePolicyEvaluatorPort` | `DefaultActivationPlanner.java:58` |
| `RoutePolicyPort` | `DefaultRoutePolicyEvaluator.java:25` |
| `ActivationContractPort` / `AssetCatalogPort` | `DefaultActivationPlanner.java:59` / `:60` |
| `KnowledgeMapPort` | `KnowledgeMapController.java:34` + `DefaultActivationPlanner.java:61` |

---

## 三、连带问题：整条链「表面在用、实际不可达」

上面"对照组"的端口之所以显示**在用**，是因为它们的消费者**全部落在两个无入口的东西上**：

```
KnowledgeElementPort  (装配 KnowledgeArchitectureConfig.java:147-150)
        ├─▶ KnowledgeMapController.java:34         ──▶ /api/v1/knowledge ──▶ 无生产前端消费者
        └─▶ KnowledgeAssembler.java:24             ──▶ 零注入点

KnowledgeWikiPort     (装配 KnowledgeArchitectureConfig.java:152-155)
        └─▶ KnowledgeAssembler.java:24             ──▶ 零注入点
            （KnowledgeWikiService.java:33 亦引用本端口，但其自身消费者未核实）

ActivationPlannerPort ──▶（零注入点）
        └─▶ RoutePolicyEvaluatorPort / ActivationContractPort / AssetCatalogPort / OntologyPort
             └─▶ 这四个端口的"生产调用方"只有 DefaultActivationPlanner —— 即这条不可达链自身
```

**结论**：`modules/knowledge-architecture` 模块的端口**装配齐全、互相都在用**，但**从业务入口不可达**。这不是"端口坏死"，而是**接入点缺失**。

---

## 四、按判据排除的（明确不算"待接线"）

| 被排除项 | 排除理由 | 证据 |
|---|---|---|
| `/api/claim`、`/api/case`、`/api/journey`、`/api/interaction`、`/api/evaluation` | **本地库功能面**，按判据留在 GITS | 其中 `/api/claim/case/{caseId}` 有前端生产调用（`engagement.ts:406` → `JourneyTimeline.vue:229`）；`/api/claim/case/{caseId}` 与 `/api/interaction?caseId=` 在平台验收清单内（`scripts/e2e-29-endpoints.sh:134` / `:146`） |
| `OracleSourcePort` 集群（含 `oracleDataSource` / `jdbcOracleSourceAdapter`） | 已有**既有废弃流程**在跑 | `loops/P38-oracle-deprecation/LOOP.yaml`（`status: blocked`，等 KERT 侧能力交付） |
| `ApiKeyValidator` | **疑似有意的启动校验**（`@Profile("prod")` 存在性校验），非缺口 | `SecurityConfig.java:68` |
| `InMemoryEventBridge` | 非知识侧（事件桥），且是否死链**未核实** | 自身文件 `:15` |
| `ProdConfigValidator`、`CrmHealthIndicator`/`LlmHealthIndicator`/`OracleHealthIndicator` | 框架回调（`ApplicationRunner` / actuator），非缺口 | — |
| `/api/v1/seed-data`（`SeedDataController`） | 运维/演示面；且 prod/staging 下**不注册**（`gits.seed.enabled` 无 `matchIfMissing`） | 类注解 `SeedDataController.java:18` |
| `/api/v1/architecture/status` | 运维面 | `ArchitectureStatusController.java:11` |
| ~~`KnowledgeRuleController`~~（**已改判，移出本表**） | 原判"端点为本地库 CRUD"；**Owner 2026-09-16 改判为知识侧**，已进入 §二 **K-10** | N-5 裁决 |

---

## 五、Owner 裁决记录（2026-09-16）

| 编号 | 裁决项 | 裁决结果 |
|---|---|---|
| **D-1** | "路由"的定义 | **＝任务 → 地图映射（KERT 口径）**。GITS 侧 `RoutePolicy` 的 4 种 mode（`ONTOLOGY_FIRST` / `MAP_FIRST` / …）**不是"路由"**，属另一概念（取材顺序） |
| **D-2** | 地图 SSOT | **在 KERT**。依据：`KnowledgeMapRegistry` 是运行时真调（`skills.py:654`），且对外提供 `GET /v1/knowledge-maps`、`POST /v1/routing/plan` |
| **D-3** | 激活合同 | **引入 KERT**。KERT 地图的 `activationContractRef` 字段已预留（当前留空，地图 notes 自述"未引入激活合同，不虚构绑定"） |

> 裁决来源：Owner 于 2026-09-16 对本文原 §五 待决项的口头裁定。本文按原文记录，**不做引申**。

### 5.1 裁决的连带影响（需后续处置，均附证据）

| 影响面 | 具体影响 | 证据 |
|---|---|---|
| **GITS `RoutePolicy` 语义需重新定位** | 4 种 mode 不再是"路由"，需改名或改挂靠（建议挂到**激活合同**——合同本就是"怎么取材 / 给什么"的授权清单） | `specs/knowledge-architecture/routes/RP-CORP-RM-001.json`（`defaultMode` + 4 条 mode 规则）；`generated/knowledge-architecture/route-policy.schema.json` |
| **GITS 知识地图降为非权威** | `specs/knowledge-architecture/maps/*`、`KnowledgeMap record`、`KnowledgeMapPort` 由"权威定义"降为"非权威"；处置只有两条：改为**消费 KERT**（`GET /v1/knowledge-maps`，GITS 目前全仓不调）或**登记退役** | `modules/knowledge-architecture/…/KnowledgeMap.java:12-26`；`…/port/KnowledgeMapPort.java:14/16`；GITS 全仓搜 `/v1/knowledge-maps`、`/routing/plan` **零命中** |
| **激活合同需在 KERT 落受治理副本** | 与 `ontology_reference`（只钉哈希、不带内容）**不同**：激活合同 KERT **需要内容**（据此决定资产 / skill / 上下文预算 / 人工闸门），不能只记哈希 → 需落副本 + provenance（来源合同号 + 内容 sha256），并纳入既有机械核对 | KERT `90_control/` 现有 `catalog/`、`schema/`（内含 `route_policy.json`、`ontology_reference.json`）；KERT `knowledge_map.py:66/196` 已把 `activationContractRef` 列为必填键 |
| **资产层级**（**已裁** → 以合同为准） | KERT 地图资产是 `KI-*`（7 条）；GITS 合同资产是 `ASSET-*`（9 个）。裁决：**以合同为权威**定资产集合与必需性，地图 `assetRefs` 降为「知识条目清单」，并在校验器加机械核对（地图 ⊆ 合同展开条目） | KERT `KM-CORP-RM-PREVISIT.json` `assetRefs` vs GITS `AC-PREVISIT-001.json` `activations` |
| **契约侧不变** | 激活合同在 GITS 已是契约（`owner=activation_contract_owner`，`consumers=activation_planner`），引入 KERT **不改 `specs/` 权威源** | `specs/CONTRACT_INDEX.yaml:307-318`（`CTR-ACTIVATION-001`）；`generated/knowledge-architecture/activation-contract.schema.json` |

### 5.2 同日补充裁决（Owner 2026-09-16）

| 编号 | 裁决项 | 裁决结果 |
|---|---|---|
| **N-1** | 激活合同在 KERT 控制面的副本落点 | **`90_control/schema/activations/`**。理由：与 `route_policy.json`、`ontology_reference.json`、`knowledge_sources.json` 同属「控制面声明」容器；合同是多份（现有 3 份），子目录避免与既有文件混层 |
| **④** | 资产层级以谁为准（合同 9 个 `ASSET-*` vs 地图 7 条 `KI-*`） | **以合同为权威**：由合同定资产集合与必需性；地图 `assetRefs` 降为「知识条目清单」；**校验器加机械核对（地图 ⊆ 合同展开条目）** |
| **N-3** | 语义查询运行时的处置 | **移到 KERT**（作为知识能力）。注：KERT 的图是 **Kùzu 属性图、不做 RDF/SPARQL** → 这是**新造能力**而非搬迁；GITS 侧 `FailClosedSemanticQueryGuard` / `RegisteredSemanticQueryCatalog` 作为 migrate-out **源**保留，期间不得标记为已启用 |
| **N-4** | `PrevisitWorkflowService` 定性 | **登记退役**（归属：被 KERT 实现取代的本地实现）。按 `loops/P38-oracle-deprecation` 规范**只标 `migration_status`、不物理删除** |
| **N-5** | `KnowledgeRuleController` 归类 | **归知识侧**，进 §二 待接线清单（**K-10**）。前置：须先定「本地 `product_catalog` 表 vs KERT `03_core` 产品卡」谁权威 |

> 以上五条是 §5.1 的直接收口；实施顺序见 §5.5。

### 5.3 仍待定 / 已关闭

| 编号 | 状态 | 结论 | 证据 |
|---|---|---|---|
| **N-2** | ✅ **已关闭**（Owner 2026-09-16 确认） | "取材顺序"（原 mode）**随激活合同进 KERT，无需新挂靠**；**禁止**把 mode 写进 KERT 的 `route_policy.json` | ① `activation-contract.schema.json`：`routeMode` 在 `required`，枚举恰 4 种（`MAP_FIRST` / `ONTOLOGY_FIRST` / `MAP_THEN_ONTOLOGY` / `ONTOLOGY_THEN_MAP`）；② 三份合同 `routeMode` 与 `RP-CORP-RM-001` 规则逐条一致；③ KERT `knowledge_map` / `route_policy` / `activation_plan` **mode 命中 0** |

> **N-2 关闭带来的机械约束（无需额外护栏）**：KERT 策略解析器对未声明字段是 **fail-closed 拒绝**而非静默忽略——`route_policy.py:142-144` 抛 `SchemaValidationError("[{source}] 含未声明字段（拒绝静默忽略）")`。因此任何"把 mode 塞进 KERT 策略"的改动都会直接失败，这是**代码级**保证，不依赖文档约定。
>
> **当前无其它待定项。**

### 5.4 原待决项（存档）

| 编号 | 原决策项 | 现状 |
|---|---|---|
| D-1 | `modules/knowledge-architecture` 归属：接入 KERT 还是保留影子？ | **已裁**（见上，地图 SSOT 在 KERT） |
| D-2 | 语义运行时去留 | 转入 **N-3** → **已裁：移 KERT** |
| D-3 | `/api/v1/knowledge` 契约已交付无消费者：标 `migration_status` 还是补消费者？ | 受裁决②影响，转入 **N-1/N-2 的连带处置** |
| D-4 | `PrevisitWorkflowService` 定性 | 转入 **N-4** → **已裁：登记退役** |
| D-5 | `KnowledgeRuleController` 定性 | 转入 **N-5** → **已裁：归知识侧（K-10）** |

### 5.5 实施顺序（施工单 · 按 N-1 / ④ / N-3 / N-4 / N-5 裁决）

| 步 | 动作 | 落点 | 验收点 |
|---|---|---|---|
| **①** | 落受治理副本 | ~~在 KERT 工作区建 `90_control/schema/activations/`，放入 `AC-*.json`（现有 3 份）~~ → **已完成 2/3**：`examples/bank-front-knowledge-maps/90_control/schema/activations/`（2 份副本 + `PROVENANCE.md` 出处） | ✅ 2 份与基准**逐字 MATCH**（字节精确复制）；第 3 份 `AC-PREVISIT-001.json` 因**权威缺口被拒收**（`CR-2026-001`） |
| **②** | 写合同解析器 | ~~建议落在 `src/kert/domain/`~~ → **已完成**：`src/kert/domain/activation_contract.py`（+ `tests/unit/test_activation_contract.py`，44 用例） | ✅ 与地图解析器同构（`code`+`allowed` 拒绝码）；unknown 字段拒绝＝权威 `additionalProperties:false` 的**直接映射**；默认拒绝 / 歧义拒绝覆盖；回归 **1008 passed** |
| **③** | 写校验器 | 校验四类：`taskType` 与地图 `tasks` 一致；**`routeMode` 合法（枚举 4 种，N-2 已关闭：mode 唯一归宿即本字段）**；`assetIds` 可解；`skills` 在 `registry()` 内；并含 **④ 的机械核对（地图 `assetRefs` ⊆ 合同展开条目）** | 均为硬校验，失败即 fail-closed |
| **④** | 填入计划预留槽位 | `activation_plan.py:243` 的 `"activationContract": None` → 真实取值（形如 `<contractId>@sha256:<哈希前16>`）；同步改地图 `notes` 中"未引入激活合同"表述并按惯例升版本 | `versions.activationContract` 非空；`replay_matches` 仍成立；`test_control_plane_consistency.py` 通过 |

> **§5.5 ①② 施工回执（2026-09-16）**
>
> - **① 只落 2 份**（Owner 裁定）：`AC-FACT-RECONCILIATION-001.json`（1652B）与 `AC-PRODUCT-RECOMMEND-001.json`（1740B），**字节精确复制**、哈希与基准逐字 MATCH；出处（来源合同号 + 权威路径 + sha256）见同目录 `PROVENANCE.md`。第 3 份被 **②** 严格拒收——权威缺口见 `CR-2026-001`。
> - **② 新增模块**：`domain/activation_contract.py`，导出 `parse_activation_contract` / `load_activation_contract_file` / `contract_files` / `ActivationContractRegistry` / `contract_key`（后者即 ④ 的 `<contractId>@sha256:<哈希前16>` 形态）。严格度策略：`preconditions` / `context` 只校验**已知子字段**、未知接受（权威仅声明 `type: object`）；其余未声明字段一律拒收。
> - **✅ 供给缺口已修（原"施工单缺一步"）**：`application/provision.py` 的 `_plan_items` 是**显式白名单**，原先不含 `schema/activations/` ⇒ 副本只存在于受治理源工作区，运行时工作区经 provision 后拿不到副本，② 的消费方会一律以 `ACTIVATION_CONTRACT_NONE_REGISTERED` 默认拒绝。现已把 `activations/AC-*.json` 同时加入 **`_plan_items`（第 5 类供给项）** 与 **`validate_source`（第 6 步）**，口径与纪律 7 一致：**缺失不报错、非法（含同 ID 注册表冲突）即中止全量供给**；模块 docstring 新增**纪律 8**；`contractCount` 已写入 `ProvisionResult` / `to_dict` / 留痕 / CLI 输出。`PROVENANCE.md` **不随供给搬运**（运行时出处由留痕逐份 `sha256` 承担，已在 docstring 显式说明）。
>
> **§5.5 ① 对账基准（2026-09-16 实测 · 文件字节 sha256）**
>
> **口径依据**：`specs/CONTRACT_INDEX.yaml:522` 记载 "content_hash 算法沿用 KERT MANIFEST"。KERT `domain/hashing.py` 提供三种口径（`sha256_hex` 数据 / `sha256_file` 文件字节 / `md_semantic_sha256` Markdown 语义）；本表采用 **`sha256_file`（文件字节）**，与既有钉值先例 `ontology_reference.py:111` 的校验口径一致。
>
> | 合同 | 文件字节 sha256 | 字节 |
> |---|---|---|
> | `AC-FACT-RECONCILIATION-001.json` | `9f7e46c563fb83c659ccd346524ad1c6d1c5c4545b0ebaa9b07398e5c36b83a9` | 1652 |
> | `AC-PREVISIT-001.json` | `d72ff9fc8bbc07e484910f75d6f34dd562fea50759a04b0e6b49d769c4f11984` | 2162 |
> | `AC-PRODUCT-RECOMMEND-001.json` | `0b7545f80dd5697ca0ffa349b2b34c382c9b2cb8ce1b70f97b2e1480fe7173dd` | 1740 |
>
> **重算条件（验收前置）**：基准的作用是"**副本与 GITS 一致**"。若在副本落地**之前** GITS 侧 `specs/knowledge-architecture/activations/` 发生任何变更，须**重算本表**再据以验收；否则会出现"副本忠实于旧版、基准已过期"的假通过。
>
> **N-3（移 KERT）的施工含义**：KERT 侧需**新造**"语义查询执行"能力（Kùzu 属性图 ≠ RDF，无 SPARQL 引擎）；GITS 现有 `FailClosedSemanticQueryGuard` + `RegisteredSemanticQueryCatalog` 作为 migrate-out **源**保留至新能力交付，期间**不得标记为已启用**（其自身注释已声明"不连接任何生产端点"）。
>
> **N-4（登记退役）的施工含义**：按 `P38` 规范只标 `migration_status`，**不物理删除**；同簇的 `WritableCommitmentRepository` 仍被其它在用组件使用，不受影响。
>
> **N-5（归知识侧）的前置**：先定「本地 `product_catalog` 表 vs KERT `03_core` 产品卡」的权威归属，否则 K-10 的改造方向无法确定。

> 本施工单**不改 `specs/` 权威源、不手工编辑 `generated/`**；若涉及契约变更，按 `docs/governance/CHANGE-CONTROL-PROCESS.md` 走流程。

| 编号 | 决策项 | 为什么需要决策 |
|---|---|---|
| **D-1** | `modules/knowledge-architecture` 的归属：**接入 KERT**，还是保留为 GITS 侧影子实现？ | 与"两套知识地图谁是 SSOT 未定"同源（`KM-CORP-RM-PREVISIT` 两仓同名、策略引用不同：`RP-CORP-RM-001` vs `RP-KERT-BANKFRONT-001`） |
| **D-2** | 语义运行时的去留：`SemanticQueryPort` / `SemanticRepositoryPort` / `FailClosedSemanticQueryGuard` / `JenaSemanticRepositoryAdapter` 是**装配启用**还是**明确不启用**？ | 目前连 Bean 都没有；若不启用，应登记状态而非留作"看起来在跑" |
| **D-3** | `KnowledgeMapController`（`/api/v1/knowledge`）契约已交付（CTR-KELEM-001）但无消费者：标 `migration_status` 还是补消费者？ | 参照 `P38-oracle-deprecation` 的规范：**合同条目只标状态、不物理删除** |
| **D-4** | `PrevisitWorkflowService` 定性：知识侧（应切 KERT）还是本地流程？ | 决定它进"待接线"还是"排除" |
| **D-5** | `KnowledgeRuleController` 定性：它的三个资源面属本地库还是知识侧？ | 决定是否进"待接线" |

---

## 六、取证方法（可复现）

**判定口径**（本文全部结论按此口径）：

- **生产调用方** = 在 `apps/**/src/main/**`、`modules/**/src/main/**`、`adapters/**/src/main/**` 中被**注入或调用**。
- **不算**：`src/test/**`、`/target/**`、类型定义文件本身、`@Bean` 工厂内部、仅 import 或 Javadoc 引用。

**复现命令**（在 `/home/szf/dev/gits-cbanking` 执行）：

```bash
# 1) 装配点：列出某模块的全部 @Bean
grep -rn "public .*Port \|@Bean" apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java

# 2) 生产调用方（排除 test / target）
grep -rn "ActivationPlannerPort" --include=*.java apps modules | grep -v "/target/" | grep -v "src/test/"

# 3) 前端是否真有消费者（注意 baseURL 拼接）
grep -rln "api/knowledge" frontend/src | grep -v "__tests__\|\.spec\.ts"

# 4) 平台验收面收录了哪些端点
grep -n "api/" scripts/e2e-29-endpoints.sh
```

**本次抽验记录**（4 项"零调用方"断言，均已复核成立）：

| 组件 | 抽验命令结果 |
|---|---|
| `ActivationPlannerPort` | 非 test 命中仅：`KnowledgeArchitectureConfig.java:13/184`、接口与实现定义 |
| `KnowledgeAssembler` | 非 test 命中仅：`EngagementConfig.java:273/276`、自身定义 |
| `PrevisitWorkflowService` | 非 test 命中仅：`EngagementConfig.java:263/267`、自身定义 |
| `OracleSourcePort` | 非 test 命中仅：`StubOracleSourceAdapter`、`EngagementConfig.java:59/379`、接口定义、`OracleSourceAutoConfiguration` |

---

## 七、非声明

- 本文是**派生核对记录**，**未写入 `evidence/`**、**未修改 `specs/`**、**未手工编辑 `generated/`**。
- **不替代** `specs/` 合同 SSOT，**不作为 Gate / ADR 依据**。
- **不代表 PRODUCTION_READY，不是 QA_PASS**。本文证明的是"按给定口径的检索结果"，不等于业务正确性。
- 本文**不提出任何删除动作**。所有"待接线"项的处置须先经 §五 的 Owner 决策，并（如涉及代码移除）按 `docs/governance/CHANGE-CONTROL-PROCESS.md` 与 `loops/P38-oracle-deprecation/LOOP.yaml` 的既有规范执行。
- §五 的**裁决结果来自 Owner（2026-09-16）**，本文按原文记录；§5.1 的连带影响与 §5.2 的待定项是**基于代码证据的推论**，不构成裁决本身。
- 遗留待核实：`KnowledgeWikiService` 自身的消费者；`InMemoryEventBridge` 是否死链；`WritableClaimLifecycleRepository` 的消费方。
