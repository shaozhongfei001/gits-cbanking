# 独立 QA 报告（波 3 / R-QA）— ONTO1-ontology-split

> 依据：`memory/DISPATCH-WAVE3-PROMPTS.md` §1（R-QA）· 本轮为波 1/2 制品冻结后的**首轮独立复算**。
> 本文所有结论均来自**我本人执行的命令**；**未采信 TL 的任何报告、结论或"已闭环"表述**。

## 0. 开工声明（三行）

```text
actor      = independent_qa（独立复算者；非实现者、非 TL；本会话不签任何 Owner/委员会文书）
写域       = loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3-2026-09-21.md（唯一）
复验对象   = 门禁板面 · A-1 处置台账 · C-2 修复与消费者扫描 · D2 分流与隔离 · A-3 包收口 · A-4 SIM 迁移 · A-5(L2/L3) · A-7 签署页校验器 · 断言强度 · 红线（generated/ 零改动 / 基线 T-Box / KERT 零写入 / 12 条未强映射）
```

- 仓库：`/home/szf/dev/gits-cbanking`，分支 `recover/PI-ARCH-product-catalog`，`HEAD = 9a6dec78046172cd60cb8032f4419905e1958515`
- 只读仓：`/home/szf/dev/Leibniz-KERT`（**零写入**，见 §6.4）

## 1. 复验基线快照（供后续比对）

| 制品 | sha256 |
|---|---|
| `specs/semantic/gits-core.owl.ttl` | `705578d6324abd0c1bd2bd670e6f3c0ffd8e04c358d0134246c89a3acfc38d00` |
| `specs/knowledge-architecture/instances/product/products.ttl` | `e1b6e09e57d5834aa8c9b33ad016d91a5e59295480ade5ba55bba843f107c514` |
| `.../product/sim/product-relations.SIM.ttl` | `6fc33da2151a01a59406507d241727499488ceac2b4d5ff043a5e0b4f95bc253` |
| `.../product/projection-config.json` | `6a4c53aff09842028ce18836f499adcece15a7cd394494464af6f380cdc802bc` |
| `evidence/prep/a2-disposition-ledger.csv` | `136e9de43cbb11fa20857abcf6004b5adb9749a00297e4a15b09a36c7317fd4a` |
| `evidence/prep/a3-freeze.json` | `a8adc05039c101d7115898dc7fc54c5de13d4e91e268f9cf2a714553a3570b9a` |
| `evidence/prep/sim-migration-verify.json` | `460fa0b0d6986c2d9d75bb2034e985e090386ef900cdd8bb364aa705f3759fea` |
| `evidence/c2-consumer-scan.json` | `6144c8bd94a8dbe397bf1c3f20c5d1afe94b60b66929308127f7648bfb405c76` |
| `EVIDENCE.json` | `9bf6a7e5cdfc24f4093921afa796b16429c4b48615d7e690abd8f26d610b5394` |

## 2. 逐项复验结论

| # | 复验项 | 结论 | 摘要 |
|---|---|---|---|
| 1 | 门禁板面 62 = 61 pass / 1 inconclusive | **ACCEPT**（+ 条件 F-1） | 板面事实我复算一致；但**该事实不是派工指定的那条命令验证的**（见 §5 F-11①） |
| 2 | A-1 处置台账（412 行） | **ACCEPT_WITH_CONDITIONS** | 1142 条证据行**全量**回源（非 20% 抽样）：1127 HIT / 13 DRIFT / 2 ABSENT（=已授权重构解消）；53 条 EXEMPT 行按**全部 188 处 hits**独立复判，0 违例。条件：F-5、F-6 |
| 3 | C-2 修复与消费者扫描 | **ACCEPT** | 13 实例 IRI 解析后逐字相同；错误类 IRI 类型断言 13→0；`equivalentClass` = 0；破坏性引用 0；两仪器 --gate/--selftest exit 0 |
| 4 | D2 分流与隔离 | **ACCEPT**（口径须精确化） | 28/12 分流闭合、`CASH_MANAGEMENT` 保持隔离、SIM 与 `aliasMap` 越界 0、账本源哈希命中。**注意口径**：见 §5 F-11② |
| 5 | A-3 包收口（T-4 C5~C7） | **ACCEPT_WITH_CONDITIONS** | 冻结 composite 我独立复算**逐字命中** `a18719778d261448…`；计数 26/16/8 我独立复跑一致；4 份日志正文**逐行可复现**（diff 空）。条件：F-8、F-9 |
| 6 | A-4 SIM 迁移验证 | **ACCEPT_WITH_CONDITIONS** | M1 87=67+20、M4 旧端 67 条 0 不可解析（我独立复算）。条件：F-4、F-2 |
| 7 | A-5（L2 补丁方案 / L3 加载夹具） | **ACCEPT_WITH_CONDITIONS** | L5 幂等为**真二次解析**（非空转）；条件：F-2、F-3、F-10 |
| 8 | A-7 签署页校验器 | **ACCEPT_WITH_CONDITIONS** | 现行 14 号独立复核 = `INCOMPLETE` / `record=OWNER_REVIEW` / `V8=FAIL`；限制见 §5 F-12 |
| 9 | 断言强度与反例完整性 | **NOT_ACCEPTED**（针对"变异复验已证明判据非空转"这一**声明**） | 57 项门禁中至少 4 处判据在**真实执行路径恒真**（F-2/F-3/F-4/F-5）；`--selftest` 的 in-memory 变异**证明不了**真实路径有判别力 |
| 10 | 红线 | **ACCEPT** | `generated/` 零改动、T-Box 哈希未动、KERT 零写入、无新 IRI 发布、`equivalentClass` = 0（.ttl 层）、12 条未强映射 |

