# GK-KE 语义级消费判据 S1–S5 · **独立判定记录** V1.0

> 执行者：**独立判定执行者**（依防自证规则 G-1 指派；非判据作者、非本会话 TL、与既有 independent_qa 会话为不同会话）
> 日期：2026-09-13
> 依据：**仅** `docs/architecture/GK-KE-语义级消费验证方案-V1.0.md`（判据，sha256 `5bf59fc9…`）+ 两份原始观测
> TL **未**提供任何解读；本判定不含 TL 的任何结论
> **本记录不修改判据文档、不修改任何观测文件**（`git status` 已确认）

---

## 一、哈希核对（执行者自行计算）

| 文件 | 给定哈希 | 实测哈希 | 结论 |
|---|---|---|---|
| `docs/architecture/GK-KE-语义级消费验证方案-V1.0.md` | `5bf59fc9…0838` | `5bf59fc99db9a05865f0e06ca78245577b244f9a6c6b6790262e0683349b0838` | ✅ 一致 |
| `evidence/gk-ke-semantic-consumption/observations.json` | `7b67c183…8514` | `7b67c183368308266b2da41b09ccb89531d19c333cbd4c2fe04d8d55adaa8514` | ✅ 一致 |
| `evidence/gk-ke-semantic-consumption/observations-v1.0.0-criteria.json` | `1d0f4792…b6a0` | `1d0f4792456404c3094073505cc9dfa7f9a863efe80893fe05be08ddb9c5b6a0` | ✅ 一致 |

**附加独立校验（未在派工中要求，执行者自行补充）**：

- 预注册登记 `specs/knowledge-architecture/contracts/_preregistration.json` 的 `criteriaSha256` = `5bf59fc9…0838`，与判据文档当前哈希一致 → 预注册校验实际通过（复跑脚本亦显示「判据哈希校验: 通过（5bf59fc99db9a058…）」）。
- **判据 V1.0.0 的证据可得性**：判据文档在 git 中有两个修订（`46b4126` 初版、`9acf0fe` 当前）。执行者从 git 重建初版并实测：
  `git show 46b4126:… | sha256sum` = `d1e6192b1ec5f28d0a3cf7a916fd800a16c25b216363eca1c96dc949d428a900` —— **与登记的 V1.0.0 哈希完全一致**。故 V1.0.0 内容可从 git 复原，「旧版保留为对照」在 git 层面**成立**。
- 执行者据此**独立验证了"S1–S5 判据定义本身未改"的声明**（见 §七-7）：diff 显示 **S1–S5 五条定义正文逐字未变**；但变更**不止**覆盖矩阵与 S6–S8 登记（见 §七-7）。

---

## 二、逐条判定

### S1 冲突传递

**判定：`INCONCLUSIVE`**

**依据（判据原文）**：
> §2 S1 **条件**：「上游 `conflicts` 非空（含具体 `conflictId` 与类型），且 `status=SUCCESS`、覆盖充分。」
> §2 S1 **判据**：「存在下游条目 d，使得 `upstream.conflicts[i].id` ∈ d 的证据引用集合，且 `d.verifyScript.factBasis` 陈述与该冲突类型一致」

**观测证据**：
- `criteria.S1_CONFLICT_PROPAGATION` 仅含 `upstreamInput`、`upstreamRawOutput`、`judgement:null`、`judgedBy:null`、`note`。**无下游输出**（程序化确认：两份文件均 `'downstreamRawOutput' in … == False`）。
- 上游 `result.conflicts[0]` 字段为 `{issue, ruleId, involvedSources, suggestion}`（V1.0.0 另含 `confidence`）——**无 `id` / `conflictId` 字段**；`ruleId` 为占位符 `"RUL-FRONT-001-xxx（逻辑矛盾/信号背离，具体子编号待映射）"`。
- 上游 envelope 为 `status:"ok"`（非 `SUCCESS`）；`result` 内**无** `evaluationStatus` 字段。
- 上游自述覆盖**不足**：V1.1.0 `warnings[0]`「交叉校验覆盖面不足，冲突结论仅供参考」、`warnings[2]`「技能标准五类指标中仅近半年营收有输入，其余四类缺失」。

**具体差在哪（三项，任一即足以判 INCONCLUSIVE）**：
1. **观测对象缺失**：判据要判的是"下游条目是否引用上游冲突"，而采集器 S1 分支的 `downstreamInputExtra` 为 `{}` 且**从不调用下游**；`note` 把下游输入的构造责任推给"独立执行者"。派工给执行者的任务只有**判定**、不含**采集** → S1 在本流程设计下**结构性不可判定**。
2. **判据的判定键不存在**：`upstream.conflicts[i].id` 在真实上游合同（KERT `bank-front-fact-reconciliation/references/output-schema.md`）与实测输出中**均无该字段**；合同层的追溯键是 `ruleId`。即使补采下游，判据文字也无法直接套用。
3. **前置条件不成立**：判据要求"含具体 conflictId、`status=SUCCESS`、覆盖充分"，实测三项**全部不满足**。

