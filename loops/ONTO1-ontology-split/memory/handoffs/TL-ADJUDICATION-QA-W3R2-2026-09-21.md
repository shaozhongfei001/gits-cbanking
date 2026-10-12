# TL 裁定｜QA 第二轮（W3R2）复核结果处置

> 受理：全局 TL（`tech_lead`）｜2026-09-21
> 被裁对象：`memory/handoffs/INDEPENDENT-QA-W3R2-2026-09-21.md`
> **SHA-256 核验**：声明 `96ecf2dce0173dad923f313d14e7aff8af592964cf98825c95612cb3c329cdff` ↔ 实测**逐字一致**（33,749 B）
> **处置原则**：① 不采信转述，每条都回现场核验；② 反例必须被**它针对的判据本尊**捕获；
> ③ 判据凡在真实路径恒真/空转 ⇒ **按缺陷处理，不按口径放宽**；④ 修不了或修不完的 ⇒ **具名登记，不假装已绿**。

---

## 一、逐项裁定

| 项 | QA 结论 | TL 裁定 | 处置 | 复跑证据 |
|---|---|---|---|---|
| F-1 | ACCEPT | 采纳 | 无 | `board_expression` = `EVIDENCE.json.gates` 复算一致 |
| F-2 / ③ | ACCEPT | 采纳 | 无 | — |
| F-3 | ACCEPT | 采纳 | 无 | — |
| F-4 / ④ | ACCEPT | 采纳 | 无 | — |
| **F-5 / ①** | **NOT_ACCEPTED** | **接受否决** | **已重修 A5**（见 §二） | `wi_a2_disposition` **9/9**、`--selftest` **9/9** |
| F-6 / ② | ACCEPT | 采纳 | 无 | — |
| F-7~F-12 | ACCEPT | 采纳 | 无 | — |
| **⑤** | ACCEPT_WITH_CONDITIONS | **接受条件** | **已修 X2~X5**（N-3） | `wi_a15_breakpoint_execution_pack` 6/6 + `--selftest` 6/6 |
| ⑥ | ACCEPT | 采纳 | 无 | — |
| ⑦ | ACCEPT | 采纳 | 无 | — |
| ⑧ | ACCEPT | 采纳 | 无 | — |
| **⑨** | **NOT_ACCEPTED** | **接受否决** | **审器 v2 重修 + 覆盖 fail-closed**（见 §三） | 自审 v2：**226 条可审判据 / 15 候选 / 13 未审仪器**（不再是「0 条」） |
| ⑩ | ACCEPT | 采纳 | 无 | 281/675 · 100/288 · 355/1398 · 66/148 逐项一致 |

**结论**：**8 ACCEPT + 1 条件接受 + 2 否决**，两项否决**均成立**，已修并有复跑证据。

## 二、F-5 否决的机理（比转述更严重）与我方修法

**机理（我复核后确认并加重）**：不是"用了同一个 key"这么简单，而是**构造性同义反复**——
`exempt_rows` 是**构建路径用 `consuming_class()` 判定**产生的（文件级"是否含本体字面量"→ 0 消费 ⇒ 判豁免），
而 A5 又用**同一个函数**复核同一批行。于是：
1. 二者恒等 ⇒ 除非文件在同一进程内变化，A5 **不可能 FAIL**；
2. 若把 `consuming_class` 恒置 `ONTOLOGY_CONSUMING` ⇒ 构建路径把**所有行**都判为有消费证据 ⇒ `exempt_rows` 变**空** ⇒ A5 **空转给绿**；
3. 恒置 `NEUTRAL` ⇒ 所有豁免行消费数 0 ⇒ 依旧绿。
⇒ QA 的"任何输入下都不可能 FAIL"**成立**。（附带：原反例 M3 改的是 A5 已不读的字段，真正的捕获者是 A8。）