**总体**：制品层面 **9/10 项 ACCEPT 或 ACCEPT_WITH_CONDITIONS，1 项（断言强度声明）NOT_ACCEPTED**；**无一条构成对 Loop 关闭或门禁提升的支持**（见 §8）。

## 3. 逐项证据（命令 / 退出码 / 原始输出）

### 3.1 项 1｜门禁板面

```text
$ python3 scripts/onto1_evidence_board_check.py --gate
[E1] evidence dir ok; gates=62
[E2] evidence logs=94 registered=62 allowlisted=32 orphan=0
[E3] registered evidence files present=62/62
onto1-evidence-board: PASS                     EXIT=0
```

**关键判读**：该命令**只做证据卫生（孤儿/登记/白名单）**，**完全不检查 61/1 拆分**（`scripts/onto1_evidence_board_check.py:63-109` 无任何 status 统计）。故板面事实由我另行复算（见 §4.1），结论一致：

- `EVIDENCE.json.gates` = 62；`{pass: 61, inconclusive: 1}`；`exit_code` = {0:61, 3:1}；status/exit **无不一致**；
- 唯一非 pass = `wi_a4_namespace_collision`（`exit_code: 3`，`note` 指明未判定项 `C-1b` 需 D3）；
- 62/62 门禁的 `actor = tech_lead`、`actor_role = implementation`（**无自签 QA**）；`independent_qa = {status: pending, actor: null}`；
- 62/62 门禁的 `output_sha256` 与磁盘证据文件 **逐一对上**（0 失配）；
- `LOOP.yaml.gates` 与 `EVIDENCE.json.gates` 两个集合 **62 = 62，双向差集皆空**。
- 我**独立复跑** `onto1_namespace_collision_check.py --gate` → **EXIT=3，末行 `INCOMPLETE`**，且与 `evidence/a3fix-after-wi_a4_namespace_collision-gate.log` 正文**逐行一致**（`diff` 为空）。结论：**不得要求它变绿，也不得被记成 pass** —— 两件事均未发生。

### 3.2 项 2｜A-1 处置台账

```text
$ python3 scripts/onto1_disposition_ledger.py --gate
PASS [A1] 条目 412 / 声明 412      PASS [A2] 表外/未决 0
PASS [A3] 不可验证 0；位移/解消记账 15 处
PASS [A4] 无归属 0                 PASS [A5] 违例 0
PASS [A6] 豁免 53/412              PASS [A7] 条目合计 8172 / 声明 8172
PASS [A8] by_final/by_wave 一致 = True
A-1 处置表闭环：PASS（8/8）                    EXIT=0
$ python3 scripts/onto1_disposition_ledger.py --selftest     EXIT=0（7/7）
```

**幂等性**：连续两次 `--gate` 后 `a2-disposition-ledger.{csv,json}` sha256 **不变**（`IDEMPOTENT=YES`）。

**我的独立复算（不复用该脚本任何函数，仅读原始 `consumer-scan-summary.csv` + `hits.jsonl`）**：

