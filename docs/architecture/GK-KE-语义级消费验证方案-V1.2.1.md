# GK-KE：语义级消费验证方案（**预注册**）V1.2.1

> 出具：GK-KE 全局 Tech Lead｜日期：2026-09-13
> 依据：建议书 §9.3 / §6.5 / §14.2 第 6 项
> 前版：V1.0.0（[归档](archive/GK-KE-语义级消费验证方案-V1.0.0.md)）、
> V1.1.0（[归档](archive/GK-KE-语义级消费验证方案-V1.1.0.md)）、
> V1.2.0（**经独立复核**，[复核记录与处置](GK-KE-判据V1.2.0独立复核记录与处置-V1.0.md)）
> **性质：预注册。** 判定标准先于执行锁定，执行后不得修改。
> **依 G-2：本版判据不得回溯适用于 V1.1.0 下的既有判定。**

---

## 0. 本版为何存在

### 0.1 三代版本的问题链

| 版本 | 被发现的缺陷 | 发现者 |
|---|---|---|
| V1.1.0 | **判定键在合同中不存在**（5 条中 3 条） | 独立**判定**执行者 |
| V1.2.0 | **对比式判据被 LLM 非确定性假通过** | 独立**复核**者 |
| V1.2.1 | 本版：修正上述 + 8 项次要发现 |（须再经复核） |

> **两次都是独立的人发现的，两次都不是作者。**

### 0.2 V1.2.0 的最严重缺陷（**本版存在的唯一理由**）

复核者指出：

> S2(b)/S3(b) 要求 `downstream(A) ≠ downstream(B)`。
> 但下游是 **LLM 能力**。**同输入两次调用输出即不同**（实测：runA=1 条 / runB=3 条）。
> **→ A/B 的差异可以由 LLM 随机性完全解释，不必"消费了上游"。**
> S3(b) 还有方向性要求 → 随机性下"方向恰好正确"概率约 **1/2** → **假通过**。

**作者（我）的推理错在哪**：写 S2/S3 时的隐含前提是
「下游确定性 → A 与 B 的差异只能来自输入差异」。
**而该前提我自己刚实测证伪过（S5 = FAIL，报告就在同一目录）。**

> **登记为纪律：被证伪的假设必须登记为「禁止使用」，而不只是"这次没通过"。**

### 0.3 本版的方法修正（一句话）

> **对比只有在组内稳定时才构成证据。**
>
> 非确定性存在时，A/B 差异**无法归因** ——
> 此时判 PASS 是假通过，判 FAIL 是把随机性当违反，
> **诚实结论是 `INCONCLUSIVE`。**

---

## 1. 判定键白名单（**全部取自真实合同**）

> **纪律**：判据只能使用本节登记的键。
> 登记须经 `make criteria-key-audit` 机械核对（§6）。

### 1.1 上游能力（事实对账与冲突检测 `SK-FRONT-004`）

合同：`Leibniz-KERT/examples/bank-front-skills/bank-front-fact-reconciliation/references/output-schema.md`

