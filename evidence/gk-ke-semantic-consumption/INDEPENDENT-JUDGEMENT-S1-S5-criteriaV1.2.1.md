# GK-KE 语义级消费判据 S1–S5 · **独立判定记录**（判据版本 V1.2.1）

> 本文件是**独立判定执行者**对判据 V1.2.1 下 S1–S5 与 §9.3 七行的判定记录。
> **本次判定不修改任何被判对象**（见 §6 与 §5.13 的 git 证据）。

---

## 0. 执行者与独立性声明

| 项 | 值 |
|---|---|
| 执行者标识 | `independent_judgement_executor` |
| 会话标识 | `independent-judge-v121-002`（与既往会话 `independent-judge-s1s5-001` **不是同一会话**） |
| 判定日期 | 2026-09-13 |
| 被判判据 | `docs/architecture/GK-KE-语义级消费验证方案-V1.2.1.md`，实测 sha256 `6d9acdb853d7d480cc484164a1297acd554e8b23908c7ed2f8c989b2f5866345` |
| 被判观测（de facto） | `evidence/gk-ke-semantic-consumption/observations.json`（sha256 `af32e44b…f26d`）<br>`evidence/gk-ke-semantic-consumption/observations-v1.0.0-criteria.json`（sha256 `1d0f4792…b6a0`） |
| 旁证物 | `evidence/gk-ke-semantic-consumption/report.json`（sha256 `3b7f8c14…1262`，**过期产物**）、`evidence/gk-ke-capability-probe/report.json`、`evidence/gk-ke-counterfactual/report.json`、`evidence/gk-ke-chain-trace/trace.json` |

**与 GK-KE 建设的关系（可核查的独立性声明）**：

- 我**未**撰写/修改判据（V1.0.0 / V1.1.0 / V1.2.0 / V1.2.1 / V1.2.2 均非我所写）；
- 我**未**编写采集器 `scripts/gk_ke_semantic_consumption.py`、**未**编写链路检验 `scripts/gk_ke_chain_trace.py`、**未**编写映射合同与义务合同；
- 我**未**参与 KERT 侧任何实现；
- 本次会话我**只做了三类动作**：读文件、运行只读探针（真实调用 KERT 两个能力，落在确定性仿真适配器上，见 §5.9）、运行交付的审计脚本并把**目标文档指向 V1.2.1**（副本置于 `/tmp`，未改仓库文件，见 §5.10 / §5.11）；
- 我会话开始时工作区已有两处未提交改动（`.gitignore`、`docs/architecture/UNDERSTAND_ANYTHING_CODE_LEVEL_ASSESSMENT.md`），**都不是我产生的**（会话起始的 `git status` 快照已显示），我未触碰它们。

**本文件的下述论断均以"我实际运行的命令 + 观测字段值"为唯一依据**；凡属"读代码得出的假设"，我均在文中显式标注为假设且**不用于判定**。

---

## 1. 逐判据判定表（S1–S5）

> **总表**

| 判据 | judgement | 一句话依据 |
|---|---|---|
| `S1_CONFLICT_PROPAGATION` | **`INCONCLUSIVE`** | 指定观测中 S1 分支**无下游输出**（仅上游）；且上游 `conflicts[0].ruleId` 含 `xxx` ⇒ `placeholder(U)=True`（判据规定此情形判 INCONCLUSIVE 并归因上游） |
| `S2_EMPTY_MEANS_NONE` | **`INCONCLUSIVE`** | 判据要求 `stable(A)≠⊥ ∧ stable(B)≠⊥`；指定观测既无 A/B 配对（仅单次调用），S5 又已实测不可复现 ⇒ 该前置不成立 |
| `S3_NOT_RUN_NOT_NONE` | **`INCONCLUSIVE`** | (a) 的判定键 `coverageStatus` 在 5 份指定下游输出中**不存在**（无值可求值）；(b) 因 `stable=⊥` 必 INCONCLUSIVE |
| `S4_HYPOTHESIS_NOT_CLOSED` | **`INCONCLUSIVE`** | (a) 要求在**下游**输出中出现上游 `indicators[].name`：5 份输出命中 **0** 项；且该值**无合法输入通道**（下游输入合同不含、V1.2.1 §1.2 明列禁止、§6.3b 禁止注入） |
| `S5_REPRODUCIBLE` | **`FAIL`** | 同输入两次：排除 `generatedAt` 后仍不一致（`kycGaps` 1 vs 3）；且 `generatedAt` 为自由文本非 ISO-8601 |

**计数**：`PASS` **0** / `FAIL` **1** / `INCONCLUSIVE` **4** / `NOT_APPLICABLE` **0**

> **依 V1.2.1 §7**：`S1–S5` 未全部 `PASS` ⇒ **语义级消费未达成**；
> 且 4 条 `INCONCLUSIVE` 依规则**不得计入通过**。
> **本判定不得表述为**「§9.3 语义级消费达成」「部分通过、基本达成」（§7 禁止表述）。

---

### S1 冲突传递 · `S1_CONFLICT_PROPAGATION`

- **judgement：`INCONCLUSIVE`**（依判据 §3 S1 前置质量门 + 采集要求未满足；**归因上游**）

- **basis（引用观测字段与值）**：
  1. 观测条目键集合 = `['judgedBy','judgement','note','upstreamInput','upstreamRawOutput']`
     ⇒ **该分支没有下游输出**（机械核验 `'downstreamRawOutput' in entry == False`）。
     判据明文「**采集要求**：**必须真实调用下游**（V1.1.0 的 S1 因采集器从不调用下游而结构性不可判定）」——本次指定观测**重演了该形态**。
     判据要求的判定键 `kycGaps[].trigger` / `kycGaps[].verifyScript.factBasis` **在本分支无任何取值**。
  2. `upstreamRawOutput.result.conflicts[0].ruleId` = `"RUL-FRONT-001-xxx（逻辑矛盾/信号背离，具体子编号待映射）"`
     ⇒ 含 `xxx` ⇒ `placeholder(U) = True`。判据前置质量门：「若 `placeholder(U)` 为真 → 判 **`INCONCLUSIVE`** 并**归因上游**」。
  3. `upstreamRawOutput.result.conflicts[0]` 字段集 = `['involvedSources','issue','ruleId','suggestion']`
     ⇒ **无 `id`**（现行上游合同 `output-schema.md` 要求 `conflicts[].id` 唯一且稳定）。
  4. 条件其余项：`coverage(U)`：`indicators` 6 条，status = `pending,pending,missing,missing,missing,missing` ⇒ **`PARTIAL`**（条件成立）；
     但 envelope 为 `status:"ok"`（**非** `SUCCESS`），且上游 `result` 顶层键仅 8 个 = `['conflicts','customerId','dataGaps','generatedAt','indicators','schemaVersion','skillId','warnings']`，**无 `taskId`/`asOf`/`executionStatus`**。

