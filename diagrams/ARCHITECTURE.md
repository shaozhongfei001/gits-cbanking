# GITS-KNE 系统架构说明

> 配套图：`architecture.html`（自包含 HTML/SVG）；~~`architecture.png`（预览）~~ 已随 P24 架构变更删除，待 CI 重新生成（见 `docs/architecture/ARCH-REVIEW-2026-08-23-001.md` §7 决议 3）
> 主题：客户经理持续经营智能体 — 系统架构
> 基线：V1.1 (P22 后)，2026-08-19

---

## 一、总体定位

GITS-KNE（杭州银行知识工程体系与智能体基础能力建设项目）面向"对公客户经理持续经营"业务闭环，构建**可编译语义合同 + 运行本体控制平面 + 多种可重建投影**的智能体基座。系统采用**模块化单体（Spring Modulith）+ 独立后台 Worker**的部署形态，前端基于 Vue3 + Naive UI 组合，业务核心通过 **Port/Adapter 六边形分层**解耦。

整体遵循三条顶层原则：

1. **合同 SSOT（Single Source of Truth）**：所有 API、事件、语义、规则、动作均由 `specs/CONTRACT_INDEX.yaml` 登记的合同权威源派生，代码生成与实现不得越界。
2. **领域优先、框架后置**：`modules/` 是纯业务逻辑的承载体，无 Spring 框架依赖（除少量可移植注解），通过 Port 接口向外暴露能力。
3. **受控副作用**：所有对外副作用（CRM 写回、客户消息发送、Opportunity 提升）必须经过 `ControlledActionService` 与 Human Gate，无门禁不执行。

---

## 二、分层结构（自上而下）

### 2.1 前端层（`frontend/`）

| 视图 | 路由 | 主要职责 |
|------|------|----------|
| Dashboard | `/` | 客户经营概览，今日重点客户 + 优先级 |
| CustomerOperatingView | `/customers/:id` | 单客户经营视图（COV），按"最近发生了什么 / 事实 / 信号 / 未闭环承诺 / 下一步"组织 |
| **EngagementWorkspace** | `/engagement` | **持续经营工作台（coral 焦点节点）**，覆盖会中助手、事实对账、离场确认、CRM 写回审批等核心交互 |
| CommitmentDashboard | `/commitments` | 承诺/任务管理面板 |
| JourneyTimeline | `/journeys/:id` | 客户旅程时间线 |
| InMeetingAssistant | `/in-meeting/:id?` | 会中助手（实时追问、来源区分） |
| AuditTrace | `/audit-trace` | 审计追踪 |
| ExternalEventMonitor | `/external-events` | 外部事件监控 |
| ReportDetail | `/reports/:id` | 报告详情 |

技术栈：Vue 3.5 + Vue Router 4 (History) + Pinia + vue-query + axios + Naive UI 主、TDesign 辅 + Tailwind CSS + ECharts + Vite 8 + Vitest + Playwright。

合规要点：
- 类型从 `frontend/src/api/*.ts`（由 OpenAPI 生成）派生，**禁止发明后端未定义字段**。
- 4 态处理（Idle/Loading/Success/Error），Loading 禁止空白页。
- 401 触发 `auth:unauthorized` 事件，自动跳转登录。

### 2.2 应用层（`apps/`）

| 应用 | 主类 | 端口 | 职责 |
|------|------|------|------|
| **GitsKnoApiApplication**（coral 焦点） | `apps/api` | `:8080`（Vite dev 代理到 `:8082`）| 主 API 服务；接受前端 REST 请求、调度领域模块、承载 OpenAPI |
| GitsKnoWorkerApplication | `apps/worker` | `:8090` | 独立后台 Worker；处理领域事件异步分发、外部事件摄取、长时任务 |

应用层**只做装配**：选择哪些 Port 由哪些 Adapter 实现、装配 Spring Bean、加载 Flyway 迁移、配置 CORS/认证/Observability。**不写任何业务规则**。

### 2.3 领域模块层（`modules/`）

所有模块**对外只暴露 Port 接口**，Port 是 `XxxPort` 命名的纯接口（无 Spring 注解），业务编排放在模块内的纯 Java Service/Orchestrator 中。

