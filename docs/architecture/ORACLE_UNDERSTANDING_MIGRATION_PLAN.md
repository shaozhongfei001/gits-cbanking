# Oracle 数据集市数据理解能力迁移计划（GITS → Leibniz-KERT）

状态：`APPROVED_FOR_KERT_EXECUTION`

日期：2026-08-31

权威依据：`docs/architecture/ADR-0018-oracle-data-understanding-migration-to-kert.md`

GITS 基线提交：`43bbc0cb0ea99d9f58ae2a20f202e7d461923bf2`

## 本文档用途

本文档由 GITS 侧 Tech Lead 编写，**供 Leibniz-KERT 工作区的会话直接读取执行**。

KERT 侧 agent 应在 Leibniz-KERT 工作区读取本文档，据此在 **KERT 仓库内**建立 Loop 并实现能力。

**强制**：KERT 侧会话严禁修改 GITS 仓库（`Leibniz-KERT/AGENTS.md` §3 Rule 1）。GITS 侧的废弃动作由 GITS 自己的 Loop `P38-oracle-deprecation` 执行。

---

## 一、迁移动因（已核实的事实，非推测）

### 1.1 GITS 在线侧能力为零且语义错配

| 事实 | 证据 |
|---|---|
| 唯一 Oracle 端口是 `OracleSourcePort.readClaims(LocalDateTime)` | `modules/operational-ontology/.../port/OracleSourcePort.java` |
| 实际 SQL 为 `SELECT ... FROM claim`（保险理赔单表语义） | `adapters/oracle-source/.../JdbcOracleSourceAdapter.java` |
| 运行时默认装配 Stub，恒返回空列表 | `apps/api/.../StubOracleSourceAdapter.java`，`oracle.source.enabled: false` |
| 零业务消费者 | 全仓检索 `readClaims(` 仅命中端口声明 + 两个实现，无 Service/Controller 调用 |

Owner 已决定废弃该端口（数据与本项目业务无关）。

### 1.2 GITS 离线侧能力较强但与运行时断链

2505 条数据理解 Claim 仅被 `CONTRACT_INDEX.yaml` 与回归清单引用，**无任何 Java / TypeScript 代码消费**。

### 1.3 编目不可复现（必须修复的缺口）

外部编目库真实存在但**采集器不在 GITS 仓库内**：

- 路径：`/home/szf/dev/data/tzbank/data/metadata/oracle_metadata_catalog.sqlite`（22MB）
- GITS 侧 `tools/quarantine/oracle/` 仅有 `README.md` + `readonly_guard.py`，**无采集脚本**

后果：Oracle 表结构变更时血缘会静默过期，编目无法增量刷新。

**KERT 侧必须把采集器入仓**（见 G2）。

---

## 二、可用资产清单（KERT 侧接收物）

### 2.1 外部编目库实测内容（仓库外，22MB SQLite）

| 表 | 行数 | 语义 |
|---|---|---|
| db_object | 71752 | 数据库对象清单 |
| source_code | 9329 | 对象源码 |
| column_metadata | 5817 | 列级元数据 |
| constraint_metadata | 4283 | 约束元数据 |
| derived_field | 1182 | 衍生字段计算逻辑 |
| field_lineage | 910 | 字段级血缘 |
| object_dependency | 344 | 对象依赖 |
| object_lineage | 234 | 对象级血缘 |
| table_metadata | 212 | 表级元数据 |
| metric_definition | 175 | 指标口径（中英文名 + 业务定义 + 公式） |
| sql_statement | 118 | SQL 语句 |
| business_description | 31 | 业务释义 |
| program_unit | 31 | 程序单元 |
| analysis_issue | 4 | 分析议题 |

### 2.2 GITS 侧脚本（迁移并改造）

