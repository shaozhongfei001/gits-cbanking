# GK-KE OC-04 第三轮独立 QA 核验报告

> 核验者：独立 QA（第三轮，非本会话 TL）
> 核验日期：2026-09-13
> 核验对象：TL 对第二轮三项问题的处理 + 本轮五项新增（链 trace / 语义预注册 / 覆盖核对 / 命名登记 / 门禁语义分离）
> 实际核验 HEAD：`5f3a770`（派发锚点 `a17d13c` 之后 +2 提交：`46b4126` 语义预注册、`febb33f` 链 trace）
> KERT HEAD：`89fbbce`（与派发说明一致）
> 核验原则：每条回到源头复现；破坏性验证后一律恢复；不因"门禁全绿"即判通过。

---

## 一、五项新增的核验结论（§二）

| # | 新增 | TL 声称 | 判定 | 独立证据 |
|---|---|---|---|---|
| ① | 链路 runtime trace | 真实调用 KERT 两能力，输入级消费已证明 | **证实** | 读 `gk_ke_chain_trace.py`：第 128/137 行真实 `svc.execute()` 调用上下游两能力。**破坏性验证**：注入 KERT `execute()` 抛异常 → chain_trace **报错 FAIL**（上游调用失败 return 1）。真实调用成立。 |
| ② | 语义消费预注册 | 判据 S1–S5 已锁定，篡改即拒绝 | **证实** | `_preregistration.json` 的 `criteriaSha256=d1e6192b…` 与文档当前字节 `sha256sum` **完全一致**。**破坏性验证**：篡改判据文档一处 → 脚本 **FAIL 并引用 G-4**（拒绝执行）。锁真实有效。 |
| ③ | 合同覆盖核对 | 4 维核对 7/7、7/7、14/14、3/3 | **部分证实（D 维形式主义，见 §二 攻击点 §三.3）** | A/B/C 三维真实有效：**破坏性验证**加自造义务 OBL-99 → B 维正确报"无法追溯 §9.3"并 FAIL。**但 D 维有缺陷**（详见下方 §三.3）。 |
| ④ | 命名差异登记 | 5 处已登记 | **部分证实（登记存在，但校验脚本只认 3 处）** | `CapabilityResultEnvelope.json#namingDivergences.map` 确实登记了 **5 处**。但 `gk_ke_contract_coverage.py` 的 `KNOWN_RENAMES` 常量只硬编码 **3 处**，D 维只校验这 3 处。见 §三.3。 |
| ⑤ | 门禁语义分离 | integrity 失败才非零；readiness 仅报告 | **部分证实（有 INCONCLUSIVE 第三态漏洞）** | `run_gates.py` 第 114-120 行确实施行 integrity 失败才 return 1、readiness 仅打印。**但 `semantic-consumption` 的 INCONCLUSIVE 态未被处理**，见 §二 攻击点 §三.5。 |

---

## 二、六个攻击点的结果

### §三.1 链路 trace 是否真的调用 KERT —— **真的调用，证实**

**破坏性验证**：
```bash
# 注入 KERT execute() 抛异常
cd /home/szf/dev/Leibniz-KERT && python3 -c "..."  # 破坏 execute
cd /home/szf/dev/gits-cbanking && python3 scripts/gk_ke_chain_trace.py
# → 报错：上游调用失败（Traceback → return 1）
# 已恢复（git diff 为空）
```

chain_trace 真实调用了 KERT `SkillExecutionService.execute`。第一轮"探针不真实调用"的问题在 chain_trace 里**不存在**。

**关于"下游输出变化=False"的解释是否成立**：

chain_trace 输出的 `下游输出变化=False` 确实来自确定性适配器——它产出占位内容（`kycGaps` 恒为空），所以"移除上游字段"不会改变下游的占位输出。TL 称这是"确定性适配器的固有限制"，**这个解释成立**，且 chain_trace 脚本本身（第 215-221 行 `whatThisDoesNotProve`）**诚实声明了这一点**："业务语义正确性…无法在本环境证明"。**不是掩盖，是如实标注。**

但要注意：chain_trace 的 `verdict=CHAIN_TRACE_PROVEN_INPUT_LEVEL` 里"输入消费证明=True"的判定，依赖的是 `map_upstream_to_downstream` 这个**脚本内硬编码的映射函数**（第 69-98 行），而非 KERT 生产实现。所以"输入级消费已证明"严格说证明的是"脚本按合同映射后，下游输入确实变了"，而非"KERT 生产实现确实消费了上游字段"。这与第二轮的 counterfactual 是**同一性质**（参考实现），但 chain_trace 的诚实标注（`whatThisDoesNotProve`）把它说清楚了。**可接受，但"输入级消费已证明"这一措辞仍略有乐观，实际是"脚本映射层已证明"。**

