# PKG-A3｜HANDOFF（W-1.5 两处门禁小修：F1 / F2 / F3 ＋ TL 追加硬验收）

| 项 | 值 |
|---|---|
| 交付人 | Feature Pilot `pilot-a3` |
| 交付对象 | TL（本 Loop Baton holder）→ 用于 AU-1~AU-7 审计与 `record_gate.py` 记账；`qa-w15` 复核对账 |
| 版本 | **V2（含 TL 追加硬验收 C-3 / C-4 / C-6 / C-7 / C-8；只增补，未重做已通过的 F-1 / F-5 `:13`）** |
| 计划 / 迭代 | `memory/waves/PKG-A3-PLAN.md`、`memory/waves/PKG-A3-ITER.md`（含 Attempt 1/2/3 与 S-1~S-3 自愈记录） |
| 前后对照证据 | `loops/ONTO1-ontology-split/evidence/a3fix-00-BEFORE-AFTER.md` |
| 授权依据 | `memory/TL-DECISIONS-W-1.md` **D-2** / **D-3**；`memory/PLAN-NEXT.md` §A3；`FAILURES.md` FAIL-2026-09-20-05 / FAIL-2026-09-20-W15TL-02/03；`memory/handoffs/INDEPENDENT-QA-W15-2026-09-20.md` §4.2 E3 / §6 条件表；TL 追加指令（2026-09-20） |

---

## 1. 交付物与哈希（AU-1 用；实测命令见 §1.1）

| # | 文件 | sha256 |
|---|---|---|
| 1 | `scripts/onto1_namespace_collision_check.py`（F1 + F2 + C-3/C-4/C-7/C-8） | `c5f7b6717f57c662d55d6d0b381bb35e7b22fee44be5af56cfb630230261770e` |
| 2 | `scripts/onto1_reference_alignment_check.py`（F3 + C-6） | `f6ef74f3767289b55e1b55e6e1ff796b3a181baa712b7758d31e96fb66d95ad3` |
| 3 | `loops/ONTO1-ontology-split/evidence/a3fix-00-BEFORE-AFTER.md` | `8ab80417f9eed9e0bff4b330eca881851d208513f6430884089d1adc6487e17d` |
| 4 | `loops/ONTO1-ontology-split/memory/waves/PKG-A3-PLAN.md` | `5e28fa6422826f2de0c443955f48fd603117cdfa821e7398d4146c894253faf0` |
| 5 | `loops/ONTO1-ontology-split/memory/waves/PKG-A3-ITER.md` | `214a60a83d6a5b56e8c932a9a5728d7bb927a218b40c80ad575d21892ebe8d00` |
| 6 | `evidence/a3fix-after-wi_a4_namespace_collision-gate.log` | `ab504082c8475834a8125024598a6ae529875d74d65e2292af20e6b038ab2467` |
| 7 | `evidence/a3fix-after-wi_a4_namespace_collision-selftest.log` | `8506983dca97d4676dec1d32e0e092952fb6accba286d5e87e638c2206ba495c` |
| 8 | `evidence/a3fix-after-wi_a3_reference_alignment-gate.log` | `4df36e47f7fd194ab7fccab402529eee78338582c7f4990dd1974494f2213d66` |
| 9 | `evidence/a3fix-after-wi_a3_reference_alignment-selftest.log` | `53f0576279832258776f7b5814dfa1ef506f518d22dd4fea734f9c61dfe5cdcb` |

**本文件（HANDOFF）自身哈希不在上表**——文件内声明自身哈希必然自指；请以 `sha256sum` 实测为准。

### 1.1 复核命令

```bash
sha256sum scripts/onto1_namespace_collision_check.py scripts/onto1_reference_alignment_check.py
sha256sum loops/ONTO1-ontology-split/evidence/a3fix-* loops/ONTO1-ontology-split/memory/waves/PKG-A3-*.md
```

## 2. 门禁实测（AU-2 用；请 TL **亲自复跑**，不采信本表）