| 模块 | 包 | 核心 Port | 职责 |
|------|-----|-----------|------|
| **operational-ontology** | `com.gien.gits.ontology` | `*Repository`（48 个） | **运行本体**：核心领域模型（Customer、Claim、Commitment、Interaction、Opportunity、HumanGate、OperatingCase、FactReconciliationCase 等）的 Port 接口与领域 Service |
| semantic-runtime | `com.gien.gits.semantic` | `SemanticQueryPort`、`RegisteredSemanticQueryCatalog`、`FailClosedSemanticQueryGuard` | 受控语义查询；只暴露白名单查询 |
| context-evidence | `com.gien.gits.context` | `ContextAssemblyPort`、`PlanDrivenContextAssembler` | 证据上下文装配，产出 `EvidenceBundle` |
| **human-action** | `com.gien.gits.action` | `ControlledActionService`、`ActionDispatchPort`、`CrmWritebackChannel`、`AuditLogPort` | **受控动作 + 人工门禁**；所有副作用必经此模块 |
| evaluation | `com.gien.gits.evaluation` | `EvaluationPort`、`DefaultEvaluator` | 反馈评测，运行 `RunManifest` |
| **scenario-customer-journey** | `com.gien.gits.customerjourney` | `CustomerJourneyRepository`、`CustomerJourneyOrchestrator` | **客户旅程领域**；编排 M17→M22 业务链，驱动 OperatingCase 状态机 |
| knowledge-architecture | `com.gien.gits.knowledge` | `KnowledgeMapPort`、`KnowledgeElementPort` | 知识架构（KnowledgeElement / KnowledgeMap / AssetManifest / ActivationPlan） |

> **核心编排器**：`CustomerJourneyOrchestrator.executeFullChain()` 编排 `M17 信号触发 → M18 AI 洞察 → M20 产品匹配 → M21 访前面谈 → M22 访后回访` 完整链路，5 次 Interaction 记录，OperatingCase 状态 `OPEN → IN_PROGRESS → WAITING_FOR_HUMAN → IN_PROGRESS → CLOSED`。
>
> **状态机约束**：`OperatingCaseStateMachine` 强制合法转移，非法转移抛 `IllegalStateException`（如 CLOSED 不能再转移）。

### 2.4 适配器层（`adapters/`）

Port 接口在适配器层有具体实现，与外部系统对接。**模块不直接依赖适配器实现**，通过 Spring 配置在 `apps/` 中注入。

| 适配器 | 路径 | 实现内容 |
|--------|------|----------|
| **persistence-relational** | `adapters/persistence-relational` | MyBatis/JDBC 关系库实现。`foundation/engagement`（Customer/CreditFacility/ExternalEvent/BankRelationshipSnapshot/Transaction）、`foundation/journey`（OperatingCase/CustomerJourney/Interaction/InsightClaim）、`foundation/ontology`（Claim/Commitment/Task/HumanGate）、`v11`（V1.1 增量：KycGap/RecordingConsent/ProductKnowledgeVersion） |
| semantic-jena | `adapters/semantic-jena` | Apache Jena 6.2.0 语义仓库适配器（`JenaSemanticRepositoryAdapter`）|
| ~~knowledge-filesystem~~ | ~~`adapters/knowledge-filesystem`~~ | ~~已移除（P24 由 DKWS 替代）~~ |
| oracle-source | `adapters/oracle-source` | Oracle 源只读适配器（`JdbcOracleSourceAdapter`、`OracleSourceAutoConfiguration`），**默认 quarantine**——需 ADR + 数据所有者授权 + 专用 Loop 才可启用 |

### 2.5 数据 / 外部层

| 节点 | 性质 |
|------|------|
| H2 / MySQL | 关系库。本地 dev 默认 H2 内存（MySQL 兼容模式），生产 MySQL；Flyway 迁移位于 `classpath:db/migration/h2` |
| Jena 语义库 | OWL/Turtle 本体 + 推理材料 |
| Oracle 源库 | 隔离资产，仅用于只读管道（quarantine）|
| 外部事件 | 工商/司法/招投标/行业资讯等第三方事件源（CTR-DATA-004 合同约束）|

---

## 三、跨层通信与依赖方向

```
Vue3 SPA ──REST/JSON──> apps/api ──> modules/* (Port) <── adapters/* (实现)
                              │                                │
                              └──> 领域事件 ──> apps/worker ──> 异步处理 / 外部回写
                              │
                              └──> 关系库 / 语义库 / 文件系统 / 外部源
```

**依赖规则**（`workspace` 总宪法）：

- 领域模块**只能依赖其他模块的 Port 接口**，不能依赖实现类。
- 适配器可以依赖 Port 接口和领域模型（Entity/Record），不能反向依赖 apps。
- apps 负责装配（选哪个 Adapter 实现哪个 Port）和应用配置。
- frontend 通过 OpenAPI 生成的前端 SDK 访问后端，**类型层面与合同严格对齐**。

---

## 四、关键技术决策（精选 ADR）

