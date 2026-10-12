# ONTO1 WI-A2｜消费者全量扫描报告（S1~S5）

| 项 | 值 |
|---|---|
| 依据 | 复审包 `09-消费者影响清单-状态修正版.md` §2（S1~S5）；落地计划 §2 WI-A2 |
| 性质 | **Wave 2/3 实施前退出门禁**的产出（未完成前 Wave 2 禁止开工） |
| 复现 | `python3 scripts/onto1_consumer_scan.py --gate --scan`（首次含扫描 ≈48s）；变异复验 `python3 scripts/onto1_consumer_scan_tests.py` |
| 机读产出 | `consumer-scan-hits.jsonl`（26690 行）、`consumer-scan-summary.csv`、`consumer-scan-obligations.csv`、`consumer-scan-dispositions.json`、`consumer-scan-manifest.json` |
| 门禁 | `wi_a2_consumer_scan` PASS、`wi_a2_scan_mutation` PASS（19/19） |

> 本轮末追加：为解除"书面复审无载体"的卡点，已增补 `13-送审函-书面复审.md` 与 `14-书面复审决议签署页.md`，并把 01~12 哈希冻结为门禁（`wi_review_package_integrity`）。

---

## 1. S1 扫描口径与规模

| 项 | 值 |
|---|---|
| 扫描根 | `gits-cbanking`（HEAD `71169042`）、`Leibniz-KERT`（HEAD `922a674d`） |
| 扫描文件 | **4818**（排除 `.git`/`node_modules`/`target`/`__pycache__`/二进制/大文件） |
| 被检索的 token | 基线 **32 类名 + 34 对象属性名 + 1 数据属性名**（由本体解析动态取得，非硬编码）＋ IRI 字面量（命名空间、`gits:` 前缀、`gits-core` 文件名）＋ ID 模式 **KM- / AC- / ASSET- / SP- / KI- / KD- / CTR-** ＋ D3-A 残留表述 |
| 命中总数 | **26690** |

## 2. S2 命中/处置表（100% 处置，无 `PENDING_TRIAGE`）

| 处置 | 命中数 | 含义 |
|---|---|---|
| `EXEMPT_SEED_DATA` | 5861 | 造数/seed，非本体消费面 |
| `FOLLOW_MIGRATION` | 5118 | **确认或候选的消费面**（含 1038 个文件级义务行） |
| `EXEMPT_FROZEN_EVIDENCE` | 3538 | 历史证据/日志，取证冻结（不可改写） |
| `DOC_TEXT_REFERENCE` | 3154 | 文档正文引用 |
| `HOMONYM_REQUIRES_SOURCE_CHECK` | 2690 | **同名候选**：词法命中 ≠ 本体消费 |
| `EXEMPT_FROZEN_CONTRACT` | 1157 | 封版受控制品（`docs/dd`） |
| `EXEMPT_FROZEN_REVIEW` | 700 | 评审记录 |
| `GENERATED_MIRROR` | 580 | `generated/` 制品（随 `make generate`） |
| `AUTHORITY_SOURCE` | 397 | 基线本体自身（迁移源，非消费者） |
| `EXEMPT_QUARANTINED_ASSET` | 8 | 隔离资产（Oracle 适配器，须 ADR+授权） |
| `EXEMPT_RUNTIME_WORKSPACE` | 17 | 运行时工作区副本 |
| `TOOLING_CONFIG` | 119 | 工具/CI 配置 |
| **`CONTROL_PLANE_REQUIRED`** | **93** | **必须转控制面/修缺陷**（= 14 个文件级义务行） |
| `SCAN_INSTRUMENT` | 17 | 扫描器/本 Loop 的自引用 |
| `EXEMPT_NON_ONTOLOGY_HOMONYM` | 1 | 经回源证明的同名不同物（`AC-004` = 账号号段） |
| `PENDING_TRIAGE` | **0** | 处置表已完成（非零即门禁 FAIL） |

> 处置规则表（58 条，按"先具体后通用"排序，末位兜底 `PENDING_TRIAGE`）：`consumer-scan-dispositions.json`。

## 3. S3 净迁移义务（file 级 1052 行）

| 类别 | 文件级行数 | 典型落点 |
|---|---|---|
| `FOLLOW_MIGRATION` | **1038** | `apps/api` 229、`specs/knowledge-architecture` 153、`specs/gk-ke` 114、`modules/operational-ontology` 80、`kert/src/kert` 38、`kert/examples/bank-front-skills` 37、`scenario/execute` 36 … |
| `CONTROL_PLANE_REQUIRED` | **14** | 见下表 |

