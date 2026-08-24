# P26-gits-skill-scripts｜Handoff

| 项 | 状态 |
|---|---|
| 交付对象 | 一键访前外联/会面改为 DKWS Skill-only（customerId，不拼种子 KYC） |
| 开发自检 | `unit_scripts` + `security_check` 已绿；未写 `DEV_SELF_CHECK_PASS` / `QA_PASS` |
| 独立QA | `PENDING` |
| 生产就绪 | `NO` |

## 交付物

- `OutreachScriptService` / `MeetingScriptService`：注入 `SkillExecutionPort`；CRM `findCustomer` 未命中抛 `IllegalArgumentException`；request 仅 `customerId`（外联可带 `channel`）；Skill 失败/空 data 持久化空脚本
- `EngagementConfig`：两服务 bean 改传 `SkillExecutionPort`，去掉 `LlmClient`
- `FallbackSkillExecutionAdapter.NO_LOCAL_FILL` 增加 `skill-customer-outreach-script`、`skill-customer-meeting-script`
- 工作台：objective/openingLine/agenda 皆空时展示「DKWS 未返回该话术」
- 测试：`OutreachScriptServiceTest`、`MeetingScriptServiceTest`、`FallbackSkillExecutionAdapterTest` 共 15 通过
- E2E Owner：AT-007/008 已改为 identity-only；`EngagementScenarioE2eIT` + 两脚本单测 rerun 24/0

## 开放项与禁止声明

不得将开发自检写成 QA、真实 E2E、客户验收或生产冻结。未写 `QA_PASS`。未碰 P24 / P25 IQA baton。未 commit。未手改 `generated/`。
