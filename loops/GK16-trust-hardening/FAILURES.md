# GK16 信任收敛 Loop · 失败记录（**已从 git 历史重建**）

> **重建说明**：本文件曾被多次**整文件覆盖**，致早期条目（T-01~T-11 等）丢失。
> 现从 git 历史（7 个版本）按 T 编号合并重建；同一编号取**最新版本**文本。
>
> **根因与教训**：这是「用整文件覆盖代替追加」造成的**真实数据丢失**——
> 而这个文件恰是本项目最有价值的产物。**增量追加优于整文件重写。**

## T-01 【攻击命中·最重要】"9 项注入被检出"中，**6 项实为崩溃**

- **攻击**：正角色报告「9 个门禁有负例证据」。反角色问：**检出 = 门禁校验失败，还是门禁崩溃？**
- **结果**：实测 6 个门禁（contract-examples / contract-coverage / metric-definitions /
  product-card / registry-contract / plan-compiler）在注入**语法非法**的 JSON 后
  **抛 Traceback 退出**。那**只证明它没有输入防御**，**不证明它的校验逻辑发现了缺陷**。
  > **一个遇到非法输入就崩溃的门禁，在真实场景下同样会崩溃，而不是给出判定。**
- **结论**：**"9" 是虚高的；真受控检出只有 3 项。**
- **修复**：① 注入改为**语法合法、语义违规**（`{}`）；② 框架**单列 crash**，
  含 Traceback 的非零退出**不计为检出**。修复后 **11 项受控检出、0 崩溃**。


## T-02 【攻击命中】`gate-injection-tests` 自身"误导性通过"

- **攻击**：该门禁在有 3 项未确立 + 7 项未设计 + 1 项跳过（**11/18 未验证**）时仍 **exit=0 → PASS**。
  读汇总的人会以为"注入测试已完成"。
- **修复**：改为**覆盖不完整即 `__GATE_VERDICT__=INCONCLUSIVE`**，并在结论中给出精确缺口。
  现门禁链显示 `[INCONCLUSIVE] gate-injection-tests` —— **"未完成"对读者可见**。


## T-03 【攻击命中】元层面静默跳过：**2 个门禁无人认领**

- **攻击**：`run_gates` 有 **22** 个门禁，而框架只认领 13（注入）+ 7（未设计）= **20**。
  → **后人在 `run_gates` 新增门禁会**自动**落入盲区，且无人察觉。**
- **修复**：新增**认领盘点**——凡未在「注入设计」或「未覆盖登记」中出现的门禁，
  **直接 FAIL**。实测该检查当场抓到 `gate-injection-tests` 自身未被认领。
  现为 **22/22 全部认领**。


## T-04 【攻击未果·已登记攻击路径】注入点选错导致的"注入无效"

- **攻击**：正角色报告 dataset-v2 / acceptance-pack / loop-guard 三项目"注入未检出"。
- **尝试的路径**：① 破坏 JSON 语法 → 无效；② 注入 `{}` → 无效；
  ③ 破坏**文件哈希** → 无效（`dataset-v2 --verify` **不比哈希**）。
- **命中**：**这三者做的是语义检查，不是结构检查** ——
  · `loop-guard --template-check` 校验 `loops/_template`，
    且要求 `EVIDENCE.json` 的 gates 与 `LOOP.yaml` 一致；
  · `dataset-v2` 校验**禁止署名**（真实监管机构名）与**时间泄漏**。
  → 改为**语义注入**后，`loop-guard` 与 `dataset-v2` **均被检出**。
- **仍余**：`acceptance-pack` 的注入有效性**未确立**（它另有 `check_structure`/`check_isolation`，
  尚未找到其校验点）→ **如实登记为未验证，不计为通过**。


## T-05 【攻击未果·已登记】剩余覆盖缺口（**未修复，如实登记**）

| 门禁 | 状态 | 原因 |
|---|---|---|
| acceptance-pack | 注入有效性未确立 | 未找到其实际校验点 |
| semantic-rule-gate | 只读跳过 | 制品 `generated/` 受保护；**按纪律不放开写位**（FAIL-51 事故） |
| contract-check | 未设计注入 | shell 脚本，未读其校验逻辑 |
| enum-consistency | 未设计注入 | 需构造三层（Java 枚举/seed/schema）漂移 |
| probe-mutation-tests | 未设计注入 | 该门禁自身即变异测试，对其注入需改被测探针 |
| capability-probe | 未设计注入 | readiness 类，需构造能力不可调用场景 |
| counterfactual-test | 未设计注入 | readiness 类，需构造反事实失效场景 |
| chain-trace | 未设计注入 | 需 KERT 服务在运行 |
| semantic-consumption | 未设计注入 | 注入点为其汇总逻辑；其结论已由 NOT_MET 实测覆盖 |

> **登记 ≠ 修复。** 但**妨碍停止的不是"仍有缺口"，而是"未尝试攻击"或"隐瞒缺口"。**
> 上表由 `gate-injection-tests` **每次运行都打印**，不可隐藏。


## T-06 【终结】实例合规**棘轮**

- 事实：58 个实例中 **30 个不合规**，而门禁只跑 `--template-check`，**从不验实例**。
- **为何不对 30 个历史实例直接判 FAIL**：它们是**已完成的历史工作**，
  一次性改判会阻断门禁链，且**不改变任何事实**。
- **棘轮策略**（新增 `loop-guard --instances-check` + 门禁 `loop-instances`）：
  · 基线 `loops/_instance_baseline.json` **冻结** 30 条历史欠账；
  · **不在基线中的实例必须合规** → 否则 **FAIL**；
  · 基线中转为合规者 → 报告进展；基线中陈旧条目 → 报告；
  · **基线条目数不得增长**。
