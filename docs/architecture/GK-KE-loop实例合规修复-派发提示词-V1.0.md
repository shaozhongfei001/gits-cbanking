# 派发提示词：30 个历史 loop 实例的合规修复

> **交给谁**：外部执行者（人或智能体）。
> **能否由智能体完成**：**能，且高度适合自动化** —— 每条修复都有**机械可验证的判据**
> （跑一条命令，看是否从"不合规"变为"合规"）。
> 唯一需要判断力的地方是**语义字段该填什么**（见 §四），那部分需要读该 loop 自己的历史。

---

## 一、任务

本仓 `loops/` 下有 **58 个 loop 实例**，其中 **30 个不符合 loop 协议 schema**。
`loop-guard` 门禁**过去从不检查它们**（它只校验模板），所以这 30 条欠账长期不可见。

现已建立**棘轮**：这 30 条被冻结在基线中，**新增不合规实例会被门禁拦截**。
**你的任务是逐条修复这 30 条，每修好一条就把它从基线移除。**

> **这不是"清库存"式的批量改写。** 每条修复都会**改变该 loop 的证据链状态**，
> 因此必须逐条读懂它原本在做什么，再补全缺失的契约字段。

---

## 二、先看清基线（你的工作清单）

```bash
cd <repo>
python3 scripts/loop_guard.py --instances-check
cat loops/_instance_baseline.json          # knownNonCompliant: 30 条
```

**你的进度判据**：基线条目数**单调下降**，且 `--instances-check` 始终保持 exit=0。
（棘轮会拦截新增违规；你只应**减少**条目，不应新增。）

---

## 三、单条 loop 的合规判据（机械，可自查）

```bash
python3 scripts/loop_guard.py --loop <loop-id>      # 期望：loop-guard: PASS
```

它会逐项报错。**已知的失败类型**（按实际出现频次）：

| # | 失败信息 | 含义 | 修法 |
|---|---|---|---|
| 1 | `unresolved placeholders: [...]` | `{{LOOP_ID}}` 等模板占位符未替换 | 按该 loop 的真实 id/holder/时间替换 |
| 2 | `baseline_commit must be a full Git SHA` | `STATE.json` 的 `baseline_commit` 缺失或非 40 位 SHA | 填该 loop **真实建立时**的完整 commit SHA（`git log` 找） |
| 3 | `NEXT_SESSION holder and ROLE_BOARD baton.holder disagree` | 两文件的 holder 不一致 | 统一。**注意格式**：`NEXT_SESSION.md` 中该单元格必须**恰好**是 ``| **holder** | `xxx` |`` |
| 4 | `STATE implementation_actor and Baton holder disagree` | `STATE.json` 缺 `implementation_actor` | 补，且与 `ROLE_BOARD.baton.holder` 一致 |
| 5 | `EVIDENCE gate set must exactly match LOOP gates` | `EVIDENCE.json` 的 gates 与 `LOOP.yaml` 的 gate id 集合不同 | 逐一对齐（**不得增删 gate**，只对齐集合） |
| 6 | `gate X: invalid evidence status` | 状态取值非法 | 只允许 `pending / pass / fail / blocked / inconclusive` |
| 7 | `gate X: pass requires exit_code=0` | 标 `pass` 但无 `exit_code` | 补 |
| 8 | `gate X: pass requires actor, role and timestamp` | 缺 `actor` / `actor_role` / `executed_at` | 补（字段名就是这三个） |
| 9 | `gate X: evidence file required` / `evidence must be inside the loop evidence directory` | 缺 `evidence_file` 或路径不在该 loop 的 `evidence/` 下 | 生成证据文件放进去 |
| 10 | `gate X: evidence file missing or hash mismatch` | `output_sha256` 与实际文件哈希不符 | 重算并回填 |

> **`pass` 的完整要求**（最常踩）：
> `status="pass"` + `exit_code=0` + `actor` + `actor_role` + `executed_at`
> + `evidence_file`（位于 `loops/<id>/evidence/` 内）+ `output_sha256`（与该文件实际哈希一致）。

---

## 四、需要判断力的部分（**不得机械填写**）

上面是格式。**下面是实质，必须逐条判断：**

1. **`baseline_commit` 必须是该 loop 真实建立时的 SHA** ——
   **不得**填当前的 `HEAD`（那会伪造时间线）。用 `git log --diff-filter=A -- loops/<id>/` 找。
2. **`status` 必须反映该 loop 的真实状态** ——
   已完成的写 `pass`，当时失败的写 `fail`，**未完成的写 `pending` 或 `blocked`**。
   > **严禁**为了变绿而把 `fail` 改成 `pass`。
   > **若某 gate 当时确实失败了，正确做法是 `status="fail"` 并保留证据文件与哈希** ——
   > **`fail` 是合规状态**，`fail` 不违反 schema。**伪造 `pass` 才违反。**
3. **`evidence_file` 必须是真实的原始输出** ——
   若原始证据已不存在，**如实写"证据已丢失"并保留为 `pending`/`blocked`**，
   **不得编造一份看起来像样的输出**。
4. **`actor` 必须是真的执行者** —— 不要把你的名字填成历史执行者。
   若无记录，写 `unknown` 并说明。

> **核心纪律**：**修复的目标是"让记录如实"，不是"让门禁变绿"。**
> 一条如实记录为 `fail` 的 gate，比一条伪造为 `pass` 的 gate **有价值得多**。

---

## 五、验收

```bash
python3 scripts/loop_guard.py --loop <loop-id>       # 每条：PASS
python3 scripts/loop_guard.py --instances-check      # exit=0 且基线条目数下降
python3 scripts/run_gates.py                         # 不得引入新的 INTEGRITY FAILURES
```

**你必须交付**：
1. 修改后的 `loops/_instance_baseline.json`（条目数 = 未修复数）；
2. 一份逐条记录表：`loop-id | 修复了什么 | 失败类型 | 是否如实（若有证据丢失，写明）`；
3. **你在修复过程中发现的、schema 本身的问题**（若你发现某条错误信息误导、
   或某条要求无法用现有字段如实表达，**这是重要发现，必须报告** ——
   本仓已有先例：loop 证据词表原先没有 `inconclusive`，导致两个真实判定被迫有损映射）。

---

## 六、边界

- **不得**修改 `scripts/loop_guard.py`（共享门禁，改动需独立复核）；
- **不得**修改基线里**没有**列出的 loop；
- **不得**通过往基线里**增加**条目来"消除"报错 —— **基线条目数只能减少**；
- **不得**为了通过而放宽任何 schema 约束。

**如果你认为某条 schema 约束本身是错的，正确做法是报告它，而不是绕过它。**
