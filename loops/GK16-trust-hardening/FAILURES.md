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