```text
ledger entries = 412 ；evidence lines checked = 1142（全量，非 20% 抽样）
overall: {'HIT': 1127, 'DRIFT': 13, 'ABSENT': 2}
  FOLLOW_MIGRATION:           HIT 949 / ABSENT 2 / DRIFT 2
  EXEMPT_NON_ONTOLOGY_HOMONYM: HIT 137 / DRIFT 1
  CLOSED_BY_OWNER_DECISION:   DRIFT 10 / HIT 1
  CONTROL_PLANE_REQUIRED:     HIT 40
--- 独立复判 EXEMPT（用**全部 hits**，非 ≤5 样本）---
EXEMPT 行 = 53 ；覆盖 hits = 188 处 ；判定为「有本体证据」= 0
```

两条 `ABSENT` 即 `scripts/gk17_prodcard_to_rdf.py:31` / `:37` 的 `IRI_BANK_EXAMPLE`，属 `MOVED_TO_CONFIG` 声明，我独立验证：

```text
源文件含 IRI 字面量 = False ；目标 projection-config.json 存在 = True
   projection-config.json:16:  "iri": "https://gits.bank.example/ontology/core#",
```

**位移项逐条核查**（15 处）：

| 文件 | 处数 | 记录原因 | 我的独立判断 |
|---|---|---|---|
| `specs/knowledge-architecture/instances/product/products.ttl` | 10 | 授权变更 | **可信**。`git diff` 实证为 Owner 授权的 C-2 命名空间分离（`gits:` → kno/、新增 `prod:` → core#），行位移与 `@prefix` 重排一致 |
| `scripts/gk17_prodcard_to_rdf.py` | 4 | 授权变更 / 重构解消 | **可信但落点不准**（F-6） |
| `frontend/src/router/index.ts` | 1 | 扫描后变更 | **可信**。`stat` mtime = `2026-09-20 23:16` > 扫描 `14:53:45Z`(=22:53:45 CST)；`git log` 命中共 `69429bf`（2026-09-20 23:22，PC0 路由追加），`index.ts:114` = `name: 'PrevisitEvidence'` 确含 token |

### 3.3 项 3｜C-2 修复

```text
$ python3 scripts/onto1_c2_fix_verify.py --gate        → C-2 验收：PASS（7/7）  EXIT=0
$ python3 scripts/onto1_c2_fix_verify.py --selftest    → --selftest PASS（6/6） EXIT=0
   （M1 类型改回错误类 ⇒ 拦下 V3+V5；M2 改实例 IRI ⇒ V2；M3 未声明类 ⇒ V3；M4 注入 equivalentClass ⇒ V6；M5 还原 ⇒ 7/7）
$ python3 scripts/onto1_c2_consumer_scan.py --gate     → C-2 消费者扫描：PASS（7/7） EXIT=0
   G2 断言 0 处；字面提及 7 文件（DOC/LOG）；G3 breaking=无；G5 CODE 消费者 0 个
   G6 扫描幂等（两次结果一致）1cb34f5bb24df26e == 1cb34f5bb24df26e   ← 真二次扫描（onto1_c2_consumer_scan.py:219-223）
```

**我的独立复算（rdflib，自写代码）**：

```text
after 实例 IRI 数 = 13  before = 13
解析后 IRI 集合逐字相同 = True          ← 注意：前缀**标签**由 gits: 改为 prod:，解析后 IRI 不变
after 类型未在 T-Box 声明 = 0
after 类型集合 = {'https://gientech.com/gits/kno/Product'}
错误类 IRI (core#Product) 作类型断言数： after = 0  |  before = 13   ← 修复正文
T-Box 中 kno/Product 是 owl:Class = True
equivalentClass 三元组数 = 0
```

> 诚实记录：先用**前缀字符串**级正则比对时得到"逐字相同 = False"（`prod:prod_cb_001` vs `gits:prod_cb_001`）。改用**解析后 IRI** 级比对后为 True。前者是我自己的口径错误，不是制品问题；此处保留以说明复验层级差异。

### 3.4 项 4｜D2 分流与隔离

```text
$ python3 scripts/onto1_product_relation_resolution.py --gate      → D2 分流：PASS（11/11） EXIT=0
$ python3 scripts/onto1_product_relation_resolution.py --selftest  → PASS（10/10） EXIT=0
```

**我的独立扫描**：

```text
隔离别名 = 7 ['CORPORATE_E_BANK','CASH_MANAGEMENT','FX_FORWARD','RECEIVABLE_LEDGER_TOOL',
              'ORDER_RECEIVABLE_CLOSED_ACCOUNT','FINANCIAL_ADVISORY','DISCOUNT_SERVICE']
  逐个别名： in_SIM=False（7/7）   in_config=True（7/7）      ← 见 F-11②
quarantined_unresolved 条数 = 7 ；resolved 条数 = 5
```