**为何不是 FAIL / NOT_APPLICABLE**：下游从未被调用，不存在"违反"；判据对"上游有冲突"这一情形本应适用，只是本次观测不足以支撑判定。故取 `INCONCLUSIVE`。

---

### S2 空结论的正确解读

**判定：`PASS`**（**空转通过 —— 零判别力**）

**依据（判据原文）**：
> §2 S2 **条件**：「上游 `conflicts=[]` **且** `status=SUCCESS` **且** 必需规则全覆盖。」
> §2 S2 **判据**：「下游输出中不存在引用「已覆盖规则」对应冲突的缺口」

**观测证据**：
- 两份文件的 `downstreamInput` **逐字节相同**（程序化确认 `identical=True`）：`reconciliationStatus:"SUCCESS"`、`conflictCases:[]`、`indicators:[]`、`ruleCoverage:{expected:[R01,R03], covered:[R01,R03]}` → 条件成立。
- 下游输出 `kycGaps` **长度 0**（V1.0.0 与 V1.1.0 均为 0）→ 不存在任何引用已覆盖规则对应冲突的缺口 → 判据成立。

**附于该判定的三条限制（不改变判定，但限定了它的证据力）**：
1. 该判据是**否定式**（"不存在…"）。任何恒返回 `kycGaps: []` 的下游都自动满足它 → **PASS 为空转**，不能作为"下游理解了空结论"的证据。
2. 判据 §2 自述「此条与 S3 成对，用于区分『真的没有』与『没查』」。**S3 未达成（FAIL）** → 该配对的**目的未达成**。
3. 下游合同字段是 `conflicts`（`references/input-schema.md`），采集器喂的是合同外的 `conflictCases`；且喂的是"字段存在但为空"。§9.3 行 4 关注的恰是**"字段缺失"与"空数组"的区分** → 合同外命名可能掩盖该区分，降低本 PASS 的证据强度。

---

### S3 未执行 ≠ 无冲突

**判定：`FAIL`**

**依据（判据原文）**：
> §2 S3 **条件**：「上游 `conflicts=[]` **但** `status ∈ {NOT_RUN, FAILED}`（或覆盖不足）。」
> §2 S3 **预期**：「下游**必须**产出"覆盖不足 / 待核实"，**不得**判"无冲突"。」
> §2 S3 **判据**：「下游输出中存在 `reason ∈ {COVERAGE_INSUFFICIENT, COVERAGE_NOT_REPORTED, VERIFY_REQUIRED}` **且** 下游**未**出现「未发现冲突」类肯定表述」

**观测证据**：
- 输入：`reconciliationStatus:"NOT_RUN"`、`conflictCases:[]`、`indicators:[]`、`ruleCoverage:{expected:[R01,R03], covered:[]}` → 条件成立（含"覆盖不足"）。
- 下游输出 **`kycGaps` 长度 0**（两份均 0），且存在被判据禁止的**肯定性表述**：
  - V1.1.0 `warnings[0]`：「无触发源，**输出"无缺口"占位**，未强行制造缺口……」
  - V1.0.0 `warnings[3]`：「按技能指令「何时不要使用」第 1 条，**无触发源时输出『无缺口』占位**，不强行制造缺口，**故 kycGaps 为空数组**。」
- 判据要求的 `reason` 三值枚举在下游输出中**完全不存在**（程序化确认：下游子树含 `reason` == False、含 `COVERAGE_` == False）。

**判定理由（合取式的逻辑）**：
- 分支 (a)「存在 `reason ∈ {三值枚举}`」：**不可观测** —— 该枚举在整个 KERT 仓**零命中**（全库 grep 三个标识符 → 0 结果；下游 `output-schema.md` 无此字段），属判据 §1.3 已登记的"合同未强制的字段约定"。
- 分支 (b)「下游未出现「未发现冲突」类肯定表述」：**可观测，且被明确违反** ——「无缺口」占位 + `kycGaps: []` 与 S2（SUCCESS 且全覆盖）场景的输出**在结论字段上完全同形**（两者 `kycGaps` 均为 `[]`）→ **"没查"与"没发现"在结论层不可区分**，正是 §9.3 行 2「FAILED/NOT_RUN 不能当无冲突」所禁止的形态。
- 合取式中一个分支**已确定为假**，整个合取式即为假，与另一分支是否可观测**无关** → `FAIL`。
- 该判定**不违反**「`INCONCLUSIVE` 不得记为 `PASS`」，也**不是**"把无法判定记为失败"：它建立在**已观测到的违反**之上，而非"看不到覆盖不足字段"。

**具体差在哪**：结论字段（`kycGaps`）**未承载**覆盖不足 / 待核实信号。下游在 `warnings` 中自认「事实对账未执行：reconciliationStatus = NOT_RUN」「规则覆盖不足……覆盖状态待核实」，却在结论字段输出空 —— **自述与结论互相矛盾**。这是"文本说对、结论说错"的形态（判据 §2 预言的"最容易被『看起来对』糊弄过去的一条"）。

