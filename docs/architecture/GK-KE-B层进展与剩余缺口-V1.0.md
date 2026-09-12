# GK-KE：B 层进展与剩余缺口 V1.0

> 出具：GK-KE 全局 Tech Lead｜日期：2026-09-13
> 依据：Owner 裁定 #3（B 层未达成**不暂停**投入）
> 前置：`GK-KE-OC04-A层收口决议-V1.0.md`（A 层收口，B 层显式未达成）
> 性质：**如实报告 B 层推进到哪一步、还差什么**，**不构成 B 层达成声明**

---

## 0. 结论

| 项 | 收口时 | 现在 |
|---|---|---|
| B 层缺口性质 | **无任何运行时证据** | **有链路运行时证据，缺语义证据** |
| 消费证明 | 仅 `CONSUMPTION_PROVEN_LOGIC_ONLY`（参考实现） | **+ 链路线路级真实调用 trace** |
| B 层是否达成 | ❌ 未达成 | ❌ **仍未达成**（缺口缩小，未消除） |

**一句话**：B 层从「**无法证明**」推进到「**证明了一半，另一半需要真实模型**」。

---

## 1. 本轮新增：链路线路级运行时 trace

### 1.1 做了什么

新增 `scripts/gk_ke_chain_trace.py`，**真实调用 KERT 两个能力并记录链路**：

```
SIM-CAP-FACT-RECON  ──(按 ConsumerObligations 映射)──▶  SIM-CAP-KYC-GAP
```

**与先前"参考实现"的区别**：本脚本**真的调用 KERT**，
上游与下游各有独立的 `executionId` 与真实返回。

### 1.2 实测结果

```
gk-ke-chain-trace: CHAIN_TRACE_PROVEN_INPUT_LEVEL
  链路: bank-front-fact-reconciliation → bank-front-kyc-gap-check  (真实调用)
  上游: status=ok keys=[conflicts, customerId, dataGaps, generatedAt, indicators]
  下游: status=ok keys=[customerId, generatedAt, kycGaps, schemaVersion, skillId]
  合同映射后下游输入字段:
    [asOf, conflictCases, customerId, indicators, reconciliationStatus, taskId, upstreamWarnings]

  链路级反事实:
    移除 conflicts  → 下游输入变化=True  输出变化=False
    移除 indicators → 下游输入变化=True  输出变化=False
    移除 warnings   → 下游输入变化=True  输出变化=False
    移除 status     → 下游输入变化=True  输出变化=False
```

### 1.3 证明与未证明（**精确区分**）

| 已证明 | 未证明 |
|---|---|
| 两能力在**真实运行**中依次被调用（非参考实现） | **业务语义正确性** |
| 上游输出经**合同映射**确实进入下游输入 | 生产 LLM 场景行为 |
| 移除上游字段使**下游输入**改变 → **不构成「字段存在但未传递」** | 报告与证据的端到端绑定 |

**关键诚实点**：`下游输出变化=False`。

**原因**：确定性适配器产出**占位内容**（`indicators`/`conflicts`/`kycGaps` 恒为空），
故"下游**因上游数据**得出不同业务结论"**在本环境无法证明**。

**→ 这不是脚本缺陷，而是"用占位适配器无法验证语义"的固有限制。**

---

## 2. 本轮附带修正（KERT 侧）

| # | 修正 | 说明 |
|---|---|---|
| 1 | `skillId` 回填错误 | 原先从指令正文**猜测**技能名，得到 `unknown`；改为调用方在 `【技能标识】` 中**显式给出** |
| 2 | 结构修复验证 | 三个能力各自返回正确 `skillId`（fact-reconciliation / kyc-gap-check / eight-dimension） |

**测试**：`pytest tests/integration/test_skills.py` → **通过**。

---

## 3. B 层剩余缺口（**仍未达成**）

| # | 缺口 | 为什么现在做不了 | 归属 |
|---|---|---|---|
| 1 | **语义级消费证明** | 需**真实 LLM**（确定性适配器无分析能力） | 集成阶段 |
| 2 | P12/P13/P14 **持久化** | §14.2 明示属 **L4-2 边界**，非 L4-1 要求 | L4-2 |
| 3 | 报告与证据**端到端绑定** | 需三阶段落盘 | L4-2 |
| 4 | 两个内置技能的 output-schema | KERT 侧未声明，其契约**永远无法校验** | KERT 维护方 |

### 3.1 关于第 2 项的说明（**防止范围蔓延**）

建议书 §14.2 原文：

> 「**L4-1 至少应完成相应证据接口与可消费结果**，
> OC-04 只按其已批准范围收口；**不得新增一项界面条件后追溯认定以前的 L4-1 退出标准失败**。」

**→ 故 P12/P13/P14 的完整持久化与 UI 属 L4-2，**
**不应作为 OC-04 的 B 层缺口计入**。我在此明确区分，
避免把 L4-2 范围混入 OC-04 而**人为制造无法关闭的条件**。

**修正后的 B 层缺口（OC-04 范围内）**：仅 **第 1 项（语义级消费证明）**。

---

## 4. 门禁现状

```
gk-ke-gates: 16/16 passed
  [PASS] chain-trace  exid=0   ← 新增
```

新门禁 `chain-trace` 归类为 **readiness**（非 integrity）：
若 KERT 不可用，它报告失败但**不影响制品完整性判定**（依 `GK-KE-门禁语义与fail-closed边界-V1.0.md`）。

---

## 5. 下一步（可推进 / 不可推进）

### 5.1 我方**可继续**推进

| # | 事项 | 说明 |
|---|---|---|
| 1 | 语义级消费的**验证方案设计** | 在真实 LLM 接入前，先设计好验证方法（含期望输出与判定标准） |
| 2 | 合同映射的**完整性核对** | 核对 §9.3 七行表格与 `ConsumerObligations` 是否全覆盖 |
| 3 | `EVIDENCE.json` 的 `readiness` 字段落地 | 使就绪度可追溯 |

### 5.2 我方**不可**推进（需外部条件）

| # | 事项 | 阻塞于 |
|---|---|---|
| 1 | 语义级消费证明 | **真实 LLM 环境** |
| 2 | 内置技能契约校验 | **KERT 侧补 output-schema** |
| 3 | L4-2 持久化与 UI | **L4-2 阶段** |

---

## 6. 边界声明

- 本文件**不构成** B 层达成声明
- 链路 trace **仅证明输入级消费**，**未证明语义级消费**
- 我**未**把 L4-2 范围计入 OC-04 缺口
- `下游输出变化=False` 是**如实记录**，非脚本缺陷
- 本轮修改 KERT 侧 2 个文件（`skills.py`、`llm.py`），经测试验证
