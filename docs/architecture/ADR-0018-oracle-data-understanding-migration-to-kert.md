# ADR-0018｜Oracle 数据集市数据理解能力迁出至 Leibniz-KERT，并废弃 GITS 侧 OracleSourcePort

状态：`ACCEPTED_PENDING_CROSS_REPO_EXECUTION`

日期：2026-08-31

决策人：Owner

基线提交：`43bbc0cb0ea99d9f58ae2a20f202e7d461923bf2`（分支 `feature/P30-gits-bank-experience-shell`）

## 背景

架构盘点（2026-08-31，Tech Lead 只读盘点）确认 GITS 仓库当前的「本地 Oracle 数据集市数据理解能力」呈现严重的分层错配：

**离线侧已具备较强能力**：

- `ADR-0007` 已授权 Oracle EDwCRM（`oracle-vm:1521/ACRM`，账号 `edwcrm`）只读访问，`P1-oracle-readonly` loop 已 CLOSED 且独立 QA_PASS。
- `tools/quarantine/oracle/readonly_guard.py` 提供 fail-closed 只读强制；`profile.json` 记录 `write_policy: DENIED`、`transaction_policy: FAIL_CLOSED_READ_ONLY`。
- 仓库外已存在 22MB Oracle 元数据编目库（`/home/szf/dev/data/tzbank/data/metadata/oracle_metadata_catalog.sqlite`），实测含 71752 db_object、5817 column_metadata、4283 constraint_metadata、1182 derived_field、910 field_lineage、234 object_lineage、212 table_metadata、175 metric_definition、31 business_description。
- 三个消费脚本已将其转为领域资产：`scripts/oracle_metadata_to_seed.py`、`scripts/oracle_customer_to_operating_case.py`、`scripts/hermes_oracle_fusion.py`。
- 已登记为受控合同：`CTR-MAP-001`（R2RML）、`CTR-DATA-002`（源合同）、`CTR-DATA-003`（指标本体）、`CTR-DATA-004`（2505 条种子 Claim）。

**在线侧能力为零，且语义错配**：

- GITS 唯一的 Oracle 运行时端口 `OracleSourcePort` 仅定义 `List<OracleClaim> readClaims(LocalDateTime since)` 与 `isAvailable()`；`JdbcOracleSourceAdapter` 的 SQL 为 `SELECT ... FROM claim`，属**保险理赔单表同步**语义，与银行数据集市的数据理解（元数据、指标口径、血缘、衍生字段逻辑）无关。
- 该端口在 `apps/api` 运行时默认装配 `StubOracleSourceAdapter`（恒返回空列表、`isAvailable()` 恒 false），`oracle.source.enabled` 默认 `false`。
- 影响面核实结论：`OracleSourcePort` **零业务消费者**——除端口自身定义、Stub、`OracleHealthIndicator` 与测试外，无任何 Service / Controller 调用 `readClaims`。
- 离线产出的 2505 条数据理解 Claim **未被任何 Java / TypeScript 代码消费**，仅被 `CONTRACT_INDEX.yaml` 与 `tests/regression/regression-suite.yaml` 引用，属于「躺在磁盘上的死资产」。
- 编目库的采集器**不在本仓库内**（`tools/quarantine/oracle/` 仅有 README 与 guard），编目不可复现、不可增量刷新，Oracle 表结构变更时血缘会静默过期。

## 决策

Owner 于 2026-08-31 作出两项决策：

### 决策一：Oracle 数据集市数据理解能力迁出至 Leibniz-KERT 维护

「本地 Oracle 数据集市数据理解」不再由 GITS 承载与演进，改由 **Leibniz-KERT（DKWS，独立知识工程服务端）** 作为唯一维护方。GITS 后续若需该能力，**只能通过 Python Core 的公共 HTTP 接口调用**，不得在 GITS 内重建数据库直连的数据理解实现。

此决策与 KERT 的 C′ 混合架构定位一致：Python Core 是唯一公共入口、控制面与知识/数据权威源；GITS 仅通过 Python Core 公共 HTTP 调用。

### 决策二：废弃 `OracleSourcePort.readClaims`（claim 表）

`OracleSourcePort` 及其 `OracleClaim` 模型所对应的 `claim` 表数据与本项目业务无关，予以废弃并物理移除相关实现代码。

## 跨仓库执行约束（强制）

### 约束 A：两仓不得混做，执行顺序不可颠倒

`Leibniz-KERT/AGENTS.md` §3 Rule 1 明确「不得修改 GITS 仓库」。因此本决策**不是一次迁移动作**，必须拆为两个独立 Loop、两个仓库、两次会话：

| 顺序 | Loop | 仓库 | 作用 |
|---|---|---|---|
| 1 | `KERT-M7.x-oracle-data-understanding` | Leibniz-KERT | 先建能力 |
| 2 | `P38-oracle-deprecation` | gits-cbanking | 后拆残留 |

`P38` 必须等 KERT 侧能力交付（Skill + OpenAPI 端点可用）后才可置为 `in_progress`，否则会出现能力真空。本 ADR 落盘时 `P38` 状态为 `blocked`。