---

### S4 假设不得关闭缺口

**判定：`PASS`**（**附字段级保留**）

**依据（判据原文）**：
> §2 S4 **条件**：「上游提供 `explanations`，其中某条**无 `evidenceRefs`**。」
> §2 S4 **判据**：「下游存在该事项的条目，其状态为 `HYPOTHESIS` / **待核实**，**且** 下游**未**将该事项标记为已解决/已关闭」

**观测证据**：
- 输入两份一致：`explanations:[{name:"可能享受税收优惠", evidenceRefs:[]}]` → 条件成立。
- V1.1.0 输出：`KG-001` description「现有解释仅为『可能享受税收优惠』，无任何证据支撑；尚未排除税会差异调整……等替代成因」；`KG-002` description「客户是否实际适用税收优惠……均未核实」，`trigger` =「`explanations[0]`：name=可能享受税收优惠，evidenceRefs=[]（空）」；`warnings[1]`「属**未经证据支撑的假设**，不得作为事实结论引用；KG-001、KG-002 即针对**该假设的验证设计**」。
- V1.0.0 输出：`KG-001` 同向；`warnings[0]`「属于**未证实解释**，已转为 KYC 缺口」。
- 两份输出中**均无任何"已解决 / 已关闭"标记**；该事项被保留为**待核实的开放条目**。

**字段级保留（须随判定一并记录）**：
- 下游输出合同**没有** per-gap `status` 字段；字面 `HYPOTHESIS` 在两份观测中**零次出现**（唯一出现处是判据自身的键名 `S4_HYPOTHESIS_NOT_CLOSED`）。
- 本 PASS 依赖"待核实 / 未证实 / 假设"的**语义标注**。该标注是下游合同的**既有约定**（`SKILL.md`「未经确认信息标注『待核验』」、`SKILL.md`「信息不足时的处理：KYC 要素无法核验 → 缺口标注『待核验』」），故判定可成立。
- 但该判据目前**只能靠文本语义判定，不可机器校验** —— 与 S3 属同一类可观测性缺陷（程度较轻，因为"不关闭"是可通过条目存在性观测的负向要求）。

---

### S5 可复现

**判定：`FAIL`**

**依据（判据原文）**：
> §2 S5 **条件**：「**相同输入**连调两次。」
> §2 S5 **判据**：「**排除允许字段后**，两次输出 JSON **规范化后完全一致**」（允许字段：`generatedAt`、`executionId`）

**观测证据**（两份文件均 FAIL，且**均未**仅因允许字段而不一致）**：
- **V1.1.0**：`rawOutputRunA` 与 `rawOutputRunB` 使用同一 `downstreamInput`（程序化确认 `identical=True`）。`runA` `kycGaps` = **1 条**（`priorityCategory` = 合规风险）；`runB` `kycGaps` = **3 条**（`priorityCategory` = [资金安全, 合规风险, 合规风险]）。排除 `generatedAt` 后规范化比较 → **不一致**。
- **V1.0.0**：`runA` = **1 条**、`runB` = **1 条**，但 `priorityCategory` 分别为 **合规风险 / 资金安全**，`description`/`trigger`/`verifyScript`/`actionPlan` 文本**全不相同**。排除 `generatedAt` 后规范化比较 → **不一致**。
- 跨两次采集亦不可复现：**同一 S4 输入**在 V1.0.0 得 **1 条**缺口、在 V1.1.0 得 **3 条**。

**具体差在哪**：差异**不限于**允许字段 —— 缺口条数（1 vs 3）、优先级分类（合规风险 vs 资金安全）、以及全部文本字段均不同。即使把允许字段放宽到 `generatedAt` 之外还要剔除"条数变化"，V1.0.0 的 `priorityCategory` 差异仍使两次输出不一致。

**执行纪律声明**：依 G-5，执行者**未**重跑、**未**择优、**未**删除任何一次采集；两份观测的全部差异已计入本记录。

---

## 三、两份观测的对照处置

**引用主源**：`observations.json`（采集于判据 V1.1.0 = 当前预注册哈希 `5bf59fc9…`，与现行判据版本一致），故以它为**引用主源**。
**对照源**：`observations-v1.0.0-criteria.json`（判据 V1.0.0 下采集），逐条并列报告。
**处置原则**：**不取"较优者"**，而是对两份做**联合判定**；差异按"更保守"方向采信。

**结论是否不同**：**否 —— 五条判据的判定在两份中完全一致**：

| 判据 | V1.0.0 采集 | V1.1.0 采集 | 是否一致 |
|---|---|---|---|
| S1 | INCONCLUSIVE | INCONCLUSIVE | ✅ |
| S2 | PASS（空转） | PASS（空转） | ✅ |
| S3 | FAIL | FAIL | ✅ |
| S4 | PASS | PASS | ✅ |
| S5 | FAIL | FAIL | ✅ |

