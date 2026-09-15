# GK-KE：语义级消费验证方案（**预注册**）V1.2.0

> 出具：GK-KE 全局 Tech Lead｜日期：2026-09-13
> 依据：建议书 §9.3 / §6.5 / §14.2 第 6 项
> 前版：V1.0.0（[归档](archive/GK-KE-语义级消费验证方案-V1.0.0.md)）、V1.1.0（[归档](archive/GK-KE-语义级消费验证方案-V1.1.0.md)）
> **性质：预注册（pre-registration）。判定标准先于执行锁定，执行后不得修改。**
> **依 G-2：本版判据不得回溯适用于 V1.1.0 下的既有判定。**

---

## 0. 本版为何存在 —— 一句话

> **V1.1.0 的五条判据中，三条的判定键在真实合同里不存在；
> 两条依赖自由文本，其中一条已被实测证伪。
> V1.2.0 把这套"按想象写判据"的方法换成"按合同写判据 + 按对比测消费"。**

### 0.1 修正来源（独立判定执行者 V1.1.0 判定 + 合同审计）

| # | V1.1.0 的缺陷 | 证据 | 本版处置 |
|---|---|---|---|
| 1 | 判据假设的键**在合同中不存在** | `evaluationStatus`/`reconciliationStatus`/`comparedMetricRefs`/`requiredQuestions`/`conflictId`/`conflicts[].id` **全库命中 0** | **§1 全部判定键重新取自真实合同** |
| 2 | S3 结构化分支**不可观测** | `COVERAGE_INSUFFICIENT`/`COVERAGE_NOT_REPORTED`/`VERIFY_REQUIRED` **全库命中 0** | **S3 改为对比式（立即可执行）**，并在 §5 请 KERT 补结构化字段 |
| 3 | 文本启发式**已被证伪** | S3 实测：`warnings` 写了"规则覆盖不足""覆盖状态待核实"，**结论字段 `kycGaps` 却是空的** → 关键词启发式会假通过 | **§1.2 明令禁止将自由文本作为判定键** |
| 4 | S1 采集器**从不调用下游** | 采集器 S1 分支 `downstreamInputExtra: {}` | **S1 纳入成对采集** |
| 5 | S5 实为**确定性门槛**却未写明 | V1.1.0 §2 未声明 | **S5 显式声明为硬门槛**；并修正允许字段判据 |
| 6 | 行 3 正向要求**无判据负责** | S2 条件是"全覆盖"，其判据是否定式尾部 | **S3 承接该正向要求** |

### 0.2 本版的核心方法变更

| V1.1.0（已证伪的方法） | V1.2.0（本版） |
|---|---|
| **按字段存在性断言**：下游输出里"有没有"某个字段 | **按对比测依赖**：改变上游输入，下游结论**是否跟着变** |
| 依赖自由文本描述 | 只依赖**合同定义的字段**与**跨场景差异** |
| 单场景运行 | **成对场景**运行（同一能力，两种上游状态） |

> **为什么对比式更本质**：§14.2 第 6 项要求的是"**能力之间真正消费结果**"。
> "消费"在语义上就是**依赖关系** —— 而依赖关系只能通过"**改变 A、观察 B 是否变**"来证明。
> 字段存在性不是消费的必要条件（下游完全可以在不引用某字段的情况下正确地消费它）。
>
> **且对比式无法被空转满足**：恒返回空数组的下游在两种场景下输出相同 → 判 FAIL。
> 这直接修掉了 V1.1.0 中 S2"空转通过"的问题。

---

## 1. 判定键白名单（**全部取自真实合同，逐项标注出处**）

> **纪律**：任何判据**只能**使用本节列出的键。
> 未列出的标识符一律不得作为判定键 —— 这是对 7.1 缺陷的机械化防线（见 §6 审计脚本）。

### 1.1 上游能力（事实对账与冲突检测 `SK-FRONT-004`）

合同文件：`Leibniz-KERT/examples/bank-front-skills/bank-front-fact-reconciliation/references/output-schema.md`