我读了 `projection-config.json`：7 个别名**只**出现在 `quarantinedAliases`（`:36-44`）声明块，**不在** `aliasMap`（`:27-33`，键恰 5 个）。仪器 G11 的判据域就是 `aliasMap`（`scripts/onto1_product_relation_resolution.py:182-183`），故 G11 正确；派工文案的字面表述不准确（F-11②）。

### 3.5 项 5｜A-3 包收口

```text
$ python3 scripts/onto1_a3_closeout.py --gate          → A-2 收口：PASS（8/8） EXIT=0
$ python3 scripts/onto1_a3_closeout.py --selftest      → --selftest PASS（6/6） EXIT=0
```

**我的独立复算（自写脚本，读同一 6 个输入件）**：

```text
我独立复算 composite = a18719778d2614481f7911ab8e2ef4ec81e2942e176cea0d86d61c1c1ac6bdac
a3-freeze.json composite 一致 = True ；inputs 逐项一致 = True
```

**四份 a3fix 日志首行/退出码（原文照录）**：

```text
a3fix-after-wi_a4_namespace_collision-gate.log      # artifact=a18719778d…  # exit=3   ← 碰撞门禁**仍非 PASS**
a3fix-after-wi_a4_namespace_collision-selftest.log  # artifact=a18719778d…  # exit=0
a3fix-after-wi_a3_reference_alignment-gate.log      # artifact=a18719778d…  # exit=0
a3fix-after-wi_a3_reference_alignment-selftest.log  # artifact=a18719778d…  # exit=0
```

**计数口径 26/16/8 我方独立复跑**（不是读台账）：

```text
$ python3 scripts/onto1_namespace_collision_check.py --selftest  → 26 条 PASS 行，**全部 PASS**，末行 selftest: PASS
$ python3 scripts/onto1_reference_alignment_check.py --selftest  → selftest: 16/16 符合预期
$ python3 scripts/onto1_w15_acceptance.py                        → onto1-w15-acceptance: PASS（8/8 符合预期）
a3-count-caliber.json 逐项：26=26 / 16=16 / 8=8 / 11=11 / 10=10 / 8=8 / 7=7，mismatches=[]
```

**日志可复现性（关键）**：我把 `a3fix-after-wi_a4_namespace_collision-gate.log` 去掉 4 行 header 后与我**现跑**的输出做 `diff` ⇒ **逐行一致**。故 C7 的"自证"不是装饰，正文可复算。

### 3.6 项 6｜A-4 SIM 迁移验证

```text
$ python3 scripts/onto1_sim_migration_verify.py --gate       → A-4：PASS（7/7） EXIT=0
$ python3 scripts/onto1_sim_migration_verify.py --selftest   → PASS（7/7） EXIT=0
   M6 输出：B6_消费者切换: 抽检 3 见黑名单 0 · B8_内容级重绑: 抽检 3 见黑名单 0
```

**我的独立复算**：

```text
csv header 已解析；rows = 87 ；迁移行 = 67 ；不可解析 = 0        ← M1/M4 我独立复算一致
new_iris (非 PENDING) 条数 = 12 ：['REGISTRY:ActivationContract', 'REGISTRY:CapabilityPublication',
 'REGISTRY:EndpointBinding','REGISTRY:ConsumerBinding','REGISTRY:ContractVersion',
 'SKOS:TaskTypeScheme','SCHEMA-FIELD:hasTaskType','SCHEMA-FIELD:governedByContract',
 'SCHEMA-FIELD:invokesCapability','SCHEMA-FIELD:referencesAsset','SCHEMA-FIELD:referencesSkill',
 'RETIRED:customerId']                                          ← 全部为**符号化占位**，无一条是 IRI ⇒ 见 F-4
M5 扫描文件数 = 2（product-relations.SIM.ttl, projection-config.json）
B6 sample = 3 条（**其中同一文件重复 2 次**）；B8 sample = 3 条（均为 Java 文件，has_legacy_ns=False）
```

### 3.7 项 7｜A-5（L2 计划 / L3 夹具）

```text
$ python3 scripts/onto1_l3_load_fixture.py --gate        → A-5/L3：PASS（6/6） EXIT=0
$ python3 scripts/onto1_l3_load_fixture.py --selftest    → PASS（6/6） EXIT=0
$ python3 scripts/onto1_l3_load_fixture.py --plan-gate   → A-5/L2：PASS（4/4） EXIT=0
```

