# 独立 QA 报告（第二轮 / W3R2）— ONTO1-ontology-split

> 清单依据：`memory/handoffs/TL-ADJUDICATION-QA-W3-2026-09-21.md` §三（F-1~F-12 修复复核）+ `memory/HUMAN-ACTIONS-PROMPTS.md` 待人类-7 的 ①~⑩。
> 原则：**不采信 TL 与本汇报方的任何结论**。下列每条结论均由**我本人执行命令**取得，原始输出照录。

## 0. 开工声明

```text
actor      = independent_qa（第二轮；非实现方、非前任 holder 执行会话、非 PSO/ICO 兼任者）
写域（唯一）= loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3R2-2026-09-21.md
只读       = /home/szf/dev/gits-cbanking 全仓 + /home/szf/dev/Leibniz-KERT（KERT 零写入）
复验对象   = F-1~F-12；重点 ①~⑩
仓库       = /home/szf/dev/gits-cbanking ｜ 分支 recover/PI-ARCH-product-catalog
HEAD       = 9a6dec78046172cd60cb8032f4419905e1958515
```

**独立性三条件（自证）**：① 本轮未参与任何实现、未改任何制品（除本报告）；② 本会话与 TL/前任 holder 执行会话不同主体，且未采信其文书结论（凡引用均回源复算）；③ PSO/ICO 的 interim holder 为项目 Owner（邵钟飞），本人非该二角色。

**Baton 观察（登记项，非停工项）**：`ROLE_BOARD.baton.holder = tech_lead`；`parallel_allowed = [pilot-a1, pilot-a2, pilot-a3, qa-w15]` **不含字面 `qa-w3r2`**（最近槽位为 `qa-w15` = `independent_audit`）。我按 qa-w15 槽位执行（只写 1 个新文件，与 TL 单写者文件零交集）；请下一 holder 把本轮 QA 角色补登记入 `ROLE_BOARD` / `parallel_allowed`。

## 1. 结论总表

| # | 复核点 | 结论 | 一句话 |
|---|---|---|---|
| **F-1** | `board_expression` 与 `gates` 一致 | **ACCEPT** | 83/0/1/84 与 `gates` 复算**逐项一致**，含 `derived_from`/`as_of` |
| **F-2** | 边界判据派生 + N7/N8/P6 真实路径 | **ACCEPT** | M6/M7/L6 均为派生探测；N7/N8/P6 为**真实文件系统**构造 |
| **F-3** | `--plan-gate` P4 双表述 + 真实路径反例 | **ACCEPT** | 判据改为两项 AND；临时文档反例实测被拦下 |
| **F-4** | A-4 M5 显式「不计为覆盖」 | **ACCEPT** | 输出明示「正式 needle 0 / 符号占位 12；不计为覆盖」 |
| **F-5** | A-1 的 A5「**非同源**」 | **NOT_ACCEPTED** | 见 §2.1：与构建路径**仍同 key 同函数**，双极端实验下均 PASS ⇒ 真实路径恒真 |
| **F-6** | 位移落点指向代码行 | **ACCEPT** | `gk17_prodcard_to_rdf.py:33→37 / :35→39`，落点即 `requiresProduct`/`complementsProduct` 值行 |
| **F-7** | D-18/D-19 改号 + 对照 | **ACCEPT** | 两编号存在、历史条目未删 |
| **F-8** | C7 旧日志备份入仓 | **ACCEPT** | `evidence/archive/a3closeout-backup/` 4 件齐备 |
| **F-9** | C5 只数 `PASS ` 行 + 反例全过 | **ACCEPT** | 输出「反例全过 = True」+ `count_semantics` 已落制品 |
| **F-10** | L1 由三元组数派生 | **ACCEPT** | 输出 `T-Box=255 A-Box=39 SIM=290` |
| **F-11** | 派工文口径拆分/精确化 | **ACCEPT** | 待人类-7 已拆分「证据卫生」与「板面复算」 |
| **F-12** | `capability_boundary` | **ACCEPT** | 判定输出含该字段（另见 N-5 健壮性观察） |
| **①** | A5 真独立复算 | **NOT_ACCEPTED** | = F-5 |
| **②** | 位移落点 | **ACCEPT** | = F-6 |
| **③** | 边界派生 + 反例真能失败 | **ACCEPT** | = F-2；诚实边界成立 |
| **④** | M5 不计为覆盖 | **ACCEPT** | = F-4 |
| **⑤** | A-14/A-15/A-16 新增门禁恒真扫描 | **ACCEPT_WITH_CONDITIONS** | A-14/A-16 判据净；**A-15 有 3 处空过滤恒真 + 1 处明细串误读**（N-3）。另：**仓内无 A-18**（见 §2.5） |
| **⑥** | A-13 硬守卫真拒绝 | **ACCEPT** | R1/R2/R3 真实路径拒绝；`apply()` 确实调用两守卫（`:118`/`:137`）。附带 N-2 死子句 |
| **⑦** | 红线 4 项 | **ACCEPT** | `generated/` 0 · 基线 `705578d6…` · KERT 今日 0 写 · 占位命名空间未入受控目录 |
| **⑧** | 本轮 5 处修复 | **ACCEPT** | G6 占位已删（真二次扫描）· P3 恰 4 项 · M4/M5 非空 · Z5 实测派生 |
| **⑨** | 13 条白名单挑战 + 「0 未复核候选」 | **NOT_ACCEPTED** | 见 §2.9：白名单清空后候选 **7 条**；自审仪对 **18/45** 仪器抽取 0 条；按**名称**豁免 |
| **⑩** | A-15 CSV 口数一致 | **ACCEPT** | 281/675 · 100/288 · 355/1398 · 66/148 与 MD 声明**逐项一致** |

