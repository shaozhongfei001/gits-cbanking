# GK17-ontology-unified-map｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-17`（Tick 20） |
| **holder** | `tech_lead` |
| **packet** | `GK17-ontology-unified-map` |
| **wave** | `W5 ACCEPTED → W2/W6 已交付（**QA 已复核完，待 Owner 签**）→ W8.0-a/b/c **与 W8.0-d（D1/D2 盲区修复）均已完成** → 四项裁定已落盘 → **W4 / W7 已解锁**` |
| **status** | `in_progress`（**未收敛**） |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED、ADR Accepted |

---

## 一句话状态

> 本体 **9 → 32 类**（W1 ACCEPT，OWL 32 类 / 34 对象属性 / 1 数据类型属性）。
> 硬约束防线**机械落地**（W5 ACCEPT）。W2 把"本体**真实**进入知识路由"从声称变成**可判定事实**。
> **当前瓶颈是「判定」，不是「实现」** —— W2 与 W6 均已交付、待 ACCEPT，而判定权**都不在 TL 手上**。
> Tick 17 已把 `NEXT_SESSION.md` §C 中**不被任何裁定阻塞**的三条预做完毕（含 D2/D4 探针 + 判定逻辑自身的变异复验）。

---

## 下一棒（新会话直接执行，按优先级）

### A. 独立 QA —— **已完成**（Tick 19 回收），**等 Owner 签**

| 项 | 值 |
|---|---|
| 报告 | `evidence/INDEPENDENT_QA-W2-W6-independent-qa.md`（回收摘要见 QA 包 §9） |
| 靶标 | **11/11 sha256 一致**（QA 复核的就是冻结状态） |
| **判定建议** | **W2 = `ACCEPT_WITH_CONDITIONS`**；**W6 = 不予 ACCEPT**（V1 ② 未执行）/ 或由 Owner 裁定缩减范围 |
| **独立性（不粉饰）** | **授权下的降级独立**：该会话**由 TL 派生**，**不是**真第三方 ⇒ 产出为**「判定建议」**，**不构成 `QA_PASS`** |
| **签权** | **ACCEPT 由 Owner 签**（TL 与 QA 会话均不代签） |
| QA 对 `gate_owner`→TL 所有权回归 | **有条件接受**（3 条件，已落盘 `ROLE_BOARD.qa_conditions`） |
| QA 新增对抗发现 | **D1 / D2 各有一条已证实的绕过盲区**（QA 报告 §3.7，TL 已核验成立）⇒ 见 §D 新增必办 |

⚠ **任何后续复核者必读 QA 包 §0**：模块级门禁依赖 `~/.m2` 新鲜度，否则会撞**假红**
（根因见 `FAILURES.md` `20260915T073300Z`；前置条件已登记进编排表 §0.1）。
⚠ **目标必须冻结**：以 QA 包 **§8.2 的 sha256 清单**为准（`HEAD=71169042` **早于**本轮改动，工作区 dirty）。

### B. Owner / 治理裁定 —— **Tick 18 已由 Owner 授权 TL 裁定并落盘**

> 文书：`docs/architecture/GK17-四项悬置口径裁定-V1.0.md`（含「Owner 授权 TL 出裁定」的边界声明）

| # | 裁定结论 | 残留（谁还需要动） |
|---|---|---|
| **①** | **维持不建权威映射表**（TL 自纠了上轮的口头建议）；出**产品 Owner 最小决策包**（12 个符号各答 1 个字）；**W7 缩减范围推进** | **产品 Owner**：逐符号定性（§1.5 表） |
| **②** | **`legal_entity` 权威 = file-first SSOT**（`scenario/seed/**`），运营库 = 投影；`WP3.2` 据此实现 | 数据映射 Owner（若有差异需提差异清单） |
| **③** | **不为 `Account` / `Document` 造类**：身份由 `Transaction.accountId` / `Evidence.sourceUri` 承担 | 语义架构 Owner（若要求独立身份） |
| **④** | **不在 GK17 内拆门禁** → 另立 `GK18-test-gate-decoupling`；GK17 如实记 `ENVIRONMENT_LIMITATION` | **项目 Owner**：是否立项 |

⇒ **`WP3.2` / `W4` / `WP7.1` 的依赖已清除。**

### C. 其余角色（按依赖）

