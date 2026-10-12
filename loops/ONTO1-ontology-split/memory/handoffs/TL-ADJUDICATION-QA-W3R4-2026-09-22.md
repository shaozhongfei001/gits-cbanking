# TL 裁定｜QA 第四轮（W3R4）结果处置 + **口径传播（板面止谎）**

> 受理：全局 TL｜2026-09-22
> 被裁对象：`memory/handoffs/INDEPENDENT-QA-W3R4-2026-09-22.md`
> **核验**：声明 `213105df192d4b5d…` ↔ 实测**逐字一致**（635 行）；**未改其一个字节**
> **本轮主线不是 QA 条目，而是一次板面可信性事件**：已授权口径变更（SIM 28→30）未传播到 ONTO1 门禁。

---

## 一、板面失效 → 止谎 → 修复（**主线**）

| 阶段 | 动作 | 结果 |
|---|---|---|
| **复算** | 我对 4 对门禁独立复跑 | `wi_d2_relation_resolution` exit 2 · `wi_a5_l3_load_fixture` exit 2 · `wi_a3_closeout` exit 2 · `wi_d2_sim_projection` 记录早于授权提交（陈旧） |
| **止谎** | 按实测重记（**不修口径、不解释为外部待定**） | 板面一度 **77 pass / 6 fail / 1 inconclusive**（比你预估的 80/3 多 3 条：那 3 个门禁的 **selftest 也全红**） |
| **修复** | ① `a3_closeout` 声明表 `wi_a2_disposition` 8→9（**我方 QA-2 改动未同步，自伤**）② `l3_load_fixture` 期望 28→30 且 L4 改**三类并检（待补∪作废∪隔离）+ 空转判 FAIL**、状态源改 `projection-config.json` ③ `d2_normalization_pack` A-1 **明示语义** ④ `namespace_collision_check` C-1 **空转不得给绿** ⑤ `product_refs_probe` C-2 P1 具名 | 四对门禁重新转绿；`wi_a4_namespace_collision` 保持 **INCOMPLETE(exit 3)** |
| **收口板面** | 统一重记 | **84 = 81 pass / 2 fail / 1 inconclusive**；仅剩 `wi_d2_relation_resolution`(＋selftest) 为 **fail** |

**口径冲突的权威依据**（我不代裁，只传播）：Owner 2026-09-22 签署「产品引用 7 符号分类」——
`CORPORATE_E_BANK` 5=有效待补 · `CASH_MANAGEMENT` 2=**错误引用→`PROD-CM-001`** · `FX_FORWARD` 1=待补 ·
`DISCOUNT_SERVICE` 1=待补 · `FINANCIAL_ADVISORY` 1=待补 · `RECEIVABLE_LEDGER_TOOL` 1=作废 · `ORDER_RECEIVABLE_CLOSED_ACCOUNT` 1=作废
⇒ **30 已解析 / 10 已分类未投影（待补 8 + 作废 2）/ 隔离 0**。我此前登记的硬约束
「`CASH_MANAGEMENT` 不得映射为现金池」**已被该签署明文取代**。

## 二、A 块（6 项）：3 ACCEPT / 3 ACCEPT_WITH_CONDITIONS

| 项 | 裁定 | 处置 |
|---|---|---|
| **A-1（我引入的表述缺陷）** | 条件接受 | **明示语义**，见 §三 |
| A-2 `cq_fixtures` | ACCEPT | 无（4 例篡改全红、不写回、唯一重生成入口 `--build` 已被独立证实） |
| A-3 `sim_projection` G8 | 条件接受 | 接受其条件：**G8 只证"一致性"，不证"授权"** ⇒ 已在明细标注，不扩张解释 |
| A-4 `d2` G8 | ACCEPT | 无（5 种变异全红） |
| A-5 自审仪 | ACCEPT | 无（227/14/13 复算一致、`--strict` exit 2、G0 误报消除） |
| **A-6（我题面不准）** | 条件接受 | **我方提示词所称「日志首行 `# artifact=`」只覆盖 9/84 门禁**（D-11 自证未全覆盖）⇒ 更正题面 + 登记覆盖面缺口 |

## 三、A-1 的处置：**明示，而非改语义**（含我一次失败尝试）

- QA 结论：我的位移容忍对「**副本追尾**」歧义不检测（`verify_ref` 先做精确行命中即短路）⇒ 我写的「0 命中/歧义一律 FAIL」**字面不成立**。
- **我的第一次修法是错的**：改成"全局唯一命中"后，真实树立刻出现 **26 条 `ambiguous` 假红**——因为锚点是**显式行钉定**，其 `expect` 字符串本就不唯一（如 `单位结算账户` 在卡内出现 2 次）。已**回退**。
- **最终处置（明示语义）**：精确行命中 ⇒ 通过；仅当精确行未命中而进入位移容忍时，才要求**全局恰好唯一命中**；0 命中 ⇒ `content lost`；≥2 命中 ⇒ `ambiguous drift`。
- **三向实验（亲自做）**：删内容 ⇒ `content lost` ✓；整体位移 +2 ⇒ 0 问题 + **位移记账 5 处** ✓；追加副本 ⇒ `ambiguous drift` ✓；实验后盘上制品**逐字节还原** ✓。