### §三.2 预注册锁是否真的锁得住 —— **锁得住，证实**

**破坏性验证**：
```bash
# 篡改判据文档（S1–S5 全部通过 → 任一通过）
python3 scripts/gk_ke_semantic_consumption.py
# → FAIL — 判据文档已被修改！引用 G-4，拒绝执行
# 已恢复
```

**哈希自查**：`sha256sum` 文档当前字节 = `d1e6192b1ec5f28d0a3cf7a916fd800a16c25b216363eca1c96dc949d428a900`，与 `_preregistration.json` 的 `criteriaSha256` **完全一致**。预注册锁真实有效，不是自欺。

### §三.3 覆盖核对器的 B 维是否有意义 —— **B 维有意义，但 D 维是形式主义（重要发现）**

**B 维（防自造要求）真实有效**：
```bash
# 加自造义务 OBL-99（建议书无此要求）
python3 scripts/gk_ke_contract_coverage.py
# → FAIL：义务 OBL-99 无法追溯到建议书 §9.3，且未标注为附加义务（防自造要求）
# 已恢复
```
B 维不是形式主义，能发现"自造要求"。

**D 维（命名差异登记）是形式主义 —— 这是本轮最重要的新发现之一**：

`gk_ke_contract_coverage.py` 第 60-64 行：
```python
KNOWN_RENAMES = {
    "evaluationStatus": "status",
    "evaluatedRuleIds": "ruleTrace.expectedRules/coveredRules",
    "capabilityId/version": "capabilityId + capabilityVersion",
}
```
只有 **3 项**。但 `CapabilityResultEnvelope.json#namingDivergences.map` 实际登记了 **5 处**（另含 `conflictCases/signals`、`requiredQuestions`）。

D 维的实现（第 208 行 `for prop_name, ours in KNOWN_RENAMES.items()`）**只遍历这硬编码的 3 项**。**破坏性验证**：删除合同里 `requiredQuestions` 的命名登记 → D 维**仍报 3/3 PASS**，因为 `requiredQuestions` 根本不在 `KNOWN_RENAMES` 里，D 维从来就没检查过它。

**这带来的两个问题**：
1. **TL 在 FAIL-13 声称"D 维检查：凡与建议书用词不一致者必须登记，未登记即 FAIL"** —— 但实现里 D 维只校验硬编码的 3 项，**无法发现"存在但没写进 KNOWN_RENAMES 的命名差异"**。这个"凡…必须登记"的检查是**虚的**。
2. **D 维显示的 `3/3` 是误导性的**：它让读者以为"命名差异全部登记且已核验"，实际上合同里登记了 5 处，而脚本只核验了其中 3 处，另外 2 处（conflictCases/signals、requiredQuestions）从未被任何脚本校验过"是否登记"。

**这是 TL 未披露的问题**。TL 在 FAIL-13 里声称"D 维检查：未登记即 FAIL"，且声称"删除 namingDivergences → D 维 0/3 并 FAIL（断言非空转）"——但 TL 的破坏性验证**删的是整个 map**（才导致 3 项全没了），**没有验证"删掉 map 里 5 处中的 1 处（如 requiredQuestions）是否被发现"**。若 TL 做过后者，就会发现 D 维只能认 3 处、发现不了另外 2 处。

### §三.4 S1–S5 判据设计评估 —— **见下方专章（三）**

### §三.5 本轮是否又出现"为通过而努力" —— **未发现放宽，但发现一个门禁语义漏洞**