- **counterExampleTried（可执行反例，命令见 §5.7）**：
  - **反例 A**：试图用同目录其余分支的下游输出**顶替** S1 缺失的下游观测——检索该 `ruleId` 是否出现在任何下游条目的 `trigger` / `verifyScript.factBasis` 中。
    **实际**：5 份下游输出命中 **0** 次 ⇒ 无法据此把 S1 抬为 PASS，INCONCLUSIVE 未被推翻。
  - **反例 B**：试图用**现网**真实上游输出替换指定观测（现网 `conflicts[].ruleId` = `RUL-FRONT-001-003` / `RUL-FRONT-001-005`，已是具体子编号，命令见 §5.9）。
    **实际**：现网确已满足 R5，但那是**新观测**；依 G-2 与 §预注册语义，不得以新观测替换指定观测作为本次判定依据 ⇒ 不采纳。
  - **反例 C**：试图证明"S1 至少可被判 FAIL"——若下游从未被调用，不存在"违反"，故 FAIL 不成立（判据本身也如此规定）。

- **缺什么证据才能判定（`INCONCLUSIVE` 的解除条件）**：一次满足下述全部条件的观测：
  ① 上游 `conflicts[].ruleId` 为**具体子编号**（非占位符）；② 该上游输出**经映射程序**生成下游输入（不得手写）；③ **真实调用下游**并落盘下游原始输出。

- **附加义务（依 §7「S1 归因上游时的附加义务」，不得只报"无法判定"）**——**上游缺陷项**：

  | 编号 | 缺陷 | 证据（观测字段值） | 现行合同要求 |
  |---|---|---|---|
  | **U-1** | `conflicts[].ruleId` 为占位符 | `"RUL-FRONT-001-xxx（…）"` | 「`ruleId` 必须为具体子编号（如 `RUL-FRONT-001-003`）。**禁止占位符**」 |
  | **U-2** | `conflicts[]` 缺 `id` | 字段集无 `id` | 「`conflicts[].id` **必须唯一且稳定**」 |
  | **U-3** | 上游顶层缺 `taskId`/`asOf`/`executionStatus` | 顶层键 8 个，三者皆无 | `output-schema.md` 顶层必备字段 |
  | **U-4** | 指标口径字段为自由文本占位 | `unit:"未提供（待核实）"`、`dataTimestamp:"未提供"` | 「`generatedAt`/`asOf` 必须为合法 ISO-8601（不得为自由文本占位）」 |

  > 说明（避免误读）：U-1~U-3 是**指定观测采集时刻**的上游状态。
  > 我在本会话实测**现网**上游已返回 `taskId=TASK-FR-20260913-SIM-C001`、`asOf=2026-09-13`、`executionStatus=PARTIAL`、`conflicts[].id=CFL-001/CFL-002`、`ruleId` 为具体子编号（§5.9）。
  > 即：**缺陷是"观测过期"还是"实现从未满足"，我无法从指定观测判定**；我只能确认**指定观测本身**不具备 S1 的可判定条件。

---

### S2 空结论的正确解读 · `S2_EMPTY_MEANS_NONE`

- **judgement：`INCONCLUSIVE`**

- **basis**：
  1. 判据 §3 S2 的**条件**：「成对 A / B 均已运行；**且 `stable(A) ≠ ⊥`、`stable(B) ≠ ⊥`**（组内不一致 → 本判据 `INCONCLUSIVE`）」。
  2. 指定观测中对应条目为 `S2_EMPTY_MEANS_NONE`：**仅一次调用**（键集合只有 `downstreamInput` + `downstreamRawOutput`），无 k≥3，**无 A/B 配对**（A 需 `coverage=FULL` 的上游，B 需 `coverage=NONE` 的上游；两场景**均无上游输出**）。
  3. 组内稳定性可直接由 S5 得到：**同一输入两次调用输出不一致**（`kycGaps` 1 条 vs 3 条，§1 S5）⇒ `stable = ⊥` ⇒ 依 §7「判据间依赖登记」，S2 的 (b) 必 `INCONCLUSIVE`。
  4. 另：`S2_EMPTY_MEANS_NONE.downstreamInput` 的键 = `['conflictCases','customerId','indicators','reconciliationStatus','ruleCoverage']`
     ⇒ 含 4 个**判据 §1.2 明确禁止使用**的键（`reconciliationStatus`/`conflictCases`/`ruleCoverage`/`indicators`），且**不含** `upstreamStatus`。
     ⇒ 该输入不是 V1.2.1 口径的下游输入，其输出不能用于对 V1.2.1 的 S2 求值。

- **counterExampleTried（命令见 §5.12）**：
  - **反例 1**：构造两个确定性下游（**合规**：无触发源时 `kycGaps: []`、仅以 `coverageStatus` 区分；**违约**：`NOT_RUN` 时凭空造缺口且仍标 `SUCCESS`），按判据原文求值。
    **期望**：合规者 PASS、违约者 FAIL。**实际**：**合规者 `S2=FAIL`、违约者 `S2=PASS`** ⇒ **方向与合同要求相反**。
  - **反例 3**：证明 `S2(a)` **恒真**——对一份与上游完全无关的荒谬输出 `{"kycGaps":[{"trigger":"RUL-FRONT-999-999"}]}`，`S2(a)` 仍为 `True`（A 场景 `conflicts=[]` ⇒ 否定式无从被违反）。**期望**：荒谬输出应不通过。**实际**：通过 ⇒ (a) 零判别力。
  - 上述两反例**都不能**把 S2 抬为 PASS 或降为 FAIL：`stable=⊥` 由指定观测决定，故仍 `INCONCLUSIVE`。

- **缺什么证据才能判定**：一套 V1.2.1 口径的成对观测——A（`coverage=FULL, conflicts=[]`）与 B（`coverage=NONE, conflicts=[]`），**各 k≥3 次**，A/B 输入**仅差 `upstreamStatus`**（§2.1 ★★ / §6.3b），且所有字段落在 §1 白名单内。

---

### S3 未执行 ≠ 无冲突 · `S3_NOT_RUN_NOT_NONE`

- **judgement：`INCONCLUSIVE`**

