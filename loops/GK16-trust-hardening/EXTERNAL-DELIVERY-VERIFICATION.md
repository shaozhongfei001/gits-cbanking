# 外部交付验收：30 个 loop 实例合规修复

> **TL 验收记录。** 外部执行者交付后，本 TL **不采信报告，先攻报告**。
> 验收结论：**交付属实；7 项 schema 问题中 4 项已修、3 项登记。**

---

## 一、机械声明验证（全部通过）

| 报告声称 | 实测 | |
|---|---|---|
| `--instances-check` exit=0，58/58 合规，基线 0 条 | ✅ 完全一致 | |
| `knownNonCompliant` 由 30 条清空为 `[]` | ✅ | |
| 未改 `scripts/loop_guard.py` | ✅ `git status scripts/` 为空 | |
| 未向基线新增条目 | ✅（基线已空，平凡成立） | |
| 未伪造 pass | 见 §二 | |

---

## 二、对"如实"声明的**主动攻击**（这是验收的重点）

**报告说"未伪造 pass"。我不接受声明，构造了 4 个攻击。**

| # | 攻击 | 结果 |
|---|---|---|
| 1 | **删门禁换合规**：把 `LOOP.yaml` 与 `EVIDENCE.json` 的 gates 都清空 —— 集合就"匹配"了 | ❌ **被挡下**：`LOOP gates must be a non-empty array`（schema 已有防护） |
| 2 | **status 变更方向**：逐条比对 `git show HEAD:` 与工作区 | ✅ **14 处全为降级**（`qa_pass`/`closed`/`ready_for_independent_qa` → `in_progress`），仅 1 处上升 |
| 3 | **gate 升格**：`pending`/`fail`/`blocked` → `pass` | ✅ **零处** |
| 4 | **删除文件** | ✅ **删除数 = 0** |

**唯一"上升"是 `P0: completed → closed`，单独深查：**

- `completed` **不在** `ALLOWED_STATES`（非法值），必须迁移；
- `independent_qa-P0-pass.json` **真实存在**，含 `qa_actor`、`verdict: QA_PASS`、
  5 个 gate 的 command+result、`independent_verification`（`make check` exit 0）；
- `ROLE_BOARD.baton.holder = independent_qa`，符合 schema 对评审态的要求；
- 5 个 gate log 均有实际内容。

→ **判定：如实更正，非美化。** 攻击 4 项全部未命中。

> **补充说明**：`diff --stat` 显示 1567 增 / **2755 删**，初看像"删内容换合规"。
> 实测**删除文件数 = 0** —— 那些"删除"是**文件内格式重写**（旧 YAML → v2.0 JSON）。
> **这正是"看统计数字会误判、必须看实际改动"的又一个例子。**

---

## 三、7 项 schema 问题的处置

### 已修（4 项）

**问题 2：`.log` 被 `.gitignore` 排除 → 证据从不入库 → 已完成 loop 的证据整体丢失**
- 实测：`.gitignore:33` 的 `*.log` 使 `loops/*/evidence/*.log` 被忽略；
  P5/P6/P21/P22 因此**只能降级 pending**。
- **修复**：新增 `!loops/**/evidence/*.log` 等例外。
  实测 `git check-ignore` 确认证据 log 现**可入库**。
- **为何重要**：这是**结构性证据丢失** —— 不是某人疏忽，而是**规则导致证据永远留不下**。

**问题 4：`ACTOR_PATTERN` 拒绝大写 → 迫使重命名历史执行者**
- 实测：`^[a-z][a-z0-9_-]{2,63}$` 拒绝 `AI-Agent`（P18）。
  唯一"合法"做法是**把历史执行者改名 = 改写历史**。
- **修复**：放宽为 `^[A-Za-z][A-Za-z0-9_-]{2,63}$`（允许大写，仍排除占位符/空白）。
- **理由**：该模式的**目的**是排除占位符，**不是规范命名风格**。