L5 幂等判读（**非空转**）：`onto1_l3_load_fixture.py:93-94` 为 `canonical_hash(sim)` vs `canonical_hash(load_all()[2])`，后者**重新解析文件**；且跳过 bnode 的条数被并入 payload（`:63`），故非"同对象哈希两次"。**判定：有效**。

### 3.8 项 8｜A-7 签署页校验器

```text
$ python3 scripts/onto1_signature_verify.py --gate       → A-7：PASS（5/5） EXIT=0
$ python3 scripts/onto1_signature_verify.py --selftest   → PASS（5/5） EXIT=0
$ python3 scripts/onto1_signature_verify.py --verify docs/review/…/14-书面复审决议签署页.md
  {"verdict":"INCOMPLETE","record_kind_allowed":"OWNER_REVIEW",
   "record_kind_forbidden":["ARCHITECTURE_COMMITTEE_APPROVED"],
   "seats_filled":0,"distinct_named_reviewers":0,"v8_verdict":"FAIL",
   "gate_effect":"…不构成委员会批准 ⇒ Wave 0 条件不成立，维持 BLOCKED"}
```

即：**当前不得记录 `ARCHITECTURE_COMMITTEE_APPROVED`**，与 `STATE.json.review_panel.composition_facts.single_natural_person_panel = true` 一致（四席同一自然人）。该门禁 PASS 只说明"分类器判得准"，**不表示 V8 通过**。

## 4. 我亲自复算的原始输出（节选，非引用 TL）

### 4.1 板面（自写聚合）

```text
status counter: {'pass': 61, 'inconclusive': 1} ；total: 62
exit_code distribution: {0: 61, 3: 1} ；status/exit mismatches: 无
--- 唯一非 pass ---
wi_a4_namespace_collision: status=inconclusive, exit_code=3,
  evidence=…/wi_a4_namespace_collision-20260921T050548Z.log,
  output_sha256=769a4611440cc0671f58eb144f70fc62db7cc76cf6bebc2a1b7a134259e5d7e4
--- actors --- {('tech_lead','implementation'): 62}
--- 证据哈希核对 --- mismatch: 0  missing/no-hash: 0
independent_qa: {"status":"pending","actor":null,"session":null,…}
LOOP gates 62 = EV gates 62 ；LOOP-EV=[] ；EV-LOOP=[]
LOOP.status=in_progress ；gate_state.current=RETURN_TO_HLD
```

### 4.2 红线（自写扫描）

```text
specs/semantic/gits-core.owl.ttl = 705578d6324abd0c…              ← 与声明一致，未动
git status --short -- generated/  → 空                            ← generated/ 改动 = 0
equivalentClass：在 *.ttl 中命中 **0 处**（命中全部出现在 docs/** 的规范叙述文本中）
find . -name namespaces.json → 空                                 ← 未建根域
SIM 目录仅 1 文件（product-relations.SIM.ttl）
KERT 仓：find -newermt "2026-09-21 00:00" → **0 个文件**；全仓最新 mtime = 2026-09-20 23:57（poc target/class）
```

### 4.3 未判定项的独立确认

```text
$ python3 scripts/onto1_namespace_collision_check.py --gate     EXIT=3
  … [C-2] PASS（实测 0 / 登记 0 / 未登记 0 / 陈旧 0）
    [C-3] PASS（closure 内 0 个 owl:versionIRI ⇒ 单版本约束**空转**，不计为覆盖）
    [C-4] PASS（…载体自冻结：受控载体 0 个，**空转不计为覆盖**）
  onto1-namespace-collision: INCOMPLETE （C-1b 未判定 ⇒ **不得计为通过**；解除需 D3 签署根域后重跑）
```

值得肯定：该仪器**主动声明自己的空转项不计为覆盖**（C-3/C-4），这是本轮少见的"判据自诚实"。

## 5. 我发现但 TL 未声明的问题

> 严重性为**我的判断**：中 = 会影响结论可信度或后续迁移动作；低 = 表述/可维护性;信息 = 口径提醒。

### F-1（中）`EVIDENCE.json.board_expression` 与自身 `gates` **自相矛盾（陈旧）**

- `EVIDENCE.json.board_expression` 写 `PASS=50 / FAIL=0 / PENDING=1 / total=51`；
- 同一文件的 `gates` 实为 **62**，其中 pass **61**、inconclusive **1**；
- 派工文书 §0 的"62 = 61 pass / 1 inconclusive"与 `gates` 相符 ⇒ **被引用的是 gates，而 board_expression 是上一纪元的残留**。
- 影响：审计者若读 `board_expression`（名字更像"板面表达"）会得到错误板面。**建议**：由实现者修正或显式标注 `stale_after_revision`。**我不代改**。

