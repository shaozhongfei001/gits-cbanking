# GK-KE WP06：能力间消费与 trace 设计 V1.0

> 执行：GK-KE 全局 Tech Lead（A1）｜Loop：`GK14-l4-0-capability-closure`｜日期：2026-09-12
> 依据：建议书 §9.3 / §9.4 / §14.2｜`GK-KE-OWNER-004`
> 基线：`06b1762`

---

## 0. 结论摘要

| 项 | 状态 |
|---|---|
| 结果合同（9 字段） | ✅ **已定义** |
| 消费义务（8 条） | ✅ **已定义** |
| 两条消费链 | ✅ **已定义** |
| **运行时 trace** | ❌ **未产出** |
| **§14.2「能力之间真正消费结果」** | ❌ **仍未达标** |

**必须说清**：本文产出的是**合同**，不是**证据**。
「能力之间真正消费结果」这一要求**尚未达成**。

---

## 1. 问题定义：什么算「真正消费」

建议书 §14.2 明确列出了**不能接受的替代**：

> 「`optional` 字段存在但未传递」

§9.3 末段进一步说明：

> 「`optional: [conflictCases]` 只能说明**结构可以省略字段**，
> 不能说明**业务接口已闭合**。」

**→ 因此"真正消费"必须满足**：

| # | 条件 |
|---|---|
| 1 | 上游**确实产出**该字段 |
| 2 | 下游**确实读取**该字段 |
| 3 | 下游输出**因此改变** |
| 4 | 该过程**有 trace 记录** |

**第 3 条是核心** —— 这也是我设计的**反事实检验**：

> **若移除上游该字段，下游输出是否改变？若不变，则不构成消费。**

---

## 2. 为什么不直接改通用 envelope

建议书 §9.3 原文约束：

> 「若既有受保护执行合同**不允许新增字段**，使用**经审查的领域载荷或版本化扩展**，
> **不直接修改通用 envelope**。」

### 2.1 既有受保护 envelope

KERT 侧统执行契约（`skills.py` 模块注释）：

```
requestId / status(ok|skill_error) / data / assemblyTrace / modelCalls
```

这**是受保护的** —— AGENTS.md 禁止绕过，跨仓更不应擅改。

### 2.2 我的处置

**9 个字段不进入通用 envelope，而承载于 `data` 层内的 `capabilityResult`**：

```
{
  "requestId": "...",           ← 既有通用 envelope，不动
  "status": "ok",               ← 既有，不动
  "data": {
    "capabilityResult": {       ← 新增：版本化领域载荷
      "taskId": "...",          ← §9.3 的 9 字段在此
      "entityId": "...",
      ...
    }
  },
  "assemblyTrace": [...],       ← 既有，不动
  "modelCalls": [...]           ← 既有，不动
}
```

**理由**：
- 通用 envelope **零修改** → 不破坏 KERT 侧既有契约
- 领域载荷可**独立版本化** → `CTR-KE-CAP-RESULT-ENVELOPE-001`
- 跨仓边界上**不施加结构性强制**

---

## 3. 结果合同（9 字段）

`specs/knowledge-architecture/contracts/CapabilityResultEnvelope.json`

| 字段 | 必填 | 关键语义 |
|---|---|---|
| `taskId` | ✅ | 三元组之一，不匹配则**拒绝消费** |
| `entityId` | ✅ | 防同名异主体（`SIM-C001`/`SIM-C011`） |
| `purpose` | ✅ | 权限与合规基础 |
| `asOf` | ✅ | **防时间泄漏**（关联 FAIL-2026-09-12-04） |
| `capabilityId` | ✅ | 能力身份 |
| `capabilityVersion` | ✅ | 不一致**不得拼接** |
| `inputDigest` | — | 支撑复算一致性（§10.3 计划摘要值） |
| **`status`** | ✅ | **`SUCCESS/PARTIAL/FAILED/NOT_RUN`** —— 本字段是**最关键的** |
| `result` | ✅ | 能力专属载荷 |
| `evidenceRefs` | ✅ | 为空则结论**不得被引用为已证实** |
| `limitations` | ✅ | 下游**必须展示**而非隐藏 |
| `ruleTrace` | — | 覆盖轨迹（`expected/covered/missing`） |
| `providerVersion` | — | 跨仓绑定溯源 |
| `executionId` | — | 幂等与追踪 |

### 3.1 `status` 为何最关键

若没有 `status`，下游看到**空数组**无法区分：

- 「**检查做了，没问题**」 ← 可以判"无缺口"
- 「**检查没做/失败了**」 ← **不能**判"无缺口"

**这正是 FAIL-2026-09-12-04（时间泄漏）的同类问题**：
把"未知"当成"没有"。

### 3.2 6 条不变量

| ID | 规则 |
|---|---|
| `INV-ENV-1` | 三元组必须一致，否则拒绝消费 |
| `INV-ENV-2` | `status ∈ {FAILED, NOT_RUN}` 时空结果**不得**解释为"未发现" |
| `INV-ENV-3` | 空数组**只有**在 `SUCCESS` + 必需规则全覆盖时才表示"未发现" |
| `INV-ENV-4` | `evidenceRefs` 为空的结论**不得**被引用为已证实 |
| `INV-ENV-5` | `capabilityVersion` 不一致**不得**拼接 |
| `INV-ENV-6` | `limitations` 非空时下游输出**必须**携带限制 |