| 路径 | 作用 |
|---|---|
| `tools/quarantine/oracle/readonly_guard.py` | fail-closed 只读强制（`SET TRANSACTION READ ONLY`，失败即关连接），含离线自测 |
| `tools/quarantine/oracle/profile.json` | 授权档：`write_policy: DENIED`、`transaction_policy: FAIL_CLOSED_READ_ONLY`、`source_capture: HASH_AND_LOCATOR_BY_DEFAULT` |
| `scripts/db/oracle_readonly_check.sh` | 只读连通性校验 |
| `scripts/db/oracle_metadata_spike.sh` | 数据字典探查（`user_tables` / `user_tab_columns`），`/nolog + CONNECT` 避免 argv 泄露 |
| `scripts/oracle_metadata_to_seed.py` | 编目 → 2505 条 Claim（175 指标 + 910 字段血缘 + 234 对象血缘 + 1182 衍生字段 + 4 风险信号） |
| `scripts/oracle_customer_to_operating_case.py` | 从 `A_ZHCX_CUST_BASE` / `F_CUST_LOAN_IFO`(55列) / `F_CUST_DEPR_IFO`(61列) / `F_CUST_ZCAMT_IFO`(75列) / `F_CUST_OWNED_PRODUCT` 构建 OperatingCase |
| `scripts/hermes_oracle_fusion.py` | 把口径/血缘作为数据质量注解 + 可追溯性证据 + 可解释性 |

### 2.3 GITS 侧合同（作为权威源输入移交）

| 合同 ID | 权威源 | 内容 |
|---|---|---|
| `CTR-MAP-001` | `specs/data/customer-source-mapping.r2rml.ttl` | R2RML 映射（**仅骨架占位**，见风险 R3） |
| `CTR-DATA-002` | `specs/data/src-edwcrm-cust-base.v0.1.json` | 源合同 |
| `CTR-DATA-003` | `specs/data/src-oracle-metric-ontology.v0.1.json` | 175 指标本体 |
| `CTR-DATA-004` | `specs/data/oracle-seed-claims.v0.1.json` | 2505 条种子 Claim |
| — | `specs/data/oracle-to-gits-mapping.md` | 8 表 300+ 列映射设计（**仅文档，未成合同**） |

这些条目在 GITS 侧已标记 `migration_target: Leibniz-KERT`、`migration_adr: ADR-0018`、`migration_status: pending_kert_landing`，**权威源与 generated 均未删除**（保留可追溯性）。

### 2.4 连接信息

- Oracle：`oracle-vm:1521/ACRM`，账号 `edwcrm`
- 凭据：仓库外 `~/.local_database.env` 的 `GITS_ORACLE_*` 环境变量
- **绝不入仓**

---

## 三、KERT 侧落点设计

### 3.1 分层落点（解决冲突 C-08 的核心设计）

Oracle 数据理解的核心载体是 SQLite 编目库，直接触及 KERT 未决冲突 **C-08**（「原始规格禁止数据库 vs 生产演进引入 SQLite」，`PENDING_OWNER_DECISION`）。

Owner 已批准采用与既有先例 **`IMP-ADR-011`（Kùzu 嵌入式图数据库受控豁免）完全同构**的论证结构处理：

| DKWS 分层 | 承载内容 | 是否允许数据库文件 | 理由 |
|---|---|---|---|
| `01_raw/oracle_edwcrm/` | 采集器导出的原始数据字典快照（JSONL/CSV） | 否，纯文本 | 权威原始输入，文本化、可 diff、可审计 |
| `02_work/` | 归一化中间产物 | 否 | 常规工作层 |
| `03_core/oracle_understanding/` | 指标口径 / 血缘 / 衍生字段逻辑的**权威知识事实**（文件化，带 `effective_from/to`） | 否 | 权威源保持文件化，与 DKWS-SPEC §1.5/§2.2 一致 |
| `04_serve/<svc>/version=*/catalog/` | SQLite 查询加速**投影** | **是（受控豁免）** | 与 IMP-ADR-011 同构：投影层可重建、可删除 |

**关键约束（照抄 IMP-ADR-011 边界结构）**：

1. 编目投影只从 `03_core` 活动投影构建，位置 `04_serve/<service>/version=*/catalog/`；
2. **禁止**编目库进入 `01_raw` / `02_work` / `03_core`；`03_core` 仍是唯一权威源；
3. 查询结果必须回传权威 ID + 证据引用（如 `metric_id` / `lineage_id` / `effective_from/to`）；
4. 编目投影纳入可重建性测试：删除后仅凭 `03_core` 重建，逻辑指纹一致；
5. 验收口径为「无隐藏持久化数据库文件」——编目库是声明式可重建投影，需在 `PROJECTION.md` 声明；
6. 若投影构建失败，查询能力应降级到文件化读取（fail-open），或明确 fail-closed 并给出可诊断错误。

**唯有采集器入仓**，SQLite 才成立为「声明式可重建投影」而非「隐藏持久化数据库」。这是 C-08 得以在本能力范围内推为 RESOLVED 的前提，而非绕过。