- **未发现校验放宽、断言删除、阈值调至刚好通过**。相反：指标复算从"统一求和"改为"按 recomputeKind 分派"（收紧）；探针从静态标志改为真实调用（收紧）；反事实结论从 PROVEN 降为 LOGIC_ONLY（降级）。
- **门禁语义分离（readiness 不计入失败）是合理修正，还是降低标准？** 我的独立判断：**方向正确，但存在一个未被处理的第三态漏洞**。

  门禁边界文档只分三类：INTEGRITY（失败）/ READINESS（报告）/ NOT_APPLICABLE。但 `semantic-consumption` 脚本的结论是 **`INCONCLUSIVE`**（第 210 行），它在第 258 行 `return 1 if failed else 0`——**INCONCLUSIVE 返回 0**。

  后果（我实测）：
  ```
  $ python3 scripts/run_gates.py --only semantic-consumption
    [PASS   ] semantic-consumption   exit=0
    gk-ke-gates: 1/1 passed
  ```
  **"语义级消费无法判定（B 层未达成）"这一最核心的 readiness 缺口，在门禁汇总里被显示为 `[PASS]`，且不进入 `READINESS NOT MET` 列表。**

  这与门禁边界文档 §1.3 宣称的"READINESS 未达成必须被打印出来、不得静默通过"**直接矛盾**。`INCONCLUSIVE` 是介于 PASS 与 FAIL 之间的**第四态**，但 run_gates 和边界文档都没有为它建模——它被 exit=0 静默归类为 PASS。

  **这是一个真实的、未披露的门禁语义漏洞**。它本身不是"为通过而努力"（TL 的收口文档里如实写了 B 层未达成），但**门禁层**确实把"B 层未达成"静默成了"PASS"，与"门禁只负责暴露事实、不得静默"的自我要求相悖。

### §三.6 TL 自陈的 13 条错误是否完整

- FAILURES.md 实际有 **10 个 `## FAIL-` 条目**（FAIL-2026-09-12-04 ~ FAIL-2026-09-13-13）。派发说明称"13 条错误"，但文件里只有 10 个正式 FAIL 条目。**"13 条"的计数口径不明**（可能含某些未冠 FAIL 前缀的自陈，或含其他文件的错误记录）。这是**计数不一致**，非隐瞒，但应澄清。
- 本轮新增 3 条（FAIL-11/12/13）**如实记录了性质**：
  - FAIL-11：TL 最深刻的自陈，承认"明知有疑而不披露"，主动列出三条指控原文，并承认"我列了攻击点却仍宣称达成，比未意识到更严重"。**诚实度极高。**
  - FAIL-12：承认"求和冒充复算"与"静态标志""永不失败门禁"同族。诚实。
  - FAIL-13：声称"首次由自己的工具发现问题（命名差异）"。**部分真实**——命名差异确实是 `contract_coverage.py` 发现的，但**这个工具的 D 维本身有形式主义缺陷**（§三.3），TL 未披露 D 维只认 3 处、认不出另外 2 处。

**未披露问题（本轮最有价值的产出）**：见 §六。

---

## 三、S1–S5 判据设计评估（§三.4，重点）

### 3.1 可观测性判断

| 判据 | 技术上可观测？ | 分析 |
|---|---|---|
| **S1 冲突传递** | **部分可观测** | 需下游输出能"引用上游 conflictId"。当前 envelope 合同里**没有定义"下游条目如何引用上游 conflictId"的字段规范**（`evidenceRefs` 是字符串数组，未规定必须含 conflictId）。执行时可能因"下游输出无结构化引用字段"而无法机械判定，只能靠文本匹配 → 可观测性弱。 |
| **S2 空结论正确解读** | **可观测** | 只需检查下游"不得产出某类缺口"，属否定式断言，可机械判定。 |
| **S3 未执行≠无冲突** | **可观测，但依赖下游输出约定** | 判据要求下游输出 `reason ∈ {COVERAGE_INSUFFICIENT, ...}`。**但合同 `ConsumerObligations.json` / `CapabilityResultEnvelope.json` 是否约束了"下游必须在输出中体现覆盖不足"？** 我核查：envelope 的 `status` 字段有 `onValue` 约束（FAILED/NOT_RUN 不得当无冲突），但**这约束的是上游状态，不是"下游必须产出 COVERAGE_INSUFFICIENT"**。即：**S3 的判据依赖一个合同未明确强制的要求**（下游必须主动声明覆盖不足），若下游实现不这么做，S3 会误判。这是 S3 的一个隐患。 |
| **S4 假设不得关闭缺口** | **可观测** | 检查下游是否把无证据的 explanation 标为 HYPOTHESIS，可机械判定（若下游有 status 字段）。 |
| **S5 可复现** | **可观测** | 已在确定性适配器下实测 PASS。 |

### 3.2 S3 的核心问题（§三.4 第 2 问）

S3 要求"下游必须产出覆盖不足/待核实"。**合同里有约束吗？**

我核查了 `CapabilityResultEnvelope.json`：`status` 字段的 `onValue` 约束只定义"FAILED/NOT_RUN 不得当无冲突"（这是**上游自身**的语义），**没有一条合同规定"下游消费到上游 NOT_RUN/FAILED 状态时，必须在其输出中产出 COVERAGE_INSUFFICIENT 类标记"**。

