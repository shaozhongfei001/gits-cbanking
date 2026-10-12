# GK-KE L0-2 CR-01~08 审计与处置（V1.0）

> 角色：Tech Lead（planning_review）｜Loop：`GK1-l0-2-contract-activation`｜日期：2026-09-12
> 依据：C08 §1 变更清单 + C08 §5 启动指令 + C06 §1 接口表
> 基线：GK-KE-CONTRACT-V1.0.2（HEAD `886f710` / tree `4c5f5373` / ZIP `b21638ab`）
> 性质：**审计记录，不改变 V1.0.2 封版制品**。本文件只判定"L0-2 范围内做什么 / 不做什么"。

## 0. 审计口径

C08 §1 的 CR-01~08 是**迁移变更清单**（跨 L0→L6 全程），不是 L0-2 的交付清单。
L0-2 的交付边界由 C08 §2 "L0-2 契约激活"一行定义：

> 审 CR-01–08；补完整 OpenAPI；定义兼容与生成策略 ｜ 产物：新候选契约、正负例、消费者驱动测试 ｜ 退出：独立 QA 查冲突；相应 Owner 批准后激活

因此本审计对每个 CR 只回答三件事：
1. **在 L0-2 是否触发合同面变更**（即是否需要写进 `specs/gk-ke/v1` / OpenAPI）；
2. **L0-2 的具体交付物**；
3. **剩余部分归属哪个后续 Loop**（防止 L0-2 越界实现服务）。

## 1. CR 逐项处置

| CR | C08 原文要点 | L0-2 触发面 | L0-2 交付物 | 剩余归属 |
|---|---|---|---|---|
| **CR-01** 公共核心独立 | 从旧双核心抽离跨域共享定义；逐类型核对 imports、公共 ID、双版本迁移；不复制后改义 | **是**（合同面） | SemanticPackage 的 `types[].writeOwner/writeEntry/authorityScope` 映射进 OpenAPI `GET /core/packages/{id}/versions/{version}` 响应；`imports[]` 版本引用规则；公共 ID 命名规范 | L1-1 做 12 类型域扩展；L2-2 做 registry 落地 |
| **CR-02** 权威矩阵细化 | 客户/产品主档与知识、任务分别归属；查重复写入口 → 改引用/投影 | **是**（合同面） | `POST /catalog/discover` 的授权入口摘要 + `catalogRevision`；AssetVersion `assetClass` **四类闭集不得替换**；KnowledgeMap `scope/purpose` 字段 | L2-2 做 CAS/断链工具；L4-1 做地图激活 |
| **CR-03** 注册与地图增量 | 保留 P20 四类资产与确定性路由；新增字段不能静默打破闭集 Schema | **是**（合同面） | Assertion / ReviewDecision / ReleaseManifest / Release 四对象映射进 `POST /reviews`、`POST /releases`、`POST /releases/{id}/revoke`；**闭集只允许显式版本化新增** | L3-1 工厂、L3-2 审核发布（服务实现） |
| **CR-04** 自动构建与发布 | 候选抽取接入 PI-0 证据/用途门禁；原 ACTIVE 不原地编辑 | **部分** | 否决：L0-2 只保证 Release 的"不可原地编辑"在**合同层可判**（releaseId 不可变 + 发布即冻结语义）；EvidenceSpan/FieldAssertion/ProductKnowledgeRelease 属 PI-0 既有合同，**不并入 gk-ke/v1**（见 §2 决策 D-2） | L3-2 门禁实现 |
| **CR-05** 语义查询 | 原注册 queryId 增补 metric/粒度/时态；旧查询继续拒绝任意 SPARQL；指标合同另行版本化 | **是**（合同面） | `POST /semantic/query` 的 SemanticRequest/SemanticResult；MetricDefinition.full 42 字段映射；**"拒绝任意 SPARQL"落为合同负例**（422） | L2-1 白名单编译器 + 复算 |
| **CR-06** 图组件 | 用户指定 KERT 内 Kuzu 模拟；新 GraphQueryPort、独立目录、锁版、可替换投影；不改权威源 | **是**（合同面，最小） | `POST /graph/query` 的 GraphRequest/GraphResponse；**合同声明 Kuzu 仅为可重建模拟投影，不承载注册中心权威事务** | L5-1 Kuzu 适配、L5-2 LightRAG |
| **CR-07** 既有 RAG 与 LightRAG | 复用已有检索；增加可关试验；source/chunk/version/ACL 对齐；不能默默更换 embedding | **是**（合同面，最小） | LegacyRagHit 的 source/chunk/version/ACL 四元组入合同；**LightRAG 在 L0-2 只登记为可关适配器，不选型** | L5-2 Spike 与 A/B/C 对照 |
| **CR-08** 模拟与动作 | 完整造数与模拟白名单动作；simulationOnly 贯穿；不创建生产写回许可 | **是**（合同面） | `simulationOnly` 贯穿全部 gk-ke/v1 schema 的非可选约束；`POST /sim/actions` + `GET /sim/actions/{id}` 的**白名单只含 CREATE_FOLLOWUP_TASK / RECORD_CONTACT_OUTCOME**；`POST /tasks/{id}/actions` 的 202 行动意图语义 | L1-2 模拟源、L4-2 闭环、L6 隔离规则 |

