# GK16 信任收敛 Loop · 失败记录

> 本 Loop **不推进功能**，只做可信度收敛：正角色检查/修复，反角色以负例攻击。
> 下列每条均为**反角色攻击命中**（即正角色的某条结论被推翻）。

## T-01 【攻击命中·最重要】"9 项注入被检出"中，**6 项实为崩溃**

- **攻击**：正角色报告「9 个门禁有负例证据」。反角色问：**检出 = 门禁校验失败，还是门禁崩溃？**
- **结果**：实测 6 个门禁（contract-examples / contract-coverage / metric-definitions /
  product-card / registry-contract / plan-compiler）在注入**语法非法**的 JSON 后
  **抛 Traceback 退出**。那**只证明它没有输入防御**，**不证明它的校验逻辑发现了缺陷**。
  > **一个遇到非法输入就崩溃的门禁，在真实场景下同样会崩溃，而不是给出判定。**
- **结论**：**"9" 是虚高的；真受控检出只有 3 项。**
- **修复**：① 注入改为**语法合法、语义违规**（`{}`）；② 框架**单列 crash**，
  含 Traceback 的非零退出**不计为检出**。修复后 **11 项受控检出、0 崩溃**。

## T-02 【攻击命中】`gate-injection-tests` 自身"误导性通过"

- **攻击**：该门禁在有 3 项未确立 + 7 项未设计 + 1 项跳过（**11/18 未验证**）时仍 **exit=0 → PASS**。
  读汇总的人会以为"注入测试已完成"。
- **修复**：改为**覆盖不完整即 `__GATE_VERDICT__=INCONCLUSIVE`**，并在结论中给出精确缺口。
  现门禁链显示 `[INCONCLUSIVE] gate-injection-tests` —— **"未完成"对读者可见**。

## T-03 【攻击命中】元层面静默跳过：**2 个门禁无人认领**

- **攻击**：`run_gates` 有 **22** 个门禁，而框架只认领 13（注入）+ 7（未设计）= **20**。
  → **后人在 `run_gates` 新增门禁会**自动**落入盲区，且无人察觉。**
- **修复**：新增**认领盘点**——凡未在「注入设计」或「未覆盖登记」中出现的门禁，
  **直接 FAIL**。实测该检查当场抓到 `gate-injection-tests` 自身未被认领。
  现为 **22/22 全部认领**。

## T-04 【攻击未果·已登记攻击路径】注入点选错导致的"注入无效"

- **攻击**：正角色报告 dataset-v2 / acceptance-pack / loop-guard 三项目"注入未检出"。
- **尝试的路径**：① 破坏 JSON 语法 → 无效；② 注入 `{}` → 无效；
  ③ 破坏**文件哈希** → 无效（`dataset-v2 --verify` **不比哈希**）。
- **命中**：**这三者做的是语义检查，不是结构检查** ——
  · `loop-guard --template-check` 校验 `loops/_template`，
    且要求 `EVIDENCE.json` 的 gates 与 `LOOP.yaml` 一致；
  · `dataset-v2` 校验**禁止署名**（真实监管机构名）与**时间泄漏**。
  → 改为**语义注入**后，`loop-guard` 与 `dataset-v2` **均被检出**。
- **仍余**：`acceptance-pack` 的注入有效性**未确立**（它另有 `check_structure`/`check_isolation`，
  尚未找到其校验点）→ **如实登记为未验证，不计为通过**。

## T-05 【攻击未果·已登记】剩余覆盖缺口（**未修复，如实登记**）

| 门禁 | 状态 | 原因 |
|---|---|---|
| acceptance-pack | 注入有效性未确立 | 未找到其实际校验点 |
| semantic-rule-gate | 只读跳过 | 制品 `generated/` 受保护；**按纪律不放开写位**（FAIL-51 事故） |
| contract-check | 未设计注入 | shell 脚本，未读其校验逻辑 |
| enum-consistency | 未设计注入 | 需构造三层（Java 枚举/seed/schema）漂移 |
| probe-mutation-tests | 未设计注入 | 该门禁自身即变异测试，对其注入需改被测探针 |
| capability-probe | 未设计注入 | readiness 类，需构造能力不可调用场景 |
| counterfactual-test | 未设计注入 | readiness 类，需构造反事实失效场景 |
| chain-trace | 未设计注入 | 需 KERT 服务在运行 |
| semantic-consumption | 未设计注入 | 注入点为其汇总逻辑；其结论已由 NOT_MET 实测覆盖 |