### 3.2 WBS 落点

建议挂到 `docs/development/DKWS_WORK_BREAKDOWN_STRUCTURE_V1.0.md` 的 **`M7.1 KnowledgeSource typed capability`**（现为空壳标题，正好承接「数据库型知识源」这一新源类别）。

### 3.3 对外暴露方式

GITS 未来只能通过 Python Core 公共 HTTP 调用（`Leibniz-KERT/AGENTS.md` §1）。因此需要：

- 注册 Skill：`oracle.data_understanding`
- 扩展 `specs/dkws-openapi-v1.yaml` 新增端点

建议能力面（对应修复 GITS 盘点发现的缺口）：

| 能力 | 说明 |
|---|---|
| `listObjects` | 对象清单查询（schema / 类型 / 名称过滤） |
| `describeTable` | 表级 + 列级元数据、约束 |
| `metricDefinition` | 指标口径（中英文名、业务定义、公式） |
| `fieldLineage` | 字段级血缘（上下游追溯） |
| `objectLineage` | 对象级血缘与依赖 |
| `derivedFieldLogic` | 衍生字段计算逻辑解释 |

注意：这套能力**语义上完全不同于** GITS 被废弃的 `readClaims`，不要复用其命名或形态。

---

## 四、Gate 定义（建议 Loop：`KERT-M7.x-oracle-data-understanding`）

| Gate | 交付物 | 通过条件 |
|---|---|---|
| **G0** | ADR：Oracle 只读接入 + 编目投影受控豁免 | 引用 `IMP-ADR-011` 论证结构；关联 C-08 并给出裁决；**登记 §8 授权表（Owner 兼任数据 owner，已 GRANTED）** |
| **G1** | `readonly_guard` 移植 + 凭据外置 | fail-closed 生效；`SET TRANSACTION READ ONLY` 强制；仅查数据字典视图；禁 SELECT 业务表；凭据不入仓 |
| **G2** | **采集器入仓**（如 `scripts/oracle_catalog_collect.py`） | 可从零重建 `01_raw` 文本快照；支持增量刷新；输出可 diff |
| **G3** | `01_raw → 03_core` 知识化 | 指标口径 / 血缘 / 衍生字段成为文件化权威事实，带 `effective_from/to`；复用现有 `ingest` 与 `_write_lineage` |
| **G4** | `04_serve` 编目投影 + 数据理解服务 | 六项能力可用；可重建性测试通过（删投影后仅凭 Core 重建，逻辑指纹一致） |
| **G5** | Skill 注册 + OpenAPI v1 端点 | GITS 可通过公共 HTTP 调用；契约与实现一致 |
| **G6** | 独立 QA | 实现角色只能记 `DEV_SELF_CHECK_PASS`；不得自签 `QA_PASS`（`AGENTS.md` §3 Rule 6） |

**G5 是 GITS 侧 `P38` 的解锁条件。** G5 交付并经 Owner 确认后，GITS 才可启动废弃。

---

## 五、技术风险（KERT 侧需正面处理）

### R1：`ingest()` 抽象只支持文件型源（主要风险）

现状核实：

- `src/dkws/infrastructure/adapters/` 仅有 `base.py`、`docx_parser.py`、`pdf_parser.py`、`text_parser.py`、`llm.py` —— **全部文件型**
- `src/dkws/application/ingest.py` 的 `ingest()` 签名为 `sources: list[Path]`

数据库型知识源是**新的源类别**。必须**扩展抽象**（如引入 `KnowledgeSource` typed capability，正对应 M7.1），**不要把数据库连接硬塞进 `list[Path]`**。

建议路径：采集器先落 `01_raw` 文本快照，再让现有 `ingest` 消费文本 —— 这样可避免第一版就改动 `ingest` 核心抽象，把风险后移到 G4/G5。

### R2：C-08 未决冲突

不要在 C-08 未裁决的情况下直接引入 SQLite。必须在 G0 的 ADR 中一并裁决（Owner 已批准按 §3.1 分层方案处理）。

### R3：R2RML 仅为占位，文档比合同丰富（反向漂移）

- `specs/data/customer-source-mapping.r2rml.ttl`：只有一个 `TriplesMap`，只映射 `A_ZHCX_CUST_BASE` 主键到 `gits:Customer`，**没有一条 `rr:predicateObjectMap`**
- `specs/data/oracle-to-gits-mapping.md`：描述 8 张表 300+ 列映射，**仅文档设计**

