# PKG-A3｜ITER（两处门禁小修：F1 / F2 / F3）

| 项 | 值 |
|---|---|
| 负责人 | Feature Pilot `pilot-a3` |
| max_attempts | 5（单门禁）；实际用 2 轮（首轮自愈后复跑） |
| 计划 | `memory/waves/PKG-A3-PLAN.md` |
| 前后对照 | `evidence/a3fix-00-BEFORE-AFTER.md` |

> 记录规则：每次 attempt 记 **命令 + 退出码 + 输出摘要**。门禁记账由 TL 用 `record_gate.py` 执行，
> 本文件**不**代记账。

---

## Attempt 1｜F1 + F2（碰撞脚本：C-4 范围收窄 + 头部自述）

- Gate：`wi_a4_namespace_collision`
- Command：`python3 scripts/onto1_namespace_collision_check.py --gate`
- Exit：`2`（**期望值**：C-2 真实 FAIL 保留）
- 输出摘要：`[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3 / 未裁决 0；载体自冻结：受控载体 0 个，**空转不计为覆盖**）`；
  失败项 = `C-2` ×2（实测碰撞 2 处 + 全豁免假绿），**C-4 噪声 ×2 消失**。
  改动前同命令的对应输出（既有已登记证据）：`[C-4] FAIL（钉值 4 个…）`＋`C-4_PIN_FILE_UNFROZEN` ×2。
- Gate：`wi_a4_namespace_collision_selftest`
- Command：`python3 scripts/onto1_namespace_collision_check.py --selftest`
- Exit：`0`
- 输出摘要：**19 项全 PASS**（改动前 16 项）：新增 `M13 取消 D-2 收窄 ⇒ FAIL`、`M13b 受控条目 0 ⇒ C-4_NO_CONTROLLED_PIN FAIL`；
  `M12` 调整为受控载体口径并附 restore⇒PASS 对照；原 `M13` 顺延为 `M14`（未删除）；`M0b` 加严为"真实仓无 C-4 失败"。

## Attempt 1｜F3（参照对齐守卫：规则陈述行放行）

- Gate：`wi_a3_reference_alignment`
- Command：`python3 scripts/onto1_reference_alignment_check.py --gate`
- Exit：`0`
- 输出摘要：`verdict: PASS`；新增 `allowed[rule_statement]=0` 与 `allowed_by_reason: {ancestor_key_negation:1, same_line_negation:58, section_heading_negation:2, table_row_negation:9}`。
  **如实声明**：真实仓当前为 0（D-3 触发行已由 TL 改写措辞）⇒ 该放行是能力项，其有效性由 `--selftest` M10 证明。
- 首轮 `--selftest` **未通过（10/12）**，两条自愈记录见下。

## 自愈记录（2 条，均属**夹具书写缺陷**，非被测对象缺陷）

### S-1｜M10 未测到 `rule_statement`（夹具被既有否定标记先接走）

- 现象：首轮 `M10 规则陈述行 ⇒ 放行` 判定 PASS 但**附加断言失败**（`allowed[rule_statement]=0`）。
- 根因：夹具该行同时含 `不得放行` 等**否定标记**，`classify_line()` 先返回 `same_line_negation`
  ⇒ `rule_statement` 分支根本没被走到（**放行原因不同、计数自然为 0**）。
- 处置：夹具改写为**不含任何否定标记**、只含元陈述关键词（`变异` / `注入`）的规则陈述行；
  该细节已写进夹具注释，避免后续维护者再次踩到。
- 复跑：`12/12 符合预期`，`allowed[rule_statement] >= 1` 断言成立。

### S-2｜M11 因标题含单字标记被**既有**放行过宽接走（残余发现，不再自愈）

- 现象：首轮 `M11 真实声称（与规则行同文件相邻）⇒ 仍 FAIL` 实测 PASS（应 FAIL）。
- 根因：夹具标题写作"**门禁**规则（夹具）"，而 `NEG_MARKERS` 含单字 `禁`
  ⇒ 既有 `section_heading_negation` 用**子串**匹配，放行其下所有命中行。
- 处置：① 夹具标题改为"规则说明（夹具）"，使 M11 真正测到"放行不扩散"；
  ② 该放行过宽面**既有且非 D-3 引入**，修复会改变既有判定面 ⇒ **不在本包擅改**，
  登记为残余发现（`evidence/a3fix-00-BEFORE-AFTER.md` §5），建议由 TL 裁定后单独处理；
  ③ 本包新增的逐原因计数已把该面暴露为可审计项（真实仓 `section_heading_negation=2`）。
- 复跑：`12/12 符合预期`。

---

## Attempt 2（F1/F2/F3 首轮收尾复跑；**已被 Attempt 3 取代**）

| Gate | Command | Exit 初值 | 输出摘要 |
|---|---|---|---|
| `wi_a4_namespace_collision` | `python3 scripts/onto1_namespace_collision_check.py --gate` | `2` | `[C-4] PASS（受控 1 / 范围外 3）`；失败项只有 `C-2` ×2 ⇒ **如实保留真实 FAIL** |
| `wi_a4_namespace_collision_selftest` | `python3 scripts/onto1_namespace_collision_check.py --selftest` | `0` | 19/19 PASS（当时版本） |
| `wi_a3_reference_alignment` | `python3 scripts/onto1_reference_alignment_check.py --gate` | `0` | PASS；`allowed[rule_statement]=0` |
| `wi_a3_reference_alignment_selftest` | `python3 scripts/onto1_reference_alignment_check.py --selftest` | `0` | 12/12（当时版本） |