**问题 1：红测/负例 gate 无法表示（GKB）**
- 实测：GKB `repro_baseline` 的 `pass_condition` = 「在不改实现的前提下**复现基线 4 errors**」
  ⇒ **期望 exit≠0**；而旧 schema 规定 `pass ⟺ exit_code=0` ⇒
  **红测只能记 fail** ⇒ `ready_for_independent_qa`（要求全 pass）**永远不可达**，
  本可 QA 就绪的 loop 被迫降级。
- **修复**：新增 `expected_exit_code`（正整数，缺省 0）；`pass` 要求 `exit_code == expected_exit_code`。
- **防滥用（关键）**：该字段可被用来把"失败"洗成"通过"。
  缓解办法是**可见性而非隐藏** —— 任何非零 `expected_exit_code` **每次运行都被打印**：
  ```
  [REVERSE-GATE] **1 个 gate 的通过条件是『命令失败』**（负例/红测）：['repro_baseline(expected_exit_code=1)']
  [REVERSE-GATE] 请核对其 pass_condition 与证据输出确实构成负例验证，而非把失败记为通过。
  ```
  **残余风险如实登记**：若有人滥用，唯一能发现的是读输出的人的审视。
  **本仓的纪律是"不隐藏"，不是"不可能滥用"。**
- **GKB 已据此更正为如实记录**（不是放宽）：
  证据 log 实测 `[ERROR] Tests run: 4, Failures: 0, Errors: 4` + `BUILD FAILURE`，
  **与 pass_condition 精确吻合**（7 处 `NoSuchBeanDefinitionException`，含 `CustomerJourneyRepository`）。

**问题 6：文档型 gate 需空 command（GKC）**
- 实测：`impact_assessment`（产出文档盘点）原 command 为空，被"non-empty executable command"拒绝，
  执行者只能填 `manual: ...` 占位 —— **而该占位恰好绕过了 `FORBIDDEN_COMMAND_PARTS`**，
  **是一个"看起来合规"的逃生口**。
- **修复**：**显式允许** `manual: <path>`，但**强制** `<path>` 必须存在且位于该 loop 的 `evidence/` 内。
  > **把隐式逃生口变成显式受约束形式** —— 否则它会继续以"合规"的面目存在。

### 登记未修（3 项）

| # | 问题 | 为何不在本次修 |
|---|---|---|
| 3 | `completed` 非 `ALLOWED_STATES` | **不应加入** —— 它是**歧义的历史同义词**（是 `qa_pass` 还是 `closed`？）。加入会永久保留歧义。**正确做法是登记迁移规则**：`completed → in_progress`，除非存在独立 QA 证据则可判 `closed`。**执行者正是这样做的**（P0 有独立 QA → `closed`；P6 无 → `in_progress`），**处置正确**。 |
| 5 | 旧格式无迁移路径（P 组 / L 组各一套） | 需**独立迁移脚本**（解析旧结构 → 生成 v2.0），属独立工作项。**执行者已如实声明丢失了 `gaps`/`acceptance`/`work_packages` 细粒度结构（仅存 git 历史）** —— 该声明本身是诚实的。 |
| 7 | `independent_qa` 同时作 gate 与 block | **约定问题，非 schema 缺陷**。登记约定：独立 QA 证据写入 `independent_qa` block，**不列为 gate**。 |

---

## 四、验收结论

> **外部执行者的交付属实。**
> - 30/30 修复，基线清空，棘轮保持 exit=0；
> - **未改共享门禁、未删证据、未升格任何 gate、未伪造 pass**；
> - 14 处 status 变更 13 处为降级，唯一上升经深查**证据真实**；
> - **7 项 schema 问题全部是真问题**，其中 4 项已修，3 项已登记并给出处置理由。
>
> **本验收本身也产生了产出**：一个初看像"删内容换合规"的统计（2755 删除）
> 经实测是格式重写（删除文件数 = 0）—— **该误判已在 §二 记录，供后人避免。**

**门禁链：22/23，唯一 FAIL 为 `semantic-consumption`（独立判定，TL 不代判）。**