| 键 | 类型 | 枚举/说明 | 合同出处 |
|---|---|---|---|
| `schemaVersion` | string | — | `output-schema.md:7` |
| `skillId` | string | `"SK-FRONT-004"` | `output-schema.md:8` |
| `customerId` | string | — | `output-schema.md:9` |
| `generatedAt` | string (ISO-8601) | — | `output-schema.md:10` |
| **`taskId`** | string | 本次任务标识（**R6 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:10` |
| **`asOf`** | string (ISO-8601) | 数据截止时点（**R6 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:11` |
| **`executionStatus`** | string | **`SUCCESS \| PARTIAL \| NOT_RUN \| FAILED`**（**R3 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:13` |
| `executionStatusReason` | string | 非 `SUCCESS` 时必填（R3） | `bank-front-fact-reconciliation/references/output-schema.md:14` |
| `indicators[]` | array | — | `output-schema.md:11` |
| `indicators[].elementId` | string | — | `output-schema.md:13` |
| `indicators[].name` | string | 例「近半年营收」 | `output-schema.md:14` |
| `indicators[].value` | 数值 | — | `output-schema.md:15` |
| `indicators[].unit` | string | 例「万元」 | `output-schema.md:15` |
| `indicators[].changeRate` | string | 同比% | `output-schema.md:15` |
| `indicators[].dataTimestamp` | string | 数据时点 | `output-schema.md:16` |
| `indicators[].source` | string | 例 `T-CORE-001` | `output-schema.md:16` |
| **`indicators[].status`** | string | **`verified \| pending \| missing`** | `output-schema.md:17` |
| `conflicts[]` | array | — | `output-schema.md:20` |
| **`conflicts[].id`** | string | 冲突实例唯一标识（**R4 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:26` |
| `conflicts[].issue` | string | — | `output-schema.md:22` |
| **`conflicts[].ruleId`** | string | 形如 `RUL-FRONT-001-xxx` | `output-schema.md:23` |
| `conflicts[].involvedSources` | array\<string\> | — | `output-schema.md:24` |
| **`conflicts[].suggestion`** | string | 「建议的核实问题」 | `output-schema.md:25` |
| `dataGaps[]` | array | — | `output-schema.md:28` |
| `dataGaps[].indicator` | string | — | `output-schema.md:29` |
| `dataGaps[].reason` | string | — | `output-schema.md:29` |
| `dataGaps[].action` | string | — | `output-schema.md:29` |

**不存在于本判据涉及的两个能力合同中**（禁止作为判定键）：
`evaluationStatus`、顶层 `status`、`conflicts[].id`、`conflictId`、`taskId`、`entityId`、`asOf`

> **更正（依复核 3.1）**：V1.2.0 曾写"**全库**命中 0"，**属错误陈述** ——
> `taskId` 实际存在于 `bank-front-report-assembler/references/output-schema.md:40` 与 `SKILL.md:134`，
> 只是不属于本判据涉及的两个能力。
> **作者在该处以未核实断言批评未核实断言。** 现作用域已收窄为"本判据涉及的两个能力"。

### 1.2 下游能力（KYC 缺口核验 `SK-FRONT-006`）

**输入合同**：`bank-front-kyc-gap-check/references/input-schema.md`

| 键 | 类型 | 必填 | 合同出处 |
|---|---|---|---|
| `customerId` | string | **是** | `input-schema.md:7` |
| **`upstreamStatus`** | string | 建议 | **`SUCCESS\|PARTIAL\|NOT_RUN\|FAILED`**（**R1b 已交付**） | `bank-front-kyc-gap-check/references/input-schema.md:8` |
| `conflicts[]` | array | 建议 | `input-schema.md:8` |
| `conflicts[].issue` | string | — | `input-schema.md:10` |
| `conflicts[].ruleId` | string | — | `input-schema.md:11` |
| `optional.customerName` | string | 否 | `input-schema.md:15` |
| `optional.industrySignals` | array\<string\> | 否 | `input-schema.md:16` |
| `optional.kycMissingFields` | array\<string\> | 否 | `input-schema.md:17` |

**不存在**（禁止使用）：`reconciliationStatus`、`conflictCases`、`ruleCoverage`、`explanations`、`indicators`
（`upstreamStatus` **已由 R1b 交付**，见上表）

**输出合同**：`bank-front-kyc-gap-check/references/output-schema.md`

