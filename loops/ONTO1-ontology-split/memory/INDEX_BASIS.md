# ONTO1-ontology-split｜索引依据（代码事实索引与检索底座）

> 流程依据：`docs/governance/CODE-FACT-INDEX-PROCESS.md`（GOV-CFI-001）
> 约束：索引是 **DERIVED 派生视图**，只给线索；下表"回源结论"必须带 `文件:行` 才可被引用。

| 项 | 值 |
|---|---|
| **索引版本** | `.ua/merge-meta.json` @ `2026-09-15T17:50:17Z` → gits `7116904` / kert `64f6f87`（合并 5106 节点 / 4235 边 / 54 层 / 26 导览） |
| **新鲜度声明**（2026-09-21 收口实测） | **gits `STALE(6)`**：`make index-status` ⇒ `WARN`，`drift={'merge-meta.json': 6, 'meta.json': 6}`（阈值内，**非** FRESH）；**KERT `INDEX_STALE(144)`**（索引 @64f6f87 → HEAD 922a674d，漂移 144 提交 > 50 阈值）⇒ KERT 侧结论**必须回源直读**，不得由索引外推 |
| **门禁** | `make index-status` → **WARN**（`ua_index_gate: WARN (nodes=5106, drift={'merge-meta.json': 6, 'meta.json': 6})`，2026-09-21 收口实测）；上一条 PASS 记录（`evidence/index_status-20260920T132340Z.log`）**已过期**，引用时须注明日期 |
| **声明** | 本会话**未**声称掌握全局设计：KERT 侧结论全部来自**直接读取 + 全文扫描**（带 `文件:行`），未使用索引做结构外推。索引刷新登记为下一 holder 动作。 |

## 候选影响面（来自索引 L0/L1/L2，**未回源前不得作为事实**）

> 本会话主要用全文扫描而非索引定位——原因见下方"盲区"：本次问题的对象是**跨仓词法引用**与**术语同名**，索引无跨仓边、无词法命中表，故索引只能给出模块级候选面。

| # | 候选对象（模块 / 文件 / 类） | 索引来源 | 回源结论（`文件:行`） | 判定 |
|---|---|---|---|---|
| 1 | GITS 本体消费链 | `layer:` semantic/tooling | `apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java:171-175`（`ontologyPort` 绑 `specs/semantic/gits-core.owl.ttl`）；`:167` 注释声明 versions.ontology 由本体 SHA-256 派生 | 受影响 |
| 2 | KERT 钉值方 | `layer:` kert/domain | `examples/bank-front-knowledge-maps/90_control/schema/ontology_reference.json`（CTR-SEM-002 @sha256:705578d6…）；`.../90_control/ontology/PROVENANCE.json`（同哈希，pinnedAt 2026-09-16） | 受影响 |
| 3 | 合同登记 | specs | `specs/CONTRACT_INDEX.yaml:35`（CTR-SEM-001）、`:51`（CTR-SEM-002） | 受影响（Wave 2 拆条） |
| 4 | A-Box 前缀错配 | specs | `specs/knowledge-architecture/instances/product/products.ttl:1` = `https://gits.bank.example/ontology/core#`；本体前缀 = `https://gientech.com/gits/kno/`（`specs/data/customer-source-mapping.r2rml.ttl:2/:14`） | 受影响（真实缺陷） |

## 索引未覆盖、必须回源的盲区（本轮实际踩到的）

| # | 问题 | 索引为何答不了 | 回源位置（`文件:行`） |
|---|---|---|---|
| 1 | 哪些文件**词法引用**了 32 类名 / 34 属性名 / `gits:` 前缀 / ID 模式？ | 索引是符号与结构图，**无词法命中表**、无跨仓边 | 自建扫描器：`scripts/onto1_consumer_scan.py`（4818 文件 / 26690 命中，机读清单 `evidence/consumer-scan-hits.jsonl`） |
| 2 | 同名 token 究竟是不是本体消费？ | 索引无法区分"同名不同物" | 抽样回源：`adapters/persistence-relational/src/main/resources/mapper/foundation/ontology/OpportunityMapper.xml:62`（`customer_id = #{customerId}` ⇒ 库列，非本体属性）；`frontend/src/api/__tests__/engagement.spec.ts:13`（`import type { Customer } from '../../api/engagement'` ⇒ OpenAPI DTO） |
| 3 | `CTR-` 合同 ID 的引用面 | 索引未建 ID 模式检索 | 本轮新增扫描模式后检出（修复记录 `FAILURES.md` FAIL-2026-09-20-01 第 3 点） |