所以 S3 的判据是**基于一个合同未强制、也未在下游 schema 中定义的要求**。真实 LLM 接入后，若下游 KYC-GAP 技能的输出 schema 里没有 `reason` 字段、或没有 `COVERAGE_INSUFFICIENT` 枚举，S3 将**无法通过结构化方式判定**，只能靠文本启发式——这会使 S3 的判定变成"LLM 自由文本是否含关键字"，可观测性弱、易被"看起来对"糊弄（正是 TL 自己在 S3 注释里警告的）。

**这是判据设计埋的一个雷**：S3 是 TL 自己标注"最重要的一条"，但它的可执行性依赖一个**尚未落到合同/下游 schema 的字段约定**。届时要么补合同（触发"判据变更须留痕"），要么用文本启发式（可观测性弱）。

### 3.3 遗漏分析（§三.4 第 3 问）

S1–S5 覆盖了：冲突传递、空结论、未执行≠无冲突、假设不关闭、可复现。

建议书 §9.3 消费表中还有哪些消费要求未被 S1–S5 覆盖？

| 建议书 §9.3 行 | 对应判据 | 是否覆盖 |
|---|---|---|
| 行1 taskId/entityId/asOf 三元组 | （无对应判据） | **遗漏**——三元组一致性（INV-ENV-1）在 envelope 里定义了 FAIL_CLOSED，但 S1–S5 **没有一条判据验证"下游是否真的校验了三元组一致性"** |
| 行2 evaluationStatus | S3 | 覆盖 |
| 行3 evaluatedRuleIds | （部分由 S2 隐含） | **部分遗漏**——"覆盖充分性"的传递未单列判据 |
| 行4 conflictCases/signals | S1/S2 | 覆盖 |
| 行5 comparedMetricRefs | （无对应判据） | **遗漏**——"可比口径，不能引用该结论"没有任何判据 |
| 行6 evidenceRefs/explanations | S4 | 覆盖 |
| 行7 requiredQuestions | （无对应判据） | **遗漏**——"必须询问，不得无理由删除"没有任何判据 |

所以 S1–S5 **遗漏了至少 3 条建议书 §9.3 的消费要求**：三元组一致性、comparedMetricRefs 可比口径、requiredQuestions 不得删除。TL 未披露这个遗漏（方案文档 §6 边界只说了"S1–S5 未经真实 LLM 检验"，未说"§9.3 有 3 行未被判据覆盖"）。

### 3.4 通过规则是否过严/过松（§三.4 第 4 问）

通过规则是"S1–S5 全部通过才达成，任一失败未达成"。这个规则**本身合理**（fail-closed），且明确"INCONCLUSIVE 不得记为通过"是**正确的**——它防止了"部分通过"被表述为"基本达成"。

但结合 3.3 的遗漏：**即使 S1–S5 全部通过，也并不能覆盖 §9.3 全部消费要求**（漏了 3 行）。所以"全部通过 = 语义级消费达成"这个等价关系**被高估了**——它最多证明"5 条判据覆盖的消费达成"，而非"§9.3 全部消费达成"。

---

## 四、"为通过而努力"的检查结论（§三.5）

**未发现**本轮存在"校验被放宽、断言被删除、阈值被调到刚好通过"的行为。相反，本轮是**持续收紧**：
- 指标复算：统一求和 → 按 recomputeKind 分派（RATIO/DAYS 改为按公式逐期交叉校验，收紧）
- 探针：静态标志 → 真实调用（收紧）
- 反事实：PROVEN → LOGIC_ONLY（主动降级）

**门禁语义分离（readiness 不计入失败）的独立判断**：

**方向正确**。TL 的理由（"若把未达成计入门禁失败，会制造'为让门禁变绿而把未达成改写成通过'的诱因"）**成立且深刻**——这确实是他犯过的错误模式的逆操作。把"结论由文档声明、门禁只暴露事实"分离，是**合理修正**，不是降低标准。

**但存在一个未处理的第三态漏洞**（§三.5）：`INCONCLUSIVE` 态既不是 PASS 也不是 FAIL，却被 exit=0 静默归为 PASS。这**削弱了"门禁只负责暴露事实"的自我要求**——"B 层语义消费未达成"这一最核心事实，在门禁层没有被暴露出来（显示为 PASS，且不打印 READINESS NOT MET）。