## 2. TL 决策记录（L0-2 边界）

**D-1｜L0-2 只产出候选 + 正负例 + 消费者测试，不产出服务实现。**
C08 §2 的产物列明此项；L0-2 退出标准是"独立 QA 查冲突 + Owner 批准后激活"，不含任何可运行服务。L0-2 若写服务实现即为越界。

**D-2｜gk-ke/v1 不吞并 PI-0 既有合同（C03/CR-04 的关键取舍）。**
PI-0 的 `CTR-PK-*`（EvidenceSpan / FieldAssertion / ConflictCase / ProductKnowledgeRelease / interpretation-api）已在 `specs/CONTRACT_INDEX.yaml` 登记为 CANDIDATE，且被 L02/L03 Loop 使用。
gk-ke/v1 的 Assertion / ReviewDecision / ReleaseManifest / Release 是**新候选剖面**，与 PI-0 对象是"映射关系"而非"替代关系"。
**处理**：L0-2 在 OpenAPI 中以 `x-gk-ke-pi0-mapping` 扩展登记映射表，**不改 PI-0 合同、不复用其 $id、不声明替代**。理由：C08 §1 CR-04 要求"原 ACTIVE 不原地编辑"，且 C08 §5 明令"禁止直接覆盖 P20/DKES/PI-0"。

**D-3｜接口命名空间隔离。**
所有 L0-2 路径落在 `/gk-ke/v1/**`，与既有 `/api/v1/**`（`gits-kno-api.openapi.json`）和 `product-recommendation.openapi.json` **物理分文件**（`specs/openapi/gk-ke-v1.openapi.json`）。
理由：C06 §3 明确"以下路径位于新候选接口命名空间 `/gk-ke/v1`，不是现有 GITS/DKES/PI-0 接口地址"。

**D-4｜14 个端点行全部落 OpenAPI，不得只落 schema。**
C06 §1 表给出 14 行（GET /core/packages/... 起，GET /sim/actions/{id} 止）。C06 §26 明确"开发 Loop 需生成并评审完整 OpenAPI"。
**验收口径**：OpenAPI 必须包含这 14 个 operation，且每个 operation **至少 2 个负例**。

**D-5｜`simulationOnly` 是 L0-2 的硬约束，不是建议。**
C08 §1 CR-08"simulationOnly 贯穿"呼应 C08 §5"所有模拟数据带 SIM 前缀与 simulationOnly，不接生产写回"。
**验收口径**：20/20 schema 保留 `simulationOnly: {const: true}` 且必填；OpenAPI 每个 operation 的请求/响应 schema 均不得放宽该约束。

**D-6｜兼容策略基调 = `explicit_migration`（非 backward_compatible）。**
依据：`specs/CONTRACT_INDEX.yaml` 现有 CTR-GKKE-001~020 全部登记 `compatibility: explicit_migration`。
CONTRACT_INDEX 现有约定是"合同类型不限于 OpenAPI"，且 workspace 规则要求"合同变化必须先改合同源 → make generate → make check → 最后才写实现"。
**因此**：gk-ke/v1 新增端点属**显式迁移**，不是向后兼容增量；激活需要相应 Owner 批准迁移映射。

## 3. 24 条"名不符实"风险清单（L0-2 必须在正负例中覆盖）

来自 C08 §5 红线与 CR 条款，L0-2 无需实现，但**正负例必须能拒绝**：

