# GK-KE L0-2 OC-01 收口：版本对象对应（V1.0）

> 角色：Tech Lead（planning_review）｜Loop：`GK1-l0-2-contract-activation`｜日期：2026-09-12
> 条件来源：Owner 决议 `GK-KE-OWNER-001` → **OC-01 版本和对象对应**，关闭时点 = **L0-2 激活前**
> 依据：C08 §4 开放事项"现有仓库与合同真实版本 ｜ 关闭责任 TL，L0"
> 性质：**收口证据文档**。OC-01 的**正式关闭**仍需独立 QA 核查 + 相应 Owner 认可（本文件只提供 TL 侧证据）。

## 1. OC-01 原文与拆解

C08 §4 开放事项表：

| 事项 | 当前处理 | 关闭责任/阶段 |
|---|---|---|
| 现有仓库与合同真实版本 | 本轮未核查源码；独立候选命名空间 | TL，L0 |

L0-1 §6 已勾选三项、留一项未闭：

- [x] V1.0.2 三值锚点（HEAD/tree/ZIP）已固定
- [x] 三仓基线已识别
- [x] 实际 YAML/JSON 路径 + **地图 ID 版本映射（待 L0-2 细化，L0-1 输出概览）**
- [x] CR-01~08 差异与兼容映射
- [ ] 独立 QA 按现有职责核查（待收口）

**OC-01 的真正缺口**在第三项：**"版本和对象对应"** —— 即
**(a) 三仓真实版本锚点**、**(b) 地图 ID ↔ 版本 ↔ 对象的对应关系**、**(c) schema ↔ 端点 ↔ 消费者 的三方对应**。
本文件逐项补齐 (a)(b)(c)。

## 2. (a) 三仓真实版本锚点

| 仓库 | 路径 | 分支 | HEAD | 性质 |
|---|---|---|---|---|
| 主仓 | `/home/szf/dev/gits-cbanking` | `feature/GK-KE-L0-contract` | `597d6facdc120a9fbffc44cff116eab50bbb3367`（L0-2 开工基线） | git，权威源（specs + modules/adapters/apps） |
| KERT 实现仓 | `/home/szf/dev/Leibniz-KERT` | `feature/PI-ARCH-L10-L13` | `3b6640b993f4834d36833fa0bc3005d73768b594` | git，Python 服务（8107） |
| 文档仓 | `/home/szf/dev/gits-kert-docs` | — | 非 git（目录快照） | 文档承载，无权威源 |

**合同封版锚点（唯一，勿改）**：

```
封版 HEAD:  886f7104f47bc3fa7ed1de1c95b91e3aa1cda13e
受控 tree:  4c5f5373c83386d27ea996293a49ee7f3b9f10ce
ZIP SHA256: b21638abef8eb0e271c2190303c8f5dfaa1609a5c82269db2c20f451d97a5ad0
包 ID:      GK-KE-CONTRACT-V1.0.2（status=CONTRACT_CANDIDATE）
```

**祖先关系核验（TL 实测）**：`git merge-base --is-ancestor 886f710 HEAD` → 真。
即 L0-2 基线 `597d6fac` 是封版 `886f710` 的**后代**，封版制品未被回退改写。

## 3. (b) 地图 ID ↔ 版本 ↔ 对象 对应表

### 3.1 既有知识地图注册表（`specs/knowledge-architecture/maps/`）

现状**已存在**的知识地图实例（非 gk-ke/v1 候选）：

| 地图 ID | 名称 | 版本 | mapType | 状态 | 物理路径 | 路由策略 |
|---|---|---|---|---|---|---|
| `KM-GITS-ROOT` | GITS企业知识工程根知识地图 | `0.1.0` | `ROOT` | `VALIDATION` | `specs/knowledge-architecture/maps/ROOT_KNOWLEDGE_MAP.md` | `RP-CORP-RM-001` |
| `KM-CORP-RM-PREVISIT` | 访前准备任务地图 | `0.1.0` | `TASK` | `VALIDATION` | `specs/knowledge-architecture/maps/corporate-rm/previsit-preparation.md` | `RP-CORP-RM-001` |
| `KM-CORP-RM-*`（域地图） | 对公客户持续经营 | — | `DOMAIN` | `VALIDATION` | `specs/knowledge-architecture/maps/corporate-rm/DOMAIN_MAP.md` | `RP-CORP-RM-001` |
| `KM-CORP-RM-*`（事实核对） | 30M 事实核对 | — | `TASK` | `VALIDATION` | `specs/knowledge-architecture/maps/corporate-rm/fact-reconciliation.md` | `RP-CORP-RM-001` |