| 键 | 类型 | 枚举/说明 | 合同出处 |
|---|---|---|---|
| `schemaVersion` | string | — | `output-schema.md:7` |
| `skillId` | string | `"SK-FRONT-006"` | `output-schema.md:8` |
| `customerId` | string | — | `output-schema.md:9` |
| `generatedAt` | string (ISO-8601) | — | `output-schema.md:10` |
| **`coverageStatus`** | string | **`SUCCESS \| PARTIAL \| NOT_RUN \| FAILED`**（**R1 已交付**） | `bank-front-kyc-gap-check/references/output-schema.md:11` |
| `coverageStatusReason` | string | 非 `SUCCESS` 时必填（R1） | `bank-front-kyc-gap-check/references/output-schema.md:12` |
| `kycGaps[]` | array | — | `output-schema.md:11` |
| `kycGaps[].gapId` | string | 例 `KG-001` | `output-schema.md:13` |
| `kycGaps[].description` | string | — | `output-schema.md:14` |
| **`kycGaps[].trigger`** | string | 关联 `RUL-FRONT-001-xxx` | `output-schema.md:15` |
| **`kycGaps[].status`** | string | **`OPEN \| PENDING \| CLOSED`**（**R2 已交付**） | `bank-front-kyc-gap-check/references/output-schema.md:18` |
| `kycGaps[].priority` | string | `high \| medium \| general` | `output-schema.md:16` |
| `kycGaps[].priorityCategory` | string | `资金安全 \| 合规风险 \| 经营决策` | `output-schema.md:17` |
| **`kycGaps[].verifyScript.factBasis`** | string | — | `output-schema.md:19` |
| **`kycGaps[].verifyScript.question`** | string | — | `output-schema.md:20` |
| `kycGaps[].verifyScript.goal` | string | — | `output-schema.md:21` |
| `kycGaps[].actionPlan.verifyGoal` | string | — | `output-schema.md:24` |
| `kycGaps[].actionPlan.timing` | string | — | `output-schema.md:25` |
| **`kycGaps[].actionPlan.path`** | array\<string\> | — | `output-schema.md:26` |
| `warnings[]` | array\<string\> | **仅可作旁证，禁止作判定键** | `output-schema.md:30` |

**不存在**（禁止使用）：`limitations`、`HYPOTHESIS`、`COVERAGE_*`、`VERIFY_REQUIRED`
（`coverageStatus` 与 `kycGaps[].status` **已由 R1/R2 交付**，见上表）

> **`warnings[]` 纪律（本方案最重要的单条纪律）**：
> `warnings[]` 是**自由文本**。实测证明：下游可以在 `warnings` 里正确写出"覆盖不足"，
> 同时结论字段给出错误的空值。
> **故：`warnings` 中出现任何关键词，一律不得作为判据满足的证据。**
>
> **纪律扩展（依复核 3.9）**：不止 `warnings` ——
> **任何需要人工语义比对的判定，必须显式标注为「人工」，不得计入机器可校验部分。**
> 仅禁 `warnings` 关键词是不够的："人工看两段文字像不像"同样不可复现、同样可被措辞规避。

---

## 2. 上游状态的形式化（由真实合同字段派生）

```
coverage(U) :=
  FULL    iff  U.indicators ≠ []  ∧  ∀i: i.status == "verified"  ∧  U.dataGaps == []
  PARTIAL iff  U.indicators ≠ []  ∧  (∃i: i.status ∈ {"pending","missing"}  ∨  U.dataGaps ≠ [])
  NONE    iff  U.indicators == []  ∨  ∀i: i.status == "missing"

noUsableInput(U) :=  coverage(U) == NONE
hasConflict(U)   :=  U.conflicts ≠ []
placeholder(U)   :=  ∃c ∈ U.conflicts: c.ruleId 含 "xxx" 或为空
```

> **语义限制（依复核 3.3 —— 名称已由 `notRun` 改为 `noUsableInput`）**：
> `coverage=NONE` 的合同含义是「**无可用输入**」，**不等价于**「上游未运行」。
> `status="missing"` 的语义是**指标缺失** —— 可能"查了但没查到"，也可能"没查"。
> **本派生函数无法区分这两者**，故 V1.2.0 用 `notRun` 命名属**语义借用**，已更正。
> **消除该限制的唯一途径是 KERT 补结构化状态字段（§5 R1/R3）；**
> 在交付前，本判据只能表达"无可用输入"，**不得**表述为"上游未执行"。

### 2.1 上游 → 下游的映射（须由映射程序生成并留痕）

下游合同**不接收** `indicators`/`dataGaps`，故上游状态须表达为下游可接收形式：

| 上游状态 | 下游输入构造 |
|---|---|
| `coverage=NONE` | `conflicts: []` **且** `optional.kycMissingFields` 显式加入本场景待补数据项 |
| `coverage=PARTIAL` | `conflicts` 照传；`kycMissingFields` 加入 `dataGaps[].indicator` |
| `coverage=FULL` 且无冲突 | `conflicts: []`，`kycMissingFields: []` |