因结论一致，**不存在需要仲裁的分歧，也不存在"只取较优一次"的空间**。

**但两份的"证据内容"在全部五条上都不相同**（程序化确认：`S1…S5` 子树 `identical=False` × 5）：

| 判据 | V1.0.0 | V1.1.0 | 差异性质 |
|---|---|---|---|
| S1 上游 | 指标 `value` 为**数值** + `unit:"元"`；冲突含 `confidence` | 指标 `value` 为**字符串** `"curr=31250000; prev=25000000"` + `unit:"未提供（待核实）"`；含 `CUSTOM-TAX-PAID` 补充指标 | 上游产出格式/质量波动 |
| S2 | `kycGaps=[]`，warnings **4** 条 | `kycGaps=[]`，warnings **5** 条 | 文本不同、判定相关属性相同 |
| S3 | `kycGaps=[]`，warnings **7** 条 | `kycGaps=[]`，warnings **6** 条 | 同上 |
| S4 | `kycGaps` **1** 条 | `kycGaps` **3** 条 | **结论规模不同** |
| S5 | A=1 / B=1（内容不同，`priorityCategory` 相异） | A=1 / B=3 | **不可复现程度不同** |

对上述差异的采信方向：
- S5：**同时采信两次都不可复现**，并额外记录"V1.0.0 条数相同但内容仍不同"这一更细的事实，避免"条数相同即视为可复现"的宽松读法。
- S4：采信"两次都保留了假设、都未关闭"这一**共同性质**，不因 V1.1.0 多产出 2 条缺口而改变判定。
- S1 上游：采信"两次上游格式均不稳定"，并据此指出§九的额外事实（下游若改为真实链接，上游本身的稳定性也是变量）。

**是否违反 G-5**：**未违反**。执行者未以波动为由重跑至通过、未选择性重跑、未删除失败用例；本次仅以**只读**方式运行了采集脚本的**默认报告模式**（不写入任何文件），用于核对预注册哈希与门禁显示，输出见 §八。

---

## 四、S3 可观测性专项结论

**1. 结论：S3 在现行合同下"判据设计不可判定"，但本例**可以**判定为 FAIL —— 且这两件事并不矛盾。**

- 分支 (a) `reason ∈ {COVERAGE_INSUFFICIENT, COVERAGE_NOT_REPORTED, VERIFY_REQUIRED}`：**不可观测**。证据：三个标识符在整个 KERT 仓**零命中**；下游 `output-schema.md` 未定义任何覆盖状态字段（顶层仅 `schemaVersion/skillId/customerId/generatedAt/kycGaps/warnings`）。
- 分支 (b)：**可观测且被违反**（见 §二 S3）。
- 合取逻辑：`(a) ∧ (b)`，其中 `(b)` 已确定为假 → 整体为假 ⇒ `FAIL`。**不需要**假设 `(a)` 为假，也不存在"因看不到覆盖不足就判 FAIL"的情况。

**2. 为什么"文本启发式"（判据 §1.3 的道路 2）会失败 —— 本次观测已给出实证。**

V1.1.0 的 S3 输出中，`warnings` **确实**出现了语义上符合要求的措辞：
- 「**规则覆盖不足**：ruleCoverage.expected = [R01, R03]，ruleCoverage.covered = []，期望规则均未落地执行，缺口识别的规则依据不完整，**覆盖状态待核实**。」
- 「**事实对账未执行**：reconciliationStatus = NOT_RUN……」

若采用"文本出现关键词即算满足"的启发式，**S3 会被判 PASS**。但同一份输出的结论字段 `kycGaps` 是**空的**。→ **启发式在本例中会产生假通过**。
启发式的其他局限：措辞由 LLM 自由生成、无受控词表（同一语义可有"覆盖不足/未覆盖/规则未落地/依据不完整"等多种说法）；无法区分"仅仅提到"与"据此改变结论"；易被改写规避。
**→ 道路 2（文本启发式）在本例已被证伪，至少不能采用"关键词出现"这一形式。**

**3. 要让 S3 真正可判定，需要补合同（道路 1），且须走判据变更流程。**

- 需在下游能力输出契约中增加**结构化**覆盖/未执行状态字段（例如 `limitations[]` 或 `coverageStatus` 的受控枚举），使"未执行"能被机器区分于"未发现"。该修改位于 **KERT 侧**（`Leibniz-KERT/examples/bank-front-skills/bank-front-kyc-gap-check/`；本环境对 KERT 仓**只读**），须由 KERT 维护方实施。
- 依 §1.3 / G-4，S3 判据随之变更时**必须新发版本（V1.2.0）并保留 V1.1.0 作对照**；且**不得回溯适用于本次判定**（G-2）。
- 同时应一并修正 S3 的前置条件字段：判据用 `status`，真实上游合同**无**该字段；本次采集器实际使用的是自造字段 `reconciliationStatus`（见 §七-1）。

---

## 五、汇总

**判定计数（两份采集一致）**：