- **棘轮自身的负例测试（两路，均实测通过）**：
  ① 新建 `loops/ZZ-ratchet-test`（不合规）→ **拦截**，报 `1 个新增不合规实例`；删除后转绿；
  ② 清空基线 → **拦截**，报 `30 个新增不合规实例`。
- **一个值得记下的自证**：新增 `loop-instances` 门禁后，
  `gate-injection-tests` 的**「无静默跳过」检查当场要求认领** —
  **那是我在第 3 代（T-03）加的检查，5 代之后验证了自己的价值。**

## 门禁链（终局）

```
gk-ke-gates: 20/23 通过（其中 1 项 INCONCLUSIVE，不计入通过）
  [PASS]          20 项（含 loop-instances / loop-guard）
  [INCONCLUSIVE]  capability-probe     ← 2 项 NOT_PROBED（可调用性未被证明）
  [INCONCLUSIVE]  gate-injection-tests ← 18 项已检出；余 3 项全为正当
  [FAIL]          chain-trace          ← 7 个合同字段上游无来源（真实缺口）
  [FAIL]          semantic-consumption ← NOT_MET（独立判定，TL 不代判）
  READINESS NOT MET: ['chain-trace','semantic-consumption','capability-probe']
```

## 剩余「未终结」项（**均非我权限内可闭合**）

| 项 | 为何不在我权限内 |
|---|---|
| `chain-trace` 的 7 个真实缺口 | 需 **KERT 侧**产出规则覆盖轨迹 / 指标引用 / 解释与依据 / 证据引用 / 必答问题 |
| `capability-probe` 的 `PENDING_NAMING_MAPPING` | 同上（9 项能力 executorId 命名映射未定） |
| `semantic-consumption` NOT_MET | 判定由**独立执行者**作出，**TL 代判即违规** |
| 30 条历史 loop 实例欠账 | 已冻结；修复属**逐个人工工作**，非门禁可代劳 |

> **这四项的共同性质：不是"我没查清"，而是"查清了、已归责、等对应方行动"。**
> **这与"未登记"有本质区别。**


## T-07 【自我更正】我称 C4「回读证据」**未建** —— **错了，loop schema 早已强制**

- **经过**：为让 GK16 通过 loop-guard，读到它要求每个 `pass` 门禁必须提供
  `evidence_file`（须位于该 loop 的 `evidence/` 内）+ **`output_sha256` 哈希校验**
  + `actor` / `actor_role` / `executed_at`。
- **更正**：这正是我在 `GK-KE-自查方案逐项源代码举证-V1.0.md` 中
  列为 **C4「未建」**的那条控制 —— **loop 协议早已强制它。我的判断是错的。**
- **教训**：**宣布"某控制不存在"之前，必须在**整个仓库**搜索它，而不只是在预期的地方。**
  这与 FAIL-43（一次 `ls` 就宣布 workspace 不存在）**同族**，
  且发生在**同一份文档、同一天**。


## T-08 【终结】loop 证据词表补入 `inconclusive`

- `ALLOWED_EVIDENCE` 由 `{pending, pass, fail, blocked}` 扩为**含 `inconclusive`**。
- 依据：判据体系已确立「**INCONCLUSIVE ≠ 通过**」，而 loop 协议**无该态**，
  迫使 `gate-injection-tests` 与 `capability-probe` 的判定**有损映射为 `blocked`**。
- GK16 的 `EVIDENCE.json` 已由有损映射**改回真实态**，并移除有损标注。
- 实测 `loop-guard: PASS`（新态被接受，且**不计为通过**）。


## T-09 【攻击命中·最重要】我宣布收敛 —— **撤回**

- **攻击**：Owner 问"没有再优化加固的必要了吗？"。反角色检查自己的停止条件：
  > 「① **所有结论**均经至少一次**可执行**攻击」
- **命中**：**7 个门禁从未被攻击过**。我在 T-05 表里写的是
  「shell 脚本，**未读其校验逻辑**」—— **那不是"攻击路径"，那是"我没看"**。
  **停止条件 ① 未满足，我却宣布收敛。**
- **同族**：**T-07（宣布"未建"之前没搜索）↔ T-09（宣布"收敛"之前没攻击）**。
  **同一个错，换个动词，同一天发生。**
- **自相矛盾**：T-02 我刚立下「覆盖不完整 → 不得计为通过」，
  然后**带着 9 项未决宣布收敛** —— 我给自己立的规矩，第一个违反的是我。
- **处置**：`STATE.json` 增 `convergence_retracted` 与 `not_yet_done`。
  **在 ① 与 ⑤ 完成前不得再宣布收敛。**


## T-10 【攻击命中】我的 11 项检出是**弱证据**

- **攻击**：那 11 项"检出"，是死于**正确原因**吗？还是死于别的检查？
- **命中**：`metric-definitions` 在 `{}` 注入下报的是
  **`registry fileSha256 不一致`** —— 那是**完整性比对，不是语义校验**。
  **空文件会先撞上哈希检查，把后面的语义检查遮住。**
  → 该证据**不能排除"这个门禁只会比哈希"**。
  （同为弱证据：`registry-contract` 报 `dangling dependencyRef`，是**级联失败**，非本体校验。）
- **决定性测试**：构造「**语义违规 + `--write` 同步哈希**」的注入（绕过完整性检查）
  → 门禁**仍**报 `simulationOnly 必须为 true`
  ⇒ **该门禁确有语义校验能力（攻击被挡下）**，**但我的原始证据确实是弱的**。
- **修复**：把**语义级注入自动化**进 harness（`SEMANTIC_INJECTIONS`），常态化运行。
  现每次运行都打印「语义级注入: N 项通过（哈希已同步，仍被检出 ⇒ 确有语义校验能力）」。
