# P38-oracle-deprecation — 证据记录

Loop 状态：`blocked`（有意阻塞，非失败）

基线提交：`43bbc0cb0ea99d9f58ae2a20f202e7d461923bf2`

立项提交：`b176664`（`contract(data): migrate Oracle data-understanding capability to Leibniz-KERT`，2026-08-31，10 files changed, 767 insertions(+), 4 deletions(-)）

权威依据：`docs/architecture/ADR-0018-oracle-data-understanding-migration-to-kert.md`

## 立项证据（2026-08-31，Tech Lead 只读盘点）

### 影响面核实：`OracleSourcePort` 零业务消费者

对 `OracleSourcePort` / `OracleClaim` / `oracle.source` 做全仓引用检索（排除 `target/`），命中点分类如下：

| 类别 | 位置 |
|---|---|
| 端口自身定义 | `modules/operational-ontology/.../port/OracleSourcePort.java` |
| 领域模型 | `modules/operational-ontology/.../model/OracleClaim.java` |
| 真实适配器 | `adapters/oracle-source/.../JdbcOracleSourceAdapter.java`、`OracleSourceAutoConfiguration.java`、`OracleSourceProperties.java` |
| Stub 适配器 | `apps/api/.../adapter/oracle/StubOracleSourceAdapter.java` |
| 运行时装配 | `apps/api/.../api/config/EngagementConfig.java` |
| 健康检查 | `apps/api/.../api/health/OracleHealthIndicator.java` |
| 测试 | `adapters/oracle-source/src/test/.../JdbcOracleSourceAdapterTest.java`、`apps/api/src/test/.../OracleHealthIndicatorTest.java` |
| 构建声明 | `pom.xml`（`<module>adapters/oracle-source</module>`） |
| 历史 Loop 记录（禁改） | `loops/P13/LOOP.yaml`、`loops/P15/LOOP.yaml`（均 CLOSED） |

对 `oracleSourcePort.` 与 `readClaims(` 的调用点检索结果：仅出现在端口声明、Stub 实现、真实适配器实现三处，**无任何 Service / Controller / Orchestrator 调用**。

结论：废弃属**低风险纯删除**，不影响任何业务链路。

### 运行时能力现状

- `oracle.source.enabled` 默认 `false`（`apps/api/src/main/resources/application-oracle.yaml`）。
- `apps/api` 默认装配 `StubOracleSourceAdapter`，`readClaims` 恒返回空列表，`isAvailable()` 恒 `false`。
- 结论：GITS 运行时**从未真实提供** Oracle 数据理解能力。

### 语义错配证据

`JdbcOracleSourceAdapter` 查询语义为 `SELECT ... FROM claim`（保险理赔单表），与银行数据集市数据理解（元数据 / 指标口径 / 血缘 / 衍生字段逻辑）无关。Owner 确认该数据与本项目业务无关。

### 离线资产与运行时断链证据

对 `oracle-seed-claims` / `src-oracle-metric-ontology` / `hermes-oracle-fusion` 的全仓引用检索：仅被 `specs/CONTRACT_INDEX.yaml` 与 `tests/regression/regression-suite.yaml` 引用，**无任何 Java / TypeScript 代码消费**。2505 条数据理解 Claim 为未激活资产。

### 外部编目库实测（仓库外）

路径：`/home/szf/dev/data/tzbank/data/metadata/oracle_metadata_catalog.sqlite`（22MB，存在）

| 表 | 行数 |
|---|---|
| db_object | 71752 |
| column_metadata | 5817 |
| source_code | 9329 |
| constraint_metadata | 4283 |
| derived_field | 1182 |
| field_lineage | 910 |
| object_dependency | 344 |
| object_lineage | 234 |
| table_metadata | 212 |
| metric_definition | 175 |
| sql_statement | 118 |
| business_description | 31 |
| program_unit | 31 |
| analysis_issue | 4 |

采集器**不在 GITS 仓库内**，编目不可复现——此缺口由 KERT 侧「采集器入仓」修复。

## Gate 证据

| Gate | 状态 | 证据 |
|---|---|---|
| precondition_kert_landed | BLOCKED | 外部依赖未交付，等待 Leibniz-KERT `KERT-M7.x-oracle-data-understanding` |
| remove_oracle_source_port | NOT_STARTED | — |
| contract_migration_marked | PARTIAL | 本次已追加 `migration_target` / `migration_adr` / `migration_status: pending_kert_landing`；推进为 `superseded_by_kert` 待 Gate 执行 |
| contract_generate | NOT_STARTED | — |
| contract_check | NOT_STARTED | — |
| security_check | NOT_STARTED | — |
| backend_test | NOT_STARTED | — |
| evidence_check | NOT_STARTED | — |

## 声明

本 Loop 立项阶段未修改任何实现代码，仅落盘 ADR、Loop 骨架、迁移计划与合同迁移标记。

实现角色不得自签 `QA_PASS`；本记录不构成 `DEV_SELF_CHECK_PASS`。