这是「低权威（文档）比高权威（合同）丰富」的反向漂移。KERT 侧正式化时必须消除：要么把文档升级为合同，要么明确文档为候选设计并标注。

### R4：Oracle 只读授权不随代码生效

GITS 的 `ADR-0007` 授权在 KERT 侧无效。签署方虽已确定（Owner 兼任，见 §8），但**必须在 KERT 侧 G0 ADR 中显式落盘**才算生效——未落盘的授权对其它 Agent 视为不存在。G0/G1 完成前不得建立真实 Oracle 连接。

### R5：数据画像能力两仓均不存在

profiling（空值率、基数、分布、异常值、数据新鲜度、跨表一致性）**当前完全没有**。`analysis_issue` 仅 4 条且来自外部编目库，非本项目生成。

如需该能力，应作为后续里程碑，并遵守 `source_capture: HASH_AND_LOCATOR_BY_DEFAULT`：只读、只统计、**不落客户行数据**。

---

## 六、GITS 侧配套动作（已完成，供 KERT 侧核对）

本计划落盘时 GITS 侧已同步完成：

| 动作 | 产物 |
|---|---|
| 决策落盘 | `docs/architecture/ADR-0018-oracle-data-understanding-migration-to-kert.md` |
| ADR 索引更新 | `docs/architecture/ADR_INDEX.md` 新增 ADR-0018 行 |
| 废弃 Loop 骨架（**blocked**） | `loops/P38-oracle-deprecation/`（`LOOP.yaml`、`STATE.json`、`EVIDENCE.md`、`FAILURES.md`、`memory/NEXT_SESSION.md`） |
| 合同迁移标记（**不删除**） | `specs/CONTRACT_INDEX.yaml` 中 `CTR-MAP-001` / `CTR-DATA-002` / `CTR-DATA-003` / `CTR-DATA-004` 追加 `migration_target` / `migration_adr` / `migration_status` |

GITS 侧**未删除任何实现代码**，能力窗口期由 `P38` 的 `blocked` 状态防护。

---

## 七、KERT 侧建议启动提示词

```text
你是 DKWS Tech Lead。
先读 /home/szf/dev/gits-cbanking/docs/architecture/ORACLE_UNDERSTANDING_MIGRATION_PLAN.md，
再读本仓 ADR.md 的 IMP-ADR-011、docs/governance/DKWS_DOCUMENT_CONFLICT_REGISTER.md 的 C-08、
docs/development/DKWS_WORK_BREAKDOWN_STRUCTURE_V1.0.md 的 M7.1。
在本仓建立 Loop KERT-M7.x-oracle-data-understanding，先只交付 G0（ADR：Oracle 只读接入 + 编目投影受控豁免）。
严禁修改 GITS 仓库。严禁自签 QA_PASS。完成 G0 后 STOP。
```

---

## 八、授权状态（已确定，无待确认项）

| 项 | 状态 | 说明 |
|---|---|---|
| KERT 侧 Oracle 只读授权签署方 | **GRANTED — Owner 兼任** | Owner 于 2026-08-31 以数据 owner 身份兼任签署方，授权 KERT 侧对 `oracle-vm:1521/ACRM`（账号 `edwcrm`）只读访问 |
| DBA（KERT 侧） | PENDING（不阻塞） | 沿用 ADR-0007 处置：只读先行，书面确认作为 KERT 侧 Loop 收尾条件 |
| SECURITY_OWNER（KERT 侧） | PENDING（不阻塞） | 同上 |
| C-08 冲突裁决 | GRANTED（本能力范围内） | 按 §3.1 分层方案处理 |

**KERT 侧 G0 ADR 必须显式登记上表**——授权不因跨仓库自动生效，未落盘即视为不存在。

授权边界（沿用 ADR-0007，不得放宽）：

- 连接后先执行 `SET TRANSACTION READ ONLY`，失败即关连接并终止；
- 禁止任何写操作；
- 仅查数据字典视图，禁止 SELECT 业务表；
- `source_capture: HASH_AND_LOCATOR_BY_DEFAULT`，不得在仓库内保存客户行数据；
- 凭据存放仓库外 `~/.local_database.env`（`GITS_ORACLE_*`），绝不入仓；
- 编目输出仅作数据映射证据/候选语义，不得自动升级为业务主本体。