| # | 风险 | 对应负例要求 |
|---|---|---|
| 1 | 把 `subjectCategory` 当资产枚举替代 `assetClass` 四类 | assetClass 非法值负例 |
| 2 | 同名不并户（客户/产品同名误并） | identityRule 缺失或冲突负例 |
| 3 | 复制后改义（公共核心类型被域内改名） | imports 版本引用不一致负例 |
| 4 | 任意 SPARQL 被旧 queryId 接受 | SemanticRequest 携带原始 SPARQL 负例 |
| 5 | 指标口径被外推成杭银规定 | MetricDefinition 缺 approvalRef 负例 |
| 6 | 空 EvidenceBundle 当成功知识交付 | unknowns/conflicts/evidenceRefs 全空负例 |
| 7 | LLM 覆盖规则判定 | ruleResults 缺 ruleRef/premiseRefs 负例 |
| 8 | planHash 含随机 planId/traceId/时间 | planHash 字段缺失或含非确定字段负例 |
| 9 | 把"名义未用额度"写成可提款金额 | ControlledAction parametersHash 不符负例 |
| 10 | 审核人自审 | ReviewDecision targetHash 一致但审核人=提交人负例 |
| 11 | 审批后改字 | ReleaseManifest hash 与 targetHash 不一致负例 |
| 12 | 半发布 | Release 缺 staging 终态负例 |
| 13 | 撤销后仍可查询为有效 | revoke 后 expectedVersion 冲突负例 |
| 14 | 图服务不可用却返回 200 空结果 | /graph/query 503 语义负例 |
| 15 | 静默更换 embedding | LegacyRagHit 缺 chunk/version 负例 |
| 16 | 生产写回许可被创建 | /sim/actions 白名单外动作（转账/放款/授信审批）负例 |
| 17 | 幂等键相同但 payload 不同 | Idempotency-Key 冲突负例 |
| 18 | 版本倒退事件覆盖当前状态 | aggregateVersion 倒退负例 |
| 19 | 外部 API 泄露服务器路径/凭据/SQL | 响应含路径/凭据字段负例 |
| 20 | 金额用浮点 | 金额非十进制字符串负例 |
| 21 | 时间非 RFC3339 | occurredAt/assembledAt 格式负例 |
| 22 | scope 被当作授权证据 | 请求含 scope 但无 Authorization 语义负例 |
| 23 | 删除原文伪造可重放 | tombstone 缺失负例 |
| 24 | 把本包最小 Schema 宣称为现有 API 完整替代 | OpenAPI `info.description` 必须保留"非替代"声明 |

## 4. 与 C06 §1 的端点覆盖对照（L0-2 WI-01 验收基线）

| # | 方法与路径 | 提供方 | L0-2 主 schema | 负例类别（≥2） |
|---|---|---|---|---|
| 1 | GET /core/packages/{id}/versions/{version} | 公共核心 | SemanticPackage | 404 未解析 / 403 越权 |
| 2 | POST /catalog/discover | KERT | (请求内联) + catalogRevision | 422 PURPOSE_NOT_ALLOWED / 403 |
| 3 | POST /maps/expand | KERT | KnowledgeMap | 409 DEPENDENCY_UNRESOLVED / 403 |
| 4 | POST /plans | KERT Planner | ActivationPlan | 409 ROUTE_AMBIGUOUS / 422 必需项缺失 |
| 5 | POST /knowledge/execute | KERT Runtime | EvidenceBundle | 403 越权 / 503 依赖失效 |
| 6 | GET /knowledge/jobs/{id} | KERT Runtime | EvidenceBundle | 404 / 409 版本 |
| 7 | POST /semantic/query | 数据平台 | SemanticRequest→SemanticResult | 422 粒度/缺失/币种 / 403 范围 |
| 8 | POST /graph/query | 图适配器 | GraphRequest→GraphResponse | 409 图版本 / 503 图不可用 |
| 9 | POST /ingestion/jobs | KERT 工厂 | (jobId/candidateSetRef) | 422 来源/用途不合格 / 403 |
| 10 | POST /reviews | KERT 审核 | ReviewDecision | 403 自审 / 409 hash 变化 |
| 11 | POST /releases | KERT 发布 | ReleaseManifest→Release | 409 并发 / 422 KNOWLEDGE_GATE_FAILED |
| 12 | POST /releases/{id}/revoke | KERT 发布 | Release(revoked) | 403 / 409 |
| 13 | POST /tasks/{id}/actions | GITS | ControlledAction | 409 失效 / 403 未确认 |
| 14 | POST /sim/actions | 银行模拟平台 | (白名单动作) | 409 重复键不同内容 / 状态冲突 |
| 15 | GET /sim/actions/{id} | 银行模拟平台 | (源执行状态) | 404 未见该意图 / 403 |

> 注：C06 §1 表 13 行为 14 个路径（第 5 行含配套 GET /knowledge/jobs/{id}）。
> L0-2 WI-01 以 **15 个 operation** 为完整覆盖口径（含 /knowledge/jobs/{id}）。

## 5. L0-2 不做什么（越界警戒）

- ❌ 不实现任何 KERT/GITS 服务（模块与适配器属 L1-1~L6）。
- ❌ 不安装 Kuzu、不引入 LightRAG（L5）。
- ❌ 不修改 `docs/dd/gk-ke-contract/`（V1.0.2 封版制品，变更走新封版）。
- ❌ 不把 CONTRACT_CANDIDATE 改 APPROVED（激活是 Owner 动作）。
- ❌ 不把 36 项 PLANNED_NOT_EXECUTED 改 PASS。
- ❌ 不改 `generated/`。
- ❌ 不覆盖 P20 / DKES / PI-0 合同（见决策 D-2）。