## 本批次新增的可复用结论（供下一 holder 免于重复通读源码）

| # | 结论 | 出处（`文件:行`） | 落地位置 |
|---|---|---|---|
| 1 | 基线本体哈希与计数可复现：`sha256 705578d6324abd0c…`、32 类 / 34 对象属性 / 1 数据属性 | `specs/semantic/gits-core.owl.ttl`（rdflib 复现，`evidence/baseline-v2-manifest.json`） | `LOOP.yaml` gate `wi_a1_baseline` |
| 2 | D3-A 残留实测为 **4 文件 5 处**，非复审包 09 号所述 3 处 | `src/kert/domain/knowledge_map.py:30`、`knowledge_source.py:64`、`ontology_assets.py:1`、`ontology_reference.py:1` 与 `:56` | `evidence/consumer-scan-dispositions.json`（`R-OBL-KERT-D3A`） |
| 3 | 复审包 09 号「`service_proposal.py:30` 为 ACTIVATION_CONTRACT」不准确：实测该行是 `PROPOSAL_SKILL_ID = "SP-20"` | `src/kert/application/service_proposal.py:30` | 同上（`R-OBL-KERT-SP20`） |
| 4 | `AC-` 前缀与银行账号号段**碰撞**（`AC-004` 为账号），裸 `AC-` 计数会严重虚高 | `scenario/seed/03_bank_data/transactions_20260101_20260708.csv:3` | 处置规则 `R-HOMONYM-AC-NUMERIC` |
| 5 | KERT 硬编码地图 ID 实测 7 处（`KM-CORP-RM-*`），与复审包 09 号一致 | `src/kert/application/skills.py:1005/1039/1073/1112/1144/1153` | 处置规则 `R-OBL-KERT-MAPID-HARDCODE` |
| 6 | 两仓仓根存在未跟踪运行时日志 `lightrag.log`（含合同 ID 引用），不构成本体迁移义务 | `lightrag.log`（两仓） | 处置规则 `R-RUNTIME-LOG` |
| 7 | 净迁移义务（file 级）共 **1052 行**：`CONTROL_PLANE_REQUIRED` 14 + `FOLLOW_MIGRATION` 1038 | `evidence/consumer-scan-obligations.csv` | WI-A2 报告 §3 |

## 本批次（2026-09-20T14:15Z，包 `W-1/review-submission`：送审程序与结论回收链路）

**索引用途**：本批次对象是**文书与程序**（复审包、送审函、签署页、状态机与门禁脚本），索引（节点/边）**给不出候选面**，故直接回源；`make index-status` 复跑 PASS（`nodes=5106, drift 0`）仅用于声明新鲜度。

| # | 回源位置（`文件:行`） | 结论（事实） |
|---|---|---|
| 1 | `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md:17-30` | 包内登记 **14 件**（01~14）+ 全量 SHA-256；01~12 与 V1.0 冻结值逐字一致 |
| 2 | `docs/review/ARCH-ONTO-2026-001-rereview-package/13-送审函-书面复审.md:44` | 反馈期限建议 **10 个工作日（至 2026-10-09）**，由秘书处汇总 |
| 3 | `.../14-书面复审决议签署页.md:11-13`、`:21-24`、`:30-35`、`:39-47`、`:51-56`、`:60-72` | 6 项决议；决议 1 三个可选项；决议 4/5/6 各有「有条件 / 要求修改 / 要求补充」分支 |
| 4 | `.../14-…签署页.md:92-98` | 签署表 5 位：主席 + 3 委员（语义/集成/数据）+ 秘书处汇总人 |
| 5 | `.../14-…签署页.md:78-80` | 知悉确认三项（条件 8 `IN_PROGRESS`；无实现/QA/激活声称；计数为 `SYSTEM_OBSERVATION`） |
| 6 | `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md:19-28` | 状态机与允许/禁止；「标 `DESIGN_APPROVED`/`FROZEN`」在复审前**明令禁止** |
| 7 | 同上 `:56` | `G-1` 条件①原文：书面复审结论 = `DESIGN_APPROVED` **或** `PASS_WITH_REQUIRED_CHANGES` **且条件已登记** |
| 8 | `docs/review/ARCH-ONTO-2026-001_整改复审意见_V1.0.md:112-132` | §5 十二项最小要求 + 两条路线（严格关闭 / 缩小批准范围，后者上限 `PASS_WITH_REQUIRED_CHANGES`） |
| 9 | 同上 `:134-157` | §6 书面复审四项重点；§7 允许/禁止清单（返工期间不得标 FROZEN / 不得启动拆分与重钉） |
| 10 | `scripts/onto1_review_package_check.py:26-41` | R1 **硬编码** 12 份冻结哈希；R2 要求 13/14 齐备；R3 校验 MANIFEST 登记自洽 |
| 11 | `scripts/loop_guard.py:100-123` | `NEXT_SESSION.holder` 必须等于 `ROLE_BOARD.baton.holder`；非 review 状态下 `STATE.implementation_actor` 必须等于 holder |
| 12 | `scripts/loop_guard.py:88-97` | Loop 目录内**禁止**残留三类字面量：双左花括号、`TEMPLATE` 加连字符前缀、英文「替换说明」占位句（三者任一即 FAIL ⇒ 新增文书须避开，**含本行自身的书写陷阱**） |
| 13 | `scripts/loop_guard.py:136-145` | `EVIDENCE.json` 的 gate 集合必须与 `LOOP.yaml.gates` **精确相等** ⇒ 新增文书**不得**顺手加 gate |
| 14 | `scripts/record_gate.py:59-63` | 每 gate 预算 5 次（记于 `memory/waves/W0-ITER.md`）；本批两 gate 用至 Attempt 2 |

