# P29 Tech Lead delivery plan

Role: tech_lead
Do not touch P24–P28 IQA batons.

## Principle

产品匹配与访前 KI-FRONT-006 一样：知识在 DKWS。GITS 只确认 CRM 里有这个 `customerId`，然后调 Skill。禁止再用 H2 交易流水规则拼「供应链融资 / 流动资金贷款 / 科技贷」。

## Skill

- skillId: `bank-front-product-recommendation`（契约已注册）
- request: **仅** `{ "customerId": "..." }`
- 不传 structuredFacts / transactions / kyc / knowledgeContext

在 `docs/dd/skill-execute-api-contract.md` §3 补一行：该 Skill 与图谱相同，只认 `customerId`。不要改 OpenAPI（`ProductMatch` 数组形状保持现有 Java 记录：productId/productName/reason/confidence/signal）。

## Mapping

从 `data` 抽列表（按顺序取第一个非空）：`products` / `recommendations` / `candidates` / `items`。

每条 map：
- productId ← productId | id | code（空则 `PROD-DKWS-{index}`）
- productName ← productName | name | title（空则跳过该条）
- reason ← reason | matchReason | rationale | description | content
- confidence ← confidence | matchScore | score（缺省 0；若 >1 且 ≤100 则 /100）
- signal ← signal | source | ""

若无数组但有 `sections[]` 且 heading 含 `KI-FRONT-006` / `产品候选` / `产品组合`：合成 **一条** ProductMatch（productId=`KI-FRONT-006`，productName=heading，reason=content）。

Skill 异常 / `!isOk` / 空 data → **空 list**。客户目录未命中 → 空 list（保持现状，不要 500）。

## Fallback

`FallbackSkillExecutionAdapter.NO_LOCAL_FILL` 增加 `bank-front-product-recommendation`。参数化测试同步加上（可顺带加上已在集合里的 `bank-front-supply-chain-graph`）。

## Frontend

`CustomerOperatingView.vue` 增加「产品匹配」区块：调用已有 `matchProducts(customerId)`。
- 有结果：展示 productName + reason
- 空：文案 **「DKWS 未返回该条目，请在访前报告 KI-FRONT-006 查看」**
- 禁止展示种子产品名「流动资金贷款」除非 Skill 真的返回了

## Tests

重写 `ProductMatchingServiceTest`：
1. request 仅含 customerId，无 transactions/structuredFacts
2. Skill 返回 products 数组 → 列表含 Skill 正文
3. Skill down / SKILL_ERROR → empty，不含「流动资金贷款」「供应链融资」
4. 客户不存在 → empty，不调 Skill（或调了也无所谓，但不得抛）

`EngagementScenarioE2eIT.productMatchingBasedOnTransactions`：改 identity-only；Skill down 时空 list OK；禁止 `assertFalse(matches.isEmpty())`。

COV spec：mock `matchProducts`；空列表出现 KI-FRONT-006 提示。

## 不要做

- 不要删 GET /product 目录接口
- 不要改 OpenAPI / generated/
- 不要写 QA_PASS，不要 commit