**修法（三层，缺一不可）**：
| 层 | 做法 | 为何有判别力 |
|---|---|---|
| **行级独立信号** | A5 改为审**该行的 `文件:行` 证据本身**（`line_consuming()`：该行是否含本体字面量/RDF 标记；证据行不可定位 ⇒ 违例，fail-closed） | 与构建路径的**文件级**判定不同源；证据行可被变异 ⇒ **可 FAIL** |
| **双侧对照** | 统计命中文件总体中被判「消费」与「中性」的个数，要求**两侧均非零** | 分类器**任一方向恒置**都会让一侧归零 ⇒ A5 FAIL（直接覆盖 QA 的决定性实验） |
| **非空转** | 豁免集合为空 ⇒ A5 **FAIL**（"空转视为失败"，与 R4 同法） | 消灭"把输入清空即通过"的路径 |
| 新增 **A9** | 台账 `source_disposition` 必须与**原始扫描**记录一致（独立键 `(repo, token, rule_id)`，**不预设处置值**） | 独立于构建路径的第二把尺子 |

**反例改造（关键）**：`run()` 从「至少一项 FAIL」改为「**必须被指定判据本尊捕获**」：
`M1→A3 · M2→A2 · M3→A5（重定位：把豁免行证据指向本体消费行）· M4→A1 · M5→A6 · M6→A4 · M7→A5（豁免集合清空）· M8→A9（篡改 source_disposition）`。
⇒ 从此「捕获者不是被判对象」这类问题**会被反例集直接暴露**。

## 三、⑨ 否决：审器 v2 的重修与**诚实覆盖边界**

**QA 的两个致命点（均确认）**：
1. **覆盖率不 fail-closed**：原版对 18/45 仪器抽不到判据却报「0 条候选」——把"没审到"当"没问题"；
2. **白名单可自我满足**：按**名称**匹配 + 含泛化键（`V1/V2/V3`）；清空白名单后仍有 7 条候选 ⇒「0」完全由白名单产生（白名单作者 = 被审代码作者 = 出结论者）。

**v2 修法**：抽取扩到 **2/3 元组 · dict 式 · 字符串式 · 预计算变量（回溯源表达式）**；
**未抽到判据的仪器一律 `NOT_AUDITED`（high）**，不得静默通过；白名单改为
**（仪器, 判据名, 条件表达式 sha12）三元匹配**并**冻结哈希**（`check-strength-review-hashes.json`），
条件变更 ⇒ `REVIEW_STALE` 需重新复核。

**v2 的诚实输出（不再有「0 条」这种结论）**：
```
仪器 45 个 · 可审判据 226 条 · 候选 15 条 · 未审仪器 13 个
TAUTOLOGY_CONST 1（onto1_c2_generator_check:57 G0 —— 位于失败分支，属 fail-closed 结论，非假绿）
DECLARED_ONLY  1（onto1_sim_projection:142 G4 —— 文本存在性校验，保留观察）
NOT_AUDITED   13
```

**覆盖边界（声明，不是通过）**：这 13 个仪器用**「违规清单 + 退出码 / verdict」**形态判定
（例：`onto1_reference_alignment_check.py` 的 `findings.append({"code":…})`、`onto1_namespace_collision_check.py` 与
`onto1_evidence_board_check.py` 的 `return 2` 分支），**不在本审器的检查表模型内**。
⇒ 它们**仍然未被本审器审过**。要真正覆盖，需**第二分析器**（"违规点分析"：每个违规点的触发条件是否可复现、是否可达）
或把判定改造成元组式。**本轮不冒充已覆盖。**

## 四、新发现处置（QA 自审仪未捕获，均由 QA 报出）

