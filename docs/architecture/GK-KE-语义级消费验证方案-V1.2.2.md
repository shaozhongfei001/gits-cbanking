# GK-KE：语义级消费验证方案（**草案 · 未预注册**）V1.2.2

> 出具：GK-KE 全局 Tech Lead｜日期：2026-09-13
> 依据：建议书 §9.3 / §6.5 / §14.2 第 6 项
> 前版：V1.0.0（[归档](archive/GK-KE-语义级消费验证方案-V1.0.0.md)）、
> V1.1.0（[归档](archive/GK-KE-语义级消费验证方案-V1.1.0.md)）、
> V1.2.0（**经独立复核**，[复核记录](GK-KE-判据V1.2.0独立复核记录与处置-V1.0.md)）、
> V1.2.1（**经独立复核**，发现判据**惩罚合规下游**）
> **性质：草案。** **本版未预注册，且不得直接预注册** ——
> 须先经第三次独立复核（见 §9 待办 1b）。
> **依 G-2：本版判据不得回溯适用于 V1.1.0 下的既有判定。**
>
> ### ★ 本版存在的唯一理由（V1.2.1 复核发现的最严重缺陷）
>
> **V1.2.1 的 S2(b)/S3(b) 要求 `stable(A).kycGaps ≠ stable(B).kycGaps`。
> 但场景 A 与 B 在已交付合同下**都属"无触发源"**，合同明文要求合规下游
> **两者都输出 `kycGaps: []`**（`SK-FRONT-006/SKILL.md:48,151`），
> 仅以 `coverageStatus` 区分（`:50-51`）。**
>
> **→ 合规下游：`[] == []` → S2(b)/S3(b) 判 FAIL。
> → 违约下游（凭空造缺口）：`[] ≠ [1条]` → 判 PASS。**
>
> **判据惩罚合规、奖励违约。** 一个只回显 `upstreamStatus` 的下游亦可通过。
>
> **根因**：该缺陷由**我方 R1 交付本身引入** ——
> 合同一经提供正确通道（`coverageStatus`），合规下游即改走该通道而**不再改 `kycGaps`**；
> 而判据仍在检查 `kycGaps`。
> **本版据此删除跨场景 `kycGaps` 对比，S3 只保留结构化路径。**

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
| `generatedAt` | string (ISO-8601) | — | `output-schema.md:12` |
| **`taskId`** | string | 本次任务标识（**R6 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:10` |
| **`asOf`** | string (ISO-8601) | 数据截止时点（**R6 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:11` |
| **`executionStatus`** | string | **`SUCCESS \| PARTIAL \| NOT_RUN \| FAILED`**（**R3 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:13` |
| `executionStatusReason` | string | 非 `SUCCESS` 时必填（R3） | `bank-front-fact-reconciliation/references/output-schema.md:14` |
| `indicators[]` | array | — | `output-schema.md:15` |
| `indicators[].elementId` | string | — | `output-schema.md:17` |
| `indicators[].name` | string | 例「近半年营收」 | `output-schema.md:18` |
| `indicators[].value` | 数值 | — | `output-schema.md:19` |
| `indicators[].unit` | string | 例「万元」 | `output-schema.md:19` |
| `indicators[].changeRate` | string | 同比% | `output-schema.md:19` |
| `indicators[].dataTimestamp` | string | 数据时点 | `output-schema.md:20` |
| `indicators[].source` | string | 例 `T-CORE-001` | `output-schema.md:20` |
| **`indicators[].status`** | string | **`verified \| pending \| missing`** | `output-schema.md:21` |
| `conflicts[]` | array | — | `output-schema.md:24` |
| **`conflicts[].id`** | string | 冲突实例唯一标识（**R4 已交付**） | `bank-front-fact-reconciliation/references/output-schema.md:26` |
| `conflicts[].issue` | string | — | `output-schema.md:27` |
| **`conflicts[].ruleId`** | string | 形如 `RUL-FRONT-001-xxx` | `output-schema.md:28` |
| `conflicts[].involvedSources` | array\<string\> | — | `output-schema.md:29` |
| **`conflicts[].suggestion`** | string | 「建议的核实问题」 | `output-schema.md:30` |
| `dataGaps[]` | array | — | `output-schema.md:33` |
| `dataGaps[].indicator` | string | — | `output-schema.md:34` |
| `dataGaps[].reason` | string | — | `output-schema.md:34` |
| `dataGaps[].action` | string | — | `output-schema.md:34` |

**不存在于本判据涉及的两个能力合同中**（禁止作为判定键）：
`evaluationStatus`、顶层 `status`、`conflictId`、`entityId`

> **更正（第二次复核 Q3/Q6 指出，实测确认）**：V1.2.1 先前把 `conflicts[].id`、`taskId`、`asOf`
> **同时**列在本"不存在"清单里与 §1.1"R6/R4 已交付"中 —— **自相矛盾**。
> 原因：R1–R6 交付后**只更新了 §1 白名单，未回头清理本节**。
> 现按实际状态更正：`conflicts[].id`/`taskId`/`asOf` **已交付并存在于合同中**，移出本清单。

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
| `conflicts[]` | array | 建议 | `input-schema.md:9` |
| `conflicts[].issue` | string | — | `input-schema.md:12` |
| `conflicts[].ruleId` | string | — | `input-schema.md:13` |
| `optional.customerName` | string | 否 | `input-schema.md:17` |
| `optional.industrySignals` | array\<string\> | 否 | `input-schema.md:18` |
| `optional.kycMissingFields` | array\<string\> | 否 | `input-schema.md:19` |

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
| `kycGaps[]` | array | — | `output-schema.md:13` |
| `kycGaps[].gapId` | string | 例 `KG-001` | `output-schema.md:15` |
| `kycGaps[].description` | string | — | `output-schema.md:16` |
| **`kycGaps[].trigger`** | string | 关联 `RUL-FRONT-001-xxx` | `output-schema.md:17` |
| **`kycGaps[].status`** | string | **`OPEN \| PENDING \| CLOSED`**（**R2 已交付**） | `bank-front-kyc-gap-check/references/output-schema.md:18` |
| `kycGaps[].priority` | string | `high \| medium \| general` | `output-schema.md:19` |
| `kycGaps[].priorityCategory` | string | `资金安全 \| 合规风险 \| 经营决策` | `output-schema.md:20` |
| **`kycGaps[].verifyScript.factBasis`** | string | — | `output-schema.md:19` |
| **`kycGaps[].verifyScript.question`** | string | — | `output-schema.md:20` |
| `kycGaps[].verifyScript.goal` | string | — | `output-schema.md:24` |
| `kycGaps[].actionPlan.verifyGoal` | string | — | `output-schema.md:24` |
| `kycGaps[].actionPlan.timing` | string | — | `output-schema.md:28` |
| **`kycGaps[].actionPlan.path`** | array\<string\> | — | `output-schema.md:29` |
| `warnings[]` | array\<string\> | **仅可作旁证，禁止作判定键** | `output-schema.md:33` |

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
| `coverage=NONE`（**场景 B**） | `conflicts: []`，`upstreamStatus: "NOT_RUN"`，`kycMissingFields: []` |
| `coverage=PARTIAL` | `conflicts` 照传，`upstreamStatus: "PARTIAL"` |
| `coverage=FULL` 且无冲突（**场景 A**） | `conflicts: []`，`upstreamStatus: "SUCCESS"`，`kycMissingFields: []` |

> ### ★★ 纪律：**A/B 的下游输入只能在 `upstreamStatus` 一个字段上不同**（第二次复核 Q4 后新增）
>
> **这是本方案最关键的一条构造纪律。**
>
> V1.2.1 早期版本把 B 场景的 `dataGaps[].indicator` 值**写进了下游输入的
> `kycMissingFields`**，而 S3(b) 又要求"B 的输出引用 `dataGaps[].indicator`"。
> → **采集器先把"答案"放进输入，再检查下游有没有说出这个"答案"。**
>
> **后果**：一个**只回显自己的输入字段、完全不读上游对账结果**的下游，
> 也能满足 S3(b)（A 场景该字段为空 → 无缺口；B 场景该字段有值 → 输出缺口；
> 且输出确实"引用了 `dataGaps[].indicator`"，因为输入里就是它）。
> **→ 判据被测量装置本身绕过。**
>
> **故**：
> 1. **A 与 B 的下游输入，除 `upstreamStatus` 外必须逐字段完全相同。**
> 2. **禁止**把任何"上游结果的内容"（如缺了哪些指标）预先写入下游输入。
>    下游若要知道"缺了什么"，必须**自己消费** `upstreamStatus` 并据此产出结论。
> 3. 采集器须落盘 **A/B 输入的逐字段差异**，且该差异**必须只有 `upstreamStatus` 一项**
>    —— 由**机械校验**（`make` 目标）确认，不靠人工检查。

> **本段已作废（V1.2.2）**：该段（依 V1.2.0 复核 3.7 所写）称 A/B 差异落在
> `kycMissingFields`，与**本页映射表**（A、B 的 `kycMissingFields` 均为 `[]`）
> 及**本节 ★★ 构造纪律**（差异只允许是上游状态字段）**互斥**。
> 按实际构造更正：**A/B 的差异只落在上游状态字段**；
> 先前把“上游缺哪些指标”写进 `kycMissingFields` 的做法**本身即被 ★★ 纪律禁止**。
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
> **V1.2.2 收窄（重要）**：V1.2.0/V1.2.1 曾要求**任何以“跨场景差异”为证据的判据**
> 都必须满足 `stable(A) ≠ ⊥ ∧ stable(B) ≠ ⊥` —— 即 S2(b)、S3(b)。
> **该跨场景对比路径已于 V1.2.2 全部删除**（理由见文件头：它惩罚合规下游）。
> **故 `stable()` 现在只用于 S5**（同场景 k 次比较），**不再作为 S2/S3 的前置**。
>
> 原理由仍成立：非确定性存在时，跨场景差异**无法归因于消费**，
> 判 PASS 是假通过、判 FAIL 是把随机性当违反。
> 但 V1.2.2 的结论**更根本**：那个对比**本来就不该做** ——
> 因为合同要求合规下游在 A/B 下**不改变** `kycGaps`（`SK-FRONT-006/SKILL.md:48,151`）。
>
> **结构性差异要求 —— 已删除（V1.2.1 → V1.2.2）**
> 该要求曾用于配合 S3(b) 的跨场景对比。S3(b) 删除后，它**无任何判据实现**，
> 且其本身也可被“回显”绕过（复核 Q4）。**一并删除**，以免留下“声明了但没落实”的条款。

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

- **条件**：场景 A 已运行
- **判据**：`A.kycGaps` 中**不存在**引用"已覆盖规则"的缺口
  （即：不存在 `d` 使 `d.trigger` 匹配 `U_A` 的任一 `conflicts[].ruleId`）
- **判定键**：`kycGaps` ✅ / `conflicts[].ruleId` ✅
- **可执行性**：**可执行**（纯存在性检查，不受非确定性影响的程度较高）
- **⚠️ 单看本条无判别力**：它是否定式，**任何恒返回 `kycGaps: []` 的下游都自动通过**。
  本条的判别力**来自与 S3 的配对**（S3 要求下游在该场景下做出区分性结论）——
  **不得单独引用 S2 的 PASS 作为消费证据。**
- **⚠️ 删除记录（V1.2.1 → V1.2.2）**：V1.2.1 曾加 (b)「`A.kycGaps ≠ B.kycGaps`」以防空转。
  **该 (b) 已被证明惩罚合规下游**（见文件头），**本版删除**。
  防空转改由 S3 承担 —— 而非要求下游改变一个**合同要求它不该改变**的字段。

### S3 未执行 ≠ 无冲突 · `S3_NOT_RUN_NOT_NONE`

> 承接 §9.3 行 3 的正向要求（"必需规则缺失则返回覆盖不足"）。

- **条件**：成对 A / B 均已运行，且 `noUsableInput(U_B)` 为真
- **判据**（**唯一路径 —— 结构化**；跨场景 `kycGaps` 对比路径已删除，见下）：
  - **(a) 结构化路径 · ✅ R1 已交付，可执行**：
    `downstream(B).coverageStatus == "NOT_RUN"` ∧ `downstream(A).coverageStatus == "SUCCESS"`
    —— 该字段由合同规定、取值受控，**不依赖 LLM 随机性**。
    **依复核：这是本判据唯一免疫非确定性的路径。**
  - ~~(b) 对比路径~~ **已删除（V1.2.1 → V1.2.2）**
    > **删除理由**：该路径要求 `stable(A).kycGaps ≠ stable(B).kycGaps`。
    > 但 A、B 两场景**均无触发源**，合同**明文要求合规下游两者都输出 `kycGaps: []`**
    > （`SK-FRONT-006/SKILL.md:48,151`），仅以 `coverageStatus` 区分（`:50-51`）。
    > → **合规下游必然判 FAIL；违约（凭空造缺口）下游反而判 PASS。**
    > **该路径惩罚合同要求的行为、奖励合同禁止的行为，方向相反，必须删除。**
    > 其防空转职能**由 S3(a) 承担** —— 那才是合同为此提供的通道。
- **判定键**：`coverageStatus` ✅（R1 已交付）/ `coverageStatusReason` ✅
- **可执行性**：**可执行** —— 结构化字段、受控枚举，**不依赖 LLM 随机性**
- **⚠️ 本判据能证明什么、不能证明什么（须随结论一并声明）**：
  - ✅ **能证明**：下游**接收并反映了**上游执行状态 —— 这是**传递级**消费证据。
  - ❌ **不能证明**：下游对上游**事实内容**（`indicators` / `conflicts` / `dataGaps`）
    做了任何理解或推理。**不得**据此声称"下游理解了上游结果"。
  - 历史上本判据曾被写成"对比 `kycGaps`"：那既**惩罚合规下游**、又只证明转述，
    且受随机性污染。现仅保留结构化路径。
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
- **判定键**：`indicators[].unit`（上游 `bank-front-fact-reconciliation/references/output-schema.md:19`）；
  `indicators[].dataTimestamp`（上游 `bank-front-fact-reconciliation/references/output-schema.md:16`）
- **可执行性**：**上游侧可执行**；**下游侧无请求通道**（§5 未提该字段请求，故不标"待 KERT"——否则该"待"永不会兑现）
- **注**：实测上游出现过 `unit: "未提供（待核实）"`、`value` 为自由字符串，本判据即针对该形态

### S8' 核实问题不得删除

- **条件**：`hasConflict(U)` 且非 `placeholder(U)`
- **判据**：
  - (a) **数量约束（可机器校验）**：`|{d.verifyScript.question}| ≥ |U.conflicts|`
  - (b) **对应性（须人工语义比对，须显式标注「人工」）**
- **判定键**：`conflicts[].suggestion`（上游 `bank-front-fact-reconciliation/references/output-schema.md:30`）；
  `kycGaps[].verifyScript.question`（下游 `bank-front-kyc-gap-check/references/output-schema.md:20`）
- **可执行性**：(a) **可执行**；(b) **须人工**，**不计入机器可校验**
- **重叠登记**：见 S4 的"判定键重叠登记"

### 行 1 / 5 / 7 的完整覆盖缺口（**本版不声称已覆盖**）

`comparedMetricRefs` / `requiredQuestions` / `entityId`
**不存在于本判据涉及的两个能力合同中**；
而 `taskId` / `asOf` **已由 R6 交付**（见 §1.1 与 §5），

| §9.3 行 | 状态 |
|---|---|
| 行 1（`taskId`/`entityId`/`asOf`） | ⚠️ **字段已就绪（R6 已交付）**，但**判据仍未完整覆盖该行** —— 当前仅 S6' 覆盖 `customerId` 一致性子集 |
| 行 5（`comparedMetricRefs`） | ⚠️ **仅 S7' 覆盖上游侧**；下游侧**无请求通道**（该字段未列入 §5 请求项，故无通道） |
| 行 7（`requiredQuestions`） | ⚠️ **S8'(a) 可执行，(b) 须人工**（该字段未交付，改用 `conflicts[].suggestion`） |

> **更正（第二次复核 Q6 指出）**：V1.2.1 先前在行 1 写"完整覆盖**待 KERT（§5 R6）**"，
> 而 §5 已把 R6 标为**已交付** —— 自相矛盾。
> **须区分两件事**：**字段是否就绪**（R6 已就绪）与**判据是否覆盖该行**（仍未覆盖）。
> 先前把二者混为一谈，故产生矛盾。**本表现分别标注。**

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

### 6.3b ★ 第五项检查：**构造不得注入答案**（第二次复核 Q4 后新增）

> **A/B 的下游输入，除"上游状态字段"外必须逐字段完全相同。**
> **禁止把上游结果的内容预先写入下游输入。**

**来源**：V1.2.1 早期版本的映射把 B 场景的 `dataGaps[].indicator` 写进了下游输入
`kycMissingFields`，而判据又要求输出引用该字段值 →
**采集器先把答案放进输入，再检查下游有没有说出这个答案。**
一个只回显输入的下游即可通过。

**检查方式（须机械化，不靠人工）**：采集器落盘 A/B 两份下游输入，
由脚本逐字段对比，**差异字段集合必须等于 `{"upstreamStatus"}`**，否则该轮采集判**无效**。

> **一般化的教训（登记为纪律）**：
> **任何"测量装置向被测对象提供答案、再检查被测对象是否说出该答案"的设计，
> 都是循环论证，无论其输出检查写得多严格。**
> 修输出侧的检查（如 V1.2.1 早期的"结构性引用"要求）**不解决问题** ——
> 必须修**构造侧**。

### 6.4 可执行性自评（**区分两类下游**）

| 判据 | 可执行性 | **确定性下游**下的恒失败场景 | **非确定性下游**（LLM，实测即此类） |
|---|---|---|---|
| S1 | ✅ 可执行 | 下游不引用 `ruleId` | ✅ **不受影响**（结构性引用） |
| S2 | ⚠️ 条件性 | 下游恒返回 `kycGaps: []`（A==B） | ❌ 组内不稳定 → `INCONCLUSIVE` |
| S3 | ✅ 可执行 | 下游不把 `coverageStatus` 降级为 `NOT_RUN` | ✅ **不受影响**（结构化字段决定） |
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
| 1b | **第三次独立复核**：本轮修正（§2.1 构造纪律 + §6.3b 差异校验）仍属**新设计，未经复核** | — | **待办** |
| 2 | **采集器改造**：成对场景 + **每场景 k≥3 次** + 映射程序 + S1 真实调用下游 | 本版 | 待办 |
| 2b | **A/B 输入差异机械校验**：差异字段集合必须恰为上游状态一个字段（§6.3b） | 本版 | 待办 |
| 3 | KERT 补字段（R1/R1b/R2/R3/R4/R5/R6） | Owner 裁定 2 | ✅ **已交付**（KERT `481d696`） |
| 4 | 键审计脚本 | 本版 | ✅ 已完成 |
| 5 | 预注册（锁定哈希） | 须 #1 通过 | 待办 |

> **说明**：已发生两轮独立复核，**两轮都发现了作者（我）没发现的缺陷**；
> **且第二轮发现的，正是「第一轮的修正」引入的新问题**。
> **本节的修正（构造纪律 + 差异校验）同样未经复核** ——
> V1.2.0 的复核已经证明，**修正本身也需要复核**。
> 本版 §2.1 的构造纪律、§6.3b 的构造校验，均为新设计，**尚未被执行过**。
> **不得**因"这是修正版"而假定其正确。
