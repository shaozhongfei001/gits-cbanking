# Shared-memory protocol

## 开场

读取Git状态、`SHARED_MEMORY.md`、`NEXT_SESSION.md`、`ROLE_BOARD.yaml`、dispatch和最近handoff。holder不匹配时停止。

**TL / 架构角色追加**（`docs/governance/CODE-FACT-INDEX-PROCESS.md`，GOV-CFI-001）：
先查代码事实索引（`.ua/knowledge-graph.json`）建立模块视图与候选影响面，再回源验证；
开工声明中给出三行 `[索引] INDEX_FRESH|STALE(n)|ABSENT` / `[索引] 候选影响面` / `[回源] 文件:行`，
并把结果写入本Loop的 `memory/INDEX_BASIS.md`。索引是 DERIVED 派生视图，不得作为事实引用。

## 迭代

Plan → Build → Measure → Learn。每次命令通过 `scripts/record_gate.py`执行，失败自动先写 `FAILURES.md`和ITER；**最多 8 次**（2026-09-21 由 `TL-DECISIONS-W-1.md` D-14 自 5 调整，D-15 规定不得再上调；**权威值以 `LOOP.yaml.repair_policy.max_attempts_per_gate` 为准**），之后置`blocked`。

## 阻塞与自愈（阶梯协议）

> 依据：`docs/dispatch/GK-KE-L0-2收敛总指挥部署.md` §0（SDD 06 契约 §4a 阶梯协议）+ `docs/dispatch/ONTO1-独立会话提示词汇总-V1.0.md`「六条提示词的共同收尾语」。本 Loop 适用同一口径；**未落盘 = 不存在**，故置于本节。

**先自愈，不停工询问**：可自行解决的技术/环境问题按三级阶梯自主处理，并在 `FAILURES.md` 留痕（先记后修）：

| 级 | 手段 | 本 Loop 实测例 |
|---|---|---|
| 1 自愈 | 修检查器/期望值形态、修脚本、补扫描模式、重跑**原命令** | 期望值形态错位（`FAIL-2026-09-20-01`）、处置表覆盖不足（`-02`）、种子矩阵取值错误（`-03`）、文书自身触发占位符红线（`-04`） |
| 2 降级 | 缩小范围并**如实标注**：`NOT_EVALUATED` / `INCONCLUSIVE` / `INDEX_STALE(n)`；**禁**把"无法判定"写成通过 | 索引未刷新时 KERT 结论一律回源 `文件:行`（声明陈旧，不用索引外推） |
| 3 回退 | revert 本会话改动回到上一绿基线；保留失败记录，不覆盖 | 基线本体全程只读锚定（`sha256 705578d6…`） |

**只有下列硬阻塞才允许停机**（四类 = 用户口径；第五类为仓内既有口径）：

1. **缺凭据**——只有外部/ Owner 能提供的签署件、凭据、标准正式文本；
2. **需求冲突**——合同/决议之间的语义矛盾，TL 无权裁定；
3. **方向性变更**——需 Owner 决议的路线改变（含扩大试点/改变波次结构）；
4. **安全隐患**——凭据泄露、越权、隔离资产（Oracle/Ossie）启用；
5. **自愈耗尽**——同一 Gate 连续失败达 `LOOP.yaml.repair_policy.max_attempts_per_gate`（**=8**，由 `scripts/record_gate.py` 对 `memory/waves/W0-ITER.md` 中 ``Gate: `<id>` `` 的出现次数计数；**该上限于 2026-09-21 由 `TL-DECISIONS-W-1.md` D-14 自 5 调整为 8**——因为"revision 变更后的重记"与"修复尝试"在计数上不可区分；**权威值一律以 `LOOP.yaml` 为准**，本行数字仅作导读）。

**停机动作（四件，缺一不可）**：

1. 写 `memory/BLOCKED.md`：阻塞类型（上述之一）、触发时间、证据（命令 + 退出码 + `文件:行`）、**被阻塞的具体动作**、最小解卡动作、需要谁裁决；
2. `STATE.json`：`status=blocked` + `blocking_reason` 填具体；**不**改 `gate_state.current`（门禁位置只由委员会结论改变，不因内部阻塞而变）；
3. Baton：`blocked` 属非 review 状态 ⇒ `ROLE_BOARD.baton.holder` 与 `NEXT_SESSION.holder` 必须仍等于 `STATE.implementation_actor`（`scripts/loop_guard.py:119-123`）；**不得**为"等人"把 holder 改成不满足 guard 规则的角色；
4. 通知：`NEXT_SESSION.md`「已知边界」写明阻塞与解卡条件；复跑 `make memory-check` + `make evidence-check`。

**红线**：

- 不得为绕过阻塞**自创状态**（如把 `RETURN_TO_HLD` 写成别的批准态）；
- 不得把"等外部签署"包装成"已完成"（未收到签署件 = 未发生）；
- 自愈/降级/回退过程中**不得**改动受审证据 `01`~`12`、`generated/`、`specs/`、封版 `docs/dd/`；
- **不得**用"可自愈"之名做越界动作（Wave 0 及以后仍须委员会结论）。

> **当前状态**：**无** BLOCKED 事项（`memory/BLOCKED.md` 未创建——不预建占位文件，避免把"空文件"误读成"已阻塞"）。

## 收工

更新handoff、共享记忆、角色板、下一棒、状态和dispatch，运行memory/evidence check。开发只可交付`ready_for_independent_qa`。

**TL / 架构角色追加**：在 `INDEX_BASIS.md` 追加本批次新得到的回源结论，
并在收工声明中声明索引新鲜度；超过阈值（>50提交 / >14天 / 结构性变更）先跑刷新SOP，
再运行 `make index-status`（严格阻塞用 `make index-status STRICT=1`）。