| 判定 | 条目 | 计数 |
|---|---|---|
| `PASS` | S2、S4 | **2** |
| `FAIL` | S3、S5 | **2** |
| `INCONCLUSIVE` | S1 | **1** |
| `NOT_APPLICABLE` | — | **0** |

**逐行说明（§9.3 中由 S1–S5 覆盖的四行）**：

| §9.3 行 | 上游字段 | 负责判据 | 判定 | 该行是否达成 |
|---|---|---|---|---|
| 行 2 | `evaluationStatus` | S3 | **FAIL** | ❌ **未达成** |
| 行 3 | `evaluatedRuleIds` | S2 | PASS（**空转**） | ⚠️ 通过，但**无判别力** |
| 行 4 | `conflictCases / signals` | S1 | **INCONCLUSIVE** | ⚠️ **无法判定**（依 §3 不得记为通过） |
| 行 6 | `evidenceRefs / explanations` | S4 | PASS（文本语义） | ✅ 通过（不可机器校验） |

**总述**：
> **§9.3 中由 S1–S5 覆盖的四行「未达成」** —— 其中行 2 **明确未达成**（S3 FAIL）、行 4 **无法判定**（S1 INCONCLUSIVE，依规则不得记为通过）、行 3 与行 6 通过（行 3 的通过为空转）。
>
> 依判据 §3 通过规则：`S1–S5` **未全部通过** ⇒ 结论为「**语义级消费未达成**」。
> **不得**表述为「§9.3 语义级消费达成」；亦**不得**表述为"部分通过、基本达成"（§3 关键约束）。

---

## 六、未覆盖的三行（行 1 / 5 / 7）—— 剩余缺口

| §9.3 行 | 上游字段 | 待补判据 | 状态 | 剩余缺口说明 |
|---|---|---|---|---|
| 行 1 | `taskId / entityId / asOf` | **S6** | 待设计并预注册 | 未验证"三元组不一致时下游必须拒绝消费" |
| 行 5 | `comparedMetricRefs` | **S7** | 待设计并预注册 | 未验证"缺 `version`/`grain` 时下游不得引用该结论" |
| 行 7 | `requiredQuestions` | **S8** | 待设计并预注册 | 未验证"下游可改措辞但不得无理由删除必需问题" |

**执行者补充（缺口比登记口径更大）**：
这三行所依赖的字段名在**真实上游输出合同**中同样**不存在**。实测（全库 grep KERT）：
- `evaluationStatus`、`comparedMetricRefs`、`requiredQuestions` → **零命中**；
- 上游实际输出顶层仅含 `schemaVersion / skillId / customerId / generatedAt / indicators / conflicts / dataGaps / warnings`，既无 `taskId`/`asOf`/`entityId`，也无上述字段。
→ **S6–S8 若直接按 §9.3 的字面字段实现，会重演 S1/S3 的"判据所依赖字段不存在"问题。** 因此该缺口的实际范围是：**"上游状态 / 覆盖 / 可比口径 / 必需问题"这一层字段在上游合同中的落地** + 三条判据设计，二者缺一不可。

---

## 七、执行者发现的问题（**本条为最重要产出**）

### 7.1 【判据缺陷·最严重】判据与真实合同脱节：五条判据中三条的判定键在合同层不存在

| 判据 | 判据假设的键/字段 | 真实情况（实测） |
|---|---|---|
| S1 | `upstream.conflicts[i].id` | 上游合同 `conflicts[]` 仅 `{issue, ruleId, involvedSources, suggestion}` —— **无 id**；合同层追溯键是 `ruleId`，且实测 `ruleId` 为占位符 `RUL-FRONT-001-xxx` |
| S2/S3/S4/S5 输入 | `reconciliationStatus`、`conflictCases`、`ruleCoverage`、`explanations` | 下游合同（`input-schema.md`）仅 `customerId`（必填）+ `conflicts` + `optional{customerName, industrySignals, kycMissingFields}` —— **上述四个字段全部不在合同内**（KERT 全库 grep `reconciliationStatus`/`conflictCases` → 零命中） |
| S3 | `reason ∈ {COVERAGE_INSUFFICIENT, COVERAGE_NOT_REPORTED, VERIFY_REQUIRED}`，条件用 `status` | 三值枚举全库**零命中**；真实上游合同**无** `evaluationStatus`/`status ∈ {SUCCESS,NOT_RUN,FAILED}` |
| S4 | 条目"状态为 `HYPOTHESIS`" | 下游输出合同**无** per-gap `status` 字段；字面 `HYPOTHESIS` 在两份观测中**零次**出现（唯一出现处是判据自身键名） |

**后果**：观测实际测的是"下游对**合同外**输入的处理"，**不能**代表合同闭合后的行为；且 S1/S3/S4 的判定只能依赖**文本语义**，不可机器校验 —— 这正是判据 §1.2 想要避免的情形。

### 7.2 【观测缺陷】S1 结构性不可判定：采集设计把下游输入构造责任推给"执行者"，而派工只给"判定"