**索引未覆盖（本轮踩到）**：`.ua/knowledge-graph.json` 不含 `docs/review/**` 的**内容级**信息（无条目级解析、无哈希），也无「包内件是否齐备」这类**集合完整性**判定 ⇒ 该问题只能由专用门禁（`onto1_review_package_check.py`）回答，本批次已回源并复算。

## 本批次（2026-09-20T15:05Z，包 `W1-prep/P-1-public-semantic-owner`：候任公共语义 Owner 能力准备）

**索引用途**：本批次对象是**文书（草稿）与基线语义回源**。索引（节点/边）**不含跨仓边、不含词法命中表**，对「某术语在哪被引用」「某属性 domain/range 实测值」既给不出也读不全 ⇒ 候选面靠索引无效，**全部回源本体/矩阵**。

| # | 回源位置（`文件:行`） | 结论（事实） |
|---|---|---|
| 1 | `specs/semantic/gits-core.owl.ttl:22-24`、`:27-30` | `gits:Customer` 为域引用类（映射 EDWCRM `A_ZHCX_CUST_BASE`，ADR-0010）；`gits:customerId` 为 DatatypeProperty（domain `Customer`，range `xsd:string`）—— 即矩阵登记的退役对象 |
| 2 | `specs/semantic/gits-core.owl.ttl:115-129` | `CorporateGroup:115-117`、`LegalEntity:119-121`、`GroupRelationship:123-125`（含 `relationshipType`/`ownershipRatio`）、`Product:127-129`（注释仍写「权威物理源为 KERT 产品卡」= 与设计 B-02 纠正口径不一致，注释未改写） |
| 3 | `specs/semantic/gits-core.owl.ttl:151-173` | `memberOfGroup` 实测 domain **`LegalEntity`** → range `CorporateGroup`；`relatesToGroup` domain `GroupRelationship`；`connectsFrom`/`connectsTo` 实测 range **`LegalEntity`** ⇒ 矩阵目标把它们放宽为 `Party`，属**扩大值域**，级别判定与复审包 07 号矩阵「放宽=minor」存在口径张力（待裁 O-3/O-5） |
| 4 | `specs/semantic/gits-core.linkml.yaml:25-36` | `Customer` 8 属性：`customer_id`(identifier)/`cust_name`/`cust_code`/`cert_no`/`cust_type`/`cust_status`/`region`/`brid` |
| 5 | `rg -n "playedBy"`（全仓） | 仅命中 `docs/review/…/03-逐术语权威矩阵-22字段.csv:5` 与 `evidence/attribution-45-v2.csv:5` 两处**文书括注**，**无本体/代码实据** ⇒ 若登记为命名对象属性则为第 **37** 条，与既有 36 条口径不自洽（待裁 O-2） |
| 6 | `grep -c "改指" evidence/attribution-45-v2.csv` → `5` | `range 改指 CustomerRole` 实测 **5 条**（`gateOfCustomer`/`ofCustomer`/`opportunityOfCustomer`/`profileOfCustomer`/`refersToCustomer`），另 1 条 `opportunityForProduct`→`ProductOffering`；**设计 §4.1 写「4 条」⇒ 设计文字与机读矩阵不一致**（待裁 O-4） |
| 7 | `grep -c "L1 公共业务语义核心" evidence/attribution-45-v2.csv` → `12` | L1 资产实测 **12 项 = 8 类 + 4 属性**，与设计 §4.2（8 类）+ 复审包 04-C（4 属性）分口径自洽 |
| 8 | `awk -F, '{print $NF}' evidence/attribution-45-v2.csv \| sort \| uniq -c` | 归属列分布：`基线映射 54` + `新增 33` = 87 行 = 45 模型资产 + 41 属性行 + 1 退役项，与 45/36/5/1 分口径自洽 |

