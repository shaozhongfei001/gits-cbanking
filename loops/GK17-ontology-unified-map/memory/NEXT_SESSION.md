# GK17-ontology-unified-map｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-15` |
| **holder** | `tech_lead` |
| **packet** | `GK17-ontology-unified-map` |
| **wave** | `W0 → W1` |
| **status** | `in_progress`（**未收敛**） |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED、ADR Accepted |

---

## 一句话状态

> Owner 已批准「C 分工 + 投影」读法；本 Loop 要用**实例**验证
> 「本体承担结构化与非结构化知识统一地图、知识路由」是否成立 ——
> 判据是论证件里的 **V1 + V2/V3/V4 三个反例**，**反例不通过则 C 不成立**。

---

## 本 Loop 的编排与边界

- **长程编排**：`docs/dispatch/GK17-ontology-unified-map-长程编排-V1.0.md`（W0–W8，含派工与文件所有权）
- **第一原则**：**并行读 + 串行写**（依据 GK16 `T-24` 实测：门禁并发会互相污染并产生假 FAIL）
- **单写者独占**：`specs/semantic/`、`specs/knowledge-architecture/`、`generated/`、Loop 记忆
- **禁止**：改封版 `docs/dd/gk-ke-contract/`、手工编辑 `generated/`、解除 `_public_reference` 红线、启用隔离资产、代签 QA_PASS

---

## 当前进度

| Wave | 状态 | 说明 |
|---|---|---|
| W0 | **in_progress** | Loop 已建、编排已落盘；**待记录全量门禁基线**（含既有红灯） |
| W1 | **dispatched** | WP1.1–WP1.4 本体扩展（合同先行）；**写串行** |
| W2–W8 | not_started | 见编排表 |

**已完成的先导增量**（本 Loop 之前）：
- `edc4a55` 本体补入地图引用的 5 个 ID 空间（`KnowledgeMap`/`TaskType`/`Asset`/`Skill`/`ActivationContract`）+ 4 关系
- `76c1371`/`b072be9`/`79fbf38` 论证件（含具象说明与"非 A/B 更好"澄清）

---

## 下一棒要做的第一件事

1. 跑并记录**基线快照**：`make check`、`python3 scripts/run_gates.py`、`make backend-test`、`make frontend-test`
   —— **记录既有红灯，防止把既有问题算到本 Loop**；
2. 按 `WP1.1 → WP1.4` **串行**扩本体（合同先行：改源 → `make generate` → `make check`）；
3. 每步经 `scripts/record_gate.py` 落证；失败**先写 `FAILURES.md` 再修**。

---

## 短提示词

```text
你是 tech_lead，做 GK17 的 W0+W1。读 docs/dispatch/GK17-ontology-unified-map-长程编排-V1.0.md
与 loops/GK17-ontology-unified-map/。并行读 + 串行写；门禁串行执行。
只做 W0+W1；完成后 STOP 并在 ORCHESTRATOR 记 tick。
```