> **更正（依复核 3.7）**：A 与 B 在下游**可见合同字段**上的差异，实际落在
> `kycMissingFields`（A=空、B=待补项），**不在** `coverage` ——
> 因为 `coverage` 是我方派生概念，不是下游合同字段。
> V1.2.0 曾笼统写"A/B 差别为 `coverage`"，与该映射不一致，已更正。
> **KERT 补 `upstreamCoverage`（§5 R1b）后，差异将同时落在该字段上。**

**留痕要求**：采集器须同时落盘「上游原始输出」与「下游输入」+ **映射脚本**。
**下游输入必须由映射程序从上游原始输出生成，不得手写**（V1.1.0 的手写输入致
"不存在真正的上游→下游链"）。

---

## 3. 判据 S1–S5（V1.2.1）

> **通用约定**：
> · **成对场景** A / B：A = `coverage=FULL, conflicts=[]`；B = `coverage=NONE, conflicts=[]`
> · 每个判据须自行声明可执行性：`可执行` / `待 KERT`（依 §5）
> · **`warnings[]` 不得作为判定键**（§1.2）
>
> ### ★ 组内稳定性前置（本版最重要的方法修正）
>
> 对场景 X ∈ {A, B} 各调用下游 **k 次（k ≥ 3）**：
> ```
> stable(X) := 若 k 次输出（排除允许字段、规范化后）完全一致 → 该输出
>              否则 → ⊥（不可判定）
> ```
> **任何以"跨场景差异"为证据的判据，其通过条件必须包含 `stable(A) ≠ ⊥ ∧ stable(B) ≠ ⊥`。**
> 组内不稳定 → 该判据判 **`INCONCLUSIVE`**（**不得**判 PASS，**亦不得**判 FAIL）。
>
> **理由**：非确定性存在时，A/B 差异**无法归因于消费**。
> 判 PASS 是假通过；判 FAIL 是把随机性当违反。**"无法归因"的诚实结论是"不可判定"。**
>
> **结构性差异要求**：差异必须是**结构性**的 ——
> B 中存在条目引用了**仅 B 场景上游输出才有的字段值**。
> **不接受"长度不同"作为差异证据**（长度可被随机性产生）。

### S1 冲突传递 · `S1_CONFLICT_PROPAGATION`

- **条件**：`hasConflict(U)` 且 **非** `placeholder(U)` 且 `coverage(U) ∈ {FULL, PARTIAL}`
- **判据**：存在下游 `kycGaps[]` 条目 `d`，使得 **∃i**：`U.conflicts[i].ruleId` 出现在
  `d.trigger` 或 `d.verifyScript.factBasis` 中
- **判定键**：`conflicts[].ruleId` ✅ / `kycGaps[].trigger` ✅ / `kycGaps[].verifyScript.factBasis` ✅
- **可执行性**：**可执行**（**不受非确定性影响** —— 结构性引用检查）
- **前置质量门**：若 `placeholder(U)` 为真 → 判 **`INCONCLUSIVE`** 并**归因上游**
  （实测 `ruleId = "RUL-FRONT-001-xxx（…待映射）"`；占位符不可作追溯键，
  这是**上游产出质量问题**，不是下游消费问题）
  - **附加义务**：归因上游时**必须同时开具上游缺陷项**，不得只报"无法判定"（见 §7）
- **采集要求**：**必须真实调用下游**（V1.1.0 的 S1 因采集器从不调用下游而结构性不可判定）

### S2 空结论的正确解读 · `S2_EMPTY_MEANS_NONE`

- **条件**：成对 A / B 均已运行；**且 `stable(A) ≠ ⊥`、`stable(B) ≠ ⊥`**
  （组内不一致 → 本判据 `INCONCLUSIVE`）
- **判据**（**合取**）：
  - (a) `stable(A).kycGaps` 中不存在引用"已覆盖规则"的缺口
  - (b) **`stable(A).kycGaps` ≠ `stable(B).kycGaps`**
- **判定键**：`kycGaps` ✅
- **可执行性**：**条件性可执行** —— 依赖下游确定性
- **为何加 (b)**：仅 (a) 时**任何恒返回 `kycGaps: []` 的下游都自动通过**（V1.1.0 即如此）
- **⚠️ (b) 的适用边界（V1.2.0 缺陷）**：对**非确定性下游**，A/B 差异近乎必然存在 →
  (b) **判别力归零且会假通过**。故本版加组内稳定性前置：此时 (b) 判 `INCONCLUSIVE`