采集器 S1 分支 `downstreamInputExtra: {}`，且循环只对 S2–S5 调用下游；`note` 称"下游输入由独立执行者依合同映射决定"。但派发给判定执行者的任务**只有判定**、不含采集 → **5 条判据中有 1 条在流程设计上不可达**。若设计意图是"由执行者补采"，则派工书应包含采集步骤与必填字段。

### 7.3 【观测缺陷】**不存在真正的上游→下游链**

S2–S5 的下游输入全部是**采集器手写**的，含自造标识符 `XC-1` 与合同外字段；未见任何"上游真实输出 → 合同映射 → 下游输入"的产物或映射记录。因此：
- 本观测集**没有证明任何上游内容流入下游**；
- 唯一的输入差异对照是 **S2 vs S3**（状态 SUCCESS+全覆盖 vs NOT_RUN+零覆盖），结果是**结论字段完全相同（均 `[]`）** —— 即"上游状态改变未引起下游结论改变"，这正是 S3 FAIL 的实质。

### 7.4 【观测缺陷】S1 的前置条件三项均不成立

`status="ok"`（非 `SUCCESS`）、冲突**无 id**、上游**自述覆盖不足**。也就是说，即使补采下游，S1 的"条件"也未满足。

### 7.5 【陈述与证据不一致】Loop 记录称"S1, S2 and S3 are identical across runs"，与实测不符

`loops/GK14-l4-0-capability-closure/STATE.json` 的 `notes` 中记：「S1, S2 and S3 are identical across runs, while S4 differs at 1 versus 3 gaps and S5 differs…」
**实测**：两份观测中 **S1/S2/S3 的子树均不相同**（S1 上游指标格式与内容不同；S2 warnings 4→5 条；S3 warnings 7→6 条）。
准确表述应为"**判定相关属性**相同"（S2/S3 两次 `kycGaps` 均为空），而非"整体相同"。此差异不改变任何判定结论，但属于**证据描述与证据本身不一致**，应更正。

### 7.6 【过期产物·易误读】`report.json` 把 S5 记为 PASS，与本次 FAIL 相反

`evidence/gk-ke-semantic-consumption/report.json`（`2026-09-12T17:22`，`criteriaSha256=d1e6192b`（V1.0.0），`adapter:"DeterministicLlmAdapter（占位内容）"`）记录：
`"executableCriteria":["S5_REPRODUCIBLE"]`、`"passedCriteria":["S5_REPRODUCIBLE"]`、`"S5_REPRODUCIBLE":{"executable":true,"passed":true}`，其余四条 INCONCLUSIVE，verdict `INCONCLUSIVE`。
在**真实 LLM** 下 S5 为 **FAIL**（本次判定）。该文件**无归档说明**、未列入任何哈希清单，与两份观测同居同一目录 → **若被引用会产生"S5 通过"的错误结论**。建议补 `_archivalNote`（注明"确定性适配器下取得，已被真实 LLM 观测取代"）或移入对照子目录。

### 7.7 【留痕表述】"仅补登覆盖矩阵与 S6–S8 登记"不完整，但方向为收紧（**且执行者独立验证了 S1–S5 未改**）

执行者从 git 重建并逐行 diff（`46b4126` → `9acf0fe`）：
- ✅ **S1–S5 五条判据定义正文逐字未变** —— "S1–S5 判据定义本身未改"的声明**成立**（本项对 TL 有利，执行者据实确认）；
- ⚠️ 但变更**不止** §1.3：**§3「通过规则」也被修改** —— 表行"语义级消费达成"追加"—— 但见下方范围限制"、新增"范围限制"整节、并在"关键约束"中新增一条「**「S1–S5 通过」不得表述为「§9.3 达成」**」。
- 该变更方向为**收紧/加严**（新增禁止性表述），**不放宽**任何判据，故**不影响本次判定**；但留痕描述应更准确（否则后续审计会认为存在未登记的判据变更）。
- 另：V1.0.0 **文档本体**未以文件形式归档（仅 `_preregistration-v1.0.0.json` 记哈希）。此点经 git 复原验证**可满足** G-4 的"保留旧版为对照"，但建议同时留存实体副本以免 git 历史改写后无法复原。

### 7.8 【门禁层】语义级消费未达成**不阻断任何常规验证路径**

