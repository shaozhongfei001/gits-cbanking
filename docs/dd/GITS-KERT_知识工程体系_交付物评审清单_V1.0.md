# GITS-KERT 知识工程体系 · 交付物架构师评审清单 V1.0

> 用途：供架构师评审《GITS-KERT_知识工程体系_项目总契约_V1.0.md》约定的**全部交付内容**。
> 契约 SSOT：`/home/szf/dev/gits-kert-docs/dd/GITS-KERT_知识工程体系_项目总契约_V1.0.md`
> 交付包：`/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/`（MANIFEST 100 个文件，10 层）
> 编制：Feature Pilot（gkd-cve-pilot）｜日期：2026-09-11｜评审对象版本：契约 V1.0（2026-09-10）
> 包自检：`tools/validate_package.py` 离线 **125 项通过 / 0 失败**（`acceptance/package_self_check.json`）。
> 自检性质：作者离线自检，**非独立 QA**；服务 E2E、Kuzu/LightRAG 集成、真实人工审批均 `NOT_PERFORMED`。

---

## 0. 评审须知（边界与红线）

- 本包是**合同/设计包**，不是可上线服务；不含可运行服务、真实数据库迁移、真实人工审批、生产密钥。
- 权威顺序：已批准需求/基线 > ADR+合同注册表 > Loop/Dispatch > 实现代码。
- 合同先行：`specs/` 为 SSOT，`generated/` 只读；实现不得发明合同外字段。
- AI 边界：AI 只产出候选 Claim/Proposal；ControlledAction 必须经人工确认→权限复核→幂等→回执。
- 本清单逐项列出契约约定交付物、包内路径、验收标准与评审要点；末附评审签署区。

---

## 1. 交付物总览（契约 §0.3 十层 + MANIFEST 实测）

| 层 | 交付物 | 包内位置 | 数量 | 契约验收锚点 |
|---|---|---|---|---|
| L0 | 合同包索引与验收 | `README.md`、`MANIFEST.json`、`acceptance/` | 3 | §0.3 L0、§11 |
| L1 | 受控合同（OpenAPI/JSON Schema/AsyncAPI/事件目录） | `specs/openapi/`、`specs/schemas/`、`specs/asyncapi/`、`specs/events/` | 10 | §2、§11.1 |
| L2 | 本体与知识架构（OWL/SHACL/LinkML/R2RML/DMN） | `ontology/`、`knowledge-architecture/`、`mappings/`、`decisions/` | 28 | §3、§11.2 |
| L3 | 受控数据模型（ER/DDL/迁移/状态机/事件） | `data-model/` | 10 | §4、§11.3 |
| L4 | 应用合同（服务/端口/适配器/API 序列/降级） | `application/` | 10 | §5、§11.4 |
| L5 | 前端合同（路由/页面/状态/UX/四态） | `frontend/` | 10 | §6、§11.5 |
| L6 | 集成与部署（EIP/拓扑/compose/环境/密钥） | `integration/`、`deployment/` | 10 | §7、§11.6 |
| L7 | 测试与验收（测试矩阵/合同测试/验收用例/报告模板） | `tests/`、`acceptance/` | 10 | §8、§11.7 |
| L8 | 治理与运维（RACI/证据/审计/回滚/监控/Runbook） | `governance/`、`operations/` | 8 | §9、§11.8 |
| L9 | 种子与样例（种子数据/样例请求/响应/事件） | `seeds/`、`samples/` | 8 | §10、§11.9 |
| 工具 | 离线包校验器 | `tools/validate_package.py` | 1 | §0.3、§11 |
| 根 | 总契约本体 | 仓库外 `GITS-KERT_..._总契约_V1.0.md` | 1 | 全文 |

MANIFEST 合计 100 文件；类型分布：md 71、yaml 12、json 8、py 1、ttl 3、shacl 1、linkml 1、sql 2、dmn 1。

---

## 2. L0 — 合同包索引与验收（契约 §0.3、§11）