## 四、B 块（新范围）与覆盖缺口

QA 在 45 个仪器上定位 **205 个判定点**（120 门禁拒绝点 + 54 自检断言点 + 31 状态写入点），逐点结论
**SOUND 114 / NOT_AUDITABLE 61 / HAS_DEAD_PATH 30**（其中 18 点低置信，须回真仓复验）；
**关键量化**：我自审仪对这 205 点的覆盖率 = **0**；120 个拒绝点中仅 **36 个(30%)** 能被自家 `--selftest` 证明有牙。
⇒ 如实登记为**第二/第三类覆盖缺口**（与既有 13 个 `NOT_AUDITED`、审器不识别的两种形态并列），**不并入"已覆盖"**。

## 五、C 块（只判不改）的处置

| 项 | QA 判定 | 我的处置 |
|---|---|---|
| **C-1** C-4b 冻结域空转 | 应判 `NOT_EVALUATED`（不得给绿）；与 R4 冲突；D3 签署后会借 C-1b 转绿而整门转绿 | **已修**：任何 `VACUOUS` 子检查 ⇒ 整体 `INCOMPLETE`（exit 3），**永不 0** |
| **C-2** `product_refs_probe` P1 | 确认永不可达（形式化+实验）；反事实移位后退出语义不变 | **已修**：P1 并入异常路径（仍 exit 2，失败消息含 P1） |
| **C-3** AU-5 / `recent_changes()` | 给 ≥2 候选口径与代价，**不给结论** | **归 Owner**（候选口径见 QA 报告 §C-3，等你就其中一条定口径） |

## 六、我方两处自伤（如实记录）

1. **`wi_a3_closeout` 的红是我造成的**：QA-2 批次把 `wi_a2_disposition` 判据从 7 扩到 9，**未同步口径台账**；
   而我当时只复跑了"自己动过的门禁"，**没跑依赖它的门禁** ⇒ 漏检（本轮已修：声明表 8→9）。
   附带发现：`a3` 的 C7 是**冻结复交**语义 ⇒ 任何脚本变更后都需 `--build` 重冻（本轮再冻一次）。
2. **`record_gate` 把 exit 3 记成 `fail`**：我这次重记**把 INCOMPLETE 静默降级为 FAIL**（反向的"换口径"）。
   已修：`record_gate` 现按 `0→pass / 3→inconclusive / 其它→fail` 映射，并重记恢复。

## 七、板面与红线（本轮结束）

```
板面：84 = **81 pass / 2 fail / 1 inconclusive**
  · 2 fail = `wi_d2_relation_resolution`(+selftest) —— **待重构**（见 §八）
  · 1 inconclusive = `wi_a4_namespace_collision`（exit 3，C-1b 待 D3；现**另加**空转约束）
重记：a3(±st) · a5_l3_load_fixture(±st) · a5_d2_pack(±st) · a4_namespace_collision(±st) · a5_product_refs(±st)（D-19）
角色板：qa-w3r4 已登记（QA 请求）
红线：generated/ 0 · 基线 T-Box 705578d6324abd0c · KERT 近 1 日写入 0 · 未记 QA_PASS · 未代签 · 未把 FAIL 换口径（两个方向都未）
```

## 八、遗留（具名）

1. **`wi_d2_relation_resolution`(+selftest) = FAIL，待重构**：其输入模型已失效——它读 `UNRESOLVED.json.entries`（**已被清空为 0**）
   与我的旧登记表 `product-alias-resolution.json`（28/12）。**正确修法不是改常数，而是按新模型重构**：
   状态源改 `projection-config.json`（`aliasMap` 6 / `pendingProductCards` 4 项 8 条 / `voidReferences` 2 项 2 条 /
   `quarantinedAliases {}`），断言 30/10/0 与 CQ3 口径，并把 10 个反例按新语义重写。
   **这是较大改动**，我不在本轮硬塞（避免再造假红/假绿）——建议作为下一批专项，或与那条工作流协同。
2. **覆盖缺口三类**：13 个 `NOT_AUDITED` · 审器不识别的两形态（下标赋值 dict / `failures.append` 字符串）· **205 判定点**（B 块量化）。
3. **D-11 自证覆盖面**：`# artifact=` 仅 9/84 门禁（我已更正题面）。
4. **C-3 口径**：AU-5 / `recent_changes()` 待 Owner 选口径。

---