| # | Gate id | Command | 实测 exit | 期望 exit | 关键输出行 |
|---|---|---|---|---|---|
| A | `wi_a4_namespace_collision` | `python3 scripts/onto1_namespace_collision_check.py --gate` | `2` | **`2`（保留真实 FAIL）** | `[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3 / 未裁决 0；必需钉值 allow-list 4/4；载体自冻结：受控载体 0 个，**空转不计为覆盖**）`；`[C-2] FAIL`；失败项仅 `C-2` ×2 |
| A′ | `wi_a4_namespace_collision_selftest` | `python3 scripts/onto1_namespace_collision_check.py --selftest` | `0` | `0` | **23 项全 PASS**（19 变异 + 4 对照；含 `M12b`/`M13`/`M13b`/`M15`/`M15 对照`/`M15b`） |
| B | `wi_a3_reference_alignment` | `python3 scripts/onto1_reference_alignment_check.py --gate` | `0` | `0` | `verdict: PASS`；`allowed[rule_statement]=0`；`allowed_by_reason: {ancestor_key_negation:1, same_line_negation:58, section_heading_negation:2, table_row_negation:9}` |
| B′ | `wi_a3_reference_alignment_selftest` | `python3 scripts/onto1_reference_alignment_check.py --selftest` | `0` | `0` | **13/13**（含 `M10` 放行＋计数断言、`M11` 相邻行不扩散、`M12` `loops/**` 内真实声称 ⇒ FAIL） |

**如实声明两条"未覆盖/未决"**（不得计为通过）：

1. 门禁 A 整体 **`fail`（exit 2）**：唯一失败项是 C-2 两处真实前缀冲突（`products.ttl:1/:10/:15`），修复属 **Wave 3**。本包**未**使 C-2 转绿，**未**删除任何断言（`M0b` 已加严断言"真实仓失败项仅 C-2 且必需钉值 4/4"）。
2. C-4 的**载体自冻结**子检查在真实仓**空转**（受控钉值载体 0 个——本 Loop 两个侧车均属 D-2 范围外的清单类产物）⇒ 已在输出中显式标注"空转不计为覆盖"，**不得**把 `[C-4] PASS` 读成"该子检查通过"。

## 3. 改动明细（AU-3 / AU-5 用）

### 3.1 `scripts/onto1_namespace_collision_check.py`