| Wave | 状态 | 解锁条件 |
|---|---|---|
| **W4**（非结构化 → 候选断言） | ✅ **已解锁**（依赖已清除），未开始 | Tick 18 裁定②③ 清除了 `WP3.2` 的阻塞 |
| **W7**（产品可见化：前置/互斥/配套 + 准入） | ✅ **已解锁（范围收窄）**，未开始 | 裁定①§1.6：准入/材料/场景**可做**；前置/互斥/配套**必须醒目标注"待产品 Owner 定性"**，不得留白 |
| **W8**（收口） | 未开始 | 依赖"全部" waves；剩余必办见下 |

### D. W8 必办（TL 拥有）

| # | 项 | 状态 |
|---|---|---|
| ① | D2/D4 专门探针**内置**到 `gk17_triple_consistency_check.py` 的变异自检 | ✅ **Tick 17 完成**（含判定逻辑自身的 MUT-A/B/C 复验） |
| ② | 修脚本路径口径（编排表 §WP5.3 与 `ROLE_BOARD` 指向**不存在**的文件） | ✅ **Tick 17 完成** |
| ③ | 为模块级门禁登记**前置条件** | ✅ **Tick 17 完成**（编排表 §0.1，5 条） |
| ④ | `run_gates.py` 登记 GK17 门禁**二选一**（登记并同步改 `LOOP.yaml` 的"22/23"文案 / 删回退表） | ⬜ 待办（**会改门禁集合 ⇒ 收口期协调**） |
| ⑤ | W6 的 pending gate `gk17_v1_v4_experiments` 登记进 `LOOP.yaml.gates` | ⬜ 待办（同上，会改门禁集合） |
| ⑥ | Loop 记忆**键唯一性**校验（`STATE.json` 曾有 `W5` 重复键 ⇒ 静默读作 `not_started`） | ⬜ 待办 |
| ⑦ | 两道环境红处置 | ⬜ 待 **Owner/治理**裁定（见 B-4） |
| **⑧（Tick 19 QA 发现）** | **修 D1/D2 绕过盲区** + 把 E1/E2/E5 加入内置变异自检 | ✅ **Tick 20 完成**（修复前/后对照 `0/0/0 → 1/1/1`，基线仍 0；判定逻辑变异复验 MUT-D/MUT-F 各自转红；两道门禁已重落证） |
| **⑫（Tick 20 TL 新发现）** | **命名空间归属裁定**：本体 `gits-core.owl.ttl:1` 用 `https://gientech.com/gits/kno/`，投影 `products.ttl:1` 用 `https://gits.bank.example/ontology/core#` ⇒ **同一前缀两个命名空间，A-Box 与 T-Box 不连通**。修它须动 `products.ttl`（哈希变化 ⇒ 靶标失效）+ 改投影器 + 重跑投影门禁 | ⬜ **待 Owner / 语义架构 Owner 裁定**（已记账 `FAILURES.md` `20260917T010000Z`） |
| **⑨（新增·Tick 19）** | `run_gates.py` 汇总行分子与括注矛盾（`INCONCLUSIVE` 被计入分子）⇒ **改工具，全 Loop 共用** | ⬜ 待治理（不在 GK17 scope） |
| **⑩（新增·Tick 19）** | `LOOP.yaml.contract_check.pass_condition` 的"22/23"文案与事实对齐（属**判据内容**，`tech_lead` 明确 `forbidden`）⇒ 收口期协调变更 | ⬜ W8 |
| **⑪（新增·Tick 19）** | "25/23" 三套分母对齐（注入器覆盖 25 / `run_gates` 登记 23 / 真 PASS 21） | ⬜ W8（连带④） |

---

## 已完成（全部经门禁自证）

| Wave | 状态 | 关键产出 |
|---|---|---|
| **W0** | ACCEPT | 基线快照（含既有红灯，防"把既有问题算到本 Loop"） |
| **W1** | ACCEPT | 本体 **9 → 32 类**（OWL + LinkML 双源）；判据 V3 前置 |
| **W2** | 已实现，**待 ACCEPT** | `OntologyPort`+Jena（WP2.1）；本体真实进入路由、fail-closed（WP2.2）；`planHash` 纳入本体版本（WP2.3） |
| **W3.1** | 完成（WP3.2 阻塞） | 产品卡→RDF 投影器；**13 个体**；重复投影逐字节一致；**40 处引用 100% 悬空**（数据缺陷，已裁定） |
| **W5** | ACCEPT | 三条硬约束机械防线；`triple_consistency_check` 现**D1/D2/D4 各自有专门负例**（Tick 17） |
| **W6** | 已交付，**待 ACCEPT** | V1–V4 实验与证据包（`evidence/GK17-W6-V1-V4-证据包.md`） |
| **W8.0-a/b/c** | 完成（预做） | D2/D4 探针 + 路径口径 + 门禁前置条件；见 `memory/waves/W8-PLAN.md` |