**全部 `FAIL_CLOSED`** —— 失败时**拒绝**，不是降级通过。

---

## 4. 消费义务（8 条）

`specs/knowledge-architecture/contracts/ConsumerObligations.json`

逐条转写建议书 §9.3 的 7 行表格，并**升级为带 `onMissing` 的行为义务**：

| ID | 上游字段 | `onMissing` 行为 |
|---|---|---|
| `OBL-01` | `taskId/entityId/asOf` | `REJECT_CONSUMPTION` |
| `OBL-02` | `status` | `TREAT_AS_NOT_RUN` |
| `OBL-03` | `ruleTrace.*` | `RETURN_COVERAGE_INSUFFICIENT` |
| `OBL-04` | `conflictCases/signals` | `CONDITIONAL_EMPTY_MEANS_NONE` |
| `OBL-05` | `comparedMetricRefs` | `REJECT_METRIC_CITATION` |
| `OBL-06` | `evidenceRefs/explanations` | `KEEP_AS_HYPOTHESIS` |
| `OBL-07` | `requiredQuestions` | `FORBID_REMOVAL` |
| `OBL-08` | `产品体检结果` | `REJECT_UNHEALTHY_PRODUCT` |

### 4.1 `OBL-04` 的精确语义（最容易做错的一条）

```
空数组            →  合法
但"未发现"的解释   →  仅当 OBL-02 且 OBL-03 同时满足时才成立
否则              →  必须解读为"未执行/覆盖不足"
```

**这是"把 optional 升级为义务"的关键**：
不再允许下游看到空数组就默认"没问题"。

### 4.2 `OBL-06`：解释必须区分「假设」与「已验证」

§7.2 步骤 5 原文：「区分『解释已验证』与『仅有解释假设』」

**落地**：解释若无可核验依据 → 标记 `HYPOTHESIS`，**不得据此关闭关注事项**。

**这一条直接对应我在调研提纲 Q2.3 提出的担忧**（合法解释造成误报）：
**解释不是不能有，而是不能"无证据地压掉异常"**。

### 4.3 `OBL-08`：拆分带来的新义务

这是**拆分 `PRODUCT-REC` 后才存在**的义务（U-C 的产物）：

> `admittedProducts` 中任一产品 `healthResult != HEALTHY` → **拒绝进入条件判断**

---

## 5. 两条真实消费链

### 链 1：`FACT-RECON` → `KYC-GAP`（建议书 §9.3 原文举例）

```
对账输出                        缺口输入
─────────────                  ─────────────
taskId/entityId/asOf  ────────→ 同任务校验
status                ────────→ 判断"空数组"含义
ruleTrace             ────────→ 覆盖充分性
conflictCases/signals ────────→ 生成缺口卡片
comparedMetricRefs    ────────→ 引用依据
evidenceRefs          ────────→ 核实依据
requiredQuestions     ────────→ 必需问题（不得删）
```

**适用全部 7 条义务。**

### 链 2：`PRODUCT-DOCTOR` → `PRODUCT-CONDITION`（拆分产物）

```
体检报告                          条件核验
───────────                     ────────────
taskId/entityId/asOf ──────────→ 同任务校验
healthResult=HEALTHY ──────────→ 门禁：否则拒绝
```

**适用 `OBL-01` + `OBL-08`。**

---

## 6. 未产出的是**运行时 trace**（必须说清）

### 6.1 当前状态

```json
"currentStatus": {
  "contractDefined": true,
  "implementationExists": false,
  "runtimeTraceExists": false
}
```

### 6.2 缺什么

| # | 缺失 | 谁能补 |
|---|---|---|
| 1 | 能力实现（`callable` 10/12，但**无真实调用**） | B1（WP05） |
| 2 | 上游 executionId 记录 | B1 |
| 3 | 下游读取字段与取值记录 | W2-b |
| 4 | **反事实检验结果**（移除字段后输出是否改变） | W2-b |
| 5 | 端到端 trace 归档 | W3-a |

### 6.3 §14.2 判定

> **「能力之间真正消费结果」：未达标。**

**理由**：合同已定义，但**反事实检验尚未执行** —— 无法证明"移除字段下游会变"。

**这正是我设计这个检验的原因**：如果没有它，"已消费"是一个**无法证伪的声明**。

---

## 7. 未决问题

| # | 问题 | 阻塞 |
|---|---|---|
| U-1 | 既有通用 envelope 是否**允许**在 `data` 内嵌领域载荷 | 需 KERT 维护方确认（已入确认函 C4 相关） |
| U-2 | `assemblyTrace` 是否可复用为消费 trace，还是须平行记录 | B1 设计 |
| U-3 | 反事实检验的**实施方式**（A/B 对照 or 移除实验） | W2-b |
| U-4 | 两链之外的消费关系（如 EIGHT-DIM → AGENDA）是否也须定义 | B1 |

---

## 8. 边界声明

- 本文**未修改** KERT 任何文件；通用 envelope **零改动**
- 本文**未修改** `generated/`、`_registry.json`
- 本文**不构成** "能力间已消费"的证据
- 合同状态为 `CANDIDATE`，未声称已发布或已实现
- 未决问题 U-1 须 KERT 维护方确认后方可推进实现
