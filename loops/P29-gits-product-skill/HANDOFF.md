# P29-gits-product-skill｜Handoff

| 项 | 状态 |
|---|---|
| 交付对象 | 产品匹配只调 DKWS Skill（customerId，不用 H2 流水规则） |
| 开发自检 | `unit_product` + `security_check` 已绿；未写 `DEV_SELF_CHECK_PASS` / `QA_PASS` |
| 独立QA | `PENDING` |
| 生产就绪 | `NO` |

## 交付物

- `ProductMatchingService`：注入 `SkillExecutionPort` + `CustomerRepository`；request 仅 `customerId`；Skill 失败/空 data/客户未命中 → 空 list
- `EngagementConfig`：产品匹配 bean 去掉 TransactionRepository / KycInsightService
- `FallbackSkillExecutionAdapter.NO_LOCAL_FILL` 增加 `bank-front-product-recommendation`
- 契约 §3：产品推荐 Skill 只认 `customerId`（v1.3）
- 经营视图「产品匹配」空态展示 KI-FRONT-006 提示
- 测试：`ProductMatchingServiceTest` 5 + `FallbackSkillExecutionAdapterTest` 7 = 12/0；COV 4/0；AT-009 空 list OK
- E2E Owner：复核 Maven 13/0 + COV 4/0；未改生产代码

## 开放项与禁止声明

不得将开发自检写成 QA。未写 `QA_PASS`。未碰 P24–P28 IQA baton。未 commit。未手改 `generated/`。未改 OpenAPI。
