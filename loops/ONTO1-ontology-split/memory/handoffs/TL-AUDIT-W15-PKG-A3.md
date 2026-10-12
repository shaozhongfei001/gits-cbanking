# TL 审计报告｜W-1.5 PKG-A3（两处门禁小修）

| 项 | 值 |
|---|---|
| 审计人 | 全局 Tech Lead（main） |
| 被审包 | PKG-A3 / `pilot-a3` |
| 审计时间 | 2026-09-20T23:36Z |
| 审计规格 | `memory/W-1.5-ORCHESTRATION.md` §4（AU-1~AU-7 + D-11 新增前置） |
| **结论** | **NOT_ACCEPTED（退回）** —— 设计质量高，但**证据不可复核 + 一处控制未达条件 + 一处崩溃** |

---

## 1. AU-1 交付物哈希（**问题**）

| 项 | 结果 |
|---|---|
| 仪器 | `onto1_pkg_audit.py --pkg PKG-A3` ⇒ `declared=3 failures=0`（HANDOFF 内声明可核） |
| **但** | 其**消息**声明 `scripts/onto1_namespace_collision_check.py = 32130eeafec51bad…`，TL 实测为 `c5f7b6717f57c662`（期间经历 `7d92d14a`）⇒ **声明哈希 ≠ 交付哈希** |

## 2. AU-2 复跑门禁（TL 亲自，且遵守 D-11 前置：连续取哈希确认稳定）

| 模式 | TL 实测 | pilot 声明 | 判定 |
|---|---|---|---|
| `collision --gate` | **2** | 2 | ✅ 一致（**仅 C-2 两项 FAIL**，C-4 已转 PASS） |
| `collision --selftest`（稳定 revision） | **0（23 项）** | 0（19 项） | ⚠️ 结果一致但**项数不符**（其 after 日志对应旧 revision） |
| `collision --selftest`（审计首轮，中间 revision） | **1（15 项后崩溃）** | — | ❌ 崩溃（`FileNotFoundError … m12broot/specs/semantic/pins.json`） |
| `refalign --gate` | **0** | 0 | ✅ |
| `refalign --selftest` | **0** | 0 | ✅ |

## 3. AU-3 回源抽查（5/5 成立）

| # | 声明 | TL 复核 | 判定 |
|---|---|---|---|
| 1 | C-4 收窄为受控范围 | `CONTROLLED_PIN_PREFIXES = ("specs/semantic/", "specs/CONTRACT_INDEX.yaml", …)`（`:114-119`） | ✅ |
| 2 | 新增必需钉值 allow-list | `REQUIRED_PINS`（`:145-149`）四项 = 基线本体 + 归属矩阵 + 消费命中 + 消费汇总 | ✅（**但见 §4 缺口**） |
| 3 | 收窄到空 ⇒ FAIL | `C-4_NO_CONTROLLED_PIN` | ✅ |
| 4 | 仅 C-2 残留 | `--gate` 输出 `FAIL（2 项）`，两条均为 C-2 | ✅ |
| 5 | D-3 放行按行按语义（非目录白名单） | `allowed[rule_statement]=0` + `allowed_by_reason{…}` 逐原因计数 | ✅（能力项存在；有效由变异证明） |

## 4. AU-4 独立沙箱变异（`--root /tmp/a3root`，**发现两处缺陷**）

| 变异 | 期望 | 实测 | 判定 |
|---|---|---|---|
| M-A 沙箱对照 | C-4 PASS 4/4 | C-4 PASS 4/4；C-2 FAIL×2 | ✅ 副本忠实 |
| **M-B 删【受控】必需钉值文件**（`specs/semantic/gits-core.owl.ttl`） | 具名 FAIL | **exit=1，抛 `KeyError: 'refirement_gate_scope'`（崩溃）** | ❌ `W15A3-03` |
| **M-C 删【范围外】必需钉值文件**（`consumer-scan-summary.csv`） | `C-4_REQUIRED_PIN_MISSING` FAIL | **仍报 `[C-4] PASS（必需钉值 allow-list 4/4）`** | ❌ `W15A3-02`（**QA E3 未真正关闭**） |
| M-D 恢复 | 回到 PASS | PASS | ✅ |