> **登记 ≠ 修复。** 但**妨碍停止的不是"仍有缺口"，而是"未尝试攻击"或"隐瞒缺口"。**
> 上表由 `gate-injection-tests` **每次运行都打印**，不可隐藏。

## T-06 【攻击命中】`loop-guard` 门禁**只验模板、从不验实例**

- **攻击**：正角色报告"loop-guard PASS"。反角色新建 `GK16` loop 后运行
  `loop_guard.py --loop GK16-trust-hardening` → **连续 7 次 FAIL**
  （占位符未解析 / baseline 非完整 SHA / holder 不一致 / EVIDENCE gate 集合不匹配 /
  evidence 缺 status、exit_code、actor、actor_role、executed_at、evidence_file、output_sha256）。
- **命中**：门禁链里的 `loop-guard` 跑的是 **`--template-check`**，
  它**只校验 `loops/_template`**，**从不校验任何一个实际 loop 实例**。
  → **任何实例坏了都不会被发现**：我新建的 GK16 一直处于违规状态，而门禁全绿。
- **修复**：GK16 已按 schema 补齐并 **`loop-guard: PASS`**。
  **门禁缺口本身**（应增加"逐个实例校验"）登记为待办。

## T-07 【自我更正】我称 C4「回读证据」**未建** —— **错了，loop schema 早已强制**

- **经过**：为让 GK16 通过 loop-guard，读到它要求每个 `pass` 门禁必须提供
  `evidence_file`（须位于该 loop 的 `evidence/` 内）+ **`output_sha256` 哈希校验**
  + `actor` / `actor_role` / `executed_at`。
- **更正**：这正是我在 `GK-KE-自查方案逐项源代码举证-V1.0.md` 中
  列为 **C4「未建」**的那条控制 —— **loop 协议早已强制它。我的判断是错的。**
- **教训**：**宣布"某控制不存在"之前，必须在**整个仓库**搜索它，而不只是在预期的地方。**
  这与 FAIL-43（一次 `ls` 就宣布 workspace 不存在）**同族**，
  且发生在**同一份文档、同一天**。

## T-08 【攻击未果·已登记】`loop_guard` 的证据状态词表**无 `inconclusive`**

- **现象**：`ALLOWED_EVIDENCE = {pending, pass, fail, blocked}`。
  本 Loop 的 `gate-injection-tests` 判 INCONCLUSIVE（覆盖不完整），
  **无法在 loop 协议中如实表达**，只能有损映射为 `blocked`。
- **为何是问题**：判据系列已确立「**INCONCLUSIVE ≠ 通过**」为核心纪律；
  而 loop 协议**无该态**，迫使使用者用 `blocked` 或 `fail` 代替 ——
  两者都**丢失"未产生结论"这一语义**。
- **处置**：已在 `observed` 字段**显式标注该有损映射**并登记为协议缺口。
  **未擅自修改 `loop_guard.py`**（共享门禁，改动需独立复核）。

## 停止声明

> **反角色已无法构造新的可执行反例推翻现存结论。**
>
> - 所有结论均经至少一次**可执行**攻击（§T-01～T-06 皆为攻击命中，T-04 为攻击未果但路径已登记）
> - 剩余缺口（T-05 表 9 项 + T-06 门禁缺口 + T-08 词表缺口）**已如实登记，不可隐藏**
> - **本 Loop 不声称"18 个门禁都有负例测试"**：现状是 **11 项有受控检出证据，9 项没有**
>
> **停止不是"没有问题"，而是"我已无法再找出未被登记的问题"。**
> 二者差别，正是本 Loop 全部工作的意义。
