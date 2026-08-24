# P28-gits-page-kyc-off｜Handoff

| 项 | 状态 |
|---|---|
| 交付对象 | 工作台/COV 不把 H2 KYC/流水当页面知识 |
| 开发自检 | `unit_page` + `security_check` 已绿；未写 `QA_PASS` |
| 独立QA | `PENDING` |
| 生产就绪 | `NO` |

## 交付物

- 启动旅程：`kycGapSummary` 始终 null；orchestrator 启动不再调用 `getKycGapProfile`
- 工作台 toast 不含 KYC 摘要；启动节点副文案「选择客户，进入经营」
- `fetchCustomerContext` 不再 GET `/kyc/` 或 `/transactions`
- COV KYC 区块固定提示 KI-FRONT-005；流水不展示种子表，提示 KI-FRONT-003
- 测试：`EngagementJourneyControllerTest` 4；frontend 3 files / 53
- E2E Owner：复核 Maven 4/0 + frontend 53/0；未改生产代码

## 开放项与禁止声明

不得将开发自检写成 QA、真实 E2E、客户验收或生产冻结。未写 `QA_PASS`。未碰 P24–P27 IQA baton。未 commit。未手改 `generated/`。未改 OpenAPI。