**总体**：**2 NOT_ACCEPTED（①/F-5、⑨）+ 1 ACCEPT_WITH_CONDITIONS（⑤）+ 其余 ACCEPT**。
**没有任何一条构成对 `QA_PASS` 或门禁提升的支持**（见 §6）。

---

## 2. 逐项证据（命令 / 退出码 / 原始输出）

### 2.1 ① F-5：A-1 的 A5「独立复算」→ **NOT_ACCEPTED**

**A. 表面要求满足**（显示的行确实是指定文本）：

```text
$ python3 scripts/onto1_disposition_ledger.py --gate
PASS [A5 豁免类判定必须**独立复算**依据（原始 hits 消费证据 = 0；F-5 修正后非同源）] 独立复算 53 行（覆盖 hits 188 处）；违例 0
A-1 处置表闭环：PASS（8/8）                     EXIT=0
$ python3 scripts/onto1_disposition_ledger.py --selftest
--selftest PASS（7/7）                          EXIT=0
```

**B. 源码级判定：A5 与构建路径仍是同一 key + 同一函数 ⇒ 同源。**

- 构建路径 `build_ledger()`（`scripts/onto1_disposition_ledger.py:218-223`）：
  `key = (repo, category, r["disposition"], token, rule_id)` → `hits = idx.get(key, [])` → `consuming = classes.get("ONTOLOGY_CONSUMING", 0)`；`:255-263` **只有 `consuming == 0` 才赋 `EXEMPT_NON_ONTOLOGY_HOMONYM`**。
- A5 判据 `independent_consumption()`（`:313-325`）：key 改为**硬编码** `(repo, category, "HOMONYM_REQUIRES_SOURCE_CHECK", token, rule_id)`，用**同一个** `consuming_class()` 复算。
- 我实测 53 条 EXEMPT 行的 `source_disposition` **全部等于** `HOMONYM_REQUIRES_SOURCE_CHECK` ⇒ 两把 key **完全相同**、hits 列表相同、函数相同 ⇒ `cons` 恒等于构建期那个 `consuming`，而构建期已保证其为 0。

```text
$ python3 -c "...读 a2-disposition-ledger.json..."
EXEMPT 行数 = 53
src_disp 分布 = {'HOMONYM_REQUIRES_SOURCE_CHECK': 53}
stored ontology_consuming_hits 分布 = {0: 53}
hits_total 合计 = 188
全部 src_disp==HOMONYM_REQUIRES_SOURCE_CHECK ? True
全部 stored consuming==0 ? True
```

**C. 决定性实验（双极端输入下 A5 均 PASS ⇒ 判据恒真）**：

```text
$ python3 -c "...monkeypatch consuming_class..."
[实验] consuming_class 恒=ONTOLOGY_CONSUMING 时：豁免行 = 0
       A5 判定 = True
[实验] consuming_class 恒=NEUTRAL 时：豁免行 = 119
       A5 判定 = True
```

`consuming>0`（行被重分类 ⇒ 0 豁免行）与 `consuming==0`（119 豁免行）**两种相反输入下 A5 都 PASS** ⇒ A5 在真实路径**不可能 FAIL**。TL 在裁定书写「消除『判据与被判对象同源 ⇒ 真实路径恒真』的缺陷」，该声明**不成立**。

**D. 附带：对应反例 M3 并未检验 A5。** `cmd_selftest` 的 M3（`:410-412`）改的是 `ontology_consuming_hits`——**恰恰是 A5 已不再读的字段**：

```text
$ python3 -c "...逐项定位 M3 的捕获者..."
现状 FAIL 项 = []
M3 变异后被判 FAIL 的项 = ['A8 counts 与 entries **逐项一致**（防篡改计数）']
M3 是否被 A5 捕获 = False
M3 是否被 A8 捕获 = True
```

⇒ selftest 7/7 的「M3 被捕获」由 **A8（计数一致性）** 提供，与 A5 无关；A5 实际**无任何有效反例**。

**裁定**：`独立复算 53 行/188 处/0 违例` 的**数字**与第一轮 QA 的独立结论一致、结论本身可信；但**判据不具判别力**，「非同源」声明为假 ⇒ **NOT_ACCEPTED**。修法建议：A5 必须使用与构建**不同的证据源或不同的判定函数**（例如独立 RDF marker 表 + 全量 hits 复判，如第一轮 QA 所做），或显式改写为「已由 QA 独立复判，见 ……」的引用式记录，不再自称仪器判据。

### 2.2 ② F-6：位移落点 → **ACCEPT**