| # | 严重度 | 内容 | 处置 | 证据 |
|---|---|---|---|---|
| **N-1** | **高** | `onto1_log_hygiene.py:135` H4 = `all(...) or True` **恒真** ⇒ **已登记门禁含 1 条死判据**，且 `--selftest` 5/5 未覆盖它 | 已去 `or True` + 加非空守卫 + 派生缺件明细；**修复后立刻真失败**：白名单 53 件中 **21 件指向不存在文件** ⇒ 已剪除并留历史（`non-gate-log-allowlist-history.json`），现存 32 件 | `wi_log_hygiene` PASS；`--selftest` 5/5 |
| **N-2** | 低 | `onto1_migration_runner.py:276` R4 死子句 `or True` | 已删（沙箱内包含性由 `ok_inside` 承担） | `wi_a13_migration_runner` 9/9 |
| **N-3** | 中 | A-15 X3/X4/X5 **空过滤恒真**（`all(... if endswith("option-A.md"))`）；X2 明细 `int(bool)` 误读为「存在 1/12」 | 三处加**非空守卫**（==4）+ 明细改为**派生计数** | `wi_a15_breakpoint_execution_pack` 6/6 + 6/6 |
| **N-5** | 低 | `--verify <不存在路径>` 抛 Traceback（与「崩溃 ≠ FAIL」口径冲突） | 改为具名拒绝 `INPUT_MISSING` / `ONTOLOGY_INPUT_MISSING` / exit 2；并入自检 | 实测 `exit=2`，无 Traceback |
| **N-6** | 信息 | 派工提示词所引 **A-18 在仓内不存在** | 已更正为 **A-13~A-17** 并标注系误引 | `HUMAN-ACTIONS-PROMPTS.md` 待人类-7 ⑤ |

**21 件陈旧白名单的归因（如实）**：全仓 `find` 搜索 **0/21 命中**、`/tmp/logbak-*` 备份内亦无记录
⇒ **无法归因为 D-18 清理**（无备份即无删除痕迹）。已在历史文件中标注「无备份记录 ⇒ 需人工确认」，
**不假装查明**；剪除依据仅为"文件不存在"这一事实本身。

## 五、QA 自我披露项的处理（c2 制品哈希差异）

QA 如实披露：`evidence/c2-consumer-scan.json` 现为 `550dd34e…`（第一轮为 `6144c8bd…`），并说明差异先于其执行。
**TL 复核结论**：差异来自制品的 `regression_log_index`（9 项，含日志文件名与门禁状态——
随门禁重记与 D-18 日志清理而**合法变化**）；**实质字段逐项未变**：
`instances.count_live = 13` · `wrong_class_assertions = 0` · `breaking_refs = 0`。
**我方幂等自证**：连续三次重跑 `--gate` ⇒ 制品哈希 `550dd34e1db4a691` **三次相同** ⇒ 与 QA 的观察一致（差异非其引入）。

## 六、写域与边界声明

- **未改 QA 报告一个字节**（受理前后哈希一致：`96ecf2dc…`）；
- 本轮我改写的对象：`scripts/onto1_{disposition_ledger,log_hygiene,migration_runner,breakpoint_execution_pack,signature_verify,check_strength_audit}.py`、
  `evidence/non-gate-log-allowlist.json`(+ 历史)、`memory/HUMAN-ACTIONS-PROMPTS.md`（N-6）、`memory/ROLE_BOARD.yaml`（补 `qa-w3r2`，**QA 的请求，属 TL 写域**）；
- **未记** `QA_PASS`；**未**提升任何门禁；**未**代签；**未**触碰 `generated/`、KERT、D3 决策物。

## 七、板面与红线（受理后）

```
板面：84 = 83 pass / 1 PENDING_EXTERNAL_AUTHORITY（不变；唯一非 pass = wi_a4_namespace_collision，C-1b 待 D3）
重记：wi_a2_disposition(+st) · wi_log_hygiene(+st) · wi_a13_migration_runner(+st) · wi_a15_breakpoint_execution_pack(+st) · wi_a7_signature_verify(+st) —— 全部直接通过（D-19）
current = RETURN_TO_HLD · Wave 0+ BLOCKED · QA_PASS 未记录 · independent_qa = report_received
```

## 八、遗留（具名，不含糊）

1. **13 个 `NOT_AUDITED` 仪器**：需第二分析器或改造判定形态 —— **本轮未覆盖，登记为跟进项**（建议由下一任 holder 或 QA 第三轮承接）；
2. **自审仪不登记为门禁**（D-20 不变）；但**批次纪律**成立：本轮仪器改动已附自审结果；
3. `onto1_c2_generator_check:57 G0` 与 `onto1_sim_projection:142 G4` 两条候选保留观察（前者为失败分支 fail-closed 结论，后者为文本存在性校验），**未并入白名单**（避免泛化键问题重演），列为观察项。