### F-2（中）**常量化的边界判据 → L6 / M7 在真实路径恒真**

- `scripts/onto1_l3_load_fixture.py:103`：`"boundary": {"sim_only": True, "new_iri_published": False, "specs_written": False}` —— **字面量**，非从任何制品推导；
- `scripts/onto1_sim_migration_verify.py:121` `"dry_run_only": True`、`:125-126` 同类 `boundary` 字面量；
- 对应判据 `L6`（`:121-123`）、`M6`（`:162-164`）、`M7`（`:165-168`）在真实执行路径**不可能 FAIL**。
- `--selftest` 的 P5/N5/N6 是**直接改内存 dict**，因此"被捕获=True"**不能**推出真实路径有判别力。
- 同源问题：`scripts/onto1_product_relation_resolution.py:146` 的 `G7` 读的是制品自声明字段 `r.sim_only`（`product-alias-resolution.json`），属"信任预计算值"。

### F-3（中）`--plan-gate` P4 **恒真**（死逻辑）

- `scripts/onto1_l3_load_fixture.py:209`：`"不得**发布新 IRI" in txt.replace("**不得**", "**不得**") or "不得" in txt`
- `replace` 是无效自替换；`or "不得" in txt` 因文档必含"**不得**写入 KERT"而**永远为真**。
- 验证：把该表达式对一段**不含**"不得发布新 IRI"但含"不得写入 KERT"的文本求值 ⇒ 仍为 True。故 P4 的 4/4 中含一个**不可能失败**的项。

### F-4（中）A-4 的 M5/M2"泄漏=0"**不具备证明力**

- `scripts/onto1_sim_migration_verify.py:94`：`new_iris = [新IRI草案 for r in rows if "PENDING" not in 新IRI草案]`
- 实测这 12 条**全部是符号化占位**（`REGISTRY:*` 5、`SCHEMA-FIELD:*` 5、`SKOS:*` 1、`RETIRED:*` 1），**没有一条是 IRI 字面量**；
- 因此"在 SIM 通道里搜不到它"是**构造性必然**，与其想证明的"未提前发布新 IRI"无因果关系。
- 诚实口径应为："D3 未签 ⇒ 草案中不存在具体新 IRI ⇒ **M5 无法构造有效 needle，本条不具备证明力，待正式 IRI 发布后重建**"。
- 附带：`iri-mapping-draft.csv` 的 `新IRI形态` 含 5 条 `UNKNOWN_FORM`（SCHEMA-FIELD 类）与 1 条 `NONE_RETIRED`（`customerId`）——草案自身未收敛项，未在派工清单中提示。

### F-5（中）A-1 的 A5 判据与构建路径**同源（真实路径恒真）**

- `scripts/onto1_disposition_ledger.py:292-293` 的 `exempt_bad` = "final 为 EXEMPT 且 `ontology_consuming_hits` 非零"；
- 而同一文件 `:225` 的赋值分支决定：**只有** `consuming == 0` 才会得到 EXEMPT。两条判据出自同一函数 ⇒ **真实路径上 A5 恒真**。
- TL 已修掉"计数信任预计算值"（A7/A8 确实从 entries 复算，我核对无误），但 **A5 是同类问题的残留变体**：判据与被判对象同源。
- 我另做的**真正独立复判**（用全部 hits + 我自己的 RDF marker 表）结论一致（53 行 / 188 处 hits / 0 违例），**故结论本身可信，但仪器没在证明它**。

### F-6（低-中）位移记录落点指向**注释行**，对 Wave 2/3 迁移有误导

- 台账记 `scripts/gk17_prodcard_to_rdf.py:33→5`、`:35→5`（原因"授权变更"）；
- 实测该文件 `requiresProduct` 在**第 5 行（docstring）**与**第 37 行（映射值）**、`complementsProduct` 在**第 5 行**与**第 39 行**；
- `verify_evidence`（`scripts/onto1_disposition_ledger.py:148-158`）取的是**首个出现行**，落到注释行 ⇒ 记录的"新位置"不是真实迁移落点。移民主体若按台账逐行定位，会定位到一句说明文字。

### F-7（低）决策 ID **D-14 / D-15 各被复用于两条不同纪律**

