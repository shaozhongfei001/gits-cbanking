# Handoff｜P27-gits-r2-skill｜feature_pilot

**Time**: `2026-08-22T12:42:00Z`
**Role**: `feature_pilot`
**Baton**: handed to `independent_qa`

## Implementation

一键访前 R2 只从 R1 Skill `data.sections` 抽取。不再走 `PrevisitWorkflowService` 种子作战卡。`PrevisitWorkflowService` 类保留（COV/旅程演示）。

1. `QuickBattleCardFromSkill` — KI-009/002 → keyPoints；KI-FRONT-006 → productHints；KI-FRONT-004/005 → dontForget；heading 含「底线」才填 bottomLine。别名与 `frontend/src/utils/kiSection.ts` 一致。不调用 `KycInsightService`。
2. `EngagementOrchestrator.executePrevisitPhase` — `knowledgeDrivenPrevisitGenerator.generate` 后用 mapper；CRM `findCustomer` 只取名称/等级/风险。去掉 `PrevisitWorkflowService` 构造注入。
3. `EngagementConfig.engagementOrchestrator` — 同步去掉该构造参数；`previsitWorkflowService` bean 仍注册。
4. `KnowledgePrevisitReport.vue` — R2 区块在 battleCard 存在时始终展示；四字段全空显示「DKWS 未返回速战卡」。
5. `EngagementScenarioE2eIT` — `previsitReportGeneration` / `quickBattleCardGeneration` 走 orchestrator；允许空列表。

## Gates

- `unit_r2`: Tests run: 7, Failures: 0 (QuickBattleCardFromSkillTest 3 + KnowledgeDrivenPrevisitReportGeneratorTest 4)
- `security_check`: PASS (advisory findings only)
- Extra (not a loop gate): `EngagementScenarioE2eIT` 14/0

## 未交

- `QA_PASS` / independent QA
- OpenAPI / `generated/` (must not change)
- Did not touch `loops/P24-dkws-platform` / P25 / P26 IQA baton
- No commit
