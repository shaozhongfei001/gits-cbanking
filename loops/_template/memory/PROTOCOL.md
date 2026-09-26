# Shared-memory protocol

## 开场

读取Git状态、`SHARED_MEMORY.md`、`NEXT_SESSION.md`、`ROLE_BOARD.yaml`、dispatch和最近handoff。holder不匹配时停止。

**TL / 架构角色追加**（`docs/governance/CODE-FACT-INDEX-PROCESS.md`，GOV-CFI-001）：
先查代码事实索引（`.ua/knowledge-graph.json`）建立模块视图与候选影响面，再回源验证；
开工声明中给出三行 `[索引] INDEX_FRESH|STALE(n)|ABSENT` / `[索引] 候选影响面` / `[回源] 文件:行`，
并把结果写入本Loop的 `memory/INDEX_BASIS.md`。索引是 DERIVED 派生视图，不得作为事实引用。

## 迭代

Plan → Build → Measure → Learn。每次命令通过 `scripts/record_gate.py`执行，失败自动先写 `FAILURES.md`和ITER；最多5次，之后置`blocked`。

## 收工

更新handoff、共享记忆、角色板、下一棒、状态和dispatch，运行memory/evidence check。开发只可交付`ready_for_independent_qa`。

**TL / 架构角色追加**：在 `INDEX_BASIS.md` 追加本批次新得到的回源结论，
并在收工声明中声明索引新鲜度；超过阈值（>50提交 / >14天 / 结构性变更）先跑刷新SOP，
再运行 `make index-status`（严格阻塞用 `make index-status STRICT=1`）。