**索引未覆盖（本批次踩到）**：① 术语的 **domain/range 实测值**须逐条读本体（索引无属性级约束信息）；② **同名 token 是否为本体消费**须回源分辨（索引不分同形异物）；③ **文书间口径一致性**（设计「4 条」vs 矩阵「5 条」）索引完全无法回答 —— 只能靠机读矩阵复算。

## 本批次（2026-09-20T14:21Z，包 `W-1/D2-pack`：D2 悬空产品引用的归一化决策包）

**索引用途**：本批次对象是**另一仓（KERT）产品卡正文与产品身份空间**，以及**跨仓词表碰撞**。
索引**无跨仓边、无语料级文本、无词表命中表** ⇒ 候选面靠索引无效，**全部回源**（卡片逐行读取 + 全文扫描 + 文件名定位）。
`make index-status` 复跑 PASS（`nodes=5106, drift 0`）**仅**用于声明新鲜度；KERT 侧 `INDEX_STALE(144)` ⇒ **未**据索引对 KERT 结构做任何新判断。

| # | 回源位置（`文件:行`） | 结论（事实） |
|---|---|---|
| 1 | `KERT:examples/product-recommendation-assets/03_core/*/version=*/product-cards/PROD-*.md:19,20,26,27,28,30`（13 张同构） | 三张关系字段与准入字段的**行号在 13 张卡中同构**（19/20/26/27/28/30）⇒ 后续按行号核对可复用，不必逐卡重读 |
| 2 | `KERT:…/PROD-CM-001.md:64-65`、`PROD-CM-003.md:65`、`PROD-CB-001.md:66`、`PROD-CB-002.md:65`、`PROD-FIN-001.md:77`、`PROD-FIN-002.md:72,75`、`PROD-FIN-003.md:75`、`PROD-IB-001.md:66`、`PROD-SET-001.md:65`、`PROD-SET-002.md:66`、`PROD-TF-001.md:66`、`PROD-TF-002.md:65` | 卡片**正文 §6** 给出每个悬空 token 的**中文语义名**（前置/配套/互斥/替代产品）——这是候选映射的决定性证据，**此前各裁定件（GK17 两组、D2 请求函）均未引用正文** |
| 3 | `KERT:src/kert/application/product_recommendation/eligibility.py:547,552`、`KERT:scripts/product_recommendation_golden_benchmark.py:8`、`KERT:tests/integration/test_sp15_contract_conformance.py:155` | `SETTLEMENT_ACCOUNT` 在**账户关系位**有**可执行消费者**：与客户 `accountRelationships` 事实比对；夹具由 `customer.hasAccount` 生成 ⇒ 该 token 至少跨三槽位（产品位 / 账户关系位 / 能力特性位） |
| 4 | `GITS:adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:42,44,51,108` | GITS PI-0 种子另有**产品行**「对公结算账户」(:42)、「企业网上银行」(:51)、「外汇避险（远期结售汇）」(:108)；`SETTLEMENT_ACCOUNT` 还是**关键特性**取值 (:44) ⇒ 与 KERT `PROD-*` 身份空间**不重叠**，构成跨仓身份问题（不是缺失） |
| 5 | `GITS:specs/product-knowledge/product-taxonomy.yaml:68-69,167-168,197-200,203-204,215-218,221-222,229-232,239-240,265-268` | GITS 分类基线中与悬空取值**同物不同形**的族 / 品类：现金管理（族）、资金池、电子渠道（`has_products:false`）、承兑工具、票据贴现（`false`）、跨境结算、外汇服务（`false`）、流动资金、财务顾问（`false`）⇒ 交叉验证必须看品类层，只看产品层会漏 |
| 6 | `KERT:…/PROD-FIN-001.md:75`、`FIN-002.md:73`、`FIN-003.md:73`、`SET-001.md:64` 与 13 张卡 `:20` | `mutex_product_ids` **13/13 空**而正文仅 **4 处**叙述性互斥（含一处"无"）⇒ **零实例成立**；叙述**不得**充当实例 |
| 7 | `GITS:docs/architecture/GK17-产品卡引用空间裁定-V1.0.md:64-68,76,82-83`、`GK17-四项悬置口径裁定-V1.0.md:87-98` | 既有两组裁定的候选清单（5 条名称对应 + 族 + 工具/账户 + 未覆盖）与本批次**逐条对齐**；本批次**新增**的是"正文语义名 + 跨仓词表碰撞 + 证据强度 + 逐条机器校验"四件，**未**推翻既有候选 |