| 键 | 类型 | 枚举/说明 | 合同出处 |
|---|---|---|---|
| `schemaVersion` | string | — | `output-schema.md:7` |
| `skillId` | string | `"SK-FRONT-004"` | `output-schema.md:8` |
| `customerId` | string | — | `output-schema.md:9` |
| `generatedAt` | string (ISO-8601) | — | `output-schema.md:10` |
| `indicators[]` | array | — | `output-schema.md:11` |
| `indicators[].elementId` | string | — | `output-schema.md:13` |
| `indicators[].name` | string | 例「近半年营收」 | `output-schema.md:14` |
| `indicators[].value` | 数值 | — | `output-schema.md:15` |
| `indicators[].unit` | string | 例「万元」 | `output-schema.md:15` |
| **`indicators[].status`** | string | **`verified \| pending \| missing`** | `output-schema.md:17`；`SKILL.md:119` |
| `indicators[].dataTimestamp` | string | 数据时点 | `output-schema.md:16` |
| `indicators[].changeRate` | string | 同比% | `output-schema.md:15` |
| `indicators[].source` | string | 例 `T-CORE-001` | `output-schema.md:16` |
| `conflicts[]` | array | — | `output-schema.md:20` |
| **`conflicts[].ruleId`** | string | 形如 `RUL-FRONT-001-xxx` | `output-schema.md:23` |
| `conflicts[].issue` | string | — | `output-schema.md:22` |
| `conflicts[].involvedSources` | array\<string\> | — | `output-schema.md:24` |
| **`conflicts[].suggestion`** | string | 「建议的核实问题」 | `output-schema.md:25` |
| `dataGaps[]` | array | — | `output-schema.md:28` |
| `dataGaps[].indicator` | string | — | `output-schema.md:29` |
| `dataGaps[].reason` | string | — | `output-schema.md:29` |
| `dataGaps[].action` | string | — | `output-schema.md:29` |

**不存在（已全库 grep，命中 0，禁止作为判定键）**：
`evaluationStatus`、`status`（顶层）、`conflicts[].id`、`conflictId`、`taskId`、`entityId`、`asOf`

### 1.2 下游能力（KYC 缺口核验 `SK-FRONT-006`）

**输入合同**：`bank-front-kyc-gap-check/references/input-schema.md`

| 键 | 类型 | 必填 | 合同出处 |
|---|---|---|---|
| `customerId` | string | **是** | `input-schema.md:7` |
| `conflicts[]` | array | 建议 | `input-schema.md:8` |
| `conflicts[].issue` | string | — | `input-schema.md:10` |
| `conflicts[].ruleId` | string | — | `input-schema.md:11` |
| `optional.customerName` | string | 否 | `input-schema.md:15` |
| `optional.industrySignals` | array\<string\> | 否 | `input-schema.md:16` |
| `optional.kycMissingFields` | array\<string\> | 否 | `input-schema.md:17` |

****不存在**（禁止使用）**：`reconciliationStatus`、`conflictCases`、`ruleCoverage`、`explanations`、`indicators`
（注：**不把 `indicators[]` 直接喂给下游** —— 下游合同不接收该字段。
上游状态须经 §2 的**映射**表达为下游可接收的形式。）

**输出合同**：`bank-front-kyc-gap-check/references/output-schema.md`