- **未完成**：**其余 10 项检出的"死于正确原因"尚未逐项核验** —— 已登记。


## T-11 【未查明·如实登记】一次无法解释的哈希失配

- **现象**：重建证据文件并计算 `output_sha256` 后，`loop-guard` 报
  `gates` 与 `gate_injection_tests` **两文件哈希不符**；
  **在不改动任何文件的前提下重新计算**同一批哈希 → **`loop-guard: PASS`**。
- **已排除**：`run_gates.py` 不含任何写 evidence 的代码（grep 无命中）。
- **结论**：**原因未查明。** 可能与先后执行顺序有关，但我**没有证据**。
- **处置**：**如实登记为未解释现象**。
  > **不得把"重算一次就过了"当成"已解决"。**
  > 这正是本 Loop 一直在打的那种"看起来没事了"。
  > **推而广之：哈希锚定机制本身可能不稳定 —— 在查明前，
  > `loop-guard: PASS` 这一条的强度应视为低于它的表面值。**

---

# 停止声明（第 2 版 · **撤回上一版**）

> **上一版写的是"反角色已无法构造新的可执行反例"—— 那是错的，因为我没有让反角色去攻 7 个门禁。**
>
> **本版停止条件（未满足，故不停）：**
>
> | # | 条件 | 状态 |
> |---|---|---|
> | ① | 所有结论均经至少一次可执行攻击 | ✗ **7 个门禁从未攻击** |
> | ② | 构造不出反例者，攻击路径已登记 | ✓ 已登记（但见 ①） |
> | ③ | 所有缺口已如实登记 | ✓ |
> | ④ | "检出"须死于**正确原因** | ✗ 仅 1 项经语义级验证，**其余 10 项未核验** |
>
> **结论：本 Loop 仍在进行中，未收敛。**
>
> **Owner 的追问是对的：还有必要，而且至少还有四件事没做。**


## T-12 【攻击命中·最重要】`chain-trace`：**打印 FAIL 却不终止**，且**合同从未被使用**

- **攻击**：清空 `ConsumerObligations.json` 的 `obligations`（合同未声明任何义务）。
- **命中**：门禁仍判 **`CHAIN_TRACE_PROVEN_INPUT_LEVEL`，exit=0**。
- **根因（实测，非推测）**：
  1. `if chain_def is None:` 分支**打印了 `FAIL` 但缺少 `return 1`**，随后继续执行到底；
  2. 反事实字段**硬编码**为 `("conflicts","indicators","warnings","status")`，**不读合同**；
  3. `input_consumed = all(...)` 对空集合返回 `True`（`all([]) == True`），**静默通过**。
- **形态**：**「文本说 FAIL、结论说 PASS」** —— 与本 Loop 第一个打中的形态
  （`gate_injection_tests` 的误导性通过）**完全同构，而它出现在我自己的门禁里**。


## T-13 【自我更正·必须记录】我的"修复"本身把门禁改坏了一半

- **第一版修复**：把反事实字段改为由合同 `upstreamFields` 推导
  （`taskId/entityId/asOf/status/ruleTrace/result/evidenceRefs`）。
- **实测证伪**：上游 `bank-front-fact-reconciliation` 真实返回键为
  `asOf/conflicts/customerId/dataGaps/executionStatus/indicators/taskId/warnings`。
  **我推导的 `entityId/status/ruleTrace/result/evidenceRefs` 一个都不存在。**
- **我错在哪**：合同 `upstreamFields` 是**下游输入封装**的字段名；
  而反事实是**对上游 result 做移除** —— **两套名字根本不同**。
  **修复前硬编码的 `conflicts`/`indicators`/`warnings` 恰恰是上游真有的键。**
  → **我几乎把一个"字段选错但机制诚实"的门禁，改成"字段更错"的门禁。**
- **最终修复**：字段须同时满足 ① 合同声明 ② **上游真实存在**，
  并对二者做**显式交叉校验**（不匹配即 FAIL），而非单取任一方。


## T-14 【终结】合同/实现错位 —— 性质查明，门禁改报**真问题**

**先查清事实（不推测）**：

| 合同字段 | 上游真实返回 | 性质 |
|---|---|---|
| `taskId` / `asOf` | ✅ 存在 | 一致 |
| `entityId` | ❌ | **异名同义** ← `customerId` |
| `status` | ❌ | **异名同义** ← `executionStatus` |
| `result.conflictCases` | ❌ | **异名同义** ← `conflicts` |
| `result.signals` | ❌ | **异名同义** ← `indicators` |
| `ruleTrace.*` | ❌ | **真实缺失** |
| `comparedMetricRefs` / `explanations` / `requiredQuestions` | ❌ | **真实缺失** |
| `evidenceRefs` | ❌ | **真实缺失** |

**权威核对**：建议书 V2.0:492 原文即 `| taskId / entityId / asOf | ... |`
⇒ **合同忠实于 §9.3，不得为让门禁变绿而改合同**（那正是"把合同改成迎合实现"）。

**TL 决策**：这份映射（合同字段 ← 上游字段）**本来就必须存在** —— 它是链路适配层的职责。
**问题在于它过去是硬编码、未声明、未验证的**，从而长期掩盖了真实缺口。

**新增** `specs/knowledge-architecture/contracts/UpstreamFieldMapping.json`：
- `mappings`：6 条显式映射（含"异名同义"标注）；
- `unmappedContractFields`：7 条，**每条给出理由、影响的 §9.3 义务、责任方**；
- **三条机械校验**，由 `chain-trace` 执行：
  ① 映射的合同字段必须在 `ConsumerObligations` 中真实声明（**不得凭空发明**）；
  ② 映射的上游字段必须在上游**真实返回**中存在（**不得指向空**）；
  ③ 同一字段不得同时出现在 `mappings` 与 `unmappedContractFields`（**不得自相矛盾**）。

