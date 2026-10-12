# 独立 QA 正式复验 · ADDENDUM 01（**签署后观察，append-only**）

| 项 | 值 |
|---|---|
| 挂靠主报告 | `independent-qa-formal-20260923-1227.md`（sha256 `766cb36d2d3853d23685b0edf407b51f69c499e63102314c5cb7548f7e6530be`，**未改写**） |
| 会话 | `qa-pc-i1-formal-20260923-1227` × actor=`independent_qa` |
| 记录原因 | 主报告签署**之后**才可观测的状态后果；按本仓 append-only 纪律**另开文件**，不改写已记录哈希的主报告 |
| 角色边界 | 本追加**只新增证据**；未改 `STATE.json` / `ROLE_BOARD.yaml` / `NEXT_SESSION.md` / `LOOP.yaml` / 任何产品代码 |

---

## 一、观察到的事实（可复现）

签署命令（主报告 §四逐字）：

```bash
python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
  --actor independent_qa --session qa-pc-i1-formal-20260923-1227 --decision reject \
  --evidence loops/PC-i1-chapter-inheritance/evidence/independent-qa-formal-20260923-1227.md
# ⇒ loop-guard: PASS   ATTEST_EXIT=0
```

签署**前后**的 loop 合规度对比（同一命令，同一机器）：

| 时点 | `loop_guard.py --loop` | `--instances-check` |
|---|---|---|
| 签署前（本轮 §〇 前置自检） | **PASS** | **69/69 合规**、0 不合规 |
| **签署后** | **FAIL**：`STATE implementation_actor and Baton holder disagree`（exit 2） | **68/69**：`**1 个新增不合规实例**（不在基线中 ⇒ 不得豁免）：- PC-i1-chapter-inheritance` |

原始输出：`evidence/independent-qa-formal-post-signature-loopguard-20260923-1227.log`

根因（回源，非推断）：

| 位置 | 事实 |
|---|---|
| `scripts/qa_attest.py:50-52` | `reject` ⇒ `state["status"]="blocked"`、`blocked=True`、`blocking_reason="INDEPENDENT_QA_REJECTED"`；**不**触碰 `implementation_actor` |
| `scripts/loop_guard.py:144-148` | review 状态集合 = `{ready_for_independent_qa, qa_pass, closed}`；**`blocked` 不在其中** ⇒ 走 `elif`：要求 `state["implementation_actor"] == ROLE_BOARD.baton.holder` |
| 实测字段 | `STATE.status=blocked` · `STATE.implementation_actor=`**`tech_lead`** · `ROLE_BOARD.baton.holder=`**`independent_qa`**（TL 交棒时置，未回收） |

⇒ **`qa_attest.py --decision reject` 与 `loop_guard.py` 对「reject 之后谁持 baton」的契约不一致**：前者把 loop 推进 `blocked`，后者把 `blocked` 判为非 review 态并要求实现者持棒；而交棒后的 `ROLE_BOARD` 仍指向 `independent_qa` ⇒ 必然产生 1 个新增不合规实例。

## 二、我做了什么 / 没做什么

- **做了**：执行主报告 §四的**唯一**签署路径；把结果与前后合规度**如实登记**（本节）。
- **没做**：**未**手工改 `STATE.json.status`、**未**改 `ROLE_BOARD.baton.holder`、**未**改 `NEXT_SESSION.md`（§0.1 边界：我不得改 `loops/**` 既有受控文件；且这两处恰是解除本不合规所需的字段）。
- **未做的事也不构成"掩盖"**：本不合规**不是产品缺陷**，也不是主报告 QA-B1/QA-B2 的一部分；它是**签署动作本身的副作用**，唯一后果是「loop 实例合规度不再是 69/69」。

## 三、归属与建议（需 Owner / 收口裁决）

| 选项 | 内容 | 备注 |
|---|---|---|
| A（推荐） | 由 **TL/实现侧**把 baton 收回（`ROLE_BOARD.baton.holder` + `NEXT_SESSION.md` holder 同步为 `tech_lead`），状态保持 `blocked` ⇒ 合规度应恢复 69/69；随后按主报告 §四「解除路径」修 QA-B1/QA-B2 | 属实现侧动作（改 `loops/**`），**不在我的角色边界内** |
| B | 裁决 `blocked` 是否应视为「review 态」以修正 `loop_guard.py:144` 的状态集合 | 门禁脚本改动，需 Owner 授权（参照 R-1 的授权方式） |
| C | 裁决 `qa_attest.py` 在 `reject` 时是否应同时把 baton 交回 implementation actor | 若采纳，需同步 `loop_guard.py` 的契约 |

**红线提示**：无论选哪条，**不得**为了消除本不合规而把 `EVIDENCE.json.independent_qa.status` 从 `reject` 改回 `pending` 或 `pass`（那将构成对已登记独立 QA 结论的篡改）。

## 四、一句话

`qa_attest.py --decision reject` 是**按主报告 §四逐字执行**的，其**副作用**是 loop 实例合规度由 `69/69` 变为 `68/69`（`loop_guard: FAIL: STATE implementation_actor and Baton holder disagree`）；该副作用由「脚本只改 `status=blocked`、不交回 baton」与「`loop_guard` 把 `blocked` 判为非 review 态」两个**工具契约不一致**共同造成，按 §0.1 我**无权**修改相关受控字段，故如实登记于此并请求 Owner/收口裁定（建议选项 A）。

---

*ADDENDUM 01 生成：2026-09-23 12:33（本地）× actor=`independent_qa` × session=`qa-pc-i1-formal-20260923-1227`*