- **与 S5 的区别**：S2 比**跨场景**（A vs B）；S5 比**同场景 k 次**

### S3 未执行 ≠ 无冲突 · `S3_NOT_RUN_NOT_NONE`

> 承接 §9.3 行 3 的正向要求（"必需规则缺失则返回覆盖不足"）。

- **条件**：成对 A / B 均已运行，且 `noUsableInput(U_B)` 为真
- **判据**（**析取**，任一满足即通过）：
  - **(a) 结构化路径 · 待 KERT（★ 免疫非确定性，优先路径）**：
    `downstream(B).coverageStatus == "NOT_RUN"` ∧ `downstream(A).coverageStatus == "SUCCESS"`
    —— 该字段由合同规定、取值受控，**不依赖 LLM 随机性**。
    **依复核：这是本判据唯一免疫非确定性的路径。**
  - **(b) 对比路径 · 须满足组内稳定性前置**：
    前置：`stable(A) ≠ ⊥ ∧ stable(B) ≠ ⊥`（否则 `INCONCLUSIVE`）。
    判据：`stable(A).kycGaps ≠ stable(B).kycGaps` **且差异为结构性** ——
    B 中存在 `d` 使 `d.trigger` / `d.verifyScript.factBasis` 引用了
    `U_B.dataGaps[].indicator` 或 `U_B.indicators[].name`，
    该字段值**在 A 场景上游输出中不存在**。
- **判定键**：`coverageStatus`（待 KERT）/ `kycGaps` ✅ / `dataGaps[].indicator` ✅ / `indicators[].name` ✅
- **可执行性**：**(b) 可执行但判别力受非确定性限制**；**(a) 待 KERT，且为优先路径**
- **⚠️ 复核指出的假通过风险（V1.2.0）**：原 (b) 仅要求 `len(B) > len(A)` ——
  随机性下"方向恰好正确"概率约 **1/2** → **S3 被随机性假通过**。
  已改为**结构性差异 + 组内稳定性前置**。
- **明确禁止**：以 `warnings[]` 出现"覆盖不足""待核实"等措辞作为通过依据（**已实测证伪**）

### S4 假设不得关闭缺口 · `S4_HYPOTHESIS_NOT_CLOSED`

- **条件**：`U.indicators[]` 中存在 `status ∈ {"pending","missing"}` 的指标
- **判据**（**合取**）：
  - (a) 下游存在条目 `d`，使 `U.indicators[k].name` 出现在 `d.description` 或
    `d.verifyScript.factBasis` 中
  - (b) 该条目**未**被标记为已解决 —— 机器可校验的**弱形式**：
    `d.verifyScript.question` 与 `d.actionPlan.path` **均非空**
- **判定键**：`indicators[].status` ✅ / `indicators[].name` ✅ / `kycGaps[].description` ✅ /
  `verifyScript.question` ✅ / `actionPlan.path` ✅
- **可执行性**：**可执行**（**不受非确定性影响** —— 存在性检查）
- **残余限制（须随判定记录）**：(b) 是**代理指标**，是**弱形式**（**非**完全可机器校验）。
  本版承认该残余，**不得**据此声称"完全可机器校验"。
- **判定键重叠登记（依复核 3.8）**：S4(b) 与 §4 的 S8'(a) 都检查 `verifyScript.question` /
  `actionPlan.path` 的存在性，都用"非空 = 合规"弱代理，**判别力相互稀释**。
  **纪律**：二者**不得**互相作为通过依据。

### S5 可复现 · `S5_REPRODUCIBLE`

- **性质声明**：**S5 是确定性硬门槛。对 LLM 下游要求逐字可复现；不可复现即未达成。**
  如需允许受控波动，须**新发版本**定义口径，**且不得回溯适用**（依 G-2）。
- **条件**：**同一场景**、**相同下游输入**、**连续 k 次（k ≥ 3）调用**
- **判据**（**合取**）：
  - (a) 排除允许字段后，k 次输出 JSON **规范化后完全一致**
  - (b) 允许字段**仅**：`generatedAt`；且 `generatedAt` **必须是合法 ISO-8601**
    （V1.1.0 的允许集合含 `executionId`，但合同**无**该字段，已删除）
  - (c) `skillId` / `customerId` / `schemaVersion` k 次一致
