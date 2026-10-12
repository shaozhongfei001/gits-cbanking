# 独立 QA 复验 · ADDENDUM 01（**签署后登记，append-only 新文件**）

| 项 | 值 |
|---|---|
| 挂靠主报告 | `independent-qa-reverify-20260923-1316.md`（sha256 `db093f7086bf059d4526d3752f34042a30a3f66ee591de1cb7fa3039f44ba362`，**未改写**） |
| 会话 / 角色 | `qa-pc-i1-reverify-20260923-1316` × actor=`independent_qa`（≠ `implementation_actor=tech_lead`） |
| 记录原因 | 主报告 §四 只写了「预期结果」；签署**之后**才有的事实（实际落盘值 + 签署后门禁合规度）按 append-only 纪律另开文件登记 |
| 角色边界 | 只**新增**本文件；未改 `STATE.json` / `ROLE_BOARD.yaml` / `NEXT_SESSION.md` / `LOOP.yaml` / 任何产品代码（其变更**只**由 `qa_attest.py` 产生） |

## 一、签署命令与实际结果

```bash
python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
  --actor independent_qa --session qa-pc-i1-reverify-20260923-1316 --decision pass \
  --evidence loops/PC-i1-chapter-inheritance/evidence/independent-qa-reverify-20260923-1316.md
# ⇒ loop-guard: PASS   ATTEST_EXIT=0
```

| 落盘项 | 实际值 |
|---|---|
| `STATE.json.status` | **`qa_pass`**（`blocked=false`） |
| `EVIDENCE.json.independent_qa.status` | **`pass`** |
| `…actor` / `…session` | `independent_qa` / `qa-pc-i1-reverify-20260923-1316` |
| `…attested_at` | `2026-09-23T05:17:24.459065+00:00` |
| `…evidence_file` / `…evidence_sha256` | `loops/PC-i1-chapter-inheritance/evidence/independent-qa-reverify-20260923-1316.md` / `db093f7086bf059d…` |

## 二、签署后门禁与合规度（**本轮无副作用**）

| 检查 | 签署后实测 |
|---|---|
| `loop_guard.py --loop PC-i1-chapter-inheritance` | **PASS**（exit 0） |
| `--instances-check` | **69/69 合规、0 不合规、0 基线冻结、无新增违规** |
| 与 `--decision reject` 的差异（对照上一轮 ADDENDUM-01） | 上一轮 `reject` 使 `STATE.status=blocked`（非 review 态）而 baton 仍指向 `independent_qa` ⇒ 触发 1 个新增不合规实例；本轮 `pass` ⇒ `qa_pass` 属 review 态集合 ⇒ **无该副作用** |

## 三、上一轮 `reject` 与其证据的可追溯性（再次复核）

| 对象 | 复核值 | 结论 |
|---|---|---|
| `evidence/independent-qa-formal-20260923-1227.md` | sha256 `766cb36d2d3853d23685b0edf407b51f69c499e63102314c5cb7548f7e6530be`（与 `EVIDENCE.json` 原登记值、与上一轮报告所述一致） | **未被改动，仍可追溯** |
| `…-ADDENDUM-01.md`、4 支探针（`.mjs`）、4 份探针 JSON、3 份变异 JSON、2 份门禁日志 | 本会话只读；未触碰 | **未被改动** |
| `FAILURES.md` 中 QA-B1 / QA-B2 / QA-N1 三条登记 | 原文保留（append-only） | **未被删改** |

⇒ `EVIDENCE.json.independent_qa` 由 `reject` 变为 `pass` 是 **`qa_attest.py` 协议内规定的正式复签**，不是对既有结论的篡改（主报告 §一「覆盖声明」已显式声明）。

---

*ADDENDUM 01 生成：2026-09-23 13:20（本地）× actor=`independent_qa` × session=`qa-pc-i1-reverify-20260923-1316`*