| 交付物 | 路径 | 验收标准 | 评审要点 |
|---|---|---|---|
| 包说明 | `README.md` | 说明 SSOT、10 层、自检边界 | 是否明确"非独立 QA/非上线" |
| 清单 | `MANIFEST.json` | 100 文件、含 sha256、层级 | 哈希是否可复核、是否有未列文件 |
| 离线校验器 | `tools/validate_package.py` | 结构/引用/必填/哈希校验 | 125 检查项是否覆盖关键红线 |
| 包自检结果 | `acceptance/package_self_check.json` | passed=125 failed=0 | 独立 QA/E2E/集成/人工审批是否如实标 NOT_PERFORMED |
| 验收报告模板 | `acceptance/ACCEPTANCE_REPORT_TEMPLATE.md` | 含签署/证据/偏差栏 | 是否禁止 dev 自签 QA_PASS |

---

## 3. L1 — 受控合同（契约 §2、§11.1）

| 交付物 | 路径 | 关键内容 | 评审要点 |
|---|---|---|---|
| OpenAPI | `specs/openapi/gits-kno-api.openapi.json` | 17 个服务端点（§2.2）、统一错误结构、分页 `totalElements/totalPages/number/size`、空数组非 null | 与现有 `specs/openapi` 合同是否一致/兼容；operationId 与 Controller 对齐 |
| JSON Schema | `specs/schemas/*.schema.json`（6） | customer/claim/proposal/action/event/knowledge | 字段是否与本体/数据模型闭环；无发明字段 |
| AsyncAPI | `specs/asyncapi/gits-kno-events.asyncapi.json` | 12 类领域事件（§2.4） | CloudEvent 信封、topic、版本化 |
| 事件目录 | `specs/events/event-catalog.yaml` | 事件名/载荷/发布方/消费方 | 与 L3 状态迁移、L4 编排一致 |
| 合同注册表 | `specs/CONTRACT_INDEX.yaml` | 唯一合同注册入口 | 所有受控合同是否登记；与仓库 `specs/CONTRACT_INDEX.yaml` 衔接 |

**17 服务端点（§2.2，逐一核对）**：客户主数据、旅程、承诺、外部事件、机会、产品知识版本、信号、互动记录、技能执行、KYC 洞察、行动建议、ControlledAction 请求/回执、事件查询、知识检索、知识图谱、健康检查。

**12 类事件（§2.4）**：CustomerCreated/Merged、JourneyStarted/StageChanged、CommitmentCreated/Completed/Failed、ExternalEventReceived、SignalDetected、InteractionRecorded、ClaimCandidateRecorded、ControlledActionRequested/Approved/Rejected/Executed/Failed、KnowledgePublished/Deprecated。

---

## 4. L2 — 本体与知识架构（契约 §3、§11.2）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| 本体 OWL（3 ttl） | `ontology/owl/`（operational/semantic/bridge） | 操作本体↔语义本体双核心、桥接映射 |
| SHACL 形状 | `ontology/shacl/gits-shapes.shacl.ttl` | 实体/关系约束、闭环校验 |
| 术语表 | `ontology/glossary.yaml` | 中英文术语、与代码命名一致 |
| 知识架构合同 | `knowledge-architecture/`（KM/KI/KE/RUL/AC/RP/LinkML 等 18 文件） | 知识地图/元素/规则/激活契约/路由策略；LinkML 模型；目录结构 |
| R2RML 映射（2 sql 相关） | `mappings/r2rml/` | 关系数据→RDF 物化映射 |
| DMN 决策 | `decisions/claim-reconciliation.dmn` | Claim 三态调和（冲突/权威/证据） |
| 架构 ADR/说明 | `knowledge-architecture/*.md`、`ontology/*.md` | 双核心、Port/Adapter、降级策略 |

**核心概念（§3.2）**：Customer、Journey、Commitment、ExternalEvent、Opportunity、Signal、Interaction、Skill、Claim、Proposal、ControlledAction、KnowledgeElement/KnowledgeMap/Rule/ActivationContract/RoutePolicy。

---

## 5. L3 — 受控数据模型（契约 §4、§11.3）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| ER 模型 | `data-model/er-model.md` | 实体/关系/基数 |
| 逻辑数据模型 | `data-model/logical-data-model.yaml` | 字段/类型/约束，与 JSON Schema 一致 |
| DDL（H2 + MySQL） | `data-model/ddl/`（2 sql） | 双方言同步；无代码内 DDL |
| Flyway 迁移约定 | `data-model/migration-plan.md` | `V{版本}__{描述}.sql`、H2/MySQL 同步 |
| 状态机 | `data-model/state-machines.yaml` | 旅程/承诺/行动/审批状态迁移 |
| 事件载荷合同 | `data-model/event-payloads.yaml` | 与 L1 AsyncAPI/事件目录一致 |
| 数据字典 | `data-model/data-dictionary.md` | 字段语义、敏感分级 |