**索引未覆盖（本批次踩到）**：① **卡片正文**（§1~§11）的语义信息索引完全没有 ⇒ 候选映射必须读正文；
② **跨仓同名不同物**（`SETTLEMENT_ACCOUNT` / `CORPORATE_E_BANK` 在 GITS 侧另有身份）索引无跨仓边 ⇒ 只能回源种子与分类基线；
③ **产品族 / 品类层**与产品层的碰撞（`CASH_MANAGEMENT`）属**词表级**问题，索引答不了。

## 本批次（2026-09-20T15:20Z，包 `W-1/D4-pack`：D4 A-Box 权威确认决策包）

**索引用途**：本批次对象是**权威归属与来源系统**——属于「某能力/事实的权威在哪」类问题，索引 L0/L1 能给出**模块级候选面**（`specs/data`、`specs/semantic`、`docs/review`），但**给不出**「哪个系统是权威」「两套外部标识模型是否对齐」这类判定 ⇒ 候选面靠索引，**结论一律回源**。

| # | 回源位置（`文件:行`） | 结论（事实） |
|---|---|---|
| 1 | `specs/data/src-edwcrm-cust-base.v0.1.json:2-14` | 客户主数据源**已具名**：`system=EDWCRM`、`A_ZHCX_CUST_BASE`、`CUSTID`（`primary_key`）、`authority=AUTHORITATIVE`、`classification=SENSITIVE` ⇒ `CustomerRole` 候选 CR-1 为强证据 |
| 2 | `specs/data/customer-source-mapping.r2rml.ttl:4-15`；`specs/semantic/gits-core.owl.ttl:22-24` | 同一权威源在**R2RML 映射（CTR-MAP-001）**与**本体注释（ADR-0010）**两处一致 ⇒ 「值权威（源系统）/ 规则权威（映射合同）/ 存放（投影侧）」三列可分离 |
| 3 | `specs/data/source-contract.schema.json:7-26`；`specs/data/src-edwcrm-cust-base.v0.1.json:9-21` | 既有源合同已有 `system`/`owner`/`classification`/`effectiveFrom`/`objects[].{schema,name,authority,fields[].{name,role,mapsToSubject}}` ⇒ `SourceIdentifier` 六必填字段**可逐一对齐既有词汇，无需新造** |
| 4 | `specs/gk-ke/v1/examples/l1-1/positive/SemanticPackage.json:177-194` | GK-KE L1-1 **已登记** `core.ExternalIdentifier`（`scheme`/`value`/`issuedBy`，`identityRule=scheme+value`）⇒ 与 ONTO1 `SourceIdentifier` 并存构成两套外部标识模型（登记为 **O-D4-2**，MAJOR） |
| 5 | `docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md:207-211` | 旧送审口径：「`Customer` 实例权威 = EDWCRM」但「`LegalEntity`/`CorporateGroup`/`GroupRelationship` 实例权威 = **GITS 运营库**」「`Product` = **KERT 产品卡**」 ⇒ 正是 B-02 要纠正的三处；须防回退（已在机读清单列为 `EXCLUDED`/`PROHIBITED`） |
| 6 | `docs/dd/mybatis-integration-spec.md:68` | `Customer`/`LegalEntity`/`GroupRelationship` 均属 `modules/operational-ontology`（运营库表）⇒ 运营库**存在**这些表，但只能作投影载体，不得作正式权威 |
| 7 | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:10-14`、`:22`、`:41`、`:49-51` | 封版 C01 已给出同向口径（模拟源平台保管客户/产品主档；分析语义服务「不另存客户权威事实」；时间间隔左闭右开、业务日 Asia/Shanghai、记录时点 UTC；INV-01 每可变权威字段有唯一 ownerSystem） ⇒ 投影合同的时点与漂移条款有既有依据 |
| 8 | `specs/knowledge-architecture/instances/product/products.ttl:1`、`:9-12` | 该 A-Box 前缀为**占位根域** `https://gits.bank.example/ontology/core#`（本仓 `specs/` 下**唯一**命中），且自述「W3.1 投影产物」、含 13 个产品身份个体 ⇒ 若指定为 SIM 载体须先处置（登记为 **O-D4-6**） |
| 9 | `specs/data/oracle-to-gits-mapping.md:131-134` | 当前喂给系统的「客户主数据」来自 **Hermes 演示数据** ⇒ 这正是需要 SIM 临时权威声明的原因（无处权威 ≠ 无权威） |
| 10 | `docs/review/ARCH-ONTO-2026-001-rereview-package/03-逐术语权威矩阵-22字段.csv:6-7` + `specs/semantic/gits-core.owl.ttl:115-125` | 集团族（`EnterpriseGroup`/`GroupMembership`）仓内**只有角色级描述、零具名源系统、零源合同**；基线 `GroupRelationship` 的 `fromEntityId`/`toEntityId`/`ownershipRatio` 未绑定外部源 ⇒ **O-D4-7** |