## 九、受审报告核验与版本绑定（F1 纪律落地）

| 对象 | 版本绑定 |
|---|---|
| 受审报告 | `memory/handoffs/INDEPENDENT-QA-W3R4-2026-09-22.md` **@213105df192d4b5d**（635 行，逐字核验） |
| 我方裁定文书 | `memory/handoffs/TL-ADJUDICATION-QA-W3R4-2026-09-22.md`（本件） |
| 本轮重记的制品 | 见每条 `record_gate` 日志首部 `# artifact=<脚本>@<sha256[:16]>`（自证行，D-11） |

**F1 采纳**：此后凡"已复核/已修"声明一律绑定 `path@sha256[:16]`；凡 `scripts/onto1_*.py` 或 `specs/**` 变更，
相关门禁按**新哈希重跑重记**（本轮已执行：14 个门禁）。

## 十、A 块逐项复算命令与原始输出（A1 要求）

```text
# A-1（明示语义）三向实验 —— 临时副本/内存，不动仓内制品
(b) 删内容      ⇒ verify_all_refs 报 `line content lost`
(a) 整体位移 +2 ⇒ 问题 0 条 + `ANCHOR_DRIFT` 记账 5 处
(c) 追加副本    ⇒ 报 `ambiguous drift (N matches at [...])`
实验后盘上制品逐字节还原 = True

# A-2（cq_fixtures 只读盘）：--gate exit=0；--selftest PASS（含 M4 篡改必红 exit=2、M5 不写回、M6 negative 空缺必拦）
# A-3（sim_projection）：--gate exit=0（10/10）；篡改盘上制品副本 ⇒ 仅 G8 失败（SIM_ARTIFACT_DRIFT）
# A-4（d2 包 G8）：去 R-6 / 声明截短 / 少于 5 条 / 非列表 ⇒ 均 FAIL；对照 PASS
# A-5（审器）：加固后 可审判据 229 · 候选 14（NOT_AUDITED 13 + DECLARED_ONLY 1）· --strict exit=2 · 默认 exit=0
# A-6（FAIL 是否换口径）：wi_a5_d2_pack 复算 output_sha256 == sha256(日志 STDOUT)（我方独立复跑 exit=0）
```

## 十一、B 块六条具名发现的出口（B1）

| # | QA 事实 | TL 出口 | 证据 |
|---|---|---|---|
| **B-i1** | 120 个门禁拒绝点**全部**是 `failures.append("字符串")` 形态；自审仪结构性看不见 | **认领并已修（B2）**：`extract_in_func` 纳入裸字符串 append 与下标赋值 dict | 加固后：**裸 append 91 点 · 下标赋值 195 点**（原 0）；`可审判据 229`；`未审仪器 13`（新增两类计为 `sighted_unjudged`，**不**计入 auditable，避免自欺） |
| **B-i2** | `signature_verify.py:57/59/63` 三条 append 不参与退出码 | **接受事实；判定为"披露式但结论已由参与退出码的判据表达"** | 三条各自对应：席位未填 ⇒ `verdict=INCOMPLETE`（F3/F4 用例）；同一自然人 ⇒ `record_kind_forbidden` 含禁记 + `v8_verdict=FAIL`（M5 用例）；`findings` 仅入返回体（:90），其**语义后果**已在退出码路径上 |
| **B-i3** | `disposition_ledger:379/384` 两条 append 不进退出码 | **以构造实验反证（不采信此条）** | `exempt_bad` 是 A5 的输入集，A5 在 `checks()` 中 ⇒ `--selftest` 的 **M3**（把豁免行证据指向本体消费行）实测使 A5 FAIL 且整体 exit=2 ⇒ 该清单**确实进退出码** |
| **B-i4** | d2 包 G5 三条强度判据**从未被任何变异触发** | **认领并已补反例**：新增 M6（去 `against`）、M7（`强`且证据为空） | `--selftest` 两项均 PASS（exit 2） |
| **B-i5** | `cq_fixtures:153`（Q5 negative 空缺）唯一未被自检踩到的拒绝点 | **认领并已补反例**：新增 M6（清空 `CQ1.negative`） | `--selftest` PASS（拦下语 `Q2 CQ1 missing/empty field: negative`） |
| **B-i6** | `pkg_audit` 8/8 点位不可判（副本内仅 47 行，`--gate/--selftest` exit 2） | **查明为"入口形态不符"而非"不可判"**：该仪器**没有** `--gate/--selftest`（argparse 报错即 exit 2） | 真仓实测：`--redlines` **exit=2**（AU-5 恒红，即 C-3 对象）· `--board` **exit=0**（ACCEPTED，AU-2/3/4 需人工） |

## 十二、B3 十八个低置信度点位的真仓复验结果