- **basis**：
  1. **(a) 结构化路径**：判据要求 `downstream(B).coverageStatus == "NOT_RUN"` ∧ `downstream(A).coverageStatus == "SUCCESS"`。
     机械核验 5 份指定下游输出的顶层键均为 `['customerId','generatedAt','kycGaps','schemaVersion','skillId','warnings']`
     ⇒ **无 `coverageStatus` 键，无值可求值**。
     依纪律「**禁止把"未执行"当成"没有"**」，我**不**把"该轮未采集该字段"读成"下游没有该字段"；
     旁证：`evidence/gk-ke-capability-probe/report.json` 中 `SIM-CAP-KYC-GAP` 的 `resultKeys` 已含 `coverageStatus`、`coverageStatusReason`；KERT 现行 `output-schema.md` 亦要求该字段必填。
  2. **(b) 对比路径**：前置①（组内稳定）不成立——S5 已实测同输入两次不一致 ⇒ 依 §7 依赖登记必 `INCONCLUSIVE`。
  3. 前置②（A/B 输入仅差 `upstreamStatus`，须机械校验）**不成立**：
     `S2_EMPTY_MEANS_NONE.downstreamInput` 与 `S3_NOT_RUN_NOT_NONE.downstreamInput` 的差异字段集合 = **`['reconciliationStatus','ruleCoverage']`**（2 项），而 §2.1 ★★ 与 §6.3b 允许的差异集合 = **`['upstreamStatus']`**（1 项）
     ⇒ 依 §6.3b 原文「否则该轮采集判**无效**」。且两输入中**都没有** `upstreamStatus`。
  4. 判据明文「**明确禁止**：以 `warnings[]` 出现"覆盖不足""待核实"等措辞作为通过依据（**已实测证伪**）」——我遵守该禁令，未采信 `warnings` 文本。

- **counterExampleTried（命令见 §5.9 / §5.12）**：
  - **反例 8（A/B 真实探针，k=3，输入仅差 `upstreamStatus`，明确标注为"本次探针"而非指定观测）**：
    **期望**：`coverageStatus` 随 `upstreamStatus` 变化（`SUCCESS`→`SUCCESS`，`NOT_RUN`→`NOT_RUN`），从而 S3(a) 可通过。
    **实际**：`A#0-2` 与 `B#0-2` 的 `coverageStatus` **恒为 `"INSUFFICIENT"`**，且该值**不在**合同受控枚举 `SUCCESS|PARTIAL|NOT_RUN|FAILED` 内 ⇒ 在该（离线仿真）执行路径下 **S3(a) 结构性不可满足**。
    **该探针的效力限制（必须随结论声明）**：本会话无 LLM 端点，`SkillExecutionService` 经 `llm.py:201 → sim_bank_front.simulate` 返回**确定性仿真内容**（`simulationOnly: true`），**不是**被判定能力在真实模型下的行为。故我**不**以此探针改写 S3 的判定，只作为"结构化路径可驱动性"的反例记录。
  - **反例 1b**：在"下游尚无 `coverageStatus`"的世界里（= 指定观测所处的世界），按 V1.2.1 原文求值：
    **合规**下游（无触发源→`kycGaps: []`）→ `S3 = FAIL`；**违约**下游（`NOT_RUN` 时凭空造 1 条缺口）→ `S3 = PASS(b)`。
    **期望**：合规者通过、违约者不通过。**实际**：**方向相反**。
  - **反例 4（构造有效性机械校验）**：见 S2 basis 第 3 点 ⇒ 该轮采集依 §6.3b 判**无效**。

- **缺什么证据才能判定**：一条含 `coverageStatus` 的 V1.2.1 口径 A/B 观测（A/B 各 k≥3、输入仅差 `upstreamStatus`、字段全在白名单内）。

---

### S4 假设不得关闭缺口 · `S4_HYPOTHESIS_NOT_CLOSED`

- **judgement：`INCONCLUSIVE`**

- **basis**：
  1. **条件成立**：上游 `indicators` 含 `status ∈ {pending, missing}` 的指标 6 条（`pending`×2、`missing`×4），且 `dataGaps` 6 条。
  2. **判据 (a) 在指定观测中为假**：机械核验 5 份下游输出的 `kycGaps[].description` 与 `kycGaps[].verifyScript.factBasis` 中，上游 `indicators[].name`（如 `近半年营收`、`现有授信使用率`…）命中数 = **0**。
  3. **(a) 无法在不注入答案的前提下被驱动**（这是本判据的**前提缺失**，我据实登记而非据此判 FAIL）：
     - 下游**输入**合同的合法键 = `customerId` / `upstreamStatus` / `conflicts[]` / `optional{customerName, industrySignals, kycMissingFields}`（`input-schema.md`）；
     - V1.2.1 §1.2 把 `indicators` 列入「**不存在**（禁止使用）」；
     - V1.2.1 §2.1 ★★ / §6.3b 禁止把"上游缺了哪些指标"预先写入下游输入；
     ⇒ 指标名**只能**由采集器注入输入（被 §6.3b 禁止）或由下游凭空写出（不可保证）。
  4. **另一读法的登记（透明声明）**：若把 S4 严格按其字面"存在性检查"读（不看通道），指定观测下 (a) 为假 ⇒ 结论将是 `FAIL`。
     我判 `INCONCLUSIVE` 的理由是：该"假"的成因是**通道缺失 / 构造违规**（判据自身未登记该前提），而非下游在**可送达条件**下的违约。
     **该分歧本身即一项判据缺陷**：V1.2.1 声称 S4「**可执行**（不受非确定性影响——存在性检查）」，但未登记"指标名必须有合法通道进入下游"这一必要条件。

- **counterExampleTried（命令见 §5.8 / §5.12）**：
  - **反例 9**：检索上游 6 个指标名是否出现在任何下游输出中 → **期望**"若下游消费上游指标则应至少出现 1 次"，**实际 0 次**。
  - **反例 6（通道枚举）**：机械列出下游输入合同的合法键，逐一检查能否承载 `indicators[].name` → **期望**存在至少一条合法通道，**实际**无（唯一近似者为 `optional.industrySignals` / `optional.kycMissingFields`，语义均非"指标名"，且注入即触犯 §6.3b）。
  - **旁证（不用于判定）**：交付的 `UpstreamFieldMapping.json` 把 `result.signals ← indicators`、`result.comparedMetricRefs ← indicators` 写进下游输入容器 `result`；该容器键**不在**下游输入合同内（§5.6 实测映射后输入字段含 `result`），其是否被能力读取**我未能判定**（离线路径不读取）。

- **缺什么证据才能判定**：一条"指标名经**合法且不构成答案注入**的通道送达下游，且下游据此产出缺口条目"的观测。**据我所见，该通道在现行合同中不存在** ⇒ 在测量面改变前，S4 很可能**恒不可满足**（这属发现，不是我的判定）。

---

### S5 可复现 · `S5_REPRODUCIBLE`

- **judgement：`FAIL`**