**结果**：`chain-trace` 仍 **FAIL**，但报的是**真问题**：

```
FAIL — 合同声明但**上游无来源**的字段 (7 项，§9.3 对应义务无法达成）
  ruleTrace.expectedRules/coveredRules/missingRules  ← 行 3
  result.comparedMetricRefs                          ← 行 5
  result.explanations / evidenceRefs                 ← 行 6
  result.requiredQuestions                           ← 行 7
```

> **修复前它把"命名不同"与"真的没有"混在一张清单里报
> （`entityId/status/ruleTrace/result/evidenceRefs`），无法分辨；
> 修复后两者被机械地分开。**
> **这与本仓独立判定（`S3 FAIL`/`S5 FAIL`、§9.3 由 S1–S5 覆盖的四行未达成）同向。**


## T-15 【攻击命中·已修】`enum-consistency --quiet` 失败**完全无声**

- **攻击**：注入非法受控枚举值 `'D01_FAKE_NOT_IN_GATETYPE'`。
- **命中**：门禁 `exit=1`，但 `--quiet` 下 **stdout/stderr 全空** ——
  门禁链里只看到一个 FAIL，**失败原因不可见**（与 FAIL-22/36「静默跳过」同族）。
- **修复**：`run_gates.py` 中该门禁**去掉 `--quiet`**。
  实测非静默模式会打印 `V001__....sql: 非法受控枚举值 'D01_FAKE_NOT_IN_GATETYPE'`。

## 元教训：我本轮**连续两次用"读代码推测"宣布缺口，两次被实测证伪**

| 我推测的缺口 | 代码依据 | 实测结果 |
|---|---|---|
| `counterfactual-test` 在 `total=0` 时判 PASS | `all_consumed = total > 0 and consumed == total` | **证伪**：有另一处 failure 追加，`exit=1` |
| `chain-trace` 的攻击应走"未登记"分支 | 读了 envelope 校验 | **证伪**：实际命中 `chain_def is None` 且无 `return 1` |

> **两次"读代码 → 宣布缺口"都被实测推翻。**
> **代码阅读只能生成假设；只有实测能确立结论。**
> 这与 T-07（宣布"未建"前没搜索）、T-09（宣布"收敛"前没攻击）**同根**：
> **都是"我以为"替代了"我验证"。**

## 全仓同族 bug 扫描（12 处候选，仅 1 处为真）

对 `scripts/*.py` 扫描「打印 FAIL 但后续无 `return`/`sys.exit`/`raise`」→ 12 处候选。
**逐个复核后仅 `chain_trace.py` 为真缺口**，其余为汇总打印或后统一 `return 1`。

> **扫描器本身也会误报 —— 故"扫描出 12 处"不得直接引用为"12 个 bug"。**


## T-16 【已核实·结论成立】`counterfactual-test` **无**同族缺陷

- **攻击**：它与 `chain-trace` 是否同样"读合同但不用合同"？
- **核实（读源码 + 实测）**：
  - `apply_field_mutation` 按 `field.split(".")` **导航真实路径**并变异 —— **通用，非硬编码**；
  - `downstream_gap_generation` 读 `taskId/entityId/asOf/status/ruleTrace.coveredRules/
    result.conflictCases/result.signals/result.comparedMetricRefs/result.explanations/
    evidenceRefs/result.requiredQuestions` —— **与合同 `upstreamFields` 逐一对上**。
- **结论**：**真合同驱动。我上一轮"✅ 正确检出"的判定成立**（这次基于读源码+实测，非推测）。


## T-17 【攻击命中·已修】`capability-probe`：**零能力通过 = PASS**

- **攻击**：把**全部 12 个**条目的 `executorRef` 置为不可解析。
- **命中**：
  ```
  total=12  PASSED=0  NOT_PROBED=12   →   exit=0（PASS）
  ```
  > **即使 12 个能力全部不可调用，门禁仍 PASS，门禁链全绿。**
  > **`NOT_PROBED` 与 `PASSED` 在退出码上完全等价 ——「我没查」与「我查通过了」同义。**
- **形态**：**正是判据 `S2_EMPTY_MEANS_NONE` / `S3_NOT_RUN_NOT_NONE` 要防的形态，
  而它出现在门禁链自身**（与 T-12 同族，覆盖面更大：12 个能力的可调用性证明）。
- **修复（两条，均不含主观阈值）**：
  1. **零能力通过 ⇒ FAIL**（最小、无争议）；
  2. `NOT_PROBED` 中**「注册表条目未完成」类**（`executorRef 未解析`）⇒ **INCONCLUSIVE**。
- **为何是 INCONCLUSIVE 而非 FAIL**（实测依据）：
  `PENDING_NAMING_MAPPING` 是**已登记的已知欠账** ——
  `docs/architecture/GK-KE-GK14-UE-UC-交付报告-V1.0.md:110` 明载
  「9 项能力的 `executorRef` 仍未解析（`PENDING_NAMING_MAPPING`）」，
  `:246` 称「只要 `executorRef` 仍是 `PENDING_NAMING_MAPPING`，`callable` 就永远只有 1」。
  → **不应判 PASS（那是把它当没问题），也不应判 FAIL（那是新失败）；
  正确语义是部分证明，不得计为全部通过。**
- **修复后实测**：基线 `INCONCLUSIVE / PASSED=10/12`；决定性攻击（全部不可解析）→ **FAIL**。
- **形态一致性**：与 `gate-injection-tests` 的「覆盖不完整 ⇒ INCONCLUSIVE」**同一模式**。


## T-18 【攻击命中·已修】空注册表 ⇒ PASS（**我在修复中写出的新同族缺陷**）

