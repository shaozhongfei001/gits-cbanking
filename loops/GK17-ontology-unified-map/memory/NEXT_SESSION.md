# GK17-ontology-unified-map｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-15` |
| **holder** | `tech_lead` |
| **packet** | `GK17-ontology-unified-map` |
| **wave** | `W5 ACCEPTED → W2 已实现（WP2.1/2.2/2.3 全做完，**待 ACCEPT**）；W6 已放行` |
| **status** | `in_progress`（**未收敛**） |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED、ADR Accepted |

---

## 一句话状态

> 本体已从 9 类扩到 **32 类**（W1 ACCEPT），硬约束防线已**机械落地**（W5 ACCEPT）。
> W2 把"本体**真实**进入知识路由"从**声称**变成了**可判定事实**：
> 规划器每次真实加载本体，`versions.ontology` 是内容派生值（占位串已删除），
> `trace.ontologyEvidence` 可复核，本体不可达/不可解析 ⇒ `Deny`（fail-closed），
> `planHash` 已对本体内容敏感（**判据 V2 由构造保障**，并经变异自证）。
> **W2 尚未 ACCEPT** —— 需独立 QA / Owner。

---

## 下一棒（新会话直接执行）

**A. W2 交 ACCEPT（不得自签）**：
`memory/waves/W2-PLAN.md` 的 ACCEPT 判据已全部满足，证据见 `memory/waves/W2-ITER.md` 的 **ITER 2**
与 `memory/ORCHESTRATOR.md` 的 **Tick 14**。独立 QA 应重点复核：

1. `trace.ontologyEvidence` 是否**真含四类计数与来源**（而非"已加载"空话）；
2. 本体不可达时是否**既不抛异常也不出计划**（拒绝码 == 端口 `failureCode()`）；
3. 判据 V2 的**两条负例**是否各自具备"变异前 PASS / 变异后 FAIL / 恢复 PASS"（M1 / M2）；
4. **设计裁定 2 是否成立**：来源路径**不得**入 `planHash`（有守护用例）。

**B. W6（V1–V4 实验）已放行** —— 见 `STATE.json` 的 `next_action`。

---

## 已完成（全部经门禁自证并提交）

| Wave | 状态 | 关键产出 |
|---|---|---|
| **W0** | ACCEPT | 基线快照（含既有红灯，防"把既有问题算到本 Loop"） |
| **W1** | ACCEPT | 本体 **9 → 32 类**（OWL + LinkML 双源）；判据 V3 前置 |
| **W2** | 已实现，**待 ACCEPT** | `OntologyPort`+Jena（WP2.1）；本体真实进入路由、fail-closed（WP2.2）；`planHash` 纳入本体版本（WP2.3） |
| **W3.1** | 完成（WP3.2 阻塞） | 产品卡→RDF 投影器；**13 个体**；重复投影逐字节一致；**40 处引用 100% 悬空**（数据缺陷，已裁定） |
| **W5** | ACCEPT | 三条硬约束机械防线：`ref_anchor_check`（6/6 变异自证）、`triple_consistency_check`（根治 6 处空转）、`gk17_mutation_regression`（注入 18→20 全检出） |

**关键裁定**：
- `WP1.3` 关系类型权威=本体 / 实例权威=产品卡 / 投影单向
- **产品卡引用空间**：合法取值空间 = `PROD-*`；12 个符号**不是产品关系实例**（范畴错误）；
  候选定性归**产品 Owner**
- **W2 设计裁定**：本体加载置于**请求级护栏之后、路由解析之前**（本体是四条 routeMode 的共同前置，
  不给部分 credit）；`evidence`（含来源路径）**不入** `planHash`，只有本体**版本**入哈希（保可重放）

---

## 门禁总表

| 门禁 | 结果 |
|---|---|
| `contract_generate` / `contract_check` | **PASS**（`make check` 22/23，INTEGRITY FAILURES 空） |
| `ontology_load`（`MechanismE2eIT`） | **PASS**（`1/0/0/0`） |
| `./mvnw test`（测试面分离验证） | **PASS**（api `601/0/0/4`、worker `22/0/0/0`） |
| `frontend_test` | **FAIL（环境）** —— 沙箱批量删除守卫阻断 `npm ci` |
| `backend_test` | **FAIL（环境）** —— OWASP `dependency-check` 需联网拉 RetireJS，端点不可达 ⇒ 模块**被 SKIPPED** |

> 后两者为**环境**，不阻塞 Wave，但**共同阻塞 W8**（`exit_criteria.dev` 要求全 implementation 门禁通过）。
> **不得**把这两红读作通过；**不得**为它们改门禁构成（须治理裁定）。
> 测试面请用 **`./mvnw test`**（不进 `verify`）。

---

## 待 Owner / 治理裁定（4 项，已入 `STATE.json`）

1. 产品卡引用空间的**逐符号定性**（TL 已出候选，权威归**产品 Owner**）
2. `legal_entity` 字段口径：迁移脚本（运营库）vs file-first SSOT（场景包）
3. `Account` / `Document` 权威物理源（GITS 侧**无系统类**，不得发明字段）
4. 两道环境门禁的处置（离线缓存 feed / 拆两道 / 显式允许跳过）

---

## W8 必办（已登记）

- D2/D4 专门探针**内置**到 `gk17_triple_consistency_check.py` 的 `--selftest`
- `run_gates.py` 登记 GK17 门禁：**二选一**（登记并同步改 `LOOP.yaml` 的"22/23"文案 / 删回退表）
- **D4「有能无力」**：需产品 Owner 定性后才有真实输入
- **新增（Tick 14 附带 finding）**：`STATE.json` 曾有 **`W5` 键重复**（JSON 后键覆盖前键
  ⇒ 实际读数是 `not_started`，与 `current_phase` 矛盾）。本轮已修正；
  建议 W8 加一条**Loop 记忆的键唯一性校验**（记录静默失真比红更危险）

---

## 纪律（本 Loop 用血换来的四条）

1. **门禁 PASS ≠ 正确**：W5 曾出现"本体读成 0 类、投影读成 0 个体"却报 PASS ——
   它 PASS 是因为**什么都没解析**。**断言前必须核对输入基数**。
2. **门禁执行必须串行**（GK16 T-24：并发产生假 FAIL）。
3. **先记账再修**（`record_before_fix`），**按原命令重跑**，**追加**结果不覆盖。
4. **改公共签名前，同时 grep「构造点」与「装配方法调用点」** —— W2 曾因只 grep 前者
   而漏掉 `KnowledgeArchitectureConfigTest`，造成一次自伤回归（已记账收敛）。

---

## 边界（不可越）

- 不手工编辑 `generated/`；不改封版 `docs/dd/gk-ke-contract/`；
- 不解除 `_public_reference` 的 `VERIFICATION_ONLY` 红线；不启用隔离资产（Oracle / Ossie）；
- 不做生产写回；**不代签** `QA_PASS` / Owner 决议；**不把 `INCONCLUSIVE` 计入通过**；
- **本工作区另有其他执行者**在提交 ⇒ `git add` **只用显式路径**，勿用 `git add -A`；
- `evidence/gk-ke-chain-trace/trace.json` 每次跑门禁都会被重写，**提交前** `git checkout --` 还原。
