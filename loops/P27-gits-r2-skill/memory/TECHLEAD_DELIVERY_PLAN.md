# P27 Tech Lead delivery plan

Role: tech_lead
Do not touch P24 / P25 / P26 IQA batons.

## Principle

一键访前页的知识正文只来自 DKWS Skill。R1 已 Skill-only。R2 目前由 `EngagementOrchestrator` 返回全空卡，而 `PrevisitWorkflowService.generateQuickBattleCard` 仍用 H2 KYC/产品种子；`EngagementScenarioE2eIT` 还在测这条种子路径。

## Mapping（不改 OpenAPI 形状）

从 R1 已解析的 `skillSections` 填现有 `QuickBattleCard`：

| R2 字段 | 来源 |
|---|---|
| `keyPoints` | KI-009、KI-FRONT-002 的 content（有则加入，可截断到合理长度） |
| `productHints` | KI-FRONT-006 |
| `dontForget` | KI-FRONT-004、KI-FRONT-005 |
| `bottomLine` | 仅当某节 heading 明确含「底线」；否则空串。禁止再写种子禁令清单当知识 |
| `customerName` / `visitObjective` | 身份：CRM `findCustomer` 名称（目录字段）+ 拜访意图。不是 KYC |
| `customerTier` / `riskLevel` | 可用 CRM 主档枚举（customer 表），不要用 KYC gap |

Skill 失败 / 无对应章节 → 对应 list 为空。不要调用 `KycInsightService` / `PrevisitWorkflowService`。

Heading 对位规则与前端 `frontend/src/utils/kiSection.ts` 别名一致（KI-009、八维、KYC、产品候选等）。

## Orchestrator

`executePrevisitPhase` 用 `knowledgeDrivenPrevisitGenerator` 的 sections 建 R2。删除对 `PrevisitWorkflowService` 的无用注入（字段已注入未使用）。

`PrevisitWorkflowService` 本 Loop **不删除**（COV/旅程演示仍可能间接依赖）；但一键访前不得再走它。

## Frontend

`KnowledgePrevisitReport.vue`：R2 全空时展示「DKWS 未返回速战卡」，不要继续隐藏到用户以为没这块。有 Skill 内容则照旧渲染。

## Tests

新建 `QuickBattleCardFromSkillTest`：

1. sections 含 KI-009 / FRONT-002 / 006 / 005 → 对应 list 非空且正文来自 Skill，不含种子产品名「流动资金贷款」之类 unless it was in the section
2. 空 sections → 三 list 皆 empty
3. Orchestrator（或 mapper）不得调用 kycInsightService

改 `EngagementScenarioE2eIT`：

- `previsitReportGeneration`：走 `orchestrator.executePrevisitPhase`；允许空 productSchemes / keyQuestions
- `quickBattleCardGeneration`：走 orchestrator 的 battleCard；Skill down 时 empty lists OK；禁止 `assertFalse(keyPoints().isEmpty())` 依赖种子

## Gates

`unit_r2` + `security_check`。未写 `QA_PASS`。未 commit。