```text
loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md:123  D-14｜record_gate 尝试预算的语义修正
loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md:234  D-14｜证据文件操作纪律
loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md:104  D-15｜禁止"再次调高上限"作为触顶出口
loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md:246  D-15｜门禁尝试预算改为按 revision 纪元计数
```

且全文编号非单调（`D-3` → `D-17` → `D-16` → `D-15` → `D-14` → `D-13` → `D-14` → `D-15`）。派工文书引用的"D-14（不得删改任何证据）"与"D-15（按 revision 纪元计数）"取的是**后一套编号**。**引用歧义风险**：同一条纪律 ID 可指向两种义务。

### F-8（低）C7 覆盖日志的备份落在**仓外易失**位置

- `scripts/onto1_a3_closeout.py:126-152` 会**覆盖** 4 份 `a3fix-after-*.log`，`shutil.copy2` 备份至 `/tmp/a3closeout-backup`（我确认备份现存 4 件）；
- D-14 纪律 #4 明确"带 `# artifact=<hash>` 的旧日志无法逐字重建 ⇒ 删除视为不可逆"；`/tmp` 不具持久性 ⇒ 旧日志原文**事实上有丢失风险**，仓内仅存 `a3fix-00-BEFORE-AFTER.md` 的**摘要对照**（`:20-77`）。
- 影响有限：这 4 份是**补充日志**（非 `EVIDENCE.json` 登记证据，E3 未涉及），故不破坏证据链；但按 D-14 精神应 `cp -a` 到**仓内** `evidence/archive/`。

### F-9（低）C5 计数按"行"统计，**不校验是否全过**

- `scripts/onto1_a3_closeout.py:80`：`cases = [l for l in txt.splitlines() if l.startswith(("PASS ", "FAIL "))]` ⇒ 若某反例**漏检**（出现 `FAIL ` 行），用例数**仍为 26**，C5 照旧 PASS。
- 当前实测 26/26 全 PASS（我已逐行确认），故**不影响本轮结论**；属下一次的盲区。

### F-10（低）L1 判据写成常量 `True`

- `scripts/onto1_l3_load_fixture.py:110`：`("L1 三制品均可解析…", True, "rdflib 解析成功")`；
- 解析失败时 `inspect()` 抛异常 → 非零退出，故**实际 fail-closed**；但"6/6"里含一项非判据，计数口径不纯。

### F-11（信息）派工文书两处口径**不精确**，照字面执行会误判

1. 派工 §1 项 1 写「`python3 scripts/onto1_evidence_board_check.py --gate` 期望 62 = 61 pass / 1 inconclusive」——**该命令不检查拆分**（§3.1 已证）。板面事实为真，但**不能归因于该命令**；若下一位复验者据此断言"仪器已验板面"，会形成新的"假绿"。
2. 派工 §1 项 4 写「隔离别名在 SIM 输出与投影配置中均 0 处」——**字面为假**：7/7 别名都在 `projection-config.json` 的 `quarantinedAliases` 块内（`projection-config.json:36-44`）。正确口径是「**`aliasMap` 越界 = 0**」。按字面机械复验会得到 7 处"越界"并可能误判 NOT_ACCEPTED。

### F-12（信息）A-7 的能力边界

`ARCHITECTURE_COMMITTEE_ELIGIBLE` 只表示"4 个**非空且互异的名字字符串** + 已签字已署期"（`scripts/onto1_signature_verify.py:41-67`），**不**验证这四人是真实独立自然人；脚本 docstring 亦自陈"ELIGIBLE ≠ 已批准"。作为**形式校验器**可用，**不得**作为独立性成立的证据。

## 6. 红线复验（逐项）

| 红线 | 复验方式 | 结果 |
|---|---|---|
| 6.1 `generated/` 改动 = 0 | `git status --short -- generated/` | **空** ✅ |
| 6.2 `specs/semantic/gits-core.owl.ttl` = `705578d6324abd0c` | `sha256sum` | **一致** ✅ |
| 6.3 不得出现新 IRI 发布 | `find -name namespaces.json` = 空；SIM 目录仅 1 文件 | **未发布** ✅ |
| 6.4 KERT 仓零写入 | KERT 仓 `find -newermt "2026-09-21 00:00"` = **0 文件**；全仓最新 mtime `2026-09-20 23:57`（与本轮窗口 17:28–21:37 无交集） | **零写入** ✅ |
| 6.5 `equivalentClass` 滥用 = 0 | `*.ttl` 全仓扫描命中 0；rdflib `triples((None, OWL.equivalentClass, None))` = 0 | **0** ✅ |
| 6.6 12 条关系未被强映射 | 7 别名 ∉ `aliasMap`；∉ SIM 输出；`CASH_MANAGEMENT` 仍隔离 | **未强映射** ✅ |
| 6.7 无自签 QA / 无门禁提升 | 62/62 门禁 actor = `tech_lead`/implementation；`independent_qa.actor = null`；`gate_state.current` = `RETURN_TO_HLD` 未变 | ✅ |