严禁在 KERT 侧会话中删除 GITS 代码，亦严禁在 GITS 侧会话中创建 KERT 实现。

### 约束 B：编目载体必须按「文本权威 + 可重建投影」分层（对应 KERT 冲突 C-08）

Oracle 数据理解能力的核心载体是 SQLite 编目库，这直接触及 KERT 未决冲突 **C-08**（「原始规格禁止数据库 vs 生产演进引入 SQLite」，状态 `PENDING_OWNER_DECISION`）。Owner 批准采用与既有先例 `IMP-ADR-011`（Kùzu 嵌入式图数据库受控豁免）**完全同构**的论证结构解决：

| DKWS 分层 | 承载内容 | 理由 |
|---|---|---|
| `01_raw/oracle_edwcrm/` | 采集器导出的原始数据字典快照（JSONL/CSV，纯文本、可 diff、可审计） | 权威原始输入，文本化不违反「禁数据库」 |
| `02_work/` | 归一化中间产物 | 常规工作层 |
| `03_core/oracle_understanding/` | 指标口径 / 血缘 / 衍生字段逻辑的权威知识事实（文件化，带 `effective_from/to`） | 权威源保持文件化，与 DKWS-SPEC 一致 |
| `04_serve/<svc>/version=*/catalog/` | SQLite 查询加速投影（可删除、可重建） | 与 IMP-ADR-011 同构：投影层允许嵌入式库 |

强制要求：**采集器必须入仓**。唯有如此，SQLite 才是「声明式可重建投影」而非「隐藏持久化数据库文件」，C-08 方能在本能力范围内推为 RESOLVED，而非被绕过。此项同时修复本盘点发现的「编目不可复现」缺口。

投影层必须纳入可重建性测试：删除投影后仅凭 `03_core` 重建，逻辑指纹一致。

### 约束 C：Oracle 只读授权必须在 KERT 侧重新建立

GITS 侧授权载体为 `ADR-0007` + `tools/quarantine/oracle/profile.json`，**不随代码自动生效**。KERT 侧必须自建：

- 独立 ADR（Oracle 只读接入 + 编目投影受控豁免）；
- 数据所有者授权记录 —— **签署方已确定：Owner 兼任数据 owner，已于 2026-08-31 授权（见下「授权记录」）**。KERT 侧 G0 ADR 须显式登记该授权，不得省略；
- `readonly_guard` 移植，保持 fail-closed 与 `SET TRANSACTION READ ONLY` 强制；
- 凭据继续存放于仓库外 `~/.local_database.env`（`GITS_ORACLE_*`），**绝不入仓**；
- 保持 `source_capture: HASH_AND_LOCATOR_BY_DEFAULT`，不得在仓库内保存客户行数据；
- 仅查数据字典视图，禁止 SELECT 业务表。

在 KERT 侧 G0/G1 完成前（即授权落盘 + 只读守卫生效前），不得建立真实 Oracle 连接。

## GITS 侧废弃清单

### 待移除（`P38` 执行，零业务消费者，低风险）

| 类型 | 路径 |
|---|---|
| Port | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/port/OracleSourcePort.java` |
| Model | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/model/OracleClaim.java` |
| 适配器模块（整体） | `adapters/oracle-source/`（含 `JdbcOracleSourceAdapter`、`OracleSourceAutoConfiguration`、`OracleSourceProperties` 及测试） |
| 根 pom 模块声明 | `pom.xml`（`<module>adapters/oracle-source</module>`） |
| Stub | `apps/api/src/main/java/com/gien/gits/adapter/oracle/StubOracleSourceAdapter.java` |
| 运行时装配 | `apps/api/src/main/java/com/gien/gits/api/config/EngagementConfig.java` 中 Oracle bean |
| 健康检查 | `apps/api/src/main/java/com/gien/gits/api/health/OracleHealthIndicator.java` 及其测试 |
| 运行配置 | `apps/api/src/main/resources/application-oracle.yaml` |

### 待迁移（移交 KERT，非删除）

| 资产 | 路径 | 处置 |
|---|---|---|
| 只读守卫与授权档 | `tools/quarantine/oracle/` | 迁移到 KERT，GITS 侧保留至 `P38` 收尾 |
| 采集消费脚本 | `scripts/oracle_metadata_to_seed.py`、`scripts/oracle_customer_to_operating_case.py`、`scripts/hermes_oracle_fusion.py`、`scripts/db/oracle_metadata_spike.sh`、`scripts/db/oracle_readonly_check.sh` | 迁移到 KERT 并改造为入仓采集器 |
| 数据理解合同 | `specs/data/*`（`CTR-MAP-001` / `CTR-DATA-002` / `CTR-DATA-003` / `CTR-DATA-004`） | 移交 KERT 作为权威源输入；GITS 侧标 `migration_target`，**不物理删除** |

### 禁止改动（红线）

- `loops/P1-oracle-readonly/`、`loops/P13/`、`loops/P15/`：均已 CLOSED，禁止覆盖已完成 Loop 状态。
- `ADR-0007`：不删除历史 ADR，仅由本 ADR 标注其 Oracle 承载方变更。
- `generated/data/`：不得手工编辑；随合同条目一并标记，由 `make generate` 维护。

