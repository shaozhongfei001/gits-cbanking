# TL 对独立 QA（波 3）报告的逐条裁定书

| 项 | 值 |
|---|---|
| 对手文书 | `memory/handoffs/INDEPENDENT-QA-W3-2026-09-21.md`（独立 QA `independent_qa`，唯一写域） |
| 裁定人 | 全局 TL（delegated technical executor） |
| 日期 | 2026-09-21 |
| 总体立场 | **不辩解**：QA 的 12 条发现**全部接受**；其中 4 条"真实路径恒真"属**我实现层面的缺陷**，已修；修完**不主张该项已关闭**，须 QA 第二轮复验 |

> **原则**：QA 的结论**不是建议**而是对制品的独立判定；我不得以"我认为没问题"替代证据。凡我修正的，都给出**可复算**的验证命令与结果；凡我修正不了的，如实标注。

## 一、逐条裁定

| # | 严重性（QA） | 发现摘要 | TL 裁定 | 已采取处置（可复算） |
|---|---|---|---|---|
| **F-1** | 中 | `EVIDENCE.json.board_expression` 陈旧（写 51/50/0/1，实际 62） | **接受（事实类）** | 已按 `gates` 复算重写为 `PASS 61 / FAIL 0 / PENDING 1 / total 62`，并加 `derived_from` + `as_of` 字段，注明"每次改动后必须由实现者复算" |
| **F-2** | 中 | 常量化的边界判据 ⇒ L6 / M6 / M7 / G7 在真实路径恒真 | **接受（缺陷类）** | ① `onto1_l3_load_fixture.py`：新增 `boundary_probe()`，由**实际探测**（`namespaces.json` 存在性 + SIM 目录规模）派生；② `onto1_sim_migration_verify.py`：新增 `boundary_probe()` 与 `formal_needles()`，M6 的只读性改为**前后文件哈希一致**派生；③ `onto1_product_relation_resolution.py`：G7 改为**领域谓词派生佐证**（SIM 领域谓词不得同时作为 A-Box 领域谓词；通用词汇 rdf/rdfs 等排除）；④ 增**真实路径**反例：N7/N8（实际创建 `namespaces.json` / 实际写入 needle ⇒ 必须失败）、P6（同上，L3 侧） |
| **F-3** | 中 | `--plan-gate` P4 恒真（`replace` 自替换 + `or "不得" in txt` 同义反复） | **接受（缺陷类）** | 判据改为**要求两项表述同时出现**（"发布新 IRI" + "校验先于产出"）；并抽出 `plan_rows_for()`，新增**真实路径反例**：构造缺表述的临时文档 ⇒ P4 必须 FAIL（已实测被拦下） |
| **F-4** | 中 | A-4 的 M5/M2"泄漏=0"无证明力（12 条"新 IRI"全是符号占位，无 IRI 字面量） | **接受（缺陷类）** | M5 重写为**显式不计为覆盖**：`formal needle = 0` 时把理由写入 `coverage_exclusions`（原文："D3 未签 ⇒ 草案中不存在具体新 IRI 字面量（无 needle 可搜）… 待正式 IRI 发布后重建"）；并在制品中区分 `needles.formal / needles.symbolic`（实测 0 / 12） |
| **F-5** | 中 | A-1 的 A5 判据与构建路径**同源** ⇒ 真实路径恒真 | **接受（缺陷类）** | A5 改为**独立复算**：新增 `independent_consumption()`，**不读台账已存字段**，直接回原始 `hits.jsonl` 逐条重判消费证据。实测：独立复算 **53 行 / 覆盖 188 处 hits / 0 违例**——与 QA 的独立数字**逐项一致** |
| **F-6** | 低-中 | 位移落点指向**注释/docstring 行**（取首个出现行），对 Wave 2/3 迁移不可用 | **接受（缺陷类）** | `verify_evidence` 改为**注释 + 文档字符串感知**（逐行三引号状态机），落点取**非注释非 docstring** 行，并记该文件内命中处数。实测：`gk17_prodcard_to_rdf.py` 落点由 `:5`（docstring）改为 **`:37` / `:39`**（`prerequisite_product_ids` / `complementary_products` 真实映射值行） |
| **F-7** | 低 | `D-14` / `D-15` 各被复用于两条不同纪律；编号非单调 | **接受（治理类）** | 保留历史原文不删除，把我新增的两条**改号为 D-18（证据操作纪律）/ D-19（预算按 revision 纪元计数）**，并加**编号对照表**；同步修正本轮文书中旧编号引用（`SIM-R1-WAVE12-REPORT / NEXT_SESSION / STATE / EVIDENCE.md`） |
| **F-8** | 低 | C7 覆盖的旧日志备份落在**仓外易失** `/tmp` | **接受（治理类）** | `cp` 4 件至仓内 `evidence/archive/a3closeout-backup/`；同时落 `README` 说明"若 `/tmp` 副本已随会话清理丢失，以摘要对照为现存唯一记录（如实声明，不伪造）" |
| **F-9** | 低 | C5 按"PASS/FAIL 行"计数 ⇒ 某反例漏检时用例数仍为 26 | **接受（缺陷类）** | 改为**只数 `PASS ` 行**，并新增 `all_passed` 字段；C5 判据加"反例全过"要求；口径写入 `count_semantics` |
| **F-10** | 低 | L1 判据写成常量 `True`（fail-closed 但计数口径不纯） | **接受（缺陷类）** | L1 改为由**实际三元组数派生**（实测 T-Box 255 / A-Box 39 / SIM 290） |
| **F-11** | 信息 | 派工文两处口径不精确（① 证据卫生命令不检查板面拆分；② "投影配置中 0 处"字面为假） | **接受（文书类）** | `DISPATCH-WAVE3-PROMPTS.md` 已改写：① 拆分为"证据卫生"与"板面复算（给出一条 `EVIDENCE.json` 复算命令，并明确**不得**用证据卫生命令断言板面）"；② 精确为"**不得出现在 `aliasMap`**（出现在 `quarantinedAliases` 声明块是预期的）" |
| **F-12** | 信息 | A-7 的能力边界（ELIGIBLE 只验"姓名非空且互异 + 已签"） | **接受（声明类）** | `onto1_signature_verify.py` docstring 与判定输出均加 `capability_boundary`：**形式校验，不验证真实独立自然人 ⇒ 不得作为独立性成立的证据**；`ELIGIBLE ≠ 已批准` |

