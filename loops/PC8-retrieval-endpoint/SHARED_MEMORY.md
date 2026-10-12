# PC8-retrieval-endpoint｜Shared Memory

> Chat不是SSOT；未落盘等于不存在。

## Current Snapshot

| 字段 | 值 |
|---|---|
| status | planned |
| baseline_commit | `731853d0af5779b763f7a82a269b45aa1652e7ad` |
| baton_holder | `tech_lead` |
| current_wave | `W0` |
| updated_at | `2026-09-22T09:21:20.701832+00:00` |

## Role Results

| 角色 | 状态 | 结果 | Handoff |
|---|---|---|---|
| `tech_lead` | planned | - | `memory/handoffs/tech_lead.md` |

## 依赖与波次

| 字段 | 值 |
|---|---|
| wave | `W4` |
| depends_on | 依赖 PC8-tools-byproduct（需 Release/interpretation 产物） |
| deliverable | 新端点 + 合同 diff + 灌入记录(索引基线) + 重建对照证据（出处集合 Jaccard） |
| boundary | 不改 EGRESS_ROOTS；不把 01_raw 原文灌入；LightRAG 仅派生检索层——字段值不得取自检索 |
