# Handoff｜P28-gits-page-kyc-off｜feature_pilot

**Time**: `2026-08-22T12:56:00Z`
**Role**: `feature_pilot`
**Baton**: handed to `independent_qa`

## Implementation

工作台与客户经营视图不再把 H2 种子 KYC / 交易流水当作页面知识。那些条目属于 DKWS：KI-FRONT-005 / KI-FRONT-003。种子仍入库；`GET /kyc` 机制 API 保留。

1. `EngagementJourneyController.startJourney` — `kycGapSummary` 始终 `null`，即使 mock 带种子 profile 也不拼接 unknownItems/priorityQuestions。
2. `EngagementOrchestrator.startEngagementJourney` — `kycProfile` 固定 `Optional.empty()`；不再调用 `getKycGapProfile`。保留 `KycInsightService` 字段。
3. `EngagementWorkspace.vue` — 启动 toast 不含 KYC 摘要；副文案改为「选择客户，进入经营」。
4. `fetchCustomerContext` — 只 GET operating-view + signals；`kycGapProfile` undefined，`recentTransactions` `[]`。
5. `CustomerOperatingView.vue` — KYC 区块固定文案「DKWS 未返回该条目，请在访前报告 KI-FRONT-005 查看」；不渲染种子缺口卡片/流水表；CRM 主档/信号/旅程保留。

## Gates

- `unit_page`: Maven Tests run: 4, Failures: 0；frontend Test Files 3 / Tests 53 passed
- `security_check`: PASS (advisory findings only)

## 未交

- `QA_PASS` / independent QA
- OpenAPI / `generated/` (must not change)
- Did not touch `loops/P24` / P25 / P26 / P27 IQA baton
- Did not delete ScenarioSeed KYC/transaction loaders
- Did not change ProductMatchingService
- No commit