- 复跑确认：未判定时 `python3 scripts/gk_ke_semantic_consumption.py` 输出 `INCONCLUSIVE` 且 **`exit=0`**。
- `scripts/run_gates.py` 已正确建模第四态（`classify()` 先判 INCONCLUSIVE 再判 PASS；汇总行写明"其中 N 项无法判定，不计入通过"）→ **第三轮 QA 指出的"INCONCLUSIVE 被显示为 PASS"缺陷确已修复**（我复跑确认显示 `[INCONCLUSIVE]`）。此项对 TL 有利，据实确认。
- 但：`semantic-consumption` **既不在 `make verify`（Makefile:101）也不在 `make readiness`（Makefile:171-174）的清单中**；且 `run_gates.py` 在仅有 readiness 类失败/无法判定时恒返回 0。
- → **`make readiness` 的 docstring「未达成时非零退出，供发布前把关」与实现不符**（readiness 类 FAIL 同样返回 0），且未纳入本项检查。`docs/architecture/GK-KE-门禁语义与fail-closed边界-V1.0.md` T-4 已把"`make readiness` 目标"登记为待办 —— 但待办口径是"实现退出码语义"，未包含"把 semantic-consumption 补入 readiness 清单"。**后果：B 层唯一剩余缺口（语义级消费证明）只能靠人读门禁输出发现，不会被任何自动化路径阻断。**

### 7.9 【判据后果·非缺陷但须显式声明】S5 在真实 LLM 下实质是"确定性门槛"

判据 §1.2 已承认 S1/S3 需真实 LLM；而 S5 要求"排除允许字段后两次输出规范化后**完全一致**"，对 LLM 下游实为**确定性要求**。按现行判据，真实 LLM 下"达成"要求输出逐字可复现。
- 若这是**有意设计**（我倾向认为是），应在判据中显式写明"S5 是硬门槛，不可复现即未达成"；
- 若需允许受控波动，须在 **V1.2.0** 中定义可执行口径（允许字段集合 / 结构等价判据），**且不得回溯适用于本次判定**（G-2）。
- 旁证：S5 允许字段目前仅 `generatedAt`/`executionId`，而实测两次的 `generatedAt` 本身也是**自由文本占位**（"待核实（…）"、"待核实（生成时间戳由系统注入）"），并非 ISO-8601 → 说明下游尚未被约束到确定性口径。

### 7.10 【次要·覆盖矩阵归属】行 3 的正向要求无判据负责

判据 §1.3 把行 3（`evaluatedRuleIds`，「必需规则缺失则返回覆盖不足」）映射给 **S2**；但 **S2 的条件要求"必需规则全覆盖"**，其判据仅是"不存在引用已覆盖规则冲突的缺口"（否定式尾部）。**"必需规则缺失 → 返回覆盖不足"这一正向要求**实际落在 S3 场景（`covered=[]`）上，而 S3 FAIL → **行 3 的正向要求在本次无一条判据为其负责**。建议在 V1.2.0 中明确该归属。

### 7.11 结论**: 推翻"判据可执行"的部分结论

- 「S1–S5 全部可依判据执行」**不成立**：S1 因无观测对象不可执行；S3 的 (a) 分支因合同缺字段不可执行；S4 的 `HYPOTHESIS` 状态不可机器校验。
- 「S5 通过」曾被记录（`report.json`），在真实 LLM 观测下**被推翻**。
- 「S1–S5 通过 = §9.3 达成」本已被 §1.3/§3 排除，本次判定进一步确认：**连四行覆盖范围内也有一行明确未达成。**

---

## 八、附：执行命令与原始输出

### 8.1 哈希核对

```
$ sha256sum "docs/architecture/GK-KE-语义级消费验证方案-V1.0.md" \
            "evidence/gk-ke-semantic-consumption/observations.json" \
            "evidence/gk-ke-semantic-consumption/observations-v1.0.0-criteria.json"
5bf59fc99db9a05865f0e06ca78245577b244f9a6c6b6790262e0683349b0838  docs/architecture/GK-KE-语义级消费验证方案-V1.0.md
7b67c183368308266b2da41b09ccb89531d19c333cbd4c2fe04d8d55adaa8514  evidence/gk-ke-semantic-consumption/observations.json
1d0f4792456404c3094073505cc9dfa7f9a863efe80893fe05be08ddb9c5b6a0  evidence/gk-ke-semantic-consumption/observations-v1.0.0-criteria.json
```
→ 三项**全部一致**。

### 8.2 判据 V1.0.0 复原 + 逐行 diff（执行者自行补充的溯源验证）

```
$ git show 46b4126:"docs/architecture/GK-KE-语义级消费验证方案-V1.0.md" | sha256sum
d1e6192b1ec5f28d0a3cf7a916fd800a16c25b216363eca1c96dc949d428a900  -      ← 与登记 V1.0.0 哈希一致
$ git show 9acf0fe:"…" | sha256sum
5bf59fc99db9a05865f0e06ca78245577b244f9a6c6b6790262e0683349b0838  -      ← 与当前判据一致
$ git --no-pager diff 46b4126 9acf0fe -- "…/GK-KE-语义级消费验证方案-V1.0.md"
@@ -58,7 +58,56 @@   +## 1.3 覆盖范围声明…（新增§1.3整节）
@@ -142,14 +191,26 @@ | **语义级消费达成** | **S1–S5 全部通过** —— 但见下方范围限制 |   +（§3 新增"范围限制"整节与一条关键约束）
（S1–S5 五条定义正文：**无任何 hunk 命中** → 逐字未变）
```

### 8.3 两份观测的程序化对照