- **basis（引用观测字段与值）**：
  1. `S5_REPRODUCIBLE` 的 `downstreamInput` 唯一，`rawOutputRunA` 与 `rawOutputRunB` 使用**同一输入**（同一 JSON 文件内，`downstreamInput` 只出现一次）。
  2. **(a) 不满足**：排除允许字段 `generatedAt` 后规范化比较 ⇒ **不一致**。
     具体差异：`runA.kycGaps` **1** 条（`priorityCategory = ['合规风险']`）；`runB.kycGaps` **3** 条（`priorityCategory = ['资金安全','合规风险','合规风险']`）；`description`/`trigger`/`verifyScript`/`actionPlan` 文本均不同。
  3. **(b) 不满足**：`generatedAt` 分别为 `"待核实（生成时间戳由系统注入）"`、`"待核实（输入未提供生成时间戳）"` ⇒ **均非合法 ISO-8601**。
  4. **(c) 满足**：`skillId="SK-FRONT-006"`、`customerId="SIM-C001"`、`schemaVersion="1.0"` 两次一致。
  5. k 的说明：判据要求 **k ≥ 3**，指定观测仅 **k = 2**。但两次输出**已经不一致** ⇒ 对任何 k≥3 的调用集合都不可能"完全一致"（逻辑蕴含）⇒ **k 不足不改变结论**。
  6. 交叉核对第二份观测（`observations-v1.0.0-criteria.json`）：A/B 缺口**条数相同**（1/1），但排除 `generatedAt` 后仍不一致（`priorityCategory` `['合规风险']` vs `['资金安全']`）⇒ 两次采集**都**不可复现。

- **counterExampleTried（命令见 §5.5 / §5.8）**：
  - **反例 7**：试图把差异**全部归因于允许字段** `generatedAt`（若能成立则应改判 PASS）→ **期望**剔除后一致，**实际**剔除后仍不一致 ⇒ 无法推翻。
  - **反例 7b（宽松读法否证）**：试图采用"缺口条数相同即视为可复现"的宽松口径 → **期望**第二份观测判 PASS，**实际**其 `priorityCategory` 仍不同 ⇒ 宽松口径亦被否证。
  - **反例 7c**：试图以"LLM 随机性属环境因素"为由不予判定 → 判据 §3 S5 原文已定性「**S5 是确定性硬门槛。对 LLM 下游要求逐字可复现；不可复现即未达成**」⇒ 该说情路径不成立。

- **缺什么证据才能判定**：无（本条已成判；若要改变，须由**判据新版**定义受控波动口径，且依 G-2 不得回溯适用）。

---

## 2. §9.3 七行消费表逐行判定

> 七行原文见 `docs/architecture/GITS-KERT_…建议书_V2.0.md:490-498`。
> 登记状态由 `UpstreamFieldMapping.json`（mapping `contractField` 13 项、`unmappedContractFields` = 空）与 `ConsumerObligations.json`（7 条义务的 `upstreamFields`）机械核对得出（命令 §5.6）。

| §9.3 行 | 上游字段（§9.3 原文名） | 映射合同登记状态 | 负责判据 | **该行判定** | 依据（观测/合同字段） |
|---|---|---|---|---|---|
| **行 1** | `taskId` / `entityId` / `asOf` | 三者均登记为 **mapped**（`entityId ← customerId`） | S6'（仅 `customerId` 子集；S6' **不在** S1–S5 内） | **无法判定** | 指定观测上游 `result` 顶层键仅 8 个，**无 `taskId` / `asOf`**；`entityId` 仅能由 `customerId`（值 `SIM-C001`）异名映射；**无任何"三元组一致性校验（MATCH/MISMATCH）"的下游观测** |
| **行 2** | `evaluationStatus` | **既未登记为 mapped，也未登记为 unmapped（登记缺失）** | S3 | **无法判定** | 机械核对：`evaluationStatus` 不在 `mappings[].contractField`（合同改用 `status`），也不在 `unmappedContractFields`；**依委托要求，"来源登记为未映射（含未登记）的行必须判未达成或无法判定"** |
| **行 3** | `evaluatedRuleIds` | **登记缺失**（合同改用 `ruleTrace.{expectedRules,coveredRules,missingRules}`） | S2（V1.0 预注册矩阵）／S3（V1.2.1 §3 注释自称"承接行 3"）——**归属冲突** | **无法判定** | 同上登记缺失；且**两处登记互相矛盾**（见本表下方注），无单一判据可依 |
| **行 4** | `conflictCases` / `signals` | 登记为 **mapped**（`← conflicts` / `← indicators`） | S1 | **无法判定** | S1 = `INCONCLUSIVE`（上游 `ruleId` 占位符 + 该分支无下游调用）。另：指定观测下游输入使用**合同外名** `conflictCases`（含自造 `conflictId=XC-1`），非合同字段 |
| **行 5** | `comparedMetricRefs` | 登记为 **mapped**（`result.comparedMetricRefs ← indicators`） | **无判据覆盖**（V1.2.1 §4 自述"仅 S7' 覆盖上游侧；下游侧**无请求通道**"） | **无法判定** | 指定观测上游无 `comparedMetricRef` 形态内容（`indicators` 无 `metricId/version/grain` 三元组）；下游侧无通路 |
| **行 6** | `evidenceRefs` / `explanations` | 登记为 **mapped**（`evidenceRefs` 同名；`result.explanations ← explanations`） | S4 | **无法判定** | S4 = `INCONCLUSIVE`。**旁证（不构成判据级证据）**：S4 分支下游输出确有 `KG-001`/`KG-002` 指向"可能享受税收优惠"这一无证据假设、且 `verifyScript.question` 与 `actionPlan.path` 均非空；但该分支输入为**手写**（含合同外 `explanations` 键），非映射程序产物，依 §2.1 留痕要求不构成"真正的上游→下游链" |
| **行 7** | `requiredQuestions` | 登记为 **mapped**（`result.requiredQuestions ← requiredQuestions`） | S8'（(a) 可机器校验 / (b) **须人工**） | **无法判定** | V1.2.1 §4 明示该字段"未交付，改用 `conflicts[].suggestion`"；S8'(b) 属**人工语义比对**、依纪律**不计入机器可校验**；且 §7 规定 S6'–S8' **不影响** S1–S5 结论、**不得**因其可执行而默认通过 |

**逐行判定的三点补充**：

1. **行 2 / 行 3 属"来源登记缺失"**：委托要求「若某行的上游来源在映射合同中登记为"未映射"，该行必须判未达成或无法判定」。此处更弱——**连登记都没有**（既不在 `mappings` 也不在 `unmappedContractFields`），而我实测 `unmappedContractFields` = `[]` 且合同自述 `verdict = "FULL"`、`mappedFields = 13`（= 声明字段数 13）。**"FULL" 未覆盖 §9.3 的行 2/行 3 字段名**。
2. **行 3 的判据归属存在登记冲突**：`_preregistration.json.coverageMatrix.rows` 记 `"evaluatedRuleIds": "S2"`；而 V1.2.1 §3 S3 开头写「承接 §9.3 行 3 的正向要求（"必需规则缺失则返回覆盖不足"）」，`§4` 又说「行 3 … 正向要求无判据负责」。三处口径不一致 ⇒ 该行的判定主体不明。
3. **§7 范围限制（须随结论声明）**：V1.2.1 **仅覆盖**行 2/3/4/6；行 1/5/7 **无完整判据覆盖** ⇒ 即使将来 S1–S5 全部 PASS，也**不得**表述为「§9.3 达成」。

---

## 3. 反例清单（命令 + 期望 + 实际）

