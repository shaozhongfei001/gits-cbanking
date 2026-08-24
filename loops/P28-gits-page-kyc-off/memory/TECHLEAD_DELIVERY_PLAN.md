# P28 Tech Lead delivery plan

Role: tech_lead
Do not touch P24 / P25 / P26 / P27 IQA batons.

## Principle

H2 种子 KYC / 交易流水可以继续入库（旅程机制、E2E `getKycGapProfile` 仍可存在），但**不得作为工作台或经营视图的页面知识**。那些条目属于 DKWS：KI-FRONT-005 / KI-FRONT-003，只在一键访前报告展示。

## Backend

1. `EngagementJourneyController.startJourney`：`kycGapSummary` **始终为 null**。不要把 `unknownItems`/`priorityQuestions` 拼进工作台 toast。
2. `EngagementOrchestrator.startEngagementJourney`：`JourneyStartResult.kycProfile` 固定 `Optional.empty()`。可不再调用 `getKycGapProfile`。不要删除 `KycInsightService` 字段（访后信号等仍用）。
3. OpenAPI 不改：`kycGapSummary` 已可空。

## Frontend

1. `EngagementWorkspace.doStart`：成功 toast 不含 KYC 摘要。启动节点副文案不要写「KYC洞察」（改为「选择客户，进入经营」即可）。
2. `fetchCustomerContext`：**不要**再 GET `/kyc/:id/gap-profile`，**不要**再 GET `/customer/:id/transactions` 来填页面。仍可 GET operating-view + signals（信号是旅程产物，不是访前 KI）。
   - `kycGapProfile` / `recentTransactions` 置 `undefined` / `[]`
3. `CustomerOperatingView.vue`：
   - KYC 区块始终展示，文案 **「DKWS 未返回该条目，请在访前报告 KI-FRONT-005 查看」**（不要用 H2 unknownItems 卡片）。
   - 近期交易流水：有种子数据也不展示明细；同样提示 KI-FRONT-003，或隐藏表格。
   - CRM 主档（名称/行业/信用代码/RM）保留，那是 customer 目录。
   - 机会信号 / 旅程列表保留。

## Tests

- `EngagementJourneyControllerTest.testStartJourney`：即使 mock 带 kyc profile，响应也不得出现种子 KYC 文案；`kycGapSummary` 为 null/缺失。
- `engagement.spec.ts`：`fetchCustomerContext` 不得调用 `/kyc/` 或 `/transactions`。
- 新建 `frontend/src/views/__tests__/CustomerOperatingView.spec.ts`：有假 kycGapProfile 也不渲染种子 unknownItems；出现 KI-FRONT-005 提示。（实现上 fetch 不再返回 profile，测 empty + 提示即可。）
- `EngagementWorkspace.spec.ts`：若有启动旅程断言，toast/副文案不含种子 KYC。

## 不要做

- 不要删 `ScenarioSeedDataService.loadKycGapProfile` / 交易加载。
- 不要改 `GET /kyc/{id}/gap-profile` 合同（机制 API 可留）。
- 不要改 ProductMatchingService。
- 不要写 QA_PASS，不要 commit。