**根因**：`REQUIRED_PINS` 断言的是"该路径**出现在钉值声明集合**中"，**未断言文件存在**。QA 的 E3 删的是**文件**；A3 的 `M15/M15b` 验的是**声明消失** ⇒ 只关了一半。

## 5. AU-5 红线扫描

写域内（2 个脚本 + `evidence/a3fix-*` + `memory/waves/PKG-A3-*` + HANDOFF）；未碰 TL 单写者文件、他人交付物、`specs/generated/docs/dd`；KERT 三个 ONTO1 文件 mtime 仍为 16:28/14:48/14:49（未落本包窗口）⇒ **红线通过**。

## 6. AU-6 记账

**不新增、不修改**门禁记录：`wi_a4_namespace_collision` 仍为 `fail`（exit 2，C-2）；`wi_a3_reference_alignment` 仍为 `pass`（exit 0）。两结论在 A3 改动前后**均成立** ⇒ 板面（28 = 27 pass / 1 fail）无需改动。

## 7. 退回条件（4 条，逐条须给证据）

| # | 条件 | 判据 |
|---|---|---|
| **A3-1** | `REQUIRED_PINS` 必须断言**文件存在**（`is_file()`），缺文件 ⇒ 具名 `C-4_REQUIRED_PIN_MISSING` FAIL；覆盖受控 + 范围外**四项**；补变异 **M15c「删必需钉值文件 ⇒ FAIL」** | TL 沙箱 M-B/M-C 复跑必须 FAIL（且**非崩溃**） |
| **A3-2** | 消除缺输入崩溃：任何缺失输入 ⇒ 具名 FAIL 或 exit=3 `INCOMPLETE`，**不得抛异常**；`--gate`/`--selftest` 均不得 crash | TL 连续 3 次 `--selftest` 全绿、无 Traceback |
| **A3-3** | 修 **R-1 假绿通道**：`section_heading_negation` 用**子串**匹配否定标记，单字"禁"使**标题含"门禁"**的文书放行其下**全部**命中行（A3 自测已撞到）。改为**词级/边界**匹配，并给出修前/修后受影响面差异（真实仓该面现计数 = 2） | 构造"标题含『门禁』+ 其下真实声称"夹具 ⇒ **必须 FAIL** |
| **A3-4** | 交付纪律（D-11）：**冻结单一 revision**；HANDOFF 声明哈希 = 交付时实测；所有日志**首行嵌入脚本 sha256**；**重发** after 日志（现日志对应 19 项旧版） | TL 复算：日志首行哈希 == 脚本实测哈希 |

## 8. 已裁定的残余项

| 项 | 裁定 |
|---|---|
| R-2 载体自冻结空转的残余空间（仅覆盖范围外清单类产物） | **接受**；A3-1 完成后该空间进一步收窄（范围外也查文件存在） |
| R-3 `C-4_PIN_SCOPE_UNCLASSIFIED`（范围未裁决 ⇒ fail-closed FAIL） | **接受**（符合 D-2 的 fail-closed 要求） |

## 9. 非声明

不构成 `QA_PASS`；未验证 PKG-A1/A2；本报告的沙箱结论为 TL 复核（非第三方）；未对 KERT 侧任何文件作判断。

---

## 10. 追加：T-4 预验结果（2026-09-21T00:46Z，**A3 未正式复交前的 TL 预跑**）

`pilot-a3` 在被退回后继续修复，脚本在我审计之后又发生变更。按 **D-11 第 3 条**（审计前连续两次取哈希确认稳定）复核后预跑：

| 项 | 值 |
|---|---|
| 冻结 revision（两次取样稳定） | `collision = 8c18b5b3adc767e5` · `refalign = 4d706978a0fab7f2` |
| T-4 验收仪器 | `scripts/onto1_w15_acceptance.py`（8 用例；只写 `tempfile.mkdtemp`）⇒ **8/8 符合预期** |
| 门禁 | `collision --gate exit=2`（仅 C-2）· `collision --selftest exit=0`（**26 条用例记录**）· `refalign --gate exit=0` · `refalign --selftest` **16/16** |
| 记入门禁 | `wi_w15_a3_acceptance` 已登记（板面 **31 = 30 pass / 1 fail**） |

### 10.1 条件完成度（逐条）

