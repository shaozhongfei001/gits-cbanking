# GK17-ontology-unified-map｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-15` |
| **holder** | `tech_lead` |
| **packet** | `GK17-ontology-unified-map` |
| **wave** | `W5 ACCEPTED → W2 进行中（WP2.1 完成，WP2.2/WP2.3 待做）` |
| **status** | `in_progress`（**未收敛**） |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED、ADR Accepted |

---

## 一句话状态

> 本体已从 9 类扩到 **32 类**（W1 ACCEPT），硬约束防线已**机械落地**（W5 ACCEPT，10 门禁自证）。
> 当前把"本体**真实**进入知识路由"从**声称**变成**可判定事实** ——
> `versions.ontology` 仍是硬编码占位串，`planHash` 对本体内容不敏感 ⇒ **判据 V2 在构造上不成立**。

---

## 下一棒（新会话直接执行）

**派工提示词（自包含，可直接粘贴）**：
`memory/handoffs/GK17-W2-WP22-WP23-派工提示词-V1.0.md`

**任务**：GK17 的 **W2 · WP2.2 + WP2.3**
**写者独占**：`modules/knowledge-architecture/`、`apps/api/.../config/`、`specs/knowledge-architecture/examples/AP-*-GOLDEN.json`

---

## 已完成（全部经门禁自证并提交）

| Wave | 状态 | 关键产出 |
|---|---|---|
| **W0** | ACCEPT | 基线快照（含既有红灯，防"把既有问题算到本 Loop"） |
| **W1** | ACCEPT | 本体 **9 → 32 类**（OWL + LinkML 双源）；判据 V3 前置 |
| **W3.1** | 完成（WP3.2 阻塞） | 产品卡→RDF 投影器；**13 个体**；重复投影逐字节一致；**40 处引用 100% 悬空**（数据缺陷，已裁定） |
| **W5** | ACCEPT | 三条硬约束机械防线：`ref_anchor_check`（6/6 变异自证）、`triple_consistency_check`（根治 6 处空转）、`gk17_mutation_regression`（注入 18→20 全检出） |

**关键裁定**：
- `WP1.3` 关系类型权威=本体 / 实例权威=产品卡 / 投影单向
- **产品卡引用空间**：合法取值空间 = `PROD-*`；12 个符号**不是产品关系实例**（范畴错误）；
  候选定性归**产品 Owner**

---

## 门禁总表：**9 pass / 2 fail**

| fail | 原因 | 归属 |
|---|---|---|
| `frontend_test` | 沙箱批量删除守卫阻断 `npm ci` | 环境 |
| `backend_test` | OWASP `dependency-check` 需联网拉 RetireJS，端点不可达 ⇒ 模块**被 SKIPPED** | 环境 |

> **两者均为环境**，不阻塞 Wave，但**共同阻塞 W8**（`exit_criteria.dev` 要求全 implementation 门禁通过）。
> **不得**把这两红读作通过；**不得**为它们改门禁构成（须治理裁定）。

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
- ~~三道门禁的命令回退表~~ ⇒ 同上
- **D4「有能无力」**：需产品 Owner 定性后才有真实输入

---

## 纪律（本 Loop 用血换来的三条）

1. **门禁 PASS ≠ 正确**：W5 曾出现"本体读成 0 类、投影读成 0 个体"却报 PASS ——
   它 PASS 是因为**什么都没解析**。**断言前必须核对输入基数**。
2. **门禁执行必须串行**（GK16 T-24：并发产生假 FAIL）。
3. **先记账再修**（`record_before_fix`），**按原命令重跑**，**追加**结果不覆盖。

---

## 边界（不可越）

- 不手工编辑 `generated/`；不改封版 `docs/dd/gk-ke-contract/`；
- 不解除 `_public_reference` 的 `VERIFICATION_ONLY` 红线；不启用隔离资产（Oracle / Ossie）；
- 不做生产写回；**不代签** `QA_PASS` / Owner 决议；**不把 `INCONCLUSIVE` 计入通过**；
- **本工作区另有其他执行者**在提交 ⇒ `git add` **只用显式路径**，勿用 `git add -A`。