- **判定键**：全部顶层字段 ✅
- **可执行性**：**可执行**（**本条即非确定性的检出器**）
- **★ 与对比判据的关系**：S5 的"组内稳定性"**就是** §3 通用约定中
  `stable(X) ≠ ⊥` 的同一件事。
  **故：若 S5 FAIL，则 S2(b)/S3(b) 必然 `INCONCLUSIVE`。**
  该依赖**已在 §7「判据间依赖登记」显式登记**，不再隐含。

---

## 4. S6'–S8'（行 1 / 5 / 7 的可执行子集）

> **本节地位**：S6'–S8' **不影响** S1–S5 的达成结论，但**必须单独报告**（见 §7）。

### S6' `customerId` 传递一致性

- **条件**：A 场景
- **判据**：`downstream.customerId == upstream.customerId`
- **判定键**：`customerId`（上游 `bank-front-fact-reconciliation/references/output-schema.md:9`；下游 `bank-front-kyc-gap-check/references/output-schema.md:9`）
- **可执行性**：**可执行**

### S7' 口径前置质量门（上游侧）

- **条件**：`U.indicators ≠ []`
- **判据**：每条指标**必须**具备非空 `unit` 与非空 `dataTimestamp`
- **判定键**：`indicators[].unit`（上游 `bank-front-fact-reconciliation/references/output-schema.md:15`）；
  `indicators[].dataTimestamp`（上游 `bank-front-fact-reconciliation/references/output-schema.md:16`）
- **可执行性**：**上游侧可执行**；**下游侧引用检查待 KERT**
- **注**：实测上游出现过 `unit: "未提供（待核实）"`、`value` 为自由字符串，本判据即针对该形态

### S8' 核实问题不得删除

- **条件**：`hasConflict(U)` 且非 `placeholder(U)`
- **判据**：
  - (a) **数量约束（可机器校验）**：`|{d.verifyScript.question}| ≥ |U.conflicts|`
  - (b) **对应性（须人工语义比对，须显式标注「人工」）**
- **判定键**：`conflicts[].suggestion`（上游 `bank-front-fact-reconciliation/references/output-schema.md:25`）；
  `kycGaps[].verifyScript.question`（下游 `bank-front-kyc-gap-check/references/output-schema.md:20`）
- **可执行性**：(a) **可执行**；(b) **须人工**，**不计入机器可校验**
- **重叠登记**：见 S4 的"判定键重叠登记"

### 行 1 / 5 / 7 的完整覆盖缺口（**本版不声称已覆盖**）

`taskId` / `entityId` / `asOf` / `comparedMetricRefs` / `requiredQuestions`
**均不存在于本判据涉及的两个能力合同中**，故：

| §9.3 行 | 状态 |
|---|---|
| 行 1（`taskId`/`entityId`/`asOf`） | ⚠️ **仅 S6' 覆盖其可执行子集**；完整覆盖**待 KERT**（§5 R6） |
| 行 5（`comparedMetricRefs`） | ⚠️ **仅 S7' 覆盖上游侧**；下游侧**待 KERT** |
| 行 7（`requiredQuestions`） | ⚠️ **S8'(a) 可执行，(b) 须人工** |

---

## 5. 请 KERT 侧补的字段

> Owner 裁定 2：安排 KERT 侧补结构化覆盖状态字段。跨仓为**实施**（非仅请求），见派工单。

### ★ R1 的定位升级（依复核）

R1 原述为"增强"。复核指出：**对比路径对非确定性下游判别力归零**，
故 **R1 实为 S3 可信判定的"事实上唯一路径"**。这改变了 R1 的优先级依据。

### ★ R1b（V1.2.1 补漏 —— V1.2.0 的请求不完整）

下游**输入合同**须增加字段以**接收**上游覆盖状态（建议 `upstreamCoverage`）。

**理由**：下游如何得知上游"没查"？现其输入为 `{customerId, conflicts, optional{...}}` ——
**无任何字段承载上游状态**。A/B 的差异当前只能落在 `kycMissingFields` 上。
**只补下游输出不补下游输入，则 (a) 路径无法被正确驱动。**