**索引未覆盖（本批次踩到）**：① 「谁是权威」是**治理判定**，索引无权威字段；② 源合同的**字段级语义**（`role=primary_key`/`mapsToSubject`）索引未解析；③ 两套同名概念（`SourceIdentifier` vs `core.ExternalIdentifier`）的**跨包一致性**索引无法回答；④ 集团族的**缺失**（零证据）索引无法表达（"索引里没有" ≠ "不存在"，须回源确认）。

## P-3（D3 决策包）批次新增的可复用结论（供下一 holder 免于重复通读）

| # | 结论 | 出处（`文件:行`） | 落地位置 |
|---|---|---|---|
| 8 | 旧命名空间由脚本**从本体读取**（未硬编码）：`https://gientech.com/gits/kno/`；旧端术语 **67** = 32 类 + 34 对象属性 + 1 数据属性 | `specs/semantic/gits-core.owl.ttl:1`；`scripts/onto1_namespace_collision_check.py` `C-1a` | `evidence/iri-mapping-draft.csv`、决策包 §1 F1/F3 |
| 9 | 本体**无 `owl:versionIRI`、无 `owl:imports`** ⇒ 单版本闭包检查（C-3）当前**空转**，不得计为覆盖 | `specs/semantic/gits-core.owl.ttl`（全文件无该两谓词） | 决策包 §7.3-4；变异 `M4` / 元变异 `M-元` |
| 10 | 前缀缺陷实测 **2 处**（不是 1 处）：`C-2a` 前缀双绑定 + `C-2b` 同名不同 IRI（`gits:Product`） | `products.ttl:1`、`:10`、`:15`；`customer-source-mapping.r2rml.ttl:2` | `evidence/namespace-known-defects.json` |
| 11 | **`namespaces.json` 全仓不存在** ⇒ 碰撞检查输入只能取自映射草案；该文件属 D3 决策物，D3 未签期间**不得创建** | 仓根 `find . -name namespaces.json` → 无命中 | 决策包 §10.2-③ |
| 12 | 语义关系分布（机读复算，可复现）：`RETAINED 32`·`AUTHORITY_MOVED 4`·`REMODELED 23`·`TRANSFORMED 7`·`DEPRECATED 1`·新增 20；迁移域 67 | `evidence/iri-mapping-draft-summary.json` | 决策包 §5.1 |
| 13 | `RETAINED_AUTHORITY_MOVED` 实测 4 项：`LegalEntity`、`ProductKnowledgeCard`、`ProductKnowledgeVersion`、`supersedesVersion`（层迁移但短名与域/值域未变） | `evidence/iri-mapping-draft.csv` | 决策包 §5.3 `J-1`（待 TL 裁定） |
| 14 | 碰撞检查**当前 FAIL ⇒ 阻断发布**（C-2 未修）；`C-1b` 为 `NOT_EVALUATED` ⇒ D3 解除证据中的"碰撞检查绿"当前不可得 | `evidence/wi_a4_namespace_collision-20260920T142432Z.log` | 决策包 §7、NEXT_SESSION「三条硬事实」 |