**结论**：门禁语义分离是合理修正，但 `INCONCLUSIVE` 应被建模为独立态（如打印 `INCONCLUSIVE NOT MET`，或至少不以 PASS 显示），否则"门禁暴露事实"的承诺在语义消费这一项上是失效的。

---

## 五、A 层 / B 层的独立判定（§四）

### §四.1 A 层收口是否仍然成立

**仍然成立**。本轮新增的三项（链 trace、语义预注册、覆盖核对）都**不削弱 A 层**，反而补强了 A 层的"可测试性"证据。未发现新的 A 层未达成项。

但有一个**文档不同步**问题：A 层收口决议（V1.0，提交 5e46cb5/7c576b4）写于本轮新增脚本之前。其 §5.3 B 层缺口第 1 条"能力间消费的运行时 trace 缺失"、§7"门禁 15/15"**均已过时**（chain_trace 已产出 trace、门禁现为 18/18）。收口决议**未随本轮新增同步更新**，会造成读者对 B 层缺口的理解落后于实际。

### §四.2 B 层"仍未达成"的判断是否诚实

**诚实，且略有低估的倾向（非高估）**：

- TL 声称 B 层缺口为"语义级消费待真实 LLM"。**这个表述是准确的**，但**低估了缺口**——B 层缺口不止"语义级消费"一项，还包括：
  1. 三阶段（P12/P13/P14）**持久化未实现**（收口决议 §5.3 自己列了，但本轮语义消费方案聚焦后，这个缺口容易被淡忘）；
  2. 端到端链路（跨能力）真实调用记录（chain_trace 只做了 FACT-RECON→KYC-GAP 单链路，非全链路）；
  3. `comparedMetricRefs`、`requiredQuestions`、三元组一致性 3 条 §9.3 消费要求**连判据都没有**（§三.3 遗漏）。

- 四个 `NOT_PROBED` 能力的理由**全部成立**（我逐一核验）：
  - `SIM-CAP-INTERPRET`：GK-KE 本地执行器，非 KERT 技能，探针不声称做过 KERT 端到端调用（诚实）；
  - `SIM-CAP-PRODUCT-REC`：executorRef 未解析（PENDING_NAMING_MAPPING）；
  - `SIM-CAP-MEETING-SCRIPT` / `SIM-CAP-OUTREACH-SCRIPT`：调用成功但无独立 output-schema，无法校验契约（诚实标注，不声称满足）。

  无一为"未尝试"，也无一是"已达成但被说成未达成以显得谦虚"。**诚实。**

---

## 六、TL 披露完整性（§三.6；未披露问题是最有价值的产出）

### 已诚实披露的（值得肯定）

- FAIL-11 是 TL 迄今最深刻的自陈，主动列出三条指控原文，承认"明知有疑而不披露"比"未意识到"更严重。
- FAIL-12 承认"求和冒充复算"与前科同族。
- FAIL-13 首次由自己的工具发现问题，且诚实标注"非 QA 指出"。

### 未披露的问题（本轮最有价值的产出）

**1. 【严重】D 维（命名差异登记校验）是形式主义**
- 证据：`KNOWN_RENAMES` 硬编码 3 项，合同登记 5 处；删掉 `requiredQuestions` 登记后 D 维仍 3/3 PASS。
- TL 在 FAIL-13 声称"D 维：凡与建议书用词不一致者必须登记，未登记即 FAIL"，但实现只能发现"3 项硬编码之一缺失"，**发现不了另外 2 处（conflictCases/signals、requiredQuestions）的登记缺失**。
- TL 的破坏性验证只删了整个 map（3 项全无 → FAIL），**没有验证"删 5 处中 1 处"**，所以未发现这个盲区。

**2. 【严重】INCONCLUSIVE 门禁语义漏洞（第四态未建模）**
- 证据：`semantic-consumption` 报 INCONCLUSIVE（B 层未达成）但 exit=0，在 run_gates 显示 `[PASS]`，不进入 READINESS NOT MET。
- 门禁边界文档只分三类，未处理 INCONCLUSIVE。这与"门禁不得静默暴露事实"的自我要求矛盾。

**3. 【中】S1–S5 遗漏了 §9.3 的 3 条消费要求**
- 三元组一致性（行1）、comparedMetricRefs（行5）、requiredQuestions（行7）均无对应判据。
- 方案文档 §6 只声明"S1–S5 未经真实 LLM 检验"，未声明"§9.3 有 3 行未被判据覆盖"。这意味着"S1–S5 全部通过 = 语义消费达成"被高估了。