> 全部反例均可直接复制运行（脚本路径见 §5）。**没有一条是为"证明对"而构造的**；凡未能推翻原结论者亦如实列出。

| # | 反例 | 期望 | 实际 | 结论 |
|---|---|---|---|---|
| **1** | 构造两个确定性下游（**合规**：无触发源→`kycGaps: []`，仅以 `coverageStatus` 区分；**违约**：`NOT_RUN` 时凭空造缺口且仍标 `SUCCESS`），按 V1.2.1 原文对 S2 求值（§5.12） | 合规者 PASS、违约者 FAIL | **合规者 `S2=FAIL`；违约者 `S2=PASS`** | **设计级缺陷：判据方向与合同要求相反**（合同明文禁止"无触发源强行制造缺口"与"上游未执行仍标 SUCCESS"） |
| **1b** | 同两下游，但均**不输出** `coverageStatus`（= 指定观测所处世界），对 S3(b) 求值（§5.12） | 合规者 PASS、违约者 FAIL | **合规者 `S3=FAIL`；违约者 `S3=PASS(b)`** | 同上，S3(b) 同向反转 |
| **2** | **纯回显下游**（`coverageStatus := upstreamStatus`；`trigger := conflicts[i].ruleId`；`description := conflicts[i].issue`；零内容消费），对 S1 与 S3(a) 求值（§5.12） | 零内容消费者**不应**通过 | **`S1=True`、`S3a=True`** | S1 与 S3(a) 均可被"回显"满足；S1 的"结构性引用"要求**不能**证明消费 |
| **3** | 对一份与上游完全无关的荒谬输出求值 `S2(a)`（§5.12） | 应不通过 | **`S2(a)=True`** | **S2(a) 恒真**（A 场景 `conflicts=[]` ⇒ 否定式无从被违反），零判别力 |
| **4** | 机械校验 S2/S3 两份输入的差异字段集合（§6.3b 要求恰为 `{"upstreamStatus"}`）（§5.12 / §5.3） | 差异集合 = `['upstreamStatus']` | **差异集合 = `['reconciliationStatus','ruleCoverage']`** | 依 §6.3b 原文，**该轮采集判无效** |
| **5** | 把映射合同的校验规则（`verify_field_mapping`）施加到**指定观测的上游输出**上（§5.8） | `errs = []`（合同自述 `FULL`） | **`errs` = 9 条**：`taskId`/`asOf`/`executionStatus`/`ruleTrace`(×3)/`explanations`/`requiredQuestions`/`evidenceRefs` 均"上游真实返回中不存在" | 指定观测**早于**映射合同所声明的字段；同一合同对现网上游校验通过（§5.6），对指定观测上游校验失败 |
| **6** | 枚举下游输入合同的合法键，检查能否承载 `indicators[].name`（§5.12 / §5.7） | 存在至少一条合法通道 | **无合法通道** | S4(a) 只能靠**注入答案**（触犯 §6.3b）或下游凭空写出 |
| **7** | 把 S5 的差异归因于允许字段 `generatedAt`（§5.5） | 剔除后一致（即推翻 FAIL） | **剔除后仍不一致** | 无法推翻 S5=FAIL |
| **7b** | 采用"缺口条数相同即视为可复现"的宽松口径，套用第二份观测（`A=1/B=1`）（§5.8） | 判为可复现 | **仍不一致**（`priorityCategory` `['合规风险']` vs `['资金安全']`） | 宽松口径亦被否证 |
| **8** | 真实 A/B 探针（k=3，输入**仅差** `upstreamStatus`）：检查 `coverageStatus` 是否随 `upstreamStatus` 变化（§5.9） | `SUCCESS→"SUCCESS"`、`NOT_RUN→"NOT_RUN"` | **A/B 共 6 次调用 `coverageStatus` 恒为 `"INSUFFICIENT"`**（**不在**合同受控枚举内），`stable(A)=stable(B)=True` | 该（离线仿真）路径下 **S3(a) 结构性不可满足**；且该路径输出**违反合同枚举**（效力限制见 §1 S3） |
| **9** | 检索上游 6 个 `indicators[].name` 是否出现在 5 份下游输出中（§5.7） | 若下游消费上游指标，应 ≥1 次 | **0 次** | 与反例 6 共同支持"S4(a) 无通路" |
| **10** | 用交付的**行号审计脚本**核对 V1.2.1 的每条出处行号（§5.11） | 全部正确（`exit=0`） | **62 条引用中 5 条错位**（`verifyScript.factBasis` 标 :19 实为 :22；`question` 标 :20 实为 :23；`actionPlan.verifyGoal` 标 :24 实为 :27；`indicators[].dataTimestamp` 标 :16 实为 :20；§4 的 `question` 同前），**`exit=1`** | V1.2.1 **未通过**其 §6.2 第 1 项的机械防线 |
| **11** | 用交付的**键审计脚本**核对 V1.2.1 的判定键（§5.10） | 全部存在于真实合同 | **55 个判定键全部存在（PASS，1 条 WARN）** | 此项对 V1.2.1 有利，据实记录（**但该目标默认指向 V1.2.2**，见 §4） |

**两条反例效力限制（必须随清单声明）**：

- 反例 8 涉及真实调用，但本会话**无 LLM 端点**，调用落在 `llm.py:201 → sim_bank_front.simulate`（`simulationOnly: true`）的**确定性仿真**路径上 ⇒ 它证明的是"该执行路径"的行为，**不能**代表被判定能力在真实模型下的行为。我**未**把它作为任何判据的判定依据。
- 反例 1/1b/2/3 求值的是**判据文本**（我按其原文实现谓词），不是产品的运行结果 ⇒ 它们指向的是**判据的设计缺陷**，不是产品缺陷。

---

## 4. 未能判定的部分与原因

### 4.1 逐条列明（**"没查清"即明说**）

| # | 未能判定的事 | 原因 |
|---|---|---|
| 1 | **S1** 是否成立 | 指定观测该分支**无下游输出**（采集器"从不调用下游"形态复发）；且上游 `ruleId` 为占位符 ⇒ 依判据只能 `INCONCLUSIVE` |
| 2 | **S2** 是否成立 | 无 A/B 配对、k<3、`stable=⊥`；且 `S2(a)` 恒真无判别力 |
| 3 | **S3** 是否成立 | (a) 判定键 `coverageStatus` 在指定观测中**无取值**；(b) 前置不成立 |
| 4 | **S4** 是否成立 | (a) 在指定观测中为假，但成因是"通道缺失/构造违规"而非可送达条件下的违约；判据未登记该前提 |
| 5 | **§9.3 行 1/2/3/4/5/6/7 是否达成** | 行 2/3 **登记缺失**；行 1/4/5/6/7 或对应判据 `INCONCLUSIVE`，或**无判据覆盖**（行 5），或判定键属**人工语义比对**（行 7(b)） |
| 6 | **被判定能力的真实（LLM 路径）行为** | 本会话无 LLM 端点，真实调用落在确定性仿真适配器上；我不做"用适配器探针冒充能力实验"的替换（该替换在本系列已被明确判为错误） |
| 7 | **S3(a) 在真实 LLM 路径下是否可满足** | 同上；我只能报告：离线路径**不可满足**（`INSUFFICIENT`，枚举外），LLM 路径**未测** |
| 8 | **`conflicts[].ruleId` 占位符是"实现从未满足"还是"观测过期"** | 指定观测（2026-09-12 17:47）无该信息；现网已满足（§5.9），但我不能据新观测反推旧观测时刻的实现 |
| 9 | **上游实现与合同的差异责任归属**（GK-KE 侧 / KERT 侧） | 不在我的判定范围，且需版本/提交绑定才能归因 |