| 位置 | 改动 |
|---|---|
| 头部表格 `C-4` 行 | 改为"**可判定 → PASS**（声明 4 个：受控 1 通过 / D-2 范围外 3；**必需钉值 allow-list 4/4**；载体自冻结子检查**空转，不计为覆盖**）；判据：漂移 / 受控载体未冻结 / 必需钉值缺失 / 范围未裁决 ⇒ FAIL"（**F-5(:13) / C-7**：与实跑逐字一致） |
| 头部新增小节「C-4 适用范围（D-2 收窄）」 | 受控范围、D-2 排除类、**六条保留牙齿**（含必需钉值 allow-list、冻结作用域）、D-2 过渡义务（**C-8**）与空转声明 |
| 头部 `--selftest` 说明（原 `:34/:35`） | 改为"**19 条变异 + 4 条对照（含 2 条 restore⇒PASS）**，共 **23 项**；沙箱全绿 / 真实仓 **FAIL（exit 2）**"（**C-7**） |
| 新增常量 `CONTROLLED_PIN_PREFIXES` / `CONTROLLED_PIN_SUFFIXES` / `LIST_ARTIFACT_PREFIXES` | **F1①**：判定范围常量集中定义 + 裁定出处注释 |
| **新增常量 `REQUIRED_PINS`** | **C-4**：4 项必需钉值（`specs/semantic/gits-core.owl.ttl`、`loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv`、`…/consumer-scan-hits.jsonl`、`…/consumer-scan-summary.csv`），注释内含 `文件:行` 回源（`baseline-v2-manifest.json:3/:11`、`consumer-scan-manifest.json:18/:19`），并说明 QA 条件 C-4 的 `evidence/…` 简写与实际声明路径的对应关系（避免断言因简写而永不成立） |
| 新增 `_rel_posix()`、`pin_scope()` | 单一真值函数：`controlled` / `list_artifact` / `unclassified`（`--gate` 与 `--selftest` 共用） |
| 重写 `check_c4()` | ① 自引用检测在范围过滤**之前**（与 D-2 无关）；② 受控条目哈希比对；③ **必需钉值 allow-list**（`C-4_REQUIRED_PIN_MISSING`，**C-4**）；④ 范围外逐条登记 + 打印；⑤ 范围未裁决 ⇒ `C-4_PIN_SCOPE_UNCLASSIFIED` FAIL；⑥ 受控条目 0 ⇒ `C-4_NO_CONTROLLED_PIN` FAIL；⑦ 载体冻结只管辖**受控载体**，输出**显式声明冻结扫描根**（**C-3**），0 个时记 `VACUOUS` 并计入 `vacuous` |
| `emit()` 的 C-4 分支 | 增印"必需钉值 allow-list N/M"、"冻结记录扫描根（作用域声明；根外的记录不可见）"、逐条"载体自冻结豁免（…**已知误报**项）"与逐条"必需钉值缺失"（**C-8**：`grep -c 误报` = 4） |
| `build_sandbox()` | 沙箱与真实仓**同构**，且侧车文件名逐字对齐 `REQUIRED_PINS`（`attribution-45-v2.csv` 等） |
| `selftest()` | `M5` 改打受控制品；`M11` 补受控条目；`M12` 改受控载体口径 + 对照（记录落在**扫描根内** ⇒ PASS）；**新增 `M12b`**（记录写在扫描根**之外** ⇒ FAIL，复现 F-3）；**新增 `M13`**（取消收窄 ⇒ 旧噪声复现）、**`M13b`**（受控条目 0 ⇒ FAIL）；**新增 `M15` / `M15 对照` / `M15b`**（必需钉值缺失 ⇒ FAIL / restore ⇒ PASS）；原 `M13` 顺延 **`M14`**（**未删除**）；`M0b` 加严（真实仓失败项仅 C-2、C-4 无失败、必需钉值 4/4） |

### 3.2 `scripts/onto1_reference_alignment_check.py`

| 位置 | 改动 |
|---|---|
| 文件头「设计」/「精度上限」 | 增列"元陈述放行"（D-3 依据、留计数、**行级**作用面、M11/M12 两个边界用例） |
| 新增常量 `META_STATEMENT_MARKERS` | 六个关键词（`注入` / `变异` / `禁用词表` / `词表` / `判 FAIL` / `不得放行`）+ D-3 裁定注释 + **"不采用 `loops/**` 白名单"**的理由（**C-6**） |
| `classify_line()` | 新增放行原因 `rule_statement`（放最后，结构语境优先；作用面严格限当前行） |
| `truth()` / `print_report()` | 新增 `allowed_by_reason` 逐原因计数，并打印 `allowed[rule_statement]=N`（D-3①） |
| `SELFTEST_CASES` + 夹具 | 新增 `M10`（规则陈述行放行 + 计数断言）、`M11`（相邻行真实声称 ⇒ FAIL）、**`M12`（`loops/**` 内真实声称 ⇒ FAIL，C-6）** |

**回源锚点（AU-3 抽样用）**：D-2 排除类实际位置 `git ls-files | grep -E '(baseline-v2-manifest|consumer-scan-manifest)'`（均在 `loops/ONTO1-ontology-split/evidence/`）；C-4 噪声现场 `evidence/wi_a4_namespace_collision-20260920T145542Z.log`（`EXIT_CODE=2` + 两条 `C-4_PIN_FILE_UNFROZEN`）；F-3 现场 `INDEPENDENT-QA-W15-2026-09-20.md:150-157`。

## 4. 登记建议（TL 执行 `record_gate.py`；本包不代记账）

