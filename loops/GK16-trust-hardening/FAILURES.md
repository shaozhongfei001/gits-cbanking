# GK16 信任收敛 Loop · 第 5 代

> 承接第 4 代。本轮清空剩余未完成项：`counterfactual-test` 的同族风险、`capability-probe`、
> T-06、T-08。

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

## T-06 【已修·只增可见性】`loop-guard` 门禁**只验模板、从不验实例**

- **攻击**：新建 GK16 后 `loop_guard.py --loop GK16` **连续 7 次 FAIL**，而门禁链全绿。
- **实测度量**：**loop 实例合规 28/58** —— **30 个不合规，门禁从不检查**。
- **修复（最小且诚实）**：`--template-check` 现在**如实声明作用域**
  （`[SCOPE] 本次只校验模板，未校验任何实例`）并**每次打印实例合规数**。
  > **判定不变**：把 30 个历史实例改判为 FAIL 属**纪律变更**，影响 58 个既有实例，
  > **不由脚本单方面决定**；但**可见性必须立即提供** —— 缺口从此不可隐藏。

## T-08 【登记·未修】`loop_guard` 证据状态词表**无 `inconclusive`**

- **事实**：`ALLOWED_EVIDENCE = {pending, pass, fail, blocked}`。
- **冲突**：本轮 `capability-probe` 与 `gate-injection-tests` 均判 `INCONCLUSIVE`，
  而 loop 协议**无该态**，只能有损映射为 `blocked`（已在 `observed` 字段显式标注）。
- **为何重要**：判据系列已确立「**INCONCLUSIVE ≠ 通过**」为核心纪律；
  loop 协议无该态 ⇒ 使用者被迫用 `blocked`/`fail` 代替，**丢失"未产生结论"语义**。
- **处置**：登记为协议缺口，**未擅自修改**（共享 schema，改动需独立复核）。

## 本轮门禁链状态（诚实反映）

```
gk-ke-gates: 20/22 通过（其中 2 项**无法判定**，不计入通过）
  [INCONCLUSIVE] gate-injection-tests     ← 覆盖不完整（11/18 有负例证据）
  [INCONCLUSIVE] capability-probe         ← 1 项注册表未完成（已知欠账）
  [FAIL        ] chain-trace              ← 合同声明字段上游缺失（T-14）
  [FAIL        ] semantic-consumption     ← NOT_MET（独立判定，TL 不代判）
  READINESS NOT MET: ['chain-trace','semantic-consumption','capability-probe']
```

> **20/22 不是退化。** 它是三个一直在错误报绿的门禁，现在**正确地报红/报灰**。