### 4.2 我阅读到但**未**用于判定的材料（避免"以存在性代替证据"）

- `V1.2.2`（`docs/architecture/GK-KE-语义级消费验证方案-V1.2.2.md`，sha256 未核对）：它**删除**了 S2(b) 与 S3(b)、并自述"判据惩罚合规下游"。**我未对其作判定**——委托指定的判据版本是 V1.2.1；且依 V1.2.1 §8/G-2，版本判据不得回溯。**但必须报告：指定版本 V1.2.1 已被仓库内后续草案取代，两版对 S2/S3 的规定不同**（我的判定依 V1.2.1 作出）。
- `evidence/gk-ke-semantic-consumption/report.json`：该文件把 `S5_REPRODUCIBLE` 记为 `passed:true`，但其 `_archivalNote` 自述为"**过期产物 · 勿直接引用**"（V1.0.0 判据 + `DeterministicLlmAdapter（占位内容）`）。**我未采信**该文件的 `passedCriteria`，也未修改它。
- `docs/architecture/GK-KE-第三四次独立复核记录与测量面决策简报-V1.0.md`、`GK-KE-确定性实验协议与阻塞登记-V1.0.md`：**作为背景阅读，不作为判定依据**（判定只依据观测字段值与我运行的结果）。
- `ConsumerObligations.json` 的 `currentStatus.honestStatement`（`runtimeTraceExists: false`）：作为旁证，不替代观测。

### 4.3 交付物层面的缺失（**判据文档提到但实际不存在的材料**）

- **`docs/architecture/GK-KE-语义级消费验证方案-V1.2.1.md` 中不存在任何 §观测 一节**：全文检索「观测」**零命中**（§5.1），三版 V1.2/V1.2.1/V1.2.2 均**无**任何观测文件路径引用（§5.2）。
  ⇒ 委托清单中「观测文件①/② 见判据文档 §观测 一节所指路径」**指向悬空**。
  我据此采用**de facto 观测**（`observations.json`、`observations-v1.0.0-criteria.json`），并明示该替代关系。
- **V1.2.1 未被预注册**：仓库内登记文件仅覆盖 V1.0.0（`d1e6192b…`）与 V1.1.0（`5bf59fc9…`）；V1.2.0 为 `DRAFT_NOT_YET_PREREGISTERED`；**V1.2.1 的哈希 `6d9acdb8…` 在全库零命中**（§5.4）。
  ⇒ V1.2.1 文件头自称「**性质：预注册。** 判定标准先于执行锁定」，与 §9 待办 5「预注册（锁定哈希）— 待办」及仓库实际登记**不一致**；我无法验证"先于执行锁定"。
- **交付的两个审计脚本默认指向 V1.2.2，不指向 V1.2.1**（`gk_ke_criteria_key_audit.py:36`、`gk_ke_criteria_line_audit.py:34` 均为 `方案-V1.2.2.md`），二者均已接入 `make verify`（`Makefile:94`）。
  ⇒ V1.2.1 §6.1 声称「登记须经 `make criteria-key-audit` 机械核对」，**实际保护的文档不是 V1.2.1**。

---

## 5. 我实际运行过的全部命令（原始）

> 以下命令均可直接复制运行（工作目录 `/home/szf/dev/gits-cbanking`；解释器为仓库 `.venv`，Python 3.12.8）。
> 我**未**运行 `gk_ke_semantic_consumption.py --collect`（会写观测文件），**未**运行会写仓库内证据的脚本（链路检验的写盘位置被我重定向到 `/tmp`）。

**5.1 判据文档是否有 §观测**
```bash
grep -n "观测" docs/architecture/GK-KE-语义级消费验证方案-V1.2.1.md || echo "[NO MATCH] V1.2.1 全文无『观测』二字"
```

**5.2 三版判据是否指向观测路径**
```bash
for f in docs/architecture/GK-KE-语义级消费验证方案-V1.2.md \
         docs/architecture/GK-KE-语义级消费验证方案-V1.2.1.md \
         docs/architecture/GK-KE-语义级消费验证方案-V1.2.2.md; do
  echo "--- $f"; grep -n "观测文件\|§观测\|observations\|evidence/" "$f" || echo "   [无任何观测路径引用]"
done
```

**5.3 哈希基线**
```bash
sha256sum docs/architecture/GK-KE-语义级消费验证方案-V1.2.1.md \
          evidence/gk-ke-semantic-consumption/*.json \
          evidence/gk-ke-semantic-consumption/*.md
```

**5.4 预注册登记**
```bash
cat specs/knowledge-architecture/contracts/_preregistration.json
cat specs/knowledge-architecture/contracts/_preregistration-v1.2.0-draft.json
grep -rn "6d9acdb8" --include=* .            # V1.2.1 的哈希是否被登记 → 零命中
```

**5.5 观测文件结构机械核对（P1–P8 探针）**
```bash
.venv/bin/python - <<'PY'
import json, re
from pathlib import Path
obs = json.loads(Path('evidence/gk-ke-semantic-consumption/observations.json').read_text(encoding='utf-8'))
c = obs['criteria']
for k, v in c.items():
    print(k, sorted(v.keys()))
s1 = c['S1_CONFLICT_PROPAGATION']; up = s1['upstreamRawOutput']['result']
print('上游顶层键 =', sorted(up.keys()), '| S1 有下游输出?', 'downstreamRawOutput' in s1)
print('ruleId =', [x.get('ruleId') for x in up['conflicts']])
print('indicator status =', [(i['name'], i['status']) for i in up['indicators']])
s5 = c['S5_REPRODUCIBLE']
a = dict(s5['rawOutputRunA']['result']); b = dict(s5['rawOutputRunB']['result'])
for d in (a, b): d.pop('generatedAt', None)
print('S5 排除 generatedAt 后一致?', json.dumps(a,sort_keys=True,ensure_ascii=False)==json.dumps(b,sort_keys=True,ensure_ascii=False))
print('S5 runA/runB gaps =', len(s5['rawOutputRunA']['result']['kycGaps']), len(s5['rawOutputRunB']['result']['kycGaps']))
ISO = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}')
for k, v in c.items():
    for nm in ('downstreamRawOutput','rawOutputRunA','rawOutputRunB'):
        r = (v.get(nm) or {}).get('result')
        if r: print(k, nm, 'coverageStatus=', r.get('coverageStatus'), '| generatedAt ISO?', bool(r.get('generatedAt') and ISO.match(str(r['generatedAt']))))
i2 = c['S2_EMPTY_MEANS_NONE']['downstreamInput']; i3 = c['S3_NOT_RUN_NOT_NONE']['downstreamInput']
print('S2/S3 输入差异字段 =', [f for f in set(i2)|set(i3) if i2.get(f)!=i3.get(f)])
names = [i['name'] for i in up['indicators']]
for k, v in c.items():
    for nm in ('downstreamRawOutput','rawOutputRunA','rawOutputRunB'):
        r = (v.get(nm) or {}).get('result')
        if not r: continue
        t = ' | '.join([str(g.get('description','')) + str((g.get('verifyScript') or {}).get('factBasis','')) for g in (r.get('kycGaps') or [])])
        print(k, nm, '命中指标名 =', [n for n in names if n in t])
PY
```