| Gate id | Command | pass_condition（建议改为） | 期望 exit |
|---|---|---|---|
| `wi_a4_namespace_collision` | `python3 scripts/onto1_namespace_collision_check.py --gate` | C-1/C-2/C-3 同前；**C-4 受控钉值一致（D-2）**：只对受控钉值文件判定哈希；清单类工具产物按 D-2 逐条登记不判定；**必需钉值 allow-list 4/4 缺一即 FAIL**；**受控**载体须有落在**冻结扫描根内**的独立冻结记录；范围未裁决 / 受控条目为空 ⇒ FAIL。**当前仍 `fail`（exit 2）**：C-2 两处真实冲突未修（Wave 3）。 | `2` |
| `wi_a4_namespace_collision_selftest` | `... --selftest` | 23 项（19 变异 + 4 对照）mutate⇒FAIL / restore⇒PASS；含 **M12b**（冻结记录写在扫描根之外 ⇒ FAIL）、**M13**（取消收窄 ⇒ FAIL）、**M13b**（受控条目 0 ⇒ FAIL）、**M15/M15b**（删必需钉值 ⇒ FAIL）。 | `0` |
| `wi_a3_reference_alignment` | `python3 scripts/onto1_reference_alignment_check.py --gate` | 参照对齐（内部规则名义）检查通过；文本到手前不得出现任何标准符合性表述或被否决制品名。**D-3**：规则陈述行（行内含元陈述关键词）放行，输出 `allowed[rule_statement]=N` 供审计。 | `0` |
| `wi_a3_reference_alignment_selftest` | `... --selftest` | 13/13：注入被禁止的表述类变异 ⇒ FAIL；**M10** 放行须留计数；**M11/M12** 证明放行是**行级**的（相邻行、`loops/**` 目录内的真实声称照旧 FAIL）。 | `0` |

**另建议 TL 更新**（写域外，仅提示，不代改）：

1. `LOOP.yaml` 中 `wi_a4_namespace_collision.pass_condition` 的"**＋ C-4 已知误报**"括注应删除（误报已按 D-2 消除），改写为"C-2 两处真实冲突（修复属 Wave 3）"；
2. `memory/ORCHESTRATOR.md` §4 碰撞门禁的 `--selftest 16/16` 应更新为 **23/23**，§7.2 G-2/G-3 标注"已按 D-3 / D-2 落地"；
3. `FAILURES.md` 的 `FAIL-2026-09-20-W15TL-02/03` 与旧条目（含"`C-4` 转 PASS"口径争议，QA F-4/H-2）可补一条**事实更新**：改后真实仓 `C-4 = PASS`，且该 PASS 的构成是"**受控 1 项哈希一致 + 必需钉值 4/4 + 受控载体自冻结子检查空转**"（可复核，非"整体转 PASS"的模糊表述）。

## 5. 未决与风险（如实声明，供 TL 裁定）

| # | 项 | 影响 | 建议 |
|---|---|---|---|
| R-1 | **残余发现**：`classify_line()` 的 `section_heading_negation` 用**子串**匹配否定标记，单字 `禁` 使"门禁…"这类标题放行其下全部命中行 | 既有**放行过宽**（构造 M11 夹具时实测撞到）；真实仓计数 `section_heading_negation=2` | 改为**词级**匹配，并在同会话复跑真实仓确认判定面变化；属行为变更，本包不擅改 |
| R-2 | C-4 载体自冻结在真实仓空转 | "改侧车钉值即通过"的残余空间**仅**覆盖 D-2 范围外的清单类产物；受控件仍受"哈希 + 必需钉值 allow-list"约束 | 若不可接受，须裁定"冻结算子的**受控钉值对**"等噪声安全口径；本包不擅自发明 |
| R-3 | `C-4_PIN_SCOPE_UNCLASSIFIED` / `C-4_REQUIRED_PIN_MISSING` 为新增 fail-closed 面 | 将来扩大受控范围或调整必需钉值集合时需**改常量并留裁定依据** | 常量已集中定义（`CONTROLLED_PIN_*` / `LIST_ARTIFACT_PREFIXES` / `REQUIRED_PINS`），便于审计 |
| R-4 | 真实仓 `allowed[rule_statement]=0` | D-3 能力当前未被真实规则文书使用（触发行已由 TL 改写措辞） | 无需动作；一旦有规则陈述行，计数会显形 |
| R-5 | 沙箱与真实仓的清单类产物按**路径前缀**识别（`loops/**`、`evidence/**`） | 若将来工具产物落到别处 ⇒ `unclassified` ⇒ FAIL（fail-closed 预期） | 届时由 TL 裁定是否纳入 `LIST_ARTIFACT_PREFIXES` |
| R-6 | `REQUIRED_PINS` 是**硬编码必需集合** | 真实仓新增必需钉值时不自动纳入（需显式改常量） | 与"禁止删除硬编码冻结值"一致：只允许**增补**，且每次增补须留裁定依据 |