**红线复核**：所有 schema 变更走 Flyway；禁止代码 `CREATE/ALTER TABLE`；Entity↔DTO 分离。

---

## 6. L4 — 应用合同（契约 §5、§11.4）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| 服务目录 | `application/service-catalog.yaml` | 17 服务职责、边界 |
| Port 接口目录 | `application/ports/*.md` | 模块间仅经 Port 通信 |
| Adapter 合同 | `application/adapters/*.md` | LLM/CRM/Oracle/Kuzu/LightRAG 等防腐层 |
| API 序列 | `application/sequences/*.md` | 访前/信号/行动/审批主链时序 |
| 降级策略 | `application/degradation-policy.md` | LLM/DMN/外部系统失败兜底 |
| 编排合同 | `application/orchestration.md` | EngagementOrchestrator 关键操作发事件 |

**关键 Port（与现仓实现对照）**：LlmClient、ClaimReconciliationPort、CrmWritebackChannel、DomainEventPublisher、KnowledgeElementPort、KnowledgeWikiPort、SkillExecutionPort 等。
**分层红线**：模块禁止直接依赖实现类；新增 Port 同步 CONTRACT_INDEX。

---

## 7. L5 — 前端合同（契约 §6、§11.5）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| 路由合同 | `frontend/routes.yaml` | vue-router history、守卫 |
| 页面清单 | `frontend/pages/*.md` | 工作台/客户/旅程/信号/知识等页面 |
| 状态合同 | `frontend/state/*.md` | Pinia setup store、composable |
| UX 流程 | `frontend/ux/*.md` | 主链交互、四态（Idle/Loading/Success/Error） |
| 组件合同 | `frontend/components/*.md` | Naive UI 主、TDesign 辅；禁混用同类组件 |
| 类型来源 | `frontend/api-contract.md` | 类型仅来自 `src/api`，不发明后端字段 |

**红线复核**：`<script setup lang="ts">`、禁 any/@ts-ignore、Tailwind、ECharts option 仅在前端。

---

## 8. L6 — 集成与部署（契约 §7、§11.6）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| EIP 集成 | `integration/eip/*.md`、`integration/event-flows.yaml` | 通道/路由/转换/幂等 |
| 适配器集成 | `integration/adapters/*.md` | CRM/Oracle/LLM/图数据库契约 |
| 部署拓扑 | `deployment/architecture-topology.md` | api(8080)/worker(8090)/DB/外部系统 |
| compose | `deployment/docker-compose*.yaml`、`compose-services.yaml` | 本地 H2/MySQL、依赖服务 |
| 环境与密钥 | `deployment/env-vars.yaml`、`secrets-management.md` | 无硬编码密钥；API Key 经头注入 |
| CI/CD | `deployment/cicd.yaml` | generate→check→test 门禁 |

**红线复核**：禁止日志输出密钥；CORS 仅 localhost:5173/8080；OWASP CVSS≥7 阻断。

---

## 9. L7 — 测试与验收（契约 §8、§11.7）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| 测试策略/矩阵 | `tests/test-strategy.md`、`test-matrix.yaml` | 单元/集成/合同/E2E 分层 |
| 合同测试 | `tests/contract/*.md` | Controller 响应符合 OpenAPI schema |
| 验收用例 | `acceptance/acceptance-cases.yaml` | 主链端到端可验收步骤 |
| 验收报告模板 | `acceptance/ACCEPTANCE_REPORT_TEMPLATE.md` | 证据/偏差/签署 |
| 包自检 | `acceptance/package_self_check.json` | 125/0；非独立 QA |

**测试约定**：JUnit5+AssertJ+Mockito；`*Test`/`*IT`；JaCoCo 行覆盖 ≥0.80；Vitest+Playwright。
**未完成项（如实标注）**：服务 E2E、Kuzu 集成、LightRAG 集成、真实人工审批 = NOT_PERFORMED。

