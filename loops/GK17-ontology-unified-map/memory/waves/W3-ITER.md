# W3｜ITER 记录

## ITER 1｜WP3.1 产品卡 → RDF（2026-09-15）

### 产出

| 路径 | 内容 |
|---|---|
| `scripts/gk17_prodcard_to_rdf.py` | 确定性投影器（纯 stdlib，fail-closed，支持 `--id-map` / `--allow-unresolved` / `--verify-determinism` / `--json`） |
| `specs/knowledge-architecture/instances/product/products.ttl` | **13 个 `gits:Product` 个体** |
| `specs/knowledge-architecture/instances/product/UNRESOLVED.json` | **40 条无法解析的引用**（逐条记录来源卡 + 字段 + 符号 + 原因） |

### 实测事实（**本次最重要的发现**）

| 项 | 实测值 |
|---|---|
| 产品卡数 | **13** |
| 卡身份空间 | `PROD-{CM,CB,FIN,IB,SET,TF}-NNN` |
| 卡中引用的 product_id | **12 个唯一符号**（`SETTLEMENT_ACCOUNT` / `CORPORATE_E_BANK` / `CASH_MANAGEMENT` …） |
| 引用**能解析到真实卡**的 | **0 / 12** |
| 引用**出现次数** | **40**（13 张卡 × 三字段展开） |
| ⇒ 投影产出的**关系实例** | **0** |

> **身份空间冲突**：`CASH_MANAGEMENT` 既是 `product_family` 编码，又被当作"配套产品"引用。
> 被引用的 12 个符号**没有任何一个**是 `PROD-*` ID ⇒ 产品卡的"前置/互斥/配套"引用的是
> **一个未被产品卡覆盖的产品空间**。

### ACCEPT 判据核验

| 判据 | 结果 |
|---|---|
| 个体数可度量 | **13** ✅ |
| 重复投影**逐字节一致** | `determinism: IDENTICAL sha256=e70bbe45bebcca2ebc3cb9e805c3cf8b87961221d19f898f4571ccc90151b739` ✅ |
| **非空转证明** | 用**临时** id-map（`SETTLEMENT_ACCOUNT`→`PROD-SET-001`）实测 ⇒ **关系实例 24 条**，`gits:requiresProduct` / `gits:complementsProduct` 三元组真实产出 ⇒ **投影器不是靠夹具缺失空转** ✅（演示用临时映射已删除，权威态重生成） |
| 严格模式仍 fail-closed | `strict exit=2`（40 条悬空）✅ |
| 新制品不使门禁转红 | `make check` exit 0 / 22-23 / INTEGRITY 空 ✅ |

### 未决（**须产品 Owner 裁定**，属停止条件 #2「需求冲突」）

产品卡的关系实例引用了一个**未受控的标识空间**。三条出路（**均不得由 TL 单方选定**）：

| 出路 | 内容 | 代价 |
|---|---|---|
| **(a) 卡内改为 `PROD-*` 引用** | 产品 Owner 把 `prerequisite_product_ids` 等改为引用真实产品卡 ID | 权威源变更，需产品 Owner 执行 |
| **(b) `PROD-* ⇄ 符号名` 身份映射入册** | 新建受控映射（每行须可核），投影按映射解析 | 新增一个受控定义面 |
| **(c) 明确"符号名不是产品"** | 承认这些是产品族/能力代号，另行建模（不入 `gits:Product`） | 需重新界定关系语义 |

> **在裁定前**：投影按裁定 **fail-closed**（strict exit 2）；仓内**只保留** 13 个体 + `UNRESOLVED.json`
> 作为**缺陷证据**，**不**写入任何关系实例（避免以未裁定口径污染 A-Box）。

### 待办

- **WP3.2** 事实对象（客户 / 集团 / 法人）→ RDF：源为仓内 `V011` / `V018`，**未开始**；
- 产品卡输入的**外部依赖**：`--cards-dir` 指向工作区外；`make`/CI 不覆盖 ⇒ 本 Loop 以
  `record_gate.py` 记录命令与结果，并在 W8 说明该依赖。

## WP3.2｜**阻塞（降级处理）**，2026-09-15

### 阻塞事实（实测，非推测）

**同一实体「法人」在本仓有两套互不兼容的 `legal_entity` 定义**：

| 来源 | 列 |
|---|---|
| 迁移脚本 `adapters/persistence-relational/.../mysql/V003__customer_context.sql:32` | `entity_id, group_id, name, role, ownership, bank_customer_id, relationship_status, evidence_ref` |
| 场景种子 `scenario/seed/14_database/mysql8_seed_core.sql:3` | `entity_id, name, short_name, entity_type, role_desc, ownership_parent, ownership_pct, bank_customer_id, status` |

**列名无一对齐**（`group_id`↔`ownership_parent`、`role`↔`role_desc`、`ownership`↔`ownership_pct`、
`relationship_status`↔`status`）。同类问题也出现在 `credit_facility`
（`borrower_entity`/`credit_total_cny` vs `borrower_entity_id`/`approved_amount_cny`、多出 `facility_type`）
与 `commitment`（Java record 的 `operatingCaseId`/`journeyId`/`commitmentType` vs 场景的 `side`/`owner_id`/`source_ref`）。

且 `scenario/seed/14_database/DATA_MODEL_NOTES.md` 第 1 条自述：
> 「**Canonical data is file-first**：V1.1 包中的 JSON/JSONL/CSV 是场景 SSOT；MySQL 脚本只作为开发适配。」

⇒ 迁移脚本的 `legal_entity` **不是**事实权威源，真正的 file-first SSOT 在
`scenario/seed/02_master_data/` 等目录（**未逐一核实**）。

### 处置（**降级，不硬做**）

**WP3.2 不在本 ITER 实施**。理由：

1. 若选 `V003` 迁移 schema 投影 ⇒ 该表**无种子数据**（全仓仅 mapper 里有 INSERT，非夹具）；
2. 若选 `scenario/seed` schema 投影 ⇒ 与本体对齐的 `gits:LegalEntity` 字段（`group_id`/`role`/
   `ownership`/`relationship_status`）**不存在**，投影将**发明字段** —— 违反本 Loop 红线；
3. 选哪套 = **数据模型权威归属裁定**，属停止条件 #2，**不得由 TL 单方选定**。

### 需裁定（并入同一份 Owner 待签清单）

> **问题**：本体 `gits:LegalEntity` / `gits:CreditFacility` / `gits:Commitment` 的字段口径，
> 应以**迁移脚本（运营库）**还是**file-first SSOT（场景包）**为准？
> 若两者都要保留，则需要一份**受控映射**（否则即为"两份可独立修改的定义"，违反约束①）。

### 影响

- **不阻塞** W5（W5 只读本体/地图/投影，不依赖事实对象）；
- **可能影响** W6/V1（`PRE_VISIT_PREPARATION` 需装配客户事实）⇒ 在 W6 前解决，或 V1 链路
  只走「本体 + 地图 + 产品知识」，把客户事实装配标为已知缺口。

### 非声明

- 本 ITER **不主张**"产品关系已进图"—— 实际为 **0 条关系**，原因是数据缺陷，非投影器缺陷（已用非空转证明区分）；
- 本 ITER **未**改动 `specs/semantic/`（本体仍只承载关系**类型**，符合 WP1.3 裁定）。