**5.6 合同与映射登记机械核对**
```bash
.venv/bin/python - <<'PY'
import json
fm = json.load(open('specs/knowledge-architecture/contracts/UpstreamFieldMapping.json', encoding='utf-8'))
ob = json.load(open('specs/knowledge-architecture/contracts/ConsumerObligations.json', encoding='utf-8'))
mapped = {m["contractField"] for m in fm["mappings"]}
print('mapped =', sorted(mapped)); print('unmapped =', fm.get("unmappedContractFields"))
print('verdict =', fm["currentStatus"]["verdict"], '| mappedFields =', fm["currentStatus"]["mappedFields"])
for f in ['taskId','entityId','asOf','evaluationStatus','evaluatedRuleIds','conflictCases','signals','comparedMetricRefs','evidenceRefs','explanations','requiredQuestions']:
    print(f, '| mapped?', f in mapped or any(m.split('.')[-1]==f for m in mapped))
PY
```

**5.7 交付的链路检验（把写盘位置重定向到 /tmp，不改动仓库内证据）**
```bash
.venv/bin/python - <<'PY'
import importlib.util, pathlib, json
spec = importlib.util.spec_from_file_location("ct", "scripts/gk_ke_chain_trace.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.OUT = pathlib.Path("/tmp/gk-ke-chain-trace-judge")   # 重定向，避免改动 evidence/
try:
    rc = m.main()
except Exception as e:
    rc = f"main() 末尾打印报错（写盘已完成）: {type(e).__name__}"
print("exit =", rc)
t = json.loads(pathlib.Path("/tmp/gk-ke-chain-trace-judge/trace.json").read_text(encoding='utf-8'))
print(t["verdict"], "| inputProven:", t["inputConsumptionProven"], "| outputProven:", t["outputConsumptionProven"])
print("上游键:", t["steps"][0]["returnedTopLevelKeys"])
print("映射后下游输入字段:", t["steps"][1]["downstreamInputFields"])
print("下游键:", t["steps"][2]["returnedTopLevelKeys"])
print(t["chainCounterfactuals"])
PY
```

**5.8 映射规则施加于指定观测的上游输出 + 第二份观测的 S5 交叉核对**
```bash
.venv/bin/python - <<'PY'
import importlib.util, json
s = importlib.util.spec_from_file_location("ct", "scripts/gk_ke_chain_trace.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
obs = json.loads(open('evidence/gk-ke-semantic-consumption/observations.json', encoding='utf-8').read())
res = obs['criteria']['S1_CONFLICT_PROPAGATION']['upstreamRawOutput']['result']
fm = m.load_field_mapping(); ob = json.loads(m.OBLIGATIONS.read_text(encoding='utf-8'))
chain = next(c for c in ob['consumptionChains'] if c['upstream'] == 'SIM-CAP-FACT-RECON')
errs = m.verify_field_mapping(fm, ob, chain, res)
print('errs =', len(errs)); [print(' -', e) for e in errs]
o0 = json.loads(open('evidence/gk-ke-semantic-consumption/observations-v1.0.0-criteria.json', encoding='utf-8').read())
s5 = o0['criteria']['S5_REPRODUCIBLE']; A = s5['rawOutputRunA']['result']; B = s5['rawOutputRunB']['result']
na = json.dumps({k:v for k,v in A.items() if k!='generatedAt'}, sort_keys=True, ensure_ascii=False)
nb = json.dumps({k:v for k,v in B.items() if k!='generatedAt'}, sort_keys=True, ensure_ascii=False)
print('第二份观测 S5 一致?', na==nb, [g.get('priorityCategory') for g in A['kycGaps']], [g.get('priorityCategory') for g in B['kycGaps']])
PY
```

**5.9 真实调用探针（A/B，k=3；离线仿真路径）**
```bash
.venv/bin/python - <<'PY'
import importlib.util, json
spec = importlib.util.spec_from_file_location("ct", "scripts/gk_ke_chain_trace.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
svc = m.load_service()
base = {"customerId": "SIM-C001",
        "conflicts": [{"id": "CFL-001", "issue": "营收上升而实缴税款下降", "ruleId": "RUL-FRONT-001-003"}]}
A = dict(base, upstreamStatus="SUCCESS"); B = dict(base, upstreamStatus="NOT_RUN")
for label, inp in (("A", A), ("B", B)):
    outs = []
    for i in range(3):
        r = m.call(svc, m.DOWNSTREAM, f"JUDGE-{label}-{i}", inp); res = r["result"] or {}
        outs.append(res); print(label, i, "coverageStatus=", res.get("coverageStatus"), "gaps=", len(res.get("kycGaps") or []))
    norm = {json.dumps({k:v for k,v in o.items() if k!='generatedAt'}, sort_keys=True, ensure_ascii=False) for o in outs}
    print("stable(", label, ") =", len(norm)==1)
up = m.call(svc, m.UPSTREAM, "JUDGE-UP2", {"customerId": "SIM-C001"})["result"]
print("上游 taskId/asOf/executionStatus =", up.get("taskId"), up.get("asOf"), up.get("executionStatus"))
print("上游 conflicts ruleId =", [c["ruleId"] for c in up["conflicts"]])
PY
```

**5.10 / 5.11 把交付的审计脚本原样指向 V1.2.1（不改仓库文件）**
```bash
.venv/bin/python - <<'PY'
import importlib.util, pathlib
def load(p, name):
    s = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
doc = pathlib.Path("/home/szf/dev/gits-cbanking/docs/architecture/GK-KE-语义级消费验证方案-V1.2.1.md")
ka = load("scripts/gk_ke_criteria_key_audit.py", "ka"); ka.CRITERIA_DOC = doc
print("== key audit ==", ka.main())
la = load("scripts/gk_ke_criteria_line_audit.py", "la"); la.DOC = doc
print("== line audit ==", la.main())
PY
```

