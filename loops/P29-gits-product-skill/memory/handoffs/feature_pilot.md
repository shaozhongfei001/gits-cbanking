# Handoff｜P29-gits-product-skill｜feature_pilot

**Time**: `2026-08-22T14:22:00Z`
**Role**: `feature_pilot`
**Baton**: handed to `independent_qa`

## Implementation

GITS 产品匹配只调 DKWS Skill `bank-front-product-recommendation`，request 仅 `customerId`。不读 H2 流水规则 / KYC，不用本地 LLM 补推荐。Skill 失败或空 data → 空数组。

1. `ProductMatchingService` — `SkillExecutionPort` + `CustomerRepository`；客户未命中返回空 list（不抛）；映射 products/recommendations/candidates/items，否则 sections 含 KI-FRONT-006 / 产品候选 / 产品组合 合成一条
2. `EngagementConfig.productMatchingService` 只传 Skill 端口 + 客户仓储
3. `FallbackSkillExecutionAdapter.NO_LOCAL_FILL` 增加 `bank-front-product-recommendation`；参数化测试同步加上 `bank-front-supply-chain-graph`
4. `docs/dd/skill-execute-api-contract.md` §3 补产品推荐只认 customerId（v1.3）
5. `CustomerOperatingView` 「产品匹配」：空 → 「DKWS 未返回该条目，请在访前报告 KI-FRONT-006 查看」
6. `EngagementScenarioE2eIT.productMatchingBasedOnTransactions`：Skill down 时空 list OK，禁止 `assertFalse(isEmpty())`

## Gates

- `unit_product`: Tests run: 12, Failures: 0（ProductMatchingServiceTest 5 + FallbackSkillExecutionAdapterTest 7）
- `security_check`: PASS（advisory findings only）
- Optional COV: `CustomerOperatingView.spec.ts` 4/0
- Optional E2E: `EngagementScenarioE2eIT#productMatchingBasedOnTransactions` 1/0

## 未交

- `QA_PASS` / independent QA
- OpenAPI / `generated/`（未改）
- 未碰 P24–P28 IQA baton
- No commit