**4. 【中】S3 判据依赖一个合同未强制的字段约定**
- S3 要求下游输出 `COVERAGE_INSUFFICIENT` 类标记，但合同未强制下游 schema 必须含此字段。届时要么补合同（触发判据变更），要么用文本启发式（可观测性弱）。

**5. 【低】收口决议文档未同步本轮新增**
- A 层决议 §5.3（trace 缺失）、§7（15/15）已过时（现 18/18，trace 已产出）。

**6. 【低】"13 条错误"计数口径不明**
- FAILURES.md 实际 10 个 FAIL 条目，与派发说明"13 条"不一致，应澄清口径。

---

## 七、附：核验命令与原始输出

```bash
# 1. 锚点确认
cd /home/szf/dev/gits-cbanking && git rev-parse HEAD        # 5f3a770
cd /home/szf/dev/Leibniz-KERT && git rev-parse HEAD         # 89fbbce

# 2. 复现五项新增
python3 scripts/gk_ke_chain_trace.py
#   → CHAIN_TRACE_PROVEN_INPUT_LEVEL，下游输出变化=False（确定性适配器限制，诚实标注）
python3 scripts/gk_ke_semantic_consumption.py
#   → INCONCLUSIVE（S5 PASS，S1-S4 无法判定，不得记为通过）
python3 scripts/gk_ke_contract_coverage.py
#   → PASS：A 7/7, B 7/7, C 14/14, D 3/3
python3 scripts/gk_ke_capability_probe.py
#   → PASSED=8, NOT_PROBED=4（INTERPRET/PRODUCT-REC/MEETING-SCRIPT/OUTREACH-SCRIPT，理由均成立）
python3 scripts/run_gates.py
#   → 18/18 passed

# 3. 破坏性验证 §三.1（破坏 KERT execute → chain_trace FAIL）
#   注入 execute() 抛异常 → chain_trace 报错 FAIL → 已恢复（git diff 为空）

# 4. 破坏性验证 §三.2（篡改判据文档 → semantic FAIL 引用 G-4）
#   改"全部通过"→"任一通过" → FAIL 引用 G-4 → 已恢复
#   sha256sum 文档 = d1e6192b… 与 _preregistration.json 一致

# 5. 破坏性验证 §三.3 B 维（加自造义务 OBL-99 → FAIL）
#   加 OBL-99 → B 维 7/8，报"无法追溯 §9.3" → 已恢复

# 6. 破坏性验证 §三.3 D 维（删 requiredQuestions 登记 → 仍 3/3 PASS）
#   删 namingDivergences.map.requiredQuestions → D 维仍 3/3 PASS（形式主义证据）→ 已恢复

# 7. INCONCLUSIVE 门禁语义漏洞验证
python3 scripts/run_gates.py --only semantic-consumption
#   → [PASS] semantic-consumption exit=0（INCONCLUSIVE 被静默归为 PASS）

# 8. 计数核对
grep -c "^## FAIL-" loops/GK14-l4-0-capability-closure/FAILURES.md
#   → 10（与"13 条"口径不一致）
```

---

## 最终立场

**前两轮的否决与修复路径是真实有效的，本轮 TL 的核心修复（真实调用、预注册锁、B 维防自造、门禁语义分离）经破坏性验证均证实。**

但本轮**新增的两个形式主义问题**值得指出：

1. **D 维命名差异登记校验是形式主义的**——脚本只认硬编码 3 项，合同登记了 5 处，删掉其中 1 处（requiredQuestions）不被发现。TL 声称的"D 维凡不一致必登记"是虚的。

2. **INCONCLUSIVE 门禁第四态未建模**——"B 层语义消费未达成"在门禁层被静默显示为 PASS，与"门禁不得静默暴露事实"的自我要求矛盾。

以及 **S1–S5 遗漏了 §9.3 的 3 条消费要求**（三元组一致性、comparedMetricRefs、requiredQuestions），使"S1–S5 全部通过 = 语义消费达成"被高估。

**结论：A 层收口仍然成立，B 层仍未达成（判断诚实）。** 但 TL 应：
1. 修正 D 维，使其**从合同 `namingDivergences.map` 动态读取全部登记项**（而非硬编码 3 项），并做"删 5 处中任意 1 处"的破坏性验证；
2. 为 `INCONCLUSIVE` 建模独立门禁态（不得以 PASS 显示）；
3. 补登 S1–S5 对 §9.3 的覆盖矩阵，明确标注遗漏的 3 行；
4. 同步收口决议（trace 已产出、门禁 18/18）。