## 6. 红线声明（AU-5 用）

- 只改 `scripts/onto1_namespace_collision_check.py`、`scripts/onto1_reference_alignment_check.py`
  与本包写域内的 `evidence/a3fix-*`、`memory/waves/PKG-A3-*`、`memory/handoffs/PKG-A3-*`；
- **未**改 `specs/**`、`generated/**`、`docs/dd/**`；**未**写 KERT 仓（该仓只读；三个 ONTO1 文件 mtime 仍为 16:28 / 14:48 / 14:49，未落在本包时间窗）；
- **未**改 TL 单写者文件（`LOOP.yaml`、`EVIDENCE.json`、`EVIDENCE.md`、`STATE.json`、`FAILURES.md`、
  `memory/{ROLE_BOARD,NEXT_SESSION,ORCHESTRATOR,PLAN-NEXT,W-1.5-ORCHESTRATION,INDEX_BASIS,TL-DECISIONS-*}`）；
  **特别地：未用"在 `EVIDENCE.md` 补一行冻结声明"来满足 C-4b**（该路径已由 `M12b` 证明不可用）；
- **未**改他人交付物（`evidence/baseline-v2-manifest.json`、`evidence/consumer-scan-manifest.json`、
  `evidence/non-gate-log-allowlist.json`、`scripts/gk17_triple_consistency_check.py` 等）；
- **未**删除任何断言 / 变异用例 / 硬编码冻结值（`REQUIRED_PINS` 只增不减）；**未**放松 C-2；
  **未**把任何 `fail` 改写成 `inconclusive`；**未**改 `--gate` 的真实退出码；
- **未** `git add` / `git add .`；**未**记 `DEV_SELF_CHECK_PASS` / `QA_PASS`。

## 7. QA 条件回执表（逐条对应 `INDEPENDENT-QA-W15-2026-09-20.md` §3.3 / §6；缺表按未满足处理）