## 合同处置方式

Owner 决定采用「**复制到 KERT 后 GITS 标 superseded**」而非物理迁出，以保留证据可追溯性（符合工作区证据纪律与 KERT §3 Rule 7「不删除历史文档」）。

本 ADR 落盘阶段在 `specs/CONTRACT_INDEX.yaml` 对四个条目追加标记（不改 `authority_source`、不改 `generated`，因此不触发 `make generate` 重算与哈希漂移）：

- `migration_target: "Leibniz-KERT"`
- `migration_adr: "ADR-0018"`
- `migration_status: "pending_kert_landing"`

待 KERT 侧能力交付且 `P38` 完成后，再由独立提交将 `migration_status` 推进为 `superseded_by_kert`。

## 授权记录

| 角色 | 状态 | 说明 |
|---|---|---|
| Owner | GRANTED | 2026-08-31 决策：能力迁 KERT 维护；`OracleSourcePort` 废弃 |
| DATA_OWNER（KERT 侧 Oracle 只读） | GRANTED | 2026-08-31 Owner 明确以数据 owner 身份**兼任签署方**，授权 KERT 侧对 `oracle-vm:1521/ACRM`（账号 `edwcrm`）的只读访问。沿用 ADR-0007 的只读边界：`SET TRANSACTION READ ONLY` fail-closed 强制、禁一切写、仅查数据字典视图、`HASH_AND_LOCATOR_BY_DEFAULT` 不落客户行数据、凭据仓库外置。KERT 侧仍须在其 G0 ADR 中登记本授权（授权不因跨仓自动生效，须显式落盘） |
| DBA（KERT 侧） | PENDING | 沿用 ADR-0007 处置：owner 指示只读先行，DBA 书面确认作为 KERT 侧 Loop 收尾条件之一，不阻塞只读验证 |
| SECURITY_OWNER（KERT 侧） | PENDING | 同上，安全 owner 复核待补，不阻塞只读验证 |
| C-08 冲突裁决 | GRANTED（范围内） | Owner 批准按约束 B 分层方案处理，推动 C-08 在本能力范围内 RESOLVED |

## 后果

**正面**：

- 数据理解能力归位到专职知识工程服务端，符合 C′ 混合架构的权威源单一化目标。
- 采集器入仓解决编目不可复现问题，血缘不再静默过期。
- GITS 移除零消费者的错配端口，减少认知负担与虚假能力暗示。
- 2505 条死资产在 KERT 侧获得运行时消费路径（Skill + HTTP 端点）。

**负面与风险**：

- 跨仓库协作成本上升，需两次会话与严格顺序；期间存在能力窗口期（由 `P38` 的 `blocked` 状态防护）。
- KERT 侧 `ingest()` 现有签名为 `sources: list[Path]`，且 `infrastructure/adapters/` 现仅有 `docx_parser` / `pdf_parser` / `text_parser` / `llm` 四个**文件型**源。数据库型知识源是新的源类别，会触及 `ingest` 抽象，需扩展而非硬塞——这是 KERT 侧主要技术风险点。
- GITS 未来消费需走 HTTP，引入网络依赖与降级需求。

**未决**：

- R2RML 映射现状仅为占位（`customer-source-mapping.r2rml.ttl` 仅映射 `A_ZHCX_CUST_BASE` 主键到 `gits:Customer`，无 `rr:predicateObjectMap`），而 `specs/data/oracle-to-gits-mapping.md` 描述的 8 表 300+ 列映射仅为文档设计。该「文档比合同丰富」的反向漂移由 KERT 侧在正式化时消除。
- 数据画像（profiling：空值率、基数、分布、新鲜度）能力两仓均不存在，由 KERT 侧后续里程碑承接。

## 待验证

- KERT 侧 Oracle 只读连接与 fail-closed 强制复现成功；
- 采集器可从零重建编目，逻辑指纹一致；
- `04_serve` 投影删除后可仅凭 `03_core` 重建；
- 数据理解 Skill 与 OpenAPI 端点可被 GITS 通过公共 HTTP 调用；
- `P38` 完成后 GITS `make generate` / `make check` / `make backend-test` 全绿；
- 独立 QA 复核（实现角色只能记录 `DEV_SELF_CHECK_PASS`）。

## 参考

- `docs/architecture/ADR-0007-oracle-readonly-enablement.md`（GITS 侧原只读授权）
- `docs/architecture/ORACLE_UNDERSTANDING_MIGRATION_PLAN.md`（KERT 侧执行计划）
- `loops/P38-oracle-deprecation/LOOP.yaml`（GITS 侧废弃 Loop，blocked）
- `Leibniz-KERT/ADR.md` → `IMP-ADR-011`（Kùzu 受控豁免先例，本 ADR 约束 B 的论证模板）
- `Leibniz-KERT/docs/governance/DKWS_DOCUMENT_CONFLICT_REGISTER.md` → `C-08`
- `Leibniz-KERT/docs/development/DKWS_WORK_BREAKDOWN_STRUCTURE_V1.0.md` → `M7.1 KnowledgeSource typed capability`