```text
$ python3 -c "读 a2-disposition-ledger.json 的 line_drift"
/entries[205]/line_drift[0] = 'scripts/gk17_prodcard_to_rdf.py:33→37（授权变更；该文件共 2 处命中，落点取非注释行）'
/entries[202]/line_drift[0] = 'scripts/gk17_prodcard_to_rdf.py:35→39（授权变更；该文件共 2 处命中，落点取非注释行）'
```

落点核对（真实代码行）：

```text
$ sed -n '36,40p' scripts/gk17_prodcard_to_rdf.py
36 DEFAULT_RELATION_FIELDS = {
37 "prerequisite_product_ids": "requiresProduct",
38 "mutex_product_ids":      "mutuallyExclusiveWith",
39 "complementary_products": "complementsProduct",
40 }
```

`:37` = `requiresProduct` 映射值行、`:39` = `complementsProduct` 映射值行 —— **不再是 docstring 的 `:5`**，对 Wave 2/3 迁移可直接定位。同源修法已在 `verify_evidence()`（`:158-179`）以三引号状态机实现（注释/文档字符串均排除，且记录「该文件共 N 处命中」）。

### 2.3 ③ F-2：边界派生 + N7/N8/P6 真实路径 → **ACCEPT**

```text
$ python3 scripts/onto1_sim_migration_verify.py --gate
PASS [M5 SIM 通道无 needle 泄漏（**无正式 IRI needle 时显式不计为覆盖**）] 正式 needle 0 / 符号占位 12；泄漏 0 处；**不计为覆盖**（理由已登记）
PASS [M6 B6/B8 dry-run **只读性由前后哈希派生**（非写死）] B6_消费者切换: 抽检 3 哈希 2 文件不变=True · B8_内容级重绑（IRI/词表/哈希）: 抽检 3 哈希 2 文件不变=True
PASS [M7 边界**派生**探测（禁止文件不存在 + 无 needle 泄漏）] 探测 2 项；禁止文件命中=无
A-4 SIM 迁移验证：PASS（7/7）      EXIT=0
$ python3 scripts/onto1_sim_migration_verify.py --selftest
PASS [N7 真实路径：禁止文件存在 ⇒ 探测失败] = True
PASS [N8 真实路径：needle 写入 SIM ⇒ 探测失败] = True
--selftest PASS（9/9）             EXIT=0

$ python3 scripts/onto1_l3_load_fixture.py --gate
PASS [L1 三制品均可解析（**由实际三元组数派生**）] 三元组 T-Box=255 A-Box=39 SIM=290
PASS [L6 边界**派生**探测（禁止文件不存在 + SIM 目录规模符合预期）] 禁止文件命中=无；SIM 目录=['product-relations.SIM.ttl']
A-5/L3 加载夹具：PASS（6/6）        EXIT=0
$ python3 scripts/onto1_l3_load_fixture.py --selftest
PASS [P6 真实路径：根域文件存在 ⇒ 探测失败] = True
--selftest PASS（7/7）             EXIT=0
```

**「真能失败」的证据**（源码级，非只读输出）：

- `onto1_sim_migration_verify.py:258-276`：N7 **实际**在临时目录建 `namespaces.json` 并调用**同一个** `boundary_probe(..., extra_files=[_p])`；N8 **实际**写入 `leak.ttl`（内容 = 真 needle）后调 `boundary_probe([...], _sim)`；两者断言 `forbidden_present / needle_leaks` 为真**且** `derived_ok` 为假 ⇒ 真实执行路径上会 FAIL。
- `onto1_l3_load_fixture.py:179-188`：P6 同样实际建文件 + 调真实 `boundary_probe(extra_files=[_p])`。

**诚实边界（我接受）**：N7/N8/P6 覆盖的是**边界探测逻辑**的真实路径，不等于覆盖「全部判据」；这已是 TL 在裁定书 §二 自己声明的余留边界，我确认该声明**准确**。

### 2.4 ④ F-4 / ⑤-部分 / F-10：M5 不计为覆盖、L1 派生 → **ACCEPT**

见 §2.3 输出：`M5` 行明示「正式 needle 0 / 符号占位 12；泄漏 0 处；**不计为覆盖**（理由已登记）」；`L1` 行改用实际三元组数（255/39/290）。两项修复均可复算、无字面量。

### 2.5 ⑤ A-14/A-15/A-16 恒真扫描 → **ACCEPT_WITH_CONDITIONS**

**先澄清**：清单所称 **`A-18` 在仓内不存在**——

```text
$ grep -rn "A-18\|A18" loops/ONTO1-ontology-split/ docs/ scripts/onto1_*.py
loops/ONTO1-ontology-split/memory/HUMAN-ACTIONS-PROMPTS.md:154:⑤ A-18/A-14/A-15/A-16 ...
```

唯一命中即**派工提示词自身**，无对应工作项、无脚本、无门禁。故 ⑤ 实际只能评 A-14/A-15/A-16（+ 我把 `wi_log_hygiene` 一并扫了，见 N-1）。

**A-14（判据净）**：