**5.12 反例 1/1b/2/3/4/6（对判据文本求值）**
```bash
.venv/bin/python - <<'PY'
def S1(U, D):
    rids=[c["ruleId"] for c in U["conflicts"]]
    return any(any(r in str(d.get("trigger",""))+str((d.get("verifyScript") or {}).get("factBasis","")) for r in rids) for d in D["kycGaps"])
def S2a(A): return True
def S2b(A,B): return A["kycGaps"]!=B["kycGaps"]
def S2(A,B,st): return "INCONCLUSIVE" if not(st(A) and st(B)) else ("PASS" if S2a(A) and S2b(A,B) else "FAIL")
def S3a(A,B): return B.get("coverageStatus")=="NOT_RUN" and A.get("coverageStatus")=="SUCCESS"
def S3(A,B,st,clean): return "PASS(a)" if S3a(A,B) else ("INCONCLUSIVE(b)" if not(st(A) and st(B)) or not clean else ("PASS(b)" if S2b(A,B) else "FAIL(b)"))
compliant=lambda i:{"coverageStatus":{"SUCCESS":"SUCCESS","NOT_RUN":"NOT_RUN"}[i["upstreamStatus"]],"kycGaps":[]}
violator =lambda i:{"coverageStatus":"SUCCESS","kycGaps":[{"gapId":"KG-001"}]} if i["upstreamStatus"]=="NOT_RUN" else {"coverageStatus":"SUCCESS","kycGaps":[]}
echo=lambda i:{"coverageStatus":i["upstreamStatus"],"kycGaps":[{"trigger":c["ruleId"],"description":c["issue"]} for c in i["conflicts"]]}
A={"customerId":"SIM-C001","upstreamStatus":"SUCCESS","conflicts":[]};B={"customerId":"SIM-C001","upstreamStatus":"NOT_RUN","conflicts":[]}
for n,f in (("合规",compliant),("违约",violator)):
    a=[f(A) for _ in range(3)]; b=[f(B) for _ in range(3)]
    st=lambda X: a[0]==a[2] and b[0]==b[2]
    print(n,"S2=",S2(a[0],b[0],st),"S3=",S3(a[0],b[0],st,True))
usr={"conflicts":[{"ruleId":"RUL-FRONT-001-003","issue":"x"}]}
print("S1(回显)=",S1(usr,echo({"upstreamStatus":"PARTIAL","conflicts":usr["conflicts"]})),"S3a(回显)=",S3a(echo(A),echo(B)))
print("S2a(荒谬输出)=",S2a({"kycGaps":[{"trigger":"RUL-FRONT-999-999"}]}))
# 合规但无 coverageStatus 的世界
c2=lambda i:{"kycGaps":[]}; v2=lambda i:{"kycGaps":[{"gapId":"KG-001"}]} if i["upstreamStatus"]=="NOT_RUN" else {"kycGaps":[]}
for n,f in (("合规(无cs)",c2),("违约(无cs)",v2)):
    print(n,"S3=",S3(f(A),f(B),lambda X:True,True))
PY
```

**5.13 未改动被判对象的证据**
```bash
git status --short
git ls-files evidence/gk-ke-semantic-consumption/
git show 086bf43:evidence/gk-ke-semantic-consumption/observations.json | sha256sum
sha256sum evidence/gk-ke-semantic-consumption/observations.json
ls -la evidence/gk-ke-semantic-consumption/
```

**5.14 门禁当前显示（只读）**
```bash
.venv/bin/python scripts/gk_ke_semantic_consumption.py
# → gk-ke-semantic-consumption: NOT_MET / __GATE_VERDICT__=FAIL
#   判据哈希校验: 通过（5bf59fc99db9a058…）      ← 校验的是 V1.0.md（内容 V1.1.0）
#   真实 LLM: ❌ 未配置 KERT_LLM_BASE_URL/API_KEY/MODEL
#   已判定: 5 / 5；判定计数: {'INCONCLUSIVE': 1, 'PASS': 2, 'FAIL': 2}
```

---

## 6. 我未做的事（边界声明）

1. **未修改判据文档**：`GK-KE-语义级消费验证方案-V1.2.1.md`（及 V1.0/V1.1/V1.2/V1.2.2）一个字节未动；sha256 见 §5.3。
2. **未修改观测数据与 `report.json`**：`observations.json`、`observations-v1.0.0-criteria.json`、`report.json` 未写；`git status` 仅显示会话前既有的两处改动（`.gitignore`、`docs/architecture/UNDERSTAND_ANYTHING_CODE_LEVEL_ASSESSMENT.md`，均非我产生，我未触碰）。
3. **未修改被判定能力的实现**（GK-KE 侧与 KERT 侧均未写）。
4. **未运行采集器**：未执行 `gk_ke_semantic_consumption.py --collect`（会覆写观测文件）；也未执行 `--preregister`。
5. **未让交付的链路检验写进仓库**：其写盘位置被重定向到 `/tmp/gk-ke-chain-trace-judge`，因此 `evidence/gk-ke-chain-trace/trace.json` 未被改动。
6. **未重跑择优、未删除任何一次采集**：观测中不一致的结果（S5 A/B、两份观测之间的差异）全部如实计入。
7. **未使用 LLM**（本会话无端点）；因此**未**用适配器/仿真结果冒充"能力实验"。
8. **未以"我认为应该是"代替"观测显示"**：所有 `basis` 均为字段名 + 取值；凡属代码阅读所得的假设（如同一提供方、通道是否存在）均在文中标注为假设并**不用于判定**。
9. **未对 V1.2.2 作判定**（它只是被我报告为"指定版本已被后续草案取代"这一事实）。
10. **未给出"是否应当交付 / 是否 B 层达成"的总体结论** —— 那属委托方决定。本文件只提供证据与判定。
11. **未提交 git、未创建分支、未改动 `.codebuddy/`、未删除任何文件**。

---

### 附：本次判定与既往判定的关系（避免被误读为"翻案"）

既往判定（`INDEPENDENT-JUDGEMENT-S1-S5-V1.0.md`，session `independent-judge-s1s5-001`）依据的是**判据 V1.0/V1.1**，其 S2 不含 (b)、S3 是"合取含三值枚举 `reason`"的不同条文；
本次判定依据的是**判据 V1.2.1**（新增组内稳定性前置、新增 `upstreamStatus`/`coverageStatus` 键、S2 改为合取 (a)∧(b)）。
两者**不是同一判据**，结论不同属**预期结果**，依 V1.2.1 §8/G-2 **互不回溯**：本次判定**不**声称既往判定有误，也**不**以其推翻既往结论。
凡与既往判定同向的事实（例如"下游 `warnings` 写着覆盖不足而结论字段为空"的形态），本次以**结论字段**复核：`S3` 分支下游 `kycGaps` 为 `[]`、`warnings` 含"规则覆盖不足…覆盖状态待核实"——**我未采信 `warnings` 文本**（§1.2 禁令），该事实仅作旁证记录。