| 键 | 类型 | 枚举/说明 | 合同出处 |
|---|---|---|---|
| `schemaVersion` | string | — | `output-schema.md:7` |
| `skillId` | string | `"SK-FRONT-006"` | `output-schema.md:8` |
| `customerId` | string | — | `output-schema.md:9` |
| `generatedAt` | string (ISO-8601) | — | `output-schema.md:10` |
| `kycGaps[]` | array | — | `output-schema.md:11` |
| `kycGaps[].gapId` | string | 例 `KG-001` | `output-schema.md:13` |
| `kycGaps[].description` | string | — | `output-schema.md:14` |
| **`kycGaps[].trigger`** | string | 关联 `RUL-FRONT-001-xxx` | `output-schema.md:15` |
| `kycGaps[].priority` | string | `high \| medium \| general` | `output-schema.md:16` |
| `kycGaps[].priorityCategory` | string | `资金安全 \| 合规风险 \| 经营决策` | `output-schema.md:17` |
| **`kycGaps[].verifyScript.factBasis`** | string | — | `output-schema.md:19` |
| **`kycGaps[].verifyScript.question`** | string | — | `output-schema.md:20` |
| `kycGaps[].verifyScript.goal` | string | — | `output-schema.md:21` |
| `kycGaps[].actionPlan.verifyGoal` | string | — | `output-schema.md:24` |
| `kycGaps[].actionPlan.timing` | string | — | `output-schema.md:25` |
| `kycGaps[].actionPlan.path` | array\<string\> | — | `output-schema.md:26` |
| `warnings[]` | array\<string\> | **仅可作旁证，禁止作判定键** | `output-schema.md:30` |

**不存在（禁止使用）**：`limitations`、`coverageStatus`、per-gap `status`、`reason` 枚举、
`HYPOTHESIS`、`COVERAGE_*`、`VERIFY_REQUIRED`

> **`warnings[]` 的纪律**（**本版最重要的单条纪律**）：
> `warnings[]` 是**自由文本**。实测证明：下游可以在 `warnings` 里正确写出"覆盖不足"，
> 同时结论字段给出错误的空值。
> **故：`warnings` 中出现任何关键词，一律不得作为判据满足的证据。**
> 它只能用于**追加说明**，不得改变判定。

---

## 2. 上游状态的形式化（**由真实合同字段派生，不引入新字段**）

V1.1.0 假设上游有 `status ∈ {SUCCESS, NOT_RUN, FAILED}` —— **该字段不存在**。
本版改用**可由真实字段计算**的状态函数：

```
coverage(U) :=
  FULL    iff  U.indicators ≠ []  ∧  ∀i: i.status == "verified"  ∧  U.dataGaps == []
  PARTIAL iff  U.indicators ≠ []  ∧  (∃i: i.status ∈ {"pending","missing"}  ∨  U.dataGaps ≠ [])
  NONE    iff  U.indicators == []  ∨  ∀i: i.status == "missing"

notRun(U)   :=  coverage(U) == NONE
hasConflict(U) := U.conflicts ≠ []
placeholder(U) := ∃c ∈ U.conflicts: c.ruleId 含 "xxx" 或为空
```

**全部取自 §1.1 白名单**（`indicators[].status` 为合同定义的受控枚举）。

### 2.1 上游 → 下游的**映射**（须在采集器中显式实现并留痕）

下游合同**不接收** `indicators`/`dataGaps`。故上游状态须表达为下游**可接收**的形式：

| 上游状态 | 下游输入构造 | 依据 |
|---|---|---|
| `coverage=NONE` | `conflicts: []` **且** `optional.kycMissingFields` 中显式加入**本场景的待补数据项** | `input-schema.md:17` |
| `coverage=PARTIAL` | `conflicts` 照传；`kycMissingFields` 加入 `dataGaps[].indicator` | `input-schema.md:16-17` |
| `coverage=FULL` 且无冲突 | `conflicts: []`，`kycMissingFields: []` | — |

> **留痕要求**：采集器必须**同时落盘**「上游原始输出」与「下游输入」，并附**映射脚本**。
> V1.1.0 的下游输入是**手写的**，故 7.3 指出"不存在真正的上游→下游链"。
> 本版要求：**下游输入必须是从上游原始输出经映射程序生成的**，不得手写。

---

## 3. 判据 S1–S5（V1.2.0）

> 通用约定：
> · **成对场景** A / B：A = `coverage=FULL, conflicts=[]`；B = `coverage=NONE, conflicts=[]`
> · 每个判据**须自行声明**其可执行性：`可执行` / `待 KERT`（依 §5）
> · **`warnings[]` 不得作为判定键**（§1.2）

### S1 冲突传递 · `S1_CONFLICT_PROPAGATION`

