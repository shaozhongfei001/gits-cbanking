# P27-gits-r2-skill｜Handoff

| 项 | 状态 |
|---|---|
| 交付对象 | 一键访前 R2 从 Skill sections 抽取 |
| 开发自检 | `unit_r2` + `security_check` 已绿；未写 `DEV_SELF_CHECK_PASS` / `QA_PASS` |
| 独立QA | `PENDING` |
| 生产就绪 | `NO` |

## 交付物

- `QuickBattleCardFromSkill`：R2 列表来自 Skill 章节；空章节 → 空列表
- `EngagementOrchestrator`：一键访前不再注入/调用 `PrevisitWorkflowService`
- 工作台 R2：全空时仍展示区块文案「DKWS 未返回速战卡」
- 测试：`QuickBattleCardFromSkillTest` 3；`KnowledgeDrivenPrevisitReportGeneratorTest` 4；E2E 14/0（开发侧，非 QA_PASS）
- E2E Owner：复核合计 21/0；未改生产代码

## 开放项与禁止声明

不得将开发自检写成 QA、真实 E2E、客户验收或生产冻结。未写 `QA_PASS`。未碰 P24 / P25 / P26 IQA baton。未 commit。未手改 `generated/`。