**关键事实（TL 实测，纠正 L0-1 旧表述）**：
- 根地图的 `mapId` 是 **`KM-GITS-ROOT`**，**不是** 字面 `"ROOT"`；判别根地图必须按 `mapType == "ROOT"`，不能按 ID 字符串匹配。
- 这一"教训"已在 P22 Loop 中记录（见共享记忆 P22 条目）：`InMemoryKnowledgeStore.rootMap()` 按 `mapType=ROOT` 匹配。
- 地图实例使用 **front-matter JSON 块**（`---` 包裹单行 JSON）而非纯 YAML，读取器需按此约定解析。

### 3.2 地图 ID 版本映射（OC-01 要求细化的部分）

maps 注册表的**版本字段语义**：

| 字段 | 语义 | 取值 | 与 gk-ke/v1 的对应 |
|---|---|---|---|
| `schemaVersion` | 地图元模型的 schema 版本 | `1.0.0` | 对应 `CTR-KMAP-001` 的 schema 版本 |
| `mapId` | 地图稳定标识 | `KM-<域>-<任务>` | 对应 gk-ke/v1 `KnowledgeMap.mapId` |
| `version` | **地图内容版本** | `0.1.0`（`^\d+\.\d+\.\d+$`） | 对应 gk-ke/v1 `KnowledgeMap.version` |
| `status` | 生命周期 | `VALIDATION` / `PUBLISHED` | 对应 gk-ke/v1 `AssetVersion.lifecycle` 语义 |
| `routePolicyRef` | 路由策略引用 | `RP-CORP-RM-001` | 对应 gk-ke/v1 `KnowledgeMap.routePolicyRef.id` |
| `activationContractRefs` | 激活契约引用 | `["AC-PREVISIT-001"]` | 对应 gk-ke/v1 `ActivationPlan` 的前置契约 |
| `assetRefs` | 资产引用（10 项） | `ASSET-DATA-*` / `ASSET-KNOW-*` | 对应 gk-ke/v1 `KnowledgeMap.nodes[].ref`（`nodeType: Asset`） |
| `skillRefs` | Skill 引用 | `SP-02/05/10/15` | 对应 `CTR-SKILL-002` `SkillDescriptor` |

### 3.3 命名空间对应（关键：两套 ID 体系并存）

| 体系 | 前缀约定 | 实例 | 状态 |
|---|---|---|---|
| 既有知识架构（P20/P22） | 无 SIM 前缀 | `KM-GITS-ROOT`、`ASSET-DATA-CUSTOMER-PROFILE`、`AC-PREVISIT-001` | `VALIDATION`（文件系统/Mock 验证） |
| gk-ke/v1 候选 | **`SIM-` 前缀** | `SIM-MAP-FINANCE`、`SIM-ASSET-P001`、`SIM-REL-P001-1.0.0`、`SIM-CORE` | `CONTRACT_CANDIDATE`（SIM-only） |

**OC-01 的关键结论**：两套 ID 体系**并存且必须显式映射**，不得假设同名同物。
依据：
- C08 §5「所有模拟数据带 SIM 前缀与 simulationOnly」→ gk-ke/v1 实例强制 `SIM-` 前缀。
- 既有 maps 无 `SIM-` 前缀，说明其不是模拟数据，而是"验证态（VALIDATION）架构资产"。
- L0-1 §5.1 明确候选合同未激活。

**映射规则（L0-2 交付，Feature Pilot 在 OpenAPI 中落为 `x-gk-ke-existing-mapping`）**：

```
既有 VALIDATION 资产  →  gk-ke/v1 SIM 实例       映射方式
KM-GITS-ROOT          →  (根，无 SIM 对应)        mapType=ROOT 判别，不映射为 SIM
KM-CORP-RM-PREVISIT   →  SIM-MAP-FINANCE          taskTypes 对齐（PRE_VISIT_PREPARATION ↔ FINANCE_VISIT_PREP）
ASSET-KNOW-PRODUCT-CARDS → SIM-ASSET-P001          assetClass=KNOWLEDGE_RULE, kind=PRODUCT_CARD
AC-PREVISIT-001       →  (gk-ke/v1 ActivationPlan) 契约引用对齐
RP-CORP-RM-001        →  SIM-ROUTE-001             路由策略引用对齐
```

> 注：上表右侧为 **L0-2 待确认映射**，需 KERT 侧（Leibniz-KERT HEAD `3b6640b`）核对后由 `knowledge_architecture_owner` 批准。
> Feature Pilot 在 WI-01 交付 OpenAPI 时，须将此表以 `x-gk-ke-existing-mapping` 扩展落盘，并将未确认项标 `pending_owner_confirmation`。

## 4. (c) schema ↔ 端点 ↔ 消费者 三方对应