| 条件 | 状态 | 证据 |
|---|---|---|
| **C1** 删钉值**文件**须具名 FAIL（受控 + 范围外四项） | **已到位** | `declaration["path"].is_file()`（`onto1_namespace_collision_check.py:394`）；仪器用例 **B/C** 均得 `C-4_REQUIRED_PIN_MISSING` |
| **C2** 缺输入不得崩溃（fail-closed） | **已到位** | 用例 B 无 `Traceback`（上一轮抓到的 `KeyError: 'refirement_gate_scope'` 已消除） |
| **C3** R-1 词级匹配（标题含"门禁"不得放行整节） | **已到位** | `HEADING_NEG_MARKERS = NEG_MARKERS - {"禁","驳"}`，**只改标题两处**（面最小，`_nearest_heading_is_neg` / `_ancestor_negation` 标题分支）；仪器用例 **R1a/R1b** 均判违规 |
| **C4** D-3 收紧（QA Q-1） | **已到位且更稳** | 现为 `CLAIM_CONSTRUCTION_RE` **压倒性优先**（声称构造命中 ⇒ 永不放行），比"联合判定"更强；仪器用例 **Q1a/Q1b** 均判违规 |
| **C5** 计数口径统一 | **未完成** | 需 A3 把文档/头部的"19 变异+4 对照""16/16"等字样更新为实测（collision **26 条记录** / refalign **16/16**） |
| **C6** M12 对照夹具"先创建再哈希" | **未完成（待 A3 确认）** | 本次 `--selftest` 全绿无崩溃，但需其明示夹具顺序 |
| **C7** 冻结复交 + 日志自证 revision + 回执表 | **未完成** | 需 A3 报 DONE 后停改、重发 `evidence/a3fix-after-*`（用 `scripts/onto1_gate_log.py`，日志首行带 `# artifact=…@<哈希>`）、HANDOFF 哈希表与磁盘一致 |

### 10.2 阻断说明（**必须如实声明**）

> **⚠️ TL 更正（2026-09-21T01:20Z，采纳 `qa-w15r` U-9）**：本小节原写"本轮 2 个既有门禁的登记证据仍属**陈旧、未被刷新**"——**该句未随制品更新**。事实是：N-6（重记陈旧证据）已由 TL 于 **15:59:15Z** 执行，四个相关门禁（`wi_a4_namespace_collision`(fail/2) · `…_selftest` · `wi_a3_reference_alignment` · `…_selftest`）**已按 D-11 包装器重跑重记**，登记日志内嵌哈希 **==** 当前冻结 revision（`collision 8c18b5b3` / `refalign 4d706978`），**就"证据-制品绑定"而言并不陈旧**。方向对 TL 有利，但仍如实更正。

**仍然成立的阻断（C7 字面未完成）**：**A3 自己的 4 份 `a3fix-after-*.log` 从未重发**，仍停留在旧 revision（其 refalign 记为 `candidates=157 / allowed=78 / rule_statement=0`，而登记版为 `159/80/1`）⇒ **C5（文档计数口径）与 C7（A3 侧日志/HANDOFF 哈希表）字面未完成**，因其作者 `pilot-a3` 已下线，转为交接项；**不影响判定结论**（四个反例已由 `wi_w15_a3_acceptance` 固化门禁、并由 QA 第三轮在自建沙箱独立复现通过）。

### 10.3 交付纪律提醒（已立 **D-13**，`FAIL-2026-09-20-W15TL-08`）

**不得把禁句逐字写进文档或脚本**：TL 自己在 `FAILURES.md` / `TL-DECISIONS-W-1.md` / 验收仪器脚本里逐字引用「…〔符合〕 GB/T …」，导致 **6 条 `CONTENT_WORDING_UNALLOWED` 全部来自我方文件**，一度把 `refalign --gate` 顶成 `exit=1`。机制：`CLAIM_CONSTRUCTION_RE` 对"符合 + 空格 + GB/T"判定为**声称构造**且**优先于一切放行理由** ⇒ **引用禁句 ≡ 自己发出声称**。正确做法：文档用**方括号/省略**、脚本**运行期拼接**且夹具只写临时目录；**不得**改用注册表豁免绕过。
> 附注：该事件**正向佐证** A3 的守卫有效（连写进 `scripts/` 的夹具常量都被拦住）。