> `evidence/a3fix-after-*.log` 在 Attempt 3 被**重采**（脚本与沙箱均变更）⇒ 上表**不声明哈希**
> （避免留下陈旧哈希；AU-1 复核请以 HANDOFF §1 的 Attempt 3 终值与 `sha256sum` 实测为准）。

**占位符/TODO 自检**：两个脚本内无 `TODO`/占位常量；Loop 目录内无 `loop_guard` 三类占位字面量待复核（收工跑 `memory-check`）。

---

## Attempt 3｜TL 追加硬验收（QA 条件 C-3 / C-4 / C-6 / C-7 / C-8）

TL 依 `memory/handoffs/INDEPENDENT-QA-W15-2026-09-20.md` §4.2 E3 与 §6 条件表追加硬验收。
**仅增补，不重做**已通过的 F-1 / F-5（`:13`）。

| 条件 | 本轮动作 | 结果 |
|---|---|---|
| **C-4**（必需钉值 allow-list） | 新增常量 `REQUIRED_PINS`（4 项：基线本体 + 归属矩阵 + 消费命中 + 消费汇总，路径逐字对齐侧车 `file` 字段并回源行号）；`check_c4` 增加 `C-4_REQUIRED_PIN_MISSING`（任一项从声明集合消失 ⇒ FAIL）；新增变异 **M15**（删范围外必需钉值）+ **M15 对照**（restore ⇒ PASS）+ **M15b**（删受控必需钉值 `baseline`）；`M0b` 加严为"真实仓必需钉值 4/4 齐备" | ✓ 复现 QA E3：旧实现的"内容层 0 失败"现由 allow-list 拦下（M15/M15b 均 exit=2） |
| **C-3**（冻结作用域） | C-4b 只对**受控载体**生效，且输出**显式声明冻结扫描根**（`loops/ONTO1-ontology-split/evidence`）；新增变异 **M12b**：冻结记录**存在但写在扫描根之外**（Loop 根 `EVIDENCE.md` 形态）⇒ 仍 FAIL（复现 F-3/W15TL-03）；M12 对照改为"记录落在扫描根内 ⇒ PASS" | ✓ 未采用"在根外补一行声明"满足 C-4b（该路径现被 M12b 证明**不可用**） |
| **C-6**（放行不得退化为目录白名单） | 参照对齐脚本新增变异 **M12**：`loops/**` 内**不带元陈述关键词**的真实声称 ⇒ 必须 FAIL | ✓ `13/13`（M12 实测 `CONTENT_WORDING_UNALLOWED`） |
| **C-7**（头部三处自述） | `:13` 已改（实跑一致：`[C-4] PASS` + 判据列明）；`:34/:35` 改为"**19 条变异 + 4 条对照 … 共 23 项 / 真实仓 FAIL（exit 2）**"，与实跑逐字一致 | ✓ 三处自述均有实测对应（见 `evidence/a3fix-after-*.log`） |
| **C-8**（D-2 过渡义务） | 两条**已知误报**（两个清单类侧车的 `C-4_PIN_FILE_UNFROZEN`）经收窄**消失**；输出仍以「载体自冻结豁免」逐条**声明**对象＋原因＋出处；源码含「误报」字样（`grep -c 误报` = 4 > 0） | ✓ 两路判据同时成立（消失 + 显式声明） |
| **C-1**（不得转绿） | 改后真实仓 `--gate` 仍 **exit=2**，失败项仍只有 `C-2`×2 | ✓ |

### 自愈记录 S-3（夹具书写缺陷）

- 现象：M12b 首轮 `FileNotFoundError`（在写文件前对其调用 `sha256()`，且把"冻结记录文本"误写进了 JSON 侧车）。
- 根因：夹具构造顺序错误（M12b 应"侧车 ← 砂箱侧车副本；冻结记录 ← 写在扫描根之外"）。
- 处置：M12b 改为 `copytree` 后把侧车副本写入 `specs/semantic/pins.json`，另将冻结记录写入 `m12b_root/EVIDENCE.md`（扫描根之外）。
- 复跑：`--selftest` 23 项全 `PASS`。

### Attempt 3 复跑（四条命令，日志落 `evidence/a3fix-after-*.log`，最终版）

| Gate | Exit | 关键输出 |
|---|---|---|
| `wi_a4_namespace_collision` | `2` | `[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3 / 未裁决 0；必需钉值 allow-list 4/4；载体自冻结：受控载体 0 个，空转不计为覆盖）`；失败项仅 `C-2`×2 |
| `wi_a4_namespace_collision_selftest` | `0` | 23 项全 `PASS`（新增 `M12b`/`M15`/`M15 对照`/`M15b`） |
| `wi_a3_reference_alignment` | `0` | `verdict: PASS`；`allowed[rule_statement]=0` |
| `wi_a3_reference_alignment_selftest` | `0` | `13/13`（新增 `M12`：`loops/**` 内真实声称 ⇒ FAIL） |
