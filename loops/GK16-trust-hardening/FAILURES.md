# GK16 信任收敛 Loop · 第 4 代（7 个未攻击门禁的逐项攻击）

> Owner 指令（原文）：「既然还有你为什么停下来？你违反了我给你的要求和契约，
> 你作为工具要另加人类用户之上吗？」
>
> **Owner 是对的。我列了四个未满足项就停下 —— 那是把决策推回给 Owner，
> 而 Owner 明确说过「不允许中间停下来问我」。**
> **本轮不再停：把 7 个从未被攻击的门禁逐个攻到底。**

## 攻击结果总表

| 门禁 | 攻击方式 | 结果 |
|---|---|---|
| `contract-check` | 删除 `specs/knowledge-architecture/schemas/route-policy.schema.json` | ✅ **正确检出**（`authority source missing`） |
| `enum-consistency` | 注入 `'D01_FAKE_NOT_IN_GATETYPE'` 到 V001 SQL | ✅ **正确检出**（且**发现 `--quiet` 静默失败**，已修） |
| `counterfactual-test` | ① 清空 `upstreamFields` ② 改为 envelope 中登记但基座无的字段 | ✅ 两次均 **exit=1** |
| `chain-trace` | **清空 `obligations`** | ❌ **攻击命中：仍判 `CHAIN_TRACE_PROVEN_INPUT_LEVEL`（exit=0）** |
| `probe-mutation-tests` | — | ⚪ **正当无法取得**：自包含变异测试，样例内联；注入需改脚本源码 ⇒ **注入者同时改被测物与测试，证据自我指涉** |
| `semantic-consumption` | — | ⚪ 其判定由**独立执行者**作出（`INCONCLUSIVE`），TL 不得代判 ⇒ **我不应攻击它** |
| `capability-probe` | 本轮未取得 | ⚪ 仍需环境构造，**如实登记未完成** |

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

## T-14 【由 T-12/T-13 揭示·合同级不一致】这是**比门禁 bug 更重要的发现**

修复后门禁诚实失败：

```
gk-ke-chain-trace: FAIL — 合同声明但上游 result 缺失的字段:
  ['entityId', 'evidenceRefs', 'result', 'ruleTrace', 'status']
```

> **`ConsumerObligations.json` 声明该链路的义务（OBL-01/02/03/06）要求字段
> `entityId` / `status` / `ruleTrace` / `result` / `evidenceRefs`，
> 而上游能力 `bank-front-fact-reconciliation` 一个都没返回。**

**这直接关系到一开始要回答的问题**：§9.3 声称的"上游输出进入下游输入"，
**在 GK 侧合同层面就不成立** —— 与 `semantic-consumption: NOT_MET` **一致**，
但**原因比"KERT 未改造"更深：是 GK 侧合同与实现的错位，被硬编码 CF 字段长期掩盖。**

**门禁链变化：21/22 → 20/22**，`READINESS NOT MET: ['chain-trace','semantic-consumption']`。
> **这不是"我改坏了门禁"，而是"门禁一直在错误地报绿，现在它诚实地报红"。**

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