```text
$ python3 scripts/onto1_migration_worklist.py --gate
PASS [W3 处理口径**非空且逐类计数为正**（原先字典为空时恒真，已修）] 口径种类 3：{... 230, ... 223, ... 9}
PASS [W6 `generated/**` 项数与原因记录**一致**（原为 `>=0` 同义反复，已修）] generated 项 0 / 原因记录 0
A-14 施工清单：PASS（6/6）   EXIT=0
$ python3 scripts/onto1_migration_worklist.py --selftest
PASS [V5 处理口径为空 ⇒ FAIL] 被捕获 = True
PASS [V6 口径计数为非正 ⇒ FAIL] 被捕获 = True
PASS [V7 generated 项数 > 原因记录 ⇒ FAIL] 被捕获 = True
--selftest PASS（8/8）   EXIT=0
```

**A-16（判据净）**：

```text
$ python3 scripts/onto1_kert_registration_request.py --gate
PASS [Z5 **派生**判定未发出且未写入 KERT（KERT 近 1 日写入 = 0 且无发出标记）] 今日写入=0 件（判据）；滚动 24h=23 件（披露，含 poc 构建产物）；工作树既有改动=80（披露）；发出标记=无
A-16 KERT 请求草案：PASS（6/6）   EXIT=0；--selftest PASS（6/6）
```

**A-15（发现 3 处空过滤恒真 + 1 处明细串误读）**：

```text
$ python3 scripts/onto1_breakpoint_execution_pack.py --gate
PASS [X2 每份均存在且含**不构成出口选择**声明] 存在 1/12        ← 明细串误读（见 N-3b）
A-15 出口执行包：PASS（6/6）   EXIT=0；--selftest PASS（6/6）
```

- **X3/X4/X5 为 `all(... for … if <后缀过滤>)` 形态**：`scripts/onto1_breakpoint_execution_pack.py:148/152/156`。过滤器命中 0 个时 `all([]) == True`。实证：

```text
$ python3 -c "t={'…-option-B.md':…}; print(all(… for p,t in t.items() if p.endswith('option-A.md')))"
X3 对无 option-A.md 的 texts 求值 = True
（过滤器命中 0 个 ⇒ all([]) == True ⇒ 判据空转）
```

  当前**不构成假绿**（X1 已断言三出口集合 == {A,B,C} 且 12 份，A 包必在位），属**潜在空转**，应加「过滤器命中数 > 0」护栏。

**裁定**：A-14/A-16 判据**接受**；A-15 的 X2 判据本身健全（`ok_files and all(disclaimer in t …)`），但 **X3/X4/X5 存在空集恒真形态**且明细串误导 ⇒ 本项 **ACCEPT_WITH_CONDITIONS**。

### 2.6 ⑥ A-13 迁移器硬守卫 → **ACCEPT**

```text
$ python3 scripts/onto1_migration_runner.py --selftest
PASS [R1 真实路径：目标出沙箱 ⇒ 拒绝] 被拒绝 = True
PASS [R2 真实路径：手改 specs 路径 ⇒ 拒绝] 被拒绝 = True
PASS [R3 真实路径：沙箱设在仓内 ⇒ 拒绝] 被拒绝 = True
PASS [R4 端到端：沙箱内真改写 198 文件且全部落在沙箱] = True
PASS [R5 真实路径：写入全部在沙箱、仓内零写入] = True
--selftest PASS（11/11）   EXIT=0
```

**守卫真的被生产路径调用**（不是装饰）：

```text
$ grep -n "def apply\|guard_sandbox(\|guard_target(" scripts/onto1_migration_runner.py
96:def guard_sandbox(...)        103:def guard_target(...)
117:def apply(sandbox, limit=0):
118:    guard_sandbox(sandbox)        ← 入口即校验
137:        guard_target(dst, sandbox) ← 逐目标校验
```

R1/R2/R3 均为**真实文件系统**构造（临时目录 + 真实 `guard_target`/`guard_sandbox` + 期望 `PermissionError`，`:238-268`）⇒ 三项拒绝**真发生**。

**附带（计入 N-2，不改变本项结论）**：`R4` 的 `ok_e2e`（`:276`）含死子句 `… or True`，但同一断言的兄弟合取项 `ok_inside`（`:277`）**独立**实现了「全部落在沙箱」，故**未形成假绿**。

### 2.7 ⑦ 红线 → **ACCEPT**

```text
$ git status --short -- generated/            →（空）⇒ 改动 0
$ sha256sum specs/semantic/gits-core.owl.ttl  → 705578d6324abd0c1bd2bd…38d00   ← 与声明一致
$ find . -name "namespaces.json"              →（空）⇒ 未建根域
$ grep -rn "rehearsal.sim.local" specs/ generated/  →（空）⇒ 演练占位命名空间未入受控目录
$ find /home/szf/dev/Leibniz-KERT -newermt "2026-09-21 00:00" -type f | wc -l → 0
KERT 最新 mtime = 2026-09-20+23:57:33 /home/szf/dev/Leibniz-KERT/poc/.../target/classes/application.yml
```

`git status --short -- specs/ generated/` 仅出现 `specs/` 项（`products.ttl`、`UNRESOLVED.json` 修改 + `projection-config.json`、`sim/` 未跟踪），**无 `generated/` 项** ⇔ 与第一轮 QA 已 ACCEPT 的 C-2/D2 SIM 整改口径一致。

### 2.8 ⑧ 本轮（判据强度自审）5 处修复 → **ACCEPT**

```text
[G6]  $ python3 scripts/onto1_c2_consumer_scan.py --gate
PASS [G6 扫描幂等（两次结果一致）] b4130e8e8f0dadac == b4130e8e8f0dadac     EXIT=0
  源码：scripts/onto1_c2_consumer_scan.py:207-224 —— 占位已删；`d=write_scan()` 后 `d2=scan()` 真跑第二次，
  以 h1/h2 比对再 `rows.insert(5, …)`。✅ 真二次扫描

[P3]  $ python3 scripts/onto1_construction_plan.py --gate
PASS [P3 合同候选**恰 4 项且全部** NOT_EFFECTIVE（空集不得视为通过）] 候选 4 项；非 NOT_EFFECTIVE = 无
      --selftest PASS（11/11）                                                EXIT=0

[M4/M5] $ python3 scripts/onto1_migration_runner.py --gate
PASS [M4 改名通道**非空且**每条均带受限正则与排除清单字段（空集不得视为通过）] 7 条（声明 7）
PASS [M5 退役通道**非空且**明确不得改名并要求只读期（空集不得视为通过）] 1 条（声明 1）

[Z5]  $ python3 scripts/onto1_kert_registration_request.py --gate
PASS [Z5 …] 今日写入=0 件（判据）；滚动 24h=23 件（披露…）；发出标记=无
```

四项均**非空集自证**，且各有对应反例（V5/V6/V7、T1~T5、11/11、P3 由 `M6 分类被篡改` 覆盖）。**ACCEPT**。

### 2.9 ⑨ 13 条白名单挑战 → **NOT_ACCEPTED**

**A. 「0 条未复核候选」完全由白名单产生（自我满足的实证）**：

```text
$ python3 -c "...import 自审仪；先 scan()，再置 REVIEWED={} 后 scan()..."
[白名单生效时] flagged_total = 0  by_flag = {}
[清空白名单后] flagged_total = 7  by_flag = {'DECLARED_ONLY': 7}
   - ['DECLARED_ONLY'] onto1_breakpoint_option_rehearsal.py : 143 ::
   - ['DECLARED_ONLY'] onto1_kert_registration_request.py : 146 ::
   - ['DECLARED_ONLY'] onto1_l1_prep.py : 205 ::
   - ['DECLARED_ONLY'] onto1_l3_load_fixture.py : 125 ::
   - ['DECLARED_ONLY'] onto1_scenario_readiness.py : 240 ::
   - ['DECLARED_ONLY'] onto1_sim_rehearsal.py : 332 ::
   - ['DECLARED_ONLY'] onto1_sim_rehearsal.py : 333 ::
```

⇒ 「0 条未复核候选」= 白名单把 7 条唯一的 high/medium 候选**逐条消掉**后的残值。在**白名单作者 = 被审代码作者 = 提出"0 候选"结论者**的前提下，该数字**不具备外部证明力**（TL 已以此立 D-20 不登记为门禁；但本轮清单仍把它当复核依据 ⇒ 我判定不可采信）。

**B. 覆盖空洞：18/45 仪器抽取到 0 条判据**：

```text
$ python3 -c "...统计 check-strength-audit.json..."
仪器数 = 45   抽取到的判据三元组总数 = 201
全部 flags 计数（含 info）= {'REVIEWED_OK': 13, 'BRANCH_CONCLUSION': 6, 'MUTANT_SCOPE': 20}
checks_total==0 的仪器数 = 18
  ['onto1_attribution_rebuild.py','onto1_check_strength_audit.py','onto1_consumer_scan_tests.py',
   'onto1_cq_fixtures.py','onto1_d2_normalization_pack.py','onto1_d4_pack.py',
   'onto1_evidence_board_check.py','onto1_gate_log.py','onto1_log_hygiene.py',
   'onto1_namespace_collision_check.py', …]
```

成因（我读源码定位，三类）：
1. **2 元组判据被丢弃**：`extract_checks_in_func` 要求 `len(el.elts) >= 3`（`scripts/onto1_check_strength_audit.py:117`）⇒ `onto1_log_hygiene.py` 的 `("H1", cond)` 四元组全部不可见（**该仪器含 N-1 恒真**）。
2. **dict 式判定不可见**：`onto1_namespace_collision_check.py:596-641` 用 `report["checks"]["C-1b"] = {...}` ⇒ 注册门禁整机不可见。
3. **失败列表式判定不可见**：`onto1_d4_pack.py:121+` / `onto1_cq_fixtures.py:134+` / `onto1_evidence_board_check.py:75+` 用 `failures.append("string")` ⇒ 不可见（而 `all([])`/空失败列表**恰是这套写法的天然恒真形态**）。
4. **条件预计算为变量时不可见**：审查对象仅取元组第 2 元素表达式；`ok_files = all(...)`、`ok_e2e = … or True` 这类**赋值语句**不进入审查域（N-2 即躲在此处）。

**C. 白名单按「名称」匹配，泛化名可吸收新增判据**：`if c["name"] in REVIEWED.get(p.name, {})`（`:201`）。`onto1_c2_fix_verify.py` 用 `"V1"/"V2"/"V3"` 作键，而 REVIEWED_OK 13 条中 V1 占 2 处、V2 占 2 处、V3 占 2 处 ⇒ **同名多处自动获豁免**；后续任何新增的 `V1/V2/V3` 判据会被静默豁免。

**D. 逐条理由挑战（13 条 / 10 个不同判据名）**：

| 判据（文件:行） | TL 理由 | 我的核验 | 理由成立? |
|---|---|---|---|
| `breakpoint_option_rehearsal.py:143` C-3 出口 A 相邻名保持 | 读 `all_adjacent_preserved`，由沙箱内**逐文件前后计数比对**派生；另有 K7/K8 | `:64/85/89` 实证：`a_preserved` 初值 True，仅在**相邻名被改坏或 bleed 计数变化**时置 False ⇒ 确为派生 | **成立** |
| `c2_fix_verify.py:65/67` V1 | try 内解析成功才置 True；异常即 False 并**提前返回** ⇒ fail-closed | `:60-68` 实证：`("V1", True, …)` 在三文件 `_parse` 成功之后；`except` 分支 `("V1", False …)` + `return res` | **成立** |
| `c2_fix_verify.py:75/79` V2 | if/else 分支结论 | `:70-79` 实证：else 分支追加 False | **成立** |
| `c2_fix_verify.py:90/92` V3 | if/else 分支结论 | `:82-94` 实证：`if typed_after and not bad_types` else 追加 False | **成立** |
| `kert_registration_request.py:146` Z5 | 由 `derive_write_state()` **实测派生** | gate 输出「今日写入=0 件（判据）」；且**披露**滚动 24h=23 件与工作树 80 项 | **成立**（但口径 = 日历日，弱于「未写入」，已如实披露） |
| `l1_prep.py:205` L2 | 交叉比对**两个独立制品**；该值由 D3 台账钉定 | `:36-39` `ns` 读 `projection-config.json`；`sk_ns` 读 `l1-namespace.json` ⇒ 交叉比对**真实**。但 `"PROVISIONAL_SIM_LEGACY_NAMESPACE"` 是**代码字面量**，运行期**未**校验 D3 台账 | **部分成立**（后半句无运行期依据） |
| `l3_load_fixture.py:125` L1 | 读 `parse.ok`，由 `load_all()` 实际解析计数派生 | gate 输出实测 255/39/290 | **成立** |
| `scenario_readiness.py:240` S4 | 沙箱预演逐文件实际计数；另配 U7 | `:219` `reh = rehearse()` **in-process 真跑**；`:172` `quarantine_untouched` 由计数得出；`:302` U7 在 | **成立** |
| `sim_rehearsal.py:332` M5 | 由 `rehearse_one()` 对每个副本**实际 rdflib 解析** | `:303` `all_parsed = all(v["parse_ok"] for v in verified)`，`verified` 来自本进程真跑；`M4` 要求 `rehearsed_files>=5` ⇒ 非空 | **成立** |
| `sim_rehearsal.py:333` M6 | 由演练后文件内容**实际比对**退役名 | `:304` `all_retired_untouched = all(v["retired_untouched"] …)`，同上 | **成立** |

⇒ 10 条中 **9 条成立、1 条部分成立**（`l1_prep` L2）。**理由本身基本可信**；被否的是「0 候选」这一**结论**（A/B/C 三项）。

**裁定**：本项 **NOT_ACCEPTED**。修法建议：① 把审查域从「元组第 2 元素」扩展到「条件变量赋值语句 + 2 元组 + `failures.append` 谓词」；② 白名单键改为 `文件:判据名:判据指纹`（含条件表达式哈希），禁止泛化名；③ 报告层同时输出 `checks_total` 与 `instruments_uncovered`，禁止用「0 条」代替「未覆盖」。

### 2.10 ⑩ A-15 全量逐文件 CSV 与 MD 摘要口数一致性 → **ACCEPT**

```text
$ python3 -c "...csv.DictReader 逐文件统计..."
B-1-Customer-option-A-FULL.csv 文件行 = 281  命中合计 = 675
B-2-Product-option-A-FULL.csv  文件行 = 100  命中合计 = 288
B-3-Skill-option-A-FULL.csv    文件行 = 355  命中合计 = 1398
B-4-Asset-option-A-FULL.csv    文件行 = 66   命中合计 = 148

$ grep -n "FULL.csv" …/A/B-*-option-A.md
B-1…md:67:**全量清单**：…B-1-Customer-option-A-FULL.csv（281 个文件 / 675 处命中，含逐条签字位）
B-2…md:68:**全量清单**：…B-2-Product-option-A-FULL.csv（100 个文件 / 288 处命中，含逐条签字位）
B-3…md:62:**全量清单**：…B-3-Skill-option-A-FULL.csv（355 个文件 / 1398 处命中，含逐条签字位）
B-4…md:63:**全量清单**：…B-4-Asset-option-A-FULL.csv（66 个文件 / 148 处命中，含逐条签字位）
```

**文件口数与命中口数四项全部一致**；CSV 含 `已核（签字）` / `日期` 列（逐条签字位）。MD 正文的「前 40」表为**显式摘要**（标题写明「按命中数降序，前 40」），与全量 CSV 不冲突。**ACCEPT**。

### 2.11 F-1 / F-7 / F-8 / F-9 / F-10 / F-11 / F-12

```text
[F-1] gates 总数 = 84  status 分布 = {'pass': 83, 'inconclusive': 1}
      board_expression = {'PASS': 83, 'FAIL': 0, 'PENDING_EXTERNAL_AUTHORITY': 1, 'total': 84}
      与 gates 一致 = True      非 pass 项 = ['wi_a4_namespace_collision']
      derived_from = EVIDENCE.json.gates   as_of = 2026-09-21（采纳「按建议办」批次后）   → ACCEPT

[F-7] $ grep -n "^### D-" memory/TL-DECISIONS-W-1.md
      234:### D-18｜证据文件操作纪律（**原误用编号 D-14；依 QA F-7 改号为 D-18**，历史条目保留）
      246:### D-19｜门禁尝试预算改为**按 revision 纪元计数**（**原误用编号 D-15；依 QA F-7 改号为 D-19**）
      275:### D-20｜判据强度自审仪**不登记为门禁**
      （历史 D-14:123 / D-15:104 条目未删）                                        → ACCEPT

[F-8] $ ls evidence/archive/a3closeout-backup/    → 4 件（collision gate/selftest + refalign gate/selftest）  → ACCEPT

[F-9] $ python3 scripts/onto1_a3_closeout.py --gate
      PASS [C5 计数口径：实测 = 声明（逐项）**且反例全过**] 不一致 = 无（7 项）；反例全过 = True
      :128 count_semantics = 用例数 = `PASS ` 开头的行数；含任何 `FAIL ` 行则 all_passed=False 且 C5 FAIL → ACCEPT

[F-12] $ python3 scripts/onto1_signature_verify.py --verify docs/review/ARCH-ONTO-2026-001-rereview-package/14-书面复审决议签署页.md
      {"verdict":"INCOMPLETE","record_kind_allowed":"OWNER_REVIEW",
       "record_kind_forbidden":["ARCHITECTURE_COMMITTEE_APPROVED"],"seats_filled":0,"v8_verdict":"FAIL",
       "capability_boundary":"形式校验：仅验『姓名非空且互异 + 已签字已署期』；**不**验证四人为真实独立自然人 ⇒
                             本判定**不得**作为独立性成立的证据", … }                       → ACCEPT（另见 N-5）
```

---

## 3. 新发现（本轮独有；均为我亲自复现）

### N-1（**高**）`wi_log_hygiene` H4 为恒真判据（注册门禁，4 条判据中 1 条死）

```text
scripts/onto1_log_hygiene.py:135
  ("H4 白名单在案文件确实存在", all((EV_DIR / f).is_file() for f in allow) or True),
                                                             ^^^^^^^^ 恒真

$ python3 -c "print(all(False for f in ['a','b']) or True, all(False for f in []) or True)"
True True
```

```text
$ python3 scripts/onto1_log_hygiene.py --gate
PASS [H1 …] DESIGN  PASS [H2 …] PASS [H3 …] PASS [H4 白名单在案文件确实存在]     EXIT=0
$ python3 scripts/onto1_log_hygiene.py --selftest
--selftest PASS（5/5）      ← M1~M5 均不涉及 H4
```

H4 **在任何输入下都不可能 FAIL**，其声称的「白名单在案文件确实存在」**未被检验**；selftest 5/5 亦无覆盖。与 F-9/F-10 同类（判据失真），且**自审仪对该仪器抽取 0 条**（§2.9-B 成因 1）⇒ 逃过自审。**建议**：去掉 `or True`，并补「白名单指向不存在文件 ⇒ FAIL」反例。

### N-2（**低**）A-13 `R4` 含死子句 `or True`（有兄弟合取项兜底 ⇒ 非假绿）

```text
scripts/onto1_migration_runner.py:276
  ok_e2e = bool(res["applied"]) and all(str(sb) in _a["file"] or True for _a in res["applied"])
                                                    ^^^^^^^^ 使 all(...) 恒真
:277  ok_inside = all(str((sb / _a["file"]).resolve()).startswith(str(sb.resolve())) …)
:278  fails += 0 if (ok_e2e and ok_inside) else 1
```

「全部落在沙箱」由独立的 `ok_inside` 真正承担 ⇒ **未产生假绿**；但该 `or True` 使 `ok_e2e` 退化为 `bool(applied)`，与门禁文案「且**全部**落在沙箱」不符，属同类反模式残留，建议删。

### N-3（**中**）A-15 判据与明细串问题

- **N-3a**：X3/X4/X5 为 `all(… for … if <后缀>)`，过滤器落空即 `all([])==True`（§2.5 已实证）。建议加「过滤器命中数 > 0」。
- **N-3b**：X2 明细串 `f'存在 {int(ok_files)}/{len(packs)}'` —— `ok_files` 是 **bool**，`int(True)==1` ⇒ 打印 `存在 1/12`，**读起来像"12 份里只有 1 份存在"却判 PASS**。判据本身健全（`ok_files and all(disclaimer in t …)`），但该串属「口径不精确」（F-11 同类）。建议改打印实际存在份数。

### N-4（**中**）自审仪覆盖与白名单机制（即 §2.9 A/B/C）

已在 §2.9 详述：18/45 仪器零抽取；审查域不含「条件变量赋值」；白名单按名称匹配且含泛化键 `V1/V2/V3`。

### N-5（**低**）`onto1_signature_verify.py --verify <不存在路径>` 抛未捕获 `FileNotFoundError`

```text
$ python3 scripts/onto1_signature_verify.py --verify docs/review/nonexistent.md
  File "/usr/lib/python3.10/pathlib.py", line 1119, in open
FileNotFoundError: [Errno 2] No such file or directory: 'docs/review/nonexistent.md'
```

与 `wi_w15_a3_acceptance` 已确立的「缺文件 ⇒ **具名 FAIL**（不得 Traceback）」口径不一致（崩溃 ≠ FAIL）。不影响 `--gate`/`--selftest`，属健壮性一致性问题。

### N-6（**信息**）清单所引 `A-18` 无对应工作项

见 §2.5；建议下一轮清单在引用前先与 `LOOP.yaml.gates` / 脚本集合对齐。

---

## 4. 我这一轮的副作用（自证无漂移）

**已登记证据未动**：

```text
登记门禁 = 84   证据哈希失配/缺失 = 0   ← 84/84 的 output_sha256 与磁盘一致
```

**会重写自身制品的门禁，我实测幂等**：

```text
$ 连续三次 python3 scripts/onto1_c2_consumer_scan.py --gate 后比对制品哈希
550dd34e1db4a691 / 550dd34e1db4a691 / 550dd34e1db4a691 ⇒ 幂等 = YES
$ sha256sum evidence/prep/a2-disposition-ledger.csv
136e9de43cbb11fa20857abcf6004b5adb9749a00297e4a15b09a36c7317fd4a   ← 与第一轮 QA 基线逐字相同
```

**如实披露**：`evidence/c2-consumer-scan.json` 当前为 `550dd34e…`，与第一轮 QA 记录的 `6144c8bd…` **不同**；该差异**先于我的执行**（`EVIDENCE.json` 中 `wi_c2_consumer_scan` 的 `executed_at = 2026-09-21T15:17:56Z`，属 TL 采纳批次的重记），且我的三次重跑**逐次相同**（幂等）。该制品枚举仓内文件，随仓内新增证据日志而合法变化。

其余：我**未**执行 `onto1_a3_closeout.py --build`（会覆盖 4 份 a3fix 日志）；除本报告外**未新增/删除任何文件**；**未**对 `/home/szf/dev/Leibniz-KERT` 做任何写入；**未**改任何 `specs/**`、`generated/**`、脚本、证据。

---

## 5. 未覆盖 / 边界声明

- 本轮**只做** F-1~F-12 修复复核与 ①~⑩，**不重复**第一轮已 ACCEPT 项（C-2 修复正文、D2 分流、A-7 形式校验、红线 12 条关系等）。
- **未复验**：`docs/**` 与 KERT 侧文档语义正确性；A-6（GK17 侧重跑）；B/C 族外部依赖（D1/D2/D3/D4、KERT 写权限、委员会）。
- 我**未**对既有 84 门禁的 `status` 作任何改判；`wi_a4_namespace_collision` 仍为 `inconclusive`（`C-1b` 待 D3）。
- 与 `specs/**` 冲突时以 `specs/**` 为准；本报告引用均给 `文件:行` 或 sha256。

## 6. 关于 `QA_PASS`

**我不得、也未记录 `QA_PASS`。** 客观理由（非我的裁量）：

1. 板面仍有 **1 项 `inconclusive`**（`wi_a4_namespace_collision`，`exit=3`，`C-1b` 待 D3 签署根域）；**未判定 ≠ 通过**。
2. `LOOP.yaml.gate_state.current` 仍为 **`RETURN_TO_HLD`**；Wave 0 及以后仍 `BLOCKED`。
3. 本轮我判 **①/F-5（A5 判据恒真）与 ⑨（自审仪 0 候选不可采信）为 `NOT_ACCEPTED`**；⑤ 为 `ACCEPT_WITH_CONDITIONS`。
4. `wi_log_hygiene` 的 **H4 恒真**（N-1）为**注册门禁**中的失真判据，构成对「变异复验已证明判据非空转」这一声明的新反例。

**建议（均为建议，非结论）**：
① F-5 的 A5 改用与构建**不同的证据源/判定函数**，或降级为「引用 QA 独立复判」的记录项，不再自称仪器判据；
② 删除 `onto1_log_hygiene.py:135` 的 `or True` 并补反例；删除 `onto1_migration_runner.py:276` 的死子句；
③ 自审仪的审查域扩展到「条件变量赋值 + 2 元组 + 失败列表式」，白名单键改为「文件:判据名:条件指纹」，报告层强制输出 `checks_total` 与未覆盖仪器数；
④ A-15 的 X3/X4/X5 加「过滤器命中数 > 0」护栏，X2 明细串改打印实际份数；
⑤ `--verify` 缺文件改为具名错误（与 D-11「崩溃 ≠ FAIL」一致）；
⑥ 本轮清单所引 `A-18` 在仓内无对应工作项，建议清单与门禁表先对齐。

---

**报告完** ｜ 生成者：`independent_qa`（第二轮）｜ 唯一写域：本文件 ｜ 未代签任何文书、未改任何制品、未记 `QA_PASS`