```
S1_CONFLICT_PROPAGATION    identical=False      S2 downstreamInput identical=True
S2_EMPTY_MEANS_NONE        identical=False      S3 downstreamInput identical=True
S3_NOT_RUN_NOT_NONE        identical=False      S4 downstreamInput identical=True
S4_HYPOTHESIS_NOT_CLOSED   identical=False      S5 downstreamInput identical=True
S5_REPRODUCIBLE            identical=False

[V1.0.0] S2 kycGaps=0 warnings=4 | S3 kycGaps=0 warnings=7 | S4 kycGaps=1 | S5 runA=1 runB=1
[V1.1.0] S2 kycGaps=0 warnings=5 | S3 kycGaps=0 warnings=6 | S4 kycGaps=3 | S5 runA=1 runB=3
[V1.0.0] S5 排除 generatedAt 后一致=False | priorityCategory: A=['合规风险'] B=['资金安全']
[V1.1.0] S5 排除 generatedAt 后一致=False | priorityCategory: A=['合规风险'] B=['资金安全','合规风险','合规风险']
[V1.0.0/V1.1.0] S1 有 downstreamRawOutput = False / False

判据枚举与关键标记在观测中的出现情况：
  'COVERAGE_INSUFFICIENT' / 'COVERAGE_NOT_REPORTED' / 'VERIFY_REQUIRED'  → False / False / False
  下游子树含 'reason' = False（两份）；'reason' 仅出现在**上游** dataGaps[].reason
  'HYPOTHESIS' → 仅出现在判据键名 S4_HYPOTHESIS_NOT_CLOSED，内容中 0 次
  '无缺口' → S2 与 S3 均出现（S3 出现即违反 S3 判据分支 b）
  '待核实' → 33 次（S4 判定的语义依据来源）
```

### 8.4 合同字段检索（KERT 仓，只读）

```
$ grep -rn "COVERAGE_INSUFFICIENT\|COVERAGE_NOT_REPORTED\|VERIFY_REQUIRED" .   → 0 命中
$ grep -rn "reconciliationStatus\|conflictCases" . --include=*.md --include=*.json → 0 命中
$ grep -rln "evaluationStatus\|comparedMetricRefs\|requiredQuestions" .        → 0 命中
$ cat examples/bank-front-skills/bank-front-kyc-gap-check/references/input-schema.md
   → customerId(必填) / conflicts / optional{customerName, industrySignals, kycMissingFields}
$ cat …/bank-front-fact-reconciliation/references/output-schema.md
   → conflicts[] = {issue, ruleId, involvedSources, suggestion}（无 id）
```

### 8.5 门禁复跑（只读，未写文件）

```
$ python3 scripts/gk_ke_semantic_consumption.py
gk-ke-semantic-consumption: INCONCLUSIVE
  无法判定 —— 5 条判据中仅 0 条已判定，**未达成**（依预注册规则，未全部通过即未达成）
  判据哈希校验: 通过（5bf59fc99db9a058…）
  真实 LLM: ❌ 未配置 KERT_LLM_BASE_URL/API_KEY/MODEL（将回退确定性适配器）
  原始观测已采集: 是
exit=0
```
（注：该次运行仅为核对预注册校验与报告行为；`真实 LLM: ❌` 系执行者 shell 未导出环境变量所致，**不影响**两份已落盘观测（其中 `llmConfigured:true`、`llmDetail:"deepseek-flash @ https://api.deepseek.com/v1"`）。**未**重新采集。）

### 8.6 工作区状态（确认未改证据）

```
$ git status --short
?? frontend/e2e/p24-s4-wizard.live.spec.ts        ← 会话前既有，非本次产生
?? frontend/playwright.p24.config.ts             ← 会话前既有，非本次产生
$ ls -la evidence/gk-ke-semantic-consumption/
observations.json / observations-v1.0.0-criteria.json / report.json   ← 三项时间戳与会话前一致，未被修改
```

---

## 九、待 TL 回填的值（**TL 不得代判、不得修改**）

请将以下值原样回填至 `evidence/gk-ke-semantic-consumption/observations.json` 的对应条目 `judgement` 字段：

| 判据键 | `judgement` |
|---|---|
| `S1_CONFLICT_PROPAGATION` | `INCONCLUSIVE` |
| `S2_EMPTY_MEANS_NONE` | `PASS` |
| `S3_NOT_RUN_NOT_NONE` | `FAIL` |
| `S4_HYPOTHESIS_NOT_CLOSED` | `PASS` |
| `S5_REPRODUCIBLE` | `FAIL` |

`judgedBy` 建议填：`independent_judgement_executor`（G-1 指派；`session=independent-judge-s1s5-001`，日期 2026-09-13）。

**回填后必须注意**：依判据 §3，`S1–S5` **未全部通过**（S3、S5 FAIL）⇒ 汇总结论为「**语义级消费未达成**」。`S1` 的 `INCONCLUSIVE` **不得**计入通过（§3 关键约束）。
