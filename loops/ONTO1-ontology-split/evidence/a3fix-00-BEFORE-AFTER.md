# PKG-A3｜F1/F2/F3 改动前后对照（实测证据）

| 项 | 值 |
|---|---|
| 批次 | W-1.5 就绪加固（PKG-A3 两处门禁小修） |
| 负责人 | Feature Pilot `pilot-a3` |
| 时间 | 2026-09-20 |
| 授权依据 | `memory/TL-DECISIONS-W-1.md` **D-2**（C-4 收窄）与 **D-3**（元陈述放行）；`memory/PLAN-NEXT.md` §A3；`FAILURES.md` FAIL-2026-09-20-05 |
| 性质 | **只读加固**：只改两个脚本；不改 `specs/**`、`generated/**`、`docs/dd/**`；不写 KERT 仓；不代记账 |

---

## 1. 门禁 A：`wi_a4_namespace_collision`

命令：`python3 scripts/onto1_namespace_collision_check.py --gate`

| | 退出码 | C-4 关键行 | 失败项构成 |
|---|---|---|---|
| **改动前**（既有已登记证据，非本会话产物）<br>`evidence/wi_a4_namespace_collision-20260920T145542Z.log` | `2` | `[C-4] FAIL（钉值 4 个；含自引用与钉值文件自冻结）` | C-2 ×2（真实冲突）**＋ C-4 噪声 ×2**：`C-4_PIN_FILE_UNFROZEN`（`baseline-v2-manifest.json cac187a7624247a2`、`consumer-scan-manifest.json 45475058b3050fc1`） |
| **改动后**<br>`evidence/a3fix-after-wi_a4_namespace_collision-gate.log` | `2` | `[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3 / 未裁决 0；载体自冻结：受控载体 0 个，**空转不计为覆盖**）` | **C-2 ×2（真实 FAIL 原样保留）** |

**结论**：整体仍 `FAIL`（exit 2），失败项**只**来自 C-2 两处真实前缀冲突（修复属 Wave 3）——
没有被"顺手"放过；被消除的只有 D-2 认定的 C-4 噪声。受控制品
`specs/semantic/gits-core.owl.ttl` 仍在逐条哈希比对范围内，另有 3 条声明按 D-2 逐条**登记为范围外**
（不判定，但**显式打印**，不静默）。

C-4 收窄后的四条牙齿（真实仓逐项实测）：

1. 受控制品漂移 ⇒ `C-4` FAIL（沙箱 M5 实测 exit=2）；
2. 受控钉值载体未冻结 ⇒ `C-4_PIN_FILE_UNFROZEN` FAIL（沙箱 M12 实测 exit=2，补冻结记录后 exit=0）；
3. 声明落在受控范围与清单类产物**两者之外** ⇒ `C-4_PIN_SCOPE_UNCLASSIFIED` FAIL（fail-closed）；
4. 受控条目为 0 ⇒ `C-4_NO_CONTROLLED_PIN` FAIL（沙箱 M13b 实测 exit=2）——收窄不得收窄到空；
   自引用检测（`C-4_SELF_REFERENCE`）与范围无关，照旧对所有声明生效（沙箱 M11 实测 exit=2）。

## 2. 门禁 A′：`wi_a4_namespace_collision_selftest`

命令：`python3 scripts/onto1_namespace_collision_check.py --selftest`

| | 退出码 | 用例 | 差异 |
|---|---|---|---|
| 改动前 → `evidence/wi_a4_namespace_collision_selftest-20260920T145542Z.log` | `0` | 16 项（M0~M13 + M-元 + M0b） | M5 打在 `specs/data/…r2rml.ttl`；M12 打在**范围外**临时侧车 |
| 改动后 → `evidence/a3fix-after-wi_a4_namespace_collision-selftest.log` | `0` | **19 项**（M0~M14 + M13b + M-元 + M0b） | M5 改打**受控**制品；M12 按 D-2 口径**同步调整**；新增 M13 / M13b；原 M13 顺延为 M14（**无删除**） |

新增 / 调整的变异（逐条实测输出见日志）：

| 变异 | 内容 | 期望 | 实测 |
|---|---|---|---|
| M12（调整，未删除） | **受控**载体（`specs/semantic/pins.json`）无独立冻结记录 | `C-4_PIN_FILE_UNFROZEN` | exit=2 ✓ |
| M12 对照 | 补上独立冻结记录（restore） | PASS | exit=0 ✓（双向验证有牙齿） |
| **M13（新增）** | **取消收窄**：让范围判定对一切路径返回"受控"（＝把清单类产物放进 C-4 扫描集） | 旧噪声 FAIL 必须**复现** | exit=2 ✓ |
| **M13b（新增）** | 侧车只声明范围外清单类产物 ⇒ 受控条目 0 | `C-4_NO_CONTROLLED_PIN` | exit=2 ✓ |
| M0b（加严） | 真实仓对照增加断言"**C-4 噪声已消除**" | exit=2 且无 C-4 失败 | ✓ |

M13 的意义：被消除的 FAIL 能被**同一条断言**在范围放回时复现 ⇒ 收窄是**定向范围纠正**，
不是删断言换绿；M13b 的意义：收窄不能变成"把 C-4 收成恒绿"。

## 3. 门禁 B：`wi_a3_reference_alignment`（D-3 元陈述放行）

命令：`python3 scripts/onto1_reference_alignment_check.py --gate`