- **条件**：`hasConflict(U)` 且 **非** `placeholder(U)` 且 `coverage(U) ∈ {FULL, PARTIAL}`
- **判据**：存在下游 `kycGaps[]` 条目 `d`，使得 **∃i**：`U.conflicts[i].ruleId` 出现在
  `d.trigger` 或 `d.verifyScript.factBasis` 中（**子串匹配 `ruleId` 的字面值**）
- **判定键**：`conflicts[].ruleId` ✅ / `kycGaps[].trigger` ✅ / `kycGaps[].verifyScript.factBasis` ✅
- **可执行性**：**可执行**（键全部真实存在）
- **前置质量门**：若 `placeholder(U)` 为真 → 判 **`INCONCLUSIVE`** 并**归因上游**
  （V1.1.0 实测 `ruleId = "RUL-FRONT-001-xxx（逻辑矛盾/信号背离，具体子编号待映射）"`
  —— 占位符不可作为追溯键，这是**上游产出质量问题**，不是下游消费问题）
- **采集要求**：**必须真实调用下游**（修 7.2 的结构性不可判定）

### S2 空结论的正确解读 · `S2_EMPTY_MEANS_NONE`

> **本版改为成对判据，消除 V1.1.0 的空转。**

- **条件**：成对 A / B 均已运行
- **判据**（**合取**，两者均须满足）：
  - (a) `downstream(A).kycGaps` 中不存在引用"已覆盖规则"的缺口
    （即：不存在 `d` 使 `d.trigger` 匹配 `U_A` 的任一 `conflicts[].ruleId`）—— 原否定式部分
  - (b) **`downstream(A).kycGaps` ≠ `downstream(B).kycGaps`**（规范化后比较）
    —— 证明下游**确实读了上游状态**，而非恒返回空
- **判定键**：`kycGaps` ✅（全部真实存在）
- **可执行性**：**可执行**
- **为何必须加 (b)**：仅有 (a) 时，**任何恒返回 `kycGaps: []` 的下游都自动通过**（V1.1.0 的 S2 即如此）。
  加 (b) 后，这类下游在 B 场景下仍返回空 → A == B → **FAIL**。**空转被机械消除。**
- **与 S5 的区别**：S2 比的是**跨场景**（A vs B）；S5 比的是**同场景两次**（A1 vs A2）。

### S3 未执行 ≠ 无冲突 · `S3_NOT_RUN_NOT_NONE`

> **承接 §9.3 行 3 的正向要求**（"必需规则缺失则返回覆盖不足"，V1.1.0 无判据负责 —— 修 7.10）。
> **不得**使用不存在字段或自由文本。

- **条件**：成对 A / B 均已运行，且 `notRun(U_B)` 为真
- **判据**（**析取**，任一满足即通过）：
  - **(a) 结构化路径 · 待 KERT**：
    下游输出含**结构化**覆盖/限制状态字段（§5 请求项），其值在 A 与 B 下**不同**且方向正确
  - **(b) 对比路径 · 立即可执行**：
    **`downstream(B).kycGaps` ≠ `downstream(A).kycGaps`**，且差异方向正确：
    `len(downstream(B).kycGaps) > len(downstream(A).kycGaps)`，
    或 B 中存在 `d` 使 `d.trigger` / `d.verifyScript.factBasis` 引用了
    `U_B.dataGaps[].indicator` 或 `U_B.indicators[].name`（即：下游把"上游没查"转成了缺口）
- **判定键**：`kycGaps`（长度与内容）✅ / `dataGaps[].indicator` ✅ / `indicators[].name` ✅
- **可执行性**：**(b) 可执行**；(a) 待 KERT 交付后启用
- **明确禁止**：以 `warnings[]` 中出现"覆盖不足""待核实"等措辞作为通过依据
  （**V1.1.0 实测已证伪此路**：措辞存在而结论为空）

### S4 假设不得关闭缺口 · `S4_HYPOTHESIS_NOT_CLOSED`

> V1.1.0 的 `explanations` 与 `HYPOTHESIS` **均不存在**。本版改由真实字段表达。