- **攻击**：把 `Capability.json` 写成 `{}`。
- **命中**：`total=0 PASSED=0 NOT_PROBED=0` → **`__GATE_VERDICT__=PASS`**。
- **根因**：我修 T-17 时写的是 `if results and n_passed == 0` —— **`results` 为空时短路**，
  于是"零条目"这一**更极端**的情形**反而绕过**了检查。
- **形态**：与 `chain-trace` 的 `all([]) == True` **完全同构**。
  > **我在修一个"空集合静默通过"的同时，写了一个新的同族缺陷。**
- **修复**：`not results ⇒ FAIL`（零条目）；`results and n_passed == 0 ⇒ FAIL`（零通过）。


## T-19 【攻击命中·已修】注入测试留下副作用残留

- **命中**：注入 `capability-probe` 后，门禁**写副作用产物**
  `evidence/gk-ke-capability-probe/report.json`；框架还原了**注入目标**，
  **未还原副作用产物** → 残留空报告。
- **危险性**：**"沉默的污染"** —— 若有人在此状态下提交，就把空报告提交进去了。
- **修复**：结束时**自动回滚"本次新增的改动"**（`before_status` 中不存在的条目），
  不动运行前已存在的改动。实测回滚 1 个产物，残留检查转绿。


## T-20 【已解决·根因是我自己的静默编辑错误】

**上一轮我写的是"如实登记 —— 不解决"。那是错的** ——
**Owner 追问后我继续查，根因 10 分钟内就找到了。**
> **"登记"是防止掩盖的纪律；"不解决"是放弃。我用前者给后者做了包装。**

### Root cause：**重复字典键静默覆盖**

```270:277:scripts/gate_injection_tests.py   （修复前）
PRECISE = {
    "acceptance-pack": _inj_blank_csv_cell,        ← 我新加的
    ...
    "acceptance-pack": _inj_forbidden_signature,   ← 旧条目，**静默覆盖了上面**
}
```

**Python 字典字面量允许同名键，后者胜出 —— 无语法错误、无警告、`ast.parse` 通过。**

所以我"加了一个注入器"后：
- ✅ 函数已定义
- ✅ 字典里"看起来"有条目
- ✅ 语法检查通过
- ❌ **实际生效的是旧注入器**（为 `world_truth.json` 设计，在 CSV 上自然锚点未命中）

### 这暴露了我一个**系统性的盲区**

> **我的所有编辑都只用"文本是否存在"来自证**（改完 `grep` 一下、`ast.parse` 一下）。
> **但"文本在" ≠ "生效的是这一条"** —— 重复键、遮蔽、后定义覆盖，
> **全都能通过我的自证。**

**修复**：新增 `_assert_precise_identity()`，**用 `is` 校验对象身份**，
在模块加载时即断言 `PRECISE[k] is 期望函数`，否则**抛异常**。

### 一个值得记下的反证

> **是我的框架的"诚实"暴露了我的错误。**
> 它报 `精确注入锚点未命中 —— 测试无效`，而**不是**报"未检出"。
>
> **如果它当时把"锚点未命中"当成"门禁未检出"**，
> 我就会得出**完全相反的结论**："`acceptance-pack` 门禁有漏洞" ——
> **而真相是我的注入器根本没生效。**
>
> **这正是本 Loop 从第 1 代就在做的事**（`gate_injection_tests` 单列
> `unproven` 而非计入 `bad`）**救了我自己一次。**

### 修复后

```
注入测试: 17 项受控失败被检出 / 0 崩溃 / 0 注入有效但未被检出 / 0 项注入有效性未确立
剩余 3 项：0 未确立 + 2 正当排除 + 1 只读跳过（按纪律）
```
**"未确立"归零。剩余 3 项全部正当。**

---

# 第 8 代（TL 终局）：剩余问题逐项终结


## T-21 【数据丢失·已恢复】我多次整文件覆盖 `FAILURES.md`，丢了 T-01~T-11

- **发现方式**：写交接文档时，我按要求"**输出前逐条复核数字**"，
  用 `grep -c "^## T-"` 数出 **11 条**，而我文档里写的是"T-01 ~ T-20 共 20 条"。
  **数字对不上 ⇒ 去查 ⇒ 发现早期条目已丢失。**
- **根因**：本文件被**多次 `write_to_file` 整文件覆盖**（第 4、5、8 代各一次），
  每次只保留当代内容，**前代条目被替换**。
  git 历史显示 `T-01 ~ T-20` **全部存在过**，但**当前文件只剩 11 条且有重复**
  （T-20×2、T-08×2、T-06×2）。
- **严重性**：**这是本项目最有价值的产物**（它承载"哪些判断不可信"的全部记录），
  **而它被我用最粗暴的方式毁掉了一多半。**
- **恢复**：从 git 历史 **7 个版本**按 T 编号合并重建（同编号取最新文本），
  **T-01 ~ T-20 现已完整，编号连续无重复**。
- **教训**：
  > **增量追加优于整文件重写。**
  > 记录类文件（失败记录、证据、台账）**必须追加**，因为"重写"隐含
  > **"我知道什么该保留"** —— 而我并不知道。
- **与 T-07/T-09 同族**：那两次是"宣布之前没查"，这次是"**重写之前没查会丢什么**"。

---

# 第 9 代（新 TL 接手）：对**交接文档本身**的攻击

> **攻击方式**：§六 要求"逐条跑，不要相信本文"。故本次**不读结论、只跑命令**，把 8 条预期与实测逐条对表。
> **7 条一致，1 条不符**，另新增 5 项发现。**本代所有数字均来自命令输出**（硬约束 #4）。

## T-22 【攻击命中·已修】交接文档 §六 第 8 条不符：**KERT 跨仓工作区不干净**

- **文档称**：`cd /home/szf/dev/Leibniz-KERT && git status --porcelain  # 应为空`
- **实测**：
  ```
  ?? .ua/                ← 6.2M
  ?? .understandignore
  ```