| 仪器 | QA 低置信点数 | 真仓复验结果 |
|---|---:|---|
| `pkg_audit` | 8 | **入口不符**（无 `--gate/--selftest`）；`--redlines` exit 2、`--board` exit 0 ⇒ 结论：其输出**不得**用于支撑任何红线结论（并入 C-3） |
| `zip_manifest_verify` | 5 | **入口不符**：真实入口需 `--zip <包>`（仓内无包时不可判，属**输入缺失**而非死路径）⇒ 登记为 NOT_AUDITABLE(输入缺失) |
| `review_package_build` | 4 | **真仓可跑**：`--gate` **PASS 6/6**、`--selftest` **PASS 3/3** ⇒ 该 4 点可达 |
| `reference_alignment_check` | 1 | **真仓可跑**：`--gate` **OK**、`--selftest` **OK** ⇒ 该点可达 |

## 十三、C 块落地形态

| 项 | 落地形态 | 理由 |
|---|---|---|
| **C-1** `namespace_collision_check` C-4b | **空转 ⇒ 整体 `INCOMPLETE`（exit 3），永不 0**（board 侧继续以三值表达 `inconclusive`） | 与 R4「空转=失败」一致；**未**扩冻结口径（`loops/**` mtime 本轮漂移 ≥3 次 ⇒ 扩口径只会把恒绿换成恒红，违反 D-15）；同时消除"D3 签署后借 C-1b 转绿而整门转绿" |
| **C-2** `product_refs_probe` P1 | **P1 并入异常路径并统一失败语**（仍 exit 2） | QA 已证移位后退出语义不变；此行属具名化，不改变判死行为 |
| **C-3** `pkg_audit` AU-5 / `recent_changes()` | **升级 Owner**（见 `HUMAN-ACTIONS-PROMPTS.md` 待人类-11） | 与 C-1 属**同一语义轴**（未授权/未判定该判什么），且涉及"授权范围的书写与签认方式"⇒ **不得由 TL 单方定口径** |

## 十四、§6 六条建议的采纳决定

| # | 建议 | 决定 |
|---|---|---|
| 1 | 版本绑定纪律硬化 | **采纳**（本件 §九已落地） |
| 2 | 消除隔离幻觉（14 个硬编码 ROOT 仪器加 `--root`） | **部分采纳**：登记为专项（改动面大、须逐个核对默认值）；本轮不硬改 |
| 3 | D-11 自证覆盖缺口 | **采纳并已执行**：本轮 14 个门禁的命令**统一改走 `onto1_gate_log.py`** ⇒ 自证行覆盖 **23/84**；`EVIDENCE.json.artifact_sha256` 字段待后续（包装器已打印，落字段属下一批） |
| 4 | 自审仪纳入两类形态 | **采纳并已执行**（B-i1/B2） |
| 5 | `d2-normalization-pack.json` 内嵌 `gits_commit` ⇒ 跨 commit 哈希必变 | **采纳**：在该门禁 `pass_condition` 注明"仅同 commit 可比"（下一批随 D2 重构一并落） |
| 6 | C-1/C-3 合并为三值表达（PASS/FAIL/NOT_EVALUATED，`board_expression` 显式分列） | **部分采纳**：C-1 已按三值语义落地（INCOMPLETE）；`board_expression` 增列 `NOT_EVALUATED` 与 C-3 口径**同批**（升级 Owner 后一并执行） |

## 十五、A4 板面差异说明（必须说明的差异）

- QA 收工实测：**84 = 83 pass / 1 inconclusive**（唯一非 pass = `wi_a4_namespace_collision`）。
- 本会话现状：**84 = 81 pass / 2 fail / 1 inconclusive**。
- **差异原因（非矛盾）**：QA 收工**之后**（我在上一轮受理中）发现"已授权口径变更（SIM 28→30）未传播到 ONTO1 门禁"⇒
  先按实测**止谎**（板面一度 77/6/1），再完成 4 类修复，最终 81/2/1。全过程记于 `FAILURES.md` `W15TL-26`。
- 剩余 2 fail = `wi_d2_relation_resolution`(+selftest)：其输入模型已失效（`UNRESOLVED.json.entries` 已清空、旧登记表 28/12）
  ⇒ 须按 `projection-config.json` 驱动重构，**不以改常数了事**。

## 十六、自证行位置的**事实订正**（A-6 的最终口径）

- 事实：本轮重记后，14/14 日志**均含** `# artifact=<脚本>@<sha256[:16]> …`，但位置是 **STDOUT 段首行 ＝ 文件第 4 行**
  （`record_gate.py` 先写 `COMMAND=` / `EXIT_CODE=` / `STDOUT` 三行）。
- 结论：我此前（含派工文本）所称"日志**首行** `# artifact=`"**在本仓不可达成**，属**我方表述不准**；
  可核口径应为"日志**含**自证行，且为 STDOUT 段首行"。已同步更正提示词与 STATE。
