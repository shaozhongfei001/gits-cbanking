# PC-i1-chapter-inheritance｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`


## 独立 QA（非正式复验）— 导航

> 本节**只做导航**，不复制状态（状态以 `EVIDENCE.json` / `STATE.json` 为准；`EVIDENCE.json.independent_qa` 仍为 `pending`）。

| 产物 | sha256（前 32） |
|---|---|
| `independent-qa-gitdiff-W2-tests-20260923-1101.txt` | `8acc36c9acf4ecf39b9ae37b72a780da…` |
| `independent-qa-pc-i1-20260923-1101.md` | `d59a01098a4608e474379e4a77d6f251…` |
| `independent-qa-per-chapter-20260923-1101.json` | `484e7f285cd8dc7df9f81e7dd5b974b2…` |
| `independent-qa-replay-spec-b4-per-chapter-20260923-1101.json` | `e50897bcc61dc2cf043362c83bc37e5e…` |
| `independent-qa-replay-spec-d1-cross-page-20260923-1101.json` | `9c08aceeb59c5bc84e68b9aab6a88c80…` |
| `independent-qa-replay-spec-e1-pending-20260923-1101.json` | `ac5fcf70d21d65c371c2aa4b52fa8921…` |
| `independent-qa-replay-spec-e2-demo-20260923-1101.json` | `a097d55878e4fb771975a7c2cfeb2c1a…` |

- 报告：`evidence/independent-qa-pc-i1-20260923-1101.md`（actor=`independent_qa`，session=`qa-pc-i1-independent-20260923-1101`）
- 引用其结论（**不改写**）：「W-1/W-2 本体：独立复验通过」「loop 出口：BLOCKED，不得签 QA_PASS」
- 阻断项：`F-PC-i1-04`（R-1/R-2 待授权）· `contract_check` 门禁仍 fail（真实失败项 = `loop-instances`，QA-1 已更正归因）
- **本目录 `independent-qa-*` 文件为独立 QA 所有，任何 implementation actor 不得删改/覆盖。**


---

## 更正（append-only · 2026-09-23T05:33:14+00:00）

上文「独立 QA（非正式复验）— 导航」节写于**非正式复验期**，其中
「`EVIDENCE.json.independent_qa` 仍为 `pending`」**已过期**，**原文保留不改**：

| 时点 | `independent_qa` | 依据 |
|---|---|---|
| 非正式复验期（该节写作时） | `pending` | 当时无正式签署 |
| 2026-09-23T04:29:40Z | `reject` | `evidence/independent-qa-formal-20260923-1227.md`（sha256 `766cb36d…be`） |
| **2026-09-23T05:17:24Z（现行）** | **`pass`** | `qa_attest.py --decision pass` · 会话 `qa-pc-i1-reverify-20260923-1316` · `evidence/independent-qa-reverify-20260923-1316.md`（`db093f7086bf059d…`） |

> 状态以 `EVIDENCE.json` / `STATE.json` 为唯一权威（本节与上文导航节均**只作导航**）。