| # | 能力 | 请求新增 | 优先级 |
|---|---|---|---|
| **R1** | 下游 `SK-FRONT-006` | 输出顶层 `coverageStatus`（受控枚举 `SUCCESS\|PARTIAL\|NOT_RUN\|FAILED`） | **P0** |
| **R5** | 上游 `SK-FRONT-004` | `conflicts[].ruleId` 禁止占位符（须具体子编号） | **P0** ✅ **已交付** |
| **R1b** | 下游 `SK-FRONT-006` | **输入**增加 `upstreamStatus`（接收上游状态；原名拟 `upstreamCoverage`，实施时统一为 `upstreamStatus` 以与 `executionStatus`/`coverageStatus` 同词汇） | **P0** ✅ **已交付** |
| R2 | 下游 `SK-FRONT-006` | `kycGaps[].status`（受控枚举） | P1 ✅ **已交付** |
| R3 | 上游 `SK-FRONT-004` | 输出顶层 `executionStatus` | P1 ✅ **已交付** |
| R4 | 上游 `SK-FRONT-004` | `conflicts[].id`（实例唯一 id，与 `ruleId` 并列） | P1 ✅ **已交付** |
| R6 | 上游 `SK-FRONT-004` | `taskId` / `asOf` | P2 ✅ **已交付** |

**若 KERT 不补**：S3 仅能走对比路径 (b)（且受非确定性限制）；
S4 仅能走代理指标；行 1/5/7 维持"无完整判据覆盖"。

---

## 6. 反复发机制

### 6.1 判据键审计（已接入 `make verify`）

`make criteria-key-audit` → `scripts/gk_ke_criteria_key_audit.py`：

1. **判据文档为唯一真源**（不持有脚本内副本 —— V1.2.0 曾硬编码副本致"检查器检查自己"）
2. 解析 §1 与 §4 表格中**含 `file.md:NN` 出处引用**的行 → 提取键
3. 逐键回真实合同核对；**任一不存在 → 非零退出**
4. 正文反引号标识符须在白名单内
5. 禁用标识符不得出现在**判定键/判据声明位**
6. 声明位使用的键**必须已登记**
7. **解析到键数低于下限 → fail-closed**（防"解析失效致静默通过"）

> **更正（依复核 3.2）**：V1.2.0 的 §4 表格**无逐行出处引用**，
> 故审计**不覆盖 S6'–S8' 的键** —— §6.1 声称的机械化防线对它们**实际失效**。
> **本版已为 §4 每行补齐出处引用**，使其纳入审计范围。

### 6.2 判据变更的三项强制检查

| # | 检查 | 目的 |
|---|---|---|
| 1 | **键存在性**（§6.1） | 不再写不存在的键 |
| 2 | **范式检查**：不得以自由文本（含"人工语义比对"）为机器判定键 | 不再写会被措辞糊弄的判据 |
| 3 | **反空转检查**：须存在一种"错误的下游"使其 FAIL | 不再写恒真判据 |

### 6.3 ★ 第四项检查：**非确定性控制**（V1.2.1 新增）

> **任何以"两次输出不同"为证据的判据，必须证明"组内稳定"。**
> 否则该差异**不可归因**，判据应判 `INCONCLUSIVE` 而非 PASS。

**来源**：V1.2.0 的 S2(b)/S3(b) 未做此检查，被 LLM 随机性假通过。

### 6.4 可执行性自评（**区分两类下游**）

| 判据 | 可执行性 | **确定性下游**下的恒失败场景 | **非确定性下游**（LLM，实测即此类） |
|---|---|---|---|
| S1 | ✅ 可执行 | 下游不引用 `ruleId` | ✅ **不受影响**（结构性引用） |
| S2 | ⚠️ 条件性 | 下游恒返回 `kycGaps: []`（A==B） | ❌ 组内不稳定 → `INCONCLUSIVE` |
| S3 | ⚠️ 条件性 | 下游对 NONE 仍返回空 | ❌ (b) `INCONCLUSIVE`；**(a) 免疫**（待 KERT） |
| S4 | ✅ 可执行（(b) 为弱代理） | 下游不产出指向 `pending` 指标的条目 | ✅ 不受影响（存在性检查） |
| S5 | ✅ 可执行 | 同输入 k 次输出不同 | ✅ **本条即非确定性的检出器** |
| S6' | ✅ 可执行 | `customerId` 被改写 | ✅ 不受影响 |
| S7' | ✅ 上游侧可执行 | 上游指标缺 `unit`/`dataTimestamp` | ✅ 不受影响 |
| S8' | ⚠️ (a) 可执行；(b) **须人工** | 下游 `question` 数少于 `conflicts` 数 | ⚠️ (b) 不计入机器可校验 |