- **性质区分（不一律"删除"）**：
  - `.ua/`：Understand-Anything **派生产物**（`knowledge-graph.json`/`fingerprints.json`/`tmp`/`intermediate`）——
    **可重建、体积大、且其自身声明为 DERIVED 派生视图、不构成权威事实** ⇒ **应忽略**；
  - `.understandignore`：**人工撰写的治理资产**（含权威性声明与 Owner 裁决锚点）⇒ **应入库**。
  > **若不区分，"清干净"会把治理资产一起删掉** —— 这正是"用看起来对的动作替代被验证的动作"。
- **处置**：KERT `.gitignore` 增加 `.ua/`、`.understand-anything/`；`.understandignore` 显式 `git add` 入库。
  实测 `git check-ignore -v .ua/` → `.gitignore:62`。

## T-23 【攻击命中·已登记】门禁套件**每次运行都会弄脏受版本控制的证据文件**

- **现象（可复现）**：
  ```
  git status --porcelain          → 空（干净）
  python3 scripts/run_gates.py    → 22/23，exit=0
  git status --porcelain          →  M evidence/gk-ke-chain-trace/trace.json
  ```
- **根因（实测，非推测）**：连续运行两次，三次 sha256 **全不同**
  （已提交版 `df2ed18c` / run1 `4cfbefa7` / run2 `075052b4`）；`diff` 显示**唯一差异**为 `generatedAt` 的运行时时间戳。
  ⇒ 该"证据文件"**内容不可复现**。
- **危害（两条，均为机制性的）**：
  1. **每次跑门禁都留下未提交改动** ⇒ 与"跑完应干净"的纪律冲突，
     并使 `git status` 失去"是否被人动过"的判据价值；
  2. 它会与 `gate-injection-tests` 的"残留检测"**互相作用**（见 T-24）。
- **为何未修**：`scripts/gk_ke_chain_trace.py` **不在 GK16 的 scope 内**。
  **归属：本 Loop 需扩 scope 或另开工作项**（见本代末"归属表"）。

## T-24 【我方测量被污染·**未确立，不得断言为缺陷**】并行运行门禁 ⇒ 假 FAIL

- **经过（必须自曝）**：我把 `run_gates.py`、`gate_injection_tests.py`、`gk_ke_chain_trace.py`
  放在**同一批次并行执行**（三条 shell 命令同时跑）。结果：
  - 一次：`gate_injection_tests` **exit=1**，报"注入测试留下了改动，仓库不干净"，且**失败详情为空**（无文件名）
    —— 看起来像"门禁自己失败且不可诊断"；
  - 另一次：`run_gates` 报 **"2 项完整性失败"**，仓库出现
    `M specs/gk-ke/v1/examples/positive/ActivationPlan.json`（**合同正例被改动**）
    —— 看起来像"门禁套件破坏合同"。
- **受控复测**：**单独串行**重跑 ⇒ `run_gates` exit=0（22/23）、`gate_injection_tests` exit=0（INCONCLUSIVE）、
  仓库仅剩 T-23 的 `trace.json`。
  ⇒ **"2 项完整性失败"与"合同正例被改"是我造成的竞态，不是项目缺陷。**
- **计数不一致同理**：并行批次下报 `17 项检出 / 1 项未确立`；串行连跑 3 次报 `18 项检出 / 0 项未确立`
  （后两次 stderr 哈希完全相同 `8495b5e2`）。
- **处置**：**如实登记为"我方测量污染"，不推翻任何既有结论**，并**不据此修改门禁**。
- **但保留一个待攻击点（不得当成已排除）**：
  `gate_injection_tests` 的残留处置会对"同名路径"执行 `git checkout -- <path>`（源码 565 行附近）。
  若该路径正被**另一进程**写入，回滚会**销毁他方写入** ——
  **这是"测试破坏被测环境"的形态，与 T-19（副作用残留）方向相反但同族。**
  ⇒ **须在受控条件下复现后才可断言**（未复现前，本项**不是**缺陷）。

## T-25 【攻击命中·最重要·已修】派发提示词早于新观测 ⇒ **item #1 在构造上无法完成**

- **攻击**：交接文档把"新观测下的语义消费复判"列为第 1 项未完成项，并称"提示词已备"。
  **验证：那份提示词能把新观测交到执行者手上吗？**
- **实测四条（均为命令输出）**：
  1. 判据 V1.2.1 全文检索"观测"/`observations` → **零命中** ⇒ **§观测 一节确实不存在**；
  2. V1.0 提示词输入表第 2/3 行写"**见判据文档 §观测 一节所指路径**" ⇒ **悬空**；
  3. 提交先后：提示词出自 **`afeec79`**，新观测与处置记录出自 **`19fd228`** ⇒
     提示词**早于**"新观测就绪"，**不可能指向它**；
  4. 输入表第 4 行 `report.json` —— 其自身 `_archivalNote` 已声明
     **【过期产物 · 勿直接引用】**（占位适配器下 S5"必然通过、无判别力"）。
- **结论**：按 V1.0 派发，执行者只能拿到**悬空路径 + 已归档报告 + 旧观测**，
  判定**必然是 INCONCLUSIVE —— 且原因不是独立性不足，而是委托材料自相矛盾**。
  ⇒ **item #1 被阻断在委托环节，而非判定环节。**
- **处置（已修）**：产出 `docs/architecture/GK-KE-语义消费独立复判-派发提示词-V1.1.md`，
  并在 **V1.0 顶部加作废横幅**。V1.1 只改**委托材料**，未动判据内容与判定纪律：
  显式给出新观测路径 + `sha256`；显式声明 §观测 缺失并**要求执行者如实记录但不据此拒绝判定**；
  明示 `report.json` 禁引；列出三版本观测并存表并规定**混用即作废**；
  写入**强度上限**（`simulationOnly: true` ⇒ 上限为"输入级/逻辑级"，**不得读作 B 层达成**）；
  新增交付物 5（证据指纹声明）。