- **条件**：`U.indicators[]` 中存在 `status ∈ {"pending","missing"}` 的指标
  （合同定义的"未经确认"状态 —— 替代不存在的 `explanations`）
- **判据**（**合取**）：
  - (a) 下游存在条目 `d`，使 `U.indicators[k].name` 出现在 `d.description` 或
    `d.verifyScript.factBasis` 中（**缺口确实指向该未确认项**）
  - (b) 该条目**未**被标记为已解决/已关闭 —— 机器可校验的弱形式：
    `d.verifyScript.question` 与 `d.actionPlan.path` **均非空**
    （即：仍给出待办核实动作；空动作 = 已关闭）
- **判定键**：`indicators[].status` ✅ / `indicators[].name` ✅ /
  `kycGaps[].description` ✅ / `verifyScript.question` ✅ / `actionPlan.path` ✅
- **可执行性**：**可执行**（(b) 用"动作非空"作机器代理；语义完备性仍须人工复核，故**记录残余文本依赖**）
- **残余限制（须随判定记录）**：(b) 是**代理指标**，不能排除"给了动作但实质已关闭"。
  本版承认该残余，**不得**据此声称"完全可机器校验"。

### S5 可复现 · `S5_REPRODUCIBLE`

- **性质声明（**本版新增**）**：**S5 是确定性硬门槛。**
  **对 LLM 下游，本判据要求逐字可复现；不可复现即未达成。**
  如需允许受控波动，必须**新发版本**定义可执行口径（允许字段集合 / 结构等价判据），
  **且不得回溯适用**（依 G-2）。
- **条件**：**同一场景 A**、**相同下游输入**、**连续两次调用**
- **判据**（**合取**）：
  - (a) 排除允许字段后，两次输出 JSON **规范化后完全一致**
  - (b) 允许字段**仅**：`generatedAt`；且 `generatedAt` **必须是合法 ISO-8601**
    （**变更**：V1.1.0 的允许集合含 `executionId`，但合同审计确认下游输出合同
    **无**该字段 —— 把不存在的字段列为"允许"无意义，已删除）
    （**新增**：V1.1.0 实测 `generatedAt` 为自由文本"待核实（…）" ——
    此时该字段**不获豁免**，其差异**直接判 FAIL**）
  - (c) `skillId` / `customerId` / `schemaVersion` 两次一致
- **判定键**：全部顶层字段 ✅
- **可执行性**：**可执行**

---

## 4. S6–S8（行 1 / 5 / 7）—— **本版只登记，不声称可执行**

> 独立执行者 7.10 指出：这三行所依赖的字段名**在真实上游输出合同中同样不存在**。
> 合同审计**确认**该结论（`taskId`/`entityId`/`asOf`/`comparedMetricRefs`/`requiredQuestions`
> 在两个目标能力目录中命中 **0**）。

| 行 | V1.1.0 假设的键 | 真实情况 | 本版处置 |
|---|---|---|---|
| 1 | `taskId` / `entityId` / `asOf` | **不存在** | **待 KERT**；本版仅立可执行子项：`customerId` 上下游一致 |
| 5 | `comparedMetricRefs` | **不存在** | **待 KERT**；上游侧可用 `indicators[].{unit, dataTimestamp}` 做前置质量门 |
| 7 | `requiredQuestions` | **不存在** | **待 KERT**；上游侧可用 `conflicts[].suggestion`，下游侧 `kycGaps[].verifyScript.question` |

### S6' `customerId` 传递一致性（**立即可执行**）

- **条件**：A 场景
- **判据**：`downstream.customerId == upstream.customerId`
- **判定键**：`customerId` ✅（上游 `output-schema.md:9`，下游 `output-schema.md:9`）
- **可执行性**：**可执行**

### S7' 口径前置质量门（**上游侧，立即可执行**）

- **条件**：`U.indicators ≠ []`
- **判据**：每条指标**必须**具备非空 `unit` 与非空 `dataTimestamp`
- **判定键**：`indicators[].unit` ✅ / `indicators[].dataTimestamp` ✅
- **可执行性**：**上游侧可执行**；**下游侧引用检查待 KERT**
- **注**：V1.1.0 实测上游出现过 `unit: "未提供（待核实）"`、`value` 为自由字符串
  —— 本判据即针对该形态。