| | 退出码 | 关键输出 |
|---|---|---|
| 改动前 → `evidence/wi_a3_reference_alignment-20260920T145634Z.log` | `0` | `counter: files=4555 … allowed=68`（无逐原因计数） |
| 改动后 → `evidence/a3fix-after-wi_a3_reference_alignment-gate.log` | `0` | `counter: files=4598 … allowed=72` ＋ `allowed[rule_statement]=0` ＋ `allowed_by_reason: {"ancestor_key_negation": 1, "same_line_negation": 58, "section_heading_negation": 2, "table_row_negation": 9}` |

**如实声明**：真实仓当前 `allowed[rule_statement]=0`——D-3 触发的那行（`LOOP.yaml` 原 165 行）
已由 TL 改写措辞，故当前扫描集中没有"规则陈述行"。该放行是**为未来规则文书准备的能力**，
其有效性由 `--selftest` M10 证明（含计数断言），**不是**靠真实仓计数冒充。

## 4. 门禁 B′：`wi_a3_reference_alignment_selftest`

命令：`python3 scripts/onto1_reference_alignment_check.py --selftest`

| | 退出码 | 用例 |
|---|---|---|
| 改动前 → `evidence/wi_a3_reference_alignment_selftest-20260920T145541Z.log` | `0` | 10/10 |
| 改动后 → `evidence/a3fix-after-wi_a3_reference_alignment-selftest.log` | `0` | **12/12** |

| 用例 | 内容 | 期望 | 实测 |
|---|---|---|---|
| M10（新增，正向） | 规则陈述行（含元陈述关键词，**不含**否定标记）⇒ 放行，且断言 `allowed[rule_statement] >= 1` | PASS ＋ 计数 ≥1 | ✓ |
| M11（新增，反向） | **真实符合性声称**（无元陈述关键词）与规则陈述行**同文件相邻** | 仍 `FAIL` | ✓ `CONTENT_WORDING_UNALLOWED` |

M10 的夹具刻意**不含**否定标记（否则会被 `same_line_negation` 先接走、测不到 `rule_statement`）；
M11 证明该放行是**行级**的：文件里别处出现元陈述关键词**不会**放行本行。
放行链采用"元陈述关键词"而不是"把 `loops/**` 整体加白名单"，后者会把该目录下的真实声称一并放过。

## 5. 残余发现（**既有**问题，不属本包改动范围，须 TL 裁定）

`classify_line()` 的 `section_heading_negation` 用**子串**匹配否定标记，而 `禁` 是单字标记：
标题里含"**禁**"的词（如"门禁…"）会让其下所有命中行被放行。本会话在构造 M11 夹具时**实测撞到**
（夹具标题写作"门禁规则（夹具）"时，其下真实声称行被放行；改为"规则说明（夹具）"后立即判 FAIL）。

- 归属：**既有放行过宽**（非 D-3 引入，也非本包引入）；
- 本包**不擅自修**：改成词级匹配会改变既有判定面，可能使真实仓门禁变红 ⇒ 属需裁定的行为变更；
- 已具备的可审计抓手：本包新增的**逐原因计数**把该面暴露出来——真实仓
  `allowed_by_reason.section_heading_negation = 2`（可复核）；
- 建议（留 TL）：把单字/易碰撞标记（`禁`、`驳`、`排除` 等）改为**词级**匹配，并在同一会话内
  复跑真实仓门禁确认判定面变化。

## 6. 追加硬验收（TL 依 QA 报告 §4.2 E3 / §6 条件表追加；只增补，不重做 F-1 / F-5 `:13`）

| 条件 | 实现 | 变异 | 实测 |
|---|---|---|---|
| **C-4** 必需钉值 allow-list | 常量 `REQUIRED_PINS`（4 项）+ `C-4_REQUIRED_PIN_MISSING` | **M15**（删范围外必需钉值）/ **M15 对照**（restore⇒PASS）/ **M15b**（删受控 `baseline`） | 三条均按预期（exit 2 / 0 / 2） |
| **C-3** 冻结作用域 | 输出显式声明冻结扫描根；C-4b 只管辖受控载体 | **M12b**（记录**存在但**写在扫描根之外＝Loop 根 `EVIDENCE.md` 形态） | exit=2 ⇒ 复现 F-3，证明"根外补声明"不可用 |
| **C-6** 放行不得退化为目录白名单 | 行级关键词判定（未采用 `loops/**` 白名单） | **M12**（`loops/**` 内无元陈述关键词的真实声称） | `CONTENT_WORDING_UNALLOWED` ⇒ FAIL |
| **C-7** 头部三处自述 | `:13` 判据＋现状、`:34/:35` 计数与真实仓结果 | — | 与实跑逐字一致（19 变异 + 4 对照 = 23 项；真实仓 `FAIL(exit 2)`） |
| **C-8** D-2 过渡义务 | 两条**已知误报**经收窄消失，且输出逐条**声明**豁免对象/原因/出处；源码含"误报"字样 | **M13**（放回扫描集 ⇒ 必 FAIL） | `grep -c 误报` = 4 > 0；C-4 输出含"载体自冻结豁免（…已知误报项）"×2 |
| **C-1** 不得转绿 | 未使 C-2 转绿 | — | `--gate` exit=**2**，失败项仅 `C-2`×2 |

## 7. 复核方式（TL 可直接复跑）

```bash
python3 scripts/onto1_namespace_collision_check.py --gate        # 期望 exit=2，失败项只有 C-2；C-4 行含"必需钉值 allow-list 4/4"
python3 scripts/onto1_namespace_collision_check.py --selftest    # 期望 exit=0，23 项全 PASS
python3 scripts/onto1_reference_alignment_check.py --gate        # 期望 exit=0，含 allowed[rule_statement]=
python3 scripts/onto1_reference_alignment_check.py --selftest    # 期望 exit=0，13/13
grep -c 误报 scripts/onto1_namespace_collision_check.py          # 期望 > 0（C-8 判据）
```