| gk-ke/v1 schema | CTR 登记 | OpenAPI operation（C06 §1） | 消费者 |
|---|---|---|---|
| SemanticPackage | CTR-GKKE-001 | `GET /core/packages/{id}/versions/{version}` | public_semantic_core, gits, kert |
| AssetVersion | CTR-GKKE-002 | （经 `POST /catalog/discover` 摘要返回） | asset_registry, knowledge_map_registry |
| KnowledgeMap | CTR-GKKE-003 | `POST /maps/expand` | knowledge_map_registry, activation_planner |
| Assertion | CTR-GKKE-004 | `POST /ingestion/jobs`（candidate） | build_review_release, extraction |
| ReviewDecision | CTR-GKKE-005 | `POST /reviews` | build_review_release, human_gate |
| ReleaseManifest | CTR-GKKE-006 | `POST /releases` | build_review_release, projection |
| MetricDefinition | CTR-GKKE-007 | （`POST /semantic/query` 引用） | semantic_service, metric_governance |
| SemanticRequest | CTR-GKKE-008 | `POST /semantic/query` (request) | semantic_service |
| SemanticResult | CTR-GKKE-009 | `POST /semantic/query` (response) | semantic_service, context_evidence |
| GraphRequest | CTR-GKKE-010 | `POST /graph/query` (request) | rag_graph_adapter |
| GraphResponse | CTR-GKKE-011 | `POST /graph/query` (response) | rag_graph_adapter |
| ActivationPlan | CTR-GKKE-012 | `POST /plans` | activation_planner, agent_orchestrator |
| EvidenceBundle | CTR-GKKE-013 | `POST /knowledge/execute` → `GET /knowledge/jobs/{id}` | context_evidence, agent_orchestrator |
| ControlledAction | CTR-GKKE-014 | `POST /tasks/{id}/actions` | controlled_action, crm_writeback |
| MetricDefinition.full | CTR-GKKE-015 | （`POST /semantic/query` 指标口径源） | semantic_service, metric_governance |
| SourceVersion | CTR-GKKE-016 | `POST /ingestion/jobs`（前置 sourceVersionRef） | source_registry, semantic_runtime |
| Capability | CTR-GKKE-017 | （`POST /plans` 的 capabilityRefs） | capability_registry, activation_planner |
| QueryDefinition | CTR-GKKE-018 | （`POST /semantic/query` 的 queryId 源） | query_registry, semantic_service |
| Release | CTR-GKKE-019 | `POST /releases`、`POST /releases/{id}/revoke` | release_registry, build_review_release |
| LegacyRagHit | CTR-GKKE-020 | （既有检索适配，无独立端点） | existing_rag_adapter, context_evidence |

**覆盖核验**：
- 20 schema 全部有 CTR 登记 ✅
- 20 schema 全部归属至少 1 个 consumer ✅
- 14 schema 直接绑定 C06 端点；6 schema 为端点内引用（MetricDefinition/QueryDefinition/Capability/SourceVersion/AssetVersion/LegacyRagHit）——**这是 OC-01 的"对象对应"证据**，非缺陷。

## 5. OC-01 关闭判定

| 要件 | 证据 | 状态 |
|---|---|---|
| 三仓真实版本锚点 | §2（含祖先关系实测） | ✅ TL 侧齐备 |
| 封版三值锚点 | §2 | ✅ |
| 地图 ID ↔ 版本 ↔ 对象映射 | §3 | ✅ TL 侧齐备（含 `SIM-` vs 无前缀双体系结论） |
| schema ↔ 端点 ↔ 消费者三方对应 | §4 | ✅ TL 侧齐备（20/20 有 CTR + consumer） |
| 未确认映射项显式标记 | §3.3 映射表 | ✅ 标 `pending_owner_confirmation` |
| 独立 QA 核查 | — | ⏳ 待 L0-2 独立 QA |
| 相应 Owner 认可 | — | ⏳ 待 `gk_ke_contract_owner` + `semantic_architecture_owner` |

**TL 结论**：OC-01 的 **TL 侧证据已齐备**，缺口只剩"独立 QA 核查 + Owner 认可"两步——这两步属 L0-2 退出流程，**不得由 TL 代签**。

## 6. 遗留项（移交 L0-2 独立 QA 与 Owner）

1. §3.3 的 5 条映射需 KERT 侧核对（KERT HEAD `3b6640b`），确认后由 `knowledge_architecture_owner` 批准。
2. `KM-GITS-ROOT` 的 `mapType=ROOT` 判别约定需写入 OpenAPI 描述，防止消费者按 ID 字符串匹配（P22 FAILURES 教训复发）。
3. 既有 maps 的 `status=VALIDATION` 与 gk-ke/v1 的 `CONTRACT_CANDIDATE` 关系需 Owner 明确：是否允许 VALIDATION 资产在激活后直接投影为 SIM 实例。
