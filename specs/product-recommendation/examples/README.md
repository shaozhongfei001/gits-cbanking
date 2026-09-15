# 产品推荐正反样例（GITS WP1-5）

文档状态：`CANDIDATE / FROZEN=NO / IMPLEMENTED=NO / REAL_E2E_PASS=NO`

> 本目录仅新增样例文件，作为产品推荐三段式 SDD 契约的**测试样例（golden cases / negative cases）**。
> 权威契约与不变量定义在上层 `specs/product-recommendation/*.schema.json` 与
> `specs/product-recommendation/README.md`（本目录不改动、不重复定义）。
> 所有样例为纯 JSON（`additionalProperties:false` 约束下不携带任何状态元数据），状态块只在本 README 声明。

## 1. 样例清单与不变量 / 用例映射

| 文件 | 类型 | 对齐 schema | 满足/违反的不变量 | 映射用例 |
|---|---|---|---|---|
| `valid-eligibility.json` | 正向 | `eligibility-result.schema.json` | 满足：`eligibility=ELIGIBLE`，每条规则结论含 `ruleId/ruleVersion/result/reasonCode/inputFactRefs/evidenceRefs` | TC-PR-001 |
| `invalid-ineligible-with-score.json` | 反向 | `recommendation-result.schema.json`（含 `eligibilityResults[]` + `fitResults[]`） | 违反 INV-02：`eligibility=INELIGIBLE` 的产品对应 `fitScore=0.85`（非 null） | TC-PR-008 |
| `valid-decision.json` | 正向 | `recommendation-human-decision.schema.json` | 满足：`decision=APPROVE`，`proposalVersionId` 非空，`reason` 可空（省略） | TC-PR-014（正向） |
| `invalid-decision-reject-no-reason.json` | 反向 | `recommendation-human-decision.schema.json` | 违反决策必填约束：`decision=REJECT` 但 `reason` 缺失 | TC-PR-015 |

## 2. 逐样例说明

### 2.1 `valid-eligibility.json`（TC-PR-001 正向）

第一段硬约束过滤结果，产品 `PROD-WC-001@2.2` 判定为 `ELIGIBLE`。

- `ruleResults` 含 2 条硬规则结论：
  - `PR-ELIG-001`（产品版本有效性）`result=PASS`；
  - `PR-ADM-004`（客户准入）`result=PASS`；
- 每条均含 `ruleId + ruleVersion + result + reasonCode + inputFactRefs + evidenceRefs`，满足"每条结论必须有完整规则证据"的要求；
- `unknowns=[]`、`reviewRequirements=[]`，表示无缺失事实、无需专家复核。

对应 TC-PR-001「产品有效、客户准入满足 → 进入第二段并有完整规则证据」。

### 2.2 `invalid-ineligible-with-score.json`（INV-02 违反，TC-PR-008 反向）

以 `recommendation-result.schema.json` 的完整输出信封承载一条**跨对象不变量违例**：

- `eligibilityResults[0]`：产品 `PROD-CR-005@3.1` 被 `PR-REG-002`（监管禁止行业）判定 `FAIL`，`eligibility=INELIGIBLE`；
- `fitResults[0]`：**同一产品** `PROD-CR-005@3.1` 却被给出了 `fitScore=0.85`（非 null）且 `rank=1`。

这违反了 **INV-02**：`Eligibility=INELIGIBLE → rankScore/fitScore 必须为 null`。
即"高分产品硬规则失败"仍被错误保留分数，正是 TC-PR-008「高分产品硬规则失败 → 仍被排除，分数不可覆盖」要拦截的错误态。

> 说明：`fitScore` 在 schema 层类型为 `number|null`，因此 `0.85` 本身不触发 JSON Schema 校验失败；
> 该样例是**业务不变量（INV-02）层面的反向样例**，用于机测不变量而非 schema 结构。

### 2.3 `valid-decision.json`（TC-PR-014 正向）

第三段客户经理人工决定（HG-D01 / D01_PRODUCT_RECOMMEND）的正向样例。

- `decision=APPROVE`（采纳当前候选方案作为服务方案草案，不代表产品/建议书已审批）；
- `proposalVersionId` 非空且指向明确推荐版本，满足 INV-06「HumanDecision 必须指向当前 proposalVersionId」；
- `expectedVersion` 与 `proposalVersionId` 一致，用于 If-Match/ETag 并发校验（过期提交返回 409）；
- `reason` 省略——schema 未将 `reason` 列入 `required`，对 `APPROVE` 可空（仅 REJECT/HOLD 及高风险 APPROVE 需理由）。

对应 TC-PR-014（人工决定的正向路径：基于不可变方案版本生成决定、保留原版本）。派工指定以 `APPROVE` 作为该正向样例的决策值；结构化修改（MODIFY）路径由 `invalid-decision-reject-no-reason.json` 所覆盖的必填约束与 schema `modifications[]` 定义另行约束。

### 2.4 `invalid-decision-reject-no-reason.json`（TC-PR-015 反向）

第三段人工决定的反向样例：`decision=REJECT` 但**缺少 `reason`**。

schema 字段描述规定：`reason` 对 `REJECT/HOLD` **必填**（`REJECT` 需"驳回原因分类＋说明"）。本样例刻意省略该字段，触发业务必填约束违反。

对应 TC-PR-015「修改/驳回原因缺失 → 按规则拒绝提交」。

> 如实说明：当前 `recommendation-human-decision.schema.json` 的 `required` 数组未将 `reason` 纳入机器强制（仅写在字段 description）。
> 因此该样例在**结构上仍能通过 JSON Schema 校验**，属于**业务规则层反向样例**；若后续要把 TC-PR-015 提升为机测门禁，需在 schema 增加条件必填（`REJECT/HOLD` 时 `reason` 必填）。本任务不改动 schema，仅如实标注此缺口。

## 3. 校验方式

每个样例均为合法 JSON，可用以下命令校验语法：

```bash
python3 -m json.tool specs/product-recommendation/examples/valid-eligibility.json > /dev/null && echo OK
python3 -m json.tool specs/product-recommendation/examples/invalid-ineligible-with-score.json > /dev/null && echo OK
python3 -m json.tool specs/product-recommendation/examples/valid-decision.json > /dev/null && echo OK
python3 -m json.tool specs/product-recommendation/examples/invalid-decision-reject-no-reason.json > /dev/null && echo OK
```

结构符合性依据上层 `*.schema.json`（draft 2020-12）逐字段对齐；反向样例针对的是**业务不变量 / 决策必填约束**，而非 JSON Schema 结构本身（详见第 2 节说明）。