| ADR | 主题 | 决策摘要 |
|-----|------|----------|
| ADR-0001 | 语义-运营双核 | 语义（OWL）作为可声明资产，运营（MySQL）作为运行时事实；两者通过受控 ETL 桥接 |
| ADR-0002 | 六边形模块边界 | Port 接口在 `modules/*/port/`，实现在 `adapters/*`；`apps` 仅做装配 |
| ADR-0003 | 生产数据库 | MySQL 8，H2 仅本地开发 |
| ADR-0004 | 事件驱动集成 | 内部用 Spring `ApplicationEventPublisher`（同步语义），跨服务用 CloudEvents（CTR-EVENT-001 合同）|
| ADR-0005 | LLM 集成与降级 | `LlmClient` Port + `MockLlmClient`/`RealLlmClient`；失败 fallback 到模板/正则逻辑 |
| ADR-0007 | Oracle 只读启用 | 必须 ADR + 数据所有者授权 + 专用 Loop；默认 quarantine |
| ADR-0011 | 六边形架构 | 模块-适配器-应用三层 |
| ADR-0012 | DMN 引擎 | KIE DMN 加载 `claim-reconciliation.dmn`（CTR-RULE-001），Fallback 手写逻辑 |
| ADR-0013 | 可观测性栈 | Micrometer + Prometheus + Zipkin；Logstash JSON 日志 |
| ADR-0014 | scenario 目录聚合 | 把场景域从 `modules/` 提到 `scenario/`，强调领域聚合 |

---

## 五、可观测性与安全

### 5.1 可观测性

- **日志**：Logstash JSON encoder（结构化），禁止 `System.out`/`e.printStackTrace`。
- **指标**：Micrometer + Prometheus registry；Actuator 端点 `/actuator/{health,info,metrics,prometheus}`。
- **链路追踪**：Zipkin（dev 100% 采样）。
- **审计**：`AuditLogPort` 记录 `actorId / confirmedAt / action / payload-hash`，由 `human-action` 模块统一提供。

### 5.2 安全

- **API Key 认证**：`X-API-KEY` 请求头，dev 模式自动放行（`import.meta.env.DEV`）。
- **CORS**：仅允许 `localhost:5173`（前端 dev）与 `localhost:8080`（生产）。
- **依赖检查**：OWASP Dependency-Check；CVSS ≥ 7 阻断构建。
- **敏感数据**：禁止日志输出 API Key、客户敏感信息（身份证、卡号等）。
- **隔离资产**：Oracle / Ossie 等未授权资产放 `tools/quarantine/`，需 ADR + 数据所有者授权 + 专用 Loop 才可启用。

---

## 六、合同注册表（精选）

来自 `specs/CONTRACT_INDEX.yaml`：

| 合同 ID | 类型 | 名称 |
|---------|------|------|
| CTR-API-001 | OpenAPI | 主 API 合同 |
| CTR-EVENT-001 | AsyncAPI | 领域事件 |
| CTR-SEM-001/002 | LinkML + OWL | operational_ontology |
| CTR-RULE-001 | DMN | claim-reconciliation 决策表 |
| CTR-DATA-001~004 | 数据 | 客户/Claim/外部事件/Oracle 源 |
| CTR-V11-001/002/003/004 | OpenAPI | HumanGate / CrmWriteback / AuditTrace / EvidenceVersion |
| CTR-KELEM-001 | JSON Schema | KnowledgeElement（K-Type-F/R/P/E/M）|

合同变化必须先改合同源 → `make generate` → `make check` → 写实现。

---

## 七、目录总览

```
modules/          领域模块（纯业务，Port 接口对外）
adapters/         适配器（实现 Port，对接外部）
apps/             启动应用（api 主 + worker 后台）
scenario/         场景领域聚合
frontend/         Vue3 前端
specs/            合同权威源
generated/        自动生成制品（只读，禁止手改）
loops/            Loop 批次管理
docs/             文档
tools/quarantine/ 隔离资产（需 ADR 启用）
```

---

## 八、参考

- 详细设计：`docs/dd/engagement-main-chain-flow-design.md`、`docs/dd/ontology-core-concepts-design.md`
- V1.1 验收：`docs/V1.1_ACCEPTANCE_REPORT.md`、`docs/V1.1_IMPLEMENTATION_PLAN.md`
- 部署：`docs/architecture/deployment-architecture.md`、`docs/deployment/DEPLOYMENT-GUIDE.md`
- ADR 总索引：`docs/architecture/ADR_INDEX.md`
- 模块清单：`docs/governance/MODULE_CATALOG.md`