---

## 10. L8 — 治理与运维（契约 §9、§11.8）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| RACI | `governance/raci.yaml` | Tech Lead/Feature Pilot/E2E Owner/独立 QA/Owner 职责 |
| 证据纪律 | `governance/evidence-policy.md` | 未落盘=不存在；失败先记 FAILURES |
| 变更控制 | `governance/change-control.md` | 合同→generate→check→实现 |
| 审计/合规 | `governance/audit-logging.md`、`compliance-mapping.md` | ControlledAction 全链路可审计 |
| 回滚预案 | `operations/rollback-runbook.md` | 可回退步骤 |
| 监控/Runbook | `operations/monitoring.md`、`incident-runbook.md` | health/info/metrics/prometheus |

**角色红线**：dev 仅 DEV_SELF_CHECK_PASS；只有独立 QA 记 QA_PASS；Supervisor 阻塞写 BLOCKED.md 不向人提问。

---

## 11. L9 — 种子与样例（契约 §10、§11.9）

| 交付物 | 路径 | 评审要点 |
|---|---|---|
| 种子数据 | `seeds/*.yaml`、`seeds/README.md` | H2 自动加载、演示客户/旅程/知识 |
| 样例请求 | `samples/requests/*.json` | 覆盖 17 端点典型入参 |
| 样例响应 | `samples/responses/*.json` | 符合 OpenAPI/分页/错误结构 |
| 样例事件 | `samples/events/*.json` | 符合 CloudEvent + 事件目录 |

---

## 12. 与当前代码库的落地对照（评审重点）

评审时建议把"合同交付物"与 `gits-cbanking` 现状逐项对账：

- 已落地：Spring Boot 3.5.16 六边形工程（modules/adapters/apps/scenario/frontend）、OpenAPI+generated、MyBatis+H2、DMN Claim 调和、LLM/CRM Port+降级、领域事件、P22 知识地图内存快照/Wiki、P23 场景知识 Provider。
- 安全基线（本分支近期工作）：GKB spring-framework 窄抑制（17 CVE，until 2026-10-31）；**GKD** spring-security 6.5.11 窄抑制（CVE-2026-59270/47841，until 2026-10-31，随 GKC Boot4 根治）+ tomcat 10.1.57→10.1.59；独立 QA `qa-gkd-formal-001` QA_PASS（15 模块、1808 测试 0 失败、零 ≥7 CVE、apps/api 行覆盖 0.8001）。
- 待建/合同先行项：Kuzu 图持久化、LightRAG 集成、真实人工审批工作流、服务级 E2E、生产 DB 迁移与密钥管理。

---

## 13. 评审检查清单（架构师逐项勾选）

- [ ] L0 包索引/哈希/自检真实可复核，未把作者自检冒充独立 QA。
- [ ] L1 OpenAPI/AsyncAPI/Schema 与现仓合同兼容，无合同外字段。
- [ ] L2 本体/知识架构概念闭环，SHACL/LinkML/R2RML/DMN 可校验。
- [ ] L3 数据模型与 Schema/事件一致，DDL 双方言、迁移策略合规。
- [ ] L4 Port/Adapter 分层无越界，降级策略覆盖外部依赖失败。
- [ ] L5 前端合同遵守四态/类型来源/UI 库约定。
- [ ] L6 集成/部署无硬编码密钥，CI 门禁与 CORS/OWASP 合规。
- [ ] L7 测试分层与覆盖率门槛明确，未完成项如实标注。
- [ ] L8 治理 RACI/证据/审计/回滚闭环，AI 边界与人控点明确。
- [ ] L9 种子/样例与合同一致。
- [ ] 合同包与现仓实现差异（§12）有明确后续 Loop 承接（GKC Boot4、Kuzu、LightRAG）。

## 14. 评审签署区

| 角色 | 结论 | 姓名 | 日期 | 意见/必改项 |
|---|---|---|---|---|
| 架构师 | ○通过 ○有条件通过 ○退回 | | | |
| Tech Lead | | | | |
| Owner（安全/人控相关） | | | | |

> 必改项请引用"层-交付物"编号（如 L1-OpenAPI / L4-Port）。退回项须在合同源 `specs/` 修改后重新 `make generate && make check`，不得直接改 `generated/`。