### S8' 核实问题不得删除（**部分可执行**）

- **条件**：`hasConflict(U)` 且非 `placeholder(U)`
- **判据**：
  - (a) **数量约束（可机器校验）**：
    `|{d.verifyScript.question : d ∈ downstream.kycGaps}| ≥ |U.conflicts|`
  - (b) **对应性（须人工语义比对）**：每条 `U.conflicts[i].suggestion` 的核实意图
    在下游某 `verifyScript.question` 中有对应（**允许改措辞**，不允许无理由删除）
- **判定键**：`conflicts[].suggestion` ✅ / `kycGaps[].verifyScript.question` ✅
- **可执行性**：(a) **可执行**；(b) **须独立执行者语义比对**，须显式标注

---

## 5. 请 KERT 侧补的字段（**S3 结构化路径的唯一出路**）

> Owner 裁定 2。跨仓只读，故以**请求**形式提出（见 `GK-KE-致KERT维护方-判据V1.2所依赖字段补充请求-V1.0.md`）。

| # | 能力 | 请求新增 | 理由 | 优先级 |
|---|---|---|---|---|
| **R1** | 下游 `SK-FRONT-006` | 输出顶层结构化**覆盖/限制状态**字段（受控枚举，如 `limitations[]` 或 `coverageStatus`） | 使"未执行"与"无缺口"在**结论层**可区分 —— S3 结构化路径的唯一前提 | **P0** |
| **R2** | 下游 `SK-FRONT-006` | `kycGaps[]` 元素增加 per-gap `status`（受控枚举） | 使 S4 的"不得关闭"可机器校验 | P1 |
| **R3** | 上游 `SK-FRONT-004` | 输出顶层结构化**执行状态**字段（替代不存在的 `evaluationStatus`） | 使 `coverage()` 有权威来源而非派生 | P1 |
| **R4** | 上游 `SK-FRONT-004` | `conflicts[]` 增加稳定唯一 `id`（与 `ruleId` 并列） | 使 S1 追溯键稳定（现 `ruleId` 实测为占位符） | P1 |
| **R5** | 上游 `SK-FRONT-004` | `conflicts[].ruleId` **必须为具体子编号**（禁 `xxx` 占位符） | 占位符使追溯不可用 | **P0** |
| **R6** | 上游 `SK-FRONT-004` | 补 `taskId` / `asOf` | S6/S7 前置（行 1/5/7） | P2 |

**若 KERT 不补**：S3 仅能走对比路径 (b)（可执行，但证据力弱于结构化路径）；
S4 仅能走代理指标；行 1/5/7 维持无判据覆盖。

---

## 6. 反复发机制（**本版最重要的一节**）

> 7.1 的根因不是"我写错了字段名"，而是**没有任何机制检查我写的字段名是否存在**。
> 不加这个机制，V1.3.0 会重犯。

### 6.1 判据键审计脚本（**新增，强制**）

`scripts/gk_ke_criteria_key_audit.py`：

1. 从本判据文档 §1 白名单中提取**全部**判定键
2. 从**真实合同文件**解析实际存在的字段集合
3. **任一白名单键在合同中不存在 → 非零退出**（fail-closed）
4. 同时反向检查：判据正文中出现的反引号标识符**是否都在白名单内**
   （防止正文偷偷使用未登记键）

**纳入 `make verify`**，作为**完整性门禁**（失败即阻断）。

### 6.2 判据变更的三项强制检查

| # | 检查 | 目的 |
|---|---|---|
| 1 | **键存在性**（§6.1 脚本） | 不再写不存在的键 |
| 2 | **范式检查**：新增判据**不得**以自由文本为判定键 | 不再写会被关键词糊弄的判据 |
| 3 | **不可空转检查**：新增判据**必须**存在一种"错误的下游"使其判 FAIL | 不再写恒真判据 |