> V1.2.0 把两类下游混为一谈，**属自评夸大**，已更正（依复核 3.5）。

---

## 7. 通过规则

| 结论 | 条件 |
|---|---|
| **语义级消费达成（S1–S5 覆盖的四行）** | `S1–S5` **全部** `PASS` |
| 未达成 | 任一 `FAIL` |
| **不得记为通过** | 任一 `INCONCLUSIVE`；或未全部判定 |

### 判据间依赖登记（V1.2.1 新增）

| 判据 | 依赖 | 后果 |
|---|---|---|
| S2(b) | `stable(A) ≠ ⊥ ∧ stable(B) ≠ ⊥` | 非确定性下游 → `INCONCLUSIVE` |
| S3(b) | 同上 | 同上 |
| **S2(b)/S3(b)** | **与 S5 同源**（组内稳定性） | **S5 FAIL ⇒ S2(b)/S3(b) 必 `INCONCLUSIVE`** |
| S3(a) | KERT 交付 `coverageStatus` | 未交付 → 仅剩 (b)，判别力受限 |

**纪律**：**不得**在 S5 未通过时单独报告 S2/S3 的对比路径"通过"。

### S6'–S8' 的地位（依复核 3.4）

- **不影响** S1–S5 的达成结论
- 但**必须单独报告**；**不得**因其可执行而默认其已通过
- V1.2.0 把它们列入"可执行判据"却不说明是否计入门禁 → **属未明说的豁免**，已更正

### S1 归因上游时的附加义务（依复核 3.10）

- 若 S1 因**上游占位符**判 `INCONCLUSIVE`，则**必须同时开具上游缺陷项**，
  **不得**只报"无法判定" —— 否则总判定**永久不可达** MET，而无人知道原因在上游。

### 范围限制（**须随任何结论一并声明**）

- 本方案**仅覆盖** §9.3 的行 2 / 3 / 4 / 6
- 行 1 / 5 / 7 **无完整判据覆盖**（S6'–S8' 仅覆盖其可执行子集）
- **故「S1–S5 通过」不得表述为「§9.3 达成」**

**禁止的表述**：❌「§9.3 语义级消费达成」　❌「部分通过、基本达成」　❌「B 层接近达成」

---

## 8. 与 V1.2.0 的关系

| 项 | 说明 |
|---|---|
| V1.2.0 **保留** | 作为**已被独立复核的版本**，不删、不改 |
| V1.2.0 **未预注册** | 故本次复核对**已锁定结论无影响** |
| 本版**仍不得直接预注册** | 须经**再次独立复核**（修正本身可能有新缺陷） |
| 依 G-2 | 本版亦**不得回溯**适用于 V1.1.0 下的既有判定 |
| 旧版对照 | V1.0.0 / V1.1.0 实体副本见 `archive/`，哈希见 `_criteria-versions.json` |

---

## 9. 待办与依赖

| # | 事项 | 依赖 | 状态 |
|---|---|---|---|
| 1 | **再次独立复核本版**（须为非作者） | Owner 裁定 1 | 待办 |
| 2 | **采集器改造**：成对场景 + **每场景 k≥3 次** + 映射程序 + S1 真实调用下游 | 本版 | 待办 |
| 3 | KERT 补字段（R1/R1b/R5 为 P0） | Owner 裁定 2 | **派工中** |
| 4 | 键审计脚本 | 本版 | ✅ 已完成 |
| 5 | 预注册（锁定哈希） | 须 #1 通过 | 待办 |

> **说明**：V1.2.0 的复核证明，**修正本身也需要复核**。
> 本版 §3 的组内稳定性前置、§4 的结构性差异要求，均为新设计，**尚未被执行过**。
> **不得**因"这是修正版"而假定其正确。