| 编号 | 项 | 状态 | 证据（命令 + exit + `文件:行`） |
|---|---|---|---|
| **F-1** | C-4 未按 D-2 收窄 | **已满足** | `check_c4()` docstring「适用范围 = CONTROLLED_PIN_PREFIXES/SUFFIXES，D-2 收窄」；`--gate` exit=2 输出 `[C-4] PASS（受控 1 / D-2 范围外 3）`；`--selftest` **M13**（放回扫描集 ⇒ FAIL） |
| **F-2** | `EVIDENCE.md:74` 陈旧哈希 | **不适用（非本包写域）** | 该文件为 TL 单写者文件，TL 已按 `FAIL-2026-09-20-W15TL-02` 删除该表述；复核：`sha256sum loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json` = `45475058b3050fc1…` |
| **F-3** | 自冻结记录不在扫描根内 | **已满足（机制层）** | C-4b 只管辖**受控载体**；输出显式声明「冻结记录扫描根（作用域声明；根外的记录不可见）：`loops/ONTO1-ontology-split/evidence`」；`--selftest` **M12**（根内 ⇒ exit 0）/ **M12b**（根外 ⇒ exit 2） |
| **F-4** | `FAILURES.md` "`C-4` 转 PASS" 口径 | **不适用（非本包写域）** | TL 单写者文件；**事实更新**：改后真实仓 `C-4` 确实 `PASS`，构成为"受控 1 项哈希一致 + 必需钉值 4/4 + 受控载体自冻结子检查空转"（见 §2 输出行） |
| **F-5** | 头部三处自述（`:13`/`:34`/`:35`） | **已满足** | `grep -n "C-4 钉值一致" scripts/onto1_namespace_collision_check.py`（现状列与实跑一致）；计数 "19 条变异 + 4 条对照 … 共 23 项"与 `--selftest` 实跑 23 行一致；"真实仓 FAIL（exit 2）"由 `M0b` 断言 `real["exit_code"] == 2` |
| **F-6** | D-2 过渡义务（显式标注已知误报） | **已满足（两路同时成立）** | ① 两条已知误报**消失**（`--gate` 的失败项中无 `C-4*`；`M0b` 断言 `not any(item.startswith("C-4"))`）；② 输出仍**逐条声明**：`载体自冻结豁免（D-2 清单类产物；原 FAIL-2026-09-20-05 的C-4_PIN_FILE_UNFROZEN 已知误报项）：…baseline-v2-manifest.json`（×2）；③ `grep -c 误报 scripts/onto1_namespace_collision_check.py` = **4** > 0 |
| **C-1** | A3 改后 `--gate` 必须仍 exit=2 | **已满足** | `python3 scripts/onto1_namespace_collision_check.py --gate; echo $?` ⇒ `2`；失败项仅 `C-2`×2（`[C-2] FAIL（实测 2 / 登记 2 …）`） |
| **C-2** | 修 `EVIDENCE.md:74` 或删除该声明 | **不适用（非本包写域）** | 见 F-2（TL 已修） |
| **C-3** | 明确 `EVIDENCE.md` 是否属 C-4b 扫描根 / 记录必须落在 `evidence/` 内 | **已满足** | 实现**不**以"补冻结记录"方式满足 D-2（清单类侧车已移出范围）；同时把作用域**显式声明**到输出；`M12`（记录在根内 ⇒ PASS）/ `M12b`（记录在 Loop 根 ⇒ FAIL） |
| **C-4** | 必需钉值 allow-list 断言 + 变异 | **已满足** | `REQUIRED_PINS`（4 项，附 `文件:行` 回源）+ `C-4_REQUIRED_PIN_MISSING`；`--gate` 输出「必需钉值 allow-list **4/4**」；`--selftest` **M15**（删范围外必需项 ⇒ exit 2）/ **M15 对照**（restore ⇒ exit 0）/ **M15b**（删受控 `baseline` ⇒ exit 2）——QA E3 的"内容层 0 失败"路径已被关闭 |
| **C-5** | A2 `--precheck` 条目级变异 | **不适用（属 PKG-A2）** | 本包不碰 `scripts/onto1_wave0_readiness.py` |
| **C-6** | `rule_statement` 不得退化为 `loops/**` 目录白名单 + 反例变异 | **已满足** | 实现为**行级关键词**判定（`META_STATEMENT_MARKERS`，**未**采用目录白名单）；`--selftest` exit=0，**13/13**，其中 **M12**（`loops/ONTO1-ontology-split/memory/…` 内不带元陈述关键词的真实声称）实测 `CONTENT_WORDING_UNALLOWED` ⇒ FAIL |
| **C-7** | 修头部**三处**自述 | **已满足** | 同 F-5；三处均与实测逐字对应（`:13` 判据＋现状、`:34` 计数、`:35` 真实仓结果） |
| **C-8** | 履行 D-2 过渡义务 | **已满足** | 同 F-6（消失 + 显式声明 + `grep 误报` > 0 三路判据） |
| **C-9** | `FAILURES.md:162` 口径改为可复核子项 | **不适用（非本包写域）** | TL 单写者文件；本包提供可复核事实（§2 的输出行 + §4 登记建议第 3 条）供 TL 改写 |
| **C-10** | `FAILURES.md` 失败编号去重 | **不适用（非本包写域）** | TL 单写者文件；未在 ITER 自行编号（去重规则见 `FAILURES.md:30`），本包只记 `S-1~S-3` 之类**局部**自愈编号 |