## T-26 【待攻击·已登记】`chain-trace` 的「输入消费证明」与其自身反事实输出**不同向**

- **现象（原始输出）**：
  ```
  链路级反事实:
    移除 asOf / conflicts / customerId / evidenceRefs / executionStatus /
         explanations / indicators / requiredQuestions / ruleTrace / taskId
       → 下游输入变化=True   输出变化=False     ← 10 项全部如此
  输入消费证明: True
  ```
- **质疑**：**若移除任一上游字段后下游输出都不变**，
  则"下游消费了上游"的证据只能是"**映射层把字段传下去了**"，而非"**下游用了它**"。
  ⇒ 「输入消费」一词的强度**可能超出证据能支持的范围**（T-10「弱证据」同族）。
- **状态**：**仅登记，未断言。** 下一步读 `scripts/gk_ke_chain_trace.py` 中
  `输入消费证明` 的**计算式**，并构造负例（**上游字段缺失时下游输出必须变**）。
  **读代码只生成假设；只有运行能确立结论。**

## T-27 【复核·不复现】T-11 的"无法解释的哈希失配"当前不成立

- **复核**：解析 `EVIDENCE.json` 的 5 个 `output_sha256` 与磁盘实际逐一比对 →
  `gate_selftest` / `gate_injection_tests` / `criteria_key_audit` / `criteria_line_audit` / `gates` **5/5 MATCH**。
- **结论**：**现象当前不复现。** 按 T-11 自己的纪律：
  **不得把"复现不出来"当成"已解决"** ⇒ 本项**维持"未解释"**，不改其结论。

---

## 第 9 代归属表（**要么做掉，要么给出归属**）

| 项 | 状态 | 归属 |
|---|---|---|
| T-22 KERT 工作区不干净 | **已修** | 本 TL（跨仓，已提交） |
| T-25 派发提示词阻断 item #1 | **已修** | 本 TL（V1.1 已出，待**另一名独立执行者**执行） |
| T-23 证据文件含运行时间戳、被 git 跟踪 | 已登记，未修 | **需扩 GK16 scope** 或另开工作项（`gk_ke_chain_trace.py` 不在现 scope） |
| T-24 并发下回滚他方写入 | **未确立** | 本 TL（受控复现后再判） |
| T-26 chain-trace「输入消费」强度 | **待攻击** | 本 TL（下一步） |
| T-27 T-11 哈希失配 | 不复现，维持"未解释" | 无（如实保留） |
| `semantic-consumption` NOT_MET | 不代判 | **另一名独立执行者**（V1.1 提示词已备） |
| 判据 V1.2.1 预注册零引证 / 无 §观测 | 不改判据 | **判据作者侧** |

---

## T-28 【攻击命中·BLOCKER·**已修并自证**】下游受控枚举**恒取默认值** —— "再入式取值"从未生效

- **攻击**：把 T-26 的质疑追到底 —— **上游状态到底有没有到下游？**
- **实测（五刀，全部可复现）**：
  1. 上游 `executionStatus='PARTIAL'`；映射后下游输入**没有** `upstreamStatus` / `reconciliationStatus` /
     `executionStatus`，只有 `status='PARTIAL'`；
  2. 把上游状态改成 `NOT_RUN` / `SUCCESS` / `FAILED` 再走同一映射 → 下游 `coverageStatus`
     **恒为 `PARTIAL`**，输出**逐字节相同**；
  3. 按技能契约键名直接传 `upstreamStatus=NOT_RUN` → **仍 `PARTIAL`**
     （**这一刀推翻了我"读代码"得出的第一假设：键名不匹配**）；
  4. 在 `simulate()` 边界装间谍 → 实参 **`upstream=None`**；
  5. 抓适配器收到的 `user` 原文 → `'{"customerId": "SIM-C001", "upstreamStatus": "NOT_RUN"}'`，
     `json.loads` 成功、键存在 ⇒ **异常一定发生在更后面**。
- **根因（三层叠加，全是"声称已修但未生效"）**：

  | 层 | 位置 | 缺陷 |
  |---|---|---|
  | 1 | `llm.py:253` | `self._sample_package(customer, system)` —— **丢掉了 `user`** |
  | 2 | `llm.py:168, 208` | 签名无 `user`，函数体却 `json.loads(user)` ⇒ **`NameError`** |
  | 3 | `llm.py:214` | `except Exception` **静默吞掉**（仅 `debug`）⇒ `_up` 恒为 `None` |

- **后果（比"字段没送到"更严重）**：
  - `coverageStatus = status_map.get(None, "PARTIAL")` ⇒ **恒为默认值**；
  - ⇒ `INDEPENDENT-JUDGEMENT-DISPOSITION.md` §二 第 2 条「已修：现**依上游状态映射**得 `PARTIAL`」
    **不成立** —— **结论值对、理由错**（这正是本仓最典型的"看起来对"）；
  - ⇒ 判据 `S3(a)` 的"结构性不可满足"**并未真正修复**：由"枚举越界"变成"**恒取默认**"，
    「上游**没查**（`NOT_RUN`）」与「上游**查了**（`PARTIAL`）」**依然不可区分** ——
    正是 `S2/S3` 要防的形态。
- **元教训**：我的第一个假设（键名不匹配）被实测**证伪**，真实根因（**签名缺参 + 静默吞异常**）更严重。
  **第 N 次验证：读代码只生成假设，只有运行能确立结论。**

### T-28a 修复与**自证**（KERT 仓）