> 第 3 条源自 V1.1.0 的 S2 教训：**恒真判据 = 零判别力**。
> 每条判据须在文档中**显式写出**"什么样的下游会失败"。

### 6.3 本版可执行性自评

| 判据 | 可执行性 | 恒失败场景（判别力证明） |
|---|---|---|
| S1 | ✅ 可执行 | 下游不引用 `ruleId` |
| S2 | ✅ 可执行 | 下游恒返回 `kycGaps: []`（A==B） |
| S3 | ✅ (b) 可执行；(a) 待 KERT | 下游对 NONE 场景仍返回空（与 A 相同） |
| S4 | ✅ 可执行（(b) 为代理） | 下游不产出指向 `pending` 指标的条目 |
| S5 | ✅ 可执行 | 同输入两次输出不同 |
| S6' | ✅ 可执行 | `customerId` 被改写 |
| S7' | ✅ 上游侧可执行 | 上游指标缺 `unit`/`dataTimestamp` |
| S8' | ⚠️ (a) 可执行；(b) 须人工 | 下游 `question` 数少于 `conflicts` 数 |

---

## 7. 通过规则（**承 V1.1.0，未放宽**）

| 结论 | 条件 |
|---|---|
| **语义级消费达成（S1–S5 覆盖的四行）** | `S1–S5` **全部** `PASS` |
| 未达成 | 任一 `FAIL` |
| **不得记为通过** | 任一 `INCONCLUSIVE`；或未全部判定 |

**白名单完整性声明**：S7' 使用 `indicators[].dataTimestamp` 等字段，
现已在 §1.1 白名单登记（均为合同真实字段）。
**补登动因**：键审计脚本 L3 告警发现"S7' 使用了未登记字段" ——
**审计器发现了作者文档的内部不一致**，这正是它存在的意义。
同理，`executionId` 被发现列于"允许字段"却**不在合同中**，已删除。

**范围限制（**须随任何结论一并声明**）**：
- 本方案**仅覆盖** §9.3 的行 2 / 3 / 4 / 6
- 行 1 / 5 / 7 **无完整判据覆盖**（S6'–S8' 仅覆盖其可执行子集）
- **故「S1–S5 通过」不得表述为「§9.3 达成」**

**禁止的表述**：
- ❌「§9.3 语义级消费达成」　❌「部分通过、基本达成」　❌「B 层接近达成」

**允许的表述**：
- ✅「**输入级消费已证明；语义级消费（S1–S5 覆盖范围）已达成/未达成**」（据实）

---

## 8. 与 V1.1.0 的关系

| 项 | 说明 |
|---|---|
| V1.1.0 判定**保留** | V1.1.0 下的判定（S3 FAIL / S5 FAIL / S1 INCONCLUSIVE / S2 PASS / S4 PASS）**有效且不得重写** |
| **不得回溯** | 本版判据**不得**用于重新判定 V1.1.0 的观测（依 G-2） |
| V1.1.0 观测**可复核但不可改判** | 本版新采集须**独立成组**，与旧观测**分开存放** |
| 旧版保留为对照 | V1.0.0 / V1.1.0 实体副本见 `archive/`，哈希见 `_criteria-versions.json` |

---

## 9. 待办与依赖

| # | 事项 | 依赖 |
|---|---|---|
| 1 | **采集器改造**：实现 §2 映射程序 + 成对场景（A/B）+ S1 真实调用下游 | 本版 |
| 2 | **键审计脚本**纳入 `make verify` | 本版 |
| 3 | **KERT 补字段**（R1 为 P0） | Owner 裁定 2 已批准，须发函 |
| 4 | **本版独立复核**：建议由**非作者会话**复核判据与白名单 | 建议 |
| 5 | 预注册（锁定哈希）后再采集 | 本版 |

> **说明**：V1.1.0 的判据由我撰写，执行者测试后发现 3/5 条判定键不存在。
> 为避免**同一作者再犯同一错误**，第 4 项建议**独立复核判据本身**（非判定）。
> 是否执行由 Owner 裁定。