**`CONTROL_PLANE_REQUIRED` 全部 14 项（可直接执行的清单）**：

| # | 位置 | 问题 | 动作 |
|---|---|---|---|
| 1~2 | `specs/knowledge-architecture/instances/product/products.ttl` | `gits:` 前缀 = `https://gits.bank.example/ontology/core#`，与本体前缀不一致 ⇒ T-Box/A-Box IRI 不连通（vacuous 检验空转） | Wave 3 修前缀（会变更文件哈希，须重算冻结点） |
| 3 | `kert/src/kert/application/skills.py` | 7 处硬编码地图 ID（`KM-CORP-RM-*`，`:1005/1039/1073/1112/1144/1153`） | 转控制面读取 |
| 4 | `kert/src/kert/application/product_recommendation/sp15_skill.py` | `SKILL_ID="SP-15"`、`ACTIVATION_CONTRACT="AC-PRODUCT-RECOMMEND-001"`（`:60/:63`） | 转控制面登记 |
| 5 | `kert/src/kert/application/service_proposal.py` | `PROPOSAL_SKILL_ID="SP-20"`（`:30`） | 转控制面登记 |
| 6 | `kert/src/kert/application/customer_knowledge.py` | `KI-009` + `KI-FRONT-001~006` 硬编码（`:21-27`） | 转控制面 |
| 7~10 | `kert/src/kert/domain/{knowledge_map.py:30, knowledge_source.py:64, ontology_assets.py:1, ontology_reference.py:1,:56}` | 「依据 D3-A」残余表述（**实测 5 处，复审包 09 号称 3 处**） | 改写为现行决策 |

**重钉清单（S3 第二项）**：`kert/.../90_control/schema/ontology_reference.json`（`CTR-SEM-002` @ `sha256:705578d6…`）、`.../90_control/ontology/PROVENANCE.json`（同哈希）、`specs/CONTRACT_INDEX.yaml`（`:35/:51` CTR-SEM-001/002）、`apps/api/.../KnowledgeArchitectureConfig.java`（`:171-175` 本体端口绑定 + `:167` planHash 派生链）。

## 4. 精度限制与回源抽样（诚实性一节）

**这是本报告最重要的一节。**

词法扫描的必然结果：**token 命中 ≠ 本体消费**。基线类名多为通用英文词（`Skill` 1398、`Claim` 872、`Customer` 680、`Task` 385…），属性的 `customerId` 命中 3444 次，绝大多数落在数据库列/DTO 字段上。因此：

- `FOLLOW_MIGRATION`（1038 文件行）是**候选**义务，**不得**照单执行；
- 按类别分别采取：`specs/`、`modules/`、`adapters/semantic-jena`、`adapters/knowledge-filesystem`、`apps/*`、`kert/src`、`kert/examples`、`kert/skills` 判为跟随迁移面；`adapters/persistence-relational`、`frontend`、`tests`、`kert/scripts` 判为**同名候选待回源**（`HOMONYM_REQUIRES_SOURCE_CHECK` 共 2690）。

**已完成的回源抽样（3 项，均证伪"是本体消费"）**：

| # | 抽样 | 回源证据（`文件:行`） | 判定 |
|---|---|---|---|
| 1 | `adapters/persistence-relational` 的 160 处 `customerId` | `adapters/persistence-relational/src/main/resources/mapper/foundation/ontology/OpportunityMapper.xml:62`（`FROM opportunity WHERE customer_id = #{customerId}`） | MyBatis 参数 ↔ 库列，**非** OWL 属性消费 ⇒ 同名 |
| 2 | `frontend/src` 的 `Customer` 类型 | `frontend/src/api/__tests__/engagement.spec.ts:13`（`import type { Customer } from '../../api/engagement'`） | 类型来自 API 合同（OpenAPI DTO）⇒ 同名 |
| 3 | 裸 `AC-` 号段 | `scenario/seed/03_bank_data/transactions_20260101_20260708.csv:3`（`AC-004` 为账号） | 与 `AC-<语义名>` 形态可区分 ⇒ 号段碰撞 |

**抽样覆盖率诚实声明**：2690 处同名候选中本轮仅抽样 3 类（≈160+处、>10% 量级），**其余须在 Wave 2 逐条回源确认**；未确认项不得计入迁移义务，也不得计入"已排除"。

## 5. S4 变异复验（证明门禁非空转）

`python3 scripts/onto1_consumer_scan_tests.py` → **19/19 PASS**，其中关键 5 条：