**关键裁定**：
- `WP1.3` 关系类型权威=本体 / 实例权威=产品卡 / 投影单向；
- **产品卡引用空间**：合法取值空间 = `PROD-*`；12 个符号**不是产品关系实例**（范畴错误）；候选定性归**产品 Owner**；
- **W2 设计裁定**：本体加载置于**请求级护栏之后、路由解析之前**（四条 routeMode 的共同前置，不给部分 credit）；
  `evidence`（含来源路径）**不入** `planHash`，只有本体**版本**入哈希（保可重放）。

---

## 门禁总表（`EVIDENCE.json` 实测）

| 门禁 | 结果 |
|---|---|
| `contract_generate` / `contract_check` / `security_check` / `gk_ke_gates` | **PASS**（INTEGRITY FAILURES 空）<br>⚠ **准确口径（Tick 19 更正）**：`[PASS]=21` / `[FAIL]=1`（readiness）/ `[INCONCLUSIVE]=1` / 总 23 ⇒ **真 PASS = 21/23**（**不是** 22/23 —— 工具汇总行的分子把 `INCONCLUSIVE` 算了进去，与同句括注自相矛盾，见 `FAILURES.md` `METRIC_CLAUSE_SELF_CONTRADICTION`） |
| `ontology_load`（`MechanismE2eIT`） | **PASS**（`1/0/0/0`） |
| `ref_anchor_check` / `gk17_prodcard_projection` | **PASS** |
| `triple_consistency_check` | **PASS**（Tick 17 重落证；D2/D4 探针各自捕获） |
| `gk17_mutation_regression` | **PASS**（Tick 17 重落证；20/20 注入检出，0 崩溃 / 0 未检出 / 0 未确立） |
| `./mvnw test`（测试面分离验证） | **PASS**（api `603/0/0/4`、worker `22/0/0/0`） |
| `frontend_test` | **FAIL（环境）** —— 沙箱批量删除守卫阻断 `npm ci` |
| `backend_test` | **FAIL（环境）** —— OWASP `dependency-check` 需联网拉 RetireJS，模块**被 SKIPPED**<br>⚠ **口径更正（Tick 19）**：是 **RetireJS 端点间歇性超时**，**不是**确定性"不可达" —— 本 Loop evidence 有 **1 次全绿**（`backend_test-20260915T002338Z.log`：BUILD SUCCESS / **0 SKIPPED** / 15 份报告全 PASS）；TL 2026-09-16 重试**仍红**（`…-W8-RETRY.log`：14 模块 SKIPPED）。**两者都要写**：不得因"曾绿过"把本次红计为通过 |

> **不得**把后两红读作通过；**不得**为它们改门禁构成（须治理裁定）。
> 测试面请用 **`./mvnw test`**（不进 `verify`）。
> **不得计为通过**：`gate-injection-tests` 总判定 `INCONCLUSIVE`（3 个**非 GK17** 门禁缺负例，属 W0 既有基线）、
> `semantic-consumption` READINESS NOT MET、`KD-*` 无独立锚点（`NOT_COUNTED_AS_PASS_ASSERTION`）。

---

## 纪律（本 Loop 用血换来的五条）

1. **门禁 PASS ≠ 正确**：W5 曾出现"本体读成 0 类、投影读成 0 个体"却报 PASS ——
   它 PASS 是因为**什么都没解析**。**断言前必须核对输入基数**。
2. **门禁 PASS ≠ 判定有效**：新增断言必须**再对判定逻辑本身做变异**（Tick 17 的 MUT-A/B/C），
   否则"我加了检查"与"检查真的会红"是两件事。
3. **门禁执行必须串行**（GK16 T-24：并发产生假 FAIL）。
4. **先记账再修**（`record_before_fix`），**按原命令重跑**，**追加**结果不覆盖。
5. **改公共签名前，同时 grep「构造点」与「装配方法调用点」** —— W2 曾因只 grep 前者造成一次自伤回归。

---

## 边界（不可越）

- 不手工编辑 `generated/`；不改封版 `docs/dd/gk-ke-contract/`；
- 不解除 `_public_reference` 的 `VERIFICATION_ONLY` 红线；不启用隔离资产（Oracle / Ossie）；
- 不做生产写回；**不代签** `QA_PASS` / Owner 决议；**不把 `INCONCLUSIVE` 计入通过**；
- **本工作区另有其他执行者**在提交 ⇒ `git add` **只用显式路径**，勿用 `git add -A`；
- `evidence/gk-ke-chain-trace/trace.json` 每次跑门禁都会被重写，**提交前** `git checkout --` 还原。
