# Shared-memory protocol

## 开场

读取Git状态、`SHARED_MEMORY.md`、`NEXT_SESSION.md`、`ROLE_BOARD.yaml`、dispatch和最近handoff。holder不匹配时停止。

## 迭代

Plan → Build → Measure → Learn。每次命令通过 `scripts/record_gate.py`执行，失败自动先写 `FAILURES.md`和ITER；最多5次，之后置`blocked`。

## 收工

更新handoff、共享记忆、角色板、下一棒、状态和dispatch，运行memory/evidence check。开发只可交付`ready_for_independent_qa`。