| 用例 | 注入 | 期望 | 结果 |
|---|---|---|---|
| T06 | 规则表无任何匹配 | 门禁 FAIL（fail-closed） | PASS（exit=2） |
| T09 | 只用 gits 单仓命中缓存 | 期望命中缺失 ⇒ A3 FAIL | PASS（exit=2） |
| T10 | 全部命中豁免化 | 净义务锚点缺失 ⇒ A6 FAIL | PASS（exit=2） |
| T11 | 全部落 `PENDING_TRIAGE` | A4b FAIL | PASS（exit=2） |
| T12 | 对照（正式规则 + 正式缓存） | PASS | PASS（exit=0） |

**并行的真实收获**：T09 迫使我去核对期望值，从而发现 **ID 模式表缺 `CTR-` 前缀**——`CTR-SEM-002` 这类**合同 ID（Wave 2 拆条登记的对象）从未被扫描到**。已补模式并重扫（命中 23609 → **26690**）。记录见 `FAILURES.md` FAIL-2026-09-20-01。

## 6. S5 门禁接线（Wave 2/3 退出门禁）

Wave 2（拆分）与 Wave 3（切换）**开工条件**：

1. `python3 scripts/onto1_consumer_scan.py --gate` 绿（当前绿）；
2. `python3 scripts/onto1_consumer_scan_tests.py` 绿（当前绿）；
3. `consumer-scan-obligations.csv` 中 `FOLLOW_MIGRATION` 项**逐条回源确认**完毕（**当前未完成**——这是 Wave 2 的真实剩余工作）；
4. `CONTROL_PLANE_REQUIRED` 14 项全部关闭或具名豁免（带解除条件）；
5. 独立 QA 复核扫描清单与变异记录。

> 注意：第 3 项意味着**"扫描完成"不等于"退出门禁通过"**。本报告只交付 S1~S5 的**机制与清单**，退出门禁的通过需在 Wave 2 前由回源确认完成。

## 7. 与复审包 09 号初版清单的对账

| 09 号列举 | 本轮实测 | 判定 |
|---|---|---|
| KERT 硬编码地图 ID 7 个字面量（`skills.py:1005-1170`） | 7 处确认（`KM-CORP-RM-OUTREACH/MEETING/PREVISIT/SUPPLYCHAIN/PROPOSAL/MEMORY`） | ✅ 确认 |
| `SP-15` / `AC-PRODUCT-RECOMMEND-001`（`sp15_skill.py:60-63`） | 确认（`:60`/`:63`） | ✅ 确认 |
| `service_proposal.py:30` 为 `ACTIVATION_CONTRACT` | 实测该行是 `PROPOSAL_SKILL_ID = "SP-20"`，**该文件无 `AC-` 引用** | ⚠️ **修正** |
| KI 清单 `customer_knowledge.py:21-27` | 确认（`:21`~`:25`+） | ✅ 确认 |
| `products.ttl:1` 前缀错配 | 确认（`https://gits.bank.example/ontology/core#`） | ✅ 确认 |
| 「依据 D3-A」**3 处** | 实测 **4 文件 5 处**（多出 `ontology_assets.py:1`、`ontology_reference.py:56`） | ⚠️ **修正（低估）** |
| `CONTRACT_INDEX:646-650` | 实测 `CTR-SEM-001` 在 `:35`、`CTR-SEM-002` 在 `:51` | ⚠️ **修正（行号）** |
| 其他资产引用（`ASSET-*`/`SQ-*`/`HG-*` 等在 KERT 无定义文件） | 扫描已覆盖 `ASSET-`（200+64）等模式，落点为 `specs/knowledge-architecture` 与 `kert/examples`；须在 Wave 2 与「无定义文件」断言逐条对账 | ⏳ 待确认 |
| 命名三套并存（`bank-front-*` / `skill-customer-*` / `SP-*`） | 扫描可见；**统一命名不在本 Loop scope**（后续立项） | 登记 |

## 8. 非声明（不得援引为已完成的事）

1. 本报告**不声称**消费者影响分析已关闭——它给出的是**机制 + 100% 处置的规则表 + 候选义务清单**；
2. 不声称任何门禁为 `QA_PASS`（开发角色禁自签）；
3. 不声称 KERT 侧结构已被索引确认（`INDEX_STALE(144)`，所有 KERT 结论均回源到 `文件:行`）；
4. 不声称 `FOLLOW_MIGRATION` 1038 行都是真义务（词法级；抽样 3 类已证伪同名）；
5. 未执行 `make generate`、未改 `generated/`、未改 `specs/`、未改产品卡与本体。