## 二、对 QA 总体判定"项 9 = NOT_ACCEPTED（断言强度）"的回应

**我接受该判定，且不主张修复后已关闭。**

- QA 的论证是：`--selftest` 的**内存变异**证明不了**真实执行路径**有判别力；并点名 F-2/F-3/F-4/F-5 四处恒真。
- 我的处置正是针对这一点：把 4 处判据**从字面量/同源改为派生**，并为 F-2/F-3 **补了真实路径反例**（实际创建文件、实际写入 needle、实际构造缺表述文档）。
- **余留诚实边界**：
  1. F-4 的 M5 在 D3 签署前**结构性无法构造**（草案无 IRI 字面量）⇒ 只能"不计为覆盖"，**不主张已覆盖**；
  2. N7/N8/P6 覆盖的是"边界探测逻辑"的真实路径，**不等于**覆盖了全部判据；是否足以支撑"判据非空转"的整体声明，**由 QA 第二轮判定**，我不自行改写结论。

## 三、交付给 QA 第二轮（复验清单）

| 复验点 | 命令 | 期望 |
|---|---|---|
| F-5 非同源 | `python3 scripts/onto1_disposition_ledger.py --gate` | A5 行须显示"独立复算 53 行（覆盖 hits 188 处）；违例 0" |
| F-6 落点 | 同上，查 `a2-disposition-ledger.json` 的 `line_drift` | `gk17_prodcard_to_rdf.py:33→37 / :35→39`（指向映射值行） |
| F-2/A-4 | `python3 scripts/onto1_sim_migration_verify.py --gate / --selftest` | M6 显示"哈希 N 文件不变=True"；selftest **9/9**（含 N7/N8） |
| F-2/F-10/L3 | `python3 scripts/onto1_l3_load_fixture.py --gate / --selftest` | L1 显示三元组数；L6 显示 SIM 目录内容；selftest **7/7**（含 P6） |
| F-3 | `python3 scripts/onto1_l3_load_fixture.py --plan-gate` | P4 要求两项表述；并输出"P4 真实路径反例 ⇒ 被拦下" |
| F-2/G7 | `python3 scripts/onto1_product_relation_resolution.py --gate` | G7 显示派生佐证（SIM 领域谓词 vs A-Box 领域谓词） |
| F-4 | `python3 scripts/onto1_sim_migration_verify.py --gate` | M5 须明示"**不计为覆盖**（理由已登记）" |
| F-9 | `python3 scripts/onto1_a3_closeout.py --gate` | C5 须含"反例全过" |
| F-1 | 读 `EVIDENCE.json.board_expression` | **与 `gates` 逐字一致**（本清单原写 61/0/1/62 系当时快照；**2026-09-21 收口实测为 83/0/1/84，共 84 门禁**）——**以权威字段为准，勿沿用本行数字** |
| F-7 | `grep -n "^### D-" memory/TL-DECISIONS-W-1.md` | 新增 D-18/D-19 + 对照表；历史条目未删 |
| F-8 | `ls evidence/archive/a3closeout-backup/` | 仓内备份存在 |
| F-12 | `python3 scripts/onto1_signature_verify.py --verify docs/review/.../14-*.md` | 输出含 `capability_boundary` |

## 四、我**未**改动的东西（避免"过度修复"）

- **未**改动 QA 报告一字（它是独立文书，只有其作者可写）；
- **未**因 QA 发现而提升任何门禁：`gate_state.current` 仍 `RETURN_TO_HLD`、Wave 0+ 仍 `BLOCKED`、`independent_qa` 仍**不是** `QA_PASS`；
- **未**删除历史纪律条目（F-7 只改号 + 加对照）；
- **未**把 `/tmp` 备份丢失一事掩去（F-8 如实声明）。

## 五、失败记账

本轮已记 `FAILURES.md`：**W15TL-19**（4 处判据真实路径恒真，QA 项 9）· **W15TL-20**（陈旧 `board_expression` / 编号重用 / 备份落仓外 / 派工文口径）。