## 7. 未覆盖 / 边界声明

- **未复验**：A-6（GK17 侧重跑重记）——不在派工清单；B 族/C 族（Owner 决策、KERT 写入、域名/数据 Owner）——非本角色职责。
- **未复验**：`docs/**` 与 KERT 侧文档的语义正确性（本轮只验可复算制品与判据强度）。
- 我**只读**：未改任何 `specs/**`、`generated/**`、证据文件、脚本；未对 KERT 仓做任何写入；未删除任何证据（D-14）。
- 本报告中的判据引用均为 `文件:行`，制品引用均为 `sha256`；与 `specs/` 冲突时以 `specs/` 为准。

## 8. 关于 `QA_PASS`

**`QA_PASS` 不得由我或任何人记录。** 理由（本 Loop 的客观状态，非我的裁量）：

1. 门禁板面仍有 **1 项 `inconclusive`**（`wi_a4_namespace_collision`，`exit=3`），其未判定项 `C-1b` 待 **D3 正式根域联签**；未判定 ≠ 通过。
2. `LOOP.yaml.gate_state.current` 仍为 **`RETURN_TO_HLD`**；Wave 0 及后续仍 `BLOCKED`。
3. 本轮我另判 **项 9（断言强度声明）`NOT_ACCEPTED`**（F-2/F-3/F-4/F-5 四处判据在真实路径恒真）。

**建议的下一步（供 Owner / 下一 holder 取用，均属建议、非结论）**：
① 由实现者修正 F-1（陈旧 `board_expression`）与 F-3/F-4（死判据 / 无效 needle）——这三条是**可直接构造反例**的，可立即验证；
② F-2/F-5 属"声明类判据"，建议改为从制品/配置**派生**（而非字面量），或显式改写为"声明项（不构成验证）"以免被误读为已验证；
③ F-6 建议把位移落点改为"实际迁移目标行"，并在台账中区分"注释/说明"与"代码/配置"命中；
④ F-7 建议给第二条 D-14/D-15 重新编号并加 supersede 说明（历史记录保留，不删除）。

## 9. 我本次执行对工作区的副作用（自我披露）

复验**不是**全程只读——以下仪器在 `--gate` / `--selftest` 时会**重写自己的制品**（内容经我验证为确定性/可复现，故无实质变化）：

| 我执行的命令 | 写到了哪里 | 我验证的方式 |
|---|---|---|
| `onto1_disposition_ledger.py --gate`（×2） | `evidence/prep/a2-disposition-ledger.{csv,json}` | 两次 sha256 **不变**（`136e9de43cbb11fa…`）⇒ 幂等 |
| `onto1_sim_migration_verify.py --gate` / `--selftest` | `evidence/prep/sim-migration-verify.json` | 由制品源（mapping csv + T-Box）派生，判据 M1~M7 前后一致 |
| `onto1_c2_consumer_scan.py --gate` | `evidence/c2-consumer-scan.json` | G6 幂等判据内部已断言两次扫描一致 |
| `onto1_c2_fix_verify.py --selftest` | **临时**改写 `specs/.../products.ttl` 后**写回原文** | 我的 sha256 复核实为 `e1b6e09e57d5834aa8c9b33ad016d91a5e59295480ade5ba55bba843f107c514`，与改写前一致 |
| `onto1_l3_load_fixture.py --plan-gate` | `evidence/prep/L2-KERT-PATCH-PLAN.md`（由 `kert-change-proposal.json` **派生**） | 派生源未变 ⇒ 文本未变 |

- `onto1_evidence_board_check.py --gate`、`onto1_product_relation_resolution.py`、`onto1_a3_closeout.py --gate`、`onto1_signature_verify.py` 为只读；
- 我**未**执行 `onto1_a3_closeout.py --build`（它会覆盖四份 a3fix 日志，属 F-8 讨论的动作）；
- 除本报告外，我**未新增/删除任何文件**；`loops/ONTO1-ontology-split/` 整目录为未跟踪（`??`），故上述制品重写不体现为 git diff。

---

**报告完** ｜ 生成者：`independent_qa` ｜ 唯一写域：本文件