> 本批次**未**使用索引做任何结构外推（gits `INDEX_FRESH` @71169042；KERT `INDEX_STALE(144)` 未刷新，KERT 结论一律回源 `文件:行`）。
> 本批次涉及的问题对象是"命名空间/前缀/IRI 集合"，索引**无前缀绑定表、无 IRI 集合视图**，故 8~14 全部由自建脚本从制品复算，属"索引未覆盖、必须回源"一类。

## 非声明

- 本文件是**派生线索 + 回源结论**的记录，不是权威职责定义；与 `specs/` 冲突时以 `specs/` 为准。
- 本文件不构成 `QA_PASS`，不作为 Gate/ADR 依据。
- KERT 索引漂移 144 提交未刷新 ⇒ **不得**据索引对 KERT 结构做新判断。

---

## W-1.5 收工｜索引声明与新增回源结论（2026-09-21T00:05Z）

**索引新鲜度声明（TL 角色强制）：`gits` = `INDEX_STALE`（本会话新增/改动脚本 8 个以上，索引未刷新）；`KERT` = `INDEX_STALE(144)`（未刷新）。**
**本批次未依赖索引定位**：PKG-A1/A2/A3 的审计范围由派工单 + HANDOFF 直接给定；全部结论由**自建脚本复算**或**逐条回源 `文件:行`**得出。

| # | 回源结论（本会话新增） | 证据位置 |
|---|---|---|
| 15 | **E3 两条路径行为不同**（同冻结 revision `c5f7b671`）：删**声明行** ⇒ `exit=2` + `C-4_REQUIRED_PIN_MISSING`（具名 FAIL）；删**文件** ⇒ `exit=1` + `KeyError: 'refirement_gate_scope'`（**崩溃**）；删**范围外**钉值文件 ⇒ 仍 `[C-4] PASS（allow-list 4/4）` | TL 沙箱 `/tmp/a3root`（`--root` 副本）；`FAILURES.md` `W15A3-02/W15A3-03` |
| 16 | **PKG-A1 交付哈希与声明逐字一致且稳定**（4 秒两次取样不变）：脚本 `1982a9ec2017df97`、CSV `81e5ebc414df576c`、summary `325910baeac0a402`、报告 `89428f094a2af351` | `memory/handoffs/TL-AUDIT-W15-PKG-A1.md` §1 |
| 17 | **PKG-A1 门禁有牙齿**（TL 自建变异）：删 1 行 ⇒ `G2+G7`；证据行号改 999999 ⇒ `G4+G7`；Wave 改 `W9_BOGUS` ⇒ `G6`；还原 ⇒ `exit=0` 且 CSV 哈希**逐字回到** `81e5ebc4` | 同上 §4 |
| 18 | **PKG-A1 计数**：真义务 626 / 同名 0（"无可证明者"）/ 待回源 426 / 合计 1052；`tier` STRONG 626·MEDIUM 329·WEAK 97；Wave W3_CONSUMER_SWITCH 316·W2_SPLIT 291·W3_KERT_ASSETS 19；**P0（解析到本体/领域模型包）= 65** | `evidence/obligation-triage.csv`（TL 复算） |
| 19 | **"派工单弱面前缀在本批 0 行"属实**（严格 `path.startswith`）：`frontend/`·`tests/`·`adapters/persistence-relational/`·`evidence/`·`loops/` 全 0；易误判的是 `specs/.../tests/`、`specs/evidence/`（非顶层前缀） | 同上 |
| 20 | **`loop_guard` 禁止含 `echo ` / `printf ` 的命令**（`FORBIDDEN_COMMAND_PARTS`），故 D-11 的"日志自证 revision"**不能用 shell 拼** ⇒ 落地为 TL 工具自打印 | `scripts/loop_guard.py:33-34`；`FAIL-2026-09-20-W15TL-06` |
| 21 | **`record_gate.py` 以 `shell=True`/`/bin/bash` 在仓根执行门禁命令**，重跑会**留下 attempt 日志**（未登记即成孤儿，证据板 E2 拦下） | `scripts/record_gate.py:69`；`FAIL-2026-09-20-W15TL-07` |