| # | 修复 | 位置 |
|---|---|---|
| 1 | `_sample_package(self, customer, system, user="")` 增形参 | `src/kert/infrastructure/adapters/llm.py:168` |
| 2 | `_sample` 调用处传入 `user` | 同文件 `:253` |
| 3 | 解析失败 `debug` → **`warning` 并写出异常**（不得静默降级）；仿真器不可用同样 `warning` | 同文件 `:214`、`:217` |

- **负例测试**：`tests/unit/test_llm.py::TestPackageReentrantUpstreamStatus`

  | 用例 | 断言 |
  |---|---|
  | `test_upstream_status_not_run_is_consumed` | 上游 `NOT_RUN` ⇒ 下游 `NOT_RUN`（**不得**落回默认） |
  | `test_alternate_enum_value_changes_downstream_conclusion` | 同枚举**他值**（`SUCCESS`/`PARTIAL`）⇒ 结论随之改变 |
  | `test_missing_upstream_status_falls_back_to_default` | 上游**确实缺失** ⇒ 才允许默认 |

- **回退法自证**（硬约束 #3 要求"注入真的发生"）：

  ```
  修复后      : 19 passed
  回退 llm.py :  2 failed   ← 恰为上表前两个用例（'PARTIAL' != 'NOT_RUN' / != 'SUCCESS'）
  恢复修复    : 19 passed
  ```

  ⇒ **测试能检出该缺陷**，不是"恒通过"的空转测试。
- **修复后实测对照**（同一命令，前后各一次）：

  ```
  修复前：upstreamStatus=NOT_RUN → coverageStatus='PARTIAL'   （错）
  修复后：upstreamStatus=NOT_RUN → coverageStatus='NOT_RUN'   （通）
  ```

## T-29 【攻击命中·已修】`chain-trace` 用"输入变化"冒充"消费"，且把**反证藏在 JSON 里**

- **事实**：`input_consumed = all(c["downstreamInputChanged"])`（源码 `:332`），
  `verdict` **只看它**（`:380`）；决定性反证 `outputConsumed` **只在 JSON 内、不打印**（原 `:422`）。
- ⇒ 人类可见输出 `输入消费证明: True` 与"下游输出 10/10 不变"**并置而不提示**，
  读者会把它读成"下游消费了上游"——**与 `T-12` 同构（文本说对、结论说错）**。
- **处置（已修，仅改打印，未动任何 pass 条件）**：两侧事实一并打印，并**改名以示其真实含义**：

  ```
  上游字段进入下游输入: True
  下游输出随上游变化: 否   ← **未观察到下游消费上游**（输入到达，但输出不随其变化）
  ```

  **保留全部 JSON 键名与 verdict 字符串不变**（实测仓库内零外部引用，仍保守不动）。
- **未做（给出归属）**：是否把 `output_consumed` 纳入 pass 条件 ——
  **须待 T-30 修复后**再判；否则它会因"词汇不匹配"变红，属**错误变红**。归属：本 TL（下一步）。

## T-30 【攻击命中·BLOCKER·已登记·未修】映射层与下游技能**输入契约词汇不匹配**

- **事实（三方对照）**：

  | 来源 | 该字段叫什么 |
  |---|---|
  | 下游技能自身契约 `bank-front-kyc-gap-check/references/input-schema.md` | **`upstreamStatus`**（原文："…**不得改写**"） |
  | 适配器读取（`llm.py:210`） | `reconciliationStatus` **或** `upstreamStatus` |
  | GK 映射合同实际产出（实测键列表） | **`status`**（`executionStatus` → 叶名 `status`） |

- **实测印证（T-28 修复**之后**）**：走**真实映射**把上游状态改为 `NOT_RUN` / `SUCCESS` / `FAILED` →
  下游 `coverageStatus` **仍恒为 `PARTIAL`**，10 项反事实**输出变化仍全为 `False`**；
  而按技能契约键名直传 → 正确得 `NOT_RUN`。
  ⇒ **桥的一端接好了，另一端仍接错端口。**
- **性质**：GK 映射合同用**建议书词汇**（`status`/`ruleTrace.*`/`entityId`…），
  下游技能消费的是**它自己的输入契约词汇**（`upstreamStatus`）。
  **两者之间缺少"下游技能输入契约适配层"** —— 之前的"再入式取值"把桥接塞进了 LLM 适配器，
  且接错了端点。
- **为何不在本次修（给出理由，而非回避）**：
  1. 需动 `specs/` 合同（`UpstreamFieldMapping.json` / `ConsumerObligations.json`），
     按纪律**必须合同先行**（改合同源 → `make generate` → `make check` → 再改实现），
     且 `chain-trace` 自带三条机械校验会同时约束；
  2. 需先裁定**桥接放哪里**（映射合同里 vs 独立的下游输入适配器）——
     既是合同问题也是分层问题，属 **TL 决策**，不宜在收工前草率落地。
- **归属：本 TL，下一步第一个工作项。**

---

## 第 9 代（续）结论

> **本次接手最有价值的产出不是"修好了什么"，而是**：
> **本仓赖以证明"下游消费上游"的那条链路，其"消费"一词在链路上从未成立** ——
> 先是机制**完全死**（`T-28`，且被 `except Exception` 掩盖了一整代），
> 修好后暴露**词汇不匹配**（`T-30`）；
> 而门禁 `chain-trace` 对这两件事**全程无感**，始终打印"输入消费证明: True"并 `exit=0`（`T-29`）。
>
> **与既有结论同向**：独立判定对判据 V1.2.1 的 `PASS 0 / FAIL 1 / INCONCLUSIVE 4`
> （`semantic-consumption` = `NOT_MET`）**在此获得一条独立的机制性佐证**。
> **TL 不代判、不改该判定**；本条只是新增证据。
