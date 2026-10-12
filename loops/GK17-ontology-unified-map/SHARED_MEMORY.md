# GK17-ontology-unified-map｜Shared Memory

> Chat不是SSOT；未落盘等于不存在。

## Current Snapshot

| 字段 | 值 |
|---|---|
| status | `in_progress`（未收敛） |
| baseline_commit | `79fbf38` |
| baton_holder | `tech_lead` |
| current_wave | `W0 → W1` |
| updated_at | `2026-09-15` |

## 命题与判据（**不可漂移**）

**命题**：用本体模型承担「结构化与非结构化知识的统一地图」与「知识路由」的定位。

**已批准读法（Owner 2026-09-15）**：候选 C「分工 + 投影」是**唯一可行项**，
代价是必须补三条硬约束；**A/B 不可行**（A 与总契约 §5/§7 冲突且实践中退化为无约束的 C；
B 与 `RP-CORP-RM-001` 已配置的 `ONTOLOGY_FIRST` 理由冲突）。

**三条硬约束**：
1. **单一权威**：一条事实只有一个地方能改；
2. **引用锚定 + 查不到即拒绝**：引用必须在权威源可解析，否则规划 fail-closed；
3. **投影只读可重建**：人读层不算权威。

**判据（V1–V4）**：V1 链路跑通；**V2** 只改本体不改地图 ⇒ 计划必须变；
**V3** 引用本体不存在个体 ⇒ 必须拒绝；**V4** 手工制造不一致 ⇒ 门禁必须检出。
**V4 不过 ⇒ C 不成立** ⇒ 退路是**收窄并行范围**（不是改用 A/B）。

## 编排原则（第一原则）

> **并行读 + 串行写**。依据 GK16 `FAILURES.md` T-24 实测：
> 门禁并发运行会互相污染 `trace.json`/`gates.txt` 并产生**假 FAIL**。

单写者独占：`specs/semantic/`、`specs/knowledge-architecture/`、`generated/`、Loop 记忆。

## Role Results

| 角色 | 状态 | 范围 | 结果 |
|---|---|---|---|
| `tech_lead` | active | W0/W5/W6/W8 + 合同裁定 + 门禁执行 | W0 进行中 |
| `ontology_owner` | dispatched | W1（独占 `specs/semantic/`） | 待回报 |
| `routing_owner` | waiting_on_W1 | W2 | — |
| `abox_owner` | waiting_on_W1 | W3/W4 | — |
| `gate_owner` | waiting_on_W1 | W5 | — |
| `product_owner` | waiting_on_W2_W3 | W7 | — |
| `independent_qa` | unassigned | V1–V4 判定 | **必须独立会话，TL 不得代签** |

## 跨会话注意

2026-09-14 夜发现**另一执行者**在同一工作区提交（`82b70b4` Dockerfile 守卫）。
双方均按显式路径提交、互不纳入。本 Loop 只写 `LOOP.yaml.scope.include` 范围。
